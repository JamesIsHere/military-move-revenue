#!/usr/bin/env python3
"""Validate the synthetic Item 28A expected/invoiced/paid audit slice."""

from __future__ import annotations

import copy
import json
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.item_28a_extra_pickup import (  # noqa: E402
    INTERPRETATION_DECISION_ID,
    PROVENANCE as EXPECTED_CHARGE_PROVENANCE,
    RULE_IDS as EXPECTED_CHARGE_RULE_IDS,
    RULE_PACKAGE_ID as EXPECTED_CHARGE_RULE_PACKAGE_ID,
    rate_item_28a_extra_pickups,
)
from rules.item_28a_post_audit import (  # noqa: E402
    AUDIT_POLICY_ID,
    AUDIT_POLICY_PROVENANCE,
    AUDIT_POLICY_VERSION,
    AUDIT_SOURCE_PROVENANCE,
    AuditInputError,
    audit_item_28a,
)


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "item-28a-post-audit" / "item-28a-audit-cases.json"
REGISTRY_PATH = ROOT / "rules" / "registry" / "registry.json"


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict:
    def reject_float(value: str) -> None:
        raise ValidationError(f"{path.relative_to(ROOT)} contains non-exact JSON number {value}")

    with path.open(encoding="utf-8") as handle:
        value = json.load(handle, parse_float=reject_float)
    require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain an object")
    return value


def set_path(target: object, path: object, value: object) -> None:
    require(isinstance(path, str) and path, "mutation path is required")
    parts = path.split(".")
    current = target
    for part in parts[:-1]:
        if isinstance(current, list):
            require(part.isdigit() and int(part) < len(current), f"mutation path not found: {path}")
            current = current[int(part)]
        else:
            require(isinstance(current, dict) and part in current, f"mutation path not found: {path}")
            current = current[part]
    final = parts[-1]
    if isinstance(current, list):
        require(final.isdigit() and int(final) < len(current), f"mutation path not found: {path}")
        current[int(final)] = value
    else:
        require(isinstance(current, dict), f"mutation path parent is not an object: {path}")
        current[final] = value


def mutate(target: dict, mutations: object, case_id: str) -> None:
    require(isinstance(mutations, list), f"{case_id} mutations must be a list")
    for mutation in mutations:
        require(isinstance(mutation, dict), f"{case_id} mutation must be an object")
        set_path(target, mutation.get("path"), mutation.get("value"))


def change_records(candidate: dict, fixture: dict, case_id: str) -> None:
    remove_records = fixture.get("remove_records", {})
    require(isinstance(remove_records, dict), f"{case_id} remove_records must be an object")
    for collection, record_ids in remove_records.items():
        records = candidate["records"].get(collection)
        require(isinstance(records, list), f"{case_id} unknown removal collection {collection}")
        require(isinstance(record_ids, list), f"{case_id} removal ids must be a list")
        wanted = set(record_ids)
        before = len(records)
        records[:] = [record for record in records if record.get("id") not in wanted]
        require(before - len(records) == len(wanted), f"{case_id} removal id was not found in {collection}")

    append_records = fixture.get("append_records", {})
    require(isinstance(append_records, dict), f"{case_id} append_records must be an object")
    for collection, additions in append_records.items():
        records = candidate["records"].get(collection)
        require(isinstance(records, list), f"{case_id} unknown append collection {collection}")
        require(isinstance(additions, list), f"{case_id} appended records must be a list")
        records.extend(copy.deepcopy(additions))


def validate_contracts() -> None:
    registry = load_json(REGISTRY_PATH)
    packages = {record["id"]: record for record in registry["rule_packages"]}
    rules = {record["id"]: record for record in registry["rules"]}
    decisions = {record["id"]: record for record in registry["interpretation_decisions"]}
    claims = {record["id"]: record for record in registry["source_claims"]}
    locators = {record["id"]: record for record in registry["source_locators"]}
    require(packages[EXPECTED_CHARGE_RULE_PACKAGE_ID]["publication_status"] == "published", "upstream Item 28A package is not published")
    for rule_id in EXPECTED_CHARGE_RULE_IDS:
        require(rules[rule_id]["rule_package_id"] == EXPECTED_CHARGE_RULE_PACKAGE_ID, f"upstream rule moved packages: {rule_id}")
        require(rules[rule_id]["publication_status"] == "published", f"upstream rule is not published: {rule_id}")
    require(
        set(decisions[INTERPRETATION_DECISION_ID]["authorized_rule_ids"]) == set(EXPECTED_CHARGE_RULE_IDS),
        "upstream interpretation scope changed",
    )
    for reference in AUDIT_SOURCE_PROVENANCE:
        claim_id = reference["source_claim_id"]
        locator_id = reference["source_locator_id"]
        require(claims.get(claim_id, {}).get("source_locator_id") == locator_id, f"audit source claim/locator mismatch: {claim_id}")
        require(claims[claim_id]["interpretation_status"] == "reviewed", f"audit source claim is not reviewed: {claim_id}")
        require(locators[locator_id]["source_version_id"] == reference["source_version_id"], f"audit source locator/version mismatch: {locator_id}")

    require(AUDIT_POLICY_ID == "AUDIT-DP3-ITEM-28A-RECONCILIATION-V1", "audit policy id changed")
    require(AUDIT_POLICY_VERSION == "2026-08-03.1", "audit policy version changed")
    for reference in AUDIT_POLICY_PROVENANCE:
        path = ROOT / reference["document_path"]
        require(path.is_file(), f"audit policy source is missing: {reference['document_path']}")
    goal = (ROOT / "goal.md").read_text(encoding="utf-8")
    schema = (ROOT / "docs" / "logical-schema.md").read_text(encoding="utf-8")
    policy_text = (ROOT / "docs" / "item-28a-post-audit-policy.md").read_text(encoding="utf-8")
    require("Expected, invoiced, and paid amount comparison" in goal, "ratified comparison outcome is missing")
    require("invoiced minus expected" in schema, "logical billing-variance contract is missing")
    require("`invoiced_amount - expected_amount`" in policy_text, "audit policy billing expression is missing")
    require("Missing or stale completeness cannot" in policy_text, "audit policy completeness gate is missing")


def validate_result(result: dict, expected: dict, case_id: str) -> None:
    require(result["case_id"] == case_id, f"{case_id} result case mismatch")
    policy = result.get("audit_policy")
    require(isinstance(policy, dict), f"{case_id} audit policy is missing")
    require(policy["id"] == AUDIT_POLICY_ID and policy["version"] == AUDIT_POLICY_VERSION, f"{case_id} audit policy mismatch")
    require(policy["billing_variance_expression"] == "invoiced_amount - expected_amount", f"{case_id} billing expression mismatch")
    require(policy["payment_variance_expression"] == "paid_amount - invoiced_amount", f"{case_id} payment expression mismatch")
    require(policy["realized_variance_expression"] == "paid_amount - expected_amount", f"{case_id} realized expression mismatch")
    require(result["audited_charge"]["item_code"] == "28A", f"{case_id} item code mismatch")
    require(result["audited_charge"]["currency"] == "USD", f"{case_id} currency mismatch")
    require(result["audited_charge"]["interpretation_decision_id"] == INTERPRETATION_DECISION_ID, f"{case_id} decision mismatch")
    require(result["provenance"]["audit_policy"] == [dict(record) for record in AUDIT_POLICY_PROVENANCE], f"{case_id} policy provenance mismatch")
    require(result["provenance"]["observed_invoice_payment"] == [dict(record) for record in AUDIT_SOURCE_PROVENANCE], f"{case_id} observed-data provenance mismatch")
    require(result["provenance"]["expected_charge"] == [dict(record) for record in EXPECTED_CHARGE_PROVENANCE], f"{case_id} expected-charge provenance mismatch")
    require(result["unresolved_assumptions"] == [], f"{case_id} silently introduced an assumption")
    require(result["status"] == expected["status"], f"{case_id} expected {expected['status']}, got {result['status']}")

    finding = result.get("audit_finding")
    require(isinstance(finding, dict), f"{case_id} audit finding is missing")
    if result["status"] == "BLOCKED":
        require(result["human_review_required"] is True, f"{case_id} blocked result must require review")
        require(finding == {"finding_code": "AUDIT_BLOCKED", "finding_status": "OPEN"}, f"{case_id} blocked finding mismatch")
        require("comparison" not in result and "match" not in result, f"{case_id} blocked result exposed authoritative comparison")
        if "blocked_reasons" in expected:
            require(result["blocked_reasons"] == expected["blocked_reasons"], f"{case_id} blocked reasons mismatch: {result['blocked_reasons']}")
        if "blocked_reason_contains" in expected:
            require(any(expected["blocked_reason_contains"] in reason for reason in result["blocked_reasons"]), f"{case_id} lacks expected blocked reason")
        return

    require(result["human_review_required"] is False, f"{case_id} final result requires review")
    require("blocked_reasons" not in result, f"{case_id} final result carries blocked reasons")
    comparison = result.get("comparison")
    match = result.get("match")
    require(isinstance(comparison, dict) and isinstance(match, dict), f"{case_id} final comparison is incomplete")
    require(match["match_status"] == expected["match_status"], f"{case_id} match status mismatch")
    require(finding["billing_finding_code"] == expected["billing_code"], f"{case_id} billing code mismatch")
    require(finding["quantity_finding_code"] == expected["quantity_code"], f"{case_id} quantity code mismatch")
    require(finding["payment_finding_code"] == expected["payment_code"], f"{case_id} payment code mismatch")
    require(finding["finding_status"] == expected["finding_status"], f"{case_id} finding status mismatch")
    for field in (
        "expected_amount",
        "invoiced_amount",
        "paid_amount",
        "billing_variance",
        "payment_variance",
        "realized_variance",
        "quantity_variance",
    ):
        require(comparison[field] == expected[field], f"{case_id} {field} mismatch: {comparison[field]}")
    expected_amount = Decimal(comparison["expected_amount"])
    invoiced_amount = Decimal(comparison["invoiced_amount"])
    paid_amount = Decimal(comparison["paid_amount"])
    require(invoiced_amount - expected_amount == Decimal(comparison["billing_variance"]), f"{case_id} billing variance arithmetic mismatch")
    require(paid_amount - invoiced_amount == Decimal(comparison["payment_variance"]), f"{case_id} payment variance arithmetic mismatch")
    require(paid_amount - expected_amount == Decimal(comparison["realized_variance"]), f"{case_id} realized variance arithmetic mismatch")
    require(Decimal(comparison["invoiced_quantity"]) - Decimal(comparison["expected_quantity"]) == Decimal(comparison["quantity_variance"]), f"{case_id} quantity variance arithmetic mismatch")
    if "current_invoice_version_ids" in expected:
        require(result["input_snapshot"]["current_invoice_version_ids"] == expected["current_invoice_version_ids"], f"{case_id} current invoice selection mismatch")
    if "current_line_version_ids" in expected:
        require(result["input_snapshot"]["current_invoice_line_version_ids"] == expected["current_line_version_ids"], f"{case_id} current line selection mismatch")
    if "current_allocation_ids" in expected:
        require(result["input_snapshot"]["current_payment_allocation_ids"] == expected["current_allocation_ids"], f"{case_id} current allocation selection mismatch")


def validate_tamper_rejection(result: dict, expected: dict) -> None:
    probes = [
        ("policy", "audit_policy.id", "AUDIT-TAMPERED"),
        ("policy provenance", "provenance.audit_policy.0.document_path", "tampered.md"),
        ("expected amount", "comparison.expected_amount", "198.51"),
        ("invoiced amount", "comparison.invoiced_amount", "198.51"),
        ("billing variance", "comparison.billing_variance", "0.01"),
        ("current line", "input_snapshot.current_invoice_line_version_ids.0", "LINEV-TAMPERED"),
        ("finding", "audit_finding.billing_finding_code", "OVERBILLED"),
    ]
    for label, path, value in probes:
        tampered = copy.deepcopy(result)
        set_path(tampered, path, value)
        try:
            validate_result(tampered, expected, result["case_id"])
        except ValidationError:
            print(f"PASS audit result tamper rejected: {label}")
            continue
        raise ValidationError(f"audit result tamper was accepted: {label}")


def main() -> int:
    try:
        validate_contracts()
        suite = load_json(FIXTURE_PATH)
        require(suite.get("fixture_set") == "SYNTHETIC_ITEM_28A_POST_AUDIT_CASES", "fixture set is not labeled synthetic")
        require(suite.get("audit_policy_id") == AUDIT_POLICY_ID, "fixture audit policy mismatch")
        rating_path = (ROOT / suite["rating_fixture_path"]).resolve()
        audit_path = (ROOT / suite["audit_fixture_path"]).resolve()
        require(rating_path.is_relative_to(ROOT) and audit_path.is_relative_to(ROOT), "base fixture path escapes the repository")
        rating_base = load_json(rating_path)
        audit_base = load_json(audit_path)
        require(rating_base.get("data_status") == "SYNTHETIC" and audit_base.get("data_status") == "SYNTHETIC", "audit bases must be synthetic")

        cases = suite.get("cases")
        require(isinstance(cases, list) and cases, "audit fixture suite requires cases")
        seen: set[str] = set()
        tamper_baseline = None
        tamper_expected = None
        for fixture in cases:
            require(isinstance(fixture, dict), "fixture case must be an object")
            case_id = fixture.get("id")
            require(isinstance(case_id, str) and case_id, "fixture case id is required")
            require(case_id not in seen, f"duplicate fixture case id {case_id}")
            seen.add(case_id)

            rating_case = {
                "case_id": f"{case_id}-EXPECTED",
                "data_status": "synthetic",
                "interpretation_decision_id": INTERPRETATION_DECISION_ID,
                "records": copy.deepcopy(rating_base["records"]),
            }
            mutate(rating_case, fixture.get("rating_mutations", []), case_id)
            expected_charge_result = rate_item_28a_extra_pickups(rating_case)
            mutate(expected_charge_result, fixture.get("expected_result_mutations", []), case_id)

            candidate = {
                "case_id": case_id,
                "data_status": "synthetic",
                "as_of_at": suite["as_of_at"],
                "expected_charge_result": expected_charge_result,
                "records": copy.deepcopy(audit_base["records"]),
            }
            mutate(candidate, fixture.get("audit_mutations", []), case_id)
            change_records(candidate, fixture, case_id)
            expected = fixture.get("expected")
            require(isinstance(expected, dict), f"{case_id} expected result is required")
            expected_error = expected.get("input_error_contains")
            try:
                result = audit_item_28a(candidate)
            except AuditInputError as exc:
                require(isinstance(expected_error, str), f"{case_id} unexpectedly raised input error: {exc}")
                require(expected_error in str(exc), f"{case_id} raised the wrong input error: {exc}")
                print(f"PASS {case_id} rejected malformed input: {exc}")
                continue

            require(expected_error is None, f"{case_id} unexpectedly accepted malformed input")
            validate_result(result, expected, case_id)
            print(f"PASS {case_id} {result['status']}")
            if case_id == "AUDIT-28A-CORRECTED-CURRENT-VERSION":
                tamper_baseline = result
                tamper_expected = expected

        require(tamper_baseline is not None and tamper_expected is not None, "audit tamper baseline was not produced")
        validate_tamper_rejection(tamper_baseline, tamper_expected)
        print(f"PASS all {len(cases)} Item 28A post-audit cases and 7 result-tamper probes")
        return 0
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

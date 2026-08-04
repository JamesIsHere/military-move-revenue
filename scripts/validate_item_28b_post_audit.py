#!/usr/bin/env python3
"""Validate the synthetic Item 28B expected/invoiced/paid audit slice."""

from __future__ import annotations

import copy
import json
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.item_28b_extra_delivery import (  # noqa: E402
    INTERPRETATION_DECISION_ID,
    PROVENANCE as EXPECTED_CHARGE_PROVENANCE,
    RULE_IDS as EXPECTED_CHARGE_RULE_IDS,
    RULE_PACKAGE_ID as EXPECTED_CHARGE_RULE_PACKAGE_ID,
    rate_item_28b_extra_deliveries,
)
from rules.item_28b_post_audit import (  # noqa: E402
    AUDIT_POLICY_ID,
    AUDIT_POLICY_PROVENANCE,
    AUDIT_POLICY_VERSION,
    AUDIT_SOURCE_PROVENANCE,
    AuditInputError,
    audit_item_28b,
)


FIXTURE = ROOT / "tests" / "fixtures" / "item-28b-post-audit" / "item-28b-audit-cases.json"
REGISTRY = ROOT / "rules" / "registry" / "registry.json"


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load(path: Path) -> dict:
    def reject_float(value: str) -> None:
        raise ValidationError(f"{path.relative_to(ROOT)} contains non-exact JSON number {value}")

    with path.open(encoding="utf-8") as handle:
        result = json.load(handle, parse_float=reject_float)
    require(isinstance(result, dict), f"{path.relative_to(ROOT)} must contain an object")
    return result


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
        require(isinstance(current, dict), f"mutation parent is invalid: {path}")
        current[final] = value


def mutate(target: dict, mutations: object, case_id: str) -> None:
    require(isinstance(mutations, list), f"{case_id} mutations must be a list")
    for mutation in mutations:
        require(isinstance(mutation, dict), f"{case_id} mutation must be an object")
        set_path(target, mutation.get("path"), mutation.get("value"))


def change_records(candidate: dict, fixture: dict, case_id: str) -> None:
    for collection, record_ids in fixture.get("remove_records", {}).items():
        records = candidate["records"].get(collection)
        require(isinstance(records, list) and isinstance(record_ids, list), f"{case_id} removal is invalid")
        wanted = set(record_ids)
        before = len(records)
        records[:] = [record for record in records if record.get("id") not in wanted]
        require(before - len(records) == len(wanted), f"{case_id} removal record was not found")
    for collection, additions in fixture.get("append_records", {}).items():
        records = candidate["records"].get(collection)
        require(isinstance(records, list) and isinstance(additions, list), f"{case_id} append is invalid")
        records.extend(copy.deepcopy(additions))


def build_case(suite: dict, fixture: dict, rating_base: dict, audit_base: dict) -> dict:
    case_id = fixture["id"]
    rating_case = {
        "case_id": f"{case_id}-EXPECTED",
        "data_status": "synthetic",
        "interpretation_decision_id": INTERPRETATION_DECISION_ID,
        "records": copy.deepcopy(rating_base["records"]),
    }
    mutate(rating_case, fixture.get("rating_mutations", []), case_id)
    change_records(
        rating_case,
        {"append_records": fixture.get("rating_append_records", {})},
        case_id,
    )
    expected_result = rate_item_28b_extra_deliveries(rating_case)
    mutate(expected_result, fixture.get("expected_result_mutations", []), case_id)
    candidate = {
        "case_id": case_id,
        "data_status": "synthetic",
        "as_of_at": suite["as_of_at"],
        "expected_charge_result": expected_result,
        "records": copy.deepcopy(audit_base["records"]),
    }
    mutate(candidate, fixture.get("audit_mutations", []), case_id)
    change_records(candidate, fixture, case_id)
    return candidate


def validate_contracts() -> None:
    registry = load(REGISTRY)
    packages = {record["id"]: record for record in registry["rule_packages"]}
    rules = {record["id"]: record for record in registry["rules"]}
    decisions = {record["id"]: record for record in registry["interpretation_decisions"]}
    claims = {record["id"]: record for record in registry["source_claims"]}
    locators = {record["id"]: record for record in registry["source_locators"]}
    require(packages[EXPECTED_CHARGE_RULE_PACKAGE_ID]["publication_status"] == "published", "Item 28B package is not published")
    require(set(decisions[INTERPRETATION_DECISION_ID]["authorized_rule_ids"]) == set(EXPECTED_CHARGE_RULE_IDS), "Item 28B interpretation scope changed")
    for rule_id in EXPECTED_CHARGE_RULE_IDS:
        require(rules[rule_id]["rule_package_id"] == EXPECTED_CHARGE_RULE_PACKAGE_ID, f"Item 28B rule moved packages: {rule_id}")
        require(rules[rule_id]["publication_status"] == "published", f"Item 28B rule is not published: {rule_id}")
    for reference in AUDIT_SOURCE_PROVENANCE:
        claim = claims[reference["source_claim_id"]]
        locator = locators[reference["source_locator_id"]]
        require(claim["source_locator_id"] == reference["source_locator_id"] and claim["interpretation_status"] == "reviewed", "audit source claim mismatch")
        require(locator["source_version_id"] == reference["source_version_id"], "audit source locator mismatch")
    require(AUDIT_POLICY_ID == "AUDIT-DP3-ITEM-28B-RECONCILIATION-V1", "audit policy id changed")
    require(AUDIT_POLICY_VERSION == "2026-08-04.1", "audit policy version changed")
    for reference in AUDIT_POLICY_PROVENANCE:
        require((ROOT / reference["document_path"]).is_file(), f"policy source is missing: {reference['document_path']}")
    policy = (ROOT / "docs" / "item-28b-post-audit-policy.md").read_text(encoding="utf-8")
    require("`invoiced_amount - expected_amount`" in policy, "billing expression is missing")
    require("Missing or stale completeness cannot" in policy, "completeness gate is missing")


def validate_result(result: dict, expected: dict, case_id: str) -> None:
    require(result["case_id"] == case_id and result["data_status"] == "synthetic", f"{case_id} identity mismatch")
    require(result["audit_policy"]["id"] == AUDIT_POLICY_ID and result["audit_policy"]["version"] == AUDIT_POLICY_VERSION, f"{case_id} policy mismatch")
    require(result["audited_charge"] == {"item_code": "28B", "quantity_unit": "EA", "currency": "USD", "expected_charge_rule_package_id": EXPECTED_CHARGE_RULE_PACKAGE_ID, "interpretation_decision_id": INTERPRETATION_DECISION_ID}, f"{case_id} charge contract mismatch")
    require(result["provenance"]["audit_policy"] == [dict(record) for record in AUDIT_POLICY_PROVENANCE], f"{case_id} policy provenance mismatch")
    require(result["provenance"]["observed_invoice_payment"] == [dict(record) for record in AUDIT_SOURCE_PROVENANCE], f"{case_id} audit provenance mismatch")
    require(result["provenance"]["expected_charge"] == [dict(record) for record in EXPECTED_CHARGE_PROVENANCE], f"{case_id} expected provenance mismatch")
    require(result["unresolved_assumptions"] == [] and result["status"] == expected["status"], f"{case_id} status/assumption mismatch")
    if result["status"] == "BLOCKED":
        require(result["human_review_required"] is True and "comparison" not in result and "match" not in result, f"{case_id} blocked result leaked comparison")
        if "blocked_reasons" in expected:
            require(result["blocked_reasons"] == expected["blocked_reasons"], f"{case_id} blocked reasons mismatch")
        if "blocked_reason_contains" in expected:
            require(any(expected["blocked_reason_contains"] in reason for reason in result["blocked_reasons"]), f"{case_id} blocker missing")
        return
    comparison, finding, match = result["comparison"], result["audit_finding"], result["match"]
    require(result["human_review_required"] is False and match["match_status"] == expected["match_status"], f"{case_id} final/match mismatch")
    require(finding["billing_finding_code"] == expected["billing_code"] and finding["quantity_finding_code"] == expected["quantity_code"] and finding["payment_finding_code"] == expected["payment_code"] and finding["finding_status"] == expected["finding_status"], f"{case_id} finding mismatch")
    for field in ("expected_amount", "invoiced_amount", "paid_amount", "billing_variance", "payment_variance", "realized_variance", "quantity_variance"):
        require(comparison[field] == expected[field], f"{case_id} {field} mismatch")
    expected_amount, invoiced, paid = map(Decimal, (comparison["expected_amount"], comparison["invoiced_amount"], comparison["paid_amount"]))
    require(invoiced - expected_amount == Decimal(comparison["billing_variance"]), f"{case_id} billing arithmetic mismatch")
    require(paid - invoiced == Decimal(comparison["payment_variance"]) and paid - expected_amount == Decimal(comparison["realized_variance"]), f"{case_id} payment arithmetic mismatch")
    if "current_invoice_version_ids" in expected:
        require(result["input_snapshot"]["current_invoice_version_ids"] == expected["current_invoice_version_ids"], f"{case_id} current invoice mismatch")
    if "current_line_version_ids" in expected:
        require(result["input_snapshot"]["current_invoice_line_version_ids"] == expected["current_line_version_ids"], f"{case_id} current line mismatch")


def validate_tampers(result: dict, expected: dict) -> None:
    probes = [("policy", "audit_policy.id", "BAD"), ("policy provenance", "provenance.audit_policy.0.document_path", "bad.md"), ("expected", "comparison.expected_amount", "198.51"), ("invoiced", "comparison.invoiced_amount", "198.51"), ("variance", "comparison.billing_variance", "0.01"), ("line", "input_snapshot.current_invoice_line_version_ids.0", "BAD"), ("finding", "audit_finding.billing_finding_code", "OVERBILLED")]
    for label, path, value in probes:
        changed = copy.deepcopy(result)
        set_path(changed, path, value)
        try:
            validate_result(changed, expected, changed["case_id"])
        except ValidationError:
            print(f"PASS Item 28B audit tamper rejected: {label}")
            continue
        raise ValidationError(f"accepted Item 28B audit tamper: {label}")


def main() -> int:
    try:
        validate_contracts()
        suite = load(FIXTURE)
        require(suite.get("fixture_set") == "SYNTHETIC_ITEM_28B_POST_AUDIT_CASES" and suite.get("audit_policy_id") == AUDIT_POLICY_ID, "fixture contract mismatch")
        rating_base = load((ROOT / suite["rating_fixture_path"]).resolve())
        audit_base = load((ROOT / suite["audit_fixture_path"]).resolve())
        require(rating_base.get("data_status") == "SYNTHETIC" and audit_base.get("data_status") == "SYNTHETIC", "bases must be synthetic")
        baseline = None
        baseline_expected = None
        seen: set[str] = set()
        for fixture in suite["cases"]:
            case_id = fixture["id"]
            require(case_id not in seen, f"duplicate case {case_id}")
            seen.add(case_id)
            candidate = build_case(suite, fixture, rating_base, audit_base)
            expected = fixture["expected"]
            try:
                result = audit_item_28b(candidate)
            except AuditInputError as exc:
                require(expected.get("input_error_contains") in str(exc), f"{case_id} wrong input error: {exc}")
                print(f"PASS {case_id} rejected malformed input: {exc}")
                continue
            require("input_error_contains" not in expected, f"{case_id} accepted malformed input")
            validate_result(result, expected, case_id)
            print(f"PASS {case_id} {result['status']}")
            if case_id == "AUDIT-28B-CORRECTED-CURRENT-VERSION":
                baseline, baseline_expected = result, expected
        require(baseline is not None and baseline_expected is not None, "tamper baseline missing")
        validate_tampers(baseline, baseline_expected)
        print(f"PASS all {len(suite['cases'])} Item 28B post-audit cases and 7 result-tamper probes")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate deterministic 2026 400NG Item 28A shadow rating."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.item_28a_extra_pickup import (  # noqa: E402
    APPROVAL_REQUIREMENT_ID,
    ELIGIBILITY_RULE_ID,
    INTERPRETATION_DECISION_ID,
    PERFORMANCE_REQUIREMENT_ID,
    PROVENANCE,
    RATE_DATE_REQUIREMENT_ID,
    RATING_RULE_ID,
    RULE_IDS,
    RULE_PACKAGE_ID,
    SOURCE_CONTRACT_RULE_ID,
    RuleInputError,
    rate_item_28a_extra_pickups,
)


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "item-28a-extra-pickup" / "item-28a-cases.json"
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
        before = len(records)
        wanted = set(record_ids)
        records[:] = [record for record in records if record.get("id") not in wanted]
        require(before - len(records) == len(wanted), f"{case_id} removal id was not found in {collection}")

    append_records = fixture.get("append_records", {})
    require(isinstance(append_records, dict), f"{case_id} append_records must be an object")
    for collection, additions in append_records.items():
        records = candidate["records"].get(collection)
        require(isinstance(records, list), f"{case_id} unknown append collection {collection}")
        require(isinstance(additions, list), f"{case_id} appended records must be a list")
        records.extend(copy.deepcopy(additions))


def validate_registry_contract() -> None:
    registry = load_json(REGISTRY_PATH)
    packages = {record["id"]: record for record in registry["rule_packages"]}
    rules = {record["id"]: record for record in registry["rules"]}
    claims = {record["id"]: record for record in registry["source_claims"]}
    locators = {record["id"]: record for record in registry["source_locators"]}
    decisions = {record["id"]: record for record in registry["interpretation_decisions"]}

    require(RULE_PACKAGE_ID in packages, "Item 28A package is missing")
    package = packages[RULE_PACKAGE_ID]
    require(package["publication_status"] == "published", "Item 28A package is not published")
    require(package["effective_from"] == "2026-05-15" and package["effective_to"] == "2027-05-14", "Item 28A package has the wrong effective period")

    require(INTERPRETATION_DECISION_ID in decisions, "Item 28A interpretation decision is missing")
    decision = decisions[INTERPRETATION_DECISION_ID]
    require(decision["decision_status"] == "approved", "Item 28A interpretation is not approved")
    require(set(decision["authorized_rule_ids"]) == set(RULE_IDS), "Item 28A decision does not authorize the complete package")
    require(set(decision["cited_claim_ids"]) == {reference["source_claim_id"] for reference in PROVENANCE}, "Item 28A decision claim set differs from the evaluator")

    for rule_id in RULE_IDS:
        require(rule_id in rules, f"Item 28A rule is missing: {rule_id}")
        rule = rules[rule_id]
        require(rule["rule_package_id"] == RULE_PACKAGE_ID, f"{rule_id} uses the wrong package")
        require(rule["implementation_status"] == "implemented", f"{rule_id} is not implemented")
        require(rule["publication_status"] == "published", f"{rule_id} is not published")
        require(rule["blocked_by_conflict_ids"] == [], f"{rule_id} is unexpectedly conflict-blocked")
        require(rule["approved_interpretation_decision_ids"] == [INTERPRETATION_DECISION_ID], f"{rule_id} lacks the approved decision link")

    dependencies = [record for record in registry["rule_dependencies"] if record["rule_id"] in RULE_IDS]
    require(
        {record["input_fact_type"] for record in dependencies}
        == {
            "original_requested_pickup_date",
            "approved_interpretation_decision",
            "immutable_shipment_stop",
            "service_performance_event",
            "origin_ppso_approval_event",
            "reviewed_service_evidence",
            "eligible_item_28a_occurrence_count",
        },
        "Item 28A dependencies are incomplete",
    )
    evidence = [record for record in registry["evidence_requirements"] if record["rule_id"] in RULE_IDS]
    require(
        {record["id"] for record in evidence}
        == {APPROVAL_REQUIREMENT_ID, PERFORMANCE_REQUIREMENT_ID, RATE_DATE_REQUIREMENT_ID},
        "Item 28A evidence requirements are incomplete",
    )

    for reference in PROVENANCE:
        claim_id = reference["source_claim_id"]
        locator_id = reference["source_locator_id"]
        require(claim_id in claims, f"evaluator claim missing from registry: {claim_id}")
        require(locator_id in locators, f"evaluator locator missing from registry: {locator_id}")
        require(claims[claim_id]["source_locator_id"] == locator_id, f"claim {claim_id} uses a different locator")
        require(claims[claim_id]["interpretation_status"] == "reviewed", f"claim {claim_id} is not reviewed")
        require(locators[locator_id]["source_version_id"] == reference["source_version_id"], f"locator {locator_id} uses a different source version")


def validate_result(result: dict, expected: dict, case_id: str) -> None:
    require(result["case_id"] == case_id, f"{case_id} result case mismatch")
    require(result["rule_package_id"] == RULE_PACKAGE_ID, f"{case_id} package mismatch")
    require(result["rule_ids"] == list(RULE_IDS), f"{case_id} rule sequence mismatch")
    require(result["interpretation_decision_id"] == INTERPRETATION_DECISION_ID, f"{case_id} decision mismatch")
    require(result["status"] == expected["status"], f"{case_id} expected {expected['status']}, got {result['status']}")
    require(result["unresolved_assumptions"] == [], f"{case_id} silently introduced an assumption")
    require(result["provenance"] == [dict(reference) for reference in PROVENANCE], f"{case_id} provenance differs from the published evaluator")
    require(result["source_contract"]["item_code"] == "28A", f"{case_id} item code mismatch")
    require(result["source_contract"]["quantity_unit"] == "EA", f"{case_id} source unit mismatch")
    require(result["source_contract"]["rate_source_cell"] == "Additional Rates!A13:F13", f"{case_id} rate cell mismatch")
    require(
        result["evidence"]
        == {
            "approval_requirement_id": APPROVAL_REQUIREMENT_ID,
            "performance_requirement_id": PERFORMANCE_REQUIREMENT_ID,
            "rate_date_requirement_id": RATE_DATE_REQUIREMENT_ID,
        },
        f"{case_id} evidence contract mismatch",
    )

    if result["status"] == "BLOCKED":
        require(result["human_review_required"] is True, f"{case_id} blocked result must require review")
        require(result["blocked_reasons"] == expected["blocked_reasons"], f"{case_id} blocked reasons mismatch")
        require(result["eligible_occurrence_count"] is None, f"{case_id} blocked result exposed an occurrence count")
        require("calculation" not in result and "eligibility" not in result, f"{case_id} blocked result exposed money or eligibility")
        require("expected_line_action" not in result, f"{case_id} blocked result exposed a line action")
        return

    require(result["human_review_required"] is False, f"{case_id} final result requires review")
    require("blocked_reasons" not in result, f"{case_id} final result carries blocked reasons")
    eligibility = result["eligibility"]
    calculation = result["calculation"]
    require(eligibility["eligible_occurrence_count"] == expected["count"], f"{case_id} occurrence count mismatch")
    require(len(eligibility["counted_service_performance_ids"]) == expected["count"], f"{case_id} counted id cardinality mismatch")
    require(calculation["operation"] == "MULTIPLY", f"{case_id} operation mismatch")
    require(calculation["quantity"] == str(expected["count"]), f"{case_id} quantity mismatch")
    require(calculation["quantity_unit"] == "EA", f"{case_id} quantity unit mismatch")
    require(calculation["unit_rate"] == "198.50", f"{case_id} unit rate mismatch")
    require(calculation["expected_amount"] == expected["amount"], f"{case_id} exact amount mismatch")
    require(calculation["unrounded_amount"] == expected["amount"], f"{case_id} unrounded amount mismatch")
    require(calculation["currency"] == "USD", f"{case_id} currency mismatch")
    require(calculation["rounding"] == "NONE_EXACT_INTEGER_MULTIPLICATION", f"{case_id} rounding contract mismatch")
    require(result["expected_line_action"] == expected["line_action"], f"{case_id} line action mismatch")
    if "ineligible_reason" in expected:
        require(
            [record["reason_code"] for record in eligibility["ineligible_occurrences"]] == [expected["ineligible_reason"]],
            f"{case_id} ineligible reason mismatch",
        )


def validate_tamper_rejection(result: dict, expected: dict) -> None:
    probes = [
        ("package", "rule_package_id", "RP-TAMPERED"),
        ("decision", "interpretation_decision_id", "INT-TAMPERED"),
        ("rule sequence", "rule_ids", [SOURCE_CONTRACT_RULE_ID, RATING_RULE_ID]),
        ("provenance", "provenance.0.source_claim_id", "CLM-TAMPERED"),
        ("amount", "calculation.expected_amount", "198.51"),
    ]
    for label, path, value in probes:
        tampered = copy.deepcopy(result)
        set_path(tampered, path, value)
        try:
            validate_result(tampered, expected, result["case_id"])
        except ValidationError:
            print(f"PASS result tamper rejected: {label}")
            continue
        raise ValidationError(f"result tamper was accepted: {label}")


def main() -> int:
    try:
        validate_registry_contract()
        suite = load_json(FIXTURE_PATH)
        require(suite.get("fixture_set") == "SYNTHETIC_2026_ITEM_28A_EXTRA_PICKUP_CASES", "fixture set is not labeled synthetic")
        require(suite.get("provenance", {}).get("interpretation_decision_id") == INTERPRETATION_DECISION_ID, "fixture decision provenance mismatch")
        base_path = (ROOT / suite["base_fixture_path"]).resolve()
        require(base_path.is_relative_to(ROOT), "base fixture path escapes the repository")
        base = load_json(base_path)
        require(base.get("data_status") == "SYNTHETIC", "base logical fixture must be synthetic")
        require(base.get("scenario_type") == "item_28a_extra_pickup_facts", "base logical fixture has the wrong scenario")

        cases = suite.get("cases")
        require(isinstance(cases, list) and cases, "Item 28A fixture suite requires cases")
        ids: set[str] = set()
        baseline_result = None
        baseline_expected = None
        for fixture in cases:
            require(isinstance(fixture, dict), "fixture case must be an object")
            case_id = fixture.get("id")
            require(isinstance(case_id, str) and case_id, "fixture case id is required")
            require(case_id not in ids, f"duplicate fixture case id {case_id}")
            ids.add(case_id)

            candidate = {
                "case_id": case_id,
                "data_status": "synthetic",
                "interpretation_decision_id": INTERPRETATION_DECISION_ID,
                "records": copy.deepcopy(base["records"]),
            }
            mutate(candidate, fixture.get("mutations", []), case_id)
            change_records(candidate, fixture, case_id)
            mutate(candidate, fixture.get("case_mutations", []), case_id)
            expected = fixture.get("expected")
            require(isinstance(expected, dict), f"{case_id} expected result is required")
            expected_error = expected.get("input_error_contains")
            try:
                result = rate_item_28a_extra_pickups(candidate)
            except RuleInputError as exc:
                require(isinstance(expected_error, str), f"{case_id} unexpectedly raised input error: {exc}")
                require(expected_error in str(exc), f"{case_id} raised the wrong input error: {exc}")
                print(f"PASS {case_id} rejected malformed input: {exc}")
                continue

            require(expected_error is None, f"{case_id} unexpectedly accepted malformed input")
            validate_result(result, expected, case_id)
            print(f"PASS {case_id} {result['status']}")
            if case_id == "ITEM-28A-BOUNDARY-START":
                baseline_result = result
                baseline_expected = expected

        require(baseline_result is not None and baseline_expected is not None, "tamper baseline was not produced")
        validate_tamper_rejection(baseline_result, baseline_expected)
        print(f"PASS all {len(cases)} Item 28A cases and 5 result-tamper probes")
        return 0
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

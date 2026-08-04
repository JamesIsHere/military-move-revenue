#!/usr/bin/env python3
"""Validate deterministic 2026 400NG Item 28B shadow rating."""

from __future__ import annotations

import copy
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.item_28b_extra_delivery import (  # noqa: E402
    APPROVAL_REQUIREMENT_ID, INTERPRETATION_DECISION_ID, PERFORMANCE_REQUIREMENT_ID,
    PROVENANCE, RATE_DATE_REQUIREMENT_ID, RULE_IDS, RULE_PACKAGE_ID, RuleInputError,
    rate_item_28b_extra_deliveries,
)

FIXTURE = ROOT / "tests" / "fixtures" / "item-28b-extra-delivery" / "item-28b-cases.json"
REGISTRY = ROOT / "rules" / "registry" / "registry.json"


class ValidationError(Exception): pass


def require(value: bool, message: str) -> None:
    if not value: raise ValidationError(message)


def load(path: Path) -> dict:
    def no_float(value: str) -> None: raise ValidationError(f"{path.name} contains JSON float {value}")
    with path.open(encoding="utf-8") as handle: value = json.load(handle, parse_float=no_float)
    require(isinstance(value, dict), f"{path.name} must contain an object")
    return value


def set_path(target: object, path: object, value: object) -> None:
    require(isinstance(path, str) and path, "mutation path required")
    current = target
    parts = path.split(".")
    for part in parts[:-1]:
        if isinstance(current, list): current = current[int(part)]
        else: current = current[part]  # type: ignore[index]
    if isinstance(current, list): current[int(parts[-1])] = value
    else: current[parts[-1]] = value  # type: ignore[index]


def mutate(target: dict, changes: object) -> None:
    require(isinstance(changes, list), "mutations must be a list")
    for change in changes: set_path(target, change["path"], change.get("value"))


def change_records(candidate: dict, fixture: dict) -> None:
    for collection, ids in fixture.get("remove_records", {}).items():
        records = candidate["records"][collection]
        before = len(records)
        records[:] = [value for value in records if value.get("id") not in set(ids)]
        require(before - len(records) == len(ids), "removal record not found")
    for collection, additions in fixture.get("append_records", {}).items():
        candidate["records"][collection].extend(copy.deepcopy(additions))


def validate_registry(registry: dict) -> None:
    packages = {value["id"]: value for value in registry["rule_packages"]}
    rules = {value["id"]: value for value in registry["rules"]}
    decisions = {value["id"]: value for value in registry["interpretation_decisions"]}
    claims = {value["id"]: value for value in registry["source_claims"]}
    locators = {value["id"]: value for value in registry["source_locators"]}
    package = packages.get(RULE_PACKAGE_ID)
    require(isinstance(package, dict) and package.get("publication_status") == "published", "Item 28B package is not published")
    require(package.get("effective_from") == "2026-05-15" and package.get("effective_to") == "2027-05-14", "Item 28B effective period mismatch")
    decision = decisions.get(INTERPRETATION_DECISION_ID)
    require(isinstance(decision, dict) and decision.get("decision_status") == "approved", "Item 28B decision is not approved")
    require(set(decision["authorized_rule_ids"]) == set(RULE_IDS), "Item 28B authorized rule set mismatch")
    require(set(decision["cited_claim_ids"]) == {value["source_claim_id"] for value in PROVENANCE}, "Item 28B decision/evaluator claims mismatch")
    for rule_id in RULE_IDS:
        rule = rules.get(rule_id)
        require(isinstance(rule, dict) and rule.get("rule_package_id") == RULE_PACKAGE_ID, f"{rule_id} package mismatch")
        require(rule.get("implementation_status") == "implemented" and rule.get("publication_status") == "published", f"{rule_id} is not published")
        require(rule.get("approved_interpretation_decision_ids") == [INTERPRETATION_DECISION_ID], f"{rule_id} decision link mismatch")
    dependencies = {value["input_fact_type"] for value in registry["rule_dependencies"] if value["rule_id"] in RULE_IDS}
    require(dependencies == {"actual_pickup_date", "approved_interpretation_decision", "immutable_shipment_stop", "service_performance_event", "government_authorization_event", "reviewed_service_evidence", "eligible_item_28b_occurrence_count"}, "Item 28B dependencies incomplete")
    evidence = {value["id"] for value in registry["evidence_requirements"] if value["rule_id"] in RULE_IDS}
    require(evidence == {APPROVAL_REQUIREMENT_ID, PERFORMANCE_REQUIREMENT_ID, RATE_DATE_REQUIREMENT_ID}, "Item 28B evidence incomplete")
    for reference in PROVENANCE:
        claim, locator = claims[reference["source_claim_id"]], locators[reference["source_locator_id"]]
        require(claim["source_locator_id"] == reference["source_locator_id"] and claim["interpretation_status"] == "reviewed", "Item 28B claim contract mismatch")
        require(locator["source_version_id"] == reference["source_version_id"], "Item 28B locator/version mismatch")


def validate_result(result: dict, expected: dict, case_id: str) -> None:
    require(result["case_id"] == case_id and result["rule_package_id"] == RULE_PACKAGE_ID, f"{case_id} identity mismatch")
    require(result["rule_ids"] == list(RULE_IDS) and result["interpretation_decision_id"] == INTERPRETATION_DECISION_ID, f"{case_id} rule/decision mismatch")
    require(result["provenance"] == [dict(value) for value in PROVENANCE] and result["unresolved_assumptions"] == [], f"{case_id} provenance/assumption mismatch")
    require(
        result["source_contract"]
        == {
            "item_code": "28B",
            "quantity_unit": "EA",
            "rate_date_role": "ACTUAL_PICKUP",
            "rate_effective_from": "2026-05-15",
            "rate_effective_to": "2027-05-14",
            "rate_source_cell": "Additional Rates!A13:F13",
        },
        f"{case_id} source contract mismatch",
    )
    require(
        result["evidence"]
        == {
            "approval_requirement_id": APPROVAL_REQUIREMENT_ID,
            "performance_requirement_id": PERFORMANCE_REQUIREMENT_ID,
            "rate_date_requirement_id": RATE_DATE_REQUIREMENT_ID,
        },
        f"{case_id} evidence contract mismatch",
    )
    require(result["status"] == expected["status"], f"{case_id} status mismatch")
    if result["status"] == "BLOCKED":
        require(result["blocked_reasons"] == expected["blocked_reasons"] and result["human_review_required"] is True, f"{case_id} block mismatch")
        require("calculation" not in result and "eligibility" not in result and result["eligible_occurrence_count"] is None, f"{case_id} blocked money leak")
        require("expected_line_action" not in result, f"{case_id} blocked line-action leak")
        return
    eligibility, calculation = result["eligibility"], result["calculation"]
    require(result["human_review_required"] is False and "blocked_reasons" not in result, f"{case_id} final-state mismatch")
    require(eligibility["eligible_occurrence_count"] == expected["count"], f"{case_id} count mismatch")
    require(len(eligibility["counted_service_performance_ids"]) == expected["count"], f"{case_id} counted ID cardinality mismatch")
    require(calculation["operation"] == "MULTIPLY", f"{case_id} operation mismatch")
    require(calculation["quantity"] == str(expected["count"]) and calculation["quantity_unit"] == "EA", f"{case_id} quantity mismatch")
    require(calculation["expected_amount"] == expected["amount"] and calculation["unrounded_amount"] == expected["amount"], f"{case_id} amount mismatch")
    require(calculation["unit_rate"] == "198.50" and calculation["rate_unit"] == "USD_per_occurrence", f"{case_id} rate mismatch")
    require(calculation["currency"] == "USD" and calculation["rounding"] == "NONE_EXACT_INTEGER_MULTIPLICATION", f"{case_id} money contract mismatch")
    require(Decimal(calculation["quantity"]) * Decimal(calculation["unit_rate"]) == Decimal(calculation["expected_amount"]), f"{case_id} arithmetic mismatch")
    require(result["expected_line_action"] == expected["line_action"], f"{case_id} line action mismatch")
    if "ineligible_reason" in expected:
        require([value["reason_code"] for value in eligibility["ineligible_occurrences"]] == [expected["ineligible_reason"]], f"{case_id} ineligible reason mismatch")


def main() -> int:
    try:
        suite, registry = load(FIXTURE), load(REGISTRY)
        validate_registry(registry)
        base_path = (ROOT / suite["base_fixture_path"]).resolve()
        require(base_path.is_relative_to(ROOT), "base path escapes repository")
        base = load(base_path)
        require(base.get("data_status") == "SYNTHETIC", "base is not synthetic")
        baseline = None
        for fixture in suite["cases"]:
            case_id = fixture["id"]
            candidate = {"case_id": case_id, "data_status": "synthetic", "interpretation_decision_id": INTERPRETATION_DECISION_ID, "records": copy.deepcopy(base["records"])}
            mutate(candidate, fixture.get("case_mutations", [])); mutate(candidate, fixture.get("mutations", [])); change_records(candidate, fixture)
            expected = fixture["expected"]
            try: result = rate_item_28b_extra_deliveries(candidate)
            except RuleInputError as exc:
                require(expected.get("input_error_contains") in str(exc), f"{case_id} wrong input error: {exc}")
                print(f"PASS {case_id} rejected malformed input")
                continue
            require("input_error_contains" not in expected, f"{case_id} accepted malformed input")
            validate_result(result, expected, case_id); print(f"PASS {case_id} {result['status']}")
            if case_id == "ITEM-28B-BOUNDARY-START": baseline = (result, expected)
        require(baseline is not None, "tamper baseline missing")
        probes = [("package", "rule_package_id", "BAD"), ("decision", "interpretation_decision_id", "BAD"), ("rules", "rule_ids", []), ("provenance", "provenance.0.source_claim_id", "BAD"), ("amount", "calculation.expected_amount", "198.51")]
        for label, path, value in probes:
            changed = copy.deepcopy(baseline[0]); set_path(changed, path, value)
            try: validate_result(changed, baseline[1], changed["case_id"])
            except ValidationError: print(f"PASS Item 28B result tamper rejected: {label}")
            else: raise ValidationError(f"accepted result tamper: {label}")
        print(f"PASS all {len(suite['cases'])} Item 28B cases and 5 result-tamper probes")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr); return 1


if __name__ == "__main__": raise SystemExit(main())

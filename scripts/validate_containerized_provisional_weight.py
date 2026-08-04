#!/usr/bin/env python3
"""Validate the 2026 containerized provisional-weight package."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.containerized_provisional_weight import (  # noqa: E402
    CALCULATION_RULE_ID,
    INITIAL_RESULT_EVIDENCE_REQUIREMENT_ID,
    NEW_GROSS_EVIDENCE_REQUIREMENT_ID,
    ORIGINAL_TARE_EVIDENCE_REQUIREMENT_ID,
    PROVENANCE,
    RULE_IDS,
    RULE_PACKAGE_ID,
    SELECTION_RULE_ID,
    RuleInputError,
    determine_containerized_provisional_weight,
)
from rules.weight_determination import (  # noqa: E402
    RuleInputError as InitialWeightInputError,
    determine_initial_scale_weight,
)


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "containerized-provisional-weight" / "provisional-weight-cases.json"
REGISTRY_PATH = ROOT / "rules" / "registry" / "registry.json"


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain an object")
    return value


def set_path(target: object, path: object, value: object, case_id: str) -> None:
    require(isinstance(path, str) and path, f"{case_id} mutation path is required")
    parts = path.split(".")
    current = target
    for part in parts[:-1]:
        if isinstance(current, list):
            require(part.isdigit() and int(part) < len(current), f"{case_id} mutation path not found: {path}")
            current = current[int(part)]
        else:
            require(isinstance(current, dict) and part in current, f"{case_id} mutation path not found: {path}")
            current = current[part]
    final = parts[-1]
    if isinstance(current, list):
        require(final.isdigit() and int(final) < len(current), f"{case_id} mutation path not found: {path}")
        current[int(final)] = value
    else:
        require(isinstance(current, dict), f"{case_id} mutation parent is not an object")
        current[final] = value


def apply_path_mutations(target: dict, mutations: object, case_id: str) -> None:
    require(isinstance(mutations, list), f"{case_id} path mutations must be a list")
    for mutation in mutations:
        require(isinstance(mutation, dict), f"{case_id} path mutation must be an object")
        set_path(target, mutation.get("path"), mutation.get("value"), case_id)


def apply_record_mutations(records: dict, mutations: object, case_id: str) -> None:
    require(isinstance(mutations, list), f"{case_id} record mutations must be a list")
    for mutation in mutations:
        require(isinstance(mutation, dict), f"{case_id} record mutation must be an object")
        collection_name = mutation.get("collection")
        collection = records.get(collection_name)
        require(isinstance(collection, list), f"{case_id} mutation collection not found: {collection_name}")
        matches = [record for record in collection if record.get("id") == mutation.get("id")]
        require(len(matches) == 1, f"{case_id} mutation record not found: {mutation.get('id')}")
        field = mutation.get("field")
        require(isinstance(field, str) and field, f"{case_id} record mutation field is required")
        require(mutation.get("op") == "set", f"{case_id} unsupported record mutation operation")
        matches[0][field] = mutation.get("value")


def validate_registry_contract() -> None:
    registry = load_json(REGISTRY_PATH)
    packages = {record["id"]: record for record in registry["rule_packages"]}
    rules = {record["id"]: record for record in registry["rules"]}
    claims = {record["id"]: record for record in registry["source_claims"]}
    locators = {record["id"]: record for record in registry["source_locators"]}
    dependencies = registry["rule_dependencies"]
    evidence = registry["evidence_requirements"]
    sources = registry["rule_sources"]

    require(RULE_PACKAGE_ID in packages, "containerized provisional-weight package is missing")
    package = packages[RULE_PACKAGE_ID]
    require(package["version"] == "2026.containerized-provisional-weight.1", "containerized package version mismatch")
    require(package["publication_status"] == "published", "containerized provisional-weight package is not published")
    for rule_id in RULE_IDS:
        require(rule_id in rules, f"containerized provisional rule is missing: {rule_id}")
        require(rules[rule_id]["rule_package_id"] == RULE_PACKAGE_ID, f"{rule_id} uses the wrong package")
        require(rules[rule_id]["implementation_status"] == "implemented", f"{rule_id} is not implemented")
        require(rules[rule_id]["publication_status"] == "published", f"{rule_id} is not published")
        require(not rules[rule_id]["blocked_by_conflict_ids"], f"{rule_id} is unexpectedly conflict-blocked")

    deps_by_rule = {
        rule_id: {record["input_fact_type"] for record in dependencies if record["rule_id"] == rule_id}
        for rule_id in RULE_IDS
    }
    require(
        deps_by_rule[CALCULATION_RULE_ID] == {"original_tare_scale_weight", "new_gross_scale_weight"},
        "containerized provisional calculation dependencies are incomplete",
    )
    require(
        deps_by_rule[SELECTION_RULE_ID]
        == {"final_initial_net_scale_weight_result", "final_containerized_provisional_net_weight_result"},
        "containerized provisional selection dependencies are incomplete",
    )
    evidence_ids = {record["id"] for record in evidence if record["rule_id"] in RULE_IDS}
    require(
        evidence_ids
        == {
            ORIGINAL_TARE_EVIDENCE_REQUIREMENT_ID,
            NEW_GROSS_EVIDENCE_REQUIREMENT_ID,
            INITIAL_RESULT_EVIDENCE_REQUIREMENT_ID,
        },
        "containerized provisional evidence requirements are incomplete",
    )
    for rule_id in RULE_IDS:
        require(
            {record["source_claim_id"] for record in sources if record["rule_id"] == rule_id} == {"CLM-0027"},
            f"{rule_id} must use only CLM-0027",
        )
    reference = PROVENANCE[0]
    require(claims[reference["source_claim_id"]]["source_locator_id"] == reference["source_locator_id"], "CLM-0027 locator mismatch")
    require(claims[reference["source_claim_id"]]["interpretation_status"] == "reviewed", "CLM-0027 is not reviewed")
    require(locators[reference["source_locator_id"]]["source_version_id"] == reference["source_version_id"], "LOC-0023 source mismatch")


def validate_result(result: dict, expected: dict, case_id: str) -> None:
    require(result.get("case_id") == case_id, f"{case_id} case mismatch")
    require(result.get("rule_package_id") == RULE_PACKAGE_ID, f"{case_id} package mismatch")
    require(result.get("rule_ids") == list(RULE_IDS), f"{case_id} rule set mismatch")
    require(result.get("status") == expected.get("status"), f"{case_id} status mismatch")
    require(result.get("provenance") == list(PROVENANCE), f"{case_id} provenance mismatch")
    require(result.get("unresolved_assumptions") == [], f"{case_id} silently introduced an assumption")
    evidence = result.get("evidence", {})
    require(evidence.get("original_tare_requirement_id") == ORIGINAL_TARE_EVIDENCE_REQUIREMENT_ID, f"{case_id} original-tare evidence mismatch")
    require(evidence.get("new_gross_requirement_id") == NEW_GROSS_EVIDENCE_REQUIREMENT_ID, f"{case_id} new-gross evidence mismatch")
    require(evidence.get("initial_result_requirement_id") == INITIAL_RESULT_EVIDENCE_REQUIREMENT_ID, f"{case_id} initial-result evidence mismatch")

    forbidden_fragments = ("new_tare", "tolerance", "reimbursement", "fee", "refund", "billing", "item_code", "amount", "currency")
    def check_scope(value: object) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                require(not any(fragment in key.lower() for fragment in forbidden_fragments), f"{case_id} crossed rule scope at {key}")
                check_scope(child)
        elif isinstance(value, list):
            for child in value:
                check_scope(child)
    check_scope(result)

    if result["status"] == "FINAL":
        require(result.get("human_review_required") is False, f"{case_id} final result requires review")
        require("blocked_reasons" not in result, f"{case_id} final result carries blocked reasons")
        calculation = result.get("calculation")
        selection = result.get("selection")
        require(isinstance(calculation, dict) and isinstance(selection, dict), f"{case_id} final result is incomplete")
        require(calculation.get("result") == expected.get("provisional_net_weight"), f"{case_id} provisional result mismatch")
        require(calculation.get("result_unit") == "lb", f"{case_id} provisional unit mismatch")
        require(calculation.get("rounding_rule") == "NONE_SOURCE_DOES_NOT_SPECIFY_ROUNDING", f"{case_id} rounding rule mismatch")
        for field in ("selected_weight", "selected_source", "initial_net_weight", "provisional_net_weight"):
            require(selection.get(field) == expected.get(field), f"{case_id} {field} mismatch")
        require(selection.get("comparison_method") == "LOWER_OF_INITIAL_AND_CONTAINERIZED_PROVISIONAL_WEIGHT", f"{case_id} method mismatch")
        require(selection.get("weight_unit") == "lb", f"{case_id} selected unit mismatch")
    else:
        require(result.get("human_review_required") is True, f"{case_id} blocked result must require review")
        require("calculation" not in result and "selection" not in result, f"{case_id} blocked result must omit authoritative outputs")
        require(result.get("blocked_reasons") == expected.get("blocked_reasons"), f"{case_id} blocked reasons mismatch")
        if "upstream_blocked_reasons" in expected:
            require(result.get("upstream_blocked_reasons") == expected["upstream_blocked_reasons"], f"{case_id} upstream blockers mismatch")


def main() -> int:
    try:
        validate_registry_contract()
        suite = load_json(FIXTURE_PATH)
        require(suite.get("fixture_set") == "SYNTHETIC_CONTAINERIZED_PROVISIONAL_WEIGHT_CASES", "fixture set is not labeled synthetic")
        fact_path = (ROOT / suite["containerized_facts_fixture_path"]).resolve()
        initial_path = (ROOT / suite["initial_weight_fixture_path"]).resolve()
        require(fact_path.is_relative_to(ROOT) and initial_path.is_relative_to(ROOT), "fixture path escapes repository")
        fact_fixture = load_json(fact_path)
        initial_base = load_json(initial_path).get("base_case")
        require(fact_fixture.get("data_status") == "SYNTHETIC", "containerized facts must be synthetic")
        require(isinstance(initial_base, dict) and initial_base.get("data_status") == "synthetic", "initial base must be synthetic")

        cases = suite.get("cases")
        require(isinstance(cases, list) and cases, "containerized provisional suite requires cases")
        for fixture in cases:
            require(isinstance(fixture, dict), "fixture case must be an object")
            case_id = fixture.get("id")
            require(isinstance(case_id, str) and case_id, "fixture case id is required")

            initial_case = copy.deepcopy(initial_base)
            initial_case["case_id"] = f"{case_id}-INITIAL"
            apply_path_mutations(initial_case, fixture.get("initial_weight_mutations", []), case_id)
            initial_result = determine_initial_scale_weight(initial_case)
            apply_path_mutations(initial_result, fixture.get("initial_result_mutations", []), case_id)

            provisional_records = copy.deepcopy(fact_fixture["records"])
            apply_record_mutations(provisional_records, fixture.get("record_mutations", []), case_id)
            candidate = {
                "case_id": case_id,
                "data_status": "synthetic",
                "records": provisional_records,
                "initial_weight_result": initial_result,
            }
            expected = fixture.get("expected")
            require(isinstance(expected, dict), f"{case_id} expected result is required")
            expected_input_error = expected.get("input_error_contains")
            try:
                result = determine_containerized_provisional_weight(candidate)
            except RuleInputError as exc:
                require(isinstance(expected_input_error, str), f"{case_id} unexpectedly raised input error: {exc}")
                require(expected_input_error in str(exc), f"{case_id} raised the wrong input error: {exc}")
                print(f"PASS {case_id} rejected malformed input: {exc}")
                continue

            require(expected_input_error is None, f"{case_id} unexpectedly accepted malformed input")
            apply_path_mutations(result, fixture.get("result_mutations", []), case_id)
            expected_result_error = expected.get("result_error_contains")
            if expected_result_error is not None:
                try:
                    validate_result(result, {"status": result.get("status")}, case_id)
                except ValidationError as exc:
                    require(expected_result_error in str(exc), f"{case_id} raised the wrong result error: {exc}")
                    print(f"PASS {case_id} rejected tampered result: {exc}")
                    continue
                raise ValidationError(f"{case_id} unexpectedly accepted a tampered result")

            validate_result(result, expected, case_id)
            print(f"PASS {case_id} {result['status']}")

        print(f"PASS all {len(cases)} containerized provisional-weight cases")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, ValidationError, InitialWeightInputError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

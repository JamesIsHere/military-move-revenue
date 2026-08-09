#!/usr/bin/env python3
"""Validate lower-of-initial-and-completed-reweigh reference decisions."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.completed_reweigh_selection import (  # noqa: E402
    RuleInputError as CompletedReweighInputError,
    select_lowest_current_completed_reweigh,
)
from rules.scale_reweigh_lower_reference import (  # noqa: E402
    COMPLETED_REWEIGH_RESULT_REQUIREMENT_ID,
    INITIAL_RESULT_REQUIREMENT_ID,
    PROVENANCE,
    RULE_ID,
    RULE_PACKAGE_ID,
    RuleInputError,
    select_scale_reweigh_lower_reference,
)
from rules.weight_determination import (  # noqa: E402
    RuleInputError as InitialWeightInputError,
    determine_initial_scale_weight,
)


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "scale-reweigh-lower-reference" / "lower-weight-cases.json"
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
        require(isinstance(current, dict), f"{case_id} mutation parent is not an object: {path}")
        current[final] = value


def apply_path_mutations(target: dict, mutations: object, case_id: str) -> None:
    require(isinstance(mutations, list), f"{case_id} path mutations must be a list")
    for mutation in mutations:
        require(isinstance(mutation, dict), f"{case_id} mutation must be an object")
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
        require(mutation.get("op") == "set", f"{case_id} unsupported record mutation operation")
        field = mutation.get("field")
        require(isinstance(field, str) and field, f"{case_id} record mutation field is required")
        matches[0][field] = mutation.get("value")


def validate_registry_contract() -> None:
    registry = load_json(REGISTRY_PATH)
    packages = {record["id"]: record for record in registry["rule_packages"]}
    rules = {record["id"]: record for record in registry["rules"]}
    claims = {record["id"]: record for record in registry["source_claims"]}
    locators = {record["id"]: record for record in registry["source_locators"]}
    dependencies = [record for record in registry["rule_dependencies"] if record["rule_id"] == RULE_ID]
    evidence = [record for record in registry["evidence_requirements"] if record["rule_id"] == RULE_ID]
    sources = [record for record in registry["rule_sources"] if record["rule_id"] == RULE_ID]

    require(RULE_PACKAGE_ID in packages, "scale-reweigh lower-reference package is missing")
    require(packages[RULE_PACKAGE_ID]["publication_status"] == "published", "scale-reweigh lower-reference package is not published")
    require(RULE_ID in rules, "scale-reweigh lower-reference rule is missing")
    require(rules[RULE_ID]["rule_package_id"] == RULE_PACKAGE_ID, "scale-reweigh lower-reference rule uses the wrong package")
    require(rules[RULE_ID]["implementation_status"] == "implemented", "scale-reweigh lower-reference rule is not implemented")
    require(rules[RULE_ID]["publication_status"] == "published", "scale-reweigh lower-reference rule is not published")
    require(not rules[RULE_ID]["blocked_by_conflict_ids"], "scale-reweigh lower-reference rule is unexpectedly conflict-blocked")
    require(
        {record["input_fact_type"] for record in dependencies}
        == {"final_initial_net_scale_weight_result", "final_completed_reweigh_net_selection_result"},
        "scale-reweigh lower-reference dependencies are incomplete",
    )
    require(
        {record["id"] for record in evidence}
        == {INITIAL_RESULT_REQUIREMENT_ID, COMPLETED_REWEIGH_RESULT_REQUIREMENT_ID},
        "scale-reweigh lower-reference evidence requirements are incomplete",
    )
    require(
        {record["source_claim_id"] for record in sources} == {"CLM-0030"},
        "scale-reweigh lower-reference source scope must use only the general Tender claim",
    )

    for reference in PROVENANCE:
        claim_id = reference["source_claim_id"]
        locator_id = reference["source_locator_id"]
        require(claims[claim_id]["source_locator_id"] == locator_id, f"claim {claim_id} uses a different locator")
        require(claims[claim_id]["interpretation_status"] == "reviewed", f"claim {claim_id} is not reviewed")
        require(locators[locator_id]["source_version_id"] == reference["source_version_id"], f"locator {locator_id} uses a different source version")


def validate_result(result: dict, expected: dict, case_id: str) -> None:
    require(result.get("case_id") == case_id, f"{case_id} case mismatch")
    require(result.get("rule_package_id") == RULE_PACKAGE_ID, f"{case_id} package mismatch")
    require(result.get("rule_id") == RULE_ID, f"{case_id} rule mismatch")
    require(result.get("status") == expected.get("status"), f"{case_id} status mismatch")
    require(result.get("provenance") == list(PROVENANCE), f"{case_id} provenance mismatch")
    require(result.get("unresolved_assumptions") == [], f"{case_id} silently introduced an assumption")
    evidence = result.get("evidence", {})
    require(evidence.get("initial_result_requirement_id") == INITIAL_RESULT_REQUIREMENT_ID, f"{case_id} initial-result requirement mismatch")
    require(
        evidence.get("completed_reweigh_result_requirement_id") == COMPLETED_REWEIGH_RESULT_REQUIREMENT_ID,
        f"{case_id} completed-reweigh requirement mismatch",
    )

    forbidden_fragments = ("fee", "tolerance", "refund", "billing", "controlling_weight", "item_code", "amount", "containerized")
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
        reference = result.get("reference")
        require(isinstance(reference, dict), f"{case_id} final result lacks reference")
        require(reference.get("comparison_method") == "LOWER_OF_INITIAL_AND_COMPLETED_REWEIGH", f"{case_id} method mismatch")
        for field in (
            "lower_weight",
            "initial_net_weight",
            "completed_reweigh_net_weight",
            "selected_source",
            "selected_reweigh_observation_ids",
        ):
            require(reference.get(field) == expected.get(field), f"{case_id} {field} mismatch")
        require(reference.get("weight_unit") == "lb", f"{case_id} weight unit mismatch")
    else:
        require(result.get("human_review_required") is True, f"{case_id} blocked result must require review")
        require("reference" not in result, f"{case_id} blocked result must omit reference")
        require(result.get("blocked_reasons") == expected.get("blocked_reasons"), f"{case_id} blocked reasons mismatch")
        require(
            result.get("upstream_blocked_reasons") == expected.get("upstream_blocked_reasons"),
            f"{case_id} upstream blocked reasons mismatch",
        )


def main() -> int:
    try:
        validate_registry_contract()
        suite = load_json(FIXTURE_PATH)
        require(
            suite.get("fixture_set") == "SYNTHETIC_SCALE_REWEIGH_LOWER_REFERENCE_CASES",
            "fixture set is not labeled synthetic",
        )
        initial_path = (ROOT / suite["initial_weight_fixture_path"]).resolve()
        reweigh_path = (ROOT / suite["reweigh_history_fixture_path"]).resolve()
        require(initial_path.is_relative_to(ROOT) and reweigh_path.is_relative_to(ROOT), "fixture path escapes repository")
        initial_base = load_json(initial_path).get("base_case")
        reweigh_fixture = load_json(reweigh_path)
        require(isinstance(initial_base, dict) and initial_base.get("data_status") == "synthetic", "initial base must be synthetic")
        require(reweigh_fixture.get("data_status") == "SYNTHETIC", "reweigh base must be synthetic")
        reweigh_base = reweigh_fixture.get("records")
        require(isinstance(reweigh_base, dict), "reweigh base lacks records")

        cases = suite.get("cases")
        require(isinstance(cases, list) and cases, "scale-reweigh lower-reference suite requires cases")
        for fixture in cases:
            require(isinstance(fixture, dict), "fixture case must be an object")
            case_id = fixture.get("id")
            require(isinstance(case_id, str) and case_id, "fixture case id is required")

            initial_case = copy.deepcopy(initial_base)
            initial_case["case_id"] = f"{case_id}-INITIAL"
            apply_path_mutations(initial_case, fixture.get("initial_weight_mutations", []), case_id)
            initial_result = determine_initial_scale_weight(initial_case)
            apply_path_mutations(initial_result, fixture.get("initial_result_mutations", []), case_id)

            reweigh_records = copy.deepcopy(reweigh_base)
            apply_record_mutations(reweigh_records, fixture.get("reweigh_record_mutations", []), case_id)
            reweigh_result = select_lowest_current_completed_reweigh(
                {"case_id": f"{case_id}-REWEIGH", "data_status": "synthetic", "records": reweigh_records}
            )
            apply_path_mutations(reweigh_result, fixture.get("reweigh_result_mutations", []), case_id)

            expected = fixture.get("expected")
            require(isinstance(expected, dict), f"{case_id} expected result is required")
            candidate = {
                "case_id": case_id,
                "data_status": "synthetic",
                "initial_weight_result": initial_result,
                "completed_reweigh_result": reweigh_result,
            }
            expected_input_error = expected.get("input_error_contains")
            try:
                result = select_scale_reweigh_lower_reference(candidate)
            except RuleInputError as exc:
                require(isinstance(expected_input_error, str), f"{case_id} unexpectedly raised input error: {exc}")
                require(expected_input_error in str(exc), f"{case_id} raised the wrong input error: {exc}")
                print(f"PASS {case_id} rejected malformed input: {exc}")
                continue

            require(expected_input_error is None, f"{case_id} unexpectedly accepted malformed input")
            apply_path_mutations(result, fixture.get("combined_result_mutations", []), case_id)
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

        print(f"PASS all {len(cases)} scale-reweigh lower-reference cases")
        return 0
    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        ValidationError,
        InitialWeightInputError,
        CompletedReweighInputError,
    ) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

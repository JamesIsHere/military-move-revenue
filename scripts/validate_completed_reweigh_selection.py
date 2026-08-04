#!/usr/bin/env python3
"""Validate lowest-current-completed-reweigh selection and publication contract."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.completed_reweigh_selection import (  # noqa: E402
    DPS_EVIDENCE_REQUIREMENT_ID,
    PROVENANCE,
    RULE_ID,
    RULE_PACKAGE_ID,
    TICKET_EVIDENCE_REQUIREMENT_ID,
    RuleInputError,
    select_lowest_current_completed_reweigh,
)


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "completed-reweigh-selection" / "lowest-current-net-cases.json"
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


def apply_record_mutations(records: dict, mutations: object, case_id: str) -> None:
    require(isinstance(mutations, list), f"{case_id} mutations must be a list")
    for mutation in mutations:
        require(isinstance(mutation, dict), f"{case_id} mutation must be an object")
        collection_name = mutation.get("collection")
        collection = records.get(collection_name)
        require(isinstance(collection, list), f"{case_id} mutation collection not found: {collection_name}")
        record_id = mutation.get("id")
        matches = [record for record in collection if record.get("id") == record_id]
        require(len(matches) == 1, f"{case_id} mutation record not found: {record_id}")
        operation = mutation.get("op")
        if operation == "set":
            field = mutation.get("field")
            require(isinstance(field, str) and field, f"{case_id} set mutation field is required")
            matches[0][field] = mutation.get("value")
        elif operation == "remove":
            collection.remove(matches[0])
        else:
            raise ValidationError(f"{case_id} unsupported mutation operation {operation!r}")


def set_path(target: dict, path: object, value: object, case_id: str) -> None:
    require(isinstance(path, str) and path, f"{case_id} result mutation path is required")
    parts = path.split(".")
    current: object = target
    for part in parts[:-1]:
        require(isinstance(current, dict) and part in current, f"{case_id} result mutation path not found: {path}")
        current = current[part]
    require(isinstance(current, dict), f"{case_id} result mutation parent is not an object")
    current[parts[-1]] = value


def validate_registry_contract() -> None:
    registry = load_json(REGISTRY_PATH)
    packages = {record["id"]: record for record in registry["rule_packages"]}
    rules = {record["id"]: record for record in registry["rules"]}
    claims = {record["id"]: record for record in registry["source_claims"]}
    locators = {record["id"]: record for record in registry["source_locators"]}
    dependencies = [record for record in registry["rule_dependencies"] if record["rule_id"] == RULE_ID]
    evidence = [record for record in registry["evidence_requirements"] if record["rule_id"] == RULE_ID]

    require(RULE_PACKAGE_ID in packages, "completed-reweigh package is missing")
    require(packages[RULE_PACKAGE_ID]["publication_status"] == "published", "completed-reweigh package is not published")
    require(RULE_ID in rules, "completed-reweigh selector rule is missing")
    require(rules[RULE_ID]["rule_package_id"] == RULE_PACKAGE_ID, "completed-reweigh selector uses the wrong package")
    require(rules[RULE_ID]["implementation_status"] == "implemented", "completed-reweigh selector is not implemented")
    require(rules[RULE_ID]["publication_status"] == "published", "completed-reweigh selector is not published")
    require(not rules[RULE_ID]["blocked_by_conflict_ids"], "completed-reweigh selector is unexpectedly conflict-blocked")
    require(
        {record["input_fact_type"] for record in dependencies}
        == {
            "immutable_reweigh_observation_version",
            "completed_reweigh_gross_tare_net",
            "reweigh_observation_supersession",
            "reviewed_reweigh_ticket_evidence",
            "dps_reweigh_update",
        },
        "completed-reweigh selector dependencies are incomplete",
    )
    require(
        {record["id"] for record in evidence}
        == {TICKET_EVIDENCE_REQUIREMENT_ID, DPS_EVIDENCE_REQUIREMENT_ID},
        "completed-reweigh selector evidence requirements are incomplete",
    )

    for reference in PROVENANCE:
        claim_id = reference["source_claim_id"]
        locator_id = reference["source_locator_id"]
        require(claim_id in claims, f"selector claim missing from registry: {claim_id}")
        require(locator_id in locators, f"selector locator missing from registry: {locator_id}")
        require(claims[claim_id]["source_locator_id"] == locator_id, f"claim {claim_id} uses a different locator")
        require(claims[claim_id]["interpretation_status"] == "reviewed", f"claim {claim_id} is not reviewed")
        require(
            locators[locator_id]["source_version_id"] == reference["source_version_id"],
            f"locator {locator_id} uses a different source version",
        )


def validate_result(result: dict, expected: dict, case_id: str) -> None:
    require(result.get("case_id") == case_id, f"{case_id} case mismatch")
    require(result.get("rule_package_id") == RULE_PACKAGE_ID, f"{case_id} package mismatch")
    require(result.get("rule_id") == RULE_ID, f"{case_id} rule mismatch")
    require(result.get("status") == expected.get("status"), f"{case_id} status mismatch")
    require(result.get("unresolved_assumptions") == [], f"{case_id} silently introduced an assumption")
    require(result.get("provenance") == list(PROVENANCE), f"{case_id} provenance is incomplete")
    require(
        result.get("evidence", {}).get("ticket_requirement_id") == TICKET_EVIDENCE_REQUIREMENT_ID,
        f"{case_id} ticket requirement mismatch",
    )
    require(
        result.get("evidence", {}).get("dps_requirement_id") == DPS_EVIDENCE_REQUIREMENT_ID,
        f"{case_id} DPS requirement mismatch",
    )

    forbidden_fragments = ("fee", "tolerance", "refund", "billing", "initial_weight", "controlling_weight")
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
        selection = result.get("selection")
        require(isinstance(selection, dict), f"{case_id} final result lacks selection")
        require(selection.get("comparison_method") == "LOWEST_CURRENT_COMPLETED_REWEIGH_NET", f"{case_id} method mismatch")
        require(selection.get("selected_net_weight") == expected.get("selected_net_weight"), f"{case_id} selected net mismatch")
        require(selection.get("weight_unit") == "lb", f"{case_id} selected unit mismatch")
        require(selection.get("selected_observation_ids") == expected.get("selected_observation_ids"), f"{case_id} selected observation mismatch")
        require(selection.get("candidate_count") == expected.get("candidate_count"), f"{case_id} candidate count mismatch")
        current_ids = result["input_snapshot"]["current_observation_ids"]
        require("WEV-REW-B-001" not in current_ids, f"{case_id} included a superseded observation")
    else:
        require(result.get("human_review_required") is True, f"{case_id} blocked result must require review")
        require("selection" not in result, f"{case_id} blocked result must omit selection")
        require(result.get("blocked_reasons") == expected.get("blocked_reasons"), f"{case_id} blocked reasons mismatch")
        blocked_ids = [row["observation_id"] for row in result.get("observation_issues", [])]
        require(blocked_ids == expected.get("blocked_observation_ids"), f"{case_id} blocked observation mismatch")


def main() -> int:
    try:
        validate_registry_contract()
        suite = load_json(FIXTURE_PATH)
        require(
            suite.get("fixture_set") == "SYNTHETIC_LOWEST_CURRENT_COMPLETED_REWEIGH_CASES",
            "fixture set is not labeled synthetic",
        )
        logical_path = (ROOT / suite["logical_fixture_path"]).resolve()
        require(logical_path.is_relative_to(ROOT), "logical fixture path escapes the repository")
        logical_fixture = load_json(logical_path)
        require(logical_fixture.get("data_status") == "SYNTHETIC", "base reweigh history must be synthetic")
        base_records = logical_fixture.get("records")
        require(isinstance(base_records, dict), "base reweigh history lacks records")

        cases = suite.get("cases")
        require(isinstance(cases, list) and cases, "completed-reweigh fixture suite requires cases")
        for fixture in cases:
            require(isinstance(fixture, dict), "fixture case must be an object")
            case_id = fixture.get("id")
            require(isinstance(case_id, str) and case_id, "fixture case id is required")
            records = copy.deepcopy(base_records)
            apply_record_mutations(records, fixture.get("mutations", []), case_id)
            expected = fixture.get("expected")
            require(isinstance(expected, dict), f"{case_id} expected result is required")

            candidate = {"case_id": case_id, "data_status": "synthetic", "records": records}
            expected_input_error = expected.get("input_error_contains")
            try:
                result = select_lowest_current_completed_reweigh(candidate)
            except RuleInputError as exc:
                require(isinstance(expected_input_error, str), f"{case_id} unexpectedly raised input error: {exc}")
                require(expected_input_error in str(exc), f"{case_id} raised the wrong input error: {exc}")
                print(f"PASS {case_id} rejected malformed input: {exc}")
                continue

            require(expected_input_error is None, f"{case_id} unexpectedly accepted malformed input")
            for mutation in fixture.get("result_mutations", []):
                set_path(result, mutation.get("path"), mutation.get("value"), case_id)

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

        print(f"PASS all {len(cases)} completed-reweigh selection cases")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

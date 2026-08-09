#!/usr/bin/env python3
"""Validate deterministic initial scale-weight rules against synthetic cases."""

from __future__ import annotations

import copy
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.weight_determination import (  # noqa: E402
    PROVENANCE,
    RULE_IDS,
    RULE_PACKAGE_ID,
    SOURCE_VERSION_ID,
    RuleInputError,
    determine_initial_scale_weight,
)


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "weight-determination" / "initial-scale-weight-cases.json"
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


def set_path(target: object, path: str, value: object) -> None:
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


def validate_registry_contract() -> None:
    registry = load_json(REGISTRY_PATH)
    packages = {record["id"]: record for record in registry["rule_packages"]}
    rules = {record["id"]: record for record in registry["rules"]}
    claims = {record["id"]: record for record in registry["source_claims"]}
    locators = {record["id"]: record for record in registry["source_locators"]}

    require(RULE_PACKAGE_ID in packages, "weight rule package is missing from registry")
    require(packages[RULE_PACKAGE_ID]["publication_status"] == "published", "weight rule package is not published")
    for rule_id in RULE_IDS:
        require(rule_id in rules, f"implemented rule missing from registry: {rule_id}")
        require(rules[rule_id]["rule_package_id"] == RULE_PACKAGE_ID, f"{rule_id} uses the wrong package")
        require(rules[rule_id]["implementation_status"] == "implemented", f"{rule_id} is not implemented")
        require(rules[rule_id]["publication_status"] == "published", f"{rule_id} is not published")
        require(not rules[rule_id]["blocked_by_conflict_ids"], f"{rule_id} is unexpectedly conflict-blocked")

    for reference in PROVENANCE:
        claim_id = reference["source_claim_id"]
        locator_id = reference["source_locator_id"]
        require(claim_id in claims, f"evaluator claim missing from registry: {claim_id}")
        require(locator_id in locators, f"evaluator locator missing from registry: {locator_id}")
        require(claims[claim_id]["source_locator_id"] == locator_id, f"claim {claim_id} uses a different locator")
        require(claims[claim_id]["interpretation_status"] == "reviewed", f"claim {claim_id} is not reviewed")
        require(locators[locator_id]["source_version_id"] == SOURCE_VERSION_ID, f"locator {locator_id} uses a different source version")


def validate_result(result: dict, expected: dict, case_id: str) -> None:
    require(result["case_id"] == case_id, f"{case_id} result case_id mismatch")
    require(result["rule_package_id"] == RULE_PACKAGE_ID, f"{case_id} package mismatch")
    require(result["rule_ids"] == list(RULE_IDS), f"{case_id} rule list mismatch")
    require(result["unresolved_assumptions"] == [], f"{case_id} silently introduced an assumption")
    require(result["status"] == expected["status"], f"{case_id} expected {expected['status']}, got {result['status']}")
    require(len(result["provenance"]) == len(PROVENANCE), f"{case_id} provenance is incomplete")
    require(
        all(reference["source_version_id"] == SOURCE_VERSION_ID for reference in result["provenance"]),
        f"{case_id} uses the wrong source version",
    )

    if result["status"] == "FINAL":
        require(result["human_review_required"] is False, f"{case_id} final result cannot require review")
        require("blocked_reasons" not in result, f"{case_id} final result carries blocked reasons")
        calculation = result.get("calculation")
        require(isinstance(calculation, dict), f"{case_id} final result lacks calculation")
        require(calculation["result"] == expected["net_weight"], f"{case_id} net weight mismatch")
        require(calculation["result_unit"] == "lb", f"{case_id} result unit mismatch")
        try:
            Decimal(calculation["result"])
        except (InvalidOperation, TypeError) as exc:
            raise ValidationError(f"{case_id} result is not an exact decimal string") from exc
        if "ticket_count" in expected:
            require(len(result["evidence"]["ticket_ids"]) == expected["ticket_count"], f"{case_id} ticket count mismatch")
    else:
        require(result["human_review_required"] is True, f"{case_id} blocked result must require review")
        require("calculation" not in result, f"{case_id} blocked result must omit authoritative calculation")
        require(result.get("blocked_reasons") == expected["blocked_reasons"], f"{case_id} blocked reasons mismatch")


def main() -> int:
    try:
        validate_registry_contract()
        suite = load_json(FIXTURE_PATH)
        require(suite.get("fixture_set") == "SYNTHETIC_INITIAL_SCALE_WEIGHT_CASES", "fixture set is not labeled synthetic")
        base_case = suite.get("base_case")
        cases = suite.get("cases")
        require(isinstance(base_case, dict), "base_case must be an object")
        require(base_case.get("data_status") == "synthetic", "base_case must be synthetic")
        require(isinstance(cases, list) and cases, "fixture suite requires cases")

        for fixture in cases:
            require(isinstance(fixture, dict), "fixture case must be an object")
            case_id = fixture.get("id")
            require(isinstance(case_id, str) and case_id, "fixture case id is required")
            candidate = copy.deepcopy(base_case)
            candidate["case_id"] = case_id
            for mutation in fixture.get("mutations", []):
                require(isinstance(mutation, dict), f"{case_id} mutation must be an object")
                set_path(candidate, mutation.get("path"), mutation.get("value"))

            expected = fixture.get("expected")
            require(isinstance(expected, dict), f"{case_id} expected result is required")
            expected_error = expected.get("input_error_contains")
            try:
                result = determine_initial_scale_weight(candidate)
            except RuleInputError as exc:
                require(isinstance(expected_error, str), f"{case_id} unexpectedly raised input error: {exc}")
                require(expected_error in str(exc), f"{case_id} raised the wrong input error: {exc}")
                print(f"PASS {case_id} rejected malformed input: {exc}")
                continue

            require(expected_error is None, f"{case_id} unexpectedly accepted malformed input")
            validate_result(result, expected, case_id)
            print(f"PASS {case_id} {result['status']}")

        print(f"PASS all {len(cases)} initial scale-weight cases")
        return 0
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

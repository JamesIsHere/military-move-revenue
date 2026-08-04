#!/usr/bin/env python3
"""Validate the 2026 post-invoice reweigh refund workflow package."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.completed_reweigh_selection import select_lowest_current_completed_reweigh  # noqa: E402
from rules.reweigh_refund_workflow import (  # noqa: E402
    DPS_UPDATE_REQUIREMENT_ID,
    HOLD_RULE_ID,
    INVOICE_SUBMISSION_REQUIREMENT_ID,
    LOWER_RESULT_REQUIREMENT_ID,
    PROVENANCE,
    REFUND_PROCESSING_REQUIREMENT_ID,
    REFUND_RULE_ID,
    RULE_IDS,
    RULE_PACKAGE_ID,
    TICKET_DELIVERY_REQUIREMENT_ID,
    RuleInputError,
    determine_reweigh_refund_workflow,
)
from rules.scale_reweigh_lower_reference import select_scale_reweigh_lower_reference  # noqa: E402
from rules.weight_determination import determine_initial_scale_weight  # noqa: E402


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "reweigh-refund-workflow" / "workflow-cases.json"
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
        set_path(target, mutation.get("path"), mutation.get("value"), case_id)


def apply_record_mutations(records: dict, mutations: object, case_id: str) -> None:
    require(isinstance(mutations, list), f"{case_id} record mutations must be a list")
    for mutation in mutations:
        collection = records.get(mutation.get("collection"))
        require(isinstance(collection, list), f"{case_id} mutation collection not found")
        matches = [record for record in collection if record.get("id") == mutation.get("id")]
        require(len(matches) == 1, f"{case_id} mutation record not found: {mutation.get('id')}")
        require(mutation.get("op") == "set", f"{case_id} unsupported record mutation")
        matches[0][mutation["field"]] = mutation.get("value")


def validate_registry_contract() -> None:
    registry = load_json(REGISTRY_PATH)
    packages = {record["id"]: record for record in registry["rule_packages"]}
    rules = {record["id"]: record for record in registry["rules"]}
    claims = {record["id"]: record for record in registry["source_claims"]}
    locators = {record["id"]: record for record in registry["source_locators"]}
    require(packages[RULE_PACKAGE_ID]["version"] == "2026.reweigh-refund-workflow.1", "workflow package version mismatch")
    require(packages[RULE_PACKAGE_ID]["publication_status"] == "published", "workflow package is not published")
    for rule_id in RULE_IDS:
        require(rules[rule_id]["rule_package_id"] == RULE_PACKAGE_ID, f"{rule_id} package mismatch")
        require(rules[rule_id]["implementation_status"] == "implemented", f"{rule_id} is not implemented")
        require(rules[rule_id]["publication_status"] == "published", f"{rule_id} is not published")
        require(not rules[rule_id]["blocked_by_conflict_ids"], f"{rule_id} is conflict-blocked")

    dependencies = registry["rule_dependencies"]
    deps_by_rule = {rule_id: {row["input_fact_type"] for row in dependencies if row["rule_id"] == rule_id} for rule_id in RULE_IDS}
    require(
        deps_by_rule[REFUND_RULE_ID] == {
            "final_initial_vs_completed_reweigh_lower_reference_result",
            "original_invoice_submission_event",
            "completed_reweigh_event",
        },
        "supplemental-refund dependencies are incomplete",
    )
    require(
        deps_by_rule[HOLD_RULE_ID] == {
            "final_supplemental_refund_requirement_result",
            "completed_dps_reweigh_update",
            "reviewed_ppso_ticket_delivery",
            "refund_submission_and_processing_history",
        },
        "hold-readiness dependencies are incomplete",
    )
    evidence_ids = {row["id"] for row in registry["evidence_requirements"] if row["rule_id"] in RULE_IDS}
    require(
        evidence_ids == {
            LOWER_RESULT_REQUIREMENT_ID,
            INVOICE_SUBMISSION_REQUIREMENT_ID,
            DPS_UPDATE_REQUIREMENT_ID,
            TICKET_DELIVERY_REQUIREMENT_ID,
            REFUND_PROCESSING_REQUIREMENT_ID,
        },
        "workflow evidence requirements are incomplete",
    )
    sources = registry["rule_sources"]
    require({row["source_claim_id"] for row in sources if row["rule_id"] == REFUND_RULE_ID} == {"CLM-0026", "CLM-0031"}, "refund rule sources are incomplete")
    require({row["source_claim_id"] for row in sources if row["rule_id"] == HOLD_RULE_ID} == {"CLM-0026", "CLM-0032"}, "hold rule sources are incomplete")
    for reference in PROVENANCE:
        claim = claims[reference["source_claim_id"]]
        require(claim["source_locator_id"] == reference["source_locator_id"] and claim["interpretation_status"] == "reviewed", "workflow claim provenance mismatch")
        require(locators[reference["source_locator_id"]]["source_version_id"] == reference["source_version_id"], "workflow source-version provenance mismatch")


def validate_result(result: dict, expected: dict, case_id: str) -> None:
    require(result.get("case_id") == case_id, f"{case_id} case mismatch")
    require(result.get("rule_package_id") == RULE_PACKAGE_ID, f"{case_id} package mismatch")
    require(result.get("rule_ids") == list(RULE_IDS), f"{case_id} rule set mismatch")
    require(result.get("status") == expected.get("status"), f"{case_id} status mismatch")
    require(result.get("provenance") == list(PROVENANCE), f"{case_id} provenance mismatch")
    require(result.get("unresolved_assumptions") == [], f"{case_id} silently introduced an assumption")
    evidence = result.get("evidence", {})
    require(set(evidence.values()) == {
        LOWER_RESULT_REQUIREMENT_ID,
        INVOICE_SUBMISSION_REQUIREMENT_ID,
        DPS_UPDATE_REQUIREMENT_ID,
        TICKET_DELIVERY_REQUIREMENT_ID,
        REFUND_PROCESSING_REQUIREMENT_ID,
    }, f"{case_id} evidence contract mismatch")
    forbidden = ("amount", "currency", "fee", "tolerance", "item_code", "expected_charge", "payment")
    def check_scope(value: object) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                require(not any(fragment in key.lower() for fragment in forbidden), f"{case_id} crossed scope at {key}")
                check_scope(child)
        elif isinstance(value, list):
            for child in value:
                check_scope(child)
    check_scope(result)

    if result["status"] == "FINAL":
        require(result.get("human_review_required") is False, f"{case_id} final result requires review")
        decisions = result.get("decisions", {})
        refund = decisions.get("supplemental_refund", {})
        hold = decisions.get("destination_direct_delivery_hold", {})
        require(refund.get("required") == expected.get("refund_required"), f"{case_id} refund requirement mismatch")
        require(refund.get("reason_code") == expected.get("refund_reason"), f"{case_id} refund reason mismatch")
        require(hold.get("release_ready") == expected.get("release_ready"), f"{case_id} hold readiness mismatch")
        require(hold.get("unmet_prerequisites") == expected.get("unmet_prerequisites", []), f"{case_id} unmet prerequisites mismatch")
    else:
        require(result.get("human_review_required") is True, f"{case_id} blocked result must require review")
        require("decisions" not in result, f"{case_id} blocked result contains decisions")
        require(result.get("blocked_reasons") == expected.get("blocked_reasons"), f"{case_id} blocked reasons mismatch")
        if "upstream_blocked_reasons" in expected:
            require(result.get("upstream_blocked_reasons") == expected["upstream_blocked_reasons"], f"{case_id} upstream reasons mismatch")


def main() -> int:
    try:
        validate_registry_contract()
        suite = load_json(FIXTURE_PATH)
        require(suite.get("fixture_set") == "SYNTHETIC_REWEIGH_REFUND_WORKFLOW_CASES", "fixture set is not labeled synthetic")
        workflow_fixture = load_json((ROOT / suite["workflow_fixture_path"]).resolve())
        initial_base = load_json((ROOT / suite["initial_weight_fixture_path"]).resolve()).get("base_case")
        require(workflow_fixture.get("data_status") == "SYNTHETIC", "workflow fixture must be synthetic")
        require(isinstance(initial_base, dict) and initial_base.get("data_status") == "synthetic", "initial fixture must be synthetic")

        cases = suite.get("cases")
        require(isinstance(cases, list) and cases, "workflow suite requires cases")
        for fixture in cases:
            case_id = fixture["id"]
            initial_case = copy.deepcopy(initial_base)
            initial_case["case_id"] = f"{case_id}-INITIAL"
            apply_path_mutations(initial_case, fixture.get("initial_weight_mutations", []), case_id)
            initial_result = determine_initial_scale_weight(initial_case)

            upstream_records = copy.deepcopy(workflow_fixture["records"])
            apply_record_mutations(upstream_records, fixture.get("upstream_record_mutations", []), case_id)
            completed_result = select_lowest_current_completed_reweigh({"case_id": f"{case_id}-REWEIGH", "data_status": "synthetic", "records": upstream_records})
            lower_result = select_scale_reweigh_lower_reference({
                "case_id": f"{case_id}-LOWER",
                "data_status": "synthetic",
                "initial_weight_result": initial_result,
                "completed_reweigh_result": completed_result,
            })
            apply_path_mutations(lower_result, fixture.get("lower_result_mutations", []), case_id)

            workflow_records = copy.deepcopy(workflow_fixture["records"])
            apply_record_mutations(workflow_records, fixture.get("upstream_record_mutations", []), case_id)
            workflow_records["reweigh_refund_cases"][0]["lower_weight_result_ref"] = lower_result["case_id"]
            apply_record_mutations(workflow_records, fixture.get("workflow_record_mutations", []), case_id)
            expected = fixture["expected"]
            candidate = {"case_id": case_id, "data_status": "synthetic", "records": workflow_records, "lower_weight_result": lower_result}
            try:
                result = determine_reweigh_refund_workflow(candidate)
            except RuleInputError as exc:
                expected_error = expected.get("input_error_contains")
                require(isinstance(expected_error, str) and expected_error in str(exc), f"{case_id} raised wrong input error: {exc}")
                print(f"PASS {case_id} rejected malformed input: {exc}")
                continue
            require("input_error_contains" not in expected, f"{case_id} unexpectedly accepted malformed input")
            apply_path_mutations(result, fixture.get("result_mutations", []), case_id)
            expected_result_error = expected.get("result_error_contains")
            if expected_result_error:
                try:
                    validate_result(result, {"status": result.get("status")}, case_id)
                except ValidationError as exc:
                    require(expected_result_error in str(exc), f"{case_id} raised wrong result error: {exc}")
                    print(f"PASS {case_id} rejected tampered result: {exc}")
                    continue
                raise ValidationError(f"{case_id} accepted a tampered result")
            validate_result(result, expected, case_id)
            print(f"PASS {case_id} {result['status']}")
        print(f"PASS all {len(cases)} reweigh refund-workflow cases")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

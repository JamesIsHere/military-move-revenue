#!/usr/bin/env python3
"""Validate the approved 2026 reweigh-tolerance eligibility package."""

from __future__ import annotations

import copy
import json
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.reweigh_tolerance import (  # noqa: E402
    EFFECTIVE_FROM,
    EFFECTIVE_TO,
    EXPECTED_INITIAL_PROVENANCE,
    FEE_PROVENANCE,
    FEE_RULE_ID,
    INTERPRETATION_DECISION_ID,
    LOWER_RESULT_REQUIREMENT_ID,
    REIMBURSEMENT_PROVENANCE,
    REIMBURSEMENT_RULE_ID,
    RULE_PACKAGE_ID,
    SCOPE_EXCLUSIONS,
    RuleInputError,
    determine_containerized_reimbursement_tolerance,
    determine_reweigh_fee_tolerance,
)
from rules.scale_reweigh_lower_reference import (  # noqa: E402
    PROVENANCE as LOWER_RESULT_PROVENANCE,
    RULE_ID as LOWER_RESULT_RULE_ID,
    RULE_PACKAGE_ID as LOWER_RESULT_PACKAGE_ID,
)
from rules.weight_determination import (  # noqa: E402
    RULE_IDS as INITIAL_WEIGHT_RULE_IDS,
    RULE_PACKAGE_ID as INITIAL_WEIGHT_PACKAGE_ID,
)


DOSSIER = ROOT / "docs" / "decisions" / "0006-cf-0004-reweigh-tolerance-dossier.json"
REGISTRY = ROOT / "rules" / "registry" / "registry.json"
FIVE_THOUSAND = Decimal("5000")
ONE_HUNDRED_FIFTY = Decimal("150")
FIVE_PERCENT = Decimal("0.05")


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"{path.name} must contain an object")
    return value


def canonical(value: Decimal) -> str:
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def lower_result(case: dict, *, status: str = "FINAL") -> dict:
    initial = Decimal(case["initial_net_lb"])
    reweigh = Decimal(case["completed_reweigh_net_lb"])
    result = {
        "case_id": f"{case['id']}-LOWER",
        "rule_package_id": LOWER_RESULT_PACKAGE_ID,
        "rule_id": LOWER_RESULT_RULE_ID,
        "status": status,
        "human_review_required": status == "BLOCKED",
        "evidence": {"synthetic_upstream_evidence": "REVIEWED"},
        "provenance": [dict(value) for value in LOWER_RESULT_PROVENANCE],
        "unresolved_assumptions": [],
    }
    if status == "BLOCKED":
        result["blocked_reasons"] = ["SYNTHETIC_UPSTREAM_BLOCK"]
    else:
        selected = "INITIAL_SCALE_WEIGHT" if initial < reweigh else "COMPLETED_REWEIGH" if reweigh < initial else "TIE"
        result["reference"] = {
            "comparison_method": "LOWER_OF_INITIAL_AND_COMPLETED_REWEIGH",
            "lower_weight": canonical(min(initial, reweigh)),
            "weight_unit": "lb",
            "selected_source": selected,
            "initial_net_weight": canonical(initial),
            "completed_reweigh_net_weight": canonical(reweigh),
            "selected_reweigh_observation_ids": [f"SYNTH-{case['id']}-REWEIGH"],
        }
    return result


def initial_result(case_id: str, initial_net: str, *, status: str = "FINAL") -> dict:
    result = {
        "case_id": f"{case_id}-INITIAL",
        "rule_package_id": INITIAL_WEIGHT_PACKAGE_ID,
        "rule_ids": list(INITIAL_WEIGHT_RULE_IDS),
        "status": status,
        "human_review_required": status == "BLOCKED",
        "evidence": {"synthetic_initial_tickets": "REVIEWED"},
        "provenance": [dict(value) for value in EXPECTED_INITIAL_PROVENANCE],
        "unresolved_assumptions": [],
    }
    if status == "BLOCKED":
        result["blocked_reasons"] = ["SYNTHETIC_INITIAL_BLOCK"]
    else:
        result["calculation"] = {
            "expression": "gross_weight_lb - tare_weight_lb",
            "result": initial_net,
            "result_unit": "lb",
            "rounding_rule": "NONE_SOURCE_DOES_NOT_SPECIFY_ROUNDING",
        }
    return result


def tare(case_id: str, shipment_id: str, role: str, value: object, review: str = "REVIEWED") -> dict:
    suffix = "ORIGINAL" if role == "ORIGINAL_TARE" else "REWEIGH"
    return {
        "id": f"SYNTH-{case_id}-{suffix}-TARE",
        "shipment_id": shipment_id,
        "measurement_role": role,
        "weight_value": value,
        "weight_unit": "lb",
        "ticket_id": f"SYNTH-{case_id}-{suffix}-TICKET",
        "evidence_link_id": f"SYNTH-{case_id}-{suffix}-EVIDENCE",
        "evidence_review_status": review,
    }


def fee_input(case: dict, pickup_date: str = "2026-05-15") -> dict:
    return {
        "case_id": case["id"],
        "shipment_id": f"SYNTH-{case['id']}-SHIPMENT",
        "data_status": "synthetic",
        "actual_pickup_date": pickup_date,
        "lower_weight_result": lower_result(case),
    }


def reimbursement_input(case: dict, pickup_date: str = "2026-05-15") -> dict:
    shipment_id = f"SYNTH-{case['id']}-SHIPMENT"
    return {
        "case_id": case["id"],
        "shipment_id": shipment_id,
        "data_status": "synthetic",
        "actual_pickup_date": pickup_date,
        "initial_weight_result": initial_result(case["id"], case["initial_net_lb"]),
        "original_tare_observation": tare(case["id"], shipment_id, "ORIGINAL_TARE", case["original_tare_lb"]),
        "reweigh_tare_observation": tare(case["id"], shipment_id, "REWEIGH_TARE", case["reweigh_tare_lb"]),
    }


def expected_fee(case: dict) -> bool:
    initial = Decimal(case["initial_net_lb"])
    reweigh = Decimal(case["completed_reweigh_net_lb"])
    lower = min(initial, reweigh)
    if reweigh >= initial:
        return True
    difference = initial - reweigh
    return difference < ONE_HUNDRED_FIFTY if initial <= FIVE_THOUSAND else difference < lower * FIVE_PERCENT


def expected_reimbursement(case: dict) -> bool:
    initial = Decimal(case["initial_net_lb"])
    original = Decimal(case["original_tare_lb"])
    reweigh = Decimal(case["reweigh_tare_lb"])
    if reweigh <= original:
        return False
    increase = reweigh - original
    return increase > ONE_HUNDRED_FIFTY if initial <= FIVE_THOUSAND else increase >= min(original, reweigh) * FIVE_PERCENT


def reject_money(value: object, path: str = "result") -> None:
    forbidden = ("amount", "currency", "rate", "item_code", "invoice", "payment")
    if isinstance(value, dict):
        for key, child in value.items():
            require(not any(fragment in key.lower() for fragment in forbidden), f"monetary scope crossed at {path}.{key}")
            reject_money(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_money(child, f"{path}[{index}]")


def validate_result(result: dict, rule_id: str, provenance: tuple[dict, ...], expected_status: str, expected_eligible: bool | None = None) -> None:
    require(result.get("rule_package_id") == RULE_PACKAGE_ID, "result package mismatch")
    require(result.get("rule_id") == rule_id, "result rule mismatch")
    require(result.get("interpretation_decision_id") == INTERPRETATION_DECISION_ID, "result interpretation mismatch")
    require(result.get("provenance") == [dict(value) for value in provenance], "result provenance mismatch")
    require(result.get("scope_exclusions") == list(SCOPE_EXCLUSIONS), "result scope exclusions mismatch")
    require(result.get("unresolved_assumptions") == [], "result carries unresolved assumptions")
    require(result.get("status") == expected_status, "result status mismatch")
    reject_money(result)
    if expected_status == "FINAL":
        require(result.get("human_review_required") is False, "final result requires review")
        eligibility = result.get("eligibility")
        require(isinstance(eligibility, dict), "final result lacks eligibility")
        require(eligibility.get("eligible") is expected_eligible, "eligibility mismatch")
        require(eligibility.get("branch_selector_fact_type") == "FINAL_REVIEWED_INITIAL_NET_SCALE_WEIGHT", "selector fact mismatch")
        require(eligibility.get("rounding_rule") == "NONE_EXACT_DECIMAL", "rounding rule mismatch")
        require(eligibility.get("weight_unit") == "lb", "result unit mismatch")
        require("blocked_reasons" not in result, "final result contains blockers")
    else:
        require(result.get("human_review_required") is True, "blocked result must require review")
        require("eligibility" not in result, "blocked result exposes eligibility")
        require(isinstance(result.get("blocked_reasons"), list) and result["blocked_reasons"], "blocked result lacks reasons")


def validate_registry() -> None:
    registry = load(REGISTRY)
    conflicts = {value["id"]: value for value in registry["conflict_cases"]}
    decisions = {value["id"]: value for value in registry["interpretation_decisions"]}
    packages = {value["id"]: value for value in registry["rule_packages"]}
    rules = {value["id"]: value for value in registry["rules"]}
    dependencies = registry["rule_dependencies"]
    evidence = registry["evidence_requirements"]
    sources = registry["rule_sources"]

    require(conflicts["CF-0004"]["status"] == "resolved", "CF-0004 is not resolved")
    decision = decisions[INTERPRETATION_DECISION_ID]
    require(decision["decision_status"] == "approved", "INT-0003 is not approved")
    require(decision["authorized_rule_ids"] == [FEE_RULE_ID, REIMBURSEMENT_RULE_ID], "INT-0003 rule scope mismatch")
    require(len(decision["required_regression_tests"]) == 13, "INT-0003 mandatory test count mismatch")
    require(packages[RULE_PACKAGE_ID]["publication_status"] == "published", "tolerance package is not published")
    for rule_id in (FEE_RULE_ID, REIMBURSEMENT_RULE_ID):
        rule = rules[rule_id]
        require(rule["rule_package_id"] == RULE_PACKAGE_ID, f"{rule_id} package mismatch")
        require(rule["implementation_status"] == "implemented" and rule["publication_status"] == "published", f"{rule_id} is not published")
        require(rule["approved_interpretation_decision_ids"] == [INTERPRETATION_DECISION_ID], f"{rule_id} decision link mismatch")
        require(rule["blocked_by_conflict_ids"] == ["CF-0004"], f"{rule_id} reopen gate mismatch")

    deps = {
        rule_id: {value["input_fact_type"] for value in dependencies if value["rule_id"] == rule_id}
        for rule_id in (FEE_RULE_ID, REIMBURSEMENT_RULE_ID)
    }
    require(deps[FEE_RULE_ID] == {"final_initial_vs_completed_reweigh_lower_reference_result", "actual_pickup_date"}, "fee dependency contract mismatch")
    require(deps[REIMBURSEMENT_RULE_ID] == {"original_tare_scale_weight", "reweigh_tare_scale_weight", "final_initial_net_scale_weight_result", "actual_pickup_date"}, "reimbursement dependency contract mismatch")
    evidence_ids = {value["id"] for value in evidence if value["rule_id"] in {FEE_RULE_ID, REIMBURSEMENT_RULE_ID}}
    require(evidence_ids == {"EVID-REWEIGH-TOL-001", "EVID-REIMBURSE-TOL-001", "EVID-REIMBURSE-TOL-002"}, "tolerance evidence contract mismatch")
    source_claims = {
        rule_id: {value["source_claim_id"] for value in sources if value["rule_id"] == rule_id}
        for rule_id in (FEE_RULE_ID, REIMBURSEMENT_RULE_ID)
    }
    require(source_claims[FEE_RULE_ID] == {"CLM-0023", "CLM-0044"}, "fee source contract mismatch")
    require(source_claims[REIMBURSEMENT_RULE_ID] == {"CLM-0028"}, "reimbursement source contract mismatch")


def main() -> int:
    try:
        validate_registry()
        dossier = load(DOSSIER)
        fee_cases = dossier["boundary_cases"]["reweigh_fee"]
        reimbursement_cases = dossier["boundary_cases"]["containerized_reimbursement"]
        require(len(fee_cases) == 7 and len(reimbursement_cases) == 6, "dossier boundary suite mismatch")

        for case in fee_cases:
            expected = expected_fee(case)
            require(expected is ("INITIAL_NET" in case["expected_eligible_candidate_ids"]), f"{case['id']} dossier initial-net expectation mismatch")
            result = determine_reweigh_fee_tolerance(fee_input(case))
            validate_result(result, FEE_RULE_ID, FEE_PROVENANCE, "FINAL", expected)
            require(result["evidence"]["lower_weight_result_requirement_id"] == LOWER_RESULT_REQUIREMENT_ID, f"{case['id']} evidence mismatch")
            print(f"PASS {case['id']} {'QUALIFIES' if expected else 'DOES_NOT_QUALIFY'}")

        for case in reimbursement_cases:
            expected = expected_reimbursement(case)
            require(expected is ("INITIAL_NET" in case["expected_eligible_candidate_ids"]), f"{case['id']} dossier initial-net expectation mismatch")
            result = determine_containerized_reimbursement_tolerance(reimbursement_input(case))
            validate_result(result, REIMBURSEMENT_RULE_ID, REIMBURSEMENT_PROVENANCE, "FINAL", expected)
            print(f"PASS {case['id']} {'REQUIRED' if expected else 'NOT_REQUIRED'}")

        base_fee = fee_cases[0]
        for label, pickup, status in (
            ("effective start", EFFECTIVE_FROM.isoformat(), "FINAL"),
            ("effective end", EFFECTIVE_TO.isoformat(), "FINAL"),
            ("before effective period", "2026-05-14", "BLOCKED"),
            ("after effective period", "2027-05-15", "BLOCKED"),
        ):
            result = determine_reweigh_fee_tolerance(fee_input(base_fee, pickup))
            validate_result(result, FEE_RULE_ID, FEE_PROVENANCE, status, expected_fee(base_fee) if status == "FINAL" else None)
            print(f"PASS tolerance date gate: {label}")

        blocked_fee = fee_input(base_fee)
        blocked_fee["lower_weight_result"] = lower_result(base_fee, status="BLOCKED")
        result = determine_reweigh_fee_tolerance(blocked_fee)
        validate_result(result, FEE_RULE_ID, FEE_PROVENANCE, "BLOCKED")
        require(result["blocked_reasons"] == ["LOWER_WEIGHT_RESULT_BLOCKED"], "fee upstream blocker mismatch")
        require(result["upstream_blocked_reasons"] == ["SYNTHETIC_UPSTREAM_BLOCK"], "fee upstream reasons mismatch")
        print("PASS blocked lower-weight result propagated")

        base_reimbursement = reimbursement_cases[0]
        for label, mutate, expected_reason in (
            ("blocked initial", lambda value: value.__setitem__("initial_weight_result", initial_result("BLOCKED", "5001", status="BLOCKED")), "INITIAL_WEIGHT_RESULT_BLOCKED"),
            ("unreviewed original tare", lambda value: value["original_tare_observation"].__setitem__("evidence_review_status", "PENDING"), "ORIGINAL_TARE_EVIDENCE_MISSING_OR_UNREVIEWED"),
            ("unreviewed reweigh tare", lambda value: value["reweigh_tare_observation"].__setitem__("evidence_review_status", "PENDING"), "REWEIGH_TARE_EVIDENCE_MISSING_OR_UNREVIEWED"),
        ):
            candidate = reimbursement_input(base_reimbursement)
            mutate(candidate)
            result = determine_containerized_reimbursement_tolerance(candidate)
            validate_result(result, REIMBURSEMENT_RULE_ID, REIMBURSEMENT_PROVENANCE, "BLOCKED")
            require(expected_reason in result["blocked_reasons"], f"{label} reason mismatch")
            print(f"PASS {label} blocked")

        malformed = (
            ("binary tare", lambda value: value["reweigh_tare_observation"].__setitem__("weight_value", 2150.0), "exact decimal JSON string"),
            ("lower provenance", lambda value: value["lower_weight_result"]["provenance"][0].__setitem__("source_claim_id", "CLM-TAMPERED"), "lower_weight_result provenance mismatch"),
            ("initial provenance", lambda value: value["initial_weight_result"]["provenance"][0].__setitem__("source_claim_id", "CLM-TAMPERED"), "initial_weight_result provenance mismatch"),
        )
        for label, mutate, expected_error in malformed:
            candidate = reimbursement_input(base_reimbursement) if label != "lower provenance" else fee_input(base_fee)
            mutate(candidate)
            try:
                determine_containerized_reimbursement_tolerance(candidate) if label != "lower provenance" else determine_reweigh_fee_tolerance(candidate)
            except RuleInputError as exc:
                require(expected_error in str(exc), f"{label} raised wrong error: {exc}")
                print(f"PASS malformed input rejected: {label}")
                continue
            raise ValidationError(f"malformed input accepted: {label}")

        canonical_result = determine_reweigh_fee_tolerance(fee_input(base_fee))
        tamper_probes = (
            ("package", "rule_package_id", "RP-TAMPERED"),
            ("decision", "interpretation_decision_id", "INT-TAMPERED"),
            ("rule", "rule_id", REIMBURSEMENT_RULE_ID),
        )
        for label, field, value in tamper_probes:
            changed = copy.deepcopy(canonical_result)
            changed[field] = value
            try:
                validate_result(changed, FEE_RULE_ID, FEE_PROVENANCE, "FINAL", expected_fee(base_fee))
            except ValidationError:
                print(f"PASS result tamper rejected: {label}")
                continue
            raise ValidationError(f"accepted result tamper: {label}")

        changed = copy.deepcopy(canonical_result)
        changed["eligibility"]["eligible"] = not changed["eligibility"]["eligible"]
        try:
            validate_result(changed, FEE_RULE_ID, FEE_PROVENANCE, "FINAL", expected_fee(base_fee))
        except ValidationError:
            print("PASS result tamper rejected: eligibility")
        else:
            raise ValidationError("accepted result tamper: eligibility")

        print("PASS reweigh tolerance package: 13 dossier boundaries, 4 date gates, 4 evidence/upstream blocks, 3 malformed inputs, and 4 result-tamper probes")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValidationError, RuleInputError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

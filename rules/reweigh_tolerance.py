"""Apply the approved 2026 initial-net reweigh-tolerance interpretation."""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation

from rules.scale_reweigh_lower_reference import (
    PROVENANCE as LOWER_RESULT_PROVENANCE,
    RULE_ID as LOWER_RESULT_RULE_ID,
    RULE_PACKAGE_ID as LOWER_RESULT_PACKAGE_ID,
)
from rules.weight_determination import (
    PROVENANCE as INITIAL_WEIGHT_PROVENANCE_BASE,
    RULE_IDS as INITIAL_WEIGHT_RULE_IDS,
    RULE_PACKAGE_ID as INITIAL_WEIGHT_PACKAGE_ID,
    SOURCE_VERSION_ID as INITIAL_WEIGHT_SOURCE_VERSION_ID,
)


RULE_PACKAGE_ID = "RP-DP3-2026-REWEIGH-TOLERANCE-1"
FEE_RULE_ID = "RULE-REWEIGH-FEE-TOLERANCE-QUALIFIES"
REIMBURSEMENT_RULE_ID = "RULE-CONTAINERIZED-REWEIGH-REIMBURSEMENT-TOLERANCE"
INTERPRETATION_DECISION_ID = "INT-0003"
EFFECTIVE_FROM = date(2026, 5, 15)
EFFECTIVE_TO = date(2027, 5, 14)
FEE_PROVENANCE = (
    {
        "source_version_id": "SV-DP3-2026-400NG-2025-12-05",
        "source_claim_id": "CLM-0023",
        "source_locator_id": "LOC-0019",
    },
    {
        "source_version_id": "SV-DP3-ADV-23-0004-2022-10-13",
        "source_claim_id": "CLM-0044",
        "source_locator_id": "LOC-0039",
    },
)
REIMBURSEMENT_PROVENANCE = (
    {
        "source_version_id": "SV-DP3-2026-400NG-2025-12-05",
        "source_claim_id": "CLM-0028",
        "source_locator_id": "LOC-0024",
    },
)
EXPECTED_INITIAL_PROVENANCE = tuple(
    {"source_version_id": INITIAL_WEIGHT_SOURCE_VERSION_ID, **reference}
    for reference in INITIAL_WEIGHT_PROVENANCE_BASE
)
LOWER_RESULT_REQUIREMENT_ID = "EVID-REWEIGH-TOL-001"
INITIAL_RESULT_REQUIREMENT_ID = "EVID-REIMBURSE-TOL-002"
TARE_TICKET_REQUIREMENT_ID = "EVID-REIMBURSE-TOL-001"
DECIMAL_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")
ZERO = Decimal("0")
FIVE_PERCENT = Decimal("0.05")
ONE_HUNDRED_FIFTY = Decimal("150")
FIVE_THOUSAND = Decimal("5000")
SCOPE_EXCLUSIONS = (
    "FEE_RATE_OR_BILLING_CODE",
    "DISCOUNT_TREATMENT",
    "REIMBURSEMENT_OR_REFUND_AMOUNT",
    "CHARGE_ALLOCATION",
    "LIVE_INVOICE_SUBMISSION",
    "MONEY_MOVEMENT",
)


class RuleInputError(ValueError):
    """Raised when an input or upstream result is malformed or tampered."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuleInputError(message)


def _decimal(value: object, label: str) -> Decimal:
    _require(isinstance(value, str), f"{label} must be an exact decimal JSON string")
    _require(DECIMAL_RE.fullmatch(value) is not None, f"{label} is not a canonical nonnegative decimal")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise RuleInputError(f"{label} is not an exact decimal") from exc


def _canonical_decimal(value: Decimal) -> str:
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def _local_date(value: object) -> date:
    _require(isinstance(value, str), "actual_pickup_date must be an ISO local-date string")
    try:
        result = date.fromisoformat(value)
    except ValueError as exc:
        raise RuleInputError("actual_pickup_date must be an ISO local-date string") from exc
    _require(result.isoformat() == value, "actual_pickup_date must be canonical YYYY-MM-DD")
    return result


def _case_header(case: object) -> tuple[dict, str, str, date]:
    _require(isinstance(case, dict), "case must be an object")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id, "case_id is required")
    _require(case.get("data_status") in {"synthetic", "authorized_sanitized"}, "data_status must be synthetic or authorized_sanitized")
    shipment_id = case.get("shipment_id")
    _require(isinstance(shipment_id, str) and shipment_id, "shipment_id is required")
    return case, case_id, shipment_id, _local_date(case.get("actual_pickup_date"))


def _validate_lower_result(value: object) -> dict:
    _require(isinstance(value, dict), "lower_weight_result must be an object")
    _require(value.get("rule_package_id") == LOWER_RESULT_PACKAGE_ID, "lower_weight_result uses an unknown rule package")
    _require(value.get("rule_id") == LOWER_RESULT_RULE_ID, "lower_weight_result rule mismatch")
    _require(value.get("provenance") == list(LOWER_RESULT_PROVENANCE), "lower_weight_result provenance mismatch")
    _require(value.get("status") in {"FINAL", "BLOCKED"}, "lower_weight_result has invalid status")
    return value


def _validate_initial_result(value: object) -> dict:
    _require(isinstance(value, dict), "initial_weight_result must be an object")
    _require(value.get("rule_package_id") == INITIAL_WEIGHT_PACKAGE_ID, "initial_weight_result uses an unknown rule package")
    rule_ids = value.get("rule_ids")
    _require(isinstance(rule_ids, list) and set(rule_ids) == set(INITIAL_WEIGHT_RULE_IDS), "initial_weight_result rule set mismatch")
    _require(value.get("provenance") == list(EXPECTED_INITIAL_PROVENANCE), "initial_weight_result provenance mismatch")
    _require(value.get("status") in {"FINAL", "BLOCKED"}, "initial_weight_result has invalid status")
    return value


def _branch(initial_net: Decimal) -> str:
    return "AT_OR_BELOW_5000" if initial_net <= FIVE_THOUSAND else "OVER_5000"


def _base_result(case_id: str, shipment_id: str, pickup_date: str, rule_id: str, provenance: tuple[dict, ...]) -> dict:
    return {
        "case_id": case_id,
        "shipment_id": shipment_id,
        "actual_pickup_date": pickup_date,
        "rule_package_id": RULE_PACKAGE_ID,
        "rule_id": rule_id,
        "interpretation_decision_id": INTERPRETATION_DECISION_ID,
        "provenance": [dict(reference) for reference in provenance],
        "unresolved_assumptions": [],
        "scope_exclusions": list(SCOPE_EXCLUSIONS),
    }


def determine_reweigh_fee_tolerance(case: dict) -> dict:
    """Decide only whether Item 4.5's reweigh-fee tolerance qualifies."""

    case, case_id, shipment_id, pickup_date = _case_header(case)
    lower_result = _validate_lower_result(case.get("lower_weight_result"))
    common = {
        **_base_result(case_id, shipment_id, pickup_date.isoformat(), FEE_RULE_ID, FEE_PROVENANCE),
        "input_snapshot": {"lower_weight_result_case_id": lower_result.get("case_id")},
        "evidence": {
            "lower_weight_result_requirement_id": LOWER_RESULT_REQUIREMENT_ID,
            "upstream_evidence": lower_result.get("evidence", {}),
        },
    }
    blocked_reasons: list[str] = []
    if not EFFECTIVE_FROM <= pickup_date <= EFFECTIVE_TO:
        blocked_reasons.append("OUTSIDE_RULE_EFFECTIVE_PERIOD")
    if lower_result["status"] == "BLOCKED":
        blocked_reasons.append("LOWER_WEIGHT_RESULT_BLOCKED")
    if blocked_reasons:
        result = {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": blocked_reasons,
        }
        if lower_result["status"] == "BLOCKED":
            result["upstream_blocked_reasons"] = lower_result.get("blocked_reasons", [])
        return result

    reference = lower_result.get("reference")
    _require(isinstance(reference, dict), "FINAL lower_weight_result lacks reference")
    _require(reference.get("weight_unit") == "lb", "lower_weight_result unit must be lb")
    initial_net = _decimal(reference.get("initial_net_weight"), "lower_weight_result.reference.initial_net_weight")
    reweigh_net = _decimal(reference.get("completed_reweigh_net_weight"), "lower_weight_result.reference.completed_reweigh_net_weight")
    lower_net = _decimal(reference.get("lower_weight"), "lower_weight_result.reference.lower_weight")
    _require(initial_net > ZERO and reweigh_net > ZERO, "fee weight inputs must be positive")
    _require(lower_net == min(initial_net, reweigh_net), "lower_weight_result arithmetic mismatch")

    branch = _branch(initial_net)
    difference = max(initial_net - reweigh_net, ZERO)
    if reweigh_net >= initial_net:
        eligible = True
        threshold_kind = "NOT_APPLIED_REWEIGH_EQUAL_OR_GREATER"
        threshold_value = None
        comparison_operator = "NOT_APPLIED"
        reason_code = "REWEIGH_EQUAL_OR_GREATER_THAN_INITIAL"
    elif branch == "AT_OR_BELOW_5000":
        threshold_kind = "FIXED_150_LB"
        threshold_value = _canonical_decimal(ONE_HUNDRED_FIFTY)
        comparison_operator = "LT"
        eligible = difference < ONE_HUNDRED_FIFTY
        reason_code = "LOWER_REWEIGH_WITHIN_TOLERANCE" if eligible else "LOWER_REWEIGH_OUTSIDE_TOLERANCE"
    else:
        threshold = lower_net * FIVE_PERCENT
        threshold_kind = "FIVE_PERCENT_OF_LOWER_NET"
        threshold_value = _canonical_decimal(threshold)
        comparison_operator = "LT"
        eligible = difference < threshold
        reason_code = "LOWER_REWEIGH_WITHIN_TOLERANCE" if eligible else "LOWER_REWEIGH_OUTSIDE_TOLERANCE"

    return {
        **common,
        "status": "FINAL",
        "human_review_required": False,
        "eligibility": {
            "decision_kind": "REWEIGH_FEE_TOLERANCE_QUALIFIES",
            "eligible": eligible,
            "reason_code": reason_code,
            "branch_selector_fact_type": "FINAL_REVIEWED_INITIAL_NET_SCALE_WEIGHT",
            "branch": branch,
            "branch_weight": _canonical_decimal(initial_net),
            "initial_net_weight": _canonical_decimal(initial_net),
            "completed_reweigh_net_weight": _canonical_decimal(reweigh_net),
            "lower_net_weight": _canonical_decimal(lower_net),
            "difference": _canonical_decimal(difference),
            "threshold_kind": threshold_kind,
            "threshold_value": threshold_value,
            "comparison_operator": comparison_operator,
            "weight_unit": "lb",
            "rounding_rule": "NONE_EXACT_DECIMAL",
        },
    }


def _tare_observation(value: object, role: str, shipment_id: str) -> tuple[dict, Decimal]:
    label = role.lower()
    _require(isinstance(value, dict), f"{label} observation must be an object")
    _require(value.get("measurement_role") == role, f"{label} measurement role mismatch")
    _require(value.get("shipment_id") == shipment_id, f"{label} shipment mismatch")
    _require(value.get("weight_unit") == "lb", f"{label} unit must be lb")
    for field in ("id", "ticket_id", "evidence_link_id"):
        _require(isinstance(value.get(field), str) and value[field], f"{label} {field} is required")
    weight = _decimal(value.get("weight_value"), f"{label}.weight_value")
    return value, weight


def determine_containerized_reimbursement_tolerance(case: dict) -> dict:
    """Decide only whether Item 4.13's reimbursement tolerance is crossed."""

    case, case_id, shipment_id, pickup_date = _case_header(case)
    initial_result = _validate_initial_result(case.get("initial_weight_result"))
    original, original_tare = _tare_observation(case.get("original_tare_observation"), "ORIGINAL_TARE", shipment_id)
    reweigh, reweigh_tare = _tare_observation(case.get("reweigh_tare_observation"), "REWEIGH_TARE", shipment_id)
    _require(original["id"] != reweigh["id"], "tare observation IDs must be distinct")
    _require(original["ticket_id"] != reweigh["ticket_id"], "tare ticket IDs must be distinct")

    common = {
        **_base_result(case_id, shipment_id, pickup_date.isoformat(), REIMBURSEMENT_RULE_ID, REIMBURSEMENT_PROVENANCE),
        "input_snapshot": {
            "initial_weight_result_case_id": initial_result.get("case_id"),
            "original_tare_observation_id": original["id"],
            "reweigh_tare_observation_id": reweigh["id"],
        },
        "evidence": {
            "initial_weight_result_requirement_id": INITIAL_RESULT_REQUIREMENT_ID,
            "tare_ticket_requirement_id": TARE_TICKET_REQUIREMENT_ID,
            "original_tare_evidence_link_id": original["evidence_link_id"],
            "reweigh_tare_evidence_link_id": reweigh["evidence_link_id"],
        },
    }
    blocked_reasons: list[str] = []
    if not EFFECTIVE_FROM <= pickup_date <= EFFECTIVE_TO:
        blocked_reasons.append("OUTSIDE_RULE_EFFECTIVE_PERIOD")
    if initial_result["status"] == "BLOCKED":
        blocked_reasons.append("INITIAL_WEIGHT_RESULT_BLOCKED")
    if original.get("evidence_review_status") != "REVIEWED":
        blocked_reasons.append("ORIGINAL_TARE_EVIDENCE_MISSING_OR_UNREVIEWED")
    if reweigh.get("evidence_review_status") != "REVIEWED":
        blocked_reasons.append("REWEIGH_TARE_EVIDENCE_MISSING_OR_UNREVIEWED")
    if original_tare <= ZERO:
        blocked_reasons.append("ORIGINAL_TARE_NOT_POSITIVE")
    if blocked_reasons:
        result = {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": blocked_reasons,
        }
        if initial_result["status"] == "BLOCKED":
            result["upstream_blocked_reasons"] = initial_result.get("blocked_reasons", [])
        return result

    calculation = initial_result.get("calculation")
    _require(isinstance(calculation, dict), "FINAL initial_weight_result lacks calculation")
    _require(calculation.get("result_unit") == "lb", "initial_weight_result unit must be lb")
    initial_net = _decimal(calculation.get("result"), "initial_weight_result.calculation.result")
    _require(initial_net > ZERO, "initial net must be positive")
    branch = _branch(initial_net)
    increase = max(reweigh_tare - original_tare, ZERO)
    lower_tare = min(original_tare, reweigh_tare)

    if reweigh_tare <= original_tare:
        eligible = False
        threshold_kind = "NOT_APPLIED_NEW_TARE_NOT_GREATER"
        threshold_value = None
        comparison_operator = "NOT_APPLIED"
        reason_code = "NEW_TARE_NOT_GREATER_THAN_ORIGINAL"
    elif branch == "AT_OR_BELOW_5000":
        threshold_kind = "FIXED_150_LB"
        threshold_value = _canonical_decimal(ONE_HUNDRED_FIFTY)
        comparison_operator = "GT"
        eligible = increase > ONE_HUNDRED_FIFTY
        reason_code = "REIMBURSEMENT_TOLERANCE_CROSSED" if eligible else "REIMBURSEMENT_TOLERANCE_NOT_CROSSED"
    else:
        threshold = lower_tare * FIVE_PERCENT
        threshold_kind = "FIVE_PERCENT_OF_LOWER_TARE"
        threshold_value = _canonical_decimal(threshold)
        comparison_operator = "GTE"
        eligible = increase >= threshold
        reason_code = "REIMBURSEMENT_TOLERANCE_CROSSED" if eligible else "REIMBURSEMENT_TOLERANCE_NOT_CROSSED"

    return {
        **common,
        "status": "FINAL",
        "human_review_required": False,
        "eligibility": {
            "decision_kind": "CONTAINERIZED_REIMBURSEMENT_TOLERANCE_CROSSED",
            "eligible": eligible,
            "reason_code": reason_code,
            "branch_selector_fact_type": "FINAL_REVIEWED_INITIAL_NET_SCALE_WEIGHT",
            "branch": branch,
            "branch_weight": _canonical_decimal(initial_net),
            "original_tare_weight": _canonical_decimal(original_tare),
            "reweigh_tare_weight": _canonical_decimal(reweigh_tare),
            "lower_tare_weight": _canonical_decimal(lower_tare),
            "tare_increase": _canonical_decimal(increase),
            "threshold_kind": threshold_kind,
            "threshold_value": threshold_value,
            "comparison_operator": comparison_operator,
            "weight_unit": "lb",
            "rounding_rule": "NONE_EXACT_DECIMAL",
        },
    }

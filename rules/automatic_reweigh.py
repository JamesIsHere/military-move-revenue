"""Deterministic automatic-reweigh requirement under 2026 400NG Item 4.8."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation


RULE_PACKAGE_ID = "RP-DP3-2026-AUTO-REWEIGH-1"
RULE_ID = "RULE-AUTOMATIC-REWEIGH-REQUIRED"
WEIGHT_RULE_PACKAGE_ID = "RP-DP3-2026-WEIGHT-1"
WEIGHT_RULE_ID = "RULE-INITIAL-NET-SCALE-WEIGHT"
SOURCE_VERSION_ID = "SV-DP3-2026-400NG-2025-12-05"
PROVENANCE = (
    {"source_claim_id": "CLM-0020", "source_locator_id": "LOC-0018"},
    {"source_claim_id": "CLM-0021", "source_locator_id": "LOC-0018"},
    {"source_claim_id": "CLM-0022", "source_locator_id": "LOC-0018"},
)
GRADE_THRESHOLDS = {
    "E1_THRU_E5": Decimal("4000"),
    "E6_THRU_O10": Decimal("7000"),
    "DOW_CIVILIAN": Decimal("7000"),
}
DECIMAL_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")


class RuleInputError(ValueError):
    """Raised when the upstream decision structure is invalid or tampered."""


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


def determine_automatic_reweigh(case: dict) -> dict:
    """Determine whether Item 4.8 requires an automatic reweigh.

    The caller supplies an already classified grade band. This rule deliberately
    does not map individual grades, calculate a reweigh fee, select a billing
    code, or choose the controlling weight after a reweigh.
    """

    _require(isinstance(case, dict), "case must be an object")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id, "case_id is required")
    data_status = case.get("data_status")
    _require(data_status in {"synthetic", "authorized_sanitized"}, "data_status must be synthetic or authorized_sanitized")
    _require(
        case.get("grade_band_fact_status") == data_status,
        "grade_band_fact_status must match the case data_status",
    )

    initial_weight = case.get("initial_weight_result")
    _require(isinstance(initial_weight, dict), "initial_weight_result must be an object")
    _require(
        initial_weight.get("rule_package_id") == WEIGHT_RULE_PACKAGE_ID,
        "initial_weight_result uses an unknown rule package",
    )
    rule_ids = initial_weight.get("rule_ids")
    _require(isinstance(rule_ids, list) and WEIGHT_RULE_ID in rule_ids, "initial_weight_result lacks the net-weight rule")
    _require(initial_weight.get("status") in {"FINAL", "BLOCKED"}, "initial_weight_result has invalid status")

    common = {
        "case_id": case_id,
        "rule_package_id": RULE_PACKAGE_ID,
        "rule_id": RULE_ID,
        "input_snapshot": {
            "grade_band": case.get("grade_band"),
            "initial_weight_case_id": initial_weight.get("case_id"),
        },
        "evidence": {
            "grade_band_requirement_id": "EVID-REWEIGH-001",
            "grade_band_fact_status": case["grade_band_fact_status"],
            "initial_weight_evidence": initial_weight.get("evidence", {}),
        },
        "provenance": [
            {"source_version_id": SOURCE_VERSION_ID, **reference} for reference in PROVENANCE
        ],
        "unresolved_assumptions": [],
    }

    if initial_weight["status"] == "BLOCKED":
        return {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": ["INITIAL_WEIGHT_DETERMINATION_BLOCKED"],
            "upstream_blocked_reasons": initial_weight.get("blocked_reasons", []),
        }

    calculation = initial_weight.get("calculation")
    _require(isinstance(calculation, dict), "FINAL initial_weight_result lacks calculation")
    _require(calculation.get("result_unit") == "lb", "initial_weight_result unit must be lb")
    weight = _decimal(calculation.get("result"), "initial_weight_result.calculation.result")

    grade_band = case.get("grade_band")
    if grade_band not in GRADE_THRESHOLDS:
        return {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": ["GRADE_BAND_NOT_COVERED_BY_ITEM_4_8"],
        }

    threshold = GRADE_THRESHOLDS[grade_band]
    required = weight >= threshold
    return {
        **common,
        "status": "FINAL",
        "human_review_required": False,
        "decision": {
            "automatic_reweigh_required": required,
            "preapproval_required": False,
            "grade_band": grade_band,
            "initial_weight": _canonical_decimal(weight),
            "weight_unit": "lb",
            "comparison_operator": ">=",
            "threshold": _canonical_decimal(threshold),
            "threshold_unit": "lb",
        },
    }

"""Select the lower initial-or-completed-reweigh scale-weight reference."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from rules.completed_reweigh_selection import (
    PROVENANCE as COMPLETED_REWEIGH_PROVENANCE,
    RULE_ID as COMPLETED_REWEIGH_RULE_ID,
    RULE_PACKAGE_ID as COMPLETED_REWEIGH_PACKAGE_ID,
)
from rules.weight_determination import (
    PROVENANCE as INITIAL_WEIGHT_PROVENANCE_BASE,
    RULE_IDS as INITIAL_WEIGHT_RULE_IDS,
    RULE_PACKAGE_ID as INITIAL_WEIGHT_PACKAGE_ID,
    SOURCE_VERSION_ID as INITIAL_WEIGHT_SOURCE_VERSION_ID,
)


RULE_PACKAGE_ID = "RP-DP3-2026-SCALE-REWEIGH-LOWER-1"
RULE_ID = "RULE-LOWER-OF-INITIAL-AND-COMPLETED-REWEIGH"
SOURCE_VERSION_ID = "SV-DP3-2026-TOS-C1-2026-02-18"
PROVENANCE = (
    {
        "source_version_id": SOURCE_VERSION_ID,
        "source_claim_id": "CLM-0030",
        "source_locator_id": "LOC-0026",
    },
)
INITIAL_RESULT_REQUIREMENT_ID = "EVID-SCALE-REWEIGH-LOWER-001"
COMPLETED_REWEIGH_RESULT_REQUIREMENT_ID = "EVID-SCALE-REWEIGH-LOWER-002"
INITIAL_NET_RULE_ID = "RULE-INITIAL-NET-SCALE-WEIGHT"
EXPECTED_INITIAL_PROVENANCE = tuple(
    {"source_version_id": INITIAL_WEIGHT_SOURCE_VERSION_ID, **reference}
    for reference in INITIAL_WEIGHT_PROVENANCE_BASE
)
DECIMAL_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")


class RuleInputError(ValueError):
    """Raised when an upstream result is malformed, unknown, or tampered."""


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


def _validate_initial_result(result: object) -> dict:
    _require(isinstance(result, dict), "initial_weight_result must be an object")
    _require(result.get("rule_package_id") == INITIAL_WEIGHT_PACKAGE_ID, "initial_weight_result uses an unknown rule package")
    rule_ids = result.get("rule_ids")
    _require(isinstance(rule_ids, list) and set(rule_ids) == set(INITIAL_WEIGHT_RULE_IDS), "initial_weight_result rule set mismatch")
    _require(INITIAL_NET_RULE_ID in rule_ids, "initial_weight_result lacks the net-weight rule")
    _require(result.get("provenance") == list(EXPECTED_INITIAL_PROVENANCE), "initial_weight_result provenance mismatch")
    _require(result.get("status") in {"FINAL", "BLOCKED"}, "initial_weight_result has invalid status")
    return result


def _validate_completed_reweigh_result(result: object) -> dict:
    _require(isinstance(result, dict), "completed_reweigh_result must be an object")
    _require(
        result.get("rule_package_id") == COMPLETED_REWEIGH_PACKAGE_ID,
        "completed_reweigh_result uses an unknown rule package",
    )
    _require(result.get("rule_id") == COMPLETED_REWEIGH_RULE_ID, "completed_reweigh_result rule mismatch")
    _require(
        result.get("provenance") == list(COMPLETED_REWEIGH_PROVENANCE),
        "completed_reweigh_result provenance mismatch",
    )
    _require(result.get("status") in {"FINAL", "BLOCKED"}, "completed_reweigh_result has invalid status")
    return result


def select_scale_reweigh_lower_reference(case: dict) -> dict:
    """Return the lower verified scale-weight reference or a blocked result.

    This rule covers only a final initial scale weight and a final selected
    completed-reweigh net. It does not decide charge-specific weight use,
    constructive/containerized paths, tolerances, fees, refunds, or money.
    """

    _require(isinstance(case, dict), "case must be an object")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id, "case_id is required")
    _require(
        case.get("data_status") in {"synthetic", "authorized_sanitized"},
        "data_status must be synthetic or authorized_sanitized",
    )
    initial_result = _validate_initial_result(case.get("initial_weight_result"))
    reweigh_result = _validate_completed_reweigh_result(case.get("completed_reweigh_result"))

    common = {
        "case_id": case_id,
        "rule_package_id": RULE_PACKAGE_ID,
        "rule_id": RULE_ID,
        "input_snapshot": {
            "initial_weight_result_case_id": initial_result.get("case_id"),
            "completed_reweigh_result_case_id": reweigh_result.get("case_id"),
        },
        "evidence": {
            "initial_result_requirement_id": INITIAL_RESULT_REQUIREMENT_ID,
            "completed_reweigh_result_requirement_id": COMPLETED_REWEIGH_RESULT_REQUIREMENT_ID,
            "initial_weight_evidence": initial_result.get("evidence", {}),
            "completed_reweigh_evidence": reweigh_result.get("evidence", {}),
        },
        "provenance": [dict(reference) for reference in PROVENANCE],
        "unresolved_assumptions": [],
    }

    blocked_reasons: list[str] = []
    upstream_reasons: dict[str, list[str]] = {}
    if initial_result["status"] == "BLOCKED":
        blocked_reasons.append("INITIAL_WEIGHT_RESULT_BLOCKED")
        upstream_reasons["initial_weight_result"] = initial_result.get("blocked_reasons", [])
    if reweigh_result["status"] == "BLOCKED":
        blocked_reasons.append("COMPLETED_REWEIGH_SELECTION_BLOCKED")
        upstream_reasons["completed_reweigh_result"] = reweigh_result.get("blocked_reasons", [])
    if blocked_reasons:
        return {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": blocked_reasons,
            "upstream_blocked_reasons": upstream_reasons,
        }

    initial_calculation = initial_result.get("calculation")
    _require(isinstance(initial_calculation, dict), "FINAL initial_weight_result lacks calculation")
    _require(initial_calculation.get("result_unit") == "lb", "initial_weight_result unit must be lb")
    initial_weight = _decimal(initial_calculation.get("result"), "initial_weight_result.calculation.result")

    reweigh_selection = reweigh_result.get("selection")
    _require(isinstance(reweigh_selection, dict), "FINAL completed_reweigh_result lacks selection")
    _require(reweigh_selection.get("weight_unit") == "lb", "completed_reweigh_result unit must be lb")
    reweigh_weight = _decimal(
        reweigh_selection.get("selected_net_weight"),
        "completed_reweigh_result.selection.selected_net_weight",
    )
    selected_observation_ids = reweigh_selection.get("selected_observation_ids")
    _require(
        isinstance(selected_observation_ids, list)
        and selected_observation_ids
        and all(isinstance(value, str) and value for value in selected_observation_ids),
        "completed_reweigh_result selected observation IDs are invalid",
    )

    lower_weight = min(initial_weight, reweigh_weight)
    if initial_weight < reweigh_weight:
        selected_source = "INITIAL_SCALE_WEIGHT"
    elif reweigh_weight < initial_weight:
        selected_source = "COMPLETED_REWEIGH"
    else:
        selected_source = "TIE"

    return {
        **common,
        "status": "FINAL",
        "human_review_required": False,
        "reference": {
            "comparison_method": "LOWER_OF_INITIAL_AND_COMPLETED_REWEIGH",
            "lower_weight": _canonical_decimal(lower_weight),
            "weight_unit": "lb",
            "selected_source": selected_source,
            "initial_net_weight": _canonical_decimal(initial_weight),
            "completed_reweigh_net_weight": _canonical_decimal(reweigh_weight),
            "selected_reweigh_observation_ids": list(selected_observation_ids),
        },
    }

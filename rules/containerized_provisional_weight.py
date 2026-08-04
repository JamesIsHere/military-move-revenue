"""Calculate and select a 2026 DP3 containerized provisional weight."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from rules.weight_determination import (
    PROVENANCE as INITIAL_WEIGHT_PROVENANCE_BASE,
    RULE_IDS as INITIAL_WEIGHT_RULE_IDS,
    RULE_PACKAGE_ID as INITIAL_WEIGHT_PACKAGE_ID,
    SOURCE_VERSION_ID as INITIAL_WEIGHT_SOURCE_VERSION_ID,
)


RULE_PACKAGE_ID = "RP-DP3-2026-CONTAINERIZED-PROVISIONAL-1"
CALCULATION_RULE_ID = "RULE-CONTAINERIZED-PROVISIONAL-NET-WEIGHT"
SELECTION_RULE_ID = "RULE-LOWER-OF-INITIAL-AND-CONTAINERIZED-PROVISIONAL-WEIGHT"
RULE_IDS = (CALCULATION_RULE_ID, SELECTION_RULE_ID)
SOURCE_VERSION_ID = "SV-DP3-2026-400NG-2025-12-05"
PROVENANCE = (
    {
        "source_version_id": SOURCE_VERSION_ID,
        "source_claim_id": "CLM-0027",
        "source_locator_id": "LOC-0023",
    },
)
ORIGINAL_TARE_EVIDENCE_REQUIREMENT_ID = "EVID-CONTAINERIZED-PROVISIONAL-001"
NEW_GROSS_EVIDENCE_REQUIREMENT_ID = "EVID-CONTAINERIZED-PROVISIONAL-002"
INITIAL_RESULT_EVIDENCE_REQUIREMENT_ID = "EVID-CONTAINERIZED-PROVISIONAL-003"
INITIAL_NET_RULE_ID = "RULE-INITIAL-NET-SCALE-WEIGHT"
EXPECTED_INITIAL_PROVENANCE = tuple(
    {"source_version_id": INITIAL_WEIGHT_SOURCE_VERSION_ID, **reference}
    for reference in INITIAL_WEIGHT_PROVENANCE_BASE
)
DECIMAL_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")


class RuleInputError(ValueError):
    """Raised when a provisional-weight input is malformed or tampered."""


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


def _instant(value: object, label: str) -> datetime:
    _require(isinstance(value, str) and value, f"{label} must be an ISO instant")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuleInputError(f"{label} must be an ISO instant") from exc
    _require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return parsed


def _index(records: object, label: str) -> dict[str, dict]:
    _require(isinstance(records, list), f"{label} must be a list")
    result: dict[str, dict] = {}
    for record in records:
        _require(isinstance(record, dict), f"{label} record must be an object")
        record_id = record.get("id")
        _require(isinstance(record_id, str) and record_id, f"{label} record id is required")
        _require(record_id not in result, f"duplicate {label} id {record_id}")
        result[record_id] = record
    return result


def _validate_initial_result(result: object) -> dict:
    _require(isinstance(result, dict), "initial_weight_result must be an object")
    _require(result.get("rule_package_id") == INITIAL_WEIGHT_PACKAGE_ID, "initial_weight_result uses an unknown rule package")
    rule_ids = result.get("rule_ids")
    _require(isinstance(rule_ids, list) and set(rule_ids) == set(INITIAL_WEIGHT_RULE_IDS), "initial_weight_result rule set mismatch")
    _require(INITIAL_NET_RULE_ID in rule_ids, "initial_weight_result lacks the net-weight rule")
    _require(result.get("provenance") == list(EXPECTED_INITIAL_PROVENANCE), "initial_weight_result provenance mismatch")
    _require(result.get("status") in {"FINAL", "BLOCKED"}, "initial_weight_result has invalid status")
    return result


def _reviewed_measurement_evidence(
    measurement: dict,
    *,
    evidence_role: str,
    evidence_links: dict[str, dict],
    tickets: dict[str, dict],
    document_versions: dict[str, dict],
    documents: dict[str, dict],
) -> str | None:
    ticket_id = measurement.get("weight_ticket_id")
    if ticket_id not in tickets:
        return None
    ticket = tickets[ticket_id]
    matches = [
        link
        for link in evidence_links.values()
        if link.get("target_kind") == "WEIGHT_TICKET_MEASUREMENT"
        and link.get("target_id") == measurement.get("id")
        and link.get("evidence_role") == evidence_role
        and link.get("review_status") == "REVIEWED"
        and link.get("document_version_id") == ticket.get("document_version_id")
    ]
    if len(matches) != 1:
        return None
    document_version_id = matches[0].get("document_version_id")
    if document_version_id not in document_versions:
        return None
    document_id = document_versions[document_version_id].get("document_id")
    if document_id not in documents or documents[document_id].get("document_type") != "WEIGHT_TICKET":
        return None
    return matches[0]["id"]


def determine_containerized_provisional_weight(case: dict) -> dict:
    """Return the exact provisional net and lower initial/provisional reference.

    Only 400NG Item 4.13(1)-(2) is implemented. A later new tare, the
    reimbursement-tolerance decision, fees, refunds, billing items, and money
    remain outside this package.
    """

    _require(isinstance(case, dict), "case must be an object")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id, "case_id is required")
    _require(
        case.get("data_status") in {"synthetic", "authorized_sanitized"},
        "data_status must be synthetic or authorized_sanitized",
    )
    initial_result = _validate_initial_result(case.get("initial_weight_result"))
    records = case.get("records")
    _require(isinstance(records, dict), "records must be an object")

    provisional_cases = _index(records.get("containerized_reweigh_cases"), "containerized_reweigh_cases")
    measurements = _index(records.get("weight_ticket_measurements"), "weight_ticket_measurements")
    events = _index(records.get("weighing_events"), "weighing_events")
    tickets = _index(records.get("weight_tickets"), "weight_tickets")
    evidence_links = _index(records.get("evidence_links"), "evidence_links")
    document_versions = _index(records.get("document_versions"), "document_versions")
    documents = _index(records.get("documents"), "documents")
    _require(len(provisional_cases) == 1, "exactly one containerized provisional case is required")
    provisional_case = next(iter(provisional_cases.values()))

    original_tare_id = provisional_case.get("original_tare_measurement_id")
    new_gross_id = provisional_case.get("new_gross_measurement_id")
    _require(original_tare_id in measurements, "containerized case references unknown original tare")
    _require(new_gross_id in measurements, "containerized case references unknown new gross")
    original_tare = measurements[original_tare_id]
    new_gross = measurements[new_gross_id]
    _require(original_tare.get("measurement_role") == "ORIGINAL_TARE", "original tare measurement role mismatch")
    _require(new_gross.get("measurement_role") == "NEW_GROSS", "new gross measurement role mismatch")
    _require(original_tare.get("weight_unit") == "lb", "original tare unit must be lb")
    _require(new_gross.get("weight_unit") == "lb", "new gross unit must be lb")
    original_tare_weight = _decimal(original_tare.get("weight_value"), "original_tare.weight_value")
    new_gross_weight = _decimal(new_gross.get("weight_value"), "new_gross.weight_value")

    original_event_id = original_tare.get("weighing_event_id")
    new_gross_event_id = new_gross.get("weighing_event_id")
    _require(original_event_id in events and new_gross_event_id in events, "provisional measurement event is missing")
    original_event = events[original_event_id]
    new_gross_event = events[new_gross_event_id]
    shipment_id = provisional_case.get("shipment_id")
    _require(original_event.get("shipment_id") == shipment_id, "original tare and provisional case shipments differ")
    _require(new_gross_event.get("shipment_id") == shipment_id, "new gross and provisional case shipments differ")
    original_instant = _instant(original_event.get("occurred_at_or_date"), "original tare occurred_at_or_date")
    new_gross_instant = _instant(new_gross_event.get("occurred_at_or_date"), "new gross occurred_at_or_date")
    _require(original_instant < new_gross_instant, "original tare must precede new gross")
    _require(
        _instant(provisional_case.get("created_at"), "containerized case created_at") >= new_gross_instant,
        "containerized case cannot precede new gross",
    )

    original_evidence_link_id = _reviewed_measurement_evidence(
        original_tare,
        evidence_role="ORIGINAL_TARE_TRUE_COPY",
        evidence_links=evidence_links,
        tickets=tickets,
        document_versions=document_versions,
        documents=documents,
    )
    new_gross_evidence_link_id = _reviewed_measurement_evidence(
        new_gross,
        evidence_role="NEW_GROSS_TRUE_COPY",
        evidence_links=evidence_links,
        tickets=tickets,
        document_versions=document_versions,
        documents=documents,
    )

    blocked_reasons: list[str] = []
    if original_tare_weight <= 0:
        blocked_reasons.append("ORIGINAL_TARE_NOT_POSITIVE")
    if new_gross_weight <= original_tare_weight:
        blocked_reasons.append("NEW_GROSS_NOT_GREATER_THAN_ORIGINAL_TARE")
    if original_evidence_link_id is None:
        blocked_reasons.append("ORIGINAL_TARE_EVIDENCE_MISSING_OR_UNREVIEWED")
    if new_gross_evidence_link_id is None:
        blocked_reasons.append("NEW_GROSS_EVIDENCE_MISSING_OR_UNREVIEWED")
    if provisional_case.get("provisional_readiness_status") != "READY_FOR_DETERMINISTIC_RULE":
        blocked_reasons.append("CONTAINERIZED_PROVISIONAL_CASE_NOT_READY")
    upstream_blocked_reasons: list[str] = []
    if initial_result["status"] == "BLOCKED":
        blocked_reasons.append("INITIAL_WEIGHT_RESULT_BLOCKED")
        upstream_blocked_reasons = initial_result.get("blocked_reasons", [])

    common = {
        "case_id": case_id,
        "rule_package_id": RULE_PACKAGE_ID,
        "rule_ids": list(RULE_IDS),
        "input_snapshot": {
            "shipment_id": shipment_id,
            "containerized_reweigh_case_id": provisional_case["id"],
            "initial_weight_result_case_id": initial_result.get("case_id"),
            "original_tare_measurement_id": original_tare["id"],
            "new_gross_measurement_id": new_gross["id"],
            "original_tare_weight": _canonical_decimal(original_tare_weight),
            "new_gross_weight": _canonical_decimal(new_gross_weight),
            "weight_unit": "lb",
        },
        "evidence": {
            "original_tare_requirement_id": ORIGINAL_TARE_EVIDENCE_REQUIREMENT_ID,
            "new_gross_requirement_id": NEW_GROSS_EVIDENCE_REQUIREMENT_ID,
            "initial_result_requirement_id": INITIAL_RESULT_EVIDENCE_REQUIREMENT_ID,
            "original_tare_evidence_link_id": original_evidence_link_id,
            "new_gross_evidence_link_id": new_gross_evidence_link_id,
        },
        "provenance": [dict(reference) for reference in PROVENANCE],
        "unresolved_assumptions": [],
    }
    if blocked_reasons:
        result = {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": blocked_reasons,
        }
        if upstream_blocked_reasons:
            result["upstream_blocked_reasons"] = upstream_blocked_reasons
        return result

    initial_calculation = initial_result.get("calculation")
    _require(isinstance(initial_calculation, dict), "FINAL initial_weight_result lacks calculation")
    _require(initial_calculation.get("result_unit") == "lb", "initial_weight_result unit must be lb")
    initial_weight = _decimal(initial_calculation.get("result"), "initial_weight_result.calculation.result")
    provisional_weight = new_gross_weight - original_tare_weight
    selected_weight = min(initial_weight, provisional_weight)
    if initial_weight < provisional_weight:
        selected_source = "INITIAL_SCALE_WEIGHT"
    elif provisional_weight < initial_weight:
        selected_source = "CONTAINERIZED_PROVISIONAL_WEIGHT"
    else:
        selected_source = "TIE"

    return {
        **common,
        "status": "FINAL",
        "human_review_required": False,
        "calculation": {
            "expression": "new_gross_weight_lb - original_tare_weight_lb",
            "steps": [
                {"ordinal": 1, "operation": "NEW_GROSS", "value": _canonical_decimal(new_gross_weight), "unit": "lb"},
                {"ordinal": 2, "operation": "SUBTRACT_ORIGINAL_TARE", "value": _canonical_decimal(original_tare_weight), "unit": "lb"},
            ],
            "result": _canonical_decimal(provisional_weight),
            "result_unit": "lb",
            "rounding_rule": "NONE_SOURCE_DOES_NOT_SPECIFY_ROUNDING",
        },
        "selection": {
            "comparison_method": "LOWER_OF_INITIAL_AND_CONTAINERIZED_PROVISIONAL_WEIGHT",
            "selected_weight": _canonical_decimal(selected_weight),
            "weight_unit": "lb",
            "selected_source": selected_source,
            "initial_net_weight": _canonical_decimal(initial_weight),
            "provisional_net_weight": _canonical_decimal(provisional_weight),
        },
    }

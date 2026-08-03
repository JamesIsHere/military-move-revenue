"""Deterministic initial scale-weight determination under 2026 400NG Item 4."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation


RULE_PACKAGE_ID = "RP-DP3-2026-WEIGHT-1"
SOURCE_VERSION_ID = "SV-DP3-2026-400NG-2025-12-05"
RULE_IDS = (
    "RULE-INITIAL-NET-SCALE-WEIGHT",
    "RULE-INITIAL-SCALE-METHOD",
    "RULE-INITIAL-WEIGHING-CONDITIONS",
    "RULE-INITIAL-WEIGHT-TICKET-SUFFICIENCY",
)
PROVENANCE = (
    {"source_claim_id": "CLM-0013", "source_locator_id": "LOC-0011"},
    {"source_claim_id": "CLM-0014", "source_locator_id": "LOC-0012"},
    {"source_claim_id": "CLM-0015", "source_locator_id": "LOC-0013"},
    {"source_claim_id": "CLM-0016", "source_locator_id": "LOC-0014"},
    {"source_claim_id": "CLM-0017", "source_locator_id": "LOC-0015"},
    {"source_claim_id": "CLM-0018", "source_locator_id": "LOC-0016"},
    {"source_claim_id": "CLM-0019", "source_locator_id": "LOC-0017"},
)
DECIMAL_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")
REQUIRED_TICKET_FIELDS = (
    "weighmaster_signature",
    "scale_name_and_location",
    "weighing_date",
    "weight_entry_labels",
    "vehicle_or_container_identifier",
    "shipper_identity_reference",
    "shipment_or_bl_reference",
)
SCALE_TYPES = {"vehicle", "platform", "warehouse"}
FUEL_FULL = "FULL_AT_BOTH_WEIGHINGS"
FUEL_NO_ADDITION = "NO_FUEL_ADDED_BETWEEN_WEIGHINGS"


class RuleInputError(ValueError):
    """Raised when a rule input is structurally invalid rather than incomplete."""


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


def _deduplicate(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def determine_initial_scale_weight(case: dict) -> dict:
    """Return a FINAL explained net weight or a BLOCKED human-review result.

    This function intentionally does not rate a charge, select a reweigh, apply a
    constructive article weight, or use an external billing item code.
    """

    _require(isinstance(case, dict), "case must be an object")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id, "case_id is required")
    _require(
        case.get("data_status") in {"synthetic", "authorized_sanitized"},
        "data_status must be synthetic or authorized_sanitized",
    )
    _require(case.get("weighing_context") == "initial", "only initial weighing_context is implemented")

    measurements = case.get("measurements")
    tickets = case.get("tickets")
    facts = case.get("shipment_facts")
    _require(isinstance(measurements, list) and len(measurements) == 2, "exactly two measurements are required")
    _require(isinstance(tickets, list) and tickets, "at least one weight ticket is required")
    _require(isinstance(facts, dict), "shipment_facts must be an object")

    measurements_by_kind: dict[str, dict] = {}
    sequences: set[int] = set()
    for measurement in measurements:
        _require(isinstance(measurement, dict), "measurement must be an object")
        kind = measurement.get("kind")
        _require(kind in {"gross", "tare"}, "measurement kind must be gross or tare")
        _require(kind not in measurements_by_kind, f"duplicate {kind} measurement")
        _require(measurement.get("unit") == "lb", f"{kind} measurement unit must be lb")
        sequence = measurement.get("sequence")
        _require(isinstance(sequence, int) and sequence in {1, 2}, f"{kind} sequence must be 1 or 2")
        _require(sequence not in sequences, "measurement sequences must be unique")
        sequences.add(sequence)
        ticket_id = measurement.get("ticket_id")
        _require(isinstance(ticket_id, str) and ticket_id, f"{kind} ticket_id is required")
        measurements_by_kind[kind] = measurement

    gross = _decimal(measurements_by_kind["gross"].get("weight"), "gross.weight")
    tare = _decimal(measurements_by_kind["tare"].get("weight"), "tare.weight")
    net = gross - tare

    tickets_by_id: dict[str, dict] = {}
    for ticket in tickets:
        _require(isinstance(ticket, dict), "ticket must be an object")
        ticket_id = ticket.get("id")
        _require(isinstance(ticket_id, str) and ticket_id, "ticket id is required")
        _require(ticket_id not in tickets_by_id, f"duplicate ticket id {ticket_id}")
        _require(ticket.get("scale_type") in SCALE_TYPES, f"ticket {ticket_id} has invalid scale_type")
        scale_id = ticket.get("scale_id")
        _require(isinstance(scale_id, str) and scale_id, f"ticket {ticket_id} scale_id is required")
        entry_kinds = ticket.get("entry_kinds")
        _require(isinstance(entry_kinds, list), f"ticket {ticket_id} entry_kinds must be a list")
        _require(set(entry_kinds).issubset({"gross", "tare"}), f"ticket {ticket_id} has invalid entry kind")
        presence = ticket.get("required_field_presence")
        _require(isinstance(presence, dict), f"ticket {ticket_id} required_field_presence must be an object")
        tickets_by_id[ticket_id] = ticket

    reasons: list[str] = []
    determining_ticket_ids: list[str] = []
    for kind in ("gross", "tare"):
        ticket_id = measurements_by_kind[kind]["ticket_id"]
        if ticket_id not in tickets_by_id:
            reasons.append(f"MISSING_{kind.upper()}_TICKET")
            continue
        determining_ticket_ids.append(ticket_id)
        if kind not in tickets_by_id[ticket_id]["entry_kinds"]:
            reasons.append(f"TICKET_MISSING_{kind.upper()}_ENTRY")

    for ticket_id in _deduplicate(determining_ticket_ids):
        ticket = tickets_by_id[ticket_id]
        if ticket.get("certified_scale") is not True:
            reasons.append("UNCERTIFIED_SCALE")
        if ticket.get("true_copy_available") is not True:
            reasons.append("MISSING_TRUE_TICKET_COPY")
        presence = ticket["required_field_presence"]
        for field in REQUIRED_TICKET_FIELDS:
            if presence.get(field) is not True:
                reasons.append(f"MISSING_TICKET_FIELD_{field.upper()}")

    if net <= 0:
        reasons.append("NONPOSITIVE_NET_WEIGHT")

    if facts.get("same_vehicle_or_container") is not True:
        reasons.append("VEHICLE_OR_CONTAINER_CONTINUITY_UNPROVED")

    determining_tickets = [tickets_by_id[ticket_id] for ticket_id in _deduplicate(determining_ticket_ids) if ticket_id in tickets_by_id]
    scale_types = {ticket["scale_type"] for ticket in determining_tickets}
    if scale_types.intersection({"platform", "warehouse"}):
        containerized = facts.get("containerized_at_no_additional_cost") is True
        if net > Decimal("1000") and not containerized:
            reasons.append("PLATFORM_OR_WAREHOUSE_SCALE_WEIGHT_EXCEEDS_1000_LB")

    if "vehicle" in scale_types:
        if facts.get("equipment_consistent") is not True:
            reasons.append("TRANSPORT_EQUIPMENT_NOT_PROVEN_CONSISTENT")
        if facts.get("vehicle_unoccupied") is not True:
            reasons.append("VEHICLE_UNOCCUPIED_NOT_PROVEN")
        fuel_condition = facts.get("fuel_condition")
        tare_first = measurements_by_kind["tare"]["sequence"] == 1
        if fuel_condition != FUEL_FULL and not (tare_first and fuel_condition == FUEL_NO_ADDITION):
            reasons.append("FUEL_CONDITION_NOT_COMPLIANT")

    reasons = _deduplicate(reasons)
    common = {
        "case_id": case_id,
        "rule_package_id": RULE_PACKAGE_ID,
        "rule_ids": list(RULE_IDS),
        "input_snapshot": {
            "gross_weight": _canonical_decimal(gross),
            "tare_weight": _canonical_decimal(tare),
            "weight_unit": "lb",
            "gross_sequence": measurements_by_kind["gross"]["sequence"],
            "tare_sequence": measurements_by_kind["tare"]["sequence"],
            "determining_ticket_ids": _deduplicate(determining_ticket_ids),
        },
        "evidence": {
            "requirement_id": "EVID-WEIGHT-001",
            "ticket_ids": _deduplicate(determining_ticket_ids),
        },
        "provenance": [
            {"source_version_id": SOURCE_VERSION_ID, **reference} for reference in PROVENANCE
        ],
        "unresolved_assumptions": [],
    }

    if reasons:
        return {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": reasons,
        }

    return {
        **common,
        "status": "FINAL",
        "human_review_required": False,
        "calculation": {
            "expression": "gross_weight_lb - tare_weight_lb",
            "steps": [
                {"ordinal": 1, "operation": "GROSS", "value": _canonical_decimal(gross), "unit": "lb"},
                {"ordinal": 2, "operation": "SUBTRACT_TARE", "value": _canonical_decimal(tare), "unit": "lb"},
            ],
            "result": _canonical_decimal(net),
            "result_unit": "lb",
        },
    }

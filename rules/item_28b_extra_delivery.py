"""Rate eligible 2026 400NG Item 28B extra-delivery occurrences."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


RULE_PACKAGE_ID = "RP-DP3-2026-ITEM-28B-1"
SOURCE_CONTRACT_RULE_ID = "RULE-ITEM-28B-SCOPED-SOURCE-CONTRACT"
ELIGIBILITY_RULE_ID = "RULE-ITEM-28B-ELIGIBLE-OCCURRENCE"
RATING_RULE_ID = "RULE-ITEM-28B-EXPECTED-CHARGE"
RULE_IDS = (SOURCE_CONTRACT_RULE_ID, ELIGIBILITY_RULE_ID, RATING_RULE_ID)
INTERPRETATION_DECISION_ID = "INT-0002"
ITEM_CODE = "28B"
QUANTITY_UNIT = "EA"
CURRENCY = "USD"
UNIT_RATE = Decimal("198.50")
RATE_EFFECTIVE_FROM = date(2026, 5, 15)
RATE_EFFECTIVE_TO = date(2027, 5, 14)
RATE_SOURCE_CELL = "Additional Rates!A13:F13"
APPROVAL_REQUIREMENT_ID = "EVID-ITEM-28B-001"
PERFORMANCE_REQUIREMENT_ID = "EVID-ITEM-28B-002"
RATE_DATE_REQUIREMENT_ID = "EVID-ITEM-28B-003"
PROVENANCE = (
    {"source_version_id": "SV-DP3-2026-400NG-2025-12-05", "source_claim_id": "CLM-0001", "source_locator_id": "LOC-0001"},
    {"source_version_id": "SV-DP3-2026-RATES-2026", "source_claim_id": "CLM-0002", "source_locator_id": "LOC-0002"},
    {"source_version_id": "SV-DP3-2026-400NG-2025-12-05", "source_claim_id": "CLM-0010", "source_locator_id": "LOC-0010"},
    {"source_version_id": "SV-DP3-LIBRARY-SNAPSHOT-2026-08-03", "source_claim_id": "CLM-0037", "source_locator_id": "LOC-0033"},
    {"source_version_id": "SV-DP3-2026-400NG-2025-12-05", "source_claim_id": "CLM-0041", "source_locator_id": "LOC-0036"},
    {"source_version_id": "SV-DP3-2026-RATES-2026", "source_claim_id": "CLM-0042", "source_locator_id": "LOC-0037"},
    {"source_version_id": "SV-DP3-ITEM-CODES-2022-08-12", "source_claim_id": "CLM-0043", "source_locator_id": "LOC-0038"},
)
DECIMAL_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")


class RuleInputError(ValueError):
    """Raised when Item 28B input is malformed or tampered."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuleInputError(message)


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


def _local_date(value: object, label: str) -> date:
    _require(isinstance(value, str) and value, f"{label} must be an ISO local date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RuleInputError(f"{label} must be an ISO local date") from exc


def _instant(value: object, label: str) -> datetime:
    _require(isinstance(value, str) and value, f"{label} must be an ISO instant")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuleInputError(f"{label} must be an ISO instant") from exc
    _require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return parsed


def _decimal(value: object, label: str) -> Decimal:
    _require(isinstance(value, str), f"{label} must be an exact decimal JSON string")
    _require(bool(DECIMAL_RE.fullmatch(value)), f"{label} must be a canonical nonnegative decimal string")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise RuleInputError(f"{label} must be an exact decimal") from exc


def _reviewed_evidence(link_id: object, links: dict[str, dict], versions: dict[str, dict], *, target_kind: str, target_id: str, role: str) -> bool:
    if not isinstance(link_id, str) or link_id not in links:
        return False
    link = links[link_id]
    return (
        link.get("document_version_id") in versions
        and link.get("target_kind") == target_kind
        and link.get("target_id") == target_id
        and link.get("evidence_role") == role
        and link.get("review_status") == "REVIEWED"
    )


def rate_item_28b_extra_deliveries(case: dict) -> dict:
    """Return an exact expected Item 28B amount or a human-review block."""

    _require(isinstance(case, dict), "case must be an object")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id, "case_id is required")
    _require(case.get("data_status") in {"synthetic", "authorized_sanitized"}, "data_status must be synthetic or authorized_sanitized")
    _require(case.get("interpretation_decision_id") == INTERPRETATION_DECISION_ID, "Item 28B interpretation decision mismatch")
    records = case.get("records")
    _require(isinstance(records, dict), "records must be an object")

    shipments = _index(records.get("shipments"), "shipments")
    dates = _index(records.get("shipment_date_observations"), "shipment_date_observations")
    locations = _index(records.get("locations"), "locations")
    stops = _index(records.get("shipment_stops"), "shipment_stops")
    definitions = _index(records.get("service_definitions"), "service_definitions")
    documents = _index(records.get("documents"), "documents")
    versions = _index(records.get("document_versions"), "document_versions")
    performances = _index(records.get("service_performances"), "service_performances")
    approvals = _index(records.get("service_approval_events"), "service_approval_events")
    evidence_links = _index(records.get("evidence_links"), "evidence_links")
    _require(len(shipments) == 1, "Item 28B rating requires exactly one shipment")
    shipment_id = next(iter(shipments))
    shipment = shipments[shipment_id]
    _require(shipment.get("program_code") == "DP3" and shipment.get("domestic_indicator") is True, "shipment is outside domestic DP3 scope")

    actual_dates = [value for value in dates.values() if value.get("shipment_id") == shipment_id and value.get("date_role") == "ACTUAL_PICKUP"]
    _require(len(actual_dates) == 1, "exactly one actual pickup date observation is required")
    actual_date_record = actual_dates[0]
    actual_pickup_date = _local_date(actual_date_record.get("local_date"), "actual pickup date")
    _require(actual_date_record.get("observation_kind") == "PERFORMANCE_FACT", "actual pickup date must be a performance fact")

    _require(len(definitions) == 1, "exactly one Item 28B service definition is required")
    definition = next(iter(definitions.values()))
    _require(definition.get("service_code") == ITEM_CODE and definition.get("service_family") == "EXTRA_DELIVERY_STOP_OFF", "service definition is not Item 28B extra delivery")
    _require(definition.get("quantity_unit") == QUANTITY_UNIT, "Item 28B definition unit must be EA")
    _require(definition.get("rate_date_role") == "ACTUAL_PICKUP", "Item 28B rate date role must be ACTUAL_PICKUP")
    _require(definition.get("interpretation_decision_id") == INTERPRETATION_DECISION_ID, "Item 28B definition decision mismatch")

    sequences: set[int] = set()
    final_stops: list[dict] = []
    for stop in stops.values():
        _require(stop.get("shipment_id") == shipment_id, f"{stop['id']} belongs to another shipment")
        _require(stop.get("location_id") in locations, f"{stop['id']} references unknown location")
        sequence = stop.get("stop_sequence")
        _require(isinstance(sequence, int) and sequence > 0 and sequence not in sequences, "stop sequences must be unique positive integers")
        sequences.add(sequence)
        if stop.get("stop_role") == "FINAL_DELIVERY":
            final_stops.append(stop)
    _require(len(final_stops) == 1, "exactly one final delivery stop is required")
    final_sequence = final_stops[0]["stop_sequence"]

    for version in versions.values():
        _require(version.get("document_id") in documents, f"{version['id']} references unknown document")
    evidence_keys: set[tuple[str, str, str]] = set()
    for link in evidence_links.values():
        key = (str(link.get("target_kind")), str(link.get("target_id")), str(link.get("evidence_role")))
        _require(key not in evidence_keys, f"duplicate evidence role for {key[0]} {key[1]}")
        evidence_keys.add(key)

    approvals_by_performance: dict[str, list[dict]] = defaultdict(list)
    for approval in approvals.values():
        performance_id = approval.get("service_performance_id")
        _require(performance_id in performances, f"{approval['id']} references unknown service performance")
        approvals_by_performance[performance_id].append(approval)

    counted_ids: list[str] = []
    approval_ids: list[str] = []
    evidence_ids: list[str] = []
    ineligible: list[dict] = []
    blocked_reasons: list[str] = []
    seen_stops: set[str] = set()
    for performance_id in sorted(performances):
        performance = performances[performance_id]
        _require(performance.get("shipment_id") == shipment_id, f"{performance_id} belongs to another shipment")
        _require(performance.get("service_definition_id") == definition["id"], f"{performance_id} uses another service definition")
        stop_id = performance.get("shipment_stop_id")
        _require(stop_id in stops, f"{performance_id} references unknown shipment stop")
        _require(stop_id not in seen_stops, f"duplicate Item 28B occurrence for shipment stop {stop_id}")
        seen_stops.add(stop_id)
        _require(_decimal(performance.get("quantity"), f"{performance_id}.quantity") == Decimal("1"), f"{performance_id}.quantity must be exactly 1")
        _require(performance.get("quantity_unit") == QUANTITY_UNIT, f"{performance_id}.quantity_unit must be EA")
        performed_at = _instant(performance.get("performed_at"), f"{performance_id}.performed_at")
        status = performance.get("performance_status")
        if status not in {"COMPLETED", "NOT_PERFORMED"}:
            blocked_reasons.append(f"PERFORMANCE_STATUS_UNRESOLVED:{performance_id}")
            continue
        if status != "COMPLETED":
            ineligible.append({"service_performance_id": performance_id, "reason_code": "SERVICE_NOT_COMPLETED"})
            continue
        if not _reviewed_evidence(performance.get("evidence_link_id"), evidence_links, versions, target_kind="SERVICE_PERFORMANCE", target_id=performance_id, role="COMPLETED_EXTRA_DELIVERY"):
            blocked_reasons.append(f"PERFORMANCE_EVIDENCE_MISSING_OR_UNREVIEWED:{performance_id}")
        else:
            evidence_ids.append(performance["evidence_link_id"])
        stop = stops[stop_id]
        if stop.get("stop_role") != "EXTRA_DELIVERY" or stop["stop_sequence"] >= final_sequence:
            ineligible.append({"service_performance_id": performance_id, "reason_code": "NOT_ADDITIONAL_DELIVERY_BEFORE_FINAL"})
            continue
        related = approvals_by_performance.get(performance_id, [])
        if not related:
            blocked_reasons.append(f"APPROVAL_EVENT_MISSING:{performance_id}")
            continue
        _require(len(related) == 1, f"multiple authorization events for {performance_id}")
        approval = related[0]
        _require(approval.get("approval_event_type") in {"PREAPPROVAL", "GOVERNMENT_REQUEST"}, f"{approval['id']} has invalid approval type")
        _require(approval.get("approver_role") == "DESTINATION_PPSO", f"{approval['id']} approver role must be Destination PPSO")
        _require(_instant(approval.get("occurred_at"), f"{approval['id']}.occurred_at") <= performed_at, f"{approval['id']} occurred after performance")
        if not _reviewed_evidence(approval.get("evidence_link_id"), evidence_links, versions, target_kind="SERVICE_APPROVAL_EVENT", target_id=approval["id"], role="GOVERNMENT_AUTHORIZATION"):
            blocked_reasons.append(f"APPROVAL_EVIDENCE_MISSING_OR_UNREVIEWED:{performance_id}")
            continue
        approval_ids.append(approval["id"])
        evidence_ids.append(approval["evidence_link_id"])
        decision_status = approval.get("decision_status")
        if decision_status not in {"APPROVED", "DENIED"}:
            blocked_reasons.append(f"APPROVAL_STATUS_UNRESOLVED:{performance_id}")
        elif decision_status == "DENIED":
            ineligible.append({"service_performance_id": performance_id, "reason_code": "GOVERNMENT_APPROVAL_DENIED"})
        else:
            counted_ids.append(performance_id)

    common = {
        "case_id": case_id, "rule_package_id": RULE_PACKAGE_ID, "rule_ids": list(RULE_IDS),
        "interpretation_decision_id": INTERPRETATION_DECISION_ID,
        "source_contract": {"item_code": ITEM_CODE, "quantity_unit": QUANTITY_UNIT, "rate_date_role": "ACTUAL_PICKUP", "rate_effective_from": RATE_EFFECTIVE_FROM.isoformat(), "rate_effective_to": RATE_EFFECTIVE_TO.isoformat(), "rate_source_cell": RATE_SOURCE_CELL},
        "input_snapshot": {"shipment_id": shipment_id, "actual_pickup_date_observation_id": actual_date_record["id"], "actual_pickup_date": actual_pickup_date.isoformat(), "service_definition_id": definition["id"], "shipment_stop_ids": sorted(stops), "service_performance_ids": sorted(performances), "approval_event_ids": sorted(approval_ids), "reviewed_evidence_link_ids": sorted(set(evidence_ids))},
        "evidence": {"approval_requirement_id": APPROVAL_REQUIREMENT_ID, "performance_requirement_id": PERFORMANCE_REQUIREMENT_ID, "rate_date_requirement_id": RATE_DATE_REQUIREMENT_ID},
        "provenance": [dict(value) for value in PROVENANCE], "unresolved_assumptions": [],
    }
    if not RATE_EFFECTIVE_FROM <= actual_pickup_date <= RATE_EFFECTIVE_TO:
        blocked_reasons.append("NO_APPLICABLE_2026_ITEM_28B_RATE_VERSION")
    if blocked_reasons:
        return {**common, "status": "BLOCKED", "human_review_required": True, "blocked_reasons": sorted(set(blocked_reasons)), "eligible_occurrence_count": None}
    count = len(counted_ids)
    amount_text = f"{UNIT_RATE * count:.2f}"
    return {
        **common, "status": "FINAL", "human_review_required": False,
        "eligibility": {"eligible_occurrence_count": count, "counted_service_performance_ids": counted_ids, "ineligible_occurrences": ineligible},
        "calculation": {"operation": "MULTIPLY", "quantity": str(count), "quantity_unit": QUANTITY_UNIT, "unit_rate": f"{UNIT_RATE:.2f}", "rate_unit": "USD_per_occurrence", "unrounded_amount": amount_text, "expected_amount": amount_text, "currency": CURRENCY, "rounding": "NONE_EXACT_INTEGER_MULTIPLICATION"},
        "expected_line_action": "CREATE" if count else "OMIT",
    }

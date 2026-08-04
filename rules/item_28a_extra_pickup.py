"""Rate eligible 2026 400NG Item 28A extra-pickup occurrences."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


RULE_PACKAGE_ID = "RP-DP3-2026-ITEM-28A-1"
SOURCE_CONTRACT_RULE_ID = "RULE-ITEM-28A-SCOPED-SOURCE-CONTRACT"
ELIGIBILITY_RULE_ID = "RULE-ITEM-28A-ELIGIBLE-OCCURRENCE"
RATING_RULE_ID = "RULE-ITEM-28A-EXPECTED-CHARGE"
RULE_IDS = (SOURCE_CONTRACT_RULE_ID, ELIGIBILITY_RULE_ID, RATING_RULE_ID)
INTERPRETATION_DECISION_ID = "INT-0001"
ITEM_CODE = "28A"
QUANTITY_UNIT = "EA"
CURRENCY = "USD"
UNIT_RATE = Decimal("198.50")
RATE_EFFECTIVE_FROM = date(2026, 5, 15)
RATE_EFFECTIVE_TO = date(2027, 5, 14)
RATE_SOURCE_CELL = "Additional Rates!A13:F13"
APPROVAL_REQUIREMENT_ID = "EVID-ITEM-28A-001"
PERFORMANCE_REQUIREMENT_ID = "EVID-ITEM-28A-002"
RATE_DATE_REQUIREMENT_ID = "EVID-ITEM-28A-003"
PROVENANCE = (
    {
        "source_version_id": "SV-DP3-2026-400NG-2025-12-05",
        "source_claim_id": "CLM-0001",
        "source_locator_id": "LOC-0001",
    },
    {
        "source_version_id": "SV-DP3-2026-400NG-2025-12-05",
        "source_claim_id": "CLM-0010",
        "source_locator_id": "LOC-0010",
    },
    {
        "source_version_id": "SV-DP3-2026-400NG-2025-12-05",
        "source_claim_id": "CLM-0034",
        "source_locator_id": "LOC-0030",
    },
    {
        "source_version_id": "SV-DP3-2026-RATES-2026",
        "source_claim_id": "CLM-0035",
        "source_locator_id": "LOC-0031",
    },
    {
        "source_version_id": "SV-DP3-ITEM-CODES-2022-08-12",
        "source_claim_id": "CLM-0036",
        "source_locator_id": "LOC-0032",
    },
    {
        "source_version_id": "SV-DP3-LIBRARY-SNAPSHOT-2026-08-03",
        "source_claim_id": "CLM-0037",
        "source_locator_id": "LOC-0033",
    },
)
DECIMAL_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")
PICKUP_DELIVERY_ROLES = {"ORIGINAL_PICKUP", "EXTRA_PICKUP", "FINAL_DELIVERY", "EXTRA_DELIVERY"}
SELF_STORAGE_LOCATION_KINDS = {"SELF_STORAGE", "MINI_WAREHOUSE"}


class RuleInputError(ValueError):
    """Raised when Item 28A input is malformed or tampered."""


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


def _reviewed_evidence(
    link_id: object,
    evidence_links: dict[str, dict],
    document_versions: dict[str, dict],
    *,
    target_kind: str,
    target_id: str,
    evidence_role: str,
) -> bool:
    if not isinstance(link_id, str) or link_id not in evidence_links:
        return False
    link = evidence_links[link_id]
    return (
        link.get("document_version_id") in document_versions
        and link.get("target_kind") == target_kind
        and link.get("target_id") == target_id
        and link.get("evidence_role") == evidence_role
        and link.get("review_status") == "REVIEWED"
    )


def rate_item_28a_extra_pickups(case: dict) -> dict:
    """Return an exact expected Item 28A amount or a human-review block."""

    _require(isinstance(case, dict), "case must be an object")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id, "case_id is required")
    _require(
        case.get("data_status") in {"synthetic", "authorized_sanitized"},
        "data_status must be synthetic or authorized_sanitized",
    )
    _require(
        case.get("interpretation_decision_id") == INTERPRETATION_DECISION_ID,
        "Item 28A interpretation decision mismatch",
    )
    records = case.get("records")
    _require(isinstance(records, dict), "records must be an object")

    shipments = _index(records.get("shipments"), "shipments")
    date_observations = _index(records.get("shipment_date_observations"), "shipment_date_observations")
    locations = _index(records.get("locations"), "locations")
    stops = _index(records.get("shipment_stops"), "shipment_stops")
    definitions = _index(records.get("service_definitions"), "service_definitions")
    performances = _index(records.get("service_performances"), "service_performances")
    approvals = _index(records.get("service_approval_events"), "service_approval_events")
    evidence_links = _index(records.get("evidence_links"), "evidence_links")
    documents = _index(records.get("documents"), "documents")
    document_versions = _index(records.get("document_versions"), "document_versions")

    for version in document_versions.values():
        _require(version.get("document_id") in documents, f"{version['id']} references unknown document")
    for link in evidence_links.values():
        target_kind = link.get("target_kind")
        target_id = link.get("target_id")
        if target_kind == "SERVICE_PERFORMANCE":
            _require(target_id in performances, f"{link['id']} references unknown service performance")
        elif target_kind == "SERVICE_APPROVAL_EVENT":
            _require(target_id in approvals, f"{link['id']} references unknown service approval event")
        else:
            raise RuleInputError(f"{link['id']} has unsupported evidence target kind")

    _require(len(shipments) == 1, "exactly one shipment is required")
    shipment = next(iter(shipments.values()))
    _require(shipment.get("program_code") == "DP3" and shipment.get("domestic_indicator") is True, "shipment is outside domestic DP3 scope")
    shipment_id = shipment["id"]

    requested_dates = [
        row
        for row in date_observations.values()
        if row.get("shipment_id") == shipment_id and row.get("date_role") == "ORIGINAL_REQUESTED_PICKUP"
    ]
    _require(len(requested_dates) == 1, "exactly one original requested pickup date is required")
    requested_observation = requested_dates[0]
    requested_date = _local_date(requested_observation.get("local_date"), "original requested pickup date")

    _require(len(definitions) == 1, "exactly one Item 28A service definition is required")
    definition = next(iter(definitions.values()))
    _require(definition.get("service_code") == ITEM_CODE, "service definition code must be 28A")
    _require(definition.get("quantity_unit") == QUANTITY_UNIT, "Item 28A service definition unit must be EA")
    _require(definition.get("rate_date_role") == "ORIGINAL_REQUESTED_PICKUP", "Item 28A rate-date role mismatch")
    _require(
        definition.get("interpretation_decision_id") == INTERPRETATION_DECISION_ID,
        "service definition interpretation decision mismatch",
    )

    sequences: dict[int, str] = {}
    for stop in stops.values():
        _require(stop.get("shipment_id") == shipment_id, f"{stop['id']} belongs to another shipment")
        sequence = stop.get("stop_sequence")
        _require(isinstance(sequence, int) and sequence > 0, f"{stop['id']} stop_sequence must be a positive integer")
        _require(sequence not in sequences, f"duplicate shipment stop sequence {sequence}")
        sequences[sequence] = stop["id"]
        _require(stop.get("location_id") in locations, f"{stop['id']} references unknown location")

    original_stops = [stop for stop in stops.values() if stop.get("stop_role") == "ORIGINAL_PICKUP"]
    _require(len(original_stops) == 1, "exactly one original pickup stop is required")
    original_sequence = original_stops[0]["stop_sequence"]
    pickup_delivery_stops = [stop for stop in stops.values() if stop.get("stop_role") in PICKUP_DELIVERY_ROLES]
    self_storage_only = (
        len(pickup_delivery_stops) == 1
        and locations[pickup_delivery_stops[0]["location_id"]].get("location_kind") in SELF_STORAGE_LOCATION_KINDS
    )

    evidence_keys: set[tuple[str, str, str]] = set()
    for link in evidence_links.values():
        key = (str(link.get("target_kind")), str(link.get("target_id")), str(link.get("evidence_role")))
        _require(key not in evidence_keys, f"duplicate evidence role for {key[0]} {key[1]}")
        evidence_keys.add(key)

    performances_by_stop: dict[str, list[str]] = {}
    for performance in performances.values():
        _require(performance.get("shipment_id") == shipment_id, f"{performance['id']} belongs to another shipment")
        _require(performance.get("service_definition_id") == definition["id"], f"{performance['id']} uses another service definition")
        stop_id = performance.get("shipment_stop_id")
        _require(stop_id in stops, f"{performance['id']} references unknown shipment stop")
        performances_by_stop.setdefault(stop_id, []).append(performance["id"])
    for stop_id, performance_ids in performances_by_stop.items():
        _require(len(performance_ids) == 1, f"duplicate Item 28A occurrence for shipment stop {stop_id}")

    approvals_by_performance: dict[str, list[dict]] = {}
    for approval in approvals.values():
        performance_id = approval.get("service_performance_id")
        _require(performance_id in performances, f"{approval['id']} references unknown service performance")
        approvals_by_performance.setdefault(performance_id, []).append(approval)

    blocked_reasons: list[str] = []
    counted_ids: list[str] = []
    approval_ids: list[str] = []
    evidence_ids: list[str] = []
    ineligible: list[dict] = []

    for performance in sorted(performances.values(), key=lambda row: row["id"]):
        performance_id = performance["id"]
        quantity = _decimal(performance.get("quantity"), f"{performance_id}.quantity")
        _require(quantity == Decimal("1"), f"{performance_id}.quantity must equal one occurrence")
        _require(performance.get("quantity_unit") == QUANTITY_UNIT, f"{performance_id}.quantity_unit must be EA")
        performed_at = _instant(performance.get("performed_at"), f"{performance_id}.performed_at")
        status = performance.get("performance_status")
        _require(status in {"COMPLETED", "NOT_PERFORMED", "CANCELLED", "UNKNOWN"}, f"{performance_id} has unsupported performance_status")
        if status == "UNKNOWN":
            blocked_reasons.append(f"PERFORMANCE_STATUS_UNRESOLVED:{performance_id}")
            continue
        if status != "COMPLETED":
            ineligible.append({"service_performance_id": performance_id, "reason_code": "SERVICE_NOT_COMPLETED"})
            continue

        if not _reviewed_evidence(
            performance.get("evidence_link_id"),
            evidence_links,
            document_versions,
            target_kind="SERVICE_PERFORMANCE",
            target_id=performance_id,
            evidence_role="COMPLETED_EXTRA_PICKUP",
        ):
            blocked_reasons.append(f"PERFORMANCE_EVIDENCE_MISSING_OR_UNREVIEWED:{performance_id}")
        else:
            evidence_ids.append(performance["evidence_link_id"])

        stop = stops[performance["shipment_stop_id"]]
        if self_storage_only:
            ineligible.append({"service_performance_id": performance_id, "reason_code": "SELF_STORAGE_ONLY_EXCLUSION"})
            continue
        if stop.get("stop_role") != "EXTRA_PICKUP" or stop.get("stop_sequence") <= original_sequence:
            ineligible.append({"service_performance_id": performance_id, "reason_code": "NOT_AN_ADDITIONAL_PICKUP_AFTER_FIRST"})
            continue

        related_approvals = approvals_by_performance.get(performance_id, [])
        if not related_approvals:
            blocked_reasons.append(f"APPROVAL_EVENT_MISSING:{performance_id}")
            continue
        _require(len(related_approvals) == 1, f"multiple authorization events for {performance_id}")
        approval = related_approvals[0]
        decision_status = approval.get("decision_status")
        _require(approval.get("approval_event_type") in {"PREAPPROVAL", "GOVERNMENT_REQUEST"}, f"{approval['id']} has invalid approval type")
        _require(approval.get("approver_role") == "ORIGIN_PPSO", f"{approval['id']} approver role must be Origin PPSO")
        _require(_instant(approval.get("occurred_at"), f"{approval['id']}.occurred_at") <= performed_at, f"{approval['id']} occurred after performance")
        if not _reviewed_evidence(
            approval.get("evidence_link_id"),
            evidence_links,
            document_versions,
            target_kind="SERVICE_APPROVAL_EVENT",
            target_id=approval["id"],
            evidence_role="GOVERNMENT_AUTHORIZATION",
        ):
            blocked_reasons.append(f"APPROVAL_EVIDENCE_MISSING_OR_UNREVIEWED:{performance_id}")
            continue
        approval_ids.append(approval["id"])
        evidence_ids.append(approval["evidence_link_id"])

        if decision_status not in {"APPROVED", "DENIED"}:
            blocked_reasons.append(f"APPROVAL_STATUS_UNRESOLVED:{performance_id}")
            continue
        if decision_status == "DENIED":
            ineligible.append({"service_performance_id": performance_id, "reason_code": "GOVERNMENT_APPROVAL_DENIED"})
            continue
        counted_ids.append(performance_id)

    common = {
        "case_id": case_id,
        "rule_package_id": RULE_PACKAGE_ID,
        "rule_ids": list(RULE_IDS),
        "interpretation_decision_id": INTERPRETATION_DECISION_ID,
        "source_contract": {
            "item_code": ITEM_CODE,
            "quantity_unit": QUANTITY_UNIT,
            "rate_date_role": "ORIGINAL_REQUESTED_PICKUP",
            "rate_effective_from": RATE_EFFECTIVE_FROM.isoformat(),
            "rate_effective_to": RATE_EFFECTIVE_TO.isoformat(),
            "rate_source_cell": RATE_SOURCE_CELL,
        },
        "input_snapshot": {
            "shipment_id": shipment_id,
            "requested_pickup_date_observation_id": requested_observation["id"],
            "original_requested_pickup_date": requested_date.isoformat(),
            "service_definition_id": definition["id"],
            "shipment_stop_ids": sorted(stops),
            "service_performance_ids": sorted(performances),
            "approval_event_ids": sorted(approval_ids),
            "reviewed_evidence_link_ids": sorted(set(evidence_ids)),
        },
        "evidence": {
            "approval_requirement_id": APPROVAL_REQUIREMENT_ID,
            "performance_requirement_id": PERFORMANCE_REQUIREMENT_ID,
            "rate_date_requirement_id": RATE_DATE_REQUIREMENT_ID,
        },
        "provenance": [dict(reference) for reference in PROVENANCE],
        "unresolved_assumptions": [],
    }

    if not (RATE_EFFECTIVE_FROM <= requested_date <= RATE_EFFECTIVE_TO):
        blocked_reasons.insert(0, "NO_APPLICABLE_2026_ITEM_28A_RATE_VERSION")
    if blocked_reasons:
        return {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": sorted(set(blocked_reasons)),
            "eligible_occurrence_count": None,
        }

    count = len(counted_ids)
    amount = UNIT_RATE * count
    amount_text = f"{amount:.2f}"
    return {
        **common,
        "status": "FINAL",
        "human_review_required": False,
        "eligibility": {
            "eligible_occurrence_count": count,
            "counted_service_performance_ids": counted_ids,
            "ineligible_occurrences": ineligible,
        },
        "calculation": {
            "operation": "MULTIPLY",
            "quantity": str(count),
            "quantity_unit": QUANTITY_UNIT,
            "unit_rate": f"{UNIT_RATE:.2f}",
            "rate_unit": "USD_per_occurrence",
            "unrounded_amount": amount_text,
            "expected_amount": amount_text,
            "currency": CURRENCY,
            "rounding": "NONE_EXACT_INTEGER_MULTIPLICATION",
        },
        "expected_line_action": "CREATE" if count else "OMIT",
    }

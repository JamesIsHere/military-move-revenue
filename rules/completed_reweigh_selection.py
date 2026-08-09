"""Select the lowest current completed reweigh net under 2026 DP3 sources."""

from __future__ import annotations

import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation


RULE_PACKAGE_ID = "RP-DP3-2026-COMPLETED-REWEIGH-1"
RULE_ID = "RULE-LOWEST-CURRENT-COMPLETED-REWEIGH-NET"
PROVENANCE = (
    {
        "source_version_id": "SV-DP3-2026-400NG-2025-12-05",
        "source_claim_id": "CLM-0029",
        "source_locator_id": "LOC-0025",
    },
    {
        "source_version_id": "SV-DTR-IV-A402-2026-07-14",
        "source_claim_id": "CLM-0032",
        "source_locator_id": "LOC-0028",
    },
)
TICKET_EVIDENCE_REQUIREMENT_ID = "EVID-COMPLETED-REWEIGH-001"
DPS_EVIDENCE_REQUIREMENT_ID = "EVID-COMPLETED-REWEIGH-002"
REQUIRED_DPS_FACT_ROLES = {"GROSS", "TARE", "NET", "TICKET_NUMBER", "REWEIGH_DATE"}
DECIMAL_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")


class RuleInputError(ValueError):
    """Raised when reweigh input structure is malformed or internally tampered."""


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


def _deduplicate(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def select_lowest_current_completed_reweigh(case: dict) -> dict:
    """Return an evidence-gated lowest current completed reweigh net.

    This selector does not compare against an initial weight, choose a billed or
    controlling weight, apply a tolerance, determine a fee/refund, or rate money.
    """

    _require(isinstance(case, dict), "case must be an object")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id, "case_id is required")
    _require(
        case.get("data_status") in {"synthetic", "authorized_sanitized"},
        "data_status must be synthetic or authorized_sanitized",
    )
    records = case.get("records")
    _require(isinstance(records, dict), "records must be an object")

    events = _index(records.get("weighing_events"), "weighing_events")
    measurements = _index(records.get("weight_ticket_measurements"), "weight_ticket_measurements")
    tickets = _index(records.get("weight_tickets"), "weight_tickets")
    evidence_links = _index(records.get("evidence_links"), "evidence_links")
    updates = _index(records.get("dps_reweigh_update_events"), "dps_reweigh_update_events")
    _require(events, "at least one reweigh observation is required")

    observation_groups: dict[str, list[dict]] = defaultdict(list)
    shipment_ids: set[str] = set()
    for event in events.values():
        _require(event.get("weighing_kind") == "REWEIGH_SCALE", f"{event['id']} is not a scale reweigh")
        _require(event.get("completion_status") in {"COMPLETED", "INCOMPLETE"}, f"{event['id']} has invalid completion_status")
        observation_key = event.get("observation_key")
        _require(isinstance(observation_key, str) and observation_key, f"{event['id']} lacks observation_key")
        version = event.get("observation_version")
        _require(isinstance(version, int) and not isinstance(version, bool) and version > 0, f"{event['id']} has invalid observation_version")
        shipment_id = event.get("shipment_id")
        _require(isinstance(shipment_id, str) and shipment_id, f"{event['id']} lacks shipment_id")
        shipment_ids.add(shipment_id)
        observation_groups[observation_key].append(event)
    _require(len(shipment_ids) == 1, "reweigh observations span multiple shipments")

    superseded_event_ids: set[str] = set()
    for observation_key, group in observation_groups.items():
        versions = sorted(group, key=lambda row: row["observation_version"])
        _require(
            [row["observation_version"] for row in versions] == list(range(1, len(versions) + 1)),
            f"{observation_key} versions must be contiguous from one",
        )
        _require("supersedes_id" not in versions[0], f"{versions[0]['id']} first version cannot supersede another event")
        for previous, current in zip(versions, versions[1:]):
            _require(current.get("supersedes_id") == previous["id"], f"{current['id']} does not directly supersede {previous['id']}")
            _require(current.get("correction_reason"), f"{current['id']} correction lacks a reason")
            superseded_event_ids.add(previous["id"])

    current_events = sorted(
        (event for event in events.values() if event["id"] not in superseded_event_ids),
        key=lambda row: row["id"],
    )
    _require(len(current_events) == len(observation_groups), "each observation must have exactly one current version")

    measurements_by_event: dict[str, list[dict]] = defaultdict(list)
    for measurement in measurements.values():
        event_id = measurement.get("weighing_event_id")
        ticket_id = measurement.get("weight_ticket_id")
        _require(event_id in events, f"{measurement['id']} references unknown weighing event")
        _require(ticket_id in tickets, f"{measurement['id']} references unknown weight ticket")
        measurements_by_event[event_id].append(measurement)

    for ticket in tickets.values():
        _require(isinstance(ticket.get("document_version_id"), str) and ticket["document_version_id"], f"{ticket['id']} lacks document_version_id")

    updates_by_event: dict[str, list[dict]] = defaultdict(list)
    for update in updates.values():
        event_id = update.get("weighing_event_id")
        _require(event_id in events, f"{update['id']} references unknown weighing event")
        evidence_id = update.get("evidence_link_id")
        _require(evidence_id in evidence_links, f"{update['id']} references unknown evidence link")
        if update.get("supersedes_id") is not None:
            _require(update["supersedes_id"] in updates, f"{update['id']} supersedes unknown DPS update")
        updates_by_event[event_id].append(update)

    issues_by_event: dict[str, list[str]] = defaultdict(list)
    candidate_rows: list[dict] = []
    evidence_snapshot: list[dict] = []

    for event in current_events:
        event_id = event["id"]
        if event["completion_status"] != "COMPLETED":
            issues_by_event[event_id].append("CURRENT_REWEIGH_OBSERVATION_NOT_COMPLETED")
            continue

        event_measurements = measurements_by_event.get(event_id, [])
        roles = [measurement.get("measurement_role") for measurement in event_measurements]
        if len(event_measurements) != 3 or set(roles) != {"GROSS", "TARE", "NET"}:
            issues_by_event[event_id].append("CURRENT_REWEIGH_MEASUREMENTS_INCOMPLETE")
            continue
        by_role = {measurement["measurement_role"]: measurement for measurement in event_measurements}
        for measurement in event_measurements:
            _require(measurement.get("weight_unit") == "lb", f"{measurement['id']} weight_unit must be lb")
        gross = _decimal(by_role["GROSS"].get("weight_value"), f"{event_id}.gross")
        tare = _decimal(by_role["TARE"].get("weight_value"), f"{event_id}.tare")
        net = _decimal(by_role["NET"].get("weight_value"), f"{event_id}.net")
        if gross - tare != net or net <= 0:
            issues_by_event[event_id].append("CURRENT_REWEIGH_NET_ARITHMETIC_INVALID")

        ticket_ids = sorted({measurement["weight_ticket_id"] for measurement in event_measurements})
        ticket_document_ids = {tickets[ticket_id]["document_version_id"] for ticket_id in ticket_ids}
        reviewed_document_ids = {
            link.get("document_version_id")
            for link in evidence_links.values()
            if link.get("target_kind") == "WEIGHING_EVENT"
            and link.get("target_id") == event_id
            and link.get("evidence_role") == "REWEIGH_TICKET_TRUE_COPY"
            and link.get("review_status") == "REVIEWED"
        }
        if not ticket_document_ids.issubset(reviewed_document_ids):
            issues_by_event[event_id].append("CURRENT_REWEIGH_TICKET_EVIDENCE_MISSING_OR_UNREVIEWED")

        event_updates = updates_by_event.get(event_id, [])
        update_id = None
        if len(event_updates) != 1:
            issues_by_event[event_id].append("CURRENT_REWEIGH_DPS_UPDATE_MISSING_OR_AMBIGUOUS")
        else:
            update = event_updates[0]
            update_id = update["id"]
            evidence = evidence_links[update["evidence_link_id"]]
            if (
                update.get("update_status") != "RECORDED"
                or set(update.get("recorded_fact_roles", [])) != REQUIRED_DPS_FACT_ROLES
                or evidence.get("target_kind") != "WEIGHING_EVENT"
                or evidence.get("target_id") != event_id
            ):
                issues_by_event[event_id].append("CURRENT_REWEIGH_DPS_UPDATE_INCOMPLETE")

        candidate_rows.append(
            {
                "observation_id": event_id,
                "observation_key": event["observation_key"],
                "observation_version": event["observation_version"],
                "net_weight": _canonical_decimal(net),
                "weight_unit": "lb",
            }
        )
        evidence_snapshot.append(
            {
                "observation_id": event_id,
                "ticket_ids": ticket_ids,
                "dps_update_id": update_id,
            }
        )

    common = {
        "case_id": case_id,
        "rule_package_id": RULE_PACKAGE_ID,
        "rule_id": RULE_ID,
        "input_snapshot": {
            "shipment_id": next(iter(shipment_ids)),
            "current_observation_ids": [event["id"] for event in current_events],
            "completed_candidates": candidate_rows,
        },
        "evidence": {
            "ticket_requirement_id": TICKET_EVIDENCE_REQUIREMENT_ID,
            "dps_requirement_id": DPS_EVIDENCE_REQUIREMENT_ID,
            "observations": evidence_snapshot,
        },
        "provenance": [dict(reference) for reference in PROVENANCE],
        "unresolved_assumptions": [],
    }

    if issues_by_event:
        reason_codes = _deduplicate(
            [reason for event_id in sorted(issues_by_event) for reason in issues_by_event[event_id]]
        )
        return {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": reason_codes,
            "observation_issues": [
                {"observation_id": event_id, "reasons": issues_by_event[event_id]}
                for event_id in sorted(issues_by_event)
            ],
        }

    _require(candidate_rows, "current completed reweigh candidates unexpectedly empty")
    selected_net = min(_decimal(row["net_weight"], row["observation_id"]) for row in candidate_rows)
    selected_ids = sorted(
        row["observation_id"]
        for row in candidate_rows
        if _decimal(row["net_weight"], row["observation_id"]) == selected_net
    )
    return {
        **common,
        "status": "FINAL",
        "human_review_required": False,
        "selection": {
            "comparison_method": "LOWEST_CURRENT_COMPLETED_REWEIGH_NET",
            "selected_net_weight": _canonical_decimal(selected_net),
            "weight_unit": "lb",
            "selected_observation_ids": selected_ids,
            "candidate_count": len(candidate_rows),
        },
    }

#!/usr/bin/env python3
"""Validate synthetic logical-schema scenarios without choosing physical types."""

from __future__ import annotations

import copy
import json
import re
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "logical-schema"
DECIMAL_FIELDS = {
    "allocated_amount",
    "amount",
    "amount_variance",
    "claimed_amount",
    "claimed_total",
    "comparison_amount",
    "declared_weight",
    "determined_weight",
    "expected_amount",
    "quantity",
    "released_weight",
    "result_value",
    "variance_amount",
    "volume_value",
    "weight",
    "weight_value",
}
FORBIDDEN_KEY_FRAGMENTS = (
    "account_number",
    "address",
    "financial_account",
    "government_identifier",
    "person_name",
    "signature_image",
    "social_security",
)
DECIMAL_RE = re.compile(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?$")
MONEY_FIELDS = {
    "allocated_amount",
    "amount",
    "amount_variance",
    "claimed_amount",
    "claimed_total",
    "comparison_amount",
    "expected_amount",
    "variance_amount",
}
QUANTITY_UNIT_FIELDS = {
    "declared_weight": "declared_weight_unit",
    "determined_weight": "weight_unit",
    "quantity": "quantity_unit",
    "released_weight": "weight_unit",
    "volume_value": "volume_unit",
    "weight": "weight_unit",
    "weight_value": "weight_unit",
}
REFERENCE_TARGETS = {
    "bills_of_lading": {"shipment_id": "shipments"},
    "invoices": {"bill_of_lading_id": "bills_of_lading", "parent_invoice_id": "invoices"},
    "invoice_versions": {
        "invoice_id": "invoices",
        "supersedes_id": "invoice_versions",
        "evidence_link_id": "evidence_links",
    },
    "invoice_lines": {"invoice_id": "invoices", "parent_line_id": "invoice_lines"},
    "invoice_line_versions": {
        "invoice_line_id": "invoice_lines",
        "invoice_version_id": "invoice_versions",
        "supersedes_id": "invoice_line_versions",
        "evidence_link_id": "evidence_links",
    },
    "invoice_line_status_events": {"invoice_line_id": "invoice_lines"},
    "invoice_submissions": {"invoice_version_id": "invoice_versions"},
    "rating_runs": {"shipment_id": "shipments", "supersedes_id": "rating_runs"},
    "rule_decisions": {"rating_run_id": "rating_runs"},
    "billing_eligibility_decisions": {"rule_decision_id": "rule_decisions"},
    "charge_calculations": {"rating_run_id": "rating_runs"},
    "calculation_steps": {"charge_calculation_id": "charge_calculations"},
    "expected_charge_lines": {
        "rating_run_id": "rating_runs",
        "charge_calculation_id": "charge_calculations",
        "eligibility_decision_id": "billing_eligibility_decisions",
    },
    "reconciliation_matches": {
        "expected_charge_line_id": "expected_charge_lines",
        "invoice_line_version_id": "invoice_line_versions",
    },
    "payments": {"evidence_link_id": "evidence_links"},
    "payment_allocations": {
        "payment_id": "payments",
        "invoice_line_id": "invoice_lines",
        "supersedes_id": "payment_allocations",
        "evidence_link_id": "evidence_links",
    },
    "audit_data_completeness_assertions": {"shipment_id": "shipments"},
    "shipment_portions": {"shipment_id": "shipments", "parent_portion_id": "shipment_portions"},
    "weight_determinations": {"shipment_id": "shipments"},
    "sit_episodes": {
        "shipment_id": "shipments",
        "shipment_portion_id": "shipment_portions",
        "parent_episode_id": "sit_episodes",
    },
    "sit_charge_intervals": {
        "sit_episode_id": "sit_episodes",
        "weight_basis_decision_id": "sit_weight_basis_decisions",
    },
    "sit_weight_basis_decisions": {
        "sit_episode_id": "sit_episodes",
        "charge_interval_id": "sit_charge_intervals",
        "shipment_portion_id": "shipment_portions",
    },
    "sit_release_events": {"sit_episode_id": "sit_episodes", "released_portion_id": "shipment_portions"},
    "shipment_date_observations": {"shipment_id": "shipments"},
    "shipment_stops": {"shipment_id": "shipments", "location_id": "locations"},
    "document_versions": {"document_id": "documents", "supersedes_id": "document_versions"},
    "weighing_events": {
        "shipment_id": "shipments",
        "scale_location_id": "locations",
        "supersedes_id": "weighing_events",
    },
    "weight_tickets": {"document_version_id": "document_versions"},
    "weight_ticket_measurements": {
        "weight_ticket_id": "weight_tickets",
        "weighing_event_id": "weighing_events",
    },
    "evidence_links": {"document_version_id": "document_versions"},
    "service_performances": {
        "shipment_id": "shipments",
        "service_definition_id": "service_definitions",
        "shipment_stop_id": "shipment_stops",
        "evidence_link_id": "evidence_links",
    },
    "service_approval_events": {
        "service_performance_id": "service_performances",
        "evidence_link_id": "evidence_links",
    },
    "dps_reweigh_update_events": {
        "weighing_event_id": "weighing_events",
        "evidence_link_id": "evidence_links",
        "supersedes_id": "dps_reweigh_update_events",
    },
    "shipment_volume_observations": {
        "shipment_id": "shipments",
        "evidence_link_id": "evidence_links",
        "supersedes_id": "shipment_volume_observations",
    },
    "constructive_weight_approval_events": {
        "shipment_id": "shipments",
        "volume_observation_id": "shipment_volume_observations",
        "evidence_link_id": "evidence_links",
        "supersedes_id": "constructive_weight_approval_events",
    },
    "constructive_weight_assessments": {
        "shipment_id": "shipments",
        "volume_observation_id": "shipment_volume_observations",
        "approval_event_id": "constructive_weight_approval_events",
        "ticket_evidence_link_id": "evidence_links",
    },
    "containerized_reweigh_cases": {
        "shipment_id": "shipments",
        "original_tare_measurement_id": "weight_ticket_measurements",
        "new_gross_measurement_id": "weight_ticket_measurements",
    },
    "containerized_reweigh_completion_events": {
        "containerized_reweigh_case_id": "containerized_reweigh_cases",
        "new_tare_measurement_id": "weight_ticket_measurements",
        "evidence_link_id": "evidence_links",
        "supersedes_id": "containerized_reweigh_completion_events",
    },
    "reweigh_refund_cases": {
        "shipment_id": "shipments",
        "original_invoice_id": "invoices",
        "completed_reweigh_event_id": "weighing_events",
    },
    "reweigh_ticket_delivery_events": {
        "reweigh_refund_case_id": "reweigh_refund_cases",
        "ticket_document_version_id": "document_versions",
        "evidence_link_id": "evidence_links",
    },
    "reweigh_refund_adjustment_events": {
        "reweigh_refund_case_id": "reweigh_refund_cases",
        "supplemental_invoice_id": "invoices",
        "previous_event_id": "reweigh_refund_adjustment_events",
        "evidence_link_id": "evidence_links",
    },
    "reweigh_billing_hold_events": {
        "reweigh_refund_case_id": "reweigh_refund_cases",
        "previous_event_id": "reweigh_billing_hold_events",
        "evidence_link_id": "evidence_links",
    },
    "audit_findings": {
        "rating_run_id": "rating_runs",
        "invoice_line_id": "invoice_lines",
        "rule_decision_id": "rule_decisions",
    },
    "human_review_cases": {"audit_finding_id": "audit_findings"},
}


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def decimal(value: object, label: str) -> Decimal:
    require(isinstance(value, str), f"{label} must be a JSON string, not {type(value).__name__}")
    require(bool(DECIMAL_RE.fullmatch(value)), f"{label} is not a canonical decimal string: {value!r}")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValidationError(f"{label} is not an exact decimal: {value!r}") from exc


def records(fixture: dict, entity: str) -> list[dict]:
    value = fixture.get("records", {}).get(entity, [])
    require(isinstance(value, list), f"{entity} must be a list")
    return value


def by_id(fixture: dict, entity: str) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for record in records(fixture, entity):
        require("id" in record, f"{entity} record lacks id")
        require(record["id"] not in result, f"duplicate {entity} id {record['id']}")
        result[record["id"]] = record
    return result


def parse_instant(value: str, label: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{label} is not an ISO instant") from exc


def parse_local_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{label} is not an ISO local date") from exc


def validate_common(fixture: dict) -> None:
    require(fixture.get("data_status") == "SYNTHETIC", "fixture must be explicitly SYNTHETIC")
    require(str(fixture.get("fixture_id", "")).startswith("SYNTH-"), "fixture id must be synthetic")
    provenance = by_id({"records": {"provenance": fixture.get("provenance", [])}}, "provenance")
    require(provenance, "fixture requires provenance")

    global_ids: set[str] = set()
    for entity, entity_records in fixture.get("records", {}).items():
        for record in entity_records:
            record_id = record.get("id")
            require(record_id, f"{entity} record lacks id")
            require(record_id not in global_ids, f"record id reused across entities: {record_id}")
            global_ids.add(record_id)
            require(record.get("provenance_ref") in provenance, f"{record_id} lacks valid provenance_ref")
            for key, value in record.items():
                lower_key = key.lower()
                require(not any(fragment in lower_key for fragment in FORBIDDEN_KEY_FRAGMENTS), f"{record_id} contains forbidden sensitive field {key}")
                if key in DECIMAL_FIELDS:
                    decimal(value, f"{record_id}.{key}")
            if any(field in record for field in MONEY_FIELDS):
                require("currency" in record, f"{record_id} monetary value lacks currency")
            if "currency" in record:
                require(record["currency"] == "USD", f"{record_id} must use USD in domestic fixture")
            for quantity_field, unit_field in QUANTITY_UNIT_FIELDS.items():
                if quantity_field in record:
                    require(bool(record.get(unit_field)), f"{record_id}.{quantity_field} lacks {unit_field}")

    indexes = {entity: by_id(fixture, entity) for entity in fixture.get("records", {})}
    for entity, references in REFERENCE_TARGETS.items():
        for record in records(fixture, entity):
            for field, target_entity in references.items():
                if field in record:
                    require(record[field] in indexes.get(target_entity, {}), f"{record['id']}.{field} references missing {target_entity} record {record[field]}")

    for shipment in records(fixture, "shipments"):
        require(shipment.get("program_code") == "DP3", "fixture shipment must be DP3")
        require(shipment.get("domestic_indicator") is True, "fixture shipment must be domestic")

    validate_invoice_totals(fixture)
    validate_rule_decisions(fixture)


def validate_invoice_totals(fixture: dict) -> None:
    line_versions = records(fixture, "invoice_line_versions")
    for version in records(fixture, "invoice_versions"):
        related = [line for line in line_versions if line.get("invoice_version_id") == version["id"]]
        require(related, f"{version['id']} has no line versions")
        total = sum((decimal(line["claimed_amount"], f"{line['id']}.claimed_amount") for line in related), Decimal("0"))
        require(total == decimal(version["claimed_total"], f"{version['id']}.claimed_total"), f"{version['id']} total does not equal its line versions")


def validate_rule_decisions(fixture: dict) -> None:
    decisions = by_id(fixture, "rule_decisions")
    for decision in decisions.values():
        status = decision.get("evaluation_status")
        if status == "DECIDED":
            require("outcome_value" in decision and "outcome_type" in decision, f"{decision['id']} decided outcome is incomplete")
            require("blocked_by_conflict_id" not in decision, f"{decision['id']} cannot be decided and conflict-blocked")
        elif status in {"BLOCKED", "UNKNOWN"}:
            require("outcome_value" not in decision and "outcome_type" not in decision, f"{decision['id']} blocked/unknown outcome must be absent")
            require(decision.get("blocked_by_conflict_id") or decision.get("unresolved_assumption"), f"{decision['id']} lacks blocker")
        else:
            raise ValidationError(f"{decision['id']} has unsupported evaluation_status {status!r}")

    for eligibility in records(fixture, "billing_eligibility_decisions"):
        decision = decisions.get(eligibility.get("rule_decision_id"))
        require(decision is not None, f"{eligibility['id']} references missing rule decision")
        if decision["evaluation_status"] == "DECIDED":
            require(isinstance(eligibility.get("eligible"), bool), f"{eligibility['id']} decided eligibility needs boolean")
        else:
            require("eligible" not in eligibility, f"{eligibility['id']} blocked eligibility must remain absent")
            require(bool(eligibility.get("hold_reason")), f"{eligibility['id']} blocked eligibility needs hold_reason")


def validate_straight_through(fixture: dict) -> None:
    expected = by_id(fixture, "expected_charge_lines")
    calculations = by_id(fixture, "charge_calculations")
    steps = records(fixture, "calculation_steps")
    require(len(expected) == 1, "straight-through scenario needs one expected line")
    line = next(iter(expected.values()))
    require(line["charge_calculation_id"] in calculations, "expected line lacks calculation")
    calc_steps = sorted((step for step in steps if step["charge_calculation_id"] == line["charge_calculation_id"]), key=lambda step: step["ordinal"])
    require(calc_steps, "calculation needs steps")
    require(decimal(calc_steps[-1]["result_value"], "final calculation step") == decimal(line["expected_amount"], "expected amount"), "final calculation step differs from expected amount")
    for step in calc_steps:
        if step["operation"] == "MULTIPLY":
            operands = [decimal(value, f"{step['id']}.operand") for value in step["operand_values"]]
            require(operands[0] * operands[1] == decimal(step["result_value"], f"{step['id']}.result_value"), "multiplication step is incorrect")

    payments = by_id(fixture, "payments")
    allocations = records(fixture, "payment_allocations")
    for payment in payments.values():
        allocated = sum((decimal(row["allocated_amount"], f"{row['id']}.allocated_amount") for row in allocations if row["payment_id"] == payment["id"]), Decimal("0"))
        require(allocated == decimal(payment["amount"], f"{payment['id']}.amount"), f"{payment['id']} allocations do not balance")


def validate_split_sit(fixture: dict) -> None:
    portions = by_id(fixture, "shipment_portions")
    episodes = by_id(fixture, "sit_episodes")
    intervals = by_id(fixture, "sit_charge_intervals")
    whole = records(fixture, "weight_determinations")
    require(len(whole) == 1, "split-SIT scenario needs one whole weight")
    portion_total = sum((decimal(row["declared_weight"], f"{row['id']}.declared_weight") for row in portions.values()), Decimal("0"))
    require(portion_total == decimal(whole[0]["determined_weight"], "whole determined_weight"), "portion weights do not reconcile to whole")

    child_episodes = [episode for episode in episodes.values() if episode.get("parent_episode_id")]
    require(len(child_episodes) >= 2, "split-SIT scenario needs at least two child episodes")
    require(all(episode.get("shipment_portion_id") in portions for episode in child_episodes), "split SIT child needs a valid portion")

    releases = records(fixture, "sit_release_events")
    release_by_episode = {row["sit_episode_id"]: row for row in releases}
    for interval in intervals.values():
        episode = episodes[interval["sit_episode_id"]]
        release = release_by_episode.get(episode["id"])
        require(release is not None, f"{episode['id']} lacks release")
        require(interval["interval_end"] == release["release_date"], f"{interval['id']} extends past or stops before release")
        require(release.get("released_portion_id") == episode.get("shipment_portion_id"), f"{release['id']} releases wrong portion")

    end_dates = {interval["interval_end"] for interval in intervals.values()}
    require(len(end_dates) > 1, "split portion release must not silently close sibling intervals")


def validate_correction_history(fixture: dict) -> None:
    for entity in ("invoice_versions", "invoice_line_versions"):
        versions = sorted(records(fixture, entity), key=lambda row: row["version_number"])
        require([row["version_number"] for row in versions] == list(range(1, len(versions) + 1)), f"{entity} version numbers must be contiguous")
        for previous, current in zip(versions, versions[1:]):
            require(current.get("supersedes_id") == previous["id"], f"{current['id']} does not supersede prior immutable version")

    events = records(fixture, "invoice_line_status_events")
    require(any(parse_instant(row["recorded_at"], row["id"]) > parse_instant(row["effective_at"], row["id"]) for row in events), "correction scenario must preserve a late-recorded event")


def validate_reweigh_observation_history(fixture: dict) -> None:
    events = by_id(fixture, "weighing_events")
    tickets = by_id(fixture, "weight_tickets")
    document_versions = by_id(fixture, "document_versions")
    evidence_links = by_id(fixture, "evidence_links")
    updates = by_id(fixture, "dps_reweigh_update_events")
    required_dps_facts = {"GROSS", "TARE", "NET", "TICKET_NUMBER", "REWEIGH_DATE"}

    observation_groups: dict[str, list[dict]] = {}
    for event in events.values():
        require(event.get("weighing_kind") == "REWEIGH_SCALE", f"{event['id']} is not a scale reweigh")
        require(event.get("completion_status") == "COMPLETED", f"{event['id']} is not completed")
        observation_key = event.get("observation_key")
        require(isinstance(observation_key, str) and observation_key, f"{event['id']} lacks observation_key")
        observation_groups.setdefault(observation_key, []).append(event)

    require(len(observation_groups) >= 2, "duplicate-reweigh scenario needs at least two distinct observation keys")
    require(any(len(group) > 1 for group in observation_groups.values()), "reweigh scenario needs an immutable correction chain")

    superseded_event_ids = {event["supersedes_id"] for event in events.values() if event.get("supersedes_id")}
    current_events = [event for event in events.values() if event["id"] not in superseded_event_ids]
    require(len(current_events) == len(observation_groups), "each reweigh observation needs exactly one current version")

    updates_by_event: dict[str, list[dict]] = {}
    for update in updates.values():
        updates_by_event.setdefault(update["weighing_event_id"], []).append(update)

    measurements_by_event: dict[str, list[dict]] = {}
    for measurement in records(fixture, "weight_ticket_measurements"):
        measurements_by_event.setdefault(measurement["weighing_event_id"], []).append(measurement)

    for observation_key, group in observation_groups.items():
        versions = sorted(group, key=lambda row: row["observation_version"])
        require(
            [row["observation_version"] for row in versions] == list(range(1, len(versions) + 1)),
            f"{observation_key} versions must be contiguous from one",
        )
        require("supersedes_id" not in versions[0], f"{versions[0]['id']} first version cannot supersede another event")
        for previous, current in zip(versions, versions[1:]):
            require(current.get("supersedes_id") == previous["id"], f"{current['id']} does not directly supersede {previous['id']}")
            require(current.get("correction_reason"), f"{current['id']} correction lacks a reason")
            require(current["shipment_id"] == previous["shipment_id"], f"{current['id']} correction changed shipment")
            require(
                parse_instant(current["recorded_at"], current["id"]) > parse_instant(previous["recorded_at"], previous["id"]),
                f"{current['id']} correction was not recorded after its prior version",
            )

            current_update = updates_by_event.get(current["id"], [])
            previous_update = updates_by_event.get(previous["id"], [])
            require(len(current_update) == 1 and len(previous_update) == 1, f"{current['id']} correction needs prior and current DPS updates")
            require(current_update[0].get("supersedes_id") == previous_update[0]["id"], f"{current_update[0]['id']} does not supersede the prior DPS update")

            current_ticket_ids = {row["weight_ticket_id"] for row in measurements_by_event.get(current["id"], [])}
            previous_ticket_ids = {row["weight_ticket_id"] for row in measurements_by_event.get(previous["id"], [])}
            require(len(current_ticket_ids) == 1 and len(previous_ticket_ids) == 1, f"{current['id']} correction fixture needs one prior and one current ticket")
            current_doc = document_versions[tickets[next(iter(current_ticket_ids))]["document_version_id"]]
            previous_doc = document_versions[tickets[next(iter(previous_ticket_ids))]["document_version_id"]]
            require(current_doc.get("supersedes_id") == previous_doc["id"], f"{current_doc['id']} does not preserve ticket-version correction history")

    for event in events.values():
        event_measurements = measurements_by_event.get(event["id"], [])
        roles = {row.get("measurement_role") for row in event_measurements}
        require(len(event_measurements) == 3 and roles == {"GROSS", "TARE", "NET"}, f"{event['id']} needs exactly gross, tare, and net")
        by_role = {row["measurement_role"]: row for row in event_measurements}
        require(all(row.get("weight_unit") == "lb" for row in event_measurements), f"{event['id']} measurements must use lb")
        gross = decimal(by_role["GROSS"]["weight_value"], f"{event['id']}.gross")
        tare = decimal(by_role["TARE"]["weight_value"], f"{event['id']}.tare")
        net = decimal(by_role["NET"]["weight_value"], f"{event['id']}.net")
        require(gross - tare == net and net > 0, f"{event['id']} net must exactly equal positive gross minus tare")

        ticket_document_ids = {
            tickets[row["weight_ticket_id"]]["document_version_id"] for row in event_measurements
        }
        event_evidence = [
            link for link in evidence_links.values()
            if link.get("target_kind") == "WEIGHING_EVENT" and link.get("target_id") == event["id"]
        ]
        require(event_evidence, f"{event['id']} lacks ticket evidence")
        require(
            any(link.get("review_status") == "REVIEWED" and link.get("document_version_id") in ticket_document_ids for link in event_evidence),
            f"{event['id']} lacks reviewed evidence for its determining ticket",
        )

        event_updates = updates_by_event.get(event["id"], [])
        require(len(event_updates) == 1, f"{event['id']} needs exactly one DPS update version")
        update = event_updates[0]
        require(update.get("update_status") == "RECORDED", f"{update['id']} DPS update is not recorded")
        require(set(update.get("recorded_fact_roles", [])) == required_dps_facts, f"{update['id']} DPS fact coverage is incomplete")
        require(evidence_links[update["evidence_link_id"]].get("target_id") == event["id"], f"{update['id']} evidence targets another event")

    corrected_events = [event for event in events.values() if event.get("supersedes_id")]
    require(
        any(parse_instant(event["recorded_at"], event["id"]) > parse_instant(event["occurred_at_or_date"], event["id"]) for event in corrected_events),
        "reweigh scenario must preserve a late-recorded correction",
    )
    correction_targets = {
        row.get("aggregate_id") for row in records(fixture, "record_change_events")
        if row.get("aggregate_kind") == "WEIGHING_OBSERVATION" and row.get("change_kind") == "CORRECTION_VERSION_CREATED"
    }
    require({event["id"] for event in corrected_events}.issubset(correction_targets), "corrected reweigh lacks a record-change event")
    require(not records(fixture, "weight_determinations"), "observation-only scenario must not select a controlling weight")
    require(not records(fixture, "rule_decisions"), "observation-only scenario must not apply tolerance or fee logic")


def validate_constructive_weight_facts(fixture: dict) -> None:
    volumes = by_id(fixture, "shipment_volume_observations")
    approvals = by_id(fixture, "constructive_weight_approval_events")
    assessments = by_id(fixture, "constructive_weight_assessments")
    evidence_links = by_id(fixture, "evidence_links")
    document_versions = by_id(fixture, "document_versions")
    documents = by_id(fixture, "documents")
    require(len(volumes) == len(approvals) == len(assessments) == 1, "constructive-weight scenario needs one volume, approval, and assessment")

    provenance_claims = {
        claim_id
        for entry in fixture.get("provenance", [])
        for claim_id in entry.get("source_claim_refs", [])
    }
    require({"CLM-0025", "CLM-0033"}.issubset(provenance_claims), "constructive-weight source provenance is incomplete")

    volume = next(iter(volumes.values()))
    require(volume.get("observation_version") == 1 and "supersedes_id" not in volume, "constructive volume needs an immutable first version")
    require(volume.get("volume_unit") == "cu_ft", "constructive volume must use cu_ft")
    require(decimal(volume.get("volume_value"), f"{volume['id']}.volume_value") > 0, "constructive volume must be positive")
    require(volume.get("verification_status") == "VERIFIED", "constructive volume must be verified")

    approval = next(iter(approvals.values()))
    require(
        approval.get("eligibility_reason_code") in {"SCALES_UNAVAILABLE", "SCALE_USE_IMPRACTICAL", "WEIGHT_TICKETS_LOST"},
        "constructive-weight eligibility reason is unsupported",
    )
    require(approval.get("decision_status") == "APPROVED", "constructive-weight path lacks approval")
    require(approval.get("approver_role") == "RESPONSIBLE_PPSO", "constructive-weight approval must come from responsible PPSO")
    require(
        parse_instant(approval["recorded_at"], approval["id"]) >= parse_instant(approval["occurred_at"], approval["id"]),
        "constructive-weight approval was recorded before it occurred",
    )

    assessment = next(iter(assessments.values()))
    require(assessment.get("factor_source_claim_id") == "CLM-0025", "constructive factor lacks its source claim")
    require(assessment.get("readiness_status") == "READY_FOR_DETERMINISTIC_RULE", "constructive assessment is not ready")
    require(assessment.get("valid_ticket_status") in {"FINAL_VALID_PUBLISHED_RESULT", "NOT_AVAILABLE_DOCUMENTED"}, "constructive ticket status is unresolved")
    if assessment["valid_ticket_status"] == "FINAL_VALID_PUBLISHED_RESULT":
        require(isinstance(assessment.get("ticket_weight_result_ref"), str) and assessment["ticket_weight_result_ref"], "valid ticket status lacks published result reference")
        require("ticket_unavailability_reason" not in assessment, "valid ticket status cannot carry unavailability reason")
        require(isinstance(assessment.get("ticket_evidence_link_id"), str), "valid ticket status lacks evidence")
    else:
        require("ticket_weight_result_ref" not in assessment, "unavailable ticket cannot carry a result reference")
        require(assessment.get("ticket_unavailability_reason") == "WEIGHT_TICKETS_LOST", "ticket unavailability must be documented")

    evidence_expectations = (
        (volume, "evidence_link_id", "SHIPMENT_VOLUME_OBSERVATION", "VOLUME_WORKSHEET"),
        (approval, "evidence_link_id", "CONSTRUCTIVE_WEIGHT_APPROVAL_EVENT", "PPSO_APPROVAL_RECORD"),
    )
    for target, field, target_kind, document_type in evidence_expectations:
        link = evidence_links[target[field]]
        require(link.get("target_kind") == target_kind and link.get("target_id") == target["id"], f"{link['id']} targets the wrong constructive fact")
        require(link.get("review_status") == "REVIEWED", f"{link['id']} is not reviewed")
        document = documents[document_versions[link["document_version_id"]]["document_id"]]
        require(document.get("document_type") == document_type, f"{link['id']} uses the wrong evidence document type")

    if assessment["valid_ticket_status"] == "FINAL_VALID_PUBLISHED_RESULT":
        ticket_link = evidence_links[assessment["ticket_evidence_link_id"]]
        require(ticket_link.get("target_kind") == "CONSTRUCTIVE_WEIGHT_ASSESSMENT" and ticket_link.get("target_id") == assessment["id"], "ticket evidence targets the wrong assessment")
        require(ticket_link.get("review_status") == "REVIEWED", "ticket evidence is not reviewed")
        ticket_document = documents[document_versions[ticket_link["document_version_id"]]["document_id"]]
        require(ticket_document.get("document_type") == "WEIGHT_TICKET", "ticket evidence is not a weight ticket")

    require(not records(fixture, "shipment_article_weights"), "fact-only constructive scenario must not calculate a weight")
    require(not records(fixture, "weight_determinations"), "fact-only constructive scenario must not create a determination")
    require(not records(fixture, "rule_decisions"), "fact-only constructive scenario must not execute the 7-lb rule")


def validate_containerized_reweigh_facts(fixture: dict) -> None:
    cases = by_id(fixture, "containerized_reweigh_cases")
    completions = by_id(fixture, "containerized_reweigh_completion_events")
    measurements = by_id(fixture, "weight_ticket_measurements")
    events = by_id(fixture, "weighing_events")
    tickets = by_id(fixture, "weight_tickets")
    evidence_links = by_id(fixture, "evidence_links")
    document_versions = by_id(fixture, "document_versions")
    documents = by_id(fixture, "documents")
    require(len(cases) == len(completions) == 1, "containerized scenario needs one case and one later completion")

    provenance_claims = {
        claim_id
        for entry in fixture.get("provenance", [])
        for claim_id in entry.get("source_claim_refs", [])
    }
    provenance_conflicts = {
        conflict_id
        for entry in fixture.get("provenance", [])
        for conflict_id in entry.get("conflict_refs", [])
    }
    require({"CLM-0027", "CLM-0028"}.issubset(provenance_claims), "containerized source provenance is incomplete")
    require("CF-0004" in provenance_conflicts, "containerized tolerance conflict provenance is missing")

    case = next(iter(cases.values()))
    completion = next(iter(completions.values()))
    original_tare = measurements[case["original_tare_measurement_id"]]
    new_gross = measurements[case["new_gross_measurement_id"]]
    new_tare = measurements[completion["new_tare_measurement_id"]]
    require(original_tare.get("measurement_role") == "ORIGINAL_TARE", "containerized case lacks typed original tare")
    require(new_gross.get("measurement_role") == "NEW_GROSS", "containerized case lacks typed new gross")
    require(new_tare.get("measurement_role") == "NEW_TARE", "containerized completion lacks typed new tare")
    require(all(row.get("weight_unit") == "lb" for row in (original_tare, new_gross, new_tare)), "containerized measurements must use lb")
    original_tare_value = decimal(original_tare["weight_value"], "containerized original tare")
    new_gross_value = decimal(new_gross["weight_value"], "containerized new gross")
    new_tare_value = decimal(new_tare["weight_value"], "containerized new tare")
    require(original_tare_value > 0 and new_tare_value > 0, "containerized tare weights must be positive")
    require(new_gross_value > original_tare_value, "containerized provisional inputs would not produce a positive net")

    measurement_events = [events[row["weighing_event_id"]] for row in (original_tare, new_gross, new_tare)]
    require(all(event.get("shipment_id") == case["shipment_id"] for event in measurement_events), "containerized measurements span shipments")
    require(
        parse_instant(measurement_events[0]["occurred_at_or_date"], measurement_events[0]["id"])
        < parse_instant(measurement_events[1]["occurred_at_or_date"], measurement_events[1]["id"])
        < parse_instant(completion["occurred_at"], completion["id"]),
        "containerized original, provisional, and completion chronology is invalid",
    )
    require(
        parse_instant(completion["recorded_at"], completion["id"]) >= parse_instant(completion["occurred_at"], completion["id"]),
        "containerized completion was recorded before it occurred",
    )

    def require_ticket_evidence(measurement: dict, target_kind: str, target_id: str, evidence_role: str) -> None:
        ticket = tickets[measurement["weight_ticket_id"]]
        matching = [
            link for link in evidence_links.values()
            if link.get("target_kind") == target_kind
            and link.get("target_id") == target_id
            and link.get("evidence_role") == evidence_role
            and link.get("review_status") == "REVIEWED"
        ]
        require(len(matching) == 1, f"{target_id} lacks reviewed {evidence_role} evidence")
        link = matching[0]
        require(link.get("document_version_id") == ticket["document_version_id"], f"{link['id']} does not use the measurement ticket")
        document = documents[document_versions[link["document_version_id"]]["document_id"]]
        require(document.get("document_type") == "WEIGHT_TICKET", f"{link['id']} is not weight-ticket evidence")

    require_ticket_evidence(original_tare, "WEIGHT_TICKET_MEASUREMENT", original_tare["id"], "ORIGINAL_TARE_TRUE_COPY")
    require_ticket_evidence(new_gross, "WEIGHT_TICKET_MEASUREMENT", new_gross["id"], "NEW_GROSS_TRUE_COPY")
    require_ticket_evidence(new_tare, "CONTAINERIZED_REWEIGH_COMPLETION_EVENT", completion["id"], "NEW_TARE_TRUE_COPY")

    require(case.get("provisional_readiness_status") == "READY_FOR_DETERMINISTIC_RULE", "containerized provisional case is not ready")
    require(case.get("provisional_result_status") == "NOT_YET_EVALUATED", "fact-only containerized scenario cannot contain a provisional result")
    require(case.get("conflict_hold_ids") == ["CF-0004"], "containerized reimbursement tolerance lacks the scoped CF-0004 hold")
    require(completion.get("reimbursement_tolerance_status") == "BLOCKED_BY_CF_0004", "containerized reimbursement tolerance crossed CF-0004")

    require(not any(row.get("measurement_role") in {"PROVISIONAL_NET", "COMPLETED_NET"} for row in measurements.values()), "fact-only containerized scenario must not calculate net weight")
    require(not records(fixture, "containerized_provisional_weight_results"), "fact-only containerized scenario must not contain a provisional result")
    require(not records(fixture, "weight_determinations"), "fact-only containerized scenario must not create a weight determination")
    require(not records(fixture, "rule_decisions"), "fact-only containerized scenario must not execute a calculation")


def validate_reweigh_refund_workflow(fixture: dict) -> None:
    shipments = by_id(fixture, "shipments")
    bills = by_id(fixture, "bills_of_lading")
    invoices = by_id(fixture, "invoices")
    invoice_versions = by_id(fixture, "invoice_versions")
    invoice_lines = by_id(fixture, "invoice_lines")
    invoice_line_versions = by_id(fixture, "invoice_line_versions")
    invoice_statuses = by_id(fixture, "invoice_line_status_events")
    cases = by_id(fixture, "reweigh_refund_cases")
    events = by_id(fixture, "weighing_events")
    measurements = by_id(fixture, "weight_ticket_measurements")
    tickets = by_id(fixture, "weight_tickets")
    updates = by_id(fixture, "dps_reweigh_update_events")
    deliveries = by_id(fixture, "reweigh_ticket_delivery_events")
    adjustments = by_id(fixture, "reweigh_refund_adjustment_events")
    holds = by_id(fixture, "reweigh_billing_hold_events")
    evidence_links = by_id(fixture, "evidence_links")
    document_versions = by_id(fixture, "document_versions")
    documents = by_id(fixture, "documents")
    require(len(cases) == 1, "reweigh-refund scenario needs one workflow case")

    provenance_claims = {
        claim_id
        for entry in fixture.get("provenance", [])
        for claim_id in entry.get("source_claim_refs", [])
    }
    require(
        {"CLM-0026", "CLM-0031", "CLM-0032"}.issubset(provenance_claims),
        "reweigh-refund workflow source provenance is incomplete",
    )
    require(
        not any(entry.get("conflict_refs") for entry in fixture.get("provenance", [])),
        "fact-only reweigh-refund workflow unexpectedly depends on a conflict",
    )

    case = next(iter(cases.values()))
    original_invoice = invoices[case["original_invoice_id"]]
    original_bill = bills[original_invoice["bill_of_lading_id"]]
    require(original_bill["shipment_id"] == case["shipment_id"] in shipments, "refund case and original invoice shipments differ")
    require(original_invoice.get("invoice_kind") == "ORIGINAL", "refund case must preserve an original invoice")
    supplemental = [invoice for invoice in invoices.values() if invoice.get("parent_invoice_id") == original_invoice["id"]]
    require(len(supplemental) == 1, "refund workflow needs one separate supplemental invoice identity")
    supplemental_invoice = supplemental[0]
    require(supplemental_invoice.get("invoice_kind") == "NEGATIVE_SUPPLEMENTAL_REFUND", "supplemental invoice kind mismatch")

    original_versions = [version for version in invoice_versions.values() if version["invoice_id"] == original_invoice["id"]]
    require(len(original_versions) == 1 and original_versions[0].get("version_number") == 1, "original invoice history was rewritten")
    require(not [version for version in invoice_versions.values() if version["invoice_id"] == supplemental_invoice["id"]], "fact-only workflow cannot create a monetary supplemental version")
    original_invoice_line_ids = {line["id"] for line in invoice_lines.values() if line["invoice_id"] == original_invoice["id"]}
    require(original_invoice_line_ids, "original invoice lines are missing")
    require(not [line for line in invoice_lines.values() if line["invoice_id"] == supplemental_invoice["id"]], "fact-only workflow cannot create supplemental monetary lines")
    require(
        all(line["invoice_line_id"] in original_invoice_line_ids for line in invoice_line_versions.values()),
        "line history escaped the original invoice",
    )

    approved_statuses = [
        status for status in invoice_statuses.values()
        if status["invoice_line_id"] in original_invoice_line_ids and status.get("status_code") == "APPROVED"
    ]
    require(len(approved_statuses) == len(original_invoice_line_ids), "original invoice must be approved before the reweigh")
    approved_at = max(parse_instant(status["effective_at"], status["id"]) for status in approved_statuses)
    original_version_ids = {version["id"] for version in original_versions}
    submissions = [submission for submission in records(fixture, "invoice_submissions") if submission.get("invoice_version_id") in original_version_ids]
    require(len(submissions) == 1, "original invoice needs one immutable submission event")
    submitted_at = parse_instant(submissions[0]["submitted_at"], submissions[0]["id"])

    reweigh = events[case["completed_reweigh_event_id"]]
    require(reweigh.get("shipment_id") == case["shipment_id"], "refund case references another shipment's reweigh")
    require(reweigh.get("weighing_kind") == "REWEIGH_SCALE" and reweigh.get("completion_status") == "COMPLETED", "refund trigger is not a completed scale reweigh")
    reweigh_at = parse_instant(reweigh["occurred_at_or_date"], reweigh["id"])
    require(submitted_at < reweigh_at, "refund workflow is not post-invoice submission")
    require(approved_at < reweigh_at, "refund workflow is not post-invoice approval")
    require(case.get("trigger_timing_code") == "REWEIGH_AFTER_INITIAL_INVOICE_APPROVAL", "refund trigger timing is not explicit")
    require(isinstance(case.get("lower_weight_result_ref"), str) and case["lower_weight_result_ref"], "refund case lacks lower-weight result reference")

    reweigh_measurements = [measurement for measurement in measurements.values() if measurement["weighing_event_id"] == reweigh["id"]]
    require({measurement.get("measurement_role") for measurement in reweigh_measurements} == {"GROSS", "TARE", "NET"}, "refund reweigh needs gross, tare, and net")
    require(all(measurement.get("weight_unit") == "lb" for measurement in reweigh_measurements), "refund reweigh measurements must use lb")
    by_role = {measurement["measurement_role"]: measurement for measurement in reweigh_measurements}
    gross = decimal(by_role["GROSS"]["weight_value"], "refund reweigh gross")
    tare = decimal(by_role["TARE"]["weight_value"], "refund reweigh tare")
    net = decimal(by_role["NET"]["weight_value"], "refund reweigh net")
    require(gross - tare == net and net > 0, "refund reweigh net is not exact and positive")
    ticket_document_ids = {tickets[measurement["weight_ticket_id"]]["document_version_id"] for measurement in reweigh_measurements}
    ticket_evidence = [
        link for link in evidence_links.values()
        if link.get("target_kind") == "WEIGHING_EVENT"
        and link.get("target_id") == reweigh["id"]
        and link.get("review_status") == "REVIEWED"
        and link.get("document_version_id") in ticket_document_ids
    ]
    require(ticket_evidence, "refund reweigh lacks reviewed determining-ticket evidence")

    related_updates = [update for update in updates.values() if update["weighing_event_id"] == reweigh["id"]]
    require(len(related_updates) == 1, "refund reweigh needs one DPS update")
    update = related_updates[0]
    require(update.get("update_status") == "RECORDED", "refund DPS update is not recorded")
    require(set(update.get("recorded_fact_roles", [])) == {"GROSS", "TARE", "NET", "TICKET_NUMBER", "REWEIGH_DATE"}, "refund DPS fact coverage is incomplete")
    update_at = parse_instant(update["occurred_at"], update["id"])
    require(update_at >= reweigh_at, "DPS update predates the reweigh")
    update_evidence = evidence_links[update["evidence_link_id"]]
    require(update_evidence.get("review_status") == "REVIEWED", "DPS update evidence is not reviewed")

    require(len(deliveries) == 1, "refund workflow needs one ticket-delivery event")
    delivery = next(iter(deliveries.values()))
    require(delivery["reweigh_refund_case_id"] == case["id"], "ticket delivery references another refund case")
    require(set(delivery.get("recipient_role_codes", [])) == {"ORIGIN_PPSO", "ORDERING_PPSO"}, "ticket delivery recipient coverage is incomplete")
    require(delivery.get("timeliness_status") == "WITHIN_SEVEN_WORKING_DAYS_REVIEWED", "ticket delivery timeliness is unresolved")
    require(delivery["ticket_document_version_id"] in ticket_document_ids, "ticket delivery references a non-determining ticket")
    delivery_at = parse_instant(delivery["occurred_at"], delivery["id"])
    require(delivery_at >= update_at, "ticket delivery predates the DPS update")
    delivery_evidence = evidence_links[delivery["evidence_link_id"]]
    require(delivery_evidence.get("target_kind") == "REWEIGH_TICKET_DELIVERY_EVENT" and delivery_evidence.get("target_id") == delivery["id"], "ticket-delivery evidence targets another event")
    require(delivery_evidence.get("review_status") == "REVIEWED", "ticket-delivery evidence is not reviewed")
    delivery_document = documents[document_versions[delivery_evidence["document_version_id"]]["document_id"]]
    require(delivery_document.get("document_type") == "PPSO_TICKET_DELIVERY_RECEIPT", "ticket-delivery evidence has the wrong type")

    adjustment_order = ["REFUND_REQUIRED", "NEGATIVE_SUPPLEMENTAL_SUBMITTED", "REFUND_PROCESSED_FOR_PAYMENT"]
    ordered_adjustments = sorted(adjustments.values(), key=lambda event: parse_instant(event["occurred_at"], event["id"]))
    require([event.get("event_type") for event in ordered_adjustments] == adjustment_order, "refund adjustment history is incomplete or out of order")
    for previous, current in zip(ordered_adjustments, ordered_adjustments[1:]):
        require(current.get("previous_event_id") == previous["id"], f"{current['id']} does not preserve the adjustment chain")
    require("previous_event_id" not in ordered_adjustments[0], "first refund event cannot have a predecessor")
    require(all(event["reweigh_refund_case_id"] == case["id"] for event in ordered_adjustments), "refund events span cases")
    require(all(event.get("supplemental_invoice_id") == supplemental_invoice["id"] for event in ordered_adjustments[1:]), "submitted refund events lack the separate supplemental invoice")
    processed_event = ordered_adjustments[-1]
    processed_at = parse_instant(processed_event["occurred_at"], processed_event["id"])
    processed_evidence = evidence_links[processed_event["evidence_link_id"]]
    require(processed_evidence.get("target_id") == processed_event["id"] and processed_evidence.get("review_status") == "REVIEWED", "refund processing evidence is incomplete")

    ordered_holds = sorted(holds.values(), key=lambda event: parse_instant(event["occurred_at"], event["id"]))
    require([event.get("hold_action") for event in ordered_holds] == ["PLACED", "RELEASED"], "billing-hold history is incomplete")
    placed, released = ordered_holds
    require(released.get("previous_event_id") == placed["id"], "hold release does not preserve the placed event")
    require(all(event.get("target_service_scope") == "DESTINATION_AND_DIRECT_DELIVERY" for event in ordered_holds), "billing hold has the wrong service scope")
    require(placed.get("reason_code") == "AWAITING_REWEIGH_UPDATE_TICKETS_AND_REFUND_PROCESSING", "billing hold reason is incomplete")
    release_at = parse_instant(released["occurred_at"], released["id"])
    require(release_at >= max(update_at, delivery_at, processed_at), "billing hold released before all prerequisites")
    require(
        set(released.get("release_basis_event_ids", [])) == {update["id"], delivery["id"], processed_event["id"]},
        "billing hold release basis is incomplete",
    )

    forbidden_workflow_fields = {
        "refund_amount", "expected_amount", "variance_amount", "signed_amount",
        "tolerance_result", "reweigh_fee", "billing_item_code_version_id",
    }
    workflow_collections = (
        "reweigh_refund_cases",
        "reweigh_ticket_delivery_events",
        "reweigh_refund_adjustment_events",
        "reweigh_billing_hold_events",
    )
    for collection in workflow_collections:
        for record in records(fixture, collection):
            require(not forbidden_workflow_fields.intersection(record), f"{record['id']} contains a premature financial or tolerance result")
    require(not records(fixture, "invoice_adjustment_lines"), "fact-only refund workflow cannot create an adjustment amount")
    require(not records(fixture, "charge_calculations"), "fact-only refund workflow cannot calculate money")
    require(not records(fixture, "expected_charge_lines"), "fact-only refund workflow cannot assert expected charges")
    require(not records(fixture, "reconciliation_matches"), "fact-only refund workflow cannot assert a monetary comparison")
    require(not records(fixture, "payments"), "fact-only refund workflow cannot assert payment")
    require(not records(fixture, "rule_decisions"), "fact-only refund workflow cannot apply tolerance, fee, or financial rules")


def validate_item_28a_extra_pickup_facts(fixture: dict) -> None:
    shipments = by_id(fixture, "shipments")
    dates = records(fixture, "shipment_date_observations")
    locations = by_id(fixture, "locations")
    stops = by_id(fixture, "shipment_stops")
    definitions = by_id(fixture, "service_definitions")
    performances = by_id(fixture, "service_performances")
    approvals = records(fixture, "service_approval_events")
    evidence_links = by_id(fixture, "evidence_links")

    require(len(shipments) == 1, "Item 28A fact scenario requires one shipment")
    shipment_id = next(iter(shipments))
    requested = [
        row
        for row in dates
        if row.get("shipment_id") == shipment_id and row.get("date_role") == "ORIGINAL_REQUESTED_PICKUP"
    ]
    require(len(requested) == 1, "Item 28A requires one original requested pickup date")
    parse_local_date(requested[0].get("local_date"), requested[0]["id"])

    require(len(definitions) == 1, "Item 28A fact scenario requires one service definition")
    definition = next(iter(definitions.values()))
    require(definition.get("service_code") == "28A", "service definition is not Item 28A")
    require(definition.get("quantity_unit") == "EA", "Item 28A service definition must use EA")
    require(
        definition.get("rate_date_role") == "ORIGINAL_REQUESTED_PICKUP",
        "Item 28A rate-date role mismatch",
    )
    require(
        definition.get("interpretation_decision_id") == "INT-0001",
        "Item 28A source decision mismatch",
    )

    sequences = [stop.get("stop_sequence") for stop in stops.values()]
    require(
        all(isinstance(value, int) and value > 0 for value in sequences),
        "shipment stop sequence must be a positive integer",
    )
    require(len(sequences) == len(set(sequences)), "shipment stop sequence must be unique")
    original_stops = [stop for stop in stops.values() if stop.get("stop_role") == "ORIGINAL_PICKUP"]
    require(len(original_stops) == 1, "Item 28A facts require one original pickup stop")
    original_sequence = original_stops[0]["stop_sequence"]

    require(len(performances) == 1, "Item 28A fact scenario requires one service performance")
    performance = next(iter(performances.values()))
    require(
        performance.get("service_definition_id") == definition["id"],
        "performance uses the wrong service definition",
    )
    stop = stops[performance["shipment_stop_id"]]
    require(
        stop.get("shipment_id") == shipment_id and performance.get("shipment_id") == shipment_id,
        "Item 28A stop/performance shipment mismatch",
    )
    require(
        stop.get("stop_role") == "EXTRA_PICKUP" and stop.get("stop_sequence") > original_sequence,
        "Item 28A performance is not an additional pickup after the first",
    )
    require(
        locations[stop["location_id"]].get("location_kind") not in {"SELF_STORAGE", "MINI_WAREHOUSE"},
        "synthetic positive Item 28A fact cannot be self-storage-only",
    )
    require(performance.get("performance_status") == "COMPLETED", "Item 28A performance is not completed")
    require(
        decimal(performance.get("quantity"), f"{performance['id']}.quantity") == Decimal("1"),
        "Item 28A performance quantity must be one",
    )
    require(performance.get("quantity_unit") == "EA", "Item 28A performance unit must be EA")
    performed_at = parse_instant(performance.get("performed_at"), performance["id"])

    related_approvals = [row for row in approvals if row.get("service_performance_id") == performance["id"]]
    require(len(related_approvals) == 1, "Item 28A performance requires one approval event")
    approval = related_approvals[0]
    require(
        approval.get("approval_event_type") in {"PREAPPROVAL", "GOVERNMENT_REQUEST"},
        "Item 28A approval type is invalid",
    )
    require(approval.get("decision_status") == "APPROVED", "Item 28A approval is not approved")
    require(approval.get("approver_role") == "ORIGIN_PPSO", "Item 28A approval role must be Origin PPSO")
    require(
        parse_instant(approval.get("occurred_at"), approval["id"]) <= performed_at,
        "Item 28A approval occurred after performance",
    )

    for record, target_kind, evidence_role in (
        (approval, "SERVICE_APPROVAL_EVENT", "GOVERNMENT_AUTHORIZATION"),
        (performance, "SERVICE_PERFORMANCE", "COMPLETED_EXTRA_PICKUP"),
    ):
        link = evidence_links.get(record.get("evidence_link_id"))
        require(link is not None, f"{record['id']} lacks evidence")
        require(
            link.get("target_kind") == target_kind and link.get("target_id") == record["id"],
            f"{record['id']} evidence target mismatch",
        )
        require(
            link.get("evidence_role") == evidence_role and link.get("review_status") == "REVIEWED",
            f"{record['id']} evidence is not reviewed for the required role",
        )

    for collection in (
        "charge_calculations",
        "calculation_steps",
        "expected_charge_lines",
        "payments",
        "payment_allocations",
    ):
        require(not records(fixture, collection), f"Item 28A fact-only scenario cannot contain {collection}")


def validate_item_28b_extra_delivery_facts(fixture: dict) -> None:
    shipments = by_id(fixture, "shipments")
    dates = records(fixture, "shipment_date_observations")
    stops = by_id(fixture, "shipment_stops")
    definitions = by_id(fixture, "service_definitions")
    performances = by_id(fixture, "service_performances")
    approvals = records(fixture, "service_approval_events")
    evidence_links = by_id(fixture, "evidence_links")

    require(len(shipments) == 1, "Item 28B fact scenario requires one shipment")
    shipment = next(iter(shipments.values()))
    require(
        shipment.get("program_code") == "DP3" and shipment.get("domestic_indicator") is True,
        "Item 28B fact scenario must be domestic DP3",
    )
    actual_pickup = [
        row
        for row in dates
        if row.get("shipment_id") == shipment["id"] and row.get("date_role") == "ACTUAL_PICKUP"
    ]
    require(len(actual_pickup) == 1, "Item 28B requires one actual pickup date")
    require(
        actual_pickup[0].get("observation_kind") == "PERFORMANCE_FACT",
        "Item 28B actual pickup date must be a performance fact",
    )
    parse_local_date(actual_pickup[0].get("local_date"), actual_pickup[0]["id"])

    require(len(definitions) == 1, "Item 28B fact scenario requires one service definition")
    definition = next(iter(definitions.values()))
    require(
        definition.get("service_code") == "28B"
        and definition.get("service_family") == "EXTRA_DELIVERY_STOP_OFF"
        and definition.get("quantity_unit") == "EA",
        "Item 28B service definition mismatch",
    )
    require(definition.get("rate_date_role") == "ACTUAL_PICKUP", "Item 28B rate-date role mismatch")
    require(definition.get("interpretation_decision_id") == "INT-0002", "Item 28B source decision mismatch")

    sequences = [stop.get("stop_sequence") for stop in stops.values()]
    require(
        all(isinstance(value, int) and value > 0 for value in sequences),
        "shipment stop sequence must be a positive integer",
    )
    require(len(sequences) == len(set(sequences)), "shipment stop sequence must be unique")
    final_stops = [stop for stop in stops.values() if stop.get("stop_role") == "FINAL_DELIVERY"]
    require(len(final_stops) == 1, "Item 28B facts require one final delivery stop")
    final_sequence = final_stops[0]["stop_sequence"]

    require(len(performances) == 1, "Item 28B fact scenario requires one service performance")
    performance = next(iter(performances.values()))
    require(performance.get("service_definition_id") == definition["id"], "performance uses the wrong service definition")
    stop = stops[performance["shipment_stop_id"]]
    require(
        stop.get("shipment_id") == shipment["id"] and performance.get("shipment_id") == shipment["id"],
        "Item 28B stop/performance shipment mismatch",
    )
    require(
        stop.get("stop_role") == "EXTRA_DELIVERY" and stop.get("stop_sequence") < final_sequence,
        "Item 28B performance is not an additional delivery before final delivery",
    )
    require(performance.get("performance_status") == "COMPLETED", "Item 28B performance is not completed")
    require(
        decimal(performance.get("quantity"), f"{performance['id']}.quantity") == Decimal("1"),
        "Item 28B performance quantity must be one",
    )
    require(performance.get("quantity_unit") == "EA", "Item 28B performance unit must be EA")
    performed_at = parse_instant(performance.get("performed_at"), performance["id"])

    related_approvals = [row for row in approvals if row.get("service_performance_id") == performance["id"]]
    require(len(related_approvals) == 1, "Item 28B performance requires one approval event")
    approval = related_approvals[0]
    require(
        approval.get("approval_event_type") in {"PREAPPROVAL", "GOVERNMENT_REQUEST"},
        "Item 28B approval type is invalid",
    )
    require(approval.get("decision_status") == "APPROVED", "Item 28B approval is not approved")
    require(approval.get("approver_role") == "DESTINATION_PPSO", "Item 28B approval role must be Destination PPSO")
    require(
        parse_instant(approval.get("occurred_at"), approval["id"]) <= performed_at,
        "Item 28B approval occurred after performance",
    )

    for record, target_kind, evidence_role in (
        (approval, "SERVICE_APPROVAL_EVENT", "GOVERNMENT_AUTHORIZATION"),
        (performance, "SERVICE_PERFORMANCE", "COMPLETED_EXTRA_DELIVERY"),
    ):
        link = evidence_links.get(record.get("evidence_link_id"))
        require(link is not None, f"{record['id']} lacks evidence")
        require(
            link.get("target_kind") == target_kind and link.get("target_id") == record["id"],
            f"{record['id']} evidence target mismatch",
        )
        require(
            link.get("evidence_role") == evidence_role and link.get("review_status") == "REVIEWED",
            f"{record['id']} evidence is not reviewed for the required role",
        )

    for collection in (
        "charge_calculations",
        "calculation_steps",
        "expected_charge_lines",
        "payments",
        "payment_allocations",
    ):
        require(not records(fixture, collection), f"Item 28B fact-only scenario cannot contain {collection}")


def validate_item_invoice_payment_history(
    fixture: dict,
    *,
    shipment_id: str,
    item_code: str,
    interpretation_decision_id: str,
) -> None:
    shipments = by_id(fixture, "shipments")
    invoices = by_id(fixture, "invoices")
    invoice_versions = by_id(fixture, "invoice_versions")
    invoice_lines = by_id(fixture, "invoice_lines")
    line_versions = by_id(fixture, "invoice_line_versions")
    documents = by_id(fixture, "documents")
    document_versions = by_id(fixture, "document_versions")
    evidence_links = by_id(fixture, "evidence_links")
    payments = by_id(fixture, "payments")
    allocations = by_id(fixture, "payment_allocations")

    require(set(shipments) == {shipment_id}, f"Item {item_code} audit history requires the rating shipment identity")
    require(len(invoices) == 1 and len(invoice_lines) == 1, f"Item {item_code} audit history requires one stable invoice and line identity")

    def validate_version_chain(rows: list[dict], label: str) -> dict:
        ordered = sorted(rows, key=lambda row: row.get("version_number", 0))
        require(
            [row.get("version_number") for row in ordered] == list(range(1, len(ordered) + 1)),
            f"{label} version numbers must be contiguous",
        )
        for previous, current in zip(ordered, ordered[1:]):
            require(current.get("supersedes_id") == previous["id"], f"{current['id']} does not supersede the prior {label}")
        return ordered[-1]

    invoice = next(iter(invoices.values()))
    current_invoice_version = validate_version_chain(
        [row for row in invoice_versions.values() if row.get("invoice_id") == invoice["id"]],
        "invoice",
    )
    line = next(iter(invoice_lines.values()))
    require(line.get("invoice_id") == invoice["id"], f"Item {item_code} line belongs to another invoice")
    current_line_version = validate_version_chain(
        [row for row in line_versions.values() if row.get("invoice_line_id") == line["id"]],
        "invoice line",
    )
    require(
        current_line_version.get("invoice_version_id") == current_invoice_version["id"],
        f"current Item {item_code} line does not belong to the current invoice version",
    )
    require(current_line_version.get("billing_item_code_text") == item_code, f"current audit line must preserve raw code {item_code}")
    require(current_line_version.get("mapping_status") == "ACCEPTED", "current audit line mapping must be accepted")
    require(current_line_version.get("interpretation_decision_id") == interpretation_decision_id, "current audit line interpretation mismatch")
    require(current_line_version.get("quantity_unit") == "EA", "current audit line unit must be EA")

    invoice_document_versions = [
        row for row in document_versions.values() if documents[row["document_id"]].get("document_type") == "SYNTHETIC_INVOICE"
    ]
    validate_version_chain(invoice_document_versions, "invoice document")

    evidence_contracts = [
        *[(row, "INVOICE_VERSION", "INVOICE_VERSION_SOURCE") for row in invoice_versions.values()],
        *[(row, "INVOICE_LINE_VERSION", "INVOICE_LINE_SOURCE") for row in line_versions.values()],
        *[(row, "PAYMENT", "PAYMENT_SOURCE") for row in payments.values()],
        *[(row, "PAYMENT_ALLOCATION", "PAYMENT_ALLOCATION_SOURCE") for row in allocations.values()],
    ]
    for record, target_kind, evidence_role in evidence_contracts:
        link = evidence_links.get(record.get("evidence_link_id"))
        require(link is not None, f"{record['id']} lacks evidence")
        require(
            link.get("target_kind") == target_kind and link.get("target_id") == record["id"],
            f"{record['id']} evidence target mismatch",
        )
        require(
            link.get("evidence_role") == evidence_role and link.get("review_status") == "REVIEWED",
            f"{record['id']} evidence is not reviewed for the required role",
        )

    current_allocations = [
        row for row in allocations.values() if row["id"] not in {candidate.get("supersedes_id") for candidate in allocations.values()}
    ]
    for payment in payments.values():
        allocated = sum(
            (
                decimal(row["allocated_amount"], f"{row['id']}.allocated_amount")
                for row in current_allocations
                if row.get("payment_id") == payment["id"]
            ),
            Decimal("0"),
        )
        require(allocated == decimal(payment["amount"], f"{payment['id']}.amount"), f"{payment['id']} current allocations do not balance")

    assertions = records(fixture, "audit_data_completeness_assertions")
    require(
        {row.get("fact_scope") for row in assertions} == {"INVOICE_HISTORY", "PAYMENT_HISTORY"},
        "Item 28A audit history requires invoice and payment completeness assertions",
    )
    for assertion in assertions:
        require(assertion.get("assertion_status") == "COMPLETE", f"{assertion['id']} is not complete")
        require(assertion.get("review_status") == "REVIEWED", f"{assertion['id']} is not reviewed")
        parse_instant(assertion.get("complete_through"), assertion["id"])

    for collection in (
        "rating_runs",
        "rule_decisions",
        "charge_calculations",
        "calculation_steps",
        "expected_charge_lines",
        "reconciliation_matches",
        "audit_findings",
        "human_review_cases",
    ):
        require(not records(fixture, collection), f"Item {item_code} audit-history facts cannot contain {collection}")


def validate_item_28a_invoice_payment_history(fixture: dict) -> None:
    validate_item_invoice_payment_history(
        fixture,
        shipment_id="SHP-28A-001",
        item_code="28A",
        interpretation_decision_id="INT-0001",
    )


def validate_item_28b_invoice_payment_history(fixture: dict) -> None:
    validate_item_invoice_payment_history(
        fixture,
        shipment_id="SHP-28B-001",
        item_code="28B",
        interpretation_decision_id="INT-0002",
    )


def validate_conflict_gated(fixture: dict) -> None:
    runs = records(fixture, "rating_runs")
    require(len(runs) == 1 and runs[0].get("run_status") == "BLOCKED", "conflict scenario rating run must be BLOCKED")
    require(runs[0].get("blocked_reason") == "CF-0001", "conflict scenario must expose CF-0001")
    require(not records(fixture, "expected_charge_lines"), "blocked conflict scenario cannot assert expected charge")
    dates = {row["date_role"]: row["local_date"] for row in records(fixture, "shipment_date_observations")}
    require(dates.get("ORIGINAL_REQUESTED_PICKUP") != dates.get("ACTUAL_PICKUP"), "conflict boundary needs distinct requested and actual dates")
    line_versions = records(fixture, "invoice_line_versions")
    require(line_versions and line_versions[0].get("billing_item_code_text"), "raw billed code must be preserved")
    require("billing_item_code_version_id" not in line_versions[0], "CF-0003 scenario cannot assert authoritative code version")

    findings = by_id(fixture, "audit_findings")
    reviews = records(fixture, "human_review_cases")
    require(findings, "blocked material conflict needs an audit finding")
    require(all("expected_amount" not in row and "variance_amount" not in row for row in findings.values()), "unrated finding cannot invent expected amount or variance")
    reviewed_findings = {row["audit_finding_id"] for row in reviews}
    require(set(findings).issubset(reviewed_findings), "every blocked finding must enter human review")


VALIDATORS = {
    "straight_through": validate_straight_through,
    "split_sit": validate_split_sit,
    "correction_history": validate_correction_history,
    "reweigh_observation_history": validate_reweigh_observation_history,
    "constructive_weight_facts": validate_constructive_weight_facts,
    "containerized_reweigh_facts": validate_containerized_reweigh_facts,
    "reweigh_refund_workflow": validate_reweigh_refund_workflow,
    "item_28a_extra_pickup_facts": validate_item_28a_extra_pickup_facts,
    "item_28b_extra_delivery_facts": validate_item_28b_extra_delivery_facts,
    "item_28a_invoice_payment_history": validate_item_28a_invoice_payment_history,
    "item_28b_invoice_payment_history": validate_item_28b_invoice_payment_history,
    "conflict_gated": validate_conflict_gated,
}


def validate_fixture(fixture: dict) -> None:
    validate_common(fixture)
    scenario_type = fixture.get("scenario_type")
    require(scenario_type in VALIDATORS, f"unknown scenario_type {scenario_type!r}")
    VALIDATORS[scenario_type](fixture)


def negative_probe(fixture: dict) -> None:
    broken = copy.deepcopy(fixture)
    scenario_type = broken["scenario_type"]
    if scenario_type == "straight_through":
        broken["records"]["invoice_versions"][0]["claimed_total"] = 125.5
    elif scenario_type == "split_sit":
        broken["records"]["shipment_portions"][0]["declared_weight"] = "5999"
    elif scenario_type == "correction_history":
        del broken["records"]["invoice_versions"][1]["supersedes_id"]
    elif scenario_type == "reweigh_observation_history":
        broken["records"]["weight_ticket_measurements"] = [
            row for row in broken["records"]["weight_ticket_measurements"]
            if row["id"] != "WTM-REW-B2-NET"
        ]
    elif scenario_type == "constructive_weight_facts":
        broken["records"]["constructive_weight_approval_events"][0]["decision_status"] = "DENIED"
    elif scenario_type == "containerized_reweigh_facts":
        broken["records"]["containerized_reweigh_completion_events"][0]["reimbursement_tolerance_status"] = "EVALUATED"
    elif scenario_type == "reweigh_refund_workflow":
        broken["records"]["reweigh_billing_hold_events"][1]["occurred_at"] = "2026-06-11T12:00:00Z"
    elif scenario_type == "item_28a_extra_pickup_facts":
        broken["records"]["shipment_stops"][1]["stop_role"] = "ORIGINAL_PICKUP"
    elif scenario_type == "item_28b_extra_delivery_facts":
        broken["records"]["shipment_stops"][1]["stop_sequence"] = 4
    elif scenario_type == "item_28a_invoice_payment_history":
        del broken["records"]["invoice_line_versions"][1]["supersedes_id"]
    elif scenario_type == "item_28b_invoice_payment_history":
        broken["records"]["invoice_line_versions"][1]["interpretation_decision_id"] = "INT-0001"
    elif scenario_type == "conflict_gated":
        broken["records"]["rule_decisions"][0]["outcome_value"] = "false"
        broken["records"]["rule_decisions"][0]["outcome_type"] = "BOOLEAN"
    try:
        validate_fixture(broken)
    except ValidationError:
        return
    raise ValidationError(f"negative regression probe did not fail for {scenario_type}")


def main() -> int:
    paths = sorted(FIXTURE_DIR.glob("*.json"))
    require(paths, f"no fixtures found under {FIXTURE_DIR}")
    seen_types: set[str] = set()
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            fixture = json.load(handle, parse_float=lambda value: (_ for _ in ()).throw(ValidationError(f"JSON float forbidden in {path.name}: {value}")))
        validate_fixture(fixture)
        negative_probe(fixture)
        seen_types.add(fixture["scenario_type"])
        print(f"PASS {fixture['fixture_id']} {fixture['scenario_type']} (positive + negative probe)")
    require(seen_types == set(VALIDATORS), f"fixture set incomplete: expected {sorted(VALIDATORS)}, got {sorted(seen_types)}")
    print(f"PASS all {len(paths)} logical-schema scenarios")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValidationError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)

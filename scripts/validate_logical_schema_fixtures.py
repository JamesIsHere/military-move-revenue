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
    "measurement_value",
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
        "article_id": "shipment_articles",
        "supersedes_id": "service_performances",
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
    "shipment_articles": {
        "shipment_id": "shipments",
        "supersedes_id": "shipment_articles",
    },
    "article_measurement_observations": {
        "article_id": "shipment_articles",
        "evidence_link_id": "evidence_links",
        "supersedes_id": "article_measurement_observations",
    },
    "article_condition_observations": {
        "article_id": "shipment_articles",
        "evidence_link_id": "evidence_links",
        "supersedes_id": "article_condition_observations",
    },
    "article_service_context_observations": {
        "article_id": "shipment_articles",
        "evidence_link_id": "evidence_links",
        "supersedes_id": "article_service_context_observations",
    },
    "combined_handling_pair_candidates": {
        "article_id": "shipment_articles",
        "loading_service_performance_id": "service_performances",
        "unloading_service_performance_id": "service_performances",
        "sit_episode_id": "sit_episodes",
        "evidence_link_id": "evidence_links",
        "supersedes_id": "combined_handling_pair_candidates",
    },
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


def validate_item_130_non_monetary_facts(fixture: dict) -> None:
    articles = by_id(fixture, "shipment_articles")
    measurements = by_id(fixture, "article_measurement_observations")
    conditions = by_id(fixture, "article_condition_observations")
    contexts = by_id(fixture, "article_service_context_observations")
    performances = by_id(fixture, "service_performances")
    approvals = by_id(fixture, "service_approval_events")
    pairs = by_id(fixture, "combined_handling_pair_candidates")
    evidence = by_id(fixture, "evidence_links")
    item_130_records = [
        *articles.values(),
        *measurements.values(),
        *conditions.values(),
        *contexts.values(),
        *performances.values(),
        *approvals.values(),
        *pairs.values(),
    ]
    common_fields = {
        "recorded_at", "recorded_by", "record_source_kind", "source_version_id",
        "source_locator_id", "interpretation_status", "sensitivity_class",
        "sanitization_status",
    }
    prohibited_financial_fields = {
        "billing_item_code", "billing_item_code_text", "billable_quantity",
        "quantity", "quantity_unit", "rate", "rate_version", "amount",
        "expected_amount", "currency", "rule_package_id", "audit_adapter",
        "interpretation_decision_id",
    }
    for record in item_130_records:
        require(common_fields.issubset(record), f"{record['id']} lacks approved common metadata")
        parse_instant(record["recorded_at"], f"{record['id']}.recorded_at")
        require(record["record_source_kind"] == "SYNTHETIC_FIXTURE", f"{record['id']} source kind mismatch")
        require(record["sanitization_status"] == "SYNTHETIC", f"{record['id']} is not synthetic")
        require(record["sensitivity_class"] != "PII", f"{record['id']} cannot contain PII")
        require(record["source_version_id"] and record["source_locator_id"], f"{record['id']} lacks source provenance")
        require(not prohibited_financial_fields.intersection(record), f"{record['id']} contains prohibited financial or mapping fields")
        if "supersedes_id" in record:
            require(record["supersedes_id"] != record["id"], f"{record['id']} cannot supersede itself")
            require(bool(record.get("correction_reason")), f"{record['id']} supersession lacks correction reason")
        else:
            require("correction_reason" not in record, f"{record['id']} correction reason lacks supersession")

    def reviewed_evidence(record: dict, target_kind: str, role: str) -> None:
        link_id = record.get("evidence_link_id")
        if link_id is None:
            candidates = [
                link for link in evidence.values()
                if link.get("target_kind") == target_kind and link.get("target_id") == record["id"]
            ]
            require(len(candidates) == 1, f"{record['id']} needs one exact evidence target")
            link = candidates[0]
        else:
            link = evidence.get(link_id)
            require(link is not None, f"{record['id']} lacks evidence link")
        require(link.get("target_kind") == target_kind and link.get("target_id") == record["id"], f"{record['id']} evidence target mismatch")
        require(link.get("evidence_role") == role and link.get("review_status") == "REVIEWED", f"{record['id']} evidence role/review mismatch")

    require(len(articles) == 1, "Item 130 scenario needs one article")
    article = next(iter(articles.values()))
    require(article.get("shipment_id") == "SHP-130-001", "Item 130 article shipment mismatch")
    require(article.get("article_kind_observed") == "MOTORCYCLE", "Item 130 boundary article must be a motorcycle")
    require(article.get("tariff_classification_candidate") == "130B", "motorcycle classification candidate mismatch")
    require(article.get("classification_review_status") == "ACCEPTED", "motorcycle classification must be reviewed")
    require(article.get("associated_trailer_status") == "ABSENT", "motorcycle trailer state mismatch")
    reviewed_evidence(article, "SHIPMENT_ARTICLE", "ARTICLE_IDENTITY_AND_CLASSIFICATION_REVIEW")

    require(len(measurements) == 1, "Item 130 motorcycle needs one displacement measurement")
    measurement = next(iter(measurements.values()))
    require(measurement.get("article_id") == article["id"], "measurement article mismatch")
    require(measurement.get("measurement_kind") == "ENGINE_DISPLACEMENT", "measurement kind mismatch")
    require(decimal(measurement.get("measurement_value"), "Item 130 displacement") == Decimal("250"), "fixture must exercise exact 250cc boundary")
    require(measurement.get("measurement_unit") == "cc" and measurement.get("measurement_method") == "DOCUMENTED_SPECIFICATION", "measurement unit/method mismatch")
    require(measurement.get("review_status") == "ACCEPTED", "measurement is not reviewed")
    reviewed_evidence(measurement, "ARTICLE_MEASUREMENT_OBSERVATION", "ENGINE_DISPLACEMENT_SPECIFICATION")

    require(len(conditions) == 1, "Item 130 scenario needs one hand-carry condition")
    condition = next(iter(conditions.values()))
    require(condition.get("condition_kind") == "ONE_PERSON_HAND_CARRY" and condition.get("condition_value") == "NO", "hand-carry condition mismatch")
    reviewed_evidence(condition, "ARTICLE_CONDITION_OBSERVATION", "HANDLING_CONDITION_REVIEW")

    context_values = {row.get("context_kind"): row for row in contexts.values()}
    require(set(context_values) == {"SHIPMENT_SERVICE_CODE", "CRATING_APPROVAL", "CRATING_PERFORMANCE"}, "Item 130 service-context set mismatch")
    require(context_values["SHIPMENT_SERVICE_CODE"].get("context_value_text") == "CODE_D", "service code observation mismatch")
    require(context_values["CRATING_APPROVAL"].get("context_value_text") == "NOT_REQUESTED", "crating approval observation mismatch")
    require(context_values["CRATING_PERFORMANCE"].get("context_value_text") == "NOT_PERFORMED", "crating performance observation mismatch")
    context_roles = {
        "SHIPMENT_SERVICE_CODE": "SHIPMENT_SERVICE_CODE_OBSERVATION",
        "CRATING_APPROVAL": "CRATING_APPROVAL_OBSERVATION",
        "CRATING_PERFORMANCE": "CRATING_PERFORMANCE_OBSERVATION",
    }
    for kind, context in context_values.items():
        require(context.get("article_id") == article["id"] and context.get("context_review_status") == "ACCEPTED", f"{context['id']} context review mismatch")
        reviewed_evidence(context, "ARTICLE_SERVICE_CONTEXT_OBSERVATION", context_roles[kind])

    require(len(performances) == 3, "Item 130 scenario needs planned, loading, and unloading performances")
    by_kind = {row.get("observed_handling_kind"): row for row in performances.values()}
    require(set(by_kind) == {"HANDLING_AND_BLOCKING", "LOADING", "UNLOADING"}, "Item 130 performance-kind set mismatch")
    for performance in performances.values():
        require(performance.get("shipment_id") == "SHP-130-001" and performance.get("article_id") == article["id"], f"{performance['id']} subject mismatch")
        require(performance.get("candidate_service_family") == "ITEM_130_ARTICLE_HANDLING", f"{performance['id']} candidate family mismatch")
        require(performance.get("mapping_status") == "UNMAPPED", f"{performance['id']} must remain unmapped")
        require("service_definition_id" not in performance, f"{performance['id']} cannot assert a service definition")
    plan = by_kind["HANDLING_AND_BLOCKING"]
    loading = by_kind["LOADING"]
    unloading = by_kind["UNLOADING"]
    require(plan.get("performance_status") == "PLANNED" and "performed_at" not in plan, "planned handling performance mismatch")
    require(loading.get("performance_status") == "COMPLETED" and unloading.get("performance_status") == "COMPLETED", "loading/unloading must be completed")
    loading_at = parse_instant(loading.get("performed_at"), loading["id"])
    unloading_at = parse_instant(unloading.get("performed_at"), unloading["id"])
    require(loading_at < unloading_at, "unloading must follow loading")
    reviewed_evidence(plan, "SERVICE_PERFORMANCE", "PLANNED_ARTICLE_HANDLING")
    reviewed_evidence(loading, "SERVICE_PERFORMANCE", "COMPLETED_LOADING")
    reviewed_evidence(unloading, "SERVICE_PERFORMANCE", "COMPLETED_UNLOADING")

    require(len(approvals) == 1, "Item 130 scenario needs one preapproval event")
    approval = next(iter(approvals.values()))
    require(approval.get("service_performance_id") == plan["id"], "preapproval must target the stable planned performance")
    require(approval.get("approval_event_type") == "PREAPPROVAL" and approval.get("decision_status") == "APPROVED", "preapproval decision mismatch")
    require(approval.get("approver_role_mapping_status") == "UNMAPPED" and "approver_role" not in approval, "approver role was prematurely mapped")
    require(parse_instant(approval.get("occurred_at"), approval["id"]) < loading_at, "preapproval must precede loading")
    reviewed_evidence(approval, "SERVICE_APPROVAL_EVENT", "GOVERNMENT_PREAPPROVAL")

    require(len(pairs) == 1, "Item 130 scenario needs one handling pair candidate")
    pair = next(iter(pairs.values()))
    require(pair.get("article_id") == article["id"], "pair article mismatch")
    require(pair.get("loading_service_performance_id") == loading["id"] and pair.get("unloading_service_performance_id") == unloading["id"], "pair performance references mismatch")
    require(pair.get("pairing_status") == "ACCEPTED", "pairing needs reviewed acceptance")
    reviewed_evidence(pair, "COMBINED_HANDLING_PAIR_CANDIDATE", "HUMAN_REVIEWED_PAIRING")

    for collection in (
        "service_definitions", "rating_runs", "rule_decisions", "billing_eligibility_decisions",
        "charge_calculations", "calculation_steps", "expected_charge_lines",
        "reconciliation_matches", "invoice_lines", "invoice_line_versions", "payments",
        "payment_allocations", "audit_findings", "human_review_cases",
    ):
        require(not records(fixture, collection), f"Item 130 non-monetary fixture cannot contain {collection}")


def validate_item_130_tv_boundaries(fixture: dict) -> None:
    articles = by_id(fixture, "shipment_articles")
    measurements = by_id(fixture, "article_measurement_observations")
    conditions = by_id(fixture, "article_condition_observations")
    evidence = by_id(fixture, "evidence_links")
    require(
        set(articles) == {"ART-130G-BOUNDARY", "ART-130G-BELOW", "ART-130G-FLAT"},
        "Item 130G scenario needs boundary, below-threshold, and flat-screen articles",
    )
    require(len(measurements) == 3 and len(conditions) == 3, "each Item 130G article needs one measurement and one condition")

    common_fields = {
        "recorded_at", "recorded_by", "record_source_kind", "source_version_id",
        "source_locator_id", "interpretation_status", "sensitivity_class",
        "sanitization_status",
    }
    prohibited_fields = {
        "billing_item_code", "billing_item_code_text", "billable_quantity",
        "quantity", "quantity_unit", "rate", "rate_version", "amount",
        "expected_amount", "currency", "rule_package_id", "audit_adapter",
        "interpretation_decision_id", "service_definition_id",
    }
    for record in [*articles.values(), *measurements.values(), *conditions.values()]:
        require(common_fields.issubset(record), f"{record['id']} lacks approved common metadata")
        parse_instant(record["recorded_at"], f"{record['id']}.recorded_at")
        require(record["record_source_kind"] == "SYNTHETIC_FIXTURE", f"{record['id']} source kind mismatch")
        require(record["sanitization_status"] == "SYNTHETIC", f"{record['id']} is not synthetic")
        require(record["sensitivity_class"] != "PII", f"{record['id']} cannot contain PII")
        require(record["source_version_id"] and record["source_locator_id"], f"{record['id']} lacks source provenance")
        require(not prohibited_fields.intersection(record), f"{record['id']} contains a prohibited financial or mapping field")

    def reviewed_evidence(record: dict, target_kind: str, role: str) -> None:
        link_id = record.get("evidence_link_id")
        if link_id is None:
            candidates = [
                link for link in evidence.values()
                if link.get("target_kind") == target_kind and link.get("target_id") == record["id"]
            ]
            require(len(candidates) == 1, f"{record['id']} needs one exact evidence target")
            link = candidates[0]
        else:
            link = evidence.get(link_id)
            require(link is not None, f"{record['id']} lacks evidence link")
        require(link.get("target_kind") == target_kind and link.get("target_id") == record["id"], f"{record['id']} evidence target mismatch")
        require(link.get("evidence_role") == role and link.get("review_status") == "REVIEWED", f"{record['id']} evidence role/review mismatch")

    measurements_by_article = {row.get("article_id"): row for row in measurements.values()}
    conditions_by_article = {row.get("article_id"): row for row in conditions.values()}
    require(set(measurements_by_article) == set(articles), "Item 130G measurements do not cover each article exactly once")
    require(set(conditions_by_article) == set(articles), "Item 130G conditions do not cover each article exactly once")

    expected = {
        "ART-130G-BOUNDARY": (Decimal("48"), "NO", "130G", "ACCEPTED"),
        "ART-130G-BELOW": (Decimal("47.999"), "NO", None, "REJECTED"),
        "ART-130G-FLAT": (Decimal("48"), "YES", None, "REJECTED"),
    }
    for article_id, (screen_size, flat_screen, candidate, review_status) in expected.items():
        article = articles[article_id]
        measurement = measurements_by_article[article_id]
        condition = conditions_by_article[article_id]
        require(article.get("shipment_id") == "SHP-130G-001", f"{article_id} shipment mismatch")
        require(article.get("article_kind_observed") == "BIG_SCREEN_TV", f"{article_id} article kind mismatch")
        require(article.get("classification_review_status") == review_status, f"{article_id} classification review mismatch")
        if candidate is None:
            require("tariff_classification_candidate" not in article, f"{article_id} must not auto-classify as 130G")
        else:
            require(article.get("tariff_classification_candidate") == candidate, f"{article_id} classification candidate mismatch")
        require(measurement.get("measurement_kind") == "SCREEN_SIZE", f"{measurement['id']} measurement kind mismatch")
        require(decimal(measurement.get("measurement_value"), f"{measurement['id']}.measurement_value") == screen_size, f"{measurement['id']} screen boundary mismatch")
        require(measurement.get("measurement_unit") == "in", f"{measurement['id']} must use inches")
        require(measurement.get("measurement_method") == "DOCUMENTED_SPECIFICATION", f"{measurement['id']} measurement method mismatch")
        require(measurement.get("review_status") == "ACCEPTED", f"{measurement['id']} is not reviewed")
        require(condition.get("condition_kind") == "FLAT_SCREEN", f"{condition['id']} condition kind mismatch")
        require(condition.get("condition_value") == flat_screen, f"{condition['id']} flat-screen state mismatch")
        reviewed_evidence(article, "SHIPMENT_ARTICLE", "ARTICLE_IDENTITY_AND_CLASSIFICATION_REVIEW")
        reviewed_evidence(measurement, "ARTICLE_MEASUREMENT_OBSERVATION", "SCREEN_SIZE_SPECIFICATION")
        reviewed_evidence(condition, "ARTICLE_CONDITION_OBSERVATION", "FLAT_SCREEN_CONDITION_REVIEW")

    for collection in (
        "service_definitions", "service_performances", "service_approval_events",
        "combined_handling_pair_candidates", "rating_runs", "rule_decisions",
        "billing_eligibility_decisions", "charge_calculations", "calculation_steps",
        "expected_charge_lines", "reconciliation_matches", "invoice_lines",
        "invoice_line_versions", "payments", "payment_allocations", "audit_findings",
        "human_review_cases",
    ):
        require(not records(fixture, collection), f"Item 130G fact fixture cannot contain {collection}")


def validate_item_130_volume_assembly_boundaries(fixture: dict) -> None:
    articles = by_id(fixture, "shipment_articles")
    measurements = by_id(fixture, "article_measurement_observations")
    conditions = by_id(fixture, "article_condition_observations")
    evidence = by_id(fixture, "evidence_links")
    expected = {
        "ART-130I-OVER-ASSEMBLED": ("PLAYHOUSE", Decimal("100.001"), "YES", "130I", "ACCEPTED"),
        "ART-130I-EXACT-ASSEMBLED": ("PLAYHOUSE", Decimal("100"), "YES", None, "REJECTED"),
        "ART-130I-OVER-DISASSEMBLED": ("PLAYHOUSE", Decimal("100.001"), "NO", None, "REJECTED"),
        "ART-130J-OVER-ASSEMBLED": ("HOT_TUB", Decimal("100.001"), "YES", "130J", "ACCEPTED"),
        "ART-130J-EXACT-ASSEMBLED": ("HOT_TUB", Decimal("100"), "YES", None, "REJECTED"),
        "ART-130J-OVER-DISASSEMBLED": ("HOT_TUB", Decimal("100.001"), "NO", None, "REJECTED"),
    }
    require(set(articles) == set(expected), "Item 130I/130J scenario does not contain the six required boundary articles")
    require(len(measurements) == 6 and len(conditions) == 6, "each Item 130I/130J article needs one volume and one assembled-state observation")

    common_fields = {
        "recorded_at", "recorded_by", "record_source_kind", "source_version_id",
        "source_locator_id", "interpretation_status", "sensitivity_class",
        "sanitization_status",
    }
    prohibited_fields = {
        "billing_item_code", "billing_item_code_text", "billable_quantity",
        "quantity", "quantity_unit", "rate", "rate_version", "amount",
        "expected_amount", "currency", "rule_package_id", "audit_adapter",
        "interpretation_decision_id", "service_definition_id",
    }
    for record in [*articles.values(), *measurements.values(), *conditions.values()]:
        require(common_fields.issubset(record), f"{record['id']} lacks approved common metadata")
        parse_instant(record["recorded_at"], f"{record['id']}.recorded_at")
        require(record["record_source_kind"] == "SYNTHETIC_FIXTURE", f"{record['id']} source kind mismatch")
        require(record["sanitization_status"] == "SYNTHETIC", f"{record['id']} is not synthetic")
        require(record["sensitivity_class"] != "PII", f"{record['id']} cannot contain PII")
        require(record["source_version_id"] and record["source_locator_id"], f"{record['id']} lacks source provenance")
        require(not prohibited_fields.intersection(record), f"{record['id']} contains a prohibited financial or mapping field")

    def reviewed_evidence(record: dict, target_kind: str, role: str) -> None:
        link_id = record.get("evidence_link_id")
        if link_id is None:
            candidates = [
                link for link in evidence.values()
                if link.get("target_kind") == target_kind and link.get("target_id") == record["id"]
            ]
            require(len(candidates) == 1, f"{record['id']} needs one exact evidence target")
            link = candidates[0]
        else:
            link = evidence.get(link_id)
            require(link is not None, f"{record['id']} lacks evidence link")
        require(link.get("target_kind") == target_kind and link.get("target_id") == record["id"], f"{record['id']} evidence target mismatch")
        require(link.get("evidence_role") == role and link.get("review_status") == "REVIEWED", f"{record['id']} evidence role/review mismatch")

    measurements_by_article = {row.get("article_id"): row for row in measurements.values()}
    conditions_by_article = {row.get("article_id"): row for row in conditions.values()}
    require(set(measurements_by_article) == set(articles), "Item 130I/130J volumes do not cover each article exactly once")
    require(set(conditions_by_article) == set(articles), "Item 130I/130J assembled states do not cover each article exactly once")

    for article_id, (article_kind, volume, assembled, candidate, review_status) in expected.items():
        article = articles[article_id]
        measurement = measurements_by_article[article_id]
        condition = conditions_by_article[article_id]
        require(article.get("shipment_id") == "SHP-130IJ-001", f"{article_id} shipment mismatch")
        require(article.get("article_kind_observed") == article_kind, f"{article_id} article family mismatch")
        require(article.get("classification_review_status") == review_status, f"{article_id} classification review mismatch")
        if candidate is None:
            require("tariff_classification_candidate" not in article, f"{article_id} must not auto-classify")
        else:
            require(article.get("tariff_classification_candidate") == candidate, f"{article_id} classification candidate mismatch")
        require(measurement.get("measurement_kind") == "VOLUME", f"{measurement['id']} measurement kind mismatch")
        require(decimal(measurement.get("measurement_value"), f"{measurement['id']}.measurement_value") == volume, f"{measurement['id']} volume boundary mismatch")
        require(measurement.get("measurement_unit") == "cu_ft", f"{measurement['id']} must use cubic feet")
        require(measurement.get("measurement_method") == "PHYSICAL_DIMENSIONS", f"{measurement['id']} measurement method mismatch")
        require(measurement.get("review_status") == "ACCEPTED", f"{measurement['id']} is not reviewed")
        require(condition.get("condition_kind") == "ASSEMBLED", f"{condition['id']} condition kind mismatch")
        require(condition.get("condition_value") == assembled, f"{condition['id']} moved-assembled state mismatch")
        reviewed_evidence(article, "SHIPMENT_ARTICLE", "ARTICLE_IDENTITY_AND_CLASSIFICATION_REVIEW")
        reviewed_evidence(measurement, "ARTICLE_MEASUREMENT_OBSERVATION", "CUBIC_VOLUME_MEASUREMENT")
        reviewed_evidence(condition, "ARTICLE_CONDITION_OBSERVATION", "MOVED_ASSEMBLED_CONDITION_REVIEW")

    for collection in (
        "service_definitions", "service_performances", "service_approval_events",
        "combined_handling_pair_candidates", "rating_runs", "rule_decisions",
        "billing_eligibility_decisions", "charge_calculations", "calculation_steps",
        "expected_charge_lines", "reconciliation_matches", "invoice_lines",
        "invoice_line_versions", "payments", "payment_allocations", "audit_findings",
        "human_review_cases",
    ):
        require(not records(fixture, collection), f"Item 130I/130J fact fixture cannot contain {collection}")


def validate_item_130_boat_boundaries(fixture: dict) -> None:
    articles = by_id(fixture, "shipment_articles")
    measurements = by_id(fixture, "article_measurement_observations")
    contexts = by_id(fixture, "article_service_context_observations")
    evidence = by_id(fixture, "evidence_links")
    expected_articles = {
        "ART-130C-CANOE-ABSENT": ("CANOE", "130C", "ACCEPTED", "ABSENT"),
        "ART-130C-JETSKI-PRESENT": ("JET_SKI", "130C", "ACCEPTED", "PRESENT"),
        "ART-130C-KAYAK-UNKNOWN": ("KAYAK", "130C", "ACCEPTED", "UNKNOWN"),
        "ART-130D-FRACTION": ("BOAT_AT_MOST_14_FT", "130D", "ACCEPTED", "ABSENT"),
        "ART-130E-MANUFACTURER-HHG": ("BOAT_OVER_14_FT_WITH_HHG", "130E", "ACCEPTED", "ABSENT"),
        "ART-130D-WIDE-OTO": ("BOAT_AT_MOST_14_FT", "130D", "ACCEPTED", "ABSENT"),
        "ART-130E-DINGHY-GAP": ("DINGHY_OVER_14_FT_WITH_HHG", "130E", "ACCEPTED", "UNKNOWN"),
        "ART-130F-FRACTION": ("BOAT_TRAILER_AT_MOST_16_FT_BOTO_REFERENCE", "130F", "ACCEPTED", "PRESENT"),
        "ART-130F-SEVENTEEN": ("BOAT_TRAILER", None, "REJECTED", "PRESENT"),
    }
    require(set(articles) == set(expected_articles), "Item 130C-130F scenario article set mismatch")
    require(
        {row.get("tariff_classification_candidate") for row in articles.values() if row.get("tariff_classification_candidate")} == {"130C", "130D", "130E", "130F"},
        "Item 130C-130F direct tariff candidates are incomplete",
    )
    require(
        {row.get("associated_trailer_status") for row in articles.values()} == {"PRESENT", "ABSENT", "UNKNOWN"},
        "Item 130C-130F trailer-state coverage is incomplete",
    )

    gaps = fixture.get("unresolved_source_gaps")
    require(isinstance(gaps, list), "Item 130 boat fixture needs unresolved_source_gaps")
    gap_index = {row.get("id"): row for row in gaps}
    require(set(gap_index) == {"GAP-130E-SUBTYPE-ROWS", "GAP-130F-BOTO-BOUNDARY"}, "Item 130 boat source gaps changed")
    require(gap_index["GAP-130E-SUBTYPE-ROWS"].get("status") == "OPEN_DO_NOT_INFER_MAPPING", "130E subtype gap must remain open")
    require(gap_index["GAP-130F-BOTO-BOUNDARY"].get("status") == "OPEN_PROGRAM_BOUNDARY_REVIEW", "130F BOTO gap must remain open")
    require(all(set(row.get("provenance_refs", [])) == {"PROV-130BOAT-TARIFF", "PROV-130BOAT-ITEM-CODES"} for row in gaps), "Item 130 boat gaps need both conflicting sources")

    common_fields = {
        "recorded_at", "recorded_by", "record_source_kind", "source_version_id",
        "source_locator_id", "interpretation_status", "sensitivity_class",
        "sanitization_status",
    }
    prohibited_fields = {
        "billing_item_code", "billing_item_code_text", "billable_quantity",
        "quantity", "quantity_unit", "rate", "rate_version", "amount",
        "expected_amount", "currency", "rule_package_id", "audit_adapter",
        "interpretation_decision_id", "service_definition_id",
    }
    for record in [*articles.values(), *measurements.values(), *contexts.values()]:
        require(common_fields.issubset(record), f"{record['id']} lacks approved common metadata")
        parse_instant(record["recorded_at"], f"{record['id']}.recorded_at")
        require(record["record_source_kind"] == "SYNTHETIC_FIXTURE", f"{record['id']} source kind mismatch")
        require(record["sanitization_status"] == "SYNTHETIC", f"{record['id']} is not synthetic")
        require(record["sensitivity_class"] != "PII", f"{record['id']} cannot contain PII")
        require(record["source_version_id"] and record["source_locator_id"], f"{record['id']} lacks source provenance")
        require(not prohibited_fields.intersection(record), f"{record['id']} contains a prohibited financial or mapping field")

    def reviewed_evidence(record: dict, target_kind: str, role: str) -> None:
        link_id = record.get("evidence_link_id")
        if link_id is None:
            candidates = [
                link for link in evidence.values()
                if link.get("target_kind") == target_kind and link.get("target_id") == record["id"]
            ]
            require(len(candidates) == 1, f"{record['id']} needs one exact evidence target")
            link = candidates[0]
        else:
            link = evidence.get(link_id)
            require(link is not None, f"{record['id']} lacks evidence link")
        require(link.get("target_kind") == target_kind and link.get("target_id") == record["id"], f"{record['id']} evidence target mismatch")
        require(link.get("evidence_role") == role and link.get("review_status") == "REVIEWED", f"{record['id']} evidence role/review mismatch")

    for article_id, (kind, candidate, status, trailer_status) in expected_articles.items():
        article = articles[article_id]
        require(article.get("shipment_id") == "SHP-130BOAT-001", f"{article_id} shipment mismatch")
        require(article.get("article_kind_observed") == kind, f"{article_id} article kind mismatch")
        require(article.get("classification_review_status") == status, f"{article_id} classification review mismatch")
        require(article.get("associated_trailer_status") == trailer_status, f"{article_id} trailer state mismatch")
        if candidate is None:
            require("tariff_classification_candidate" not in article, f"{article_id} must not auto-classify")
        else:
            require(article.get("tariff_classification_candidate") == candidate, f"{article_id} classification candidate mismatch")
        reviewed_evidence(article, "SHIPMENT_ARTICLE", "ARTICLE_IDENTITY_AND_CLASSIFICATION_REVIEW")

    expected_measurements = {
        "AMO-130D-FRACTION-LENGTH": ("ART-130D-FRACTION", "LENGTH", Decimal("14.999"), "ft", "PHYSICAL_CENTER_LINE", "BOAT_CENTER_LINE_PHYSICAL_MEASUREMENT"),
        "AMO-130E-MANUFACTURER-LENGTH": ("ART-130E-MANUFACTURER-HHG", "LENGTH", Decimal("15.25"), "ft", "MANUFACTURER_LENGTH_OVERALL", "MANUFACTURER_LENGTH_OVERALL_SPECIFICATION"),
        "AMO-130D-WIDE-LENGTH": ("ART-130D-WIDE-OTO", "LENGTH", Decimal("14"), "ft", "PHYSICAL_CENTER_LINE", "BOAT_CENTER_LINE_PHYSICAL_MEASUREMENT"),
        "AMO-130D-WIDE-WIDTH": ("ART-130D-WIDE-OTO", "WIDTH", Decimal("83"), "in", "PHYSICAL_DIMENSIONS", "BOAT_WIDTH_MEASUREMENT"),
        "AMO-130D-WIDE-HEIGHT": ("ART-130D-WIDE-OTO", "HEIGHT", Decimal("77"), "in", "PHYSICAL_DIMENSIONS", "BOAT_HEIGHT_MEASUREMENT"),
        "AMO-130E-DINGHY-LENGTH": ("ART-130E-DINGHY-GAP", "LENGTH", Decimal("15"), "ft", "MANUFACTURER_CENTER_LINE", "MANUFACTURER_CENTER_LINE_SPECIFICATION"),
        "AMO-130F-FRACTION-LENGTH": ("ART-130F-FRACTION", "LENGTH", Decimal("16.999"), "ft", "PHYSICAL_DIMENSIONS", "TRAILER_LENGTH_MEASUREMENT"),
        "AMO-130F-SEVENTEEN-LENGTH": ("ART-130F-SEVENTEEN", "LENGTH", Decimal("17"), "ft", "PHYSICAL_DIMENSIONS", "TRAILER_LENGTH_MEASUREMENT"),
    }
    require(set(measurements) == set(expected_measurements), "Item 130 boat measurement set mismatch")
    for measurement_id, (article_id, kind, value, unit, method, role) in expected_measurements.items():
        measurement = measurements[measurement_id]
        require(measurement.get("article_id") == article_id, f"{measurement_id} article mismatch")
        require(measurement.get("measurement_kind") == kind, f"{measurement_id} kind mismatch")
        require(decimal(measurement.get("measurement_value"), f"{measurement_id}.measurement_value") == value, f"{measurement_id} value mismatch")
        require(measurement.get("measurement_unit") == unit, f"{measurement_id} unit mismatch")
        require(measurement.get("measurement_method") == method, f"{measurement_id} method mismatch")
        require(measurement.get("review_status") == "ACCEPTED", f"{measurement_id} is not reviewed")
        reviewed_evidence(measurement, "ARTICLE_MEASUREMENT_OBSERVATION", role)

    require(int(decimal(measurements["AMO-130D-FRACTION-LENGTH"]["measurement_value"], "130D fractional length")) == 14, "130D fractional feet were not disregarded")
    require(int(decimal(measurements["AMO-130E-MANUFACTURER-LENGTH"]["measurement_value"], "130E manufacturer length")) == 15, "130E manufacturer length boundary mismatch")
    require(int(decimal(measurements["AMO-130F-FRACTION-LENGTH"]["measurement_value"], "130F fractional length")) == 16, "130F fractional feet were not disregarded")
    require(decimal(measurements["AMO-130D-WIDE-WIDTH"]["measurement_value"], "boat width") > Decimal("82"), "separate OTO width boundary is not exercised")
    require(decimal(measurements["AMO-130D-WIDE-HEIGHT"]["measurement_value"], "boat height") == Decimal("77"), "boat height boundary mismatch")

    expected_contexts = {
        "ASC-130E-MANUFACTURER-HHG": ("ART-130E-MANUFACTURER-HHG", "HHG_CO_MOVE_AGREEMENT", "AGREED", "ACCEPTED", "HHG_CO_MOVE_AGREEMENT_REVIEW"),
        "ASC-130D-WIDE-OTO": ("ART-130D-WIDE-OTO", "BOTO_PROGRAM", "SEPARATE_DOMESTIC_OTO_REQUIRED", "ACCEPTED", "BOTO_PROGRAM_CONTEXT_REVIEW"),
        "ASC-130E-DINGHY-HHG": ("ART-130E-DINGHY-GAP", "HHG_CO_MOVE_AGREEMENT", "AGREED", "ACCEPTED", "HHG_CO_MOVE_AGREEMENT_REVIEW"),
        "ASC-130F-BOTO-CONFLICT": ("ART-130F-FRACTION", "BOTO_PROGRAM", "BOTO_SCOPE_REVIEW_REQUIRED", "CONFLICTING", "BOTO_PROGRAM_CONTEXT_REVIEW"),
    }
    require(set(contexts) == set(expected_contexts), "Item 130 boat program-context set mismatch")
    for context_id, (article_id, kind, value, status, role) in expected_contexts.items():
        context = contexts[context_id]
        require(context.get("article_id") == article_id, f"{context_id} article mismatch")
        require(context.get("context_kind") == kind and context.get("context_value_text") == value, f"{context_id} value mismatch")
        require(context.get("context_review_status") == status, f"{context_id} review status mismatch")
        reviewed_evidence(context, "ARTICLE_SERVICE_CONTEXT_OBSERVATION", role)

    require("GAP_130E_SUBTYPE_ROWS_OPEN" in articles["ART-130E-DINGHY-GAP"].get("interpretation_status", ""), "130E subtype mapping gap is not exposed")
    require("GAP_130F_BOTO_BOUNDARY_OPEN" in articles["ART-130F-FRACTION"].get("interpretation_status", ""), "130F BOTO gap is not exposed")
    require("GAP_130F_BOTO_BOUNDARY" in contexts["ASC-130F-BOTO-CONFLICT"].get("interpretation_status", ""), "130F program context is not held for review")

    for collection in (
        "service_definitions", "service_performances", "service_approval_events",
        "combined_handling_pair_candidates", "rating_runs", "rule_decisions",
        "billing_eligibility_decisions", "charge_calculations", "calculation_steps",
        "expected_charge_lines", "reconciliation_matches", "invoice_lines",
        "invoice_line_versions", "payments", "payment_allocations", "audit_findings",
        "human_review_cases",
    ):
        require(not records(fixture, collection), f"Item 130 boat fact fixture cannot contain {collection}")


def validate_item_130_handling_sit_pairing_boundaries(fixture: dict) -> None:
    articles = by_id(fixture, "shipment_articles")
    performances = by_id(fixture, "service_performances")
    pairs = by_id(fixture, "combined_handling_pair_candidates")
    sit_episodes = by_id(fixture, "sit_episodes")
    evidence = by_id(fixture, "evidence_links")

    expected_articles = {
        "ART-130PAIR-ZERO",
        "ART-130PAIR-ONE",
        "ART-130PAIR-MULTI",
        "ART-130PAIR-UNMATCHED-LOAD",
        "ART-130PAIR-UNMATCHED-UNLOAD",
        "ART-130PAIR-DUP",
        "ART-130PAIR-SIT-TSP",
        "ART-130PAIR-SIT-NONTSP",
        "ART-130PAIR-SIT-UNKNOWN",
    }
    require(set(articles) == expected_articles, "Item 130 handling/SIT article set mismatch")
    require(
        set(sit_episodes) == {"SIT-130PAIR-TSP", "SIT-130PAIR-NONTSP", "SIT-130PAIR-UNKNOWN"},
        "Item 130 handling/SIT episode set mismatch",
    )

    common_fields = {
        "recorded_at", "recorded_by", "record_source_kind", "source_version_id",
        "source_locator_id", "interpretation_status", "sensitivity_class",
        "sanitization_status",
    }
    prohibited_fields = {
        "billing_item_code", "billing_item_code_text", "billable_quantity",
        "quantity", "quantity_unit", "rate", "rate_version", "amount",
        "expected_amount", "currency", "rule_package_id", "audit_adapter",
        "interpretation_decision_id", "service_definition_id",
        "financial_eligibility", "billing_item_mapping_id",
    }
    for collection_rows in fixture.get("records", {}).values():
        for record in collection_rows:
            require(
                not prohibited_fields.intersection(record),
                f"{record['id']} contains a prohibited Item 130 financial or mapping field",
            )
    for record in [*articles.values(), *performances.values(), *pairs.values()]:
        require(common_fields.issubset(record), f"{record['id']} lacks approved common metadata")
        parse_instant(record["recorded_at"], f"{record['id']}.recorded_at")
        require(record["record_source_kind"] == "SYNTHETIC_FIXTURE", f"{record['id']} source kind mismatch")
        require(record["sanitization_status"] == "SYNTHETIC", f"{record['id']} is not synthetic")
        require(record["sensitivity_class"] != "PII", f"{record['id']} cannot contain PII")
        require(record["source_version_id"] and record["source_locator_id"], f"{record['id']} lacks source provenance")

    require(set(fixture.get("open_conflict_ids", [])) == {"CF-0001", "CF-0003"}, "Item 130 handling/SIT conflicts must remain open")
    gaps = {row.get("id"): row for row in fixture.get("unresolved_source_gaps", [])}
    require(set(gaps) == {"GAP-130-COMBINED-VS-OD"}, "combined-service source gap must remain explicit")
    gap = gaps["GAP-130-COMBINED-VS-OD"]
    require(gap.get("status") == "OPEN_DO_NOT_DERIVE_QUANTITY_OR_MATCHING", "combined-service source gap was weakened")
    require(
        set(gap.get("provenance_refs", [])) == {"PROV-130PAIR-TARIFF", "PROV-130PAIR-ITEM-CODES"},
        "combined-service source gap provenance mismatch",
    )

    def exact_evidence(target_kind: str, target_id: str, role: str) -> None:
        candidates = [
            row for row in evidence.values()
            if row.get("target_kind") == target_kind
            and row.get("target_id") == target_id
            and row.get("evidence_role") == role
        ]
        require(len(candidates) == 1, f"{target_id} needs one exact {role} evidence target")
        require(candidates[0].get("review_status") == "REVIEWED", f"{target_id} {role} evidence is not reviewed")

    for article in articles.values():
        require(article.get("shipment_id") == "SHP-130PAIR-001", f"{article['id']} shipment mismatch")
        require(article.get("article_kind_observed") == "WINDSURFER", f"{article['id']} article kind mismatch")
        require(article.get("tariff_classification_candidate") == "130C", f"{article['id']} classification mismatch")
        require(article.get("classification_review_status") == "ACCEPTED", f"{article['id']} is not reviewed")
        require(article.get("associated_trailer_status") == "ABSENT", f"{article['id']} trailer state mismatch")
        exact_evidence("SHIPMENT_ARTICLE", article["id"], "ARTICLE_IDENTITY_AND_CLASSIFICATION_REVIEW")
        exact_evidence("SHIPMENT_ARTICLE", article["id"], "HANDLING_PAIRING_COVERAGE_REVIEW")

    for sit_episode in sit_episodes.values():
        require(sit_episode.get("shipment_id") == "SHP-130PAIR-001", f"{sit_episode['id']} shipment mismatch")
        require(sit_episode.get("sit_kind") == "DESTINATION", f"{sit_episode['id']} kind mismatch")
        require(sit_episode.get("episode_status") == "CLOSED", f"{sit_episode['id']} status mismatch")

    for performance in performances.values():
        require(performance.get("shipment_id") == "SHP-130PAIR-001", f"{performance['id']} shipment mismatch")
        require(performance.get("article_id") in articles, f"{performance['id']} article mismatch")
        require(performance.get("candidate_service_family") == "ITEM_130_ARTICLE_HANDLING", f"{performance['id']} family mismatch")
        require(performance.get("mapping_status") == "UNMAPPED", f"{performance['id']} must remain unmapped")
        require(performance.get("performance_status") == "COMPLETED", f"{performance['id']} must be completed")
        kind = performance.get("observed_handling_kind")
        require(kind in {"LOADING", "UNLOADING"}, f"{performance['id']} handling kind mismatch")
        parse_instant(performance.get("performed_at"), f"{performance['id']}.performed_at")
        sit_episode_id = performance.get("sit_episode_id")
        if sit_episode_id is None:
            require("tsp_convenience_status" not in performance, f"{performance['id']} has SIT cause without SIT")
            role = "COMPLETED_LOADING" if kind == "LOADING" else "COMPLETED_UNLOADING"
        else:
            require(sit_episode_id in sit_episodes, f"{performance['id']} SIT episode mismatch")
            require(
                performance.get("tsp_convenience_status") in {"TSP_CONVENIENCE", "NOT_TSP_CONVENIENCE", "UNKNOWN"},
                f"{performance['id']} SIT cause mismatch",
            )
            role = f"COMPLETED_{kind}_WITH_SIT_CAUSE_REVIEW"
        exact_evidence("SERVICE_PERFORMANCE", performance["id"], role)

    accepted_reference_pairs: set[tuple[str, str]] = set()
    for pair in pairs.values():
        loading = performances.get(pair.get("loading_service_performance_id"))
        unloading = performances.get(pair.get("unloading_service_performance_id"))
        require(loading is not None and unloading is not None, f"{pair['id']} performance reference mismatch")
        require(loading.get("observed_handling_kind") == "LOADING", f"{pair['id']} loading reference kind mismatch")
        require(unloading.get("observed_handling_kind") == "UNLOADING", f"{pair['id']} unloading reference kind mismatch")
        require(
            pair.get("article_id") == loading.get("article_id") == unloading.get("article_id"),
            f"{pair['id']} does not preserve one article identity",
        )
        require(
            parse_instant(loading["performed_at"], loading["id"])
            < parse_instant(unloading["performed_at"], unloading["id"]),
            f"{pair['id']} chronology mismatch",
        )
        require(pair.get("pairing_status") in {"ACCEPTED", "CONFLICTING"}, f"{pair['id']} pairing status mismatch")
        require("not billable quantity" in pair.get("pairing_basis", ""), f"{pair['id']} explanation lost no-quantity boundary")
        sit_episode_id = pair.get("sit_episode_id")
        if sit_episode_id is None:
            require("sit_episode_id" not in loading and "sit_episode_id" not in unloading, f"{pair['id']} dropped SIT linkage")
        else:
            require(sit_episode_id in sit_episodes, f"{pair['id']} SIT episode is unknown")
            require(
                loading.get("sit_episode_id") == sit_episode_id == unloading.get("sit_episode_id"),
                f"{pair['id']} SIT linkage mismatch",
            )
        if pair["id"].startswith("PAIR-130PAIR-DUP-"):
            role = "HUMAN_REVIEWED_DUPLICATE_PAIRING_CONFLICT"
        elif sit_episode_id is not None:
            role = "HUMAN_REVIEWED_SIT_PAIRING"
        else:
            role = "HUMAN_REVIEWED_PAIRING"
        exact_evidence("COMBINED_HANDLING_PAIR_CANDIDATE", pair["id"], role)
        if pair.get("pairing_status") == "ACCEPTED":
            references = (loading["id"], unloading["id"])
            require(references not in accepted_reference_pairs, f"{pair['id']} duplicates an accepted pair")
            accepted_reference_pairs.add(references)

    def article_rows(article_id: str) -> tuple[list[dict], list[dict]]:
        return (
            [row for row in performances.values() if row.get("article_id") == article_id],
            [row for row in pairs.values() if row.get("article_id") == article_id],
        )

    zero_performances, zero_pairs = article_rows("ART-130PAIR-ZERO")
    require(not zero_performances and not zero_pairs, "zero-pair case must preserve reviewed absence")

    one_performances, one_pairs = article_rows("ART-130PAIR-ONE")
    require(len(one_performances) == 2 and len(one_pairs) == 1, "one-pair case cardinality mismatch")
    require(one_pairs[0].get("pairing_status") == "ACCEPTED", "one-pair case is not accepted")

    multi_performances, multi_pairs = article_rows("ART-130PAIR-MULTI")
    require(len(multi_performances) == 4 and len(multi_pairs) == 2, "multiple-pair case cardinality mismatch")
    require(all(row.get("pairing_status") == "ACCEPTED" for row in multi_pairs), "multiple-pair case is not accepted")
    require(
        len({(row["loading_service_performance_id"], row["unloading_service_performance_id"]) for row in multi_pairs}) == 2,
        "multiple-pair case collapsed distinct references",
    )

    unmatched_load_performances, unmatched_load_pairs = article_rows("ART-130PAIR-UNMATCHED-LOAD")
    require(
        len(unmatched_load_performances) == 1
        and unmatched_load_performances[0].get("observed_handling_kind") == "LOADING"
        and not unmatched_load_pairs,
        "unmatched-loading case mismatch",
    )
    unmatched_unload_performances, unmatched_unload_pairs = article_rows("ART-130PAIR-UNMATCHED-UNLOAD")
    require(
        len(unmatched_unload_performances) == 1
        and unmatched_unload_performances[0].get("observed_handling_kind") == "UNLOADING"
        and not unmatched_unload_pairs,
        "unmatched-unloading case mismatch",
    )

    duplicate_performances, duplicate_pairs = article_rows("ART-130PAIR-DUP")
    require(len(duplicate_performances) == 2 and len(duplicate_pairs) == 2, "duplicate-pair case cardinality mismatch")
    require(all(row.get("pairing_status") == "CONFLICTING" for row in duplicate_pairs), "duplicate pairs must remain conflicting")
    require(
        len({(row["loading_service_performance_id"], row["unloading_service_performance_id"]) for row in duplicate_pairs}) == 1,
        "duplicate-pair case no longer contains repeated references",
    )

    sit_cases = {
        "ART-130PAIR-SIT-TSP": ("SIT-130PAIR-TSP", "TSP_CONVENIENCE"),
        "ART-130PAIR-SIT-NONTSP": ("SIT-130PAIR-NONTSP", "NOT_TSP_CONVENIENCE"),
        "ART-130PAIR-SIT-UNKNOWN": ("SIT-130PAIR-UNKNOWN", "UNKNOWN"),
    }
    for article_id, (sit_episode_id, cause) in sit_cases.items():
        sit_performances, sit_pairs = article_rows(article_id)
        require(len(sit_performances) == 2 and len(sit_pairs) == 1, f"{article_id} SIT pair cardinality mismatch")
        require(all(row.get("sit_episode_id") == sit_episode_id for row in sit_performances), f"{article_id} SIT performance linkage mismatch")
        require(all(row.get("tsp_convenience_status") == cause for row in sit_performances), f"{article_id} SIT cause mismatch")
        require(sit_pairs[0].get("sit_episode_id") == sit_episode_id, f"{article_id} pair SIT linkage mismatch")
        require(sit_pairs[0].get("pairing_status") == "ACCEPTED", f"{article_id} factual pair must remain accepted")

    for collection in (
        "service_definitions", "service_approval_events", "rating_runs", "rule_decisions",
        "billing_eligibility_decisions", "charge_calculations", "calculation_steps",
        "expected_charge_lines", "reconciliation_matches", "invoice_lines",
        "invoice_line_versions", "payments", "payment_allocations", "audit_findings",
        "human_review_cases",
    ):
        require(not records(fixture, collection), f"Item 130 handling/SIT fixture cannot contain {collection}")


def validate_item_130_exclusion_approval_boundaries(fixture: dict) -> None:
    articles = by_id(fixture, "shipment_articles")
    conditions = by_id(fixture, "article_condition_observations")
    contexts = by_id(fixture, "article_service_context_observations")
    performances = by_id(fixture, "service_performances")
    approvals = by_id(fixture, "service_approval_events")
    evidence = by_id(fixture, "evidence_links")

    expected_articles = {
        "ART-130EA-CODE2": ("CANOE", "130C"),
        "ART-130EA-CRATE-APPROVED": ("JET_SKI", "130C"),
        "ART-130EA-CRATE-PERFORMED": ("KAYAK", "130C"),
        "ART-130EA-HANDCARRY": ("WINDSURFER", "130C"),
        "ART-130EA-CARTON": ("WINDSURFER", "130C"),
        "ART-130EA-CANOE-EXCEPTION": ("CANOE", "130C"),
        "ART-130EA-KAYAK-EXCEPTION": ("KAYAK", "130C"),
        "ART-130EA-DINGHY-EXCEPTION": ("DINGHY", "130D"),
        "ART-130EA-SHUTTLE": ("JET_SKI", "130C"),
        "ART-130EA-APPROVAL-GATES": ("WINDSURFER", "130C"),
    }
    require(set(articles) == set(expected_articles), "Item 130 exclusion/approval article set mismatch")

    common_fields = {
        "recorded_at", "recorded_by", "record_source_kind", "source_version_id",
        "source_locator_id", "interpretation_status", "sensitivity_class",
        "sanitization_status",
    }
    prohibited_fields = {
        "billing_item_code", "billing_item_code_text", "billable_quantity",
        "quantity", "quantity_unit", "rate", "rate_version", "amount",
        "expected_amount", "currency", "rule_package_id", "audit_adapter",
        "interpretation_decision_id", "service_definition_id",
        "financial_eligibility", "standardized_approver_role",
    }
    for record in [
        *articles.values(), *conditions.values(), *contexts.values(),
        *performances.values(), *approvals.values(),
    ]:
        require(common_fields.issubset(record), f"{record['id']} lacks approved common metadata")
        parse_instant(record["recorded_at"], f"{record['id']}.recorded_at")
        require(record["record_source_kind"] == "SYNTHETIC_FIXTURE", f"{record['id']} source kind mismatch")
        require(record["sanitization_status"] == "SYNTHETIC", f"{record['id']} is not synthetic")
        require(record["sensitivity_class"] != "PII", f"{record['id']} cannot contain PII")
        require(record["source_version_id"] and record["source_locator_id"], f"{record['id']} lacks source provenance")
        require(not prohibited_fields.intersection(record), f"{record['id']} contains a prohibited financial or mapping field")

    def evidence_for(record: dict, target_kind: str, role: str, review_status: str = "REVIEWED") -> dict:
        link = evidence.get(record.get("evidence_link_id"))
        if link is None:
            candidates = [
                row for row in evidence.values()
                if row.get("target_kind") == target_kind and row.get("target_id") == record["id"]
            ]
            require(len(candidates) == 1, f"{record['id']} needs one exact evidence target")
            link = candidates[0]
        require(link.get("target_kind") == target_kind and link.get("target_id") == record["id"], f"{record['id']} evidence target mismatch")
        require(link.get("evidence_role") == role and link.get("review_status") == review_status, f"{record['id']} evidence role/review mismatch")
        return link

    for article_id, (kind, candidate) in expected_articles.items():
        article = articles[article_id]
        require(article.get("shipment_id") == "SHP-130EA-001", f"{article_id} shipment mismatch")
        require(article.get("article_kind_observed") == kind, f"{article_id} article kind mismatch")
        require(article.get("tariff_classification_candidate") == candidate, f"{article_id} candidate mismatch")
        require(article.get("classification_review_status") == "ACCEPTED", f"{article_id} is not reviewed")
        require(article.get("associated_trailer_status") == "ABSENT", f"{article_id} trailer state mismatch")
        evidence_for(article, "SHIPMENT_ARTICLE", "ARTICLE_IDENTITY_AND_CLASSIFICATION_REVIEW")

    expected_contexts = {
        "ASC-130EA-CODE2": ("ART-130EA-CODE2", "SHIPMENT_SERVICE_CODE", "CODE_2", "SHIPMENT_SERVICE_CODE_OBSERVATION"),
        "ASC-130EA-CRATE-APPROVED": ("ART-130EA-CRATE-APPROVED", "CRATING_APPROVAL", "APPROVED", "CRATING_APPROVAL_OBSERVATION"),
        "ASC-130EA-CRATE-PERFORMED": ("ART-130EA-CRATE-PERFORMED", "CRATING_PERFORMANCE", "PERFORMED", "CRATING_PERFORMANCE_OBSERVATION"),
    }
    require(set(contexts) == set(expected_contexts), "Item 130 exclusion context set mismatch")
    for context_id, (article_id, kind, value, role) in expected_contexts.items():
        context = contexts[context_id]
        require(context.get("article_id") == article_id, f"{context_id} article mismatch")
        require(context.get("context_kind") == kind and context.get("context_value_text") == value, f"{context_id} value mismatch")
        require(context.get("context_review_status") == "ACCEPTED", f"{context_id} is not reviewed")
        evidence_for(context, "ARTICLE_SERVICE_CONTEXT_OBSERVATION", role)

    expected_conditions = {
        "ACO-130EA-HANDCARRY": ("ART-130EA-HANDCARRY", "ONE_PERSON_HAND_CARRY"),
        "ACO-130EA-CARTON": ("ART-130EA-CARTON", "STANDARD_CARTON_TRANSPORTABLE"),
        "ACO-130EA-CANOE-EXCEPTION": ("ART-130EA-CANOE-EXCEPTION", "ONE_PERSON_HAND_CARRY"),
        "ACO-130EA-KAYAK-EXCEPTION": ("ART-130EA-KAYAK-EXCEPTION", "STANDARD_CARTON_TRANSPORTABLE"),
        "ACO-130EA-DINGHY-EXCEPTION": ("ART-130EA-DINGHY-EXCEPTION", "ONE_PERSON_HAND_CARRY"),
    }
    require(set(conditions) == set(expected_conditions), "Item 130 exclusion condition set mismatch")
    for condition_id, (article_id, kind) in expected_conditions.items():
        condition = conditions[condition_id]
        require(condition.get("article_id") == article_id, f"{condition_id} article mismatch")
        require(condition.get("condition_kind") == kind and condition.get("condition_value") == "YES", f"{condition_id} value mismatch")
        evidence_for(condition, "ARTICLE_CONDITION_OBSERVATION", "HANDLING_CONDITION_REVIEW")

    shuttle = performances.get("SP-130EA-SHUTTLE")
    require(shuttle is not None, "Item 130 shuttle performance is missing")
    require(shuttle.get("article_id") == "ART-130EA-SHUTTLE", "shuttle performance article mismatch")
    require(shuttle.get("observed_handling_kind") == "SHUTTLE_TRANSLOAD", "shuttle transload kind mismatch")
    require(shuttle.get("performance_status") == "COMPLETED", "shuttle transload must be completed")
    evidence_for(shuttle, "SERVICE_PERFORMANCE", "COMPLETED_SHUTTLE_TRANSLOAD")

    exclusion_facts = {
        "ART-130EA-CODE2": "CODE_2",
        "ART-130EA-CRATE-APPROVED": "CRATING_APPROVED",
        "ART-130EA-CRATE-PERFORMED": "CRATING_PERFORMED",
        "ART-130EA-HANDCARRY": "ONE_PERSON_HAND_CARRY",
        "ART-130EA-CARTON": "STANDARD_CARTON_TRANSPORTABLE",
        "ART-130EA-CANOE-EXCEPTION": "NAMED_WATERCRAFT_EXCEPTION",
        "ART-130EA-KAYAK-EXCEPTION": "NAMED_WATERCRAFT_EXCEPTION",
        "ART-130EA-DINGHY-EXCEPTION": "NAMED_WATERCRAFT_EXCEPTION",
        "ART-130EA-SHUTTLE": "SHUTTLE_TRANSLOAD",
    }
    require(set(exclusion_facts) == set(articles) - {"ART-130EA-APPROVAL-GATES"}, "Item 130 exclusion coverage mismatch")
    require({articles[row]["article_kind_observed"] for row, status in exclusion_facts.items() if status == "NAMED_WATERCRAFT_EXCEPTION"} == {"CANOE", "KAYAK", "DINGHY"}, "named watercraft exception set changed")

    approval_performance_ids = {
        "SP-130EA-APPROVAL-TIMELY": "READY",
        "SP-130EA-APPROVAL-MISSING": "MISSING",
        "SP-130EA-APPROVAL-DENIED": "DENIED",
        "SP-130EA-APPROVAL-CONFLICTING": "CONFLICTING",
        "SP-130EA-APPROVAL-LATE": "LATE",
        "SP-130EA-APPROVAL-UNREVIEWED": "UNREVIEWED",
    }
    require(set(performances) == set(approval_performance_ids) | {"SP-130EA-SHUTTLE"}, "Item 130 approval performance set mismatch")
    approvals_by_performance: dict[str, list[dict]] = {}
    for approval in approvals.values():
        approvals_by_performance.setdefault(approval.get("service_performance_id"), []).append(approval)
        require(approval.get("approval_event_type") == "PREAPPROVAL", f"{approval['id']} type mismatch")
        require(approval.get("approver_role_text") == "Synthetic Government authority", f"{approval['id']} raw approver role missing")
        require(approval.get("approver_role_mapping_status") in {"UNMAPPED", "CONFLICTING"}, f"{approval['id']} approver role was prematurely mapped")
        require("approver_role" not in approval, f"{approval['id']} cannot assert a standardized approver role")

    def approval_gate(performance: dict) -> str:
        events = approvals_by_performance.get(performance["id"], [])
        if not events:
            return "MISSING"
        require(len(events) == 1, f"{performance['id']} must have at most one isolated preapproval event")
        event = events[0]
        link = evidence.get(event.get("evidence_link_id"))
        require(link is not None, f"{event['id']} lacks evidence")
        if link.get("review_status") != "REVIEWED":
            return "UNREVIEWED"
        if event.get("decision_status") == "DENIED":
            return "DENIED"
        if event.get("decision_status") == "CONFLICTING" or event.get("approver_role_mapping_status") == "CONFLICTING":
            return "CONFLICTING"
        require(event.get("decision_status") == "APPROVED", f"{event['id']} unsupported decision status")
        if parse_instant(event.get("occurred_at"), event["id"]) >= parse_instant(performance.get("performed_at"), performance["id"]):
            return "LATE"
        return "READY"

    for performance_id, expected_gate in approval_performance_ids.items():
        performance = performances[performance_id]
        require(performance.get("shipment_id") == "SHP-130EA-001" and performance.get("article_id") == "ART-130EA-APPROVAL-GATES", f"{performance_id} subject mismatch")
        require(performance.get("candidate_service_family") == "ITEM_130_ARTICLE_HANDLING", f"{performance_id} candidate family mismatch")
        require(performance.get("observed_handling_kind") == "HANDLING_AND_BLOCKING", f"{performance_id} handling kind mismatch")
        require(performance.get("mapping_status") == "UNMAPPED" and "service_definition_id" not in performance, f"{performance_id} mapping boundary mismatch")
        require(performance.get("performance_status") == "COMPLETED", f"{performance_id} must be completed")
        parse_instant(performance.get("performed_at"), performance_id)
        evidence_for(performance, "SERVICE_PERFORMANCE", "COMPLETED_ARTICLE_HANDLING")
        require(approval_gate(performance) == expected_gate, f"{performance_id} approval gate mismatch")

    expected_approval_evidence = {
        "SAE-130EA-TIMELY": ("APPROVED", "UNMAPPED", "REVIEWED"),
        "SAE-130EA-DENIED": ("DENIED", "UNMAPPED", "REVIEWED"),
        "SAE-130EA-CONFLICTING": ("CONFLICTING", "CONFLICTING", "REVIEWED"),
        "SAE-130EA-LATE": ("APPROVED", "UNMAPPED", "REVIEWED"),
        "SAE-130EA-UNREVIEWED": ("APPROVED", "UNMAPPED", "PENDING"),
    }
    require(set(approvals) == set(expected_approval_evidence), "Item 130 approval event set mismatch")
    for approval_id, (decision_status, mapping_status, review_status) in expected_approval_evidence.items():
        approval = approvals[approval_id]
        require(approval.get("decision_status") == decision_status, f"{approval_id} decision mismatch")
        require(approval.get("approver_role_mapping_status") == mapping_status, f"{approval_id} mapping status mismatch")
        evidence_for(approval, "SERVICE_APPROVAL_EVENT", "GOVERNMENT_PREAPPROVAL", review_status)

    for collection in (
        "service_definitions", "combined_handling_pair_candidates", "rating_runs",
        "rule_decisions", "billing_eligibility_decisions", "charge_calculations",
        "calculation_steps", "expected_charge_lines", "reconciliation_matches",
        "invoice_lines", "invoice_line_versions", "payments", "payment_allocations",
        "audit_findings", "human_review_cases",
    ):
        require(not records(fixture, collection), f"Item 130 exclusion/approval fixture cannot contain {collection}")


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
    "item_130_non_monetary_facts": validate_item_130_non_monetary_facts,
    "item_130_tv_boundaries": validate_item_130_tv_boundaries,
    "item_130_volume_assembly_boundaries": validate_item_130_volume_assembly_boundaries,
    "item_130_boat_boundaries": validate_item_130_boat_boundaries,
    "item_130_handling_sit_pairing_boundaries": validate_item_130_handling_sit_pairing_boundaries,
    "item_130_exclusion_approval_boundaries": validate_item_130_exclusion_approval_boundaries,
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
    if scenario_type == "item_130_handling_sit_pairing_boundaries":
        mutations = [
            lambda value: value["records"]["service_performances"][0].__setitem__("article_id", "ART-130PAIR-ZERO"),
            lambda value: value["records"]["combined_handling_pair_candidates"][0].__setitem__("pairing_status", "CONFLICTING"),
            lambda value: value["records"]["combined_handling_pair_candidates"].__setitem__(slice(None), [row for row in value["records"]["combined_handling_pair_candidates"] if row["id"] != "PAIR-130PAIR-MULTI-2"]),
            lambda value: next(row for row in value["records"]["service_performances"] if row["id"] == "SP-130PAIR-UNMATCHED-LOAD").__setitem__("observed_handling_kind", "UNLOADING"),
            lambda value: next(row for row in value["records"]["combined_handling_pair_candidates"] if row["id"] == "PAIR-130PAIR-DUP-1").__setitem__("pairing_status", "ACCEPTED"),
            lambda value: next(row for row in value["records"]["service_performances"] if row["id"] == "SP-130PAIR-SIT-TSP-LOAD").__setitem__("tsp_convenience_status", "NOT_TSP_CONVENIENCE"),
            lambda value: next(row for row in value["records"]["combined_handling_pair_candidates"] if row["id"] == "PAIR-130PAIR-SIT-UNKNOWN").pop("sit_episode_id"),
            lambda value: value["records"]["combined_handling_pair_candidates"][0].__setitem__("article_id", "ART-130PAIR-MULTI"),
            lambda value: value.__setitem__("unresolved_source_gaps", []),
            lambda value: value["records"]["service_performances"][0].__setitem__("service_definition_id", "SVCDEF-130"),
            lambda value: value["records"]["combined_handling_pair_candidates"][0].__setitem__("quantity", "1"),
            lambda value: next(row for row in value["records"]["evidence_links"] if row["id"] == "EVL-130PAIR-PAIR-SIT-UNKNOWN").__setitem__("review_status", "UNREVIEWED"),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(fixture)
            mutate(changed)
            try:
                validate_fixture(changed)
            except ValidationError:
                continue
            raise ValidationError("Item 130 handling/SIT negative regression probe did not fail")
        print("PASS SYNTH-LS-018 Item 130 handling/SIT twelve negative probes rejected")
        return
    if scenario_type == "item_130_exclusion_approval_boundaries":
        mutations = [
            lambda value: value["records"]["article_service_context_observations"][0].__setitem__("context_value_text", "CODE_D"),
            lambda value: value["records"]["article_service_context_observations"][1].__setitem__("context_kind", "CRATING_PERFORMANCE"),
            lambda value: value["records"]["article_service_context_observations"][2].__setitem__("context_value_text", "NOT_PERFORMED"),
            lambda value: value["records"]["article_condition_observations"][0].__setitem__("condition_value", "NO"),
            lambda value: value["records"]["shipment_articles"][5].__setitem__("article_kind_observed", "WINDSURFER"),
            lambda value: value["records"]["service_performances"][0].__setitem__("observed_handling_kind", "LOADING"),
            lambda value: value["records"]["service_approval_events"][0].__setitem__("occurred_at", "2026-06-15T13:00:00Z"),
            lambda value: value["records"]["service_approval_events"][1].__setitem__("decision_status", "APPROVED"),
            lambda value: value["records"]["service_approval_events"][2].__setitem__("approver_role_mapping_status", "UNMAPPED"),
            lambda value: value["records"]["evidence_links"][29].__setitem__("review_status", "REVIEWED"),
            lambda value: value["records"]["service_performances"][1].__setitem__("service_definition_id", "SVCDEF-130"),
            lambda value: value["records"]["shipment_articles"][0].update({"expected_amount": "297.78", "currency": "USD"}),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(fixture)
            mutate(changed)
            try:
                validate_fixture(changed)
            except ValidationError:
                continue
            raise ValidationError("Item 130 exclusion/approval negative regression probe did not fail")
        print("PASS SYNTH-LS-017 Item 130 exclusion/approval twelve negative probes rejected")
        return
    if scenario_type == "item_130_boat_boundaries":
        mutations = [
            lambda value: value["records"]["article_measurement_observations"][0].__setitem__("measurement_value", "15"),
            lambda value: value["records"]["article_measurement_observations"][1].__setitem__("measurement_method", "PHYSICAL_CENTER_LINE"),
            lambda value: value["records"]["shipment_articles"][2].__setitem__("associated_trailer_status", "ABSENT"),
            lambda value: value["records"]["shipment_articles"][8].__setitem__("tariff_classification_candidate", "130F"),
            lambda value: value["records"]["article_service_context_observations"][0].__setitem__("context_value_text", "NOT_AGREED"),
            lambda value: value["records"]["article_service_context_observations"][3].__setitem__("context_review_status", "ACCEPTED"),
            lambda value: value.__setitem__("unresolved_source_gaps", [row for row in value["unresolved_source_gaps"] if row["id"] != "GAP-130E-SUBTYPE-ROWS"]),
            lambda value: value.__setitem__("unresolved_source_gaps", [row for row in value["unresolved_source_gaps"] if row["id"] != "GAP-130F-BOTO-BOUNDARY"]),
            lambda value: value["records"]["shipment_articles"][0].update({"expected_amount": "297.78", "currency": "USD"}),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(fixture)
            mutate(changed)
            try:
                validate_fixture(changed)
            except ValidationError:
                continue
            raise ValidationError("Item 130C-130F negative regression probe did not fail")
        print("PASS SYNTH-LS-016 Item 130C-130F nine negative probes rejected")
        return
    if scenario_type == "item_130_volume_assembly_boundaries":
        mutations = [
            lambda value: value["records"]["article_measurement_observations"][0].__setitem__("measurement_value", "100"),
            lambda value: value["records"]["shipment_articles"][4].__setitem__("tariff_classification_candidate", "130J"),
            lambda value: value["records"]["shipment_articles"][2].__setitem__("tariff_classification_candidate", "130I"),
            lambda value: value["records"]["article_condition_observations"][3].__setitem__("condition_value", "NO"),
            lambda value: value["records"]["evidence_links"].__setitem__(slice(None), [row for row in value["records"]["evidence_links"] if row["id"] != "EVL-130I-MEASURE-EXACT"]),
            lambda value: value["records"]["shipment_articles"][0].update({"expected_amount": "297.78", "currency": "USD"}),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(fixture)
            mutate(changed)
            try:
                validate_fixture(changed)
            except ValidationError:
                continue
            raise ValidationError("Item 130I/130J negative regression probe did not fail")
        print("PASS SYNTH-LS-015 Item 130I/130J six negative probes rejected")
        return
    if scenario_type == "item_130_tv_boundaries":
        mutations = [
            lambda value: value["records"]["article_measurement_observations"][0].__setitem__("measurement_value", "47.999"),
            lambda value: value["records"]["shipment_articles"][1].__setitem__("tariff_classification_candidate", "130G"),
            lambda value: value["records"]["shipment_articles"][2].__setitem__("tariff_classification_candidate", "130G"),
            lambda value: value["records"]["evidence_links"].__setitem__(slice(None), [row for row in value["records"]["evidence_links"] if row["id"] != "EVL-130G-ARTICLE-BOUNDARY"]),
            lambda value: value["records"]["shipment_articles"][0].update({"expected_amount": "297.78", "currency": "USD"}),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(fixture)
            mutate(changed)
            try:
                validate_fixture(changed)
            except ValidationError:
                continue
            raise ValidationError("Item 130G negative regression probe did not fail")
        print("PASS SYNTH-LS-014 Item 130G five negative probes rejected")
        return
    if scenario_type == "item_130_non_monetary_facts":
        mutations = [
            lambda value: value["records"]["combined_handling_pair_candidates"][0].__setitem__("expected_amount", "297.78"),
            lambda value: value["records"]["service_performances"][0].__setitem__("service_definition_id", "SVCDEF-130B"),
            lambda value: value["records"]["evidence_links"].__setitem__(slice(None), [row for row in value["records"]["evidence_links"] if row["id"] != "EVL-130-MEASUREMENT"]),
            lambda value: value["records"]["combined_handling_pair_candidates"][0].update({"supersedes_id": "CHPC-130B-001", "correction_reason": "invalid self-reference"}),
            lambda value: value["records"]["article_measurement_observations"][0].__setitem__("measurement_value", "249"),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(fixture)
            mutate(changed)
            try:
                validate_fixture(changed)
            except ValidationError:
                continue
            raise ValidationError("Item 130 negative regression probe did not fail")
        print("PASS SYNTH-LS-013 Item 130 five negative probes rejected")
        return
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

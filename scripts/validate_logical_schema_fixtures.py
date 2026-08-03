#!/usr/bin/env python3
"""Validate synthetic logical-schema scenarios without choosing physical types."""

from __future__ import annotations

import copy
import json
import re
import sys
from datetime import datetime
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
    "weight",
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
    "weight": "weight_unit",
}
REFERENCE_TARGETS = {
    "bills_of_lading": {"shipment_id": "shipments"},
    "invoices": {"bill_of_lading_id": "bills_of_lading"},
    "invoice_versions": {"invoice_id": "invoices", "supersedes_id": "invoice_versions"},
    "invoice_lines": {"invoice_id": "invoices", "parent_line_id": "invoice_lines"},
    "invoice_line_versions": {
        "invoice_line_id": "invoice_lines",
        "invoice_version_id": "invoice_versions",
        "supersedes_id": "invoice_line_versions",
    },
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
    "payment_allocations": {"payment_id": "payments", "invoice_line_id": "invoice_lines"},
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

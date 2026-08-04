"""Decide post-invoice reweigh refund and billing-hold workflow readiness."""

from __future__ import annotations

from datetime import datetime

from rules.scale_reweigh_lower_reference import (
    PROVENANCE as LOWER_REFERENCE_PROVENANCE,
    RULE_ID as LOWER_REFERENCE_RULE_ID,
    RULE_PACKAGE_ID as LOWER_REFERENCE_PACKAGE_ID,
)


RULE_PACKAGE_ID = "RP-DP3-2026-REWEIGH-REFUND-WORKFLOW-1"
REFUND_RULE_ID = "RULE-POST-INVOICE-REWEIGH-SUPPLEMENTAL-REFUND-REQUIRED"
HOLD_RULE_ID = "RULE-REWEIGH-DESTINATION-BILLING-HOLD-RELEASE-READY"
RULE_IDS = (REFUND_RULE_ID, HOLD_RULE_ID)
PROVENANCE = (
    {"source_version_id": "SV-DP3-2026-400NG-2025-12-05", "source_claim_id": "CLM-0026", "source_locator_id": "LOC-0022"},
    {"source_version_id": "SV-DP3-2026-TOS-C1-2026-02-18", "source_claim_id": "CLM-0031", "source_locator_id": "LOC-0027"},
    {"source_version_id": "SV-DTR-IV-A402-2026-07-14", "source_claim_id": "CLM-0032", "source_locator_id": "LOC-0028"},
)
LOWER_RESULT_REQUIREMENT_ID = "EVID-REWEIGH-REFUND-WORKFLOW-001"
INVOICE_SUBMISSION_REQUIREMENT_ID = "EVID-REWEIGH-REFUND-WORKFLOW-002"
DPS_UPDATE_REQUIREMENT_ID = "EVID-REWEIGH-REFUND-WORKFLOW-003"
TICKET_DELIVERY_REQUIREMENT_ID = "EVID-REWEIGH-REFUND-WORKFLOW-004"
REFUND_PROCESSING_REQUIREMENT_ID = "EVID-REWEIGH-REFUND-WORKFLOW-005"
REQUIRED_DPS_FACTS = {"GROSS", "TARE", "NET", "TICKET_NUMBER", "REWEIGH_DATE"}


class RuleInputError(ValueError):
    """Raised when workflow input is malformed or tampered."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuleInputError(message)


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


def _validate_lower_result(result: object) -> dict:
    _require(isinstance(result, dict), "lower_weight_result must be an object")
    _require(result.get("rule_package_id") == LOWER_REFERENCE_PACKAGE_ID, "lower_weight_result uses an unknown rule package")
    _require(result.get("rule_id") == LOWER_REFERENCE_RULE_ID, "lower_weight_result rule mismatch")
    _require(result.get("provenance") == list(LOWER_REFERENCE_PROVENANCE), "lower_weight_result provenance mismatch")
    _require(result.get("status") in {"FINAL", "BLOCKED"}, "lower_weight_result has invalid status")
    return result


def _reviewed_evidence(link_id: object, evidence_links: dict[str, dict], *, target_kind: str, target_id: str) -> bool:
    if not isinstance(link_id, str) or link_id not in evidence_links:
        return False
    link = evidence_links[link_id]
    return (
        link.get("target_kind") == target_kind
        and link.get("target_id") == target_id
        and link.get("review_status") == "REVIEWED"
    )


def determine_reweigh_refund_workflow(case: dict) -> dict:
    """Return non-monetary refund-required and hold-release-readiness decisions."""

    _require(isinstance(case, dict), "case must be an object")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id, "case_id is required")
    _require(case.get("data_status") in {"synthetic", "authorized_sanitized"}, "data_status must be synthetic or authorized_sanitized")
    lower_result = _validate_lower_result(case.get("lower_weight_result"))
    records = case.get("records")
    _require(isinstance(records, dict), "records must be an object")

    workflow_cases = _index(records.get("reweigh_refund_cases"), "reweigh_refund_cases")
    invoices = _index(records.get("invoices"), "invoices")
    invoice_versions = _index(records.get("invoice_versions"), "invoice_versions")
    invoice_submissions = _index(records.get("invoice_submissions"), "invoice_submissions")
    events = _index(records.get("weighing_events"), "weighing_events")
    updates = _index(records.get("dps_reweigh_update_events"), "dps_reweigh_update_events")
    deliveries = _index(records.get("reweigh_ticket_delivery_events"), "reweigh_ticket_delivery_events")
    adjustments = _index(records.get("reweigh_refund_adjustment_events"), "reweigh_refund_adjustment_events")
    evidence_links = _index(records.get("evidence_links"), "evidence_links")
    _require(len(workflow_cases) == 1, "exactly one reweigh-refund case is required")
    workflow = next(iter(workflow_cases.values()))

    original_invoice_id = workflow.get("original_invoice_id")
    reweigh_event_id = workflow.get("completed_reweigh_event_id")
    _require(original_invoice_id in invoices, "workflow references unknown original invoice")
    _require(reweigh_event_id in events, "workflow references unknown completed reweigh")
    original_invoice = invoices[original_invoice_id]
    _require(original_invoice.get("invoice_kind") == "ORIGINAL", "workflow invoice is not original")
    original_version_ids = {version["id"] for version in invoice_versions.values() if version.get("invoice_id") == original_invoice_id}
    _require(len(original_version_ids) == 1, "workflow requires one immutable original invoice version")
    submissions = [submission for submission in invoice_submissions.values() if submission.get("invoice_version_id") in original_version_ids]
    _require(len(submissions) == 1, "workflow requires one original invoice submission")
    submission = submissions[0]
    submitted_at = _instant(submission.get("submitted_at"), "original invoice submitted_at")

    reweigh = events[reweigh_event_id]
    _require(reweigh.get("shipment_id") == workflow.get("shipment_id"), "workflow and reweigh shipments differ")
    _require(reweigh.get("weighing_kind") == "REWEIGH_SCALE" and reweigh.get("completion_status") == "COMPLETED", "workflow reweigh is not completed")
    reweigh_at = _instant(reweigh.get("occurred_at_or_date"), "reweigh occurred_at_or_date")
    _require(workflow.get("lower_weight_result_ref") == lower_result.get("case_id"), "lower-weight result reference does not match supplied result")

    common = {
        "case_id": case_id,
        "rule_package_id": RULE_PACKAGE_ID,
        "rule_ids": list(RULE_IDS),
        "input_snapshot": {
            "workflow_case_id": workflow["id"],
            "shipment_id": workflow.get("shipment_id"),
            "original_invoice_id": original_invoice_id,
            "original_invoice_submission_id": submission["id"],
            "completed_reweigh_event_id": reweigh_event_id,
            "lower_weight_result_case_id": lower_result.get("case_id"),
        },
        "evidence": {
            "lower_result_requirement_id": LOWER_RESULT_REQUIREMENT_ID,
            "invoice_submission_requirement_id": INVOICE_SUBMISSION_REQUIREMENT_ID,
            "dps_update_requirement_id": DPS_UPDATE_REQUIREMENT_ID,
            "ticket_delivery_requirement_id": TICKET_DELIVERY_REQUIREMENT_ID,
            "refund_processing_requirement_id": REFUND_PROCESSING_REQUIREMENT_ID,
        },
        "provenance": [dict(reference) for reference in PROVENANCE],
        "unresolved_assumptions": [],
    }
    if lower_result["status"] == "BLOCKED":
        return {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": ["LOWER_WEIGHT_RESULT_BLOCKED"],
            "upstream_blocked_reasons": lower_result.get("blocked_reasons", []),
        }

    reference = lower_result.get("reference")
    _require(isinstance(reference, dict), "FINAL lower_weight_result lacks reference")
    selected_source = reference.get("selected_source")
    _require(selected_source in {"INITIAL_SCALE_WEIGHT", "COMPLETED_REWEIGH", "TIE"}, "lower_weight_result selected source is invalid")
    selected_event_ids = reference.get("selected_reweigh_observation_ids")
    _require(isinstance(selected_event_ids, list) and reweigh_event_id in selected_event_ids, "workflow reweigh is not selected by the lower-weight result")

    post_invoice = reweigh_at > submitted_at
    lower_reweigh = selected_source == "COMPLETED_REWEIGH"
    refund_required = post_invoice and lower_reweigh
    if refund_required:
        refund_reason = "LOWER_REWEIGH_AFTER_INITIAL_INVOICE_SUBMISSION"
    elif not post_invoice:
        refund_reason = "REWEIGH_NOT_AFTER_INITIAL_INVOICE_SUBMISSION"
    else:
        refund_reason = "REWEIGH_DID_NOT_REDUCE_WEIGHT"

    related_updates = [update for update in updates.values() if update.get("weighing_event_id") == reweigh_event_id]
    _require(len(related_updates) == 1, "workflow requires one DPS update event")
    update = related_updates[0]
    delivery_events = [delivery for delivery in deliveries.values() if delivery.get("reweigh_refund_case_id") == workflow["id"]]
    _require(len(delivery_events) == 1, "workflow requires one ticket-delivery event")
    delivery = delivery_events[0]

    blocked_reasons: list[str] = []
    if not _reviewed_evidence(update.get("evidence_link_id"), evidence_links, target_kind="WEIGHING_EVENT", target_id=reweigh_event_id):
        blocked_reasons.append("DPS_UPDATE_EVIDENCE_MISSING_OR_UNREVIEWED")
    if set(update.get("recorded_fact_roles", [])) != REQUIRED_DPS_FACTS:
        blocked_reasons.append("DPS_UPDATE_FACT_COVERAGE_INCOMPLETE")
    if set(delivery.get("recipient_role_codes", [])) != {"ORIGIN_PPSO", "ORDERING_PPSO"}:
        blocked_reasons.append("PPSO_TICKET_DELIVERY_RECIPIENT_COVERAGE_INCOMPLETE")
    if not _reviewed_evidence(delivery.get("evidence_link_id"), evidence_links, target_kind="REWEIGH_TICKET_DELIVERY_EVENT", target_id=delivery["id"]):
        blocked_reasons.append("PPSO_TICKET_DELIVERY_EVIDENCE_MISSING_OR_UNREVIEWED")

    update_at = _instant(update.get("occurred_at"), "DPS update occurred_at")
    delivery_at = _instant(delivery.get("occurred_at"), "ticket delivery occurred_at")
    _require(update_at >= reweigh_at, "DPS update predates the reweigh")
    _require(delivery_at >= reweigh_at, "ticket delivery predates the reweigh")

    submitted_events = [event for event in adjustments.values() if event.get("event_type") == "NEGATIVE_SUPPLEMENTAL_SUBMITTED"]
    processed_events = [event for event in adjustments.values() if event.get("event_type") == "REFUND_PROCESSED_FOR_PAYMENT"]
    _require(len(submitted_events) <= 1 and len(processed_events) <= 1, "refund workflow event cardinality is invalid")
    refund_submitted = bool(submitted_events)
    refund_processed = bool(processed_events)
    if refund_processed:
        processed = processed_events[0]
        _require(refund_submitted, "refund cannot be processed before submission")
        processed_at = _instant(processed.get("occurred_at"), "refund processed occurred_at")
        submitted_event = submitted_events[0]
        _require(processed.get("previous_event_id") == submitted_event["id"], "refund processing does not follow submission")
        _require(processed_at >= _instant(submitted_event.get("occurred_at"), "refund submitted occurred_at"), "refund processed before submission")
        if not _reviewed_evidence(processed.get("evidence_link_id"), evidence_links, target_kind="REWEIGH_REFUND_ADJUSTMENT_EVENT", target_id=processed["id"]):
            blocked_reasons.append("REFUND_PROCESSING_EVIDENCE_MISSING_OR_UNREVIEWED")

    if blocked_reasons:
        return {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": blocked_reasons,
        }

    unmet: list[str] = []
    if update.get("update_status") != "RECORDED":
        unmet.append("DPS_REWEIGH_UPDATE_NOT_RECORDED")
    if delivery.get("timeliness_status") != "WITHIN_SEVEN_WORKING_DAYS_REVIEWED":
        unmet.append("PPSO_TICKET_DELIVERY_TIMELINESS_NOT_SATISFIED")
    if refund_required and not refund_submitted:
        unmet.append("SUPPLEMENTAL_REFUND_NOT_SUBMITTED")
    if refund_required and not refund_processed:
        unmet.append("REFUND_NOT_PROCESSED_FOR_PAYMENT")

    return {
        **common,
        "status": "FINAL",
        "human_review_required": False,
        "decisions": {
            "supplemental_refund": {
                "required": refund_required,
                "reason_code": refund_reason,
                "post_invoice_reweigh": post_invoice,
                "lower_reweigh_selected": lower_reweigh,
            },
            "destination_direct_delivery_hold": {
                "release_ready": not unmet,
                "target_service_scope": "DESTINATION_AND_DIRECT_DELIVERY",
                "unmet_prerequisites": unmet,
            },
        },
    }

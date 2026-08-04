"""Calculate and select a 2026 DP3 constructive-weight reference."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from rules.scale_reweigh_lower_reference import (
    PROVENANCE as SCALE_REFERENCE_PROVENANCE,
    RULE_ID as SCALE_REFERENCE_RULE_ID,
    RULE_PACKAGE_ID as SCALE_REFERENCE_PACKAGE_ID,
)


RULE_PACKAGE_ID = "RP-DP3-2026-CONSTRUCTIVE-WEIGHT-1"
CALCULATION_RULE_ID = "RULE-CONSTRUCTIVE-WEIGHT-7-LB-PER-CU-FT"
SELECTION_RULE_ID = "RULE-LOWER-OF-VALID-TICKET-AND-CONSTRUCTIVE-WEIGHT"
RULE_IDS = (CALCULATION_RULE_ID, SELECTION_RULE_ID)
FACTOR = Decimal("7")
PROVENANCE = (
    {
        "source_version_id": "SV-DP3-2026-400NG-2025-12-05",
        "source_claim_id": "CLM-0025",
        "source_locator_id": "LOC-0021",
    },
    {
        "source_version_id": "SV-DTR-IV-A402-2026-07-14",
        "source_claim_id": "CLM-0033",
        "source_locator_id": "LOC-0029",
    },
)
VOLUME_EVIDENCE_REQUIREMENT_ID = "EVID-CONSTRUCTIVE-WEIGHT-001"
APPROVAL_EVIDENCE_REQUIREMENT_ID = "EVID-CONSTRUCTIVE-WEIGHT-002"
TICKET_STATUS_EVIDENCE_REQUIREMENT_ID = "EVID-CONSTRUCTIVE-SELECT-001"
ELIGIBILITY_REASONS = {"SCALES_UNAVAILABLE", "SCALE_USE_IMPRACTICAL", "WEIGHT_TICKETS_LOST"}
DECIMAL_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")


class RuleInputError(ValueError):
    """Raised when constructive-weight input is malformed or tampered."""


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


def _reviewed_evidence(
    link_id: object,
    *,
    evidence_links: dict[str, dict],
    document_versions: dict[str, dict],
    documents: dict[str, dict],
    target_kind: str,
    target_id: str,
    document_type: str,
) -> bool:
    if not isinstance(link_id, str) or link_id not in evidence_links:
        return False
    link = evidence_links[link_id]
    if (
        link.get("target_kind") != target_kind
        or link.get("target_id") != target_id
        or link.get("review_status") != "REVIEWED"
    ):
        return False
    document_version_id = link.get("document_version_id")
    if document_version_id not in document_versions:
        return False
    document_id = document_versions[document_version_id].get("document_id")
    return document_id in documents and documents[document_id].get("document_type") == document_type


def _validate_ticket_result(result: dict) -> dict:
    _require(result.get("rule_package_id") == SCALE_REFERENCE_PACKAGE_ID, "valid_ticket_weight_result uses an unknown rule package")
    _require(result.get("rule_id") == SCALE_REFERENCE_RULE_ID, "valid_ticket_weight_result rule mismatch")
    _require(result.get("provenance") == list(SCALE_REFERENCE_PROVENANCE), "valid_ticket_weight_result provenance mismatch")
    _require(result.get("status") in {"FINAL", "BLOCKED"}, "valid_ticket_weight_result has invalid status")
    return result


def determine_constructive_weight_reference(case: dict) -> dict:
    """Return an evidence-gated constructive-weight reference.

    Exact multiplication is preserved without rounding because the reviewed
    sources state the factor but no rounding instruction. This function does not
    decide a fee, tolerance, refund, billing item, invoice amount, or money.
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

    volumes = _index(records.get("shipment_volume_observations"), "shipment_volume_observations")
    approvals = _index(records.get("constructive_weight_approval_events"), "constructive_weight_approval_events")
    assessments = _index(records.get("constructive_weight_assessments"), "constructive_weight_assessments")
    evidence_links = _index(records.get("evidence_links"), "evidence_links")
    document_versions = _index(records.get("document_versions"), "document_versions")
    documents = _index(records.get("documents"), "documents")
    _require(len(assessments) == 1, "exactly one constructive-weight assessment is required")
    assessment = next(iter(assessments.values()))

    volume_id = assessment.get("volume_observation_id")
    approval_id = assessment.get("approval_event_id")
    _require(volume_id in volumes, "assessment references unknown volume observation")
    _require(approval_id in approvals, "assessment references unknown approval event")
    volume = volumes[volume_id]
    approval = approvals[approval_id]
    _require(volume.get("shipment_id") == assessment.get("shipment_id"), "volume and assessment shipments differ")
    _require(approval.get("shipment_id") == assessment.get("shipment_id"), "approval and assessment shipments differ")
    _require(approval.get("volume_observation_id") == volume_id, "approval references a different volume observation")
    _require(assessment.get("factor_source_claim_id") == "CLM-0025", "constructive factor source claim mismatch")
    _require(volume.get("volume_unit") == "cu_ft", "verified volume unit must be cu_ft")
    volume_value = _decimal(volume.get("volume_value"), "shipment_volume_observation.volume_value")

    blocked_reasons: list[str] = []
    if volume_value <= 0 or volume.get("verification_status") != "VERIFIED":
        blocked_reasons.append("VERIFIED_POSITIVE_CUBIC_VOLUME_MISSING")
    if not _reviewed_evidence(
        volume.get("evidence_link_id"),
        evidence_links=evidence_links,
        document_versions=document_versions,
        documents=documents,
        target_kind="SHIPMENT_VOLUME_OBSERVATION",
        target_id=volume["id"],
        document_type="VOLUME_WORKSHEET",
    ):
        blocked_reasons.append("VOLUME_EVIDENCE_MISSING_OR_UNREVIEWED")
    if approval.get("eligibility_reason_code") not in ELIGIBILITY_REASONS:
        blocked_reasons.append("CONSTRUCTIVE_WEIGHT_ELIGIBILITY_NOT_ESTABLISHED")
    if approval.get("decision_status") != "APPROVED" or approval.get("approver_role") != "RESPONSIBLE_PPSO":
        blocked_reasons.append("RESPONSIBLE_PPSO_APPROVAL_MISSING")
    if not _reviewed_evidence(
        approval.get("evidence_link_id"),
        evidence_links=evidence_links,
        document_versions=document_versions,
        documents=documents,
        target_kind="CONSTRUCTIVE_WEIGHT_APPROVAL_EVENT",
        target_id=approval["id"],
        document_type="PPSO_APPROVAL_RECORD",
    ):
        blocked_reasons.append("PPSO_APPROVAL_EVIDENCE_MISSING_OR_UNREVIEWED")
    if assessment.get("readiness_status") != "READY_FOR_DETERMINISTIC_RULE":
        blocked_reasons.append("CONSTRUCTIVE_WEIGHT_ASSESSMENT_NOT_READY")

    ticket_status = assessment.get("valid_ticket_status")
    ticket_result = case.get("valid_ticket_weight_result")
    ticket_weight: Decimal | None = None
    ticket_result_blockers: list[str] = []
    if ticket_status == "FINAL_VALID_PUBLISHED_RESULT":
        if not isinstance(ticket_result, dict):
            blocked_reasons.append("VALID_TICKET_RESULT_MISSING")
        else:
            _validate_ticket_result(ticket_result)
            _require(
                assessment.get("ticket_weight_result_ref") == ticket_result.get("case_id"),
                "ticket result reference does not match the supplied result",
            )
            if ticket_result["status"] == "BLOCKED":
                blocked_reasons.append("VALID_TICKET_RESULT_BLOCKED")
                ticket_result_blockers = ticket_result.get("blocked_reasons", [])
            else:
                reference = ticket_result.get("reference")
                _require(isinstance(reference, dict), "FINAL valid_ticket_weight_result lacks reference")
                _require(reference.get("weight_unit") == "lb", "valid_ticket_weight_result unit must be lb")
                ticket_weight = _decimal(reference.get("lower_weight"), "valid_ticket_weight_result.reference.lower_weight")
        if not _reviewed_evidence(
            assessment.get("ticket_evidence_link_id"),
            evidence_links=evidence_links,
            document_versions=document_versions,
            documents=documents,
            target_kind="CONSTRUCTIVE_WEIGHT_ASSESSMENT",
            target_id=assessment["id"],
            document_type="WEIGHT_TICKET",
        ):
            blocked_reasons.append("VALID_TICKET_EVIDENCE_MISSING_OR_UNREVIEWED")
        _require("ticket_unavailability_reason" not in assessment, "valid ticket assessment carries an unavailability reason")
    elif ticket_status == "NOT_AVAILABLE_DOCUMENTED":
        _require(ticket_result is None, "documented ticket unavailability cannot carry a ticket result")
        if (
            assessment.get("ticket_unavailability_reason") != "WEIGHT_TICKETS_LOST"
            or approval.get("eligibility_reason_code") != "WEIGHT_TICKETS_LOST"
        ):
            blocked_reasons.append("TICKET_UNAVAILABILITY_NOT_ESTABLISHED")
        _require("ticket_weight_result_ref" not in assessment, "unavailable ticket assessment carries a result reference")
        _require("ticket_evidence_link_id" not in assessment, "unavailable ticket assessment carries ticket evidence")
    else:
        blocked_reasons.append("VALID_TICKET_STATUS_UNRESOLVED")

    input_snapshot = {
        "shipment_id": assessment.get("shipment_id"),
        "assessment_id": assessment["id"],
        "volume_observation_id": volume["id"],
        "verified_volume": _canonical_decimal(volume_value),
        "volume_unit": "cu_ft",
        "approval_event_id": approval["id"],
        "eligibility_reason_code": approval.get("eligibility_reason_code"),
        "valid_ticket_status": ticket_status,
    }
    evidence_snapshot = {
        "volume_requirement_id": VOLUME_EVIDENCE_REQUIREMENT_ID,
        "approval_requirement_id": APPROVAL_EVIDENCE_REQUIREMENT_ID,
        "ticket_status_requirement_id": TICKET_STATUS_EVIDENCE_REQUIREMENT_ID,
        "volume_evidence_link_id": volume.get("evidence_link_id"),
        "approval_evidence_link_id": approval.get("evidence_link_id"),
    }
    if isinstance(ticket_result, dict):
        input_snapshot["valid_ticket_result_case_id"] = ticket_result.get("case_id")
    if assessment.get("ticket_evidence_link_id") is not None:
        evidence_snapshot["ticket_evidence_link_id"] = assessment["ticket_evidence_link_id"]

    common = {
        "case_id": case_id,
        "rule_package_id": RULE_PACKAGE_ID,
        "rule_ids": list(RULE_IDS),
        "input_snapshot": input_snapshot,
        "evidence": evidence_snapshot,
        "provenance": [dict(reference) for reference in PROVENANCE],
        "unresolved_assumptions": [],
    }

    if blocked_reasons:
        result = {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": list(dict.fromkeys(blocked_reasons)),
        }
        if ticket_result_blockers:
            result["upstream_blocked_reasons"] = ticket_result_blockers
        return result

    constructive_weight = volume_value * FACTOR
    if ticket_weight is None:
        selected_weight = constructive_weight
        selected_source = "CONSTRUCTIVE_WEIGHT_ONLY_DOCUMENTED_TICKET_UNAVAILABILITY"
    elif ticket_weight < constructive_weight:
        selected_weight = ticket_weight
        selected_source = "VALID_TICKET_WEIGHT"
    elif constructive_weight < ticket_weight:
        selected_weight = constructive_weight
        selected_source = "CONSTRUCTIVE_WEIGHT"
    else:
        selected_weight = constructive_weight
        selected_source = "TIE"

    selection = {
        "comparison_method": "LOWER_OF_VALID_TICKET_AND_CONSTRUCTIVE_WEIGHT",
        "selected_weight": _canonical_decimal(selected_weight),
        "weight_unit": "lb",
        "selected_source": selected_source,
        "constructive_weight": _canonical_decimal(constructive_weight),
    }
    if ticket_weight is not None:
        selection["valid_ticket_weight"] = _canonical_decimal(ticket_weight)

    return {
        **common,
        "status": "FINAL",
        "human_review_required": False,
        "calculation": {
            "expression": "verified_volume_cu_ft * 7_lb_per_cu_ft",
            "steps": [
                {"ordinal": 1, "operation": "VERIFIED_VOLUME", "value": _canonical_decimal(volume_value), "unit": "cu_ft"},
                {"ordinal": 2, "operation": "MULTIPLY_FACTOR", "value": "7", "unit": "lb_per_cu_ft"},
            ],
            "result": _canonical_decimal(constructive_weight),
            "result_unit": "lb",
            "rounding_rule": "NONE_SOURCE_DOES_NOT_SPECIFY_ROUNDING",
        },
        "selection": selection,
    }

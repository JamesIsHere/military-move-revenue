"""Validate metadata-only controls before authorized historical case execution."""

from __future__ import annotations

import copy
import re
from datetime import date, datetime


INTAKE_SCHEMA_VERSION = "historical-intake-control.v1"
INTAKE_POLICY_ID = "HISTORICAL-INTAKE-CONTROL-V1"
INTAKE_POLICY_VERSION = "2026-08-07.1"
SCOPE_CODE = "DOMESTIC_DP3_TSP_GOV_POST_AUDIT"

SYNTHETIC_TEMPLATE = "SYNTHETIC_TEMPLATE"
OPERATIONAL = "OPERATIONAL"

PROVENANCE_FIELDS = {
    "source_id",
    "document_version",
    "effective_period",
    "locator",
    "retrieval_date",
    "interpretation_status",
}
REQUIRED_REMOVED_CATEGORIES = [
    "addresses",
    "financial_accounts",
    "hidden_document_metadata",
    "live_government_identifiers",
    "names",
    "personal_identifiers",
    "signatures",
]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

INTAKE_POLICY_PROVENANCE = (
    {
        "source_id": "GOAL-RATIFIED-2026-08-03",
        "document_path": "goal.md",
        "document_version": "ratified 2026-08-03",
        "effective_period": "2026-08-03/open",
        "locator": "Approval required; Sensitive-data quality bar; Completion verifier",
        "retrieval_date": "2026-08-07",
        "interpretation_status": "ratified_internal_policy",
    },
    {
        "source_id": "HISTORICAL-INTAKE-CONTROL-POLICY",
        "document_path": "docs/historical-intake-control.md",
        "document_version": INTAKE_POLICY_VERSION,
        "effective_period": "2026-08-07/open",
        "locator": "Envelope contract through operational promotion gate",
        "retrieval_date": "2026-08-07",
        "interpretation_status": "approved_internal_implementation_policy",
    },
)


class HistoricalIntakeError(ValueError):
    """Raised when historical intake controls are incomplete or contradictory."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HistoricalIntakeError(message)


def _require_exact_keys(value: object, expected: set[str], label: str) -> dict:
    _require(isinstance(value, dict), f"{label} must be an object")
    actual = set(value)
    _require(actual == expected, f"{label} fields mismatch: missing={sorted(expected - actual)} extra={sorted(actual - expected)}")
    return value


def _instant(value: object, label: str) -> datetime:
    _require(isinstance(value, str) and value, f"{label} must be an ISO instant")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HistoricalIntakeError(f"{label} must be an ISO instant") from exc
    _require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return parsed


def _date(value: object, label: str) -> date:
    _require(isinstance(value, str) and value, f"{label} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HistoricalIntakeError(f"{label} must be an ISO date") from exc


def _nonempty(value: object, label: str) -> str:
    _require(isinstance(value, str) and value, f"{label} is required")
    return value


def _validate_provenance(value: object, label: str) -> list[dict]:
    _require(isinstance(value, list) and value, f"{label} provenance must be a nonempty list")
    result: list[dict] = []
    for index, reference in enumerate(value):
        _require(isinstance(reference, dict), f"{label} provenance {index} must be an object")
        _require(PROVENANCE_FIELDS <= set(reference), f"{label} provenance {index} is incomplete")
        for field in PROVENANCE_FIELDS:
            _nonempty(reference[field], f"{label} provenance {index} {field}")
        _date(reference["retrieval_date"], f"{label} provenance {index} retrieval_date")
        result.append(dict(reference))
    return result


def validate_historical_intake_envelope(
    envelope: object,
    evaluated_at: object,
    *,
    allow_synthetic_template: bool = False,
) -> dict:
    """Validate a metadata-only intake envelope; templates never authorize ingest."""

    top = _require_exact_keys(
        envelope,
        {
            "schema_version",
            "policy_version",
            "control_mode",
            "envelope_id",
            "case_reference_id",
            "data_status",
            "contains_case_content",
            "real_data_ingest_authorized",
            "authorization",
            "sanitization",
            "ingest",
            "retention",
            "approval_separation",
            "provenance",
        },
        "historical intake envelope",
    )
    _require(top["schema_version"] == INTAKE_SCHEMA_VERSION, "historical intake schema version mismatch")
    _require(top["policy_version"] == INTAKE_POLICY_VERSION, "historical intake policy version mismatch")
    mode = top["control_mode"]
    _require(mode in {SYNTHETIC_TEMPLATE, OPERATIONAL}, "historical intake control mode is invalid")
    _require(mode == OPERATIONAL or allow_synthetic_template, "synthetic intake template cannot authorize operational use")
    _nonempty(top["envelope_id"], "historical intake envelope_id")
    _nonempty(top["case_reference_id"], "historical intake case_reference_id")
    _require(top["contains_case_content"] is False, "historical intake envelope must remain metadata-only")
    _validate_provenance(top["provenance"], "historical intake envelope")
    evaluated = _instant(evaluated_at, "historical intake evaluated_at")

    authorization = _require_exact_keys(
        top["authorization"],
        {
            "status",
            "reference_id",
            "scope_code",
            "valid_from",
            "valid_through",
            "verified_at",
            "data_owner_role",
            "verifier_role",
            "self_attested",
            "provenance",
        },
        "historical intake authorization",
    )
    _nonempty(authorization["reference_id"], "historical intake authorization reference_id")
    _require(authorization["scope_code"] == SCOPE_CODE, "historical intake authorization scope mismatch")
    valid_from = _date(authorization["valid_from"], "historical intake authorization valid_from")
    valid_through = _date(authorization["valid_through"], "historical intake authorization valid_through")
    verified_at = _instant(authorization["verified_at"], "historical intake authorization verified_at")
    _require(valid_from <= verified_at.date() <= valid_through, "authorization verification is outside its effective period")
    _require(evaluated.date() <= valid_through, "historical intake authorization is stale")
    data_owner_role = _nonempty(authorization["data_owner_role"], "historical intake data_owner_role")
    verifier_role = _nonempty(authorization["verifier_role"], "historical intake verifier_role")
    _require(authorization["self_attested"] is False, "historical intake authorization cannot be self-attested")
    _require(data_owner_role != verifier_role, "authorization owner and verifier roles must be distinct")
    _validate_provenance(authorization["provenance"], "historical intake authorization")

    sanitization = _require_exact_keys(
        top["sanitization"],
        {
            "status",
            "method_id",
            "method_version",
            "bundle_sha256",
            "completed_at",
            "reviewed_at",
            "sanitizer_role",
            "reviewer_role",
            "raw_source_entered_development_environment",
            "hidden_metadata_removed",
            "prohibited_categories_removed",
            "provenance",
        },
        "historical intake sanitization",
    )
    _nonempty(sanitization["method_id"], "historical intake sanitization method_id")
    _nonempty(sanitization["method_version"], "historical intake sanitization method_version")
    _require(
        isinstance(sanitization["bundle_sha256"], str) and SHA256_RE.fullmatch(sanitization["bundle_sha256"]) is not None,
        "historical intake sanitized bundle hash is invalid",
    )
    completed_at = _instant(sanitization["completed_at"], "historical intake sanitization completed_at")
    reviewed_at = _instant(sanitization["reviewed_at"], "historical intake sanitization reviewed_at")
    _require(verified_at <= completed_at <= reviewed_at, "authorization and sanitization chronology is invalid")
    sanitizer_role = _nonempty(sanitization["sanitizer_role"], "historical intake sanitizer_role")
    sanitization_reviewer_role = _nonempty(sanitization["reviewer_role"], "historical intake sanitization reviewer_role")
    _require(sanitizer_role != sanitization_reviewer_role, "sanitizer and sanitization reviewer roles must be distinct")
    _require(sanitization["raw_source_entered_development_environment"] is False, "raw source entered the development environment before sanitization")
    _require(sanitization["hidden_metadata_removed"] is True, "hidden metadata removal is not verified")
    categories = sanitization["prohibited_categories_removed"]
    _require(categories == REQUIRED_REMOVED_CATEGORIES, "sanitization removed-category declaration is incomplete or noncanonical")
    _validate_provenance(sanitization["provenance"], "historical intake sanitization")

    ingest = _require_exact_keys(
        top["ingest"],
        {"status", "approved_at", "approved_by_role", "ingest_checkpoint_at", "provenance"},
        "historical intake ingest",
    )
    ingest_approved_at = _instant(ingest["approved_at"], "historical intake ingest approved_at")
    ingest_checkpoint_at = _instant(ingest["ingest_checkpoint_at"], "historical intake ingest checkpoint_at")
    ingest_approver_role = _nonempty(ingest["approved_by_role"], "historical intake ingest approved_by_role")
    _require(reviewed_at <= ingest_approved_at <= ingest_checkpoint_at <= evaluated, "sanitization and ingest chronology is invalid")
    _validate_provenance(ingest["provenance"], "historical intake ingest")

    retention = _require_exact_keys(
        top["retention"],
        {"status", "classification", "approved_at", "approved_by_role", "delete_on", "provenance"},
        "historical intake retention",
    )
    retention_approved_at = _instant(retention["approved_at"], "historical intake retention approved_at")
    _nonempty(retention["approved_by_role"], "historical intake retention approved_by_role")
    delete_on = _date(retention["delete_on"], "historical intake retention delete_on")
    _require(retention["classification"] == "SANITIZED_HISTORICAL_ACCEPTANCE", "historical intake retention classification mismatch")
    _require(retention_approved_at <= ingest_approved_at, "retention approval must precede ingest approval")
    _require(delete_on >= evaluated.date(), "historical intake retention period has expired")
    _validate_provenance(retention["provenance"], "historical intake retention")

    separation = _require_exact_keys(
        top["approval_separation"],
        {"outcome_reviewer_role", "roles_distinct", "ai_attestation_used"},
        "historical intake approval_separation",
    )
    outcome_reviewer_role = _nonempty(separation["outcome_reviewer_role"], "historical intake outcome_reviewer_role")
    critical_roles = [verifier_role, sanitization_reviewer_role, ingest_approver_role, outcome_reviewer_role]
    _require(separation["roles_distinct"] is True and len(set(critical_roles)) == len(critical_roles), "critical approval roles are not distinct")
    _require(separation["ai_attestation_used"] is False, "AI cannot attest historical intake controls")

    if mode == SYNTHETIC_TEMPLATE:
        _require(top["data_status"] == "SYNTHETIC_METADATA_ONLY", "synthetic intake template data_status mismatch")
        _require(top["real_data_ingest_authorized"] is False, "synthetic intake template cannot authorize real-data ingest")
        _require(authorization["status"] == "SYNTHETIC_EXAMPLE_NOT_AUTHORIZATION", "synthetic authorization status mismatch")
        _require(sanitization["status"] == "SYNTHETIC_EXAMPLE_NOT_SANITIZATION", "synthetic sanitization status mismatch")
        _require(ingest["status"] == "SIMULATED_CHECKPOINT_NO_DATA_INGESTED", "synthetic ingest status mismatch")
        _require(retention["status"] == "SYNTHETIC_EXAMPLE_NOT_RETENTION_APPROVAL", "synthetic retention status mismatch")
    else:
        _require(top["data_status"] == "AUTHORIZED_SANITIZED_CONTROL_METADATA", "operational intake data_status mismatch")
        _require(top["real_data_ingest_authorized"] is True, "operational intake lacks real-data ingest authority")
        _require(authorization["status"] == "WRITTEN_AUTHORIZATION_VERIFIED", "operational written authorization is not verified")
        _require(sanitization["status"] == "VERIFIED_SANITIZED_BEFORE_INGEST", "operational pre-ingest sanitization is not verified")
        _require(ingest["status"] == "APPROVED_SANITIZED_BUNDLE_INGESTED", "operational sanitized-bundle ingest is not approved")
        _require(retention["status"] == "APPROVED", "operational retention is not approved")

    return copy.deepcopy(top)

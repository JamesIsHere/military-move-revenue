"""Validate metadata-only independent approval controls for expected labels."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import date, datetime

from rules.historical_intake import (
    OPERATIONAL,
    SYNTHETIC_TEMPLATE,
    HistoricalIntakeError,
    validate_historical_intake_envelope,
)


LABEL_CONTROL_SCHEMA_VERSION = "historical-expected-label-control.v1"
LABEL_CONTROL_POLICY_ID = "HISTORICAL-EXPECTED-LABEL-CONTROL-V1"
LABEL_CONTROL_POLICY_VERSION = "2026-08-07.1"
SCOPE_CODE = "DOMESTIC_DP3_TSP_GOV_POST_AUDIT"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PROVENANCE_FIELDS = {
    "source_id",
    "document_version",
    "effective_period",
    "locator",
    "retrieval_date",
    "interpretation_status",
}

LABEL_CONTROL_POLICY_PROVENANCE = (
    {
        "source_id": "GOAL-RATIFIED-2026-08-03",
        "document_path": "goal.md",
        "document_version": "ratified 2026-08-03",
        "effective_period": "2026-08-03/open",
        "locator": "Completion verifier; AI boundary; Sensitive-data boundary",
        "retrieval_date": "2026-08-07",
        "interpretation_status": "ratified_internal_policy",
    },
    {
        "source_id": "HISTORICAL-EXPECTED-LABEL-CONTROL-POLICY",
        "document_path": "docs/historical-expected-label-control.md",
        "document_version": LABEL_CONTROL_POLICY_VERSION,
        "effective_period": "2026-08-07/open",
        "locator": "Metadata envelope contract through operational promotion gate",
        "retrieval_date": "2026-08-07",
        "interpretation_status": "approved_internal_implementation_policy",
    },
)


class HistoricalExpectedLabelError(ValueError):
    """Raised when expected-label approval metadata is incomplete or unsafe."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HistoricalExpectedLabelError(message)


def _require_exact_keys(value: object, expected: set[str], label: str) -> dict:
    _require(isinstance(value, dict), f"{label} must be an object")
    actual = set(value)
    _require(actual == expected, f"{label} fields mismatch: missing={sorted(expected - actual)} extra={sorted(actual - expected)}")
    return value


def _nonempty(value: object, label: str) -> str:
    _require(isinstance(value, str) and value, f"{label} is required")
    return value


def _instant(value: object, label: str) -> datetime:
    _require(isinstance(value, str) and value, f"{label} must be an ISO instant")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HistoricalExpectedLabelError(f"{label} must be an ISO instant") from exc
    _require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return parsed


def _date(value: object, label: str) -> date:
    _require(isinstance(value, str) and value, f"{label} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HistoricalExpectedLabelError(f"{label} must be an ISO date") from exc


def _hash(value: object, label: str) -> str:
    _require(isinstance(value, str) and SHA256_RE.fullmatch(value) is not None, f"{label} must be a lowercase SHA-256")
    return value


def _provenance(value: object, label: str) -> list[dict]:
    _require(isinstance(value, list) and value, f"{label} provenance must be a nonempty list")
    result: list[dict] = []
    for index, reference in enumerate(value):
        item = _require_exact_keys(reference, PROVENANCE_FIELDS, f"{label} provenance {index}")
        for field in PROVENANCE_FIELDS:
            _nonempty(item[field], f"{label} provenance {index} {field}")
        _date(item["retrieval_date"], f"{label} provenance {index} retrieval_date")
        result.append(dict(item))
    return result


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_historical_expected_label_control(
    envelope: object,
    evaluated_at: object,
    linked_intake_envelope: object,
    *,
    allow_synthetic_template: bool = False,
) -> dict:
    """Validate label-approval metadata and its exact link to a valid intake envelope."""

    top = _require_exact_keys(
        envelope,
        {
            "schema_version",
            "policy_version",
            "control_mode",
            "envelope_id",
            "case_reference_id",
            "scope_code",
            "data_status",
            "contains_case_content",
            "contains_outcome_content",
            "label_use_authorized",
            "intake_link",
            "label_artifact",
            "approval",
            "execution_boundary",
            "provenance",
        },
        "historical expected-label control",
    )
    _require(top["schema_version"] == LABEL_CONTROL_SCHEMA_VERSION, "historical expected-label schema mismatch")
    _require(top["policy_version"] == LABEL_CONTROL_POLICY_VERSION, "historical expected-label policy mismatch")
    mode = top["control_mode"]
    _require(mode in {SYNTHETIC_TEMPLATE, OPERATIONAL}, "historical expected-label control mode is invalid")
    _require(mode == OPERATIONAL or allow_synthetic_template, "synthetic expected-label template cannot authorize operational use")
    _nonempty(top["envelope_id"], "historical expected-label envelope_id")
    case_reference_id = _nonempty(top["case_reference_id"], "historical expected-label case_reference_id")
    _require(top["scope_code"] == SCOPE_CODE, "historical expected-label scope mismatch")
    _require(top["contains_case_content"] is False, "historical expected-label control must remain free of case content")
    _require(top["contains_outcome_content"] is False, "historical expected-label control must remain free of outcome content")
    _provenance(top["provenance"], "historical expected-label control")
    evaluated = _instant(evaluated_at, "historical expected-label evaluated_at")

    try:
        validated_intake = validate_historical_intake_envelope(
            linked_intake_envelope,
            evaluated_at,
            allow_synthetic_template=allow_synthetic_template,
        )
    except HistoricalIntakeError as exc:
        raise HistoricalExpectedLabelError(f"linked historical intake envelope rejected: {exc}") from exc
    _require(validated_intake["control_mode"] == mode, "expected-label and intake control modes differ")
    _require(validated_intake["case_reference_id"] == case_reference_id, "expected-label and intake case references differ")

    intake_link = _require_exact_keys(
        top["intake_link"],
        {"envelope_id", "envelope_sha256", "sanitized_bundle_sha256"},
        "historical expected-label intake_link",
    )
    _require(intake_link["envelope_id"] == validated_intake["envelope_id"], "expected-label intake envelope ID mismatch")
    _require(intake_link["envelope_sha256"] == _canonical_sha256(validated_intake), "expected-label intake envelope hash mismatch")
    _hash(intake_link["envelope_sha256"], "historical expected-label intake-envelope hash")
    _require(
        intake_link["sanitized_bundle_sha256"] == validated_intake["sanitization"]["bundle_sha256"],
        "expected-label sanitized-bundle hash mismatch",
    )
    _hash(intake_link["sanitized_bundle_sha256"], "historical expected-label sanitized-bundle hash")

    label = _require_exact_keys(
        top["label_artifact"],
        {
            "label_id",
            "label_sha256",
            "storage_status",
            "creation_method",
            "authored_at",
            "author_role",
            "ai_authorship_used",
            "provenance",
        },
        "historical expected-label artifact",
    )
    label_id = _nonempty(label["label_id"], "historical expected-label label_id")
    _hash(label["label_sha256"], "historical expected-label artifact hash")
    _require(
        label["creation_method"] == "INDEPENDENTLY_AUTHORED_BEFORE_EXECUTION",
        "historical expected-label creation method mismatch",
    )
    authored_at = _instant(label["authored_at"], "historical expected-label authored_at")
    author_role = _nonempty(label["author_role"], "historical expected-label author_role")
    _require(label["ai_authorship_used"] is False, "AI cannot author a historical expected outcome")
    _provenance(label["provenance"], "historical expected-label artifact")

    approval = _require_exact_keys(
        top["approval"],
        {
            "status",
            "approval_basis",
            "approved_at",
            "reviewer_role",
            "independent_from_author",
            "ai_attestation_used",
            "provenance",
        },
        "historical expected-label approval",
    )
    approved_at = _instant(approval["approved_at"], "historical expected-label approved_at")
    reviewer_role = _nonempty(approval["reviewer_role"], "historical expected-label reviewer_role")
    _require(approval["independent_from_author"] is True and author_role != reviewer_role, "expected-label author and reviewer roles must be distinct")
    _require(approval["ai_attestation_used"] is False, "AI cannot attest historical expected-label approval")
    _provenance(approval["provenance"], "historical expected-label approval")

    intake_checkpoint = _instant(validated_intake["ingest"]["ingest_checkpoint_at"], "linked intake checkpoint")
    _require(intake_checkpoint <= authored_at <= approved_at <= evaluated, "expected-label intake/authorship/approval chronology is invalid")
    outcome_reviewer = validated_intake["approval_separation"]["outcome_reviewer_role"]
    _require(reviewer_role == outcome_reviewer, "expected-label reviewer differs from linked intake outcome reviewer")
    critical_intake_roles = {
        validated_intake["authorization"]["verifier_role"],
        validated_intake["sanitization"]["reviewer_role"],
        validated_intake["ingest"]["approved_by_role"],
    }
    _require(author_role not in critical_intake_roles, "expected-label author must be distinct from critical intake approvers")

    execution = _require_exact_keys(
        top["execution_boundary"],
        {"status", "first_execution_at", "approval_recorded_before_execution"},
        "historical expected-label execution_boundary",
    )
    _require(execution["status"] == "NOT_STARTED", "expected-label control must be completed before acceptance execution starts")
    _require(execution["first_execution_at"] is None, "unstarted expected-label control cannot carry an execution time")
    _require(execution["approval_recorded_before_execution"] is True, "pre-execution expected-label approval is not verified")

    if mode == SYNTHETIC_TEMPLATE:
        _require(top["data_status"] == "SYNTHETIC_METADATA_ONLY", "synthetic expected-label data_status mismatch")
        _require(top["label_use_authorized"] is False, "synthetic expected-label template cannot authorize label use")
        _require(label["storage_status"] == "SYNTHETIC_HASH_PLACEHOLDER_NO_ARTIFACT", "synthetic expected-label storage status mismatch")
        _require(approval["status"] == "SYNTHETIC_EXAMPLE_NOT_EXPERT_APPROVAL", "synthetic expected-label approval status mismatch")
        _require(approval["approval_basis"] == "SYNTHETIC_CONTRACT_TEST", "synthetic expected-label approval basis mismatch")
        for value, field in (
            (top["envelope_id"], "envelope_id"),
            (case_reference_id, "case_reference_id"),
            (label_id, "label_id"),
        ):
            _require(value.startswith("SYNTHETIC-"), f"synthetic expected-label {field} is not explicitly synthetic")
        for value, field in ((author_role, "author_role"), (reviewer_role, "reviewer_role")):
            _require(
                value.startswith(("SYNTHETIC-", "SYNTHETIC_")),
                f"synthetic expected-label {field} is not explicitly synthetic",
            )
    else:
        _require(top["data_status"] == "AUTHORIZED_SANITIZED_LABEL_CONTROL_METADATA", "operational expected-label data_status mismatch")
        _require(top["label_use_authorized"] is True, "operational expected-label control does not authorize label use")
        _require(
            label["storage_status"] == "HASHED_SANITIZED_LABEL_STORED_OUTSIDE_CONTROL_ENVELOPE",
            "operational expected-label storage status mismatch",
        )
        _require(approval["status"] == "EXPERT_APPROVED", "operational expected-label is not expert approved")
        _require(approval["approval_basis"] == "INDEPENDENT_EXPERT_REVIEW", "operational expected-label approval basis mismatch")

    return copy.deepcopy(top)

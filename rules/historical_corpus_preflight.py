"""Build a deterministic, non-authorizing readiness view for the empty corpus."""

from __future__ import annotations

import copy
import hashlib
import json

from rules.historical_corpus_manifest import (
    EMPTY_AWAITING_AUTHORIZATION,
    MANIFEST_POLICY_VERSION,
    REQUIRED_HISTORICAL_CASE_COUNT,
    SCOPE_CODE,
    evaluate_historical_corpus_manifest,
)


PREFLIGHT_SCHEMA_VERSION = "historical-corpus-preflight.v1"
PREFLIGHT_POLICY_ID = "HISTORICAL-CORPUS-NO-DATA-PREFLIGHT-V1"
PREFLIGHT_POLICY_VERSION = "2026-08-07.1"

PREFLIGHT_POLICY_PROVENANCE = (
    {
        "source_id": "GOAL-RATIFIED-2026-08-03",
        "document_path": "goal.md",
        "document_version": "ratified 2026-08-03",
        "effective_period": "2026-08-03/open",
        "locator": "Baseline; Approval required; Completion verifier; Completion proof",
        "retrieval_date": "2026-08-07",
        "interpretation_status": "ratified_internal_policy",
    },
    {
        "source_id": "HISTORICAL-CORPUS-PREFLIGHT-POLICY",
        "document_path": "docs/historical-corpus-preflight.md",
        "document_version": PREFLIGHT_POLICY_VERSION,
        "effective_period": "2026-08-07/open",
        "locator": "No-data preflight contract and blocker catalog",
        "retrieval_date": "2026-08-07",
        "interpretation_status": "approved_internal_implementation_policy",
    },
)


class HistoricalCorpusPreflightError(ValueError):
    """Raised when a preflight request or report violates the no-data contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HistoricalCorpusPreflightError(message)


def _source(locator: str, source_id: str = "HISTORICAL-CORPUS-PREFLIGHT-POLICY") -> list[dict]:
    if source_id == "GOAL-RATIFIED-2026-08-03":
        return [
            {
                "source_id": source_id,
                "document_version": "ratified 2026-08-03",
                "effective_period": "2026-08-03/open",
                "locator": locator,
                "retrieval_date": "2026-08-07",
                "interpretation_status": "ratified_internal_policy",
            }
        ]
    return [
        {
            "source_id": source_id,
            "document_version": PREFLIGHT_POLICY_VERSION,
            "effective_period": "2026-08-07/open",
            "locator": locator,
            "retrieval_date": "2026-08-07",
            "interpretation_status": "approved_internal_implementation_policy",
        }
    ]


def _blockers(remaining: int) -> list[dict]:
    return [
        {
            "sequence": 1,
            "code": "WRITTEN_AUTHORIZATION_REQUIRED",
            "category": "EXTERNAL_AUTHORITY",
            "status": "MISSING",
            "description": "Written authorization for sanitized domestic DP3 post-audit data is not available.",
            "required_evidence": "Authorization reference, scope, validity period, data-owner role, and independent verifier role.",
            "provenance": _source("No-data onboarding runbook step 1; Handoff checklist authorization item"),
        },
        {
            "sequence": 2,
            "code": "APPROVED_SANITIZATION_METHOD_REQUIRED",
            "category": "DATA_PROTECTION",
            "status": "MISSING",
            "description": "No approved, versioned pre-ingest sanitization method is available.",
            "required_evidence": "Approved sanitization method ID/version and confirmation that raw sources remain outside the workspace.",
            "provenance": _source("No-data onboarding runbook step 2; Handoff checklist sanitization item"),
        },
        {
            "sequence": 3,
            "code": "INDEPENDENT_SANITIZATION_REVIEW_REQUIRED",
            "category": "DATA_PROTECTION",
            "status": "MISSING",
            "description": "No independent prohibited-data and hidden-metadata review has been recorded.",
            "required_evidence": "Independent review result and sanitized-bundle SHA-256.",
            "provenance": _source("No-data onboarding runbook step 3; Handoff checklist bundle-hash item"),
        },
        {
            "sequence": 4,
            "code": "OPERATIONAL_INTAKE_ENVELOPE_REQUIRED",
            "category": "INGEST_CONTROL",
            "status": "MISSING",
            "description": "No operational historical intake-control envelope exists.",
            "required_evidence": "Validated operational intake-envelope ID and SHA-256 with authorization, retention, and separated roles.",
            "provenance": _source("No-data onboarding runbook step 4; Handoff checklist intake-envelope item"),
        },
        {
            "sequence": 5,
            "code": "INDEPENDENT_EXPECTED_LABEL_REQUIRED",
            "category": "ACCEPTANCE_CONTROL",
            "status": "MISSING",
            "description": "No independently expert-approved expected outcome is registered.",
            "required_evidence": "Expected-label ID, SHA-256, reviewer role, and approval time recorded before execution.",
            "provenance": _source("No-data onboarding runbook step 5; Handoff checklist expected-label item"),
        },
        {
            "sequence": 6,
            "code": "AUTHORIZED_SANITIZED_CASE_ENTRY_REQUIRED",
            "category": "CORPUS",
            "status": "MISSING",
            "description": "The manifest contains no authorized sanitized historical case entry.",
            "required_evidence": "Opaque case reference and immutable manifest entry linked to the validated controls and artifact hashes.",
            "provenance": _source("No-data onboarding runbook steps 6-7; Manifest contract"),
        },
        {
            "sequence": 7,
            "code": "ACCEPTANCE_EXECUTION_REPORT_REQUIRED",
            "category": "ACCEPTANCE_CONTROL",
            "status": "MISSING",
            "description": "No deterministic historical acceptance report is registered.",
            "required_evidence": "Acceptance-report ID and SHA-256 registered through a new immutable manifest entry version.",
            "provenance": _source("No-data onboarding runbook step 8; Manifest contract acceptance-report link"),
        },
        {
            "sequence": 8,
            "code": "PASSING_HISTORICAL_CASE_DEFICIT",
            "category": "COMPLETION",
            "status": "BLOCKING",
            "description": f"{remaining} additional passing authorized historical cases are required.",
            "required_evidence": "At least 25 authorized anonymized historical cases with expert-approved outcomes and passing acceptance results.",
            "provenance": _source("Completion verifier; Completion proof", "GOAL-RATIFIED-2026-08-03"),
        },
    ]


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_no_data_preflight(manifest: object) -> dict:
    """Return the canonical readiness report for an empty, non-authorizing manifest."""

    evaluation = evaluate_historical_corpus_manifest(manifest)
    _require(
        evaluation["control_mode"] == EMPTY_AWAITING_AUTHORIZATION,
        "no-data preflight accepts only an EMPTY_AWAITING_AUTHORIZATION manifest",
    )
    summary = evaluation["summary"]
    _require(summary["passing_current_case_count"] == 0, "empty-manifest preflight cannot start with passing cases")
    _require(summary["current_case_count"] == 0, "empty-manifest preflight cannot start with case entries")
    remaining = summary["remaining_passing_historical_case_count"]
    blockers = _blockers(remaining)
    manifest_id = evaluation["manifest_id"]
    manifest_as_of = evaluation["as_of_at"]
    return {
        "schema_version": PREFLIGHT_SCHEMA_VERSION,
        "policy": {
            "id": PREFLIGHT_POLICY_ID,
            "version": PREFLIGHT_POLICY_VERSION,
            "effective_period": "2026-08-07/open",
        },
        "report_id": f"{manifest_id}:NO-DATA-PREFLIGHT:{manifest_as_of}",
        "generated_from": {
            "manifest_id": manifest_id,
            "manifest_sha256": _canonical_sha256(manifest),
            "manifest_policy_version": MANIFEST_POLICY_VERSION,
            "manifest_as_of_at": manifest_as_of,
        },
        "scope_code": SCOPE_CODE,
        "status": "BLOCKED_EXTERNAL_PREREQUISITES",
        "authorizes_ingest": False,
        "contains_case_content": False,
        "progress": {
            "passing_historical_case_count": summary["passing_current_case_count"],
            "required_historical_case_count": REQUIRED_HISTORICAL_CASE_COUNT,
            "remaining_passing_historical_case_count": remaining,
            "completion_status": "NOT_READY",
        },
        "display": {
            "title": "Historical acceptance readiness",
            "headline": "Blocked - external authorization and sanitized cases required",
            "progress_label": f"0 of {REQUIRED_HISTORICAL_CASE_COUNT} passing historical cases",
            "primary_action": "Obtain written authorization and an approved sanitization process",
            "blocker_count": len(blockers),
        },
        "blockers": blockers,
        "provenance": [
            {key: value for key, value in reference.items() if key != "document_path"}
            for reference in PREFLIGHT_POLICY_PROVENANCE
        ],
        "unresolved_assumptions": [],
    }


def _first_mismatch(actual: object, expected: object, path: str = "$") -> str:
    if type(actual) is not type(expected):
        return path
    if isinstance(expected, dict):
        actual_keys = set(actual)  # type: ignore[arg-type]
        expected_keys = set(expected)
        if actual_keys != expected_keys:
            differing = sorted(actual_keys ^ expected_keys)
            return f"{path}.{differing[0]}"
        for key in sorted(expected):
            if actual[key] != expected[key]:  # type: ignore[index]
                return _first_mismatch(actual[key], expected[key], f"{path}.{key}")  # type: ignore[index]
    elif isinstance(expected, list):
        if len(actual) != len(expected):  # type: ignore[arg-type]
            return f"{path}.length"
        for index, expected_item in enumerate(expected):
            if actual[index] != expected_item:  # type: ignore[index]
                return _first_mismatch(actual[index], expected_item, f"{path}.{index}")  # type: ignore[index]
    return path


def validate_no_data_preflight(report: object, manifest: object) -> dict:
    """Reject any preflight result that differs from a deterministic rebuild."""

    _require(isinstance(report, dict), "historical corpus preflight report must be an object")
    expected = build_no_data_preflight(manifest)
    _require(report == expected, f"historical corpus preflight report differs at {_first_mismatch(report, expected)}")
    return copy.deepcopy(report)


def serialize_no_data_preflight(report: dict) -> str:
    """Return deterministic compact JSON for a validated or newly built report."""

    return json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":"))

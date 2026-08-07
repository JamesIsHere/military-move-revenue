"""Verify intake, expected-label, and manifest controls as one immutable handoff."""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime

from rules.historical_corpus_manifest import (
    OPERATIONAL,
    SYNTHETIC_TEMPLATE,
    HistoricalCorpusManifestError,
    evaluate_historical_corpus_manifest,
)
from rules.historical_expected_label import (
    HistoricalExpectedLabelError,
    validate_historical_expected_label_control,
)
from rules.historical_intake import HistoricalIntakeError, validate_historical_intake_envelope


HANDOFF_SCHEMA_VERSION = "historical-control-handoff.v1"
HANDOFF_POLICY_ID = "HISTORICAL-CONTROL-HANDOFF-V1"
HANDOFF_POLICY_VERSION = "2026-08-07.1"
SCOPE_CODE = "DOMESTIC_DP3_TSP_GOV_POST_AUDIT"

HANDOFF_POLICY_PROVENANCE = (
    {
        "source_id": "GOAL-RATIFIED-2026-08-03",
        "document_path": "goal.md",
        "document_version": "ratified 2026-08-03",
        "effective_period": "2026-08-03/open",
        "locator": "Completion verifier; Completion proof; Sensitive-data boundary",
        "retrieval_date": "2026-08-07",
        "interpretation_status": "ratified_internal_policy",
    },
    {
        "source_id": "HISTORICAL-CONTROL-HANDOFF-POLICY",
        "document_path": "docs/historical-control-handoff.md",
        "document_version": HANDOFF_POLICY_VERSION,
        "effective_period": "2026-08-07/open",
        "locator": "Cross-control contract through readiness and promotion boundaries",
        "retrieval_date": "2026-08-07",
        "interpretation_status": "approved_internal_implementation_policy",
    },
)


class HistoricalControlHandoffError(ValueError):
    """Raised when linked historical controls do not form a safe handoff."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HistoricalControlHandoffError(message)


def _instant(value: object, label: str) -> datetime:
    _require(isinstance(value, str) and value, f"{label} must be an ISO instant")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HistoricalControlHandoffError(f"{label} must be an ISO instant") from exc
    _require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return parsed


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _synthetic_blockers(remaining: int) -> list[dict]:
    definitions = (
        (
            "SYNTHETIC_INTAKE_NOT_AUTHORIZATION",
            "The linked intake envelope is a synthetic contract template, not written authorization.",
            "HISTORICAL-INTAKE-CONTROL-POLICY",
            "2026-08-07.1",
            "HISTORICAL-INTAKE-CONTROL-V1 synthetic promotion boundary",
            "approved_internal_implementation_policy",
        ),
        (
            "SYNTHETIC_LABEL_NOT_EXPERT_APPROVAL",
            "The linked expected-label control has no outcome artifact or expert approval.",
            "HISTORICAL-EXPECTED-LABEL-CONTROL-POLICY",
            "2026-08-07.1",
            "HISTORICAL-EXPECTED-LABEL-CONTROL-V1 synthetic promotion boundary",
            "approved_internal_implementation_policy",
        ),
        (
            "SYNTHETIC_MANIFEST_NONCOUNTING",
            "The current manifest entry is explicitly synthetic and non-counting.",
            "HISTORICAL-CORPUS-MANIFEST-POLICY",
            "2026-08-07.1",
            "HISTORICAL-CORPUS-MANIFEST-V1 synthetic mode",
            "approved_internal_implementation_policy",
        ),
        (
            "AUTHORIZED_HISTORICAL_CASES_REQUIRED",
            f"{remaining} passing authorized historical cases remain required.",
            "GOAL-RATIFIED-2026-08-03",
            "ratified 2026-08-03",
            "goal.md Completion verifier and Completion proof",
            "ratified_internal_policy",
        ),
    )
    return [
        {
            "sequence": index,
            "code": code,
            "status": "BLOCKING",
            "description": description,
            "provenance": [
                {
                    "source_id": source_id,
                    "document_version": document_version,
                    "effective_period": "2026-08-03/open" if source_id == "GOAL-RATIFIED-2026-08-03" else "2026-08-07/open",
                    "locator": locator,
                    "retrieval_date": "2026-08-07",
                    "interpretation_status": interpretation_status,
                }
            ],
        }
        for index, (code, description, source_id, document_version, locator, interpretation_status) in enumerate(
            definitions,
            start=1,
        )
    ]


def _operational_blockers(entry_status: str) -> list[dict]:
    if entry_status == "READY_FOR_ACCEPTANCE_EXECUTION":
        return []
    return [
        {
            "sequence": 1,
            "code": "EXPLICIT_EXECUTION_RELEASE_REQUIRED",
            "status": "BLOCKING",
            "description": "Control links are verified, but the current manifest entry has not been released for acceptance execution.",
            "provenance": [
                {
                    "source_id": "HISTORICAL-CONTROL-HANDOFF-POLICY",
                    "document_version": HANDOFF_POLICY_VERSION,
                    "effective_period": "2026-08-07/open",
                    "locator": "Operational readiness states",
                    "retrieval_date": "2026-08-07",
                    "interpretation_status": "approved_internal_implementation_policy",
                }
            ],
        }
    ]


def build_historical_control_handoff(
    intake_envelope: object,
    expected_label_control: object,
    manifest: object,
    evaluated_at: object,
    *,
    allow_synthetic_template: bool = False,
) -> dict:
    """Build the canonical cross-control readiness result for one current case entry."""

    try:
        intake = validate_historical_intake_envelope(
            intake_envelope,
            evaluated_at,
            allow_synthetic_template=allow_synthetic_template,
        )
    except HistoricalIntakeError as exc:
        raise HistoricalControlHandoffError(f"handoff intake envelope rejected: {exc}") from exc
    try:
        label_control = validate_historical_expected_label_control(
            expected_label_control,
            evaluated_at,
            intake_envelope,
            allow_synthetic_template=allow_synthetic_template,
        )
    except HistoricalExpectedLabelError as exc:
        raise HistoricalControlHandoffError(f"handoff expected-label control rejected: {exc}") from exc
    try:
        manifest_evaluation = evaluate_historical_corpus_manifest(
            manifest,
            allow_synthetic_template=allow_synthetic_template,
        )
    except HistoricalCorpusManifestError as exc:
        raise HistoricalControlHandoffError(f"handoff manifest rejected: {exc}") from exc

    mode = intake["control_mode"]
    _require(label_control["control_mode"] == mode, "handoff label-control mode differs from intake mode")
    _require(manifest_evaluation["control_mode"] == mode, "handoff manifest mode differs from intake mode")
    _require(_instant(evaluated_at, "handoff evaluated_at") == _instant(manifest_evaluation["as_of_at"], "manifest cutoff"), "handoff evaluation time differs from manifest cutoff")

    case_reference_id = intake["case_reference_id"]
    current_entries = [
        entry for entry in manifest_evaluation["current_entries"] if entry["case_reference_id"] == case_reference_id
    ]
    _require(len(current_entries) == 1, "handoff requires exactly one current manifest entry for the intake case")
    entry = current_entries[0]
    intake_hash = _canonical_sha256(intake)
    label_control_hash = _canonical_sha256(label_control)
    manifest_hash = _canonical_sha256(manifest)
    label_artifact = label_control["label_artifact"]
    intake_link = label_control["intake_link"]

    _require(entry["intake_envelope_id"] == intake["envelope_id"], "handoff manifest/intake envelope ID mismatch")
    _require(entry["intake_envelope_sha256"] == intake_hash, "handoff manifest/intake envelope hash mismatch")
    _require(entry["sanitized_bundle_sha256"] == intake["sanitization"]["bundle_sha256"], "handoff manifest/intake bundle hash mismatch")
    _require(intake_link["envelope_id"] == entry["intake_envelope_id"], "handoff label/manifest intake ID mismatch")
    _require(intake_link["envelope_sha256"] == entry["intake_envelope_sha256"], "handoff label/manifest intake hash mismatch")
    _require(intake_link["sanitized_bundle_sha256"] == entry["sanitized_bundle_sha256"], "handoff label/manifest bundle hash mismatch")
    _require(entry["expected_label_id"] == label_artifact["label_id"], "handoff manifest/label ID mismatch")
    _require(entry["expected_label_sha256"] == label_artifact["label_sha256"], "handoff manifest/label hash mismatch")
    _require(
        _instant(label_control["approval"]["approved_at"], "label approval time")
        <= _instant(entry["registered_at"], "manifest registration time"),
        "handoff manifest entry was registered before expected-label approval",
    )
    _require(entry["acceptance_report_id"] is None, "pre-execution handoff cannot use an entry with an acceptance report")

    summary = manifest_evaluation["summary"]
    remaining = summary["remaining_passing_historical_case_count"]
    if mode == SYNTHETIC_TEMPLATE:
        _require(entry["status"] == "SYNTHETIC_TEMPLATE_NONCOUNTING", "synthetic handoff manifest status mismatch")
        status = "SYNTHETIC_LINKS_VERIFIED_NON_OPERATIONAL"
        operational_ready = False
        execution_authorized = False
        blockers = _synthetic_blockers(remaining)
        headline = "Links verified - synthetic controls cannot authorize execution"
        primary_action = "Obtain written authorization and approved sanitized case controls"
    else:
        _require(
            entry["status"] in {"REGISTERED_CONTROLS_VERIFIED", "READY_FOR_ACCEPTANCE_EXECUTION"},
            "operational handoff requires a current pre-execution manifest status",
        )
        execution_authorized = entry["status"] == "READY_FOR_ACCEPTANCE_EXECUTION"
        operational_ready = execution_authorized
        status = "READY_FOR_ACCEPTANCE_EXECUTION" if execution_authorized else "CONTROLS_VERIFIED_PENDING_EXECUTION_RELEASE"
        blockers = _operational_blockers(entry["status"])
        headline = "Ready for acceptance execution" if execution_authorized else "Controls verified - execution release required"
        primary_action = "Run deterministic historical acceptance" if execution_authorized else "Record explicit execution release"

    return {
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "policy": {
            "id": HANDOFF_POLICY_ID,
            "version": HANDOFF_POLICY_VERSION,
            "effective_period": "2026-08-07/open",
        },
        "handoff_id": f"{entry['entry_id']}:CONTROL-HANDOFF:{evaluated_at}",
        "evaluated_at": evaluated_at,
        "control_mode": mode,
        "scope_code": SCOPE_CODE,
        "status": status,
        "linkage_status": "VERIFIED",
        "operational_handoff_ready": operational_ready,
        "acceptance_execution_authorized": execution_authorized,
        "counts_toward_required_25": False,
        "contains_case_content": False,
        "contains_outcome_content": False,
        "generated_from": {
            "intake_envelope_sha256": intake_hash,
            "expected_label_control_sha256": label_control_hash,
            "manifest_sha256": manifest_hash,
        },
        "linked_controls": {
            "case_reference_id": case_reference_id,
            "intake_envelope_id": intake["envelope_id"],
            "sanitized_bundle_sha256": intake["sanitization"]["bundle_sha256"],
            "expected_label_control_id": label_control["envelope_id"],
            "expected_label_id": label_artifact["label_id"],
            "expected_label_sha256": label_artifact["label_sha256"],
            "manifest_id": manifest_evaluation["manifest_id"],
            "manifest_entry_id": entry["entry_id"],
            "manifest_entry_version": entry["entry_version"],
            "manifest_entry_status": entry["status"],
        },
        "progress": {
            "passing_historical_case_count": summary["passing_current_case_count"],
            "required_historical_case_count": summary["required_historical_case_count"],
            "remaining_passing_historical_case_count": remaining,
            "completion_status": summary["completion_status"],
        },
        "display": {
            "title": "Historical control handoff",
            "headline": headline,
            "progress_label": f"{summary['passing_current_case_count']} of {summary['required_historical_case_count']} passing historical cases",
            "primary_action": primary_action,
            "blocker_count": len(blockers),
        },
        "blockers": blockers,
        "provenance": [
            {key: value for key, value in reference.items() if key != "document_path"}
            for reference in HANDOFF_POLICY_PROVENANCE
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
            return f"{path}.{sorted(actual_keys ^ expected_keys)[0]}"
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


def validate_historical_control_handoff(
    report: object,
    intake_envelope: object,
    expected_label_control: object,
    manifest: object,
    evaluated_at: object,
    *,
    allow_synthetic_template: bool = False,
) -> dict:
    """Reject a handoff report that differs from its deterministic rebuild."""

    _require(isinstance(report, dict), "historical control handoff report must be an object")
    expected = build_historical_control_handoff(
        intake_envelope,
        expected_label_control,
        manifest,
        evaluated_at,
        allow_synthetic_template=allow_synthetic_template,
    )
    _require(report == expected, f"historical control handoff report differs at {_first_mismatch(report, expected)}")
    return copy.deepcopy(report)


def serialize_historical_control_handoff(report: dict) -> str:
    """Return deterministic compact JSON for a built or validated handoff report."""

    return json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":"))

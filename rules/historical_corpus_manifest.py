"""Validate a metadata-only historical corpus manifest and derive readiness counts."""

from __future__ import annotations

import copy
import json
import re
from datetime import date, datetime


MANIFEST_SCHEMA_VERSION = "historical-corpus-manifest.v1"
EVALUATION_SCHEMA_VERSION = "historical-corpus-manifest-evaluation.v1"
MANIFEST_POLICY_ID = "HISTORICAL-CORPUS-MANIFEST-V1"
MANIFEST_POLICY_VERSION = "2026-08-07.1"
SCOPE_CODE = "DOMESTIC_DP3_TSP_GOV_POST_AUDIT"
REQUIRED_HISTORICAL_CASE_COUNT = 25

EMPTY_AWAITING_AUTHORIZATION = "EMPTY_AWAITING_AUTHORIZATION"
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
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
OPERATIONAL_STATUSES = {
    "REGISTERED_CONTROLS_VERIFIED",
    "READY_FOR_ACCEPTANCE_EXECUTION",
    "EXECUTED_PASS",
    "EXECUTED_FAIL",
    "BLOCKED_REVIEW",
}

MANIFEST_POLICY_PROVENANCE = (
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
        "source_id": "HISTORICAL-CORPUS-MANIFEST-POLICY",
        "document_path": "docs/historical-corpus-onboarding.md",
        "document_version": MANIFEST_POLICY_VERSION,
        "effective_period": "2026-08-07/open",
        "locator": "Manifest contract and no-data onboarding runbook",
        "retrieval_date": "2026-08-07",
        "interpretation_status": "approved_internal_implementation_policy",
    },
)


class HistoricalCorpusManifestError(ValueError):
    """Raised when corpus-manifest metadata is incomplete or unsafe."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HistoricalCorpusManifestError(message)


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
        raise HistoricalCorpusManifestError(f"{label} must be an ISO instant") from exc
    _require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return parsed


def _date(value: object, label: str) -> date:
    _require(isinstance(value, str) and value, f"{label} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HistoricalCorpusManifestError(f"{label} must be an ISO date") from exc


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


def _validate_hash(value: object, label: str) -> str:
    _require(isinstance(value, str) and SHA256_RE.fullmatch(value) is not None, f"{label} must be a lowercase SHA-256")
    return value


def _validate_entry(entry: object, manifest_mode: str, as_of_at: datetime) -> dict:
    value = _require_exact_keys(
        entry,
        {
            "entry_id",
            "case_reference_id",
            "entry_version",
            "supersedes_entry_id",
            "entry_mode",
            "status",
            "case_data_status",
            "scope_code",
            "contains_case_content",
            "intake_envelope_id",
            "intake_envelope_sha256",
            "sanitized_bundle_sha256",
            "expected_label_id",
            "expected_label_sha256",
            "acceptance_report_id",
            "acceptance_report_sha256",
            "registered_at",
            "provenance",
        },
        "historical corpus entry",
    )
    for field in ("entry_id", "case_reference_id", "intake_envelope_id", "expected_label_id"):
        _nonempty(value[field], f"historical corpus entry {field}")
    _require(type(value["entry_version"]) is int and value["entry_version"] >= 1, "historical corpus entry_version must be a positive integer")
    supersedes = value["supersedes_entry_id"]
    _require(supersedes is None or isinstance(supersedes, str) and supersedes, "historical corpus supersedes_entry_id is invalid")
    _require(value["entry_mode"] == manifest_mode, "historical corpus entry mode differs from manifest mode")
    _require(value["scope_code"] == SCOPE_CODE, "historical corpus entry scope mismatch")
    _require(value["contains_case_content"] is False, "historical corpus entry must remain metadata-only")
    _validate_hash(value["intake_envelope_sha256"], "historical corpus intake-envelope hash")
    _validate_hash(value["sanitized_bundle_sha256"], "historical corpus sanitized-bundle hash")
    _validate_hash(value["expected_label_sha256"], "historical corpus expected-label hash")
    report_id = value["acceptance_report_id"]
    report_hash = value["acceptance_report_sha256"]
    _require(
        (report_id is None and report_hash is None)
        or (isinstance(report_id, str) and report_id and isinstance(report_hash, str)),
        "historical corpus acceptance-report ID/hash must both be absent or present",
    )
    if report_hash is not None:
        _validate_hash(report_hash, "historical corpus acceptance-report hash")
    registered_at = _instant(value["registered_at"], "historical corpus entry registered_at")
    _require(registered_at <= as_of_at, "historical corpus entry is registered after the manifest cutoff")
    _validate_provenance(value["provenance"], "historical corpus entry")

    if manifest_mode == SYNTHETIC_TEMPLATE:
        _require(value["status"] == "SYNTHETIC_TEMPLATE_NONCOUNTING", "synthetic corpus entry status mismatch")
        _require(value["case_data_status"] == "SYNTHETIC_METADATA_ONLY", "synthetic corpus entry data_status mismatch")
        _require(report_id is None, "synthetic corpus entry cannot link an acceptance report")
        for field in ("entry_id", "case_reference_id", "intake_envelope_id", "expected_label_id"):
            _require(value[field].startswith("SYNTHETIC-"), f"synthetic corpus entry {field} is not explicitly synthetic")
    elif manifest_mode == OPERATIONAL:
        _require(value["status"] in OPERATIONAL_STATUSES, "operational corpus entry status is invalid")
        _require(value["case_data_status"] == "AUTHORIZED_SANITIZED", "operational corpus entry data_status mismatch")
        if value["status"] in {"EXECUTED_PASS", "EXECUTED_FAIL", "BLOCKED_REVIEW"}:
            _require(report_id is not None, "executed corpus status requires an acceptance-report link")
        else:
            _require(report_id is None, "unexecuted corpus status cannot link an acceptance report")
    else:
        raise HistoricalCorpusManifestError("empty corpus manifest cannot contain entries")
    return copy.deepcopy(value)


def evaluate_historical_corpus_manifest(manifest: object, *, allow_synthetic_template: bool = False) -> dict:
    """Validate manifest metadata and derive all corpus and completion counts."""

    value = _require_exact_keys(
        manifest,
        {
            "schema_version",
            "policy_version",
            "manifest_id",
            "control_mode",
            "scope_code",
            "data_status",
            "contains_case_content",
            "real_data_ingest_authorized",
            "required_historical_case_count",
            "declared_entry_count",
            "as_of_at",
            "entries",
            "provenance",
        },
        "historical corpus manifest",
    )
    _require(value["schema_version"] == MANIFEST_SCHEMA_VERSION, "historical corpus manifest schema mismatch")
    _require(value["policy_version"] == MANIFEST_POLICY_VERSION, "historical corpus manifest policy mismatch")
    _nonempty(value["manifest_id"], "historical corpus manifest_id")
    mode = value["control_mode"]
    _require(mode in {EMPTY_AWAITING_AUTHORIZATION, SYNTHETIC_TEMPLATE, OPERATIONAL}, "historical corpus control mode is invalid")
    _require(mode != SYNTHETIC_TEMPLATE or allow_synthetic_template, "synthetic corpus manifest cannot authorize operational use")
    _require(value["scope_code"] == SCOPE_CODE, "historical corpus manifest scope mismatch")
    _require(value["contains_case_content"] is False, "historical corpus manifest must remain metadata-only")
    _require(value["required_historical_case_count"] == REQUIRED_HISTORICAL_CASE_COUNT, "historical corpus required-case count mismatch")
    _require(type(value["declared_entry_count"]) is int and value["declared_entry_count"] >= 0, "historical corpus declared_entry_count is invalid")
    as_of_at = _instant(value["as_of_at"], "historical corpus as_of_at")
    _validate_provenance(value["provenance"], "historical corpus manifest")
    entries = value["entries"]
    _require(isinstance(entries, list), "historical corpus entries must be a list")
    _require(value["declared_entry_count"] == len(entries), "historical corpus declared entry count drift")

    if mode == EMPTY_AWAITING_AUTHORIZATION:
        _require(value["data_status"] == "METADATA_ONLY_NO_CASES", "empty corpus data_status mismatch")
        _require(value["real_data_ingest_authorized"] is False, "empty corpus cannot authorize real-data ingest")
        _require(not entries, "empty corpus manifest cannot contain entries")
    elif mode == SYNTHETIC_TEMPLATE:
        _require(value["data_status"] == "SYNTHETIC_METADATA_ONLY", "synthetic corpus data_status mismatch")
        _require(value["real_data_ingest_authorized"] is False, "synthetic corpus cannot authorize real-data ingest")
        _require(value["manifest_id"].startswith("SYNTHETIC-"), "synthetic corpus manifest_id is not explicitly synthetic")
    else:
        _require(value["data_status"] == "AUTHORIZED_SANITIZED_HISTORICAL_METADATA", "operational corpus data_status mismatch")
        _require(value["real_data_ingest_authorized"] is True, "operational corpus lacks real-data ingest authority")

    validated_entries = [_validate_entry(entry, mode, as_of_at) for entry in entries]
    validated_entries.sort(key=lambda entry: (entry["case_reference_id"], entry["entry_version"], entry["entry_id"]))
    _require(entries == validated_entries, "historical corpus entries are not canonically ordered")

    entry_ids: dict[str, dict] = {}
    case_versions: dict[tuple[str, int], dict] = {}
    hashes_by_case: dict[str, dict[str, str]] = {
        "intake": {},
        "bundle": {},
        "label": {},
        "report": {},
    }
    label_ids_by_case: dict[str, str] = {}
    report_ids_by_case: dict[str, str] = {}
    for entry in validated_entries:
        entry_id = entry["entry_id"]
        case_id = entry["case_reference_id"]
        version = entry["entry_version"]
        _require(entry_id not in entry_ids, f"duplicate historical corpus entry_id {entry_id}")
        _require((case_id, version) not in case_versions, f"duplicate historical corpus case version {case_id} v{version}")
        entry_ids[entry_id] = entry
        case_versions[(case_id, version)] = entry
        for kind, field in (
            ("intake", "intake_envelope_sha256"),
            ("bundle", "sanitized_bundle_sha256"),
            ("label", "expected_label_sha256"),
            ("report", "acceptance_report_sha256"),
        ):
            digest = entry[field]
            if digest is None:
                continue
            prior_case = hashes_by_case[kind].get(digest)
            _require(prior_case in {None, case_id}, f"duplicate historical corpus {kind} hash across cases")
            hashes_by_case[kind][digest] = case_id
        prior_label_case = label_ids_by_case.get(entry["expected_label_id"])
        _require(prior_label_case in {None, case_id}, "duplicate historical corpus expected-label id across cases")
        label_ids_by_case[entry["expected_label_id"]] = case_id
        if entry["acceptance_report_id"] is not None:
            prior_report_case = report_ids_by_case.get(entry["acceptance_report_id"])
            _require(prior_report_case in {None, case_id}, "duplicate historical corpus acceptance-report id across cases")
            report_ids_by_case[entry["acceptance_report_id"]] = case_id

    by_case: dict[str, list[dict]] = {}
    for entry in validated_entries:
        by_case.setdefault(entry["case_reference_id"], []).append(entry)
    current_entries: list[dict] = []
    for case_id, versions in by_case.items():
        expected_versions = list(range(1, len(versions) + 1))
        actual_versions = [entry["entry_version"] for entry in versions]
        _require(actual_versions == expected_versions, f"historical corpus versions are not contiguous for {case_id}")
        for index, entry in enumerate(versions):
            if index == 0:
                _require(entry["supersedes_entry_id"] is None, f"historical corpus first version for {case_id} cannot supersede another entry")
            else:
                _require(
                    entry["supersedes_entry_id"] == versions[index - 1]["entry_id"],
                    f"historical corpus version for {case_id} does not directly supersede its predecessor",
                )
                _require(
                    _instant(versions[index - 1]["registered_at"], "historical corpus predecessor registered_at")
                    <= _instant(entry["registered_at"], "historical corpus successor registered_at"),
                    f"historical corpus registration chronology is invalid for {case_id}",
                )
        current_entries.append(versions[-1])

    passing = sum(entry["entry_mode"] == OPERATIONAL and entry["status"] == "EXECUTED_PASS" for entry in current_entries)
    failed = sum(entry["entry_mode"] == OPERATIONAL and entry["status"] == "EXECUTED_FAIL" for entry in current_entries)
    blocked = sum(entry["entry_mode"] == OPERATIONAL and entry["status"] == "BLOCKED_REVIEW" for entry in current_entries)
    pending = sum(
        entry["entry_mode"] == OPERATIONAL
        and entry["status"] in {"REGISTERED_CONTROLS_VERIFIED", "READY_FOR_ACCEPTANCE_EXECUTION"}
        for entry in current_entries
    )
    remaining = max(0, REQUIRED_HISTORICAL_CASE_COUNT - passing)
    completion_ready = mode == OPERATIONAL and passing >= REQUIRED_HISTORICAL_CASE_COUNT and not failed and not blocked and not pending
    return {
        "schema_version": EVALUATION_SCHEMA_VERSION,
        "manifest_policy": {
            "id": MANIFEST_POLICY_ID,
            "version": MANIFEST_POLICY_VERSION,
            "required_historical_case_count": REQUIRED_HISTORICAL_CASE_COUNT,
        },
        "manifest_id": value["manifest_id"],
        "control_mode": mode,
        "as_of_at": value["as_of_at"],
        "summary": {
            "registered_entry_version_count": len(validated_entries),
            "distinct_case_count": len(by_case),
            "current_case_count": len(current_entries),
            "passing_current_case_count": passing,
            "failed_current_case_count": failed,
            "blocked_current_case_count": blocked,
            "pending_current_case_count": pending,
            "required_historical_case_count": REQUIRED_HISTORICAL_CASE_COUNT,
            "remaining_passing_historical_case_count": remaining,
            "completion_status": "READY" if completion_ready else "NOT_READY",
        },
        "current_entries": sorted(copy.deepcopy(current_entries), key=lambda entry: entry["case_reference_id"]),
        "provenance": [dict(reference) for reference in MANIFEST_POLICY_PROVENANCE],
        "unresolved_assumptions": [],
    }


def serialize_historical_corpus_evaluation(evaluation: dict) -> str:
    """Return deterministic compact JSON for a previously built evaluation."""

    return json.dumps(evaluation, ensure_ascii=True, sort_keys=True, separators=(",", ":"))

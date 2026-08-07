#!/usr/bin/env python3
"""Validate the no-data historical corpus manifest and synthetic entry contract."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.historical_corpus_manifest import (  # noqa: E402
    EVALUATION_SCHEMA_VERSION,
    MANIFEST_POLICY_PROVENANCE,
    MANIFEST_POLICY_VERSION,
    HistoricalCorpusManifestError,
    evaluate_historical_corpus_manifest,
    serialize_historical_corpus_evaluation,
)
from rules.historical_intake import (  # noqa: E402
    validate_historical_intake_envelope,
)


FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "historical-acceptance"
EMPTY_MANIFEST_PATH = FIXTURE_ROOT / "historical-corpus-manifest.json"
CASES_PATH = FIXTURE_ROOT / "historical-corpus-manifest-cases.json"
INTAKE_CASES_PATH = FIXTURE_ROOT / "historical-intake-control-cases.json"


class ValidationError(ValueError):
    """Raised when an expected manifest-contract result is not observed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def reject_float(value: str) -> object:
    raise ValidationError(f"fixture contains binary floating-point value {value}")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle, parse_float=reject_float)
    require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain an object")
    return value


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def set_path(target: object, path: str, value: object) -> None:
    current = target
    parts = path.split(".")
    for part in parts[:-1]:
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]  # type: ignore[index]
    if isinstance(current, list):
        current[int(parts[-1])] = value
    else:
        current[parts[-1]] = value  # type: ignore[index]


def expect_rejection(candidate: dict, expected: str, label: str) -> None:
    try:
        evaluate_historical_corpus_manifest(candidate, allow_synthetic_template=True)
    except HistoricalCorpusManifestError as exc:
        require(expected in str(exc), f"{label} rejected for unexpected reason: {exc}")
        print(f"PASS {label} rejected")
        return
    raise ValidationError(f"{label} invalid corpus manifest was accepted")


def validate_policy_sources() -> None:
    for reference in MANIFEST_POLICY_PROVENANCE:
        path = ROOT / reference["document_path"]
        require(path.is_file(), f"manifest policy source is missing: {reference['document_path']}")
    policy = (ROOT / "docs" / "historical-corpus-onboarding.md").read_text(encoding="utf-8")
    require(f"Version: `{MANIFEST_POLICY_VERSION}`" in policy, "manifest policy version is not documented")
    require("cannot declare a passing count" in policy, "manifest policy lacks derived-count boundary")
    require("raw source never enters this workspace" in policy, "manifest policy lacks raw-source boundary")


def validate_empty_manifest(manifest: dict) -> None:
    evaluation = evaluate_historical_corpus_manifest(manifest)
    summary = evaluation["summary"]
    require(evaluation["schema_version"] == EVALUATION_SCHEMA_VERSION, "manifest evaluation schema mismatch")
    require(evaluation["control_mode"] == "EMPTY_AWAITING_AUTHORIZATION", "checked-in manifest is not empty-mode")
    require(summary["registered_entry_version_count"] == 0, "empty manifest registered an entry")
    require(summary["distinct_case_count"] == 0, "empty manifest registered a case")
    require(summary["current_case_count"] == 0, "empty manifest selected a current case")
    require(summary["passing_current_case_count"] == 0, "empty manifest produced a pass")
    require(summary["remaining_passing_historical_case_count"] == 25, "empty manifest remaining count changed")
    require(summary["completion_status"] == "NOT_READY", "empty manifest became completion-ready")
    require(evaluation["current_entries"] == [], "empty manifest emitted current entries")
    serialized = serialize_historical_corpus_evaluation(evaluation)
    require(serialized == serialize_historical_corpus_evaluation(json.loads(serialized)), "manifest serialization is unstable")
    print("PASS checked-in corpus manifest remains metadata-only at 0 passing cases with 25 remaining")


def validate_synthetic_template(suite: dict, intake_suite: dict) -> dict:
    template = suite.get("valid_template")
    require(isinstance(template, dict), "valid_template must be an object")
    evaluation = evaluate_historical_corpus_manifest(template, allow_synthetic_template=True)
    summary = evaluation["summary"]
    require(summary["registered_entry_version_count"] == 2, "synthetic manifest version count changed")
    require(summary["distinct_case_count"] == 1, "synthetic manifest case count changed")
    require(summary["current_case_count"] == 1, "synthetic manifest current count changed")
    require(summary["passing_current_case_count"] == 0, "synthetic manifest contributed a pass")
    require(summary["remaining_passing_historical_case_count"] == 25, "synthetic manifest reduced the remaining count")
    require(summary["completion_status"] == "NOT_READY", "synthetic manifest became completion-ready")
    require(evaluation["current_entries"][0]["entry_version"] == 2, "synthetic manifest did not select the superseding version")

    intake_template = intake_suite["valid_template"]
    validated_intake = validate_historical_intake_envelope(
        intake_template,
        intake_suite["evaluated_at"],
        allow_synthetic_template=True,
    )
    intake_hash = canonical_sha256(validated_intake)
    for entry in template["entries"]:
        require(entry["case_reference_id"] == validated_intake["case_reference_id"], "manifest/intake case link mismatch")
        require(entry["intake_envelope_id"] == validated_intake["envelope_id"], "manifest/intake envelope ID mismatch")
        require(entry["intake_envelope_sha256"] == intake_hash, "manifest/intake envelope hash mismatch")
        require(
            entry["sanitized_bundle_sha256"] == validated_intake["sanitization"]["bundle_sha256"],
            "manifest/intake sanitized-bundle hash mismatch",
        )
    require(validated_intake["approval_separation"]["roles_distinct"] is True, "linked intake lacks role separation")
    require(validated_intake["approval_separation"]["ai_attestation_used"] is False, "linked intake uses AI attestation")
    print("PASS synthetic manifest links its validated intake envelope, bundle hash, and separated approval roles")

    try:
        evaluate_historical_corpus_manifest(template)
    except HistoricalCorpusManifestError as exc:
        require("cannot authorize operational use" in str(exc), "synthetic promotion gate changed")
        print("PASS synthetic corpus template rejected by the operational gate")
    else:
        raise ValidationError("synthetic corpus template passed the operational gate")
    return template


def validate_negative_mutations(suite: dict) -> int:
    template = suite["valid_template"]
    cases = suite.get("invalid_mutations")
    require(isinstance(cases, list) and cases, "invalid_mutations must be a nonempty list")
    identifiers: set[str] = set()
    for case in cases:
        require(isinstance(case, dict), "manifest mutation must be an object")
        case_id = case.get("id")
        require(isinstance(case_id, str) and case_id and case_id not in identifiers, "manifest mutation id is invalid")
        identifiers.add(case_id)
        candidate = copy.deepcopy(template)
        set_path(candidate, case["path"], copy.deepcopy(case["value"]))
        expect_rejection(candidate, case["expected_error_contains"], case_id)
    return len(cases)


def validate_structural_rejections(template: dict, empty_manifest: dict) -> None:
    extra_count = copy.deepcopy(template)
    extra_count["passing_case_count"] = 25
    expect_rejection(extra_count, "fields mismatch", "caller-declared passing count")

    extra_content = copy.deepcopy(template)
    extra_content["entries"][0]["shipment_id"] = "PROHIBITED-CONTENT-FIELD"
    expect_rejection(extra_content, "fields mismatch", "extra case-content field")

    synthetic_report = copy.deepcopy(template)
    synthetic_report["entries"][1]["acceptance_report_id"] = "SYNTHETIC-ACCEPTANCE-REPORT-001"
    synthetic_report["entries"][1]["acceptance_report_sha256"] = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    expect_rejection(synthetic_report, "cannot link an acceptance report", "synthetic acceptance-report link")

    reordered = copy.deepcopy(template)
    reordered["entries"].reverse()
    expect_rejection(reordered, "not canonically ordered", "noncanonical entry order")

    populated_empty = copy.deepcopy(empty_manifest)
    populated_empty["entries"] = [copy.deepcopy(template["entries"][0])]
    populated_empty["declared_entry_count"] = 1
    expect_rejection(populated_empty, "empty corpus manifest cannot contain entries", "populated empty-mode manifest")

    cross_case_hash = copy.deepcopy(template)
    other = copy.deepcopy(template["entries"][1])
    other["entry_id"] = "SYNTHETIC-CORPUS-ENTRY-002-V1"
    other["case_reference_id"] = "SYNTHETIC-OPAQUE-CASE-REFERENCE-002"
    other["entry_version"] = 1
    other["supersedes_entry_id"] = None
    other["intake_envelope_id"] = "SYNTHETIC-INTAKE-CONTROL-002"
    other["expected_label_id"] = "SYNTHETIC-EXPECTED-LABEL-002"
    cross_case_hash["entries"].append(other)
    cross_case_hash["declared_entry_count"] = 3
    expect_rejection(cross_case_hash, "hash across cases", "cross-case artifact-hash reuse")

    cross_case_label = copy.deepcopy(cross_case_hash)
    cross_case_label["entries"][2]["intake_envelope_sha256"] = "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
    cross_case_label["entries"][2]["sanitized_bundle_sha256"] = "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    cross_case_label["entries"][2]["expected_label_sha256"] = "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    cross_case_label["entries"][2]["expected_label_id"] = "SYNTHETIC-EXPECTED-LABEL-001"
    expect_rejection(cross_case_label, "expected-label id across cases", "cross-case expected-label reuse")


def main() -> int:
    try:
        validate_policy_sources()
        empty_manifest = load_json(EMPTY_MANIFEST_PATH)
        suite = load_json(CASES_PATH)
        intake_suite = load_json(INTAKE_CASES_PATH)
        require(
            suite.get("fixture_set") == "SYNTHETIC_METADATA_ONLY_HISTORICAL_CORPUS_MANIFEST",
            "historical corpus fixture set is not labeled synthetic metadata-only",
        )
        validate_empty_manifest(empty_manifest)
        template = validate_synthetic_template(suite, intake_suite)
        negative_count = validate_negative_mutations(suite)
        validate_structural_rejections(template, empty_manifest)
        print(
            f"PASS historical corpus manifest: 1 immutable empty manifest, 1 non-counting two-version "
            f"synthetic chain, {negative_count} negative mutations, and 8 structural/linkage gates"
        )
        return 0
    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        HistoricalCorpusManifestError,
        ValidationError,
    ) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

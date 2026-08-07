#!/usr/bin/env python3
"""Validate the deterministic cross-control historical handoff report."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.historical_control_handoff import (  # noqa: E402
    HANDOFF_POLICY_PROVENANCE,
    HANDOFF_POLICY_VERSION,
    HANDOFF_SCHEMA_VERSION,
    HistoricalControlHandoffError,
    build_historical_control_handoff,
    serialize_historical_control_handoff,
    validate_historical_control_handoff,
)


FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "historical-acceptance"
CASES_PATH = FIXTURE_ROOT / "historical-control-handoff-cases.json"
INTAKE_CASES_PATH = FIXTURE_ROOT / "historical-intake-control-cases.json"
LABEL_CASES_PATH = FIXTURE_ROOT / "historical-expected-label-control-cases.json"
MANIFEST_CASES_PATH = FIXTURE_ROOT / "historical-corpus-manifest-cases.json"
EMPTY_MANIFEST_PATH = FIXTURE_ROOT / "historical-corpus-manifest.json"


class ValidationError(ValueError):
    """Raised when an expected handoff result is not observed."""


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


def expect_report_rejection(
    candidate: dict,
    intake: dict,
    label: dict,
    manifest: dict,
    evaluated_at: str,
    expected: str,
    name: str,
) -> None:
    try:
        validate_historical_control_handoff(
            candidate,
            intake,
            label,
            manifest,
            evaluated_at,
            allow_synthetic_template=True,
        )
    except HistoricalControlHandoffError as exc:
        require(expected in str(exc), f"{name} rejected for unexpected reason: {exc}")
        print(f"PASS {name} rejected")
        return
    raise ValidationError(f"{name} invalid handoff report was accepted")


def expect_input_rejection(
    intake: dict,
    label: dict,
    manifest: dict,
    evaluated_at: str,
    expected: str,
    name: str,
) -> None:
    try:
        build_historical_control_handoff(
            intake,
            label,
            manifest,
            evaluated_at,
            allow_synthetic_template=True,
        )
    except HistoricalControlHandoffError as exc:
        require(expected in str(exc), f"{name} rejected for unexpected reason: {exc}")
        print(f"PASS {name} rejected")
        return
    raise ValidationError(f"{name} unsafe handoff inputs were accepted")


def validate_policy_sources() -> None:
    for reference in HANDOFF_POLICY_PROVENANCE:
        path = ROOT / reference["document_path"]
        require(path.is_file(), f"handoff policy source is missing: {reference['document_path']}")
    policy = (ROOT / "docs" / "historical-control-handoff.md").read_text(encoding="utf-8")
    require(f"Version: `{HANDOFF_POLICY_VERSION}`" in policy, "handoff policy version is not documented")
    require("structurally correct links are not evidence" in policy, "handoff policy lacks synthetic-authority boundary")
    require("must not" in policy, "handoff policy lacks interface override boundary")
    require("No positive operational fixture" in policy, "handoff policy lacks operational-fixture boundary")


def validate_canonical_report(
    suite: dict,
    intake: dict,
    label: dict,
    manifest: dict,
    evaluated_at: str,
) -> dict:
    report = build_historical_control_handoff(
        intake,
        label,
        manifest,
        evaluated_at,
        allow_synthetic_template=True,
    )
    require(
        validate_historical_control_handoff(
            report,
            intake,
            label,
            manifest,
            evaluated_at,
            allow_synthetic_template=True,
        )
        == report,
        "canonical handoff projection changed",
    )
    require(report["schema_version"] == HANDOFF_SCHEMA_VERSION, "handoff schema mismatch")
    require(report["status"] == suite["expected_status"], "synthetic handoff status changed")
    require(report["linkage_status"] == "VERIFIED", "synthetic handoff links are not verified")
    require(report["operational_handoff_ready"] is False, "synthetic handoff became operationally ready")
    require(report["acceptance_execution_authorized"] is False, "synthetic handoff authorized execution")
    require(report["counts_toward_required_25"] is False, "synthetic handoff became count-eligible")
    require(report["contains_case_content"] is False, "synthetic handoff contains case content")
    require(report["contains_outcome_content"] is False, "synthetic handoff contains outcome content")
    require(report["progress"] == suite["expected_progress"], "synthetic handoff progress changed")
    require(
        [blocker["code"] for blocker in report["blockers"]] == suite["expected_blocker_codes"],
        "synthetic handoff blocker catalog or order changed",
    )
    require(report["display"]["blocker_count"] == 4, "synthetic handoff display blocker count changed")
    serialized = serialize_historical_control_handoff(report)
    require(serialized == serialize_historical_control_handoff(json.loads(serialized)), "handoff serialization is unstable")
    print("PASS canonical synthetic handoff verifies all links while remaining non-operational and non-counting")

    try:
        build_historical_control_handoff(intake, label, manifest, evaluated_at)
    except HistoricalControlHandoffError as exc:
        require("cannot authorize operational use" in str(exc), "synthetic handoff promotion gate changed")
        print("PASS synthetic control handoff rejected by operational gate")
    else:
        raise ValidationError("synthetic control handoff passed the operational gate")
    return report


def validate_tamper_mutations(
    report: dict,
    suite: dict,
    intake: dict,
    label: dict,
    manifest: dict,
    evaluated_at: str,
) -> int:
    cases = suite.get("tamper_mutations")
    require(isinstance(cases, list) and cases, "tamper_mutations must be a nonempty list")
    identifiers: set[str] = set()
    for case in cases:
        require(isinstance(case, dict), "handoff tamper case must be an object")
        case_id = case.get("id")
        require(isinstance(case_id, str) and case_id and case_id not in identifiers, "handoff tamper id is invalid")
        identifiers.add(case_id)
        candidate = copy.deepcopy(report)
        set_path(candidate, case["path"], copy.deepcopy(case["value"]))
        expect_report_rejection(
            candidate,
            intake,
            label,
            manifest,
            evaluated_at,
            case["expected_error_contains"],
            case_id,
        )
    return len(cases)


def validate_report_structural_gates(
    report: dict,
    intake: dict,
    label: dict,
    manifest: dict,
    evaluated_at: str,
) -> None:
    extra = copy.deepcopy(report)
    extra["override_authorization"] = True
    expect_report_rejection(extra, intake, label, manifest, evaluated_at, "$.override_authorization", "caller authorization override")

    removed = copy.deepcopy(report)
    removed["blockers"].pop()
    expect_report_rejection(removed, intake, label, manifest, evaluated_at, "$.blockers.length", "removed handoff blocker")

    reordered = copy.deepcopy(report)
    reordered["blockers"][0], reordered["blockers"][1] = reordered["blockers"][1], reordered["blockers"][0]
    expect_report_rejection(reordered, intake, label, manifest, evaluated_at, "$.blockers.0", "reordered handoff blockers")


def validate_input_gates(
    intake: dict,
    label: dict,
    manifest: dict,
    empty_manifest: dict,
    evaluated_at: str,
) -> None:
    wrong_intake_hash = copy.deepcopy(manifest)
    wrong_intake_hash["entries"][1]["intake_envelope_sha256"] = "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
    expect_input_rejection(intake, label, wrong_intake_hash, evaluated_at, "manifest/intake envelope hash mismatch", "manifest intake-hash drift")

    wrong_bundle_hash = copy.deepcopy(manifest)
    wrong_bundle_hash["entries"][1]["sanitized_bundle_sha256"] = "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
    expect_input_rejection(intake, label, wrong_bundle_hash, evaluated_at, "manifest/intake bundle hash mismatch", "manifest bundle-hash drift")

    wrong_label_id = copy.deepcopy(manifest)
    wrong_label_id["entries"][1]["expected_label_id"] = "SYNTHETIC-EXPECTED-LABEL-999"
    expect_input_rejection(intake, label, wrong_label_id, evaluated_at, "manifest/label ID mismatch", "manifest label-ID drift")

    wrong_label_hash = copy.deepcopy(manifest)
    wrong_label_hash["entries"][1]["expected_label_sha256"] = "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
    expect_input_rejection(intake, label, wrong_label_hash, evaluated_at, "manifest/label hash mismatch", "manifest label-hash drift")

    early_registration = copy.deepcopy(manifest)
    early_registration["entries"][0]["registered_at"] = "2026-08-07T09:00:00Z"
    early_registration["entries"][1]["registered_at"] = "2026-08-07T09:59:59Z"
    expect_input_rejection(intake, label, early_registration, evaluated_at, "registered before expected-label approval", "pre-approval manifest registration")

    expect_input_rejection(intake, label, manifest, "2026-08-07T11:59:59Z", "evaluation time differs", "manifest-cutoff mismatch")
    expect_input_rejection(intake, label, empty_manifest, evaluated_at, "manifest mode differs", "empty manifest in linked handoff")

    unsafe_intake = copy.deepcopy(intake)
    unsafe_intake["sanitization"]["raw_source_entered_development_environment"] = True
    expect_input_rejection(unsafe_intake, label, manifest, evaluated_at, "raw source entered", "unsafe handoff intake")

    outcome_label = copy.deepcopy(label)
    outcome_label["contains_outcome_content"] = True
    expect_input_rejection(intake, outcome_label, manifest, evaluated_at, "free of outcome content", "outcome-bearing label control")


def main() -> int:
    try:
        validate_policy_sources()
        suite = load_json(CASES_PATH)
        intake_suite = load_json(INTAKE_CASES_PATH)
        label_suite = load_json(LABEL_CASES_PATH)
        manifest_suite = load_json(MANIFEST_CASES_PATH)
        empty_manifest = load_json(EMPTY_MANIFEST_PATH)
        require(
            suite.get("fixture_set") == "SYNTHETIC_METADATA_ONLY_HISTORICAL_CONTROL_HANDOFF",
            "handoff fixture set is not labeled synthetic metadata-only",
        )
        intake = intake_suite["valid_template"]
        label = label_suite["valid_template"]
        manifest = manifest_suite["valid_template"]
        evaluated_at = label_suite["evaluated_at"]
        report = validate_canonical_report(suite, intake, label, manifest, evaluated_at)
        tamper_count = validate_tamper_mutations(report, suite, intake, label, manifest, evaluated_at)
        validate_report_structural_gates(report, intake, label, manifest, evaluated_at)
        validate_input_gates(intake, label, manifest, empty_manifest, evaluated_at)
        print(
            f"PASS historical control handoff: 1 canonical synthetic report, {tamper_count} tamper probes, "
            "3 report-structure gates, 9 linked-input gates, and 1 operational-promotion gate"
        )
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, HistoricalControlHandoffError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

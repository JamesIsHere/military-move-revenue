#!/usr/bin/env python3
"""Validate the deterministic no-data historical corpus preflight report."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.historical_corpus_manifest import HistoricalCorpusManifestError  # noqa: E402
from rules.historical_corpus_preflight import (  # noqa: E402
    PREFLIGHT_POLICY_PROVENANCE,
    PREFLIGHT_POLICY_VERSION,
    PREFLIGHT_SCHEMA_VERSION,
    HistoricalCorpusPreflightError,
    build_no_data_preflight,
    serialize_no_data_preflight,
    validate_no_data_preflight,
)


FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "historical-acceptance"
MANIFEST_PATH = FIXTURE_ROOT / "historical-corpus-manifest.json"
CASES_PATH = FIXTURE_ROOT / "historical-corpus-preflight-cases.json"
MANIFEST_CASES_PATH = FIXTURE_ROOT / "historical-corpus-manifest-cases.json"


class ValidationError(ValueError):
    """Raised when an expected preflight result is not observed."""


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


def expect_report_rejection(candidate: dict, manifest: dict, expected: str, label: str) -> None:
    try:
        validate_no_data_preflight(candidate, manifest)
    except HistoricalCorpusPreflightError as exc:
        require(expected in str(exc), f"{label} rejected for unexpected reason: {exc}")
        print(f"PASS {label} rejected")
        return
    raise ValidationError(f"{label} invalid preflight report was accepted")


def validate_policy_sources() -> None:
    for reference in PREFLIGHT_POLICY_PROVENANCE:
        path = ROOT / reference["document_path"]
        require(path.is_file(), f"preflight policy source is missing: {reference['document_path']}")
    policy = (ROOT / "docs" / "historical-corpus-preflight.md").read_text(encoding="utf-8")
    require(f"Version: `{PREFLIGHT_POLICY_VERSION}`" in policy, "preflight policy version is not documented")
    require("cannot authorize" in policy, "preflight policy lacks non-authorizing boundary")
    require("graphical" in policy, "preflight policy lacks presentation-neutral interface boundary")


def validate_canonical_report(manifest: dict, suite: dict) -> dict:
    report = build_no_data_preflight(manifest)
    require(validate_no_data_preflight(report, manifest) == report, "canonical preflight projection changed")
    require(report["schema_version"] == PREFLIGHT_SCHEMA_VERSION, "preflight schema mismatch")
    require(report["status"] == "BLOCKED_EXTERNAL_PREREQUISITES", "empty preflight status changed")
    require(report["authorizes_ingest"] is False, "empty preflight authorizes ingest")
    require(report["contains_case_content"] is False, "empty preflight contains case content")
    require(report["progress"] == suite["expected_progress"], "empty preflight progress changed")
    require(
        [blocker["code"] for blocker in report["blockers"]] == suite["expected_blocker_codes"],
        "preflight blocker catalog or order changed",
    )
    require(report["display"]["blocker_count"] == len(report["blockers"]), "display blocker count drift")
    require(report["display"]["progress_label"] == "0 of 25 passing historical cases", "display progress drift")
    require(all(blocker["provenance"] for blocker in report["blockers"]), "preflight blocker lacks provenance")
    serialized = serialize_no_data_preflight(report)
    require(serialized == serialize_no_data_preflight(json.loads(serialized)), "preflight serialization is unstable")
    print("PASS canonical no-data preflight reports 8 blockers, 0 passing cases, and 25 remaining")
    return report


def validate_tamper_mutations(report: dict, manifest: dict, suite: dict) -> int:
    cases = suite.get("tamper_mutations")
    require(isinstance(cases, list) and cases, "tamper_mutations must be a nonempty list")
    identifiers: set[str] = set()
    for case in cases:
        require(isinstance(case, dict), "preflight tamper case must be an object")
        case_id = case.get("id")
        require(isinstance(case_id, str) and case_id and case_id not in identifiers, "preflight tamper id is invalid")
        identifiers.add(case_id)
        candidate = copy.deepcopy(report)
        set_path(candidate, case["path"], copy.deepcopy(case["value"]))
        expect_report_rejection(candidate, manifest, case["expected_error_contains"], case_id)
    return len(cases)


def validate_structural_and_input_gates(report: dict, manifest: dict, manifest_cases: dict) -> None:
    extra = copy.deepcopy(report)
    extra["override_authorization"] = True
    expect_report_rejection(extra, manifest, "$.override_authorization", "caller authorization override")

    missing_blocker = copy.deepcopy(report)
    missing_blocker["blockers"].pop()
    expect_report_rejection(missing_blocker, manifest, "$.blockers.length", "removed case-deficit blocker")

    reordered = copy.deepcopy(report)
    reordered["blockers"][0], reordered["blockers"][1] = reordered["blockers"][1], reordered["blockers"][0]
    expect_report_rejection(reordered, manifest, "$.blockers.0", "reordered blocker catalog")

    try:
        build_no_data_preflight(manifest_cases["valid_template"])
    except HistoricalCorpusManifestError as exc:
        require("cannot authorize operational use" in str(exc), "synthetic manifest rejected for unexpected reason")
        print("PASS synthetic manifest rejected by no-data preflight")
    else:
        raise ValidationError("synthetic manifest entered no-data preflight")

    content_manifest = copy.deepcopy(manifest)
    content_manifest["contains_case_content"] = True
    try:
        build_no_data_preflight(content_manifest)
    except HistoricalCorpusManifestError as exc:
        require("must remain metadata-only" in str(exc), "content-bearing manifest rejected for unexpected reason")
        print("PASS content-bearing manifest rejected by no-data preflight")
    else:
        raise ValidationError("content-bearing manifest entered no-data preflight")


def main() -> int:
    try:
        validate_policy_sources()
        manifest = load_json(MANIFEST_PATH)
        suite = load_json(CASES_PATH)
        manifest_cases = load_json(MANIFEST_CASES_PATH)
        require(
            suite.get("fixture_set") == "SYNTHETIC_NO_DATA_HISTORICAL_CORPUS_PREFLIGHT",
            "preflight fixture set is not labeled synthetic no-data",
        )
        report = validate_canonical_report(manifest, suite)
        tamper_count = validate_tamper_mutations(report, manifest, suite)
        validate_structural_and_input_gates(report, manifest, manifest_cases)
        print(
            f"PASS historical corpus preflight: 1 canonical blocked report, {tamper_count} tamper probes, "
            "3 structural gates, and 2 unsafe-input gates"
        )
        return 0
    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        HistoricalCorpusManifestError,
        HistoricalCorpusPreflightError,
        ValidationError,
    ) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

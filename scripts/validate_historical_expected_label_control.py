#!/usr/bin/env python3
"""Validate metadata-only historical expected-label approval controls."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.historical_expected_label import (  # noqa: E402
    LABEL_CONTROL_POLICY_PROVENANCE,
    LABEL_CONTROL_POLICY_VERSION,
    LABEL_CONTROL_SCHEMA_VERSION,
    HistoricalExpectedLabelError,
    validate_historical_expected_label_control,
)


FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "historical-acceptance"
CASES_PATH = FIXTURE_ROOT / "historical-expected-label-control-cases.json"
INTAKE_CASES_PATH = FIXTURE_ROOT / "historical-intake-control-cases.json"
MANIFEST_CASES_PATH = FIXTURE_ROOT / "historical-corpus-manifest-cases.json"


class ValidationError(ValueError):
    """Raised when an expected label-control result is not observed."""


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


def expect_rejection(
    candidate: object,
    evaluated_at: str,
    intake: object,
    expected: str,
    label: str,
) -> None:
    try:
        validate_historical_expected_label_control(
            candidate,
            evaluated_at,
            intake,
            allow_synthetic_template=True,
        )
    except HistoricalExpectedLabelError as exc:
        require(expected in str(exc), f"{label} rejected for unexpected reason: {exc}")
        print(f"PASS {label} rejected")
        return
    raise ValidationError(f"{label} invalid expected-label control was accepted")


def validate_policy_sources() -> None:
    for reference in LABEL_CONTROL_POLICY_PROVENANCE:
        path = ROOT / reference["document_path"]
        require(path.is_file(), f"expected-label policy source is missing: {reference['document_path']}")
    policy = (ROOT / "docs" / "historical-expected-label-control.md").read_text(encoding="utf-8")
    require(f"Version: `{LABEL_CONTROL_POLICY_VERSION}`" in policy, "expected-label policy version is not documented")
    require("never the expected projection" in policy, "expected-label policy lacks no-outcome-content boundary")
    require("cannot author" in policy, "expected-label policy lacks AI authorship boundary")
    require("No operational example" in policy, "expected-label policy lacks operational-fixture boundary")


def validate_template(suite: dict, intake_suite: dict, manifest_suite: dict) -> dict:
    template = suite.get("valid_template")
    evaluated_at = suite.get("evaluated_at")
    intake = intake_suite["valid_template"]
    require(isinstance(template, dict), "valid_template must be an object")
    require(isinstance(evaluated_at, str), "evaluated_at must be an ISO instant string")
    result = validate_historical_expected_label_control(
        template,
        evaluated_at,
        intake,
        allow_synthetic_template=True,
    )
    require(result == template, "expected-label template projection changed")
    require(result["schema_version"] == LABEL_CONTROL_SCHEMA_VERSION, "expected-label schema mismatch")
    require(result["contains_case_content"] is False, "expected-label template contains case content")
    require(result["contains_outcome_content"] is False, "expected-label template contains outcome content")
    require(result["label_use_authorized"] is False, "expected-label template authorizes label use")

    manifest = manifest_suite["valid_template"]
    for entry in manifest["entries"]:
        require(entry["case_reference_id"] == result["case_reference_id"], "label/manifest case reference mismatch")
        require(entry["intake_envelope_id"] == result["intake_link"]["envelope_id"], "label/manifest intake ID mismatch")
        require(entry["intake_envelope_sha256"] == result["intake_link"]["envelope_sha256"], "label/manifest intake hash mismatch")
        require(entry["sanitized_bundle_sha256"] == result["intake_link"]["sanitized_bundle_sha256"], "label/manifest bundle hash mismatch")
        require(entry["expected_label_id"] == result["label_artifact"]["label_id"], "label/manifest label ID mismatch")
        require(entry["expected_label_sha256"] == result["label_artifact"]["label_sha256"], "label/manifest label hash mismatch")
    require(
        result["approval"]["reviewer_role"] == intake["approval_separation"]["outcome_reviewer_role"],
        "label reviewer differs from linked intake role",
    )
    print("PASS synthetic expected-label control links the intake envelope, manifest, bundle, label hash, and reviewer role")

    try:
        validate_historical_expected_label_control(template, evaluated_at, intake)
    except HistoricalExpectedLabelError as exc:
        require("cannot authorize operational use" in str(exc), "synthetic expected-label promotion gate changed")
        print("PASS synthetic expected-label template rejected by operational gate")
    else:
        raise ValidationError("synthetic expected-label template passed the operational gate")
    return template


def validate_negative_mutations(suite: dict, intake: dict) -> int:
    template = suite["valid_template"]
    evaluated_at = suite["evaluated_at"]
    cases = suite.get("invalid_mutations")
    require(isinstance(cases, list) and cases, "invalid_mutations must be a nonempty list")
    identifiers: set[str] = set()
    for case in cases:
        require(isinstance(case, dict), "expected-label mutation must be an object")
        case_id = case.get("id")
        require(isinstance(case_id, str) and case_id and case_id not in identifiers, "expected-label mutation id is invalid")
        identifiers.add(case_id)
        candidate = copy.deepcopy(template)
        set_path(candidate, case["path"], copy.deepcopy(case["value"]))
        expect_rejection(candidate, evaluated_at, intake, case["expected_error_contains"], case_id)
    return len(cases)


def validate_structural_and_linked_input_gates(suite: dict, intake: dict) -> None:
    template = suite["valid_template"]
    evaluated_at = suite["evaluated_at"]

    outcome_content = copy.deepcopy(template)
    outcome_content["label_artifact"]["expected_projection"] = {"report_status": "FINAL"}
    expect_rejection(outcome_content, evaluated_at, intake, "fields mismatch", "embedded expected projection")

    monetary_content = copy.deepcopy(template)
    monetary_content["approval"]["expected_amount"] = "0.00"
    expect_rejection(monetary_content, evaluated_at, intake, "fields mismatch", "embedded expected amount")

    shipment_content = copy.deepcopy(template)
    shipment_content["shipment_id"] = "PROHIBITED-CONTENT-FIELD"
    expect_rejection(shipment_content, evaluated_at, intake, "fields mismatch", "embedded shipment identifier")

    mismatched_intake = copy.deepcopy(intake)
    mismatched_intake["case_reference_id"] = "SYNTHETIC-OPAQUE-CASE-REFERENCE-999"
    expect_rejection(template, evaluated_at, mismatched_intake, "case references differ", "mismatched linked intake case")

    unsafe_intake = copy.deepcopy(intake)
    unsafe_intake["sanitization"]["raw_source_entered_development_environment"] = True
    expect_rejection(template, evaluated_at, unsafe_intake, "raw source entered", "unsafe linked intake")

    conflicting_roles = copy.deepcopy(intake)
    conflicting_roles["approval_separation"]["outcome_reviewer_role"] = conflicting_roles["authorization"]["verifier_role"]
    expect_rejection(template, evaluated_at, conflicting_roles, "critical approval roles are not distinct", "role-conflicted linked intake")


def main() -> int:
    try:
        validate_policy_sources()
        suite = load_json(CASES_PATH)
        intake_suite = load_json(INTAKE_CASES_PATH)
        manifest_suite = load_json(MANIFEST_CASES_PATH)
        require(
            suite.get("fixture_set") == "SYNTHETIC_METADATA_ONLY_HISTORICAL_EXPECTED_LABEL_CONTROL",
            "expected-label fixture set is not labeled synthetic metadata-only",
        )
        template = validate_template(suite, intake_suite, manifest_suite)
        negative_count = validate_negative_mutations(suite, intake_suite["valid_template"])
        validate_structural_and_linked_input_gates(suite, intake_suite["valid_template"])
        require(template["execution_boundary"]["status"] == "NOT_STARTED", "synthetic label control execution boundary changed")
        print(
            f"PASS historical expected-label control: 1 non-authorizing template, {negative_count} negative "
            "mutations, 1 operational-promotion gate, and 6 content/intake-link gates"
        )
        return 0
    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        HistoricalExpectedLabelError,
        ValidationError,
    ) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

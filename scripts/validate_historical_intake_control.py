#!/usr/bin/env python3
"""Validate the metadata-only historical intake control contract."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.historical_intake import (  # noqa: E402
    INTAKE_POLICY_PROVENANCE,
    INTAKE_POLICY_VERSION,
    INTAKE_SCHEMA_VERSION,
    HistoricalIntakeError,
    validate_historical_intake_envelope,
)


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "historical-acceptance" / "historical-intake-control-cases.json"


class ValidationError(ValueError):
    """Raised when an expected contract result is not observed."""


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


def validate_policy_sources() -> None:
    for reference in INTAKE_POLICY_PROVENANCE:
        path = ROOT / reference["document_path"]
        require(path.is_file(), f"intake policy source is missing: {reference['document_path']}")
    policy = (ROOT / "docs" / "historical-intake-control.md").read_text(encoding="utf-8")
    require(f"Version: `{INTAKE_POLICY_VERSION}`" in policy, "intake policy version is not documented")
    require("never an authorization" in policy, "intake policy lacks synthetic-template boundary")
    require("AI may not attest" in policy, "intake policy lacks AI attestation boundary")


def validate_template(suite: dict) -> None:
    template = suite.get("valid_template")
    evaluated_at = suite.get("evaluated_at")
    require(isinstance(template, dict), "valid_template must be an object")
    result = validate_historical_intake_envelope(template, evaluated_at, allow_synthetic_template=True)
    require(result == template, "historical intake template projection changed")
    require(result["schema_version"] == INTAKE_SCHEMA_VERSION, "historical intake schema mismatch")
    require(result["contains_case_content"] is False, "synthetic intake template contains case content")
    require(result["real_data_ingest_authorized"] is False, "synthetic intake template authorizes real-data ingest")

    try:
        validate_historical_intake_envelope(template, evaluated_at)
    except HistoricalIntakeError as exc:
        require("cannot authorize operational use" in str(exc), "synthetic operational-promotion rejection changed")
        print("PASS synthetic intake template rejected by operational gate")
    else:
        raise ValidationError("synthetic intake template passed the operational gate")


def validate_negative_mutations(suite: dict) -> int:
    template = suite["valid_template"]
    evaluated_at = suite["evaluated_at"]
    cases = suite.get("invalid_mutations")
    require(isinstance(cases, list) and cases, "invalid_mutations must be a nonempty list")
    identifiers: set[str] = set()
    for case in cases:
        require(isinstance(case, dict), "intake mutation must be an object")
        case_id = case.get("id")
        require(isinstance(case_id, str) and case_id and case_id not in identifiers, "intake mutation id is invalid")
        identifiers.add(case_id)
        candidate = copy.deepcopy(template)
        set_path(candidate, case["path"], copy.deepcopy(case["value"]))
        try:
            validate_historical_intake_envelope(candidate, evaluated_at, allow_synthetic_template=True)
        except HistoricalIntakeError as exc:
            require(case["expected_error_contains"] in str(exc), f"{case_id} rejected for unexpected reason: {exc}")
            print(f"PASS {case_id} rejected: {case['description']}")
            continue
        raise ValidationError(f"{case_id} invalid intake control was accepted")
    return len(cases)


def validate_extra_field_rejection(suite: dict) -> None:
    candidate = copy.deepcopy(suite["valid_template"])
    candidate["shipment_id"] = "PROHIBITED-CONTENT-FIELD"
    try:
        validate_historical_intake_envelope(candidate, suite["evaluated_at"], allow_synthetic_template=True)
    except HistoricalIntakeError as exc:
        require("fields mismatch" in str(exc), "extra case-content field rejected for unexpected reason")
        print("PASS metadata envelope rejected an extra case-content field")
        return
    raise ValidationError("metadata envelope accepted an extra case-content field")


def main() -> int:
    try:
        validate_policy_sources()
        suite = load_json(FIXTURE_PATH)
        require(
            suite.get("fixture_set") == "SYNTHETIC_METADATA_ONLY_HISTORICAL_INTAKE_CONTROLS",
            "historical intake fixture set is not labeled synthetic metadata-only",
        )
        validate_template(suite)
        negative_count = validate_negative_mutations(suite)
        validate_extra_field_rejection(suite)
        print(
            f"PASS historical intake control: 1 non-authorizing metadata template, "
            f"{negative_count} negative mutations, 1 operational-promotion gate, and 1 extra-field gate"
        )
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, HistoricalIntakeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

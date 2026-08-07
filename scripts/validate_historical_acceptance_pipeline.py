#!/usr/bin/env python3
"""Validate the operational historical-acceptance pipeline and count gate."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.historical_acceptance import (  # noqa: E402
    ACCEPTANCE_POLICY_PROVENANCE,
    ACCEPTANCE_SCHEMA_VERSION,
    AUTHORIZED_SANITIZED_HISTORICAL,
    HistoricalAcceptanceError,
    build_historical_acceptance_report,
    serialize_historical_acceptance_report,
    validate_historical_acceptance_report,
)
from rules.audit_report import AuditReportError  # noqa: E402


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "historical-acceptance" / "historical-acceptance-cases.json"
MANIFEST_PATH = ROOT / "sources" / "source-manifest.csv"


class ValidationError(ValueError):
    """Raised when an expected validation result is not observed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def reject_float(value: str) -> object:
    raise ValidationError(f"fixture contains binary floating-point value {value}")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle, parse_float=reject_float)
    require(isinstance(value, dict), f"{path} must contain an object")
    return value


def replace_string(value: object, old: str, new: str) -> object:
    if isinstance(value, dict):
        return {key: replace_string(child, old, new) for key, child in value.items()}
    if isinstance(value, list):
        return [replace_string(child, old, new) for child in value]
    if isinstance(value, str):
        return value.replace(old, new)
    return value


def resolve_fixture_path(value: object, label: str) -> Path:
    require(isinstance(value, str) and value, f"{label} path is required")
    path = (ROOT / value).resolve()
    require(path.is_relative_to(ROOT), f"{label} path escapes repository")
    require(path.is_file(), f"{label} path is missing")
    return path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_archived_public_material(request: dict) -> None:
    public_cases = [value for value in request["cases"] if value.get("corpus_tier") == "PUBLIC_PRECEDENT"]
    require(len(public_cases) == 1, "expected exactly one public precedent fixture")
    public = public_cases[0]
    require(public.get("archive_status") == "ARCHIVED_AUTHORITATIVE", "public precedent is not archived")

    raw_path = resolve_fixture_path(public.get("raw_artifact_path"), "public raw artifact")
    extract_path = resolve_fixture_path(public.get("sanitized_extract_path"), "public sanitized extract")
    raw_digest = sha256_file(raw_path)
    extract_digest = sha256_file(extract_path)
    require(raw_path.read_bytes().startswith(b"%PDF-"), "public raw artifact is not a PDF")
    require(raw_digest == public.get("raw_artifact_sha256"), "public raw artifact hash mismatch")
    require(extract_digest == public.get("sanitized_extract_sha256"), "public sanitized extract hash mismatch")

    extract = load_json(extract_path)
    source = extract.get("source")
    derivation = extract.get("derivation")
    scope = extract.get("scope")
    require(extract.get("data_status") == "PUBLIC_PRECEDENT_SANITIZED_DERIVED", "public extract data status mismatch")
    require(extract.get("use_status") == "REFERENCE_ONLY_OUT_OF_SCOPE_CONTEXT", "public extract use status mismatch")
    require(isinstance(source, dict) and source.get("source_id") == "SRC-CBCA-1536-RELO-2009", "public extract source mismatch")
    require(source.get("raw_artifact_sha256") == raw_digest, "public extract raw-source link mismatch")
    require("canonical_url" not in source, "sanitized extract retained an identifying source URL")
    require(isinstance(derivation, dict) and derivation.get("sanitization_status") == "PASSED", "public extract sanitization did not pass")
    require(derivation.get("contains_direct_person_identifiers") is False, "public extract declares direct personal identifiers")
    require(isinstance(scope, dict) and scope.get("dp3_indicator") is False, "out-of-scope precedent was represented as DP3")

    with MANIFEST_PATH.open(encoding="utf-8-sig", newline="") as handle:
        manifest = {row["source_id"]: row for row in csv.DictReader(handle)}
    row = manifest.get(source["source_id"])
    require(row is not None, "public precedent source is absent from the manifest")
    require(row["status"] == "archived", "public precedent manifest status is not archived")
    require(row["file_name"] == raw_path.name, "public precedent manifest file name mismatch")
    require(row["bytes"] == str(raw_path.stat().st_size), "public precedent manifest byte length mismatch")
    require(row["sha256"].lower() == raw_digest, "public precedent manifest hash mismatch")


def apply_audit_mutations(records: dict, mutations: object, label: str) -> dict:
    require(isinstance(mutations, list), f"{label} audit_mutations must be a list")
    container = {"records": copy.deepcopy(records)}
    mutated_paths: set[str] = set()
    for index, mutation in enumerate(mutations):
        require(isinstance(mutation, dict), f"{label} audit mutation {index} must be an object")
        path = mutation.get("path")
        require(isinstance(path, str) and path.startswith("records."), f"{label} audit mutation {index} path must target records")
        require(path not in mutated_paths, f"{label} duplicate audit mutation path {path}")
        require("value" in mutation, f"{label} audit mutation {index} value is required")
        set_path(container, path, copy.deepcopy(mutation["value"]))
        mutated_paths.add(path)
    return container["records"]


def materialize_case(case: dict) -> dict:
    candidate = copy.deepcopy(case)
    assembly = candidate.pop("component_assembly", None)
    if assembly is None:
        return candidate
    require(isinstance(assembly, dict), "component_assembly must be an object")
    target_shipment_id = assembly.get("target_shipment_id")
    require(isinstance(target_shipment_id, str) and target_shipment_id, "target shipment id is required")
    audit_fixture = load_json(resolve_fixture_path(assembly.get("audit_records_path"), "audit records"))
    require(audit_fixture.get("data_status") == "SYNTHETIC", "acceptance audit component must be synthetic")
    candidate["audit_records"] = apply_audit_mutations(
        audit_fixture["records"],
        assembly.get("audit_mutations", []),
        "case",
    )
    charge_inputs: list[dict] = []
    components = assembly.get("charge_components")
    require(isinstance(components, list) and components, "charge components are required")
    for component in components:
        require(isinstance(component, dict), "charge component must be an object")
        rating_fixture = load_json(resolve_fixture_path(component.get("rating_fixture_path"), "rating fixture"))
        require(rating_fixture.get("data_status") == "SYNTHETIC", "acceptance rating component must be synthetic")
        source_shipment_id = component.get("source_shipment_id")
        require(isinstance(source_shipment_id, str) and source_shipment_id, "rating source shipment id is required")
        rating_records = replace_string(copy.deepcopy(rating_fixture["records"]), source_shipment_id, target_shipment_id)
        instance_id = component.get("charge_instance_id")
        charge_input = {
            "charge_instance_id": instance_id,
            "adapter_id": component.get("adapter_id"),
            "rating_case": {
                "case_id": f"{candidate['case_id']}:{instance_id}:RATING",
                "data_status": candidate["data_status"],
                "interpretation_decision_id": component.get("interpretation_decision_id"),
                "records": rating_records,
            },
        }
        component_mutations = component.get("audit_mutations", [])
        if component_mutations:
            charge_input["audit_records"] = apply_audit_mutations(
                candidate["audit_records"],
                component_mutations,
                f"charge component {instance_id}",
            )
        charge_inputs.append(charge_input)
    candidate["charge_inputs"] = charge_inputs
    return candidate


def build_request(suite: dict) -> dict:
    return {
        "corpus_run_id": suite["corpus_run_id"],
        "evaluated_at": suite["evaluated_at"],
        "cases": [materialize_case(value) for value in suite["cases"]],
    }


def set_path(target: object, path: str, value: object) -> None:
    parts = path.split(".")
    current = target
    for part in parts[:-1]:
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]  # type: ignore[index]
    if isinstance(current, list):
        current[int(parts[-1])] = value
    else:
        current[parts[-1]] = value  # type: ignore[index]


def validate_positive(report: dict) -> None:
    require(report["schema_version"] == ACCEPTANCE_SCHEMA_VERSION, "acceptance schema mismatch")
    require(report["status"] == "OPERATIONAL", "pipeline is not operational")
    require(report["completion_status"] == "NOT_READY", "synthetic corpus incorrectly completed M6")
    summary = report["summary"]
    require(summary["total_case_count"] == 4, "corpus case count mismatch")
    require(summary["source_structured_synthetic_case_count"] == 3, "synthetic benchmark count mismatch")
    require(summary["public_precedent_case_count"] == 1, "public precedent count mismatch")
    require(summary["public_precedent_pending_archive_count"] == 0, "pending public archive count mismatch")
    require(summary["authorized_historical_case_count"] == 0, "synthetic fixture became historical")
    require(summary["passing_authorized_historical_case_count"] == 0, "synthetic fixture counted as passing history")
    require(summary["remaining_passing_historical_case_count"] == 25, "remaining historical count mismatch")

    by_id = {value["case_id"]: value for value in report["case_results"]}
    synthetic = by_id["ACCEPT-SYNTH-28A-28B-001"]
    require(synthetic["execution_status"] == "EXECUTED", "synthetic case did not execute")
    require(synthetic["case_result"] == "PASS", "synthetic expected outcome did not match")
    require(synthetic["outcome_comparison"] == {"status": "MATCH", "mismatch_paths": []}, "synthetic comparison mismatch")
    require(synthetic["acceptance_eligible"] is False, "synthetic case became eligible")
    require(synthetic["counts_toward_required_25"] is False, "synthetic case counted toward 25")
    audit = synthetic["audit_report"]
    require(audit["status"] == "FINAL" and audit["summary"]["expected_amount"] == "397.00", "synthetic audit result mismatch")
    require(len(audit["charge_results"]) == 2, "synthetic audit did not execute both adapters")

    discrepancy = by_id["ACCEPT-SYNTH-28A-28B-002-DISCREPANCY"]
    require(discrepancy["execution_status"] == "EXECUTED", "discrepancy benchmark did not execute")
    require(discrepancy["case_result"] == "PASS", "discrepancy expected outcome did not match")
    require(discrepancy["outcome_comparison"] == {"status": "MATCH", "mismatch_paths": []}, "discrepancy comparison mismatch")
    require(discrepancy["acceptance_eligible"] is False, "synthetic discrepancy became eligible")
    require(discrepancy["counts_toward_required_25"] is False, "synthetic discrepancy counted toward 25")
    discrepancy_audit = discrepancy["audit_report"]
    discrepancy_summary = discrepancy_audit["summary"]
    require(discrepancy_audit["status"] == "FINAL", "discrepancy report was not final")
    require(discrepancy_audit["human_review_required"] is True, "decided discrepancies did not require review")
    require(discrepancy_summary["expected_amount"] == "397.00", "discrepancy expected total mismatch")
    require(discrepancy_summary["invoiced_amount"] == "400.00", "discrepancy invoiced total mismatch")
    require(discrepancy_summary["paid_amount"] == "400.00", "discrepancy paid total mismatch")
    require(discrepancy_summary["billing_variance"] == "3.00", "opposing variances did not net exactly")
    require(discrepancy_summary["open_finding_count"] == 2, "line-level discrepancies were lost through netting")
    discrepancy_charges = {value["charge_instance_id"]: value["audit_result"] for value in discrepancy_audit["charge_results"]}
    require(discrepancy_charges["ITEM-28A"]["comparison"]["billing_variance"] == "51.50", "Item 28A overbilling variance mismatch")
    require(discrepancy_charges["ITEM-28A"]["audit_finding"]["billing_finding_code"] == "OVERBILLED", "Item 28A overbilling finding mismatch")
    require(discrepancy_charges["ITEM-28B"]["comparison"]["billing_variance"] == "-48.50", "Item 28B underbilling variance mismatch")
    require(discrepancy_charges["ITEM-28B"]["audit_finding"]["billing_finding_code"] == "UNDERBILLED", "Item 28B underbilling finding mismatch")

    blocked = by_id["ACCEPT-SYNTH-28A-28B-003-EVIDENCE-BLOCKED"]
    require(blocked["execution_status"] == "EXECUTED", "evidence-blocked benchmark did not execute")
    require(blocked["case_result"] == "PASS", "evidence-blocked expected outcome did not match")
    require(blocked["outcome_comparison"] == {"status": "MATCH", "mismatch_paths": []}, "evidence-blocked comparison mismatch")
    require(blocked["acceptance_eligible"] is False, "evidence-blocked synthetic case became eligible")
    require(blocked["counts_toward_required_25"] is False, "evidence-blocked synthetic case counted toward 25")
    blocked_audit = blocked["audit_report"]
    blocked_summary = blocked_audit["summary"]
    require(blocked_audit["status"] == "BLOCKED", "evidence-blocked report was not blocked")
    require(blocked_audit["human_review_required"] is True, "evidence block did not require human review")
    require(blocked_summary["final_charge_count"] == 1 and blocked_summary["blocked_charge_count"] == 1, "blocked charge counts mismatch")
    require(blocked_summary["finding_count"] == 4 and blocked_summary["open_finding_count"] == 1, "blocked finding counts mismatch")
    require(blocked_summary["totals_status"] == "BLOCKED", "blocked totals status mismatch")
    for field in ("currency", "expected_amount", "invoiced_amount", "paid_amount", "billing_variance", "payment_variance", "realized_variance"):
        require(field not in blocked_summary, f"blocked report exposed aggregate {field}")
    blocked_charges = {value["charge_instance_id"]: value["audit_result"] for value in blocked_audit["charge_results"]}
    require(blocked_charges["ITEM-28A"]["status"] == "FINAL", "decided Item 28A result was not preserved")
    require(blocked_charges["ITEM-28A"]["comparison"]["expected_amount"] == "198.50", "decided Item 28A money was not preserved")
    require(blocked_charges["ITEM-28A"]["audit_finding"]["billing_finding_code"] == "CORRECTLY_BILLED", "decided Item 28A finding changed")
    require(blocked_charges["ITEM-28B"]["status"] == "BLOCKED", "unreviewed Item 28B evidence did not block")
    require(
        blocked_charges["ITEM-28B"]["blocked_reasons"]
        == ["INVOICE_LINE_EVIDENCE_MISSING_OR_UNREVIEWED:LINEV-MULTI-28B"],
        "Item 28B blocked reason mismatch",
    )
    require("comparison" not in blocked_charges["ITEM-28B"], "blocked Item 28B exposed an authoritative comparison")

    public = by_id["PUBLIC-CBCA-1536-RELO-ARCHIVED"]
    require(public["benchmark_status"] == "REGISTERED_REFERENCE_ONLY", "archived public source was not registered")
    require(public["execution_status"] == "NOT_EXECUTED_REFERENCE_ONLY", "out-of-scope public precedent was executed")
    require(public["counts_toward_required_25"] is False, "public precedent counted toward 25")
    require(public["raw_artifact_sha256"] == "27d847b1c9200d3740b32a67e1c0598da66904b2d77618f6d20b5b0eddf65071", "public raw hash was not preserved")
    require(public["sanitized_extract_sha256"] == "53505ba3a66038c75811d7c8ad9e7493a7d395d0580b9561d6d0b17e6b73136a", "public extract hash was not preserved")

    serialized = serialize_historical_acceptance_report(report)
    require(json.loads(serialized) == report, "canonical acceptance JSON does not round-trip")
    require(serialized == serialize_historical_acceptance_report(report), "acceptance serialization is unstable")
    require("\n" not in serialized, "acceptance serialization is not compact")


def expect_request_rejection(request: dict, label: str, mutate: Callable[[dict], None]) -> None:
    candidate = copy.deepcopy(request)
    mutate(candidate)
    try:
        build_historical_acceptance_report(candidate)
    except HistoricalAcceptanceError:
        print(f"PASS acceptance request rejected: {label}")
        return
    raise ValidationError(f"acceptance request was accepted: {label}")


def validate_request_gates(request: dict) -> None:
    def forge_historical_without_envelope(value: dict) -> None:
        case = value["cases"][0]
        case["corpus_tier"] = AUTHORIZED_SANITIZED_HISTORICAL
        case["data_status"] = "authorized_sanitized"
        case["intake_control"].update(
            {
                "authorization_status": "WRITTEN_AUTHORIZATION_VERIFIED",
                "sanitization_status": "VERIFIED_SANITIZED_BEFORE_INGEST",
                "authorization_reference_id": "SYNTHETIC-NOT-AUTHORITY",
            }
        )

    probes = [
        ("international scope", lambda value: set_path(value, "cases.0.scope.domestic_indicator", False)),
        ("wrong billing relationship", lambda value: set_path(value, "cases.0.scope.billing_relationship", "MEMBER_REIMBURSEMENT")),
        ("forged historical tier", lambda value: set_path(value, "cases.0.corpus_tier", AUTHORIZED_SANITIZED_HISTORICAL)),
        ("historical tier without intake envelope", forge_historical_without_envelope),
        ("synthetic case with intake envelope", lambda value: value["cases"][0]["intake_control"].update({"historical_intake_envelope": {}})),
        ("sensitive customer name", lambda value: value["cases"][0].update({"customer_name": "PROHIBITED"})),
        ("hidden document metadata", lambda value: value["cases"][0].update({"hidden-document-metadata": "PROHIBITED"})),
        ("engine-derived label", lambda value: set_path(value, "cases.0.expected_outcome_label.creation_method", "ENGINE_DERIVED")),
        ("late label approval", lambda value: set_path(value, "cases.0.expected_outcome_label.approved_at", "2026-08-08T00:00:00Z")),
        ("wrong interpretation decision", lambda value: set_path(value, "cases.0.charge_inputs.0.rating_case.interpretation_decision_id", "INT-TAMPERED")),
        ("invalid charge-scoped audit records", lambda value: set_path(value, "cases.2.charge_inputs.1.audit_records", "NOT_AN_OBJECT")),
        ("binary floating-point money", lambda value: set_path(value, "cases.0.expected_outcome_label.expected_projection.summary.expected_amount", 397.0)),
        ("duplicate case id", lambda value: value["cases"].append(copy.deepcopy(value["cases"][0]))),
        ("invalid archived extract hash", lambda value: set_path(value, "cases.3.sanitized_extract_sha256", "not-a-sha256")),
    ]
    for label, mutate in probes:
        expect_request_rejection(request, label, mutate)


def validate_mismatch_paths(request: dict) -> None:
    candidate = copy.deepcopy(request)
    set_path(candidate, "cases.0.expected_outcome_label.expected_projection.summary.expected_amount", "397.01")
    report = build_historical_acceptance_report(candidate)
    synthetic = next(value for value in report["case_results"] if value["case_id"] == "ACCEPT-SYNTH-28A-28B-001")
    require(synthetic["case_result"] == "FAIL", "expected-outcome mismatch was not surfaced")
    require(synthetic["outcome_comparison"]["status"] == "MISMATCH", "mismatch status was not recorded")
    require(
        "expected_projection.summary.expected_amount" in synthetic["outcome_comparison"]["mismatch_paths"],
        "exact mismatch path was not recorded",
    )
    require(synthetic["counts_toward_required_25"] is False, "mismatched case counted toward acceptance")

    discrepancy_candidate = copy.deepcopy(request)
    set_path(
        discrepancy_candidate,
        "cases.1.expected_outcome_label.expected_projection.charges.0.invoiced_amount",
        "249.99",
    )
    discrepancy_report = build_historical_acceptance_report(discrepancy_candidate)
    discrepancy = next(
        value
        for value in discrepancy_report["case_results"]
        if value["case_id"] == "ACCEPT-SYNTH-28A-28B-002-DISCREPANCY"
    )
    require(discrepancy["case_result"] == "FAIL", "altered discrepancy label was not surfaced")
    require(
        "expected_projection.charges.0.invoiced_amount" in discrepancy["outcome_comparison"]["mismatch_paths"],
        "altered discrepancy label path was not recorded",
    )
    require(discrepancy["audit_report"]["summary"]["invoiced_amount"] == "400.00", "label mutation changed financial output")
    require(discrepancy["counts_toward_required_25"] is False, "mismatched discrepancy counted toward acceptance")

    blocked_candidate = copy.deepcopy(request)
    set_path(
        blocked_candidate,
        "cases.2.expected_outcome_label.expected_projection.charges.1.blocked_reasons.0",
        "TAMPERED_BLOCK_REASON",
    )
    blocked_report = build_historical_acceptance_report(blocked_candidate)
    blocked = next(
        value
        for value in blocked_report["case_results"]
        if value["case_id"] == "ACCEPT-SYNTH-28A-28B-003-EVIDENCE-BLOCKED"
    )
    require(blocked["case_result"] == "FAIL", "altered blocked-case label was not surfaced")
    require(
        "expected_projection.charges.1.blocked_reasons.0" in blocked["outcome_comparison"]["mismatch_paths"],
        "altered blocked-reason path was not recorded",
    )
    require(blocked["audit_report"]["summary"]["totals_status"] == "BLOCKED", "label mutation changed blocked financial output")
    require("expected_amount" not in blocked["audit_report"]["summary"], "label mutation exposed blocked aggregate money")
    require(blocked["counts_toward_required_25"] is False, "mismatched blocked case counted toward acceptance")
    print("PASS 3 independent expected-outcome mismatches are reported without changing financial output")


def validate_assembly_gates(suite: dict) -> None:
    probes = [
        (
            "audit mutation outside records",
            lambda value: set_path(value, "cases.1.component_assembly.audit_mutations.0.path", "scope.program_code"),
        ),
        (
            "duplicate audit mutation path",
            lambda value: value["cases"][1]["component_assembly"]["audit_mutations"].append(
                copy.deepcopy(value["cases"][1]["component_assembly"]["audit_mutations"][0])
            ),
        ),
        (
            "charge audit mutation outside records",
            lambda value: set_path(
                value,
                "cases.2.component_assembly.charge_components.1.audit_mutations.0.path",
                "scope.program_code",
            ),
        ),
        (
            "duplicate charge audit mutation path",
            lambda value: value["cases"][2]["component_assembly"]["charge_components"][1]["audit_mutations"].append(
                copy.deepcopy(value["cases"][2]["component_assembly"]["charge_components"][1]["audit_mutations"][0])
            ),
        ),
    ]
    for label, mutate in probes:
        candidate = copy.deepcopy(suite)
        mutate(candidate)
        try:
            build_request(candidate)
        except ValidationError:
            print(f"PASS acceptance fixture assembly rejected: {label}")
            continue
        raise ValidationError(f"acceptance fixture assembly accepted: {label}")


def validate_report_tampers(report: dict) -> None:
    probes = [
        ("schema", "schema_version", "historical-acceptance-report.tampered"),
        ("remaining count", "summary.remaining_passing_historical_case_count", 24),
        ("corpus tier", "case_results.0.corpus_tier", AUTHORIZED_SANITIZED_HISTORICAL),
        ("synthetic count gate", "case_results.0.counts_toward_required_25", True),
        ("embedded audit total", "case_results.0.audit_report.summary.expected_amount", "397.01"),
        ("expected label", "case_results.0.expected_outcome_label.expected_projection.summary.expected_amount", "397.01"),
        ("blocked aggregate money", "case_results.2.audit_report.summary.expected_amount", "397.00"),
        ("policy provenance", "provenance.0.document_path", "tampered.md"),
    ]
    for label, path, value in probes:
        candidate = copy.deepcopy(report)
        set_path(candidate, path, value)
        try:
            validate_historical_acceptance_report(candidate)
        except (HistoricalAcceptanceError, AuditReportError):
            print(f"PASS acceptance report tamper rejected: {label}")
            continue
        raise ValidationError(f"acceptance report tamper was accepted: {label}")

    reordered = copy.deepcopy(report)
    reordered["case_results"].reverse()
    try:
        validate_historical_acceptance_report(reordered)
    except HistoricalAcceptanceError:
        print("PASS acceptance report tamper rejected: case order")
    else:
        raise ValidationError("acceptance report tamper was accepted: case order")


def validate_policy_sources() -> None:
    for reference in ACCEPTANCE_POLICY_PROVENANCE:
        path = ROOT / reference["document_path"]
        require(path.is_file(), f"acceptance policy provenance path is missing: {reference['document_path']}")
    policy = (ROOT / "docs" / "historical-acceptance-pipeline.md").read_text(encoding="utf-8")
    require("never counts toward the required 25" in policy, "policy lacks non-historical count gate")
    require("written-authorization" in policy, "policy lacks authorization gate")
    require("independently" in policy, "policy lacks independent outcome boundary")


def main() -> int:
    try:
        validate_policy_sources()
        suite = load_json(FIXTURE_PATH)
        require(suite.get("fixture_set") == "SYNTHETIC_HISTORICAL_ACCEPTANCE_PIPELINE_CASES", "fixture set is not labeled synthetic")
        validate_assembly_gates(suite)
        request = build_request(suite)
        validate_archived_public_material(request)
        report = build_historical_acceptance_report(request)
        validate_positive(report)
        print("PASS clean, opposing-discrepancy, and evidence-blocked Item 28A/28B benchmarks executed and remained non-counting")
        print("PASS archived CBCA precedent, sanitized extract, manifest, and hashes verified; record remained reference-only and non-counting")
        validate_request_gates(request)
        validate_mismatch_paths(request)
        validate_report_tampers(report)
        print("PASS historical acceptance pipeline: 4 corpus records, 4 assembly gates, 14 request gates, 3 mismatch probes, and 9 report-tamper probes")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, AuditReportError, HistoricalAcceptanceError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

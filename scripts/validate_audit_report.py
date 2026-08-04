#!/usr/bin/env python3
"""Validate the deterministic audit adapter and report envelope."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.audit_report import (  # noqa: E402
    ITEM_28A_ADAPTER_ID,
    REPORT_POLICY_ID,
    REPORT_POLICY_PROVENANCE,
    REPORT_POLICY_VERSION,
    REPORT_SCHEMA_VERSION,
    AuditReportError,
    build_audit_report,
    serialize_audit_report,
    validate_audit_report,
)
from rules.item_28a_extra_pickup import INTERPRETATION_DECISION_ID, rate_item_28a_extra_pickups  # noqa: E402


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "audit-report" / "audit-report-cases.json"


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict:
    def reject_float(value: str) -> None:
        raise ValidationError(f"{path.relative_to(ROOT)} contains non-exact JSON number {value}")

    with path.open(encoding="utf-8") as handle:
        value = json.load(handle, parse_float=reject_float)
    require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain an object")
    return value


def set_path(target: object, path: object, value: object) -> None:
    require(isinstance(path, str) and path, "mutation path is required")
    parts = path.split(".")
    current = target
    for part in parts[:-1]:
        if isinstance(current, list):
            require(part.isdigit() and int(part) < len(current), f"mutation path not found: {path}")
            current = current[int(part)]
        else:
            require(isinstance(current, dict) and part in current, f"mutation path not found: {path}")
            current = current[part]
    final = parts[-1]
    if isinstance(current, list):
        require(final.isdigit() and int(final) < len(current), f"mutation path not found: {path}")
        current[int(final)] = value
    else:
        require(isinstance(current, dict), f"mutation parent is not an object: {path}")
        current[final] = value


def mutate(target: dict, mutations: object, label: str) -> None:
    require(isinstance(mutations, list), f"{label} mutations must be a list")
    for mutation in mutations:
        require(isinstance(mutation, dict), f"{label} mutation must be an object")
        set_path(target, mutation.get("path"), mutation.get("value"))


def change_records(candidate: dict, fixture: dict, label: str) -> None:
    removals = fixture.get("remove_records", {})
    additions = fixture.get("append_records", {})
    require(isinstance(removals, dict) and isinstance(additions, dict), f"{label} record changes must be objects")
    for collection, record_ids in removals.items():
        records = candidate["records"].get(collection)
        require(isinstance(records, list) and isinstance(record_ids, list), f"{label} removal is invalid")
        wanted = set(record_ids)
        before = len(records)
        records[:] = [record for record in records if record.get("id") not in wanted]
        require(before - len(records) == len(wanted), f"{label} removal record was not found")
    for collection, records_to_add in additions.items():
        records = candidate["records"].get(collection)
        require(isinstance(records, list) and isinstance(records_to_add, list), f"{label} append is invalid")
        records.extend(copy.deepcopy(records_to_add))


def build_audit_case(audit_suite: dict, fixture: dict, rating_base: dict, audit_base: dict) -> dict:
    case_id = fixture["id"]
    rating_case = {
        "case_id": f"{case_id}-EXPECTED",
        "data_status": "synthetic",
        "interpretation_decision_id": INTERPRETATION_DECISION_ID,
        "records": copy.deepcopy(rating_base["records"]),
    }
    mutate(rating_case, fixture.get("rating_mutations", []), case_id)
    expected_result = rate_item_28a_extra_pickups(rating_case)
    mutate(expected_result, fixture.get("expected_result_mutations", []), case_id)
    candidate = {
        "case_id": case_id,
        "data_status": "synthetic",
        "as_of_at": audit_suite["as_of_at"],
        "expected_charge_result": expected_result,
        "records": copy.deepcopy(audit_base["records"]),
    }
    mutate(candidate, fixture.get("audit_mutations", []), case_id)
    change_records(candidate, fixture, case_id)
    return candidate


def validate_policy_contract() -> None:
    require(REPORT_SCHEMA_VERSION == "audit-report-envelope.v1", "report schema version changed")
    require(REPORT_POLICY_ID == "AUDIT-REPORT-ENVELOPE-V1", "report policy id changed")
    require(REPORT_POLICY_VERSION == "2026-08-03.1", "report policy version changed")
    for reference in REPORT_POLICY_PROVENANCE:
        path = ROOT / reference["document_path"]
        require(path.is_file(), f"report policy provenance path is missing: {reference['document_path']}")
    policy = (ROOT / "docs" / "audit-report-policy.md").read_text(encoding="utf-8")
    require("EXACT_DECIMAL_ALL_OR_NOTHING" not in policy, "policy should describe behavior, not depend on an implementation token")
    require("all-or-nothing" in policy, "report policy lacks blocked aggregate rule")
    require("deterministic code templates" in policy, "report policy lacks explanation boundary")


def validate_report_case(report: dict, expected: dict, case_id: str) -> None:
    require(report["status"] == expected["status"], f"{case_id} report status mismatch")
    require(report["human_review_required"] is expected["human_review_required"], f"{case_id} review flag mismatch")
    summary = report["summary"]
    require(summary["totals_status"] == expected["totals_status"], f"{case_id} totals status mismatch")
    require(summary["open_finding_count"] == expected["open_finding_count"], f"{case_id} open count mismatch")
    require([value["finding_code"] for value in report["findings"]] == expected["finding_codes"], f"{case_id} finding order/code mismatch")
    require(report["findings"] == sorted(report["findings"], key=lambda value: value["finding_id"]), f"{case_id} findings are unstable")
    require(report["unresolved_assumptions"] == [], f"{case_id} introduced an assumption")
    require(report["source_index"][0]["source_scope"] == "REPORT_POLICY", f"{case_id} report source is missing")
    require(len(report["source_index"]) == 4, f"{case_id} source scopes are incomplete")
    require(len(report["evidence_index"]) == 1, f"{case_id} evidence index is incomplete")
    if expected["totals_status"] == "FINAL":
        for field in ("expected_amount", "invoiced_amount", "paid_amount"):
            require(summary[field] == expected[field], f"{case_id} {field} mismatch")
        require(len(report["findings"]) == 3, f"{case_id} must have three decided dimensions")
        trace = report["charge_results"][0]["audit_result"]["expected_charge_trace"]["calculation"]
        require(trace["operation"] == "MULTIPLY" and trace["expected_amount"] == summary["expected_amount"], f"{case_id} expected math trace mismatch")
    else:
        for field in ("currency", "expected_amount", "invoiced_amount", "paid_amount", "billing_variance", "payment_variance", "realized_variance"):
            require(field not in summary, f"{case_id} blocked summary exposed {field}")
        require(any(expected["reason_contains"] in value.get("reason_code", "") for value in report["findings"]), f"{case_id} blocker reason mismatch")

    serialized = serialize_audit_report(report)
    require(serialized == serialize_audit_report(report), f"{case_id} serialization is unstable")
    require(json.loads(serialized) == report, f"{case_id} serialization does not round-trip")
    require("\n" not in serialized, f"{case_id} serialization is not canonical compact JSON")


def validate_tamper_rejection(report: dict) -> None:
    probes = [
        ("schema", "schema_version", "audit-report-envelope.tampered"),
        ("data status", "run.data_status", "authorized_sanitized"),
        ("adapter", "charge_results.0.adapter.version", "tampered"),
        ("expected math", "charge_results.0.audit_result.expected_charge_trace.calculation.expected_amount", "198.51"),
        ("aggregate total", "summary.expected_amount", "198.51"),
        ("finding code", "findings.0.finding_code", "OVERBILLED"),
        ("explanation", "findings.0.explanation", "AI says this is fine."),
        ("source", "source_index.0.references.0.document_path", "tampered.md"),
        ("evidence", "evidence_index.0.expected_charge_evidence_link_ids.0", "EVL-TAMPERED"),
    ]
    for label, path, value in probes:
        tampered = copy.deepcopy(report)
        set_path(tampered, path, value)
        try:
            validate_audit_report(tampered)
        except AuditReportError:
            print(f"PASS report tamper rejected: {label}")
            continue
        raise ValidationError(f"report tamper was accepted: {label}")

    reordered = copy.deepcopy(report)
    reordered["findings"].reverse()
    try:
        validate_audit_report(reordered)
    except AuditReportError:
        print("PASS report tamper rejected: finding order")
    else:
        raise ValidationError("report tamper was accepted: finding order")


def validate_request_rejection(valid_request: dict) -> None:
    probes = []
    unknown = copy.deepcopy(valid_request)
    unknown["charge_requests"][0]["adapter_id"] = "UNKNOWN-ADAPTER"
    probes.append(("unknown adapter", unknown))
    cutoff = copy.deepcopy(valid_request)
    cutoff["as_of_at"] = "2026-06-29T23:59:59Z"
    probes.append(("cutoff mismatch", cutoff))
    duplicate = copy.deepcopy(valid_request)
    duplicate["charge_requests"].append(copy.deepcopy(duplicate["charge_requests"][0]))
    duplicate["charge_requests"][1]["charge_instance_id"] = "ITEM-28A-DUPLICATE"
    probes.append(("duplicate charge family", duplicate))
    for label, request in probes:
        try:
            build_audit_report(request)
        except AuditReportError:
            print(f"PASS report request rejected: {label}")
            continue
        raise ValidationError(f"report request was accepted: {label}")


def main() -> int:
    try:
        validate_policy_contract()
        suite = load_json(FIXTURE_PATH)
        require(suite.get("fixture_set") == "SYNTHETIC_DETERMINISTIC_AUDIT_REPORT_CASES", "fixture set is not labeled synthetic")
        audit_suite_path = (ROOT / suite["audit_suite_path"]).resolve()
        require(audit_suite_path.is_relative_to(ROOT), "audit suite path escapes repository")
        audit_suite = load_json(audit_suite_path)
        rating_base = load_json((ROOT / audit_suite["rating_fixture_path"]).resolve())
        audit_base = load_json((ROOT / audit_suite["audit_fixture_path"]).resolve())
        require(rating_base.get("data_status") == "SYNTHETIC" and audit_base.get("data_status") == "SYNTHETIC", "report bases must be synthetic")
        audit_fixtures = {value["id"]: value for value in audit_suite["cases"]}

        tamper_baseline = None
        valid_request = None
        cases = suite.get("cases")
        require(isinstance(cases, list) and cases, "report suite requires cases")
        for fixture in cases:
            case_id = fixture["id"]
            audit_fixture = audit_fixtures.get(fixture["audit_case_id"])
            require(isinstance(audit_fixture, dict), f"{case_id} references unknown audit case")
            audit_case = build_audit_case(audit_suite, audit_fixture, rating_base, audit_base)
            request = {
                "audit_run_id": case_id,
                "data_status": "synthetic",
                "as_of_at": audit_suite["as_of_at"],
                "charge_requests": [
                    {
                        "charge_instance_id": "ITEM-28A",
                        "adapter_id": ITEM_28A_ADAPTER_ID,
                        "audit_case": audit_case,
                    }
                ],
            }
            report = build_audit_report(request)
            validate_report_case(report, fixture["expected"], case_id)
            print(f"PASS {case_id} {report['status']} canonical report")
            if case_id == "REPORT-28A-CLOSED":
                tamper_baseline = report
                valid_request = request

        require(tamper_baseline is not None and valid_request is not None, "report tamper baseline was not produced")
        validate_tamper_rejection(tamper_baseline)
        validate_request_rejection(valid_request)
        print(f"PASS all {len(cases)} audit-report cases, 10 output-tamper probes, and 3 request-contract probes")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, AuditReportError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

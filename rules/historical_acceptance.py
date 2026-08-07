"""Execute deterministic case benchmarks without overstating M6 acceptance."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from typing import Callable

from rules.audit_report import (
    ITEM_28A_ADAPTER_ID,
    ITEM_28B_ADAPTER_ID,
    AuditReportError,
    build_audit_report,
    validate_audit_report,
)
from rules.item_28a_extra_pickup import (
    INTERPRETATION_DECISION_ID as ITEM_28A_DECISION_ID,
    rate_item_28a_extra_pickups,
)
from rules.item_28b_extra_delivery import (
    INTERPRETATION_DECISION_ID as ITEM_28B_DECISION_ID,
    rate_item_28b_extra_deliveries,
)
from rules.historical_intake import HistoricalIntakeError, validate_historical_intake_envelope


ACCEPTANCE_SCHEMA_VERSION = "historical-acceptance-report.v1"
ACCEPTANCE_POLICY_ID = "HISTORICAL-ACCEPTANCE-PIPELINE-V1"
ACCEPTANCE_POLICY_VERSION = "2026-08-07.3"
REQUIRED_HISTORICAL_CASE_COUNT = 25

SOURCE_STRUCTURED_SYNTHETIC = "SOURCE_STRUCTURED_SYNTHETIC"
PUBLIC_PRECEDENT = "PUBLIC_PRECEDENT"
AUTHORIZED_SANITIZED_HISTORICAL = "AUTHORIZED_SANITIZED_HISTORICAL"
EXECUTABLE_AUDIT_CASE = "EXECUTABLE_AUDIT_CASE"
PUBLIC_PRECEDENT_REFERENCE = "PUBLIC_PRECEDENT_REFERENCE"

ACCEPTANCE_POLICY_PROVENANCE = (
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
        "source_id": "HISTORICAL-ACCEPTANCE-PIPELINE-POLICY",
        "document_path": "docs/historical-acceptance-pipeline.md",
        "document_version": ACCEPTANCE_POLICY_VERSION,
        "effective_period": "2026-08-07/open",
        "locator": "Corpus tiers through completion gate",
        "retrieval_date": "2026-08-07",
        "interpretation_status": "approved_internal_implementation_policy",
    },
)

PROVENANCE_FIELDS = {
    "source_id",
    "document_version",
    "effective_period",
    "locator",
    "retrieval_date",
    "interpretation_status",
}
FORBIDDEN_SENSITIVE_KEYS = {
    "accountnumber",
    "bankaccount",
    "birthdate",
    "creditcardnumber",
    "customername",
    "dateofbirth",
    "dodid",
    "edipi",
    "emailaddress",
    "firstname",
    "financialaccount",
    "fullname",
    "governmentidentifier",
    "hiddendocumentmetadata",
    "lastname",
    "maidenname",
    "membername",
    "personidentifier",
    "personalidentifier",
    "phonenumber",
    "routingnumber",
    "servicemembername",
    "shippername",
    "signature",
    "socialsecuritynumber",
    "ssn",
    "streetaddress",
}
KEY_NORMALIZER = re.compile(r"[^a-z0-9]+")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class HistoricalAcceptanceError(ValueError):
    """Raised when a corpus request, case bundle, or report is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HistoricalAcceptanceError(message)


def _instant(value: object, label: str) -> datetime:
    _require(isinstance(value, str) and value, f"{label} must be an ISO instant")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HistoricalAcceptanceError(f"{label} must be an ISO instant") from exc
    _require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return parsed


def _date(value: object, label: str) -> date:
    _require(isinstance(value, str) and value, f"{label} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HistoricalAcceptanceError(f"{label} must be an ISO date") from exc


def _reject_binary_floats(value: object, path: str = "request") -> None:
    _require(not isinstance(value, float), f"{path} contains a binary floating-point value")
    if isinstance(value, dict):
        for key, child in value.items():
            _reject_binary_floats(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_binary_floats(child, f"{path}.{index}")


def _find_sensitive_key(value: object, path: str = "case") -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = KEY_NORMALIZER.sub("", str(key).lower())
            if normalized in FORBIDDEN_SENSITIVE_KEYS:
                return f"{path}.{key}"
            found = _find_sensitive_key(child, f"{path}.{key}")
            if found:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = _find_sensitive_key(child, f"{path}.{index}")
            if found:
                return found
    return None


def _validate_provenance(value: object, label: str) -> list[dict]:
    _require(isinstance(value, list) and value, f"{label} provenance must be a nonempty list")
    result: list[dict] = []
    for index, reference in enumerate(value):
        _require(isinstance(reference, dict), f"{label} provenance {index} must be an object")
        _require(PROVENANCE_FIELDS <= set(reference), f"{label} provenance {index} is incomplete")
        for field in PROVENANCE_FIELDS:
            _require(isinstance(reference[field], str) and reference[field], f"{label} provenance {index} {field} is required")
        _date(reference["retrieval_date"], f"{label} provenance {index} retrieval_date")
        result.append(dict(reference))
    return result


def _validate_scope(scope: object) -> dict:
    _require(isinstance(scope, dict), "case scope is required")
    _require(scope.get("program_code") == "DP3", "case is outside DP3 scope")
    _require(scope.get("domestic_indicator") is True, "case is outside domestic scope")
    _require(scope.get("billing_relationship") == "TSP_TO_GOVERNMENT", "case billing relationship is out of scope")
    _require(scope.get("review_mode") == "READ_ONLY_POST_AUDIT", "case review mode is out of scope")
    _require(scope.get("shipment_status") == "COMPLETED", "case shipment must be completed")
    _validate_provenance(scope.get("provenance"), "case scope")
    return dict(scope)


def _validate_intake(case: dict, tier: str, data_status: str, evaluated_at: datetime) -> dict:
    intake = case.get("intake_control")
    _require(isinstance(intake, dict), "case intake_control is required")
    _validate_provenance(intake.get("provenance"), "case intake control")
    _instant(intake.get("reviewed_at"), "intake reviewed_at")
    _require(isinstance(intake.get("reviewer_role"), str) and intake["reviewer_role"], "intake reviewer_role is required")
    _require(intake.get("sensitive_data_review_status") == "PASSED", "sensitive-data review must pass before execution")
    _require(intake.get("prohibited_data_present") is False, "case declares prohibited sensitive data")

    if tier == SOURCE_STRUCTURED_SYNTHETIC:
        _require(data_status == "synthetic", "synthetic tier must use synthetic data_status")
        _require(intake.get("authorization_status") == "NOT_APPLICABLE_SYNTHETIC", "synthetic authorization status mismatch")
        _require(intake.get("sanitization_status") == "SYNTHETIC_NO_REAL_DATA", "synthetic sanitization status mismatch")
        _require("historical_intake_envelope" not in intake, "synthetic case cannot carry a historical intake envelope")
    elif tier == AUTHORIZED_SANITIZED_HISTORICAL:
        _require(data_status == "authorized_sanitized", "historical tier must use authorized_sanitized data_status")
        _require(intake.get("authorization_status") == "WRITTEN_AUTHORIZATION_VERIFIED", "historical case lacks verified written authorization")
        _require(intake.get("sanitization_status") == "VERIFIED_SANITIZED_BEFORE_INGEST", "historical case lacks pre-ingest sanitization verification")
        reference = intake.get("authorization_reference_id")
        _require(isinstance(reference, str) and reference, "historical authorization reference is required")
        try:
            envelope = validate_historical_intake_envelope(intake.get("historical_intake_envelope"), evaluated_at.isoformat())
        except HistoricalIntakeError as exc:
            raise HistoricalAcceptanceError(f"historical intake envelope rejected: {exc}") from exc
        _require(envelope["authorization"]["reference_id"] == reference, "historical authorization reference differs from intake envelope")
    else:
        raise HistoricalAcceptanceError(f"unsupported executable corpus tier {tier}")
    return dict(intake)


def _validate_outcome_label(label: object, tier: str, evaluated_at: datetime) -> dict:
    _require(isinstance(label, dict), "expected outcome label is required")
    _require(isinstance(label.get("label_id"), str) and label["label_id"], "outcome label id is required")
    recorded_at = _instant(label.get("recorded_at"), "outcome label recorded_at")
    approved_at = _instant(label.get("approved_at"), "outcome label approved_at")
    _require(recorded_at <= approved_at <= evaluated_at, "outcome label chronology is invalid")
    _require(label.get("creation_method") == "INDEPENDENTLY_AUTHORED_BEFORE_EXECUTION", "engine-derived outcome labels are prohibited")
    _require(isinstance(label.get("reviewer_role"), str) and label["reviewer_role"], "outcome reviewer_role is required")
    _validate_provenance(label.get("provenance"), "outcome label")
    if tier == SOURCE_STRUCTURED_SYNTHETIC:
        _require(label.get("approval_status") == "APPROVED_SYNTHETIC_ORACLE", "synthetic outcome label is not approved")
        _require(label.get("approval_basis") == "INTERNAL_SYNTHETIC_DESIGN", "synthetic outcome approval basis mismatch")
    elif tier == AUTHORIZED_SANITIZED_HISTORICAL:
        _require(label.get("approval_status") == "EXPERT_APPROVED", "historical outcome is not expert approved")
        _require(label.get("approval_basis") == "INDEPENDENT_EXPERT_REVIEW", "historical outcome approval basis mismatch")
    expected = label.get("expected_projection")
    _require(isinstance(expected, dict), "outcome expected_projection is required")
    return dict(label)


RatingEvaluator = Callable[[dict], dict]
RATING_ADAPTERS: dict[str, tuple[str, RatingEvaluator]] = {
    ITEM_28A_ADAPTER_ID: (ITEM_28A_DECISION_ID, rate_item_28a_extra_pickups),
    ITEM_28B_ADAPTER_ID: (ITEM_28B_DECISION_ID, rate_item_28b_extra_deliveries),
}


def _outcome_projection(report: dict) -> dict:
    summary_fields = (
        "charge_count",
        "final_charge_count",
        "blocked_charge_count",
        "finding_count",
        "open_finding_count",
        "totals_status",
        "currency",
        "expected_amount",
        "invoiced_amount",
        "paid_amount",
        "billing_variance",
        "payment_variance",
        "realized_variance",
    )
    summary = {field: report["summary"][field] for field in summary_fields if field in report["summary"]}
    charges: list[dict] = []
    for charge in report["charge_results"]:
        result = charge["audit_result"]
        projected = {
            "charge_instance_id": charge["charge_instance_id"],
            "adapter_id": charge["adapter"]["id"],
            "audit_status": result["status"],
        }
        if result["status"] == "BLOCKED":
            projected["blocked_reasons"] = list(result["blocked_reasons"])
        else:
            comparison = result["comparison"]
            finding = result["audit_finding"]
            projected.update(
                {
                    "expected_amount": comparison["expected_amount"],
                    "invoiced_amount": comparison["invoiced_amount"],
                    "paid_amount": comparison["paid_amount"],
                    "expected_quantity": comparison["expected_quantity"],
                    "invoiced_quantity": comparison["invoiced_quantity"],
                    "billing_finding_code": finding["billing_finding_code"],
                    "quantity_finding_code": finding["quantity_finding_code"],
                    "payment_finding_code": finding["payment_finding_code"],
                    "finding_status": finding["finding_status"],
                }
            )
        charges.append(projected)
    return {
        "report_status": report["status"],
        "human_review_required": report["human_review_required"],
        "summary": summary,
        "charges": charges,
    }


def _comparison(expected: dict, actual: dict) -> dict:
    if expected == actual:
        return {"status": "MATCH", "mismatch_paths": []}

    mismatches: list[str] = []

    def walk(left: object, right: object, path: str) -> None:
        if type(left) is not type(right):
            mismatches.append(path)
        elif isinstance(left, dict):
            keys = sorted(set(left) | set(right))
            for key in keys:
                if key not in left or key not in right:
                    mismatches.append(f"{path}.{key}")
                else:
                    walk(left[key], right[key], f"{path}.{key}")
        elif isinstance(left, list):
            if len(left) != len(right):
                mismatches.append(path)
            else:
                for index, (left_item, right_item) in enumerate(zip(left, right)):
                    walk(left_item, right_item, f"{path}.{index}")
        elif left != right:
            mismatches.append(path)

    walk(expected, actual, "expected_projection")
    return {"status": "MISMATCH", "mismatch_paths": sorted(set(mismatches))}


def _execute_audit_case(case: dict, evaluated_at: datetime) -> dict:
    tier = case.get("corpus_tier")
    _require(tier in {SOURCE_STRUCTURED_SYNTHETIC, AUTHORIZED_SANITIZED_HISTORICAL}, "executable case corpus tier is invalid")
    data_status = case.get("data_status")
    _require(data_status in {"synthetic", "authorized_sanitized"}, "executable case data_status is invalid")
    scope = _validate_scope(case.get("scope"))
    intake = _validate_intake(case, str(tier), str(data_status), evaluated_at)
    label = _validate_outcome_label(case.get("expected_outcome_label"), str(tier), evaluated_at)
    if tier == AUTHORIZED_SANITIZED_HISTORICAL:
        envelope = intake["historical_intake_envelope"]
        _require(
            envelope["approval_separation"]["outcome_reviewer_role"] == label["reviewer_role"],
            "historical outcome reviewer differs from intake envelope",
        )
    as_of_at = case.get("as_of_at")
    _instant(as_of_at, "case as_of_at")
    records = case.get("audit_records")
    _require(isinstance(records, dict), "case audit_records are required")
    sensitive_path = _find_sensitive_key(case)
    _require(sensitive_path is None, f"case contains prohibited sensitive field {sensitive_path}")

    inputs = case.get("charge_inputs")
    _require(isinstance(inputs, list) and inputs, "case charge_inputs must be a nonempty list")
    charge_requests: list[dict] = []
    for charge in inputs:
        _require(isinstance(charge, dict), "charge input must be an object")
        adapter_id = charge.get("adapter_id")
        instance_id = charge.get("charge_instance_id")
        _require(adapter_id in RATING_ADAPTERS, f"unsupported rating adapter {adapter_id}")
        _require(isinstance(instance_id, str) and instance_id, "charge_instance_id is required")
        decision_id, evaluator = RATING_ADAPTERS[str(adapter_id)]
        rating_case = charge.get("rating_case")
        _require(isinstance(rating_case, dict), f"{instance_id} rating_case is required")
        _require(rating_case.get("data_status") == data_status, f"{instance_id} rating data_status mismatch")
        _require(rating_case.get("interpretation_decision_id") == decision_id, f"{instance_id} interpretation decision mismatch")
        try:
            expected_result = evaluator(rating_case)
        except ValueError as exc:
            raise HistoricalAcceptanceError(f"{instance_id} rating rejected input: {exc}") from exc
        audit_records = charge.get("audit_records", records)
        _require(isinstance(audit_records, dict), f"{instance_id} audit_records must be an object")
        audit_case = {
            "case_id": f"{case['case_id']}:{instance_id}:AUDIT",
            "data_status": data_status,
            "as_of_at": as_of_at,
            "expected_charge_result": expected_result,
            "records": audit_records,
        }
        charge_requests.append(
            {
                "charge_instance_id": instance_id,
                "adapter_id": adapter_id,
                "audit_case": audit_case,
            }
        )

    try:
        report = build_audit_report(
            {
                "audit_run_id": f"{case['case_id']}:AUDIT",
                "data_status": data_status,
                "as_of_at": as_of_at,
                "charge_requests": charge_requests,
            }
        )
    except AuditReportError as exc:
        raise HistoricalAcceptanceError(f"case audit rejected input: {exc}") from exc
    actual_projection = _outcome_projection(report)
    comparison = _comparison(label["expected_projection"], actual_projection)
    eligible = tier == AUTHORIZED_SANITIZED_HISTORICAL
    return {
        "case_id": case["case_id"],
        "case_kind": EXECUTABLE_AUDIT_CASE,
        "corpus_tier": tier,
        "data_status": data_status,
        "scope": scope,
        "intake_control": intake,
        "expected_outcome_label": label,
        "execution_status": "EXECUTED",
        "outcome_comparison": comparison,
        "case_result": "PASS" if comparison["status"] == "MATCH" else "FAIL",
        "acceptance_eligible": eligible,
        "counts_toward_required_25": bool(eligible and comparison["status"] == "MATCH"),
        "audit_report": report,
        "unresolved_assumptions": [],
    }


def _register_public_precedent(case: dict) -> dict:
    _require(case.get("data_status") == "public", "public precedent data_status must be public")
    _require(case.get("archive_status") in {"CANDIDATE_NOT_ARCHIVED", "ARCHIVED_AUTHORITATIVE"}, "public precedent archive status is invalid")
    _require(case.get("scope_assessment") in {"IN_SCOPE_PARTIAL", "OUT_OF_SCOPE_CONTEXT_ONLY", "PENDING_REVIEW"}, "public precedent scope assessment is invalid")
    _validate_provenance(case.get("source_provenance"), "public precedent")
    _require(case.get("sensitive_data_status") in {"URL_ONLY_NOT_INGESTED", "SANITIZED_DERIVED_EXTRACT"}, "public precedent sensitive-data status is invalid")
    if case["archive_status"] == "CANDIDATE_NOT_ARCHIVED":
        _require(case["sensitive_data_status"] == "URL_ONLY_NOT_INGESTED", "unarchived precedent must remain URL-only")
        benchmark_status = "PENDING_AUTHORITATIVE_ARCHIVE"
    else:
        _require(case["sensitive_data_status"] == "SANITIZED_DERIVED_EXTRACT", "archived precedent requires a sanitized derived extract")
        for field in ("raw_artifact_path", "sanitized_extract_path", "extraction_method"):
            _require(isinstance(case.get(field), str) and case[field], f"archived precedent {field} is required")
        _require(
            isinstance(case.get("raw_artifact_sha256"), str) and SHA256_RE.fullmatch(case["raw_artifact_sha256"]) is not None,
            "archived precedent artifact hash is invalid",
        )
        _require(
            isinstance(case.get("sanitized_extract_sha256"), str) and SHA256_RE.fullmatch(case["sanitized_extract_sha256"]) is not None,
            "archived precedent sanitized extract hash is invalid",
        )
        benchmark_status = "REGISTERED_REFERENCE_ONLY"
    prohibited = _find_sensitive_key(case)
    _require(prohibited is None, f"public precedent contains prohibited sensitive field {prohibited}")
    result = {
        "case_id": case["case_id"],
        "case_kind": PUBLIC_PRECEDENT_REFERENCE,
        "corpus_tier": PUBLIC_PRECEDENT,
        "data_status": "public",
        "archive_status": case["archive_status"],
        "scope_assessment": case["scope_assessment"],
        "source_provenance": list(case["source_provenance"]),
        "sensitive_data_status": case["sensitive_data_status"],
        "execution_status": "NOT_EXECUTED_REFERENCE_ONLY",
        "benchmark_status": benchmark_status,
        "case_result": "NOT_APPLICABLE",
        "acceptance_eligible": False,
        "counts_toward_required_25": False,
        "unresolved_assumptions": [],
    }
    if case["archive_status"] == "ARCHIVED_AUTHORITATIVE":
        result.update(
            {
                "raw_artifact_path": case["raw_artifact_path"],
                "raw_artifact_sha256": case["raw_artifact_sha256"],
                "sanitized_extract_path": case["sanitized_extract_path"],
                "sanitized_extract_sha256": case["sanitized_extract_sha256"],
                "extraction_method": case["extraction_method"],
            }
        )
    return result


def _compose_report(run_id: str, evaluated_at: str, case_results: list[dict]) -> dict:
    authorized = [value for value in case_results if value["corpus_tier"] == AUTHORIZED_SANITIZED_HISTORICAL]
    passing_authorized = [value for value in authorized if value["case_result"] == "PASS"]
    failing_authorized = [value for value in authorized if value["case_result"] == "FAIL"]
    synthetic = [value for value in case_results if value["corpus_tier"] == SOURCE_STRUCTURED_SYNTHETIC]
    public = [value for value in case_results if value["corpus_tier"] == PUBLIC_PRECEDENT]
    pending_public = [value for value in public if value["benchmark_status"] == "PENDING_AUTHORITATIVE_ARCHIVE"]
    remaining = max(0, REQUIRED_HISTORICAL_CASE_COUNT - len(passing_authorized))
    completion_ready = len(passing_authorized) >= REQUIRED_HISTORICAL_CASE_COUNT and not failing_authorized
    return {
        "schema_version": ACCEPTANCE_SCHEMA_VERSION,
        "pipeline_policy": {
            "id": ACCEPTANCE_POLICY_ID,
            "version": ACCEPTANCE_POLICY_VERSION,
            "required_historical_case_count": REQUIRED_HISTORICAL_CASE_COUNT,
            "financial_calculation_method": "REGISTERED_DETERMINISTIC_RULES_ONLY",
            "historical_count_method": "AUTHORIZED_SANITIZED_EXPERT_LABELED_MATCHES_ONLY",
        },
        "run": {"corpus_run_id": run_id, "evaluated_at": evaluated_at},
        "status": "OPERATIONAL",
        "completion_status": "READY" if completion_ready else "NOT_READY",
        "summary": {
            "total_case_count": len(case_results),
            "source_structured_synthetic_case_count": len(synthetic),
            "public_precedent_case_count": len(public),
            "public_precedent_pending_archive_count": len(pending_public),
            "authorized_historical_case_count": len(authorized),
            "passing_authorized_historical_case_count": len(passing_authorized),
            "failing_authorized_historical_case_count": len(failing_authorized),
            "required_historical_case_count": REQUIRED_HISTORICAL_CASE_COUNT,
            "remaining_passing_historical_case_count": remaining,
        },
        "case_results": case_results,
        "provenance": [dict(value) for value in ACCEPTANCE_POLICY_PROVENANCE],
        "unresolved_assumptions": [],
    }


def build_historical_acceptance_report(request: dict) -> dict:
    """Execute benchmark cases and enforce the ratified 25-case completion gate."""

    _require(isinstance(request, dict), "acceptance request must be an object")
    _reject_binary_floats(request)
    run_id = request.get("corpus_run_id")
    evaluated_at = request.get("evaluated_at")
    _require(isinstance(run_id, str) and run_id, "corpus_run_id is required")
    evaluated = _instant(evaluated_at, "evaluated_at")
    cases = request.get("cases")
    _require(isinstance(cases, list) and cases, "acceptance request requires cases")
    results: list[dict] = []
    seen: set[str] = set()
    for case in cases:
        _require(isinstance(case, dict), "acceptance case must be an object")
        case_id = case.get("case_id")
        _require(isinstance(case_id, str) and case_id and case_id not in seen, "acceptance case identity is invalid")
        kind = case.get("case_kind")
        if kind == EXECUTABLE_AUDIT_CASE:
            result = _execute_audit_case(case, evaluated)
        elif kind == PUBLIC_PRECEDENT_REFERENCE:
            _require(case.get("corpus_tier") == PUBLIC_PRECEDENT, "public precedent tier mismatch")
            result = _register_public_precedent(case)
        else:
            raise HistoricalAcceptanceError(f"unknown case kind {kind}")
        results.append(result)
        seen.add(case_id)
    results.sort(key=lambda value: value["case_id"])
    report = _compose_report(str(run_id), str(evaluated_at), results)
    validate_historical_acceptance_report(report)
    return report


def validate_historical_acceptance_report(report: object) -> None:
    """Reject an altered acceptance report or an invalid embedded audit report."""

    _require(isinstance(report, dict), "acceptance report must be an object")
    _require(report.get("schema_version") == ACCEPTANCE_SCHEMA_VERSION, "acceptance schema version mismatch")
    run = report.get("run")
    _require(isinstance(run, dict), "acceptance run metadata is missing")
    _require(isinstance(run.get("corpus_run_id"), str) and run["corpus_run_id"], "acceptance run id is missing")
    _instant(run.get("evaluated_at"), "acceptance evaluated_at")
    results = report.get("case_results")
    _require(isinstance(results, list) and results, "acceptance case results are missing")
    _require(results == sorted(results, key=lambda value: value.get("case_id", "")), "acceptance case results are not ordered")
    _require(len({value.get("case_id") for value in results}) == len(results), "acceptance case results contain duplicate ids")
    evaluated = _instant(run.get("evaluated_at"), "acceptance evaluated_at")
    for result in results:
        _require(isinstance(result, dict), "acceptance case result must be an object")
        if result.get("case_kind") == EXECUTABLE_AUDIT_CASE:
            tier = result.get("corpus_tier")
            data_status = result.get("data_status")
            _require(tier in {SOURCE_STRUCTURED_SYNTHETIC, AUTHORIZED_SANITIZED_HISTORICAL}, "executable result tier is invalid")
            _require(data_status in {"synthetic", "authorized_sanitized"}, "executable result data status is invalid")
            _validate_scope(result.get("scope"))
            intake = _validate_intake(result, str(tier), str(data_status), evaluated)
            label = _validate_outcome_label(result.get("expected_outcome_label"), str(tier), evaluated)
            if tier == AUTHORIZED_SANITIZED_HISTORICAL:
                _require(
                    intake["historical_intake_envelope"]["approval_separation"]["outcome_reviewer_role"] == label["reviewer_role"],
                    "historical outcome reviewer differs from intake envelope",
                )
            _require(result.get("execution_status") == "EXECUTED", f"{result.get('case_id')} execution status mismatch")
            validate_audit_report(result.get("audit_report"))
            _require(result["audit_report"]["run"]["data_status"] == data_status, f"{result.get('case_id')} embedded audit data status mismatch")
            actual = _outcome_projection(result["audit_report"])
            expected = result.get("expected_outcome_label", {}).get("expected_projection")
            comparison = _comparison(expected, actual)
            _require(result.get("outcome_comparison") == comparison, f"{result.get('case_id')} outcome comparison was altered")
            _require(result.get("case_result") == ("PASS" if comparison["status"] == "MATCH" else "FAIL"), f"{result.get('case_id')} case result mismatch")
            eligible = result.get("corpus_tier") == AUTHORIZED_SANITIZED_HISTORICAL
            _require(result.get("acceptance_eligible") is eligible, f"{result.get('case_id')} eligibility mismatch")
            _require(result.get("counts_toward_required_25") is bool(eligible and comparison["status"] == "MATCH"), f"{result.get('case_id')} count gate mismatch")
        elif result.get("case_kind") == PUBLIC_PRECEDENT_REFERENCE:
            expected_public = _register_public_precedent(result)
            _require(result == expected_public, f"{result.get('case_id')} public precedent projection was altered")
            _require(result.get("acceptance_eligible") is False and result.get("counts_toward_required_25") is False, "public precedent counted toward acceptance")
            _require(result.get("execution_status") == "NOT_EXECUTED_REFERENCE_ONLY", "public precedent execution status mismatch")
        else:
            raise HistoricalAcceptanceError("acceptance report contains unknown case result kind")
    expected_report = _compose_report(run["corpus_run_id"], run["evaluated_at"], results)
    _require(report == expected_report, "acceptance report summary, policy, provenance, or case projection was altered")


def serialize_historical_acceptance_report(report: dict) -> str:
    """Return canonical JSON after validating the report."""

    validate_historical_acceptance_report(report)
    return json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":"))

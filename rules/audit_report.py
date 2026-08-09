"""Build and verify deterministic post-audit report envelopes."""

from __future__ import annotations

import json
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from rules.item_28a_extra_pickup import (
    CURRENCY as ITEM_28A_CURRENCY,
    INTERPRETATION_DECISION_ID as ITEM_28A_DECISION_ID,
    ITEM_CODE as ITEM_28A_CODE,
    QUANTITY_UNIT as ITEM_28A_QUANTITY_UNIT,
    RULE_PACKAGE_ID as ITEM_28A_RULE_PACKAGE_ID,
    UNIT_RATE as ITEM_28A_UNIT_RATE,
)
from rules.item_28a_post_audit import (
    AUDIT_POLICY_ID as ITEM_28A_AUDIT_POLICY_ID,
    AUDIT_POLICY_PROVENANCE as ITEM_28A_AUDIT_POLICY_PROVENANCE,
    AUDIT_POLICY_VERSION as ITEM_28A_AUDIT_POLICY_VERSION,
    AUDIT_SOURCE_PROVENANCE as ITEM_28A_AUDIT_SOURCE_PROVENANCE,
    AuditInputError,
    audit_item_28a,
)
from rules.item_28a_extra_pickup import PROVENANCE as ITEM_28A_EXPECTED_PROVENANCE
from rules.item_28b_extra_delivery import (
    CURRENCY as ITEM_28B_CURRENCY,
    INTERPRETATION_DECISION_ID as ITEM_28B_DECISION_ID,
    ITEM_CODE as ITEM_28B_CODE,
    PROVENANCE as ITEM_28B_EXPECTED_PROVENANCE,
    QUANTITY_UNIT as ITEM_28B_QUANTITY_UNIT,
    RULE_PACKAGE_ID as ITEM_28B_RULE_PACKAGE_ID,
    UNIT_RATE as ITEM_28B_UNIT_RATE,
)
from rules.item_28b_post_audit import (
    AUDIT_POLICY_ID as ITEM_28B_AUDIT_POLICY_ID,
    AUDIT_POLICY_PROVENANCE as ITEM_28B_AUDIT_POLICY_PROVENANCE,
    AUDIT_POLICY_VERSION as ITEM_28B_AUDIT_POLICY_VERSION,
    AUDIT_SOURCE_PROVENANCE as ITEM_28B_AUDIT_SOURCE_PROVENANCE,
    audit_item_28b,
)


REPORT_SCHEMA_VERSION = "audit-report-envelope.v1"
REPORT_POLICY_ID = "AUDIT-REPORT-ENVELOPE-V1"
REPORT_POLICY_VERSION = "2026-08-03.1"
REPORT_POLICY_PROVENANCE = (
    {
        "source_id": "GOAL-RATIFIED-2026-08-03",
        "document_path": "goal.md",
        "document_version": "ratified 2026-08-03",
        "effective_period": "2026-08-03/open",
        "locator": "Outcome; Quality bar; Completion verifier",
        "retrieval_date": "2026-08-03",
        "interpretation_status": "ratified_internal_policy",
    },
    {
        "source_id": "AUDIT-REPORT-POLICY",
        "document_path": "docs/audit-report-policy.md",
        "document_version": REPORT_POLICY_VERSION,
        "effective_period": "2026-08-03/open",
        "locator": "Envelope contract through AI boundary",
        "retrieval_date": "2026-08-03",
        "interpretation_status": "approved_internal_policy",
    },
)

ITEM_28A_ADAPTER_ID = "CHARGE-ADAPTER-DP3-ITEM-28A-V1"
ITEM_28A_ADAPTER_VERSION = "2026-08-03.1"
ITEM_28B_ADAPTER_ID = "CHARGE-ADAPTER-DP3-ITEM-28B-V1"
ITEM_28B_ADAPTER_VERSION = "2026-08-04.1"
REPORT_CURRENCY = "USD"
SIGNED_DECIMAL_RE = re.compile(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?$")


class AuditReportError(ValueError):
    """Raised when a report request or serialized report is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditReportError(message)


def _instant(value: object, label: str) -> datetime:
    _require(isinstance(value, str) and value, f"{label} must be an ISO instant")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuditReportError(f"{label} must be an ISO instant") from exc
    _require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return parsed


def _decimal(value: object, label: str) -> Decimal:
    _require(isinstance(value, str) and bool(SIGNED_DECIMAL_RE.fullmatch(value)), f"{label} must be a canonical exact-decimal string")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise AuditReportError(f"{label} must be an exact decimal") from exc


def _money(value: object, label: str) -> Decimal:
    amount = _decimal(value, label)
    _require(amount == amount.quantize(Decimal("0.01")), f"{label} must use no more than two decimal places")
    return amount


def _money_text(value: Decimal) -> str:
    return f"{value:.2f}"


def _sorted_unique_strings(value: object, label: str) -> list[str]:
    _require(isinstance(value, list), f"{label} must be a list")
    _require(all(isinstance(item, str) and item for item in value), f"{label} must contain nonempty strings")
    _require(value == sorted(set(value)), f"{label} must be sorted and unique")
    return value


def _validate_occurrence_result(result: object, contract: dict) -> dict:
    label = contract["label"]
    item_code = contract["item_code"]
    quantity_unit = contract["quantity_unit"]
    currency = contract["currency"]
    unit_rate = contract["unit_rate"]
    _require(isinstance(result, dict), f"{label} adapter result must be an object")
    policy = result.get("audit_policy")
    _require(
        isinstance(policy, dict)
        and policy.get("id") == contract["audit_policy_id"]
        and policy.get("version") == contract["audit_policy_version"],
        f"{label} audit policy mismatch",
    )
    _require(
        policy.get("billing_variance_expression") == "invoiced_amount - expected_amount"
        and policy.get("payment_variance_expression") == "paid_amount - invoiced_amount"
        and policy.get("realized_variance_expression") == "paid_amount - expected_amount",
        f"{label} variance contract mismatch",
    )
    charge = result.get("audited_charge")
    _require(
        isinstance(charge, dict)
        and charge.get("item_code") == item_code
        and charge.get("quantity_unit") == quantity_unit
        and charge.get("currency") == currency
        and charge.get("expected_charge_rule_package_id") == contract["rule_package_id"]
        and charge.get("interpretation_decision_id") == contract["interpretation_decision_id"],
        f"{label} audited charge contract mismatch",
    )
    _require(
        result.get("provenance")
        == {
            "audit_policy": [dict(value) for value in contract["audit_policy_provenance"]],
            "observed_invoice_payment": [dict(value) for value in contract["audit_source_provenance"]],
            "expected_charge": [dict(value) for value in contract["expected_provenance"]],
        },
        f"{label} provenance mismatch",
    )
    _require(result.get("unresolved_assumptions") == [], f"{label} result contains unresolved assumptions")
    _require(result.get("data_status") in {"synthetic", "authorized_sanitized"}, f"{label} data status is invalid")
    _instant(result.get("as_of_at"), f"{label} as_of_at")

    trace = result.get("expected_charge_trace")
    _require(isinstance(trace, dict) and trace.get("status") in {"FINAL", "BLOCKED"}, f"{label} expected trace is invalid")
    _require(isinstance(trace.get("result_case_id"), str) and trace["result_case_id"], f"{label} expected result id is missing")
    _require(isinstance(trace.get("shipment_id"), str) and trace["shipment_id"], f"{label} expected shipment id is missing")
    _sorted_unique_strings(trace.get("reviewed_evidence_link_ids"), f"{label} expected evidence ids")
    if trace["status"] == "FINAL":
        calculation = trace.get("calculation")
        _require(isinstance(calculation, dict), f"{label} expected calculation is missing")
        quantity = _decimal(calculation.get("quantity"), f"{label} expected quantity")
        observed_unit_rate = _money(calculation.get("unit_rate"), f"{label} unit rate")
        expected = _money(calculation.get("expected_amount"), f"{label} expected amount")
        _require(
            calculation.get("operation") == "MULTIPLY"
            and calculation.get("quantity_unit") == quantity_unit
            and calculation.get("currency") == currency
            and calculation.get("unrounded_amount") == calculation.get("expected_amount")
            and observed_unit_rate == unit_rate
            and quantity * observed_unit_rate == expected,
            f"{label} expected calculation mismatch",
        )
    else:
        _require("calculation" not in trace, f"blocked {label} expected trace exposes a calculation")

    status = result.get("status")
    _require(status in {"FINAL", "BLOCKED"}, f"{label} audit status is invalid")
    if status == "BLOCKED":
        reasons = _sorted_unique_strings(result.get("blocked_reasons"), f"{label} blocked reasons")
        _require(reasons, f"blocked {label} result lacks a reason")
        _require(result.get("human_review_required") is True, f"blocked {label} result must require review")
        _require(result.get("audit_finding") == {"finding_code": "AUDIT_BLOCKED", "finding_status": "OPEN"}, f"blocked {label} finding mismatch")
        _require("comparison" not in result and "match" not in result, f"blocked {label} result exposes authoritative comparison")
        snapshot = result.get("input_snapshot", {})
        _require(isinstance(snapshot, dict), f"{label} input snapshot is invalid")
        _require(snapshot.get("shipment_id", trace["shipment_id"]) == trace["shipment_id"], f"blocked {label} shipment trace mismatch")
        return {"status": status, "shipment_id": trace["shipment_id"], "currency": currency}

    _require(trace["status"] == "FINAL", f"final {label} audit has a blocked expected trace")
    _require(result.get("human_review_required") is False, f"final {label} result unexpectedly requires review")
    comparison = result.get("comparison")
    finding = result.get("audit_finding")
    _require(isinstance(comparison, dict) and isinstance(finding, dict), f"final {label} result is incomplete")
    expected = _money(comparison.get("expected_amount"), "expected amount")
    invoiced = _money(comparison.get("invoiced_amount"), "invoiced amount")
    paid = _money(comparison.get("paid_amount"), "paid amount")
    _require(expected == _money(trace["calculation"]["expected_amount"], "traced expected amount"), "expected trace differs from comparison")
    _require(_money(comparison.get("billing_variance"), "billing variance") == invoiced - expected, "billing variance arithmetic mismatch")
    _require(_money(comparison.get("payment_variance"), "payment variance") == paid - invoiced, "payment variance arithmetic mismatch")
    _require(_money(comparison.get("realized_variance"), "realized variance") == paid - expected, "realized variance arithmetic mismatch")
    expected_quantity = _decimal(comparison.get("expected_quantity"), "expected quantity")
    invoiced_quantity = _decimal(comparison.get("invoiced_quantity"), "invoiced quantity")
    _require(_decimal(comparison.get("quantity_variance"), "quantity variance") == invoiced_quantity - expected_quantity, "quantity variance arithmetic mismatch")
    _require(comparison.get("currency") == currency and comparison.get("quantity_unit") == quantity_unit, "comparison units mismatch")

    match = result.get("match")
    _require(isinstance(match, dict) and match.get("match_status") in {"EXACT", "NO_MATCH"}, f"{label} match contract mismatch")
    matched = match["match_status"] == "EXACT"
    if expected > 0 and not matched:
        billing_code = "MISSING_EXPECTED_CHARGE"
    elif expected == 0 and matched:
        billing_code = "UNSUPPORTED_BILLED_CHARGE"
    elif expected == 0 and not matched:
        billing_code = "NO_CHARGE_EXPECTED_OR_BILLED"
    elif invoiced < expected:
        billing_code = "UNDERBILLED"
    elif invoiced > expected:
        billing_code = "OVERBILLED"
    else:
        billing_code = "CORRECTLY_BILLED"
    payment_code = (
        "NO_MATCHED_INVOICE_LINE" if not matched
        else "PAID_AS_INVOICED" if paid == invoiced
        else "UNPAID" if paid == 0
        else "PARTIALLY_PAID" if paid < invoiced
        else "OVERPAID"
    )
    quantity_code = "QUANTITY_MATCH" if invoiced_quantity == expected_quantity else "QUANTITY_MISMATCH"
    _require(finding.get("billing_finding_code") == billing_code, "billing finding code mismatch")
    _require(finding.get("payment_finding_code") == payment_code, "payment finding code mismatch")
    _require(finding.get("quantity_finding_code") == quantity_code, "quantity finding code mismatch")
    no_exception = billing_code in {"CORRECTLY_BILLED", "NO_CHARGE_EXPECTED_OR_BILLED"} and payment_code in {
        "PAID_AS_INVOICED",
        "NO_MATCHED_INVOICE_LINE",
    } and quantity_code == "QUANTITY_MATCH"
    _require(
        finding.get("finding_status") == ("CLOSED_NO_EXCEPTION" if no_exception else "OPEN"),
        f"{label} overall finding status mismatch",
    )
    snapshot = result.get("input_snapshot")
    _require(isinstance(snapshot, dict) and isinstance(snapshot.get("shipment_id"), str), f"{label} input snapshot is incomplete")
    _require(snapshot["shipment_id"] == trace["shipment_id"], f"{label} shipment trace mismatch")
    for field in ("invoice_evidence_link_ids", "payment_evidence_link_ids", "completeness_assertion_ids"):
        _sorted_unique_strings(snapshot.get(field), f"{label} {field}")
    return {"status": status, "shipment_id": snapshot["shipment_id"], "currency": currency}


ITEM_28A_REPORT_CONTRACT = {
    "label": "Item 28A",
    "item_code": ITEM_28A_CODE,
    "quantity_unit": ITEM_28A_QUANTITY_UNIT,
    "currency": ITEM_28A_CURRENCY,
    "unit_rate": ITEM_28A_UNIT_RATE,
    "interpretation_decision_id": ITEM_28A_DECISION_ID,
    "rule_package_id": ITEM_28A_RULE_PACKAGE_ID,
    "audit_policy_id": ITEM_28A_AUDIT_POLICY_ID,
    "audit_policy_version": ITEM_28A_AUDIT_POLICY_VERSION,
    "audit_policy_provenance": ITEM_28A_AUDIT_POLICY_PROVENANCE,
    "audit_source_provenance": ITEM_28A_AUDIT_SOURCE_PROVENANCE,
    "expected_provenance": ITEM_28A_EXPECTED_PROVENANCE,
}
ITEM_28B_REPORT_CONTRACT = {
    "label": "Item 28B",
    "item_code": ITEM_28B_CODE,
    "quantity_unit": ITEM_28B_QUANTITY_UNIT,
    "currency": ITEM_28B_CURRENCY,
    "unit_rate": ITEM_28B_UNIT_RATE,
    "interpretation_decision_id": ITEM_28B_DECISION_ID,
    "rule_package_id": ITEM_28B_RULE_PACKAGE_ID,
    "audit_policy_id": ITEM_28B_AUDIT_POLICY_ID,
    "audit_policy_version": ITEM_28B_AUDIT_POLICY_VERSION,
    "audit_policy_provenance": ITEM_28B_AUDIT_POLICY_PROVENANCE,
    "audit_source_provenance": ITEM_28B_AUDIT_SOURCE_PROVENANCE,
    "expected_provenance": ITEM_28B_EXPECTED_PROVENANCE,
}


def _validate_item_28a_result(result: object) -> dict:
    return _validate_occurrence_result(result, ITEM_28A_REPORT_CONTRACT)


def _validate_item_28b_result(result: object) -> dict:
    return _validate_occurrence_result(result, ITEM_28B_REPORT_CONTRACT)


ADAPTERS: dict[str, dict[str, object]] = {
    ITEM_28A_ADAPTER_ID: {
        "adapter_version": ITEM_28A_ADAPTER_VERSION,
        "charge_family": "DP3_ITEM_28A_EXTRA_PICKUP",
        "audit_policy_id": ITEM_28A_AUDIT_POLICY_ID,
        "evaluator": audit_item_28a,
        "validator": _validate_item_28a_result,
    },
    ITEM_28B_ADAPTER_ID: {
        "adapter_version": ITEM_28B_ADAPTER_VERSION,
        "charge_family": "DP3_ITEM_28B_EXTRA_DELIVERY",
        "audit_policy_id": ITEM_28B_AUDIT_POLICY_ID,
        "evaluator": audit_item_28b,
        "validator": _validate_item_28b_result,
    },
}


def _billing_explanation(comparison: dict, code: str, item_label: str) -> str:
    expected = comparison["expected_amount"]
    invoiced = comparison["invoiced_amount"]
    variance = comparison["billing_variance"]
    return f"{item_label} expected USD {expected}, invoiced USD {invoiced}, and has invoiced-minus-expected variance USD {variance}; finding {code}."


def _quantity_explanation(comparison: dict, code: str, item_label: str) -> str:
    return f"{item_label} expected {comparison['expected_quantity']} EA, invoiced {comparison['invoiced_quantity']} EA, and has quantity variance {comparison['quantity_variance']} EA; finding {code}."


def _payment_explanation(comparison: dict, code: str, item_label: str) -> str:
    return f"{item_label} invoiced USD {comparison['invoiced_amount']}, paid USD {comparison['paid_amount']}, and has paid-minus-invoiced variance USD {comparison['payment_variance']}; finding {code}."


def _evidence_record(instance_id: str, result: dict) -> dict:
    trace = result["expected_charge_trace"]
    snapshot = result.get("input_snapshot", {})
    return {
        "charge_instance_id": instance_id,
        "expected_charge_evidence_link_ids": list(trace["reviewed_evidence_link_ids"]),
        "invoice_evidence_link_ids": list(snapshot.get("invoice_evidence_link_ids", [])),
        "payment_evidence_link_ids": list(snapshot.get("payment_evidence_link_ids", [])),
        "completeness_assertion_ids": list(snapshot.get("completeness_assertion_ids", [])),
    }


def _compose_report(run_id: str, data_status: str, as_of_at: str, charge_results: list[dict]) -> dict:
    findings: list[dict] = []
    source_index = [
        {"source_scope": "REPORT_POLICY", "references": [dict(value) for value in REPORT_POLICY_PROVENANCE]}
    ]
    evidence_index: list[dict] = []
    shipment_ids: set[str] = set()
    final_results: list[dict] = []

    for charge in charge_results:
        instance_id = charge["charge_instance_id"]
        result = charge["audit_result"]
        contract = ADAPTERS[charge["adapter"]["id"]]
        validated = contract["validator"](result)  # type: ignore[operator]
        if validated["shipment_id"]:
            shipment_ids.add(validated["shipment_id"])
        source_index.extend(
            {
                "source_scope": scope,
                "charge_instance_id": instance_id,
                "references": result["provenance"][key],
            }
            for scope, key in (
                ("EXPECTED_CHARGE", "expected_charge"),
                ("CHARGE_AUDIT_POLICY", "audit_policy"),
                ("OBSERVED_INVOICE_PAYMENT", "observed_invoice_payment"),
            )
        )
        evidence_index.append(_evidence_record(instance_id, result))
        evidence_ids = sorted(
            set(
                evidence_index[-1]["expected_charge_evidence_link_ids"]
                + evidence_index[-1]["invoice_evidence_link_ids"]
                + evidence_index[-1]["payment_evidence_link_ids"]
            )
        )
        item_label = f"Item {result['audited_charge']['item_code']}"
        if result["status"] == "BLOCKED":
            for sequence, reason in enumerate(result["blocked_reasons"], start=1):
                findings.append(
                    {
                        "finding_id": f"{instance_id}:900:BLOCKER:{sequence:03d}",
                        "charge_instance_id": instance_id,
                        "dimension": "REVIEW_BLOCKER",
                        "finding_code": "AUDIT_BLOCKED",
                        "reason_code": reason,
                        "finding_status": "OPEN",
                        "explanation": f"{item_label} audit is blocked pending human review: {reason}.",
                        "evidence_link_ids": evidence_ids,
                    }
                )
            continue

        final_results.append(result)
        comparison = result["comparison"]
        finding = result["audit_finding"]
        dimensions = (
            ("001", "BILLING", finding["billing_finding_code"], _billing_explanation),
            ("002", "QUANTITY", finding["quantity_finding_code"], _quantity_explanation),
            ("003", "PAYMENT", finding["payment_finding_code"], _payment_explanation),
        )
        nonexceptions = {"CORRECTLY_BILLED", "NO_CHARGE_EXPECTED_OR_BILLED", "QUANTITY_MATCH", "PAID_AS_INVOICED", "NO_MATCHED_INVOICE_LINE"}
        for order, dimension, code, explain in dimensions:
            findings.append(
                {
                    "finding_id": f"{instance_id}:{order}:{dimension}",
                    "charge_instance_id": instance_id,
                    "dimension": dimension,
                    "finding_code": code,
                    "finding_status": "CLOSED_NO_EXCEPTION" if code in nonexceptions else "OPEN",
                    "explanation": explain(comparison, code, item_label),
                    "evidence_link_ids": evidence_ids,
                }
            )

    _require(len(shipment_ids) == 1, "an audit report must contain exactly one shipment")
    findings.sort(key=lambda value: value["finding_id"])
    blocked_count = len(charge_results) - len(final_results)
    summary = {
        "charge_count": len(charge_results),
        "final_charge_count": len(final_results),
        "blocked_charge_count": blocked_count,
        "finding_count": len(findings),
        "open_finding_count": sum(value["finding_status"] == "OPEN" for value in findings),
        "totals_status": "BLOCKED" if blocked_count else "FINAL",
    }
    if not blocked_count:
        expected = sum((_money(value["comparison"]["expected_amount"], "expected total component") for value in final_results), Decimal("0"))
        invoiced = sum((_money(value["comparison"]["invoiced_amount"], "invoiced total component") for value in final_results), Decimal("0"))
        paid = sum((_money(value["comparison"]["paid_amount"], "paid total component") for value in final_results), Decimal("0"))
        summary.update(
            {
                "currency": REPORT_CURRENCY,
                "expected_amount": _money_text(expected),
                "invoiced_amount": _money_text(invoiced),
                "paid_amount": _money_text(paid),
                "billing_variance": _money_text(invoiced - expected),
                "payment_variance": _money_text(paid - invoiced),
                "realized_variance": _money_text(paid - expected),
            }
        )
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_policy": {
            "id": REPORT_POLICY_ID,
            "version": REPORT_POLICY_VERSION,
            "explanation_method": "DETERMINISTIC_CODE_TEMPLATES",
            "aggregate_money_method": "EXACT_DECIMAL_ALL_OR_NOTHING",
        },
        "run": {
            "audit_run_id": run_id,
            "data_status": data_status,
            "as_of_at": as_of_at,
            "shipment_id": next(iter(shipment_ids)),
        },
        "status": "BLOCKED" if blocked_count else "FINAL",
        "human_review_required": bool(blocked_count or summary["open_finding_count"]),
        "summary": summary,
        "charge_results": charge_results,
        "findings": findings,
        "source_index": source_index,
        "evidence_index": evidence_index,
        "unresolved_assumptions": [],
    }


def build_audit_report(request: dict) -> dict:
    """Execute registered charge adapters and return a deterministic report."""

    _require(isinstance(request, dict), "audit report request must be an object")
    run_id = request.get("audit_run_id")
    data_status = request.get("data_status")
    as_of_at = request.get("as_of_at")
    _require(isinstance(run_id, str) and run_id, "audit_run_id is required")
    _require(data_status in {"synthetic", "authorized_sanitized"}, "report data_status is invalid")
    _instant(as_of_at, "report as_of_at")
    requests = request.get("charge_requests")
    _require(isinstance(requests, list) and requests, "charge_requests must be a nonempty list")

    charge_results: list[dict] = []
    seen_instances: set[str] = set()
    seen_families: set[str] = set()
    for charge_request in requests:
        _require(isinstance(charge_request, dict), "charge request must be an object")
        instance_id = charge_request.get("charge_instance_id")
        adapter_id = charge_request.get("adapter_id")
        _require(isinstance(instance_id, str) and instance_id, "charge_instance_id is required")
        _require(instance_id not in seen_instances, f"duplicate charge instance {instance_id}")
        _require(adapter_id in ADAPTERS, f"unknown charge adapter {adapter_id}")
        contract = ADAPTERS[adapter_id]
        family = str(contract["charge_family"])
        _require(family not in seen_families, f"duplicate charge family {family}")
        audit_case = charge_request.get("audit_case")
        _require(isinstance(audit_case, dict), f"{instance_id} audit_case must be an object")
        _require(audit_case.get("data_status") == data_status, f"{instance_id} data_status differs from report")
        _require(audit_case.get("as_of_at") == as_of_at, f"{instance_id} as_of_at differs from report")
        try:
            result = contract["evaluator"](audit_case)  # type: ignore[operator]
        except AuditInputError as exc:
            raise AuditReportError(f"{instance_id} adapter rejected input: {exc}") from exc
        contract["validator"](result)  # type: ignore[operator]
        charge_results.append(
            {
                "charge_instance_id": instance_id,
                "adapter": {
                    "id": adapter_id,
                    "version": contract["adapter_version"],
                    "charge_family": family,
                    "audit_policy_id": contract["audit_policy_id"],
                },
                "audit_result": result,
            }
        )
        seen_instances.add(instance_id)
        seen_families.add(family)
    charge_results.sort(key=lambda value: value["charge_instance_id"])
    report = _compose_report(run_id, data_status, as_of_at, charge_results)
    validate_audit_report(report)
    return report


def validate_audit_report(report: object) -> None:
    """Reject a malformed or internally inconsistent audit report envelope."""

    _require(isinstance(report, dict), "audit report must be an object")
    _require(report.get("schema_version") == REPORT_SCHEMA_VERSION, "audit report schema version mismatch")
    run = report.get("run")
    _require(isinstance(run, dict), "audit report run metadata is missing")
    run_id = run.get("audit_run_id")
    data_status = run.get("data_status")
    as_of_at = run.get("as_of_at")
    _require(isinstance(run_id, str) and run_id, "audit report run id is missing")
    _require(data_status in {"synthetic", "authorized_sanitized"}, "audit report data status is invalid")
    _instant(as_of_at, "audit report as_of_at")
    charge_results = report.get("charge_results")
    _require(isinstance(charge_results, list) and charge_results, "audit report charge results are missing")
    _require(charge_results == sorted(charge_results, key=lambda value: value.get("charge_instance_id", "")), "charge results are not deterministically ordered")
    seen_instances: set[str] = set()
    seen_families: set[str] = set()
    for charge in charge_results:
        _require(isinstance(charge, dict), "charge result must be an object")
        instance_id = charge.get("charge_instance_id")
        adapter = charge.get("adapter")
        _require(isinstance(instance_id, str) and instance_id and instance_id not in seen_instances, "charge result identity is invalid")
        _require(isinstance(adapter, dict) and adapter.get("id") in ADAPTERS, f"{instance_id} adapter is invalid")
        contract = ADAPTERS[adapter["id"]]
        _require(
            adapter
            == {
                "id": adapter["id"],
                "version": contract["adapter_version"],
                "charge_family": contract["charge_family"],
                "audit_policy_id": contract["audit_policy_id"],
            },
            f"{instance_id} adapter contract mismatch",
        )
        _require(contract["charge_family"] not in seen_families, f"duplicate charge family {contract['charge_family']}")
        contract["validator"](charge.get("audit_result"))  # type: ignore[operator]
        _require(charge["audit_result"].get("as_of_at") == as_of_at, f"{instance_id} audit cutoff differs from report")
        _require(charge["audit_result"].get("data_status") == data_status, f"{instance_id} data status differs from report")
        seen_instances.add(instance_id)
        seen_families.add(str(contract["charge_family"]))
    expected = _compose_report(run_id, data_status, as_of_at, charge_results)
    _require(report == expected, "audit report projection, explanation, source, evidence, or totals were altered")


def serialize_audit_report(report: dict) -> str:
    """Return canonical JSON after validating the complete report contract."""

    validate_audit_report(report)
    return json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":"))

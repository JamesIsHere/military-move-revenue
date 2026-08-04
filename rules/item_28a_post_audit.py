"""Reconcile a final Item 28A expected charge with invoice and payment history."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from rules.item_28a_extra_pickup import (
    APPROVAL_REQUIREMENT_ID,
    CURRENCY,
    INTERPRETATION_DECISION_ID,
    ITEM_CODE,
    PERFORMANCE_REQUIREMENT_ID,
    PROVENANCE as EXPECTED_CHARGE_PROVENANCE,
    QUANTITY_UNIT,
    RATE_DATE_REQUIREMENT_ID,
    RATE_EFFECTIVE_FROM,
    RATE_EFFECTIVE_TO,
    RATE_SOURCE_CELL,
    RULE_IDS as EXPECTED_CHARGE_RULE_IDS,
    RULE_PACKAGE_ID as EXPECTED_CHARGE_RULE_PACKAGE_ID,
    UNIT_RATE,
)


AUDIT_POLICY_ID = "AUDIT-DP3-ITEM-28A-RECONCILIATION-V1"
AUDIT_POLICY_VERSION = "2026-08-03.1"
AUDIT_POLICY_PROVENANCE = (
    {
        "source_id": "GOAL-RATIFIED-2026-08-03",
        "document_path": "goal.md",
        "document_version": "ratified 2026-08-03",
        "effective_period": "2026-08-03/open",
        "locator": "Outcome; Version-one boundary; Quality bar; Completion verifier",
        "retrieval_date": "2026-08-03",
        "interpretation_status": "ratified_internal_policy",
    },
    {
        "source_id": "ITEM-28A-POST-AUDIT-POLICY",
        "document_path": "docs/item-28a-post-audit-policy.md",
        "document_version": "2026-08-03.1",
        "effective_period": "2026-08-03/open",
        "locator": "Required inputs through Blocked results and AI boundary",
        "retrieval_date": "2026-08-03",
        "interpretation_status": "approved_internal_policy",
    },
    {
        "source_id": "LOGICAL-SCHEMA-2026-08-03",
        "document_path": "docs/logical-schema.md",
        "document_version": "draft logical contract 2026-08-03",
        "effective_period": "DESIGN_CONTRACT",
        "locator": "sections 10 through 12",
        "retrieval_date": "2026-08-03",
        "interpretation_status": "reviewed_design_contract",
    },
)
AUDIT_SOURCE_PROVENANCE = (
    {
        "source_version_id": "SV-DTR-IV-AAA-2026-02-04",
        "source_claim_id": "CLM-0038",
        "source_locator_id": "LOC-0034",
    },
    {
        "source_version_id": "SV-DTR-IV-AAA-2026-02-04",
        "source_claim_id": "CLM-0039",
        "source_locator_id": "LOC-0034",
    },
    {
        "source_version_id": "SV-DTR-IV-AAA-2026-02-04",
        "source_claim_id": "CLM-0040",
        "source_locator_id": "LOC-0035",
    },
)
DECIMAL_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")


class AuditInputError(ValueError):
    """Raised when audit input or an upstream result is malformed or tampered."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditInputError(message)


def _index(records: object, label: str) -> dict[str, dict]:
    _require(isinstance(records, list), f"{label} must be a list")
    result: dict[str, dict] = {}
    for record in records:
        _require(isinstance(record, dict), f"{label} record must be an object")
        record_id = record.get("id")
        _require(isinstance(record_id, str) and record_id, f"{label} record id is required")
        _require(record_id not in result, f"duplicate {label} id {record_id}")
        result[record_id] = record
    return result


def _decimal(value: object, label: str) -> Decimal:
    _require(isinstance(value, str), f"{label} must be an exact decimal JSON string")
    _require(bool(DECIMAL_RE.fullmatch(value)), f"{label} must be a canonical nonnegative decimal string")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise AuditInputError(f"{label} must be an exact decimal") from exc


def _money(value: object, label: str) -> Decimal:
    amount = _decimal(value, label)
    _require(amount == amount.quantize(Decimal("0.01")), f"{label} must use no more than two decimal places")
    return amount


def _instant(value: object, label: str) -> datetime:
    _require(isinstance(value, str) and value, f"{label} must be an ISO instant")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuditInputError(f"{label} must be an ISO instant") from exc
    _require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return parsed


def _local_date(value: object, label: str) -> date:
    _require(isinstance(value, str) and value, f"{label} must be an ISO local date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise AuditInputError(f"{label} must be an ISO local date") from exc


def _money_text(value: Decimal) -> str:
    return f"{value:.2f}"


def _reviewed_evidence(
    link_id: object,
    evidence_links: dict[str, dict],
    document_versions: dict[str, dict],
    *,
    target_kind: str,
    target_id: str,
    evidence_role: str,
) -> bool:
    if not isinstance(link_id, str) or link_id not in evidence_links:
        return False
    link = evidence_links[link_id]
    return (
        link.get("document_version_id") in document_versions
        and link.get("target_kind") == target_kind
        and link.get("target_id") == target_id
        and link.get("evidence_role") == evidence_role
        and link.get("review_status") == "REVIEWED"
    )


def _current_version_by_owner(
    rows: dict[str, dict],
    owner_field: str,
    owner_ids: set[str],
    label: str,
) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows.values():
        owner_id = row.get(owner_field)
        _require(owner_id in owner_ids, f"{row['id']} references unknown {label} owner")
        grouped[owner_id].append(row)

    result: dict[str, dict] = {}
    for owner_id in owner_ids:
        owner_rows = sorted(grouped.get(owner_id, []), key=lambda row: row.get("version_number", 0))
        _require(owner_rows, f"{label} {owner_id} has no versions")
        _require(
            [row.get("version_number") for row in owner_rows] == list(range(1, len(owner_rows) + 1)),
            f"{label} {owner_id} version numbers must be contiguous",
        )
        for previous, current in zip(owner_rows, owner_rows[1:]):
            _require(current.get("supersedes_id") == previous["id"], f"{current['id']} does not directly supersede {previous['id']}")
        result[owner_id] = owner_rows[-1]
    return result


def _validate_expected_charge_result(result: object) -> dict:
    _require(isinstance(result, dict), "expected_charge_result must be an object")
    _require(result.get("rule_package_id") == EXPECTED_CHARGE_RULE_PACKAGE_ID, "expected charge uses an unknown rule package")
    _require(result.get("rule_ids") == list(EXPECTED_CHARGE_RULE_IDS), "expected charge rule sequence mismatch")
    _require(result.get("interpretation_decision_id") == INTERPRETATION_DECISION_ID, "expected charge interpretation mismatch")
    _require(result.get("provenance") == [dict(reference) for reference in EXPECTED_CHARGE_PROVENANCE], "expected charge provenance mismatch")
    _require(result.get("unresolved_assumptions") == [], "expected charge contains unresolved assumptions")
    _require(result.get("status") in {"FINAL", "BLOCKED"}, "expected charge has unsupported status")

    source_contract = result.get("source_contract")
    _require(isinstance(source_contract, dict), "expected charge source contract is missing")
    _require(
        source_contract
        == {
            "item_code": ITEM_CODE,
            "quantity_unit": QUANTITY_UNIT,
            "rate_date_role": "ORIGINAL_REQUESTED_PICKUP",
            "rate_effective_from": RATE_EFFECTIVE_FROM.isoformat(),
            "rate_effective_to": RATE_EFFECTIVE_TO.isoformat(),
            "rate_source_cell": RATE_SOURCE_CELL,
        },
        "expected charge source contract mismatch",
    )
    _require(
        result.get("evidence")
        == {
            "approval_requirement_id": APPROVAL_REQUIREMENT_ID,
            "performance_requirement_id": PERFORMANCE_REQUIREMENT_ID,
            "rate_date_requirement_id": RATE_DATE_REQUIREMENT_ID,
        },
        "expected charge evidence contract mismatch",
    )
    snapshot = result.get("input_snapshot")
    _require(isinstance(snapshot, dict) and isinstance(snapshot.get("shipment_id"), str), "expected charge input snapshot is incomplete")

    if result["status"] == "BLOCKED":
        _require(result.get("human_review_required") is True, "blocked expected charge must require review")
        _require(isinstance(result.get("blocked_reasons"), list) and result["blocked_reasons"], "blocked expected charge lacks reasons")
        _require("calculation" not in result and "eligibility" not in result, "blocked expected charge exposes authoritative money")
        return {"status": "BLOCKED", "shipment_id": snapshot["shipment_id"], "blocked_reasons": result["blocked_reasons"]}

    _require(result.get("human_review_required") is False, "final expected charge unexpectedly requires review")
    eligibility = result.get("eligibility")
    calculation = result.get("calculation")
    _require(isinstance(eligibility, dict) and isinstance(calculation, dict), "final expected charge is incomplete")
    count = eligibility.get("eligible_occurrence_count")
    _require(isinstance(count, int) and count >= 0, "expected occurrence count must be a nonnegative integer")
    counted_ids = eligibility.get("counted_service_performance_ids")
    _require(isinstance(counted_ids, list) and len(counted_ids) == count and len(set(counted_ids)) == count, "expected counted occurrence ids mismatch")
    quantity = _decimal(calculation.get("quantity"), "expected calculation quantity")
    rate = _money(calculation.get("unit_rate"), "expected unit rate")
    amount = _money(calculation.get("expected_amount"), "expected amount")
    _require(quantity == Decimal(count), "expected calculation quantity differs from eligibility")
    _require(rate == UNIT_RATE, "expected calculation rate mismatch")
    _require(amount == quantity * rate, "expected calculation arithmetic mismatch")
    _require(calculation.get("unrounded_amount") == calculation.get("expected_amount"), "expected calculation introduced rounding")
    _require(calculation.get("currency") == CURRENCY and calculation.get("quantity_unit") == QUANTITY_UNIT, "expected calculation unit or currency mismatch")
    _require(result.get("expected_line_action") == ("CREATE" if count else "OMIT"), "expected line action mismatch")
    return {
        "status": "FINAL",
        "shipment_id": snapshot["shipment_id"],
        "count": count,
        "amount": amount,
        "expected_result_case_id": result.get("case_id"),
    }


def audit_item_28a(case: dict) -> dict:
    """Return a deterministic Item 28A billing/payment finding or review block."""

    _require(isinstance(case, dict), "case must be an object")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id, "case_id is required")
    _require(case.get("data_status") in {"synthetic", "authorized_sanitized"}, "data_status must be synthetic or authorized_sanitized")
    as_of_at = _instant(case.get("as_of_at"), "as_of_at")
    upstream = _validate_expected_charge_result(case.get("expected_charge_result"))

    common = {
        "case_id": case_id,
        "audit_policy": {
            "id": AUDIT_POLICY_ID,
            "version": AUDIT_POLICY_VERSION,
            "scope": "DOMESTIC_DP3_ITEM_28A_POST_AUDIT",
            "billing_variance_expression": "invoiced_amount - expected_amount",
            "payment_variance_expression": "paid_amount - invoiced_amount",
            "realized_variance_expression": "paid_amount - expected_amount",
        },
        "audited_charge": {
            "item_code": ITEM_CODE,
            "quantity_unit": QUANTITY_UNIT,
            "currency": CURRENCY,
            "expected_charge_rule_package_id": EXPECTED_CHARGE_RULE_PACKAGE_ID,
            "interpretation_decision_id": INTERPRETATION_DECISION_ID,
        },
        "provenance": {
            "audit_policy": [dict(reference) for reference in AUDIT_POLICY_PROVENANCE],
            "observed_invoice_payment": [dict(reference) for reference in AUDIT_SOURCE_PROVENANCE],
            "expected_charge": [dict(reference) for reference in EXPECTED_CHARGE_PROVENANCE],
        },
        "as_of_at": as_of_at.isoformat().replace("+00:00", "Z"),
        "unresolved_assumptions": [],
    }
    if upstream["status"] == "BLOCKED":
        return {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": [f"UPSTREAM_EXPECTED_CHARGE_BLOCKED:{reason}" for reason in upstream["blocked_reasons"]],
            "audit_finding": {"finding_code": "AUDIT_BLOCKED", "finding_status": "OPEN"},
        }

    records = case.get("records")
    _require(isinstance(records, dict), "records must be an object")
    shipments = _index(records.get("shipments"), "shipments")
    bills = _index(records.get("bills_of_lading"), "bills_of_lading")
    invoices = _index(records.get("invoices"), "invoices")
    invoice_versions = _index(records.get("invoice_versions"), "invoice_versions")
    invoice_lines = _index(records.get("invoice_lines"), "invoice_lines")
    line_versions = _index(records.get("invoice_line_versions"), "invoice_line_versions")
    documents = _index(records.get("documents"), "documents")
    document_versions = _index(records.get("document_versions"), "document_versions")
    evidence_links = _index(records.get("evidence_links"), "evidence_links")
    payments = _index(records.get("payments"), "payments")
    allocations = _index(records.get("payment_allocations"), "payment_allocations")
    assertions = _index(records.get("audit_data_completeness_assertions"), "audit_data_completeness_assertions")

    _require(set(shipments) == {upstream["shipment_id"]}, "audit shipment differs from expected charge shipment")
    shipment_id = upstream["shipment_id"]
    shipment = shipments[shipment_id]
    _require(shipment.get("program_code") == "DP3" and shipment.get("domestic_indicator") is True, "audit shipment is outside domestic DP3 scope")
    _require(len(bills) == 1 and next(iter(bills.values())).get("shipment_id") == shipment_id, "audit requires one bill of lading for the expected shipment")
    bill_id = next(iter(bills))

    blocked_reasons: list[str] = []
    assertion_by_scope: dict[str, dict] = {}
    for assertion in assertions.values():
        _require(assertion.get("shipment_id") == shipment_id, f"{assertion['id']} belongs to another shipment")
        scope = assertion.get("fact_scope")
        _require(scope in {"INVOICE_HISTORY", "PAYMENT_HISTORY"}, f"{assertion['id']} has unsupported completeness scope")
        _require(scope not in assertion_by_scope, f"duplicate completeness assertion for {scope}")
        assertion_by_scope[scope] = assertion
        if (
            assertion.get("assertion_status") != "COMPLETE"
            or assertion.get("review_status") != "REVIEWED"
            or _instant(assertion.get("complete_through"), f"{assertion['id']}.complete_through") < as_of_at
        ):
            blocked_reasons.append(f"DATA_COMPLETENESS_NOT_ESTABLISHED:{scope}")
    for scope in ("INVOICE_HISTORY", "PAYMENT_HISTORY"):
        if scope not in assertion_by_scope:
            blocked_reasons.append(f"DATA_COMPLETENESS_NOT_ESTABLISHED:{scope}")

    for version in document_versions.values():
        _require(version.get("document_id") in documents, f"{version['id']} references unknown document")

    allowed_targets = {
        "INVOICE_VERSION": invoice_versions,
        "INVOICE_LINE_VERSION": line_versions,
        "PAYMENT": payments,
        "PAYMENT_ALLOCATION": allocations,
    }
    evidence_keys: set[tuple[str, str, str]] = set()
    for link in evidence_links.values():
        target_kind = link.get("target_kind")
        target_id = link.get("target_id")
        _require(target_kind in allowed_targets, f"{link['id']} has unsupported evidence target kind")
        _require(target_id in allowed_targets[target_kind], f"{link['id']} references unknown evidence target")
        key = (target_kind, str(target_id), str(link.get("evidence_role")))
        _require(key not in evidence_keys, f"duplicate evidence role for {target_kind} {target_id}")
        evidence_keys.add(key)

    invoice_identity_keys: set[tuple[str, str]] = set()
    for invoice in invoices.values():
        _require(invoice.get("bill_of_lading_id") == bill_id, f"{invoice['id']} belongs to another bill of lading")
        identity = (str(invoice.get("invoice_namespace")), str(invoice.get("invoice_number")))
        _require(all(identity), f"{invoice['id']} invoice identity is incomplete")
        _require(identity not in invoice_identity_keys, f"duplicate invoice identity {identity}")
        invoice_identity_keys.add(identity)

    current_invoice_versions = _current_version_by_owner(invoice_versions, "invoice_id", set(invoices), "invoice") if invoices else {}
    line_identity_keys: set[tuple[str, str]] = set()
    for line in invoice_lines.values():
        _require(line.get("invoice_id") in invoices, f"{line['id']} references unknown invoice")
        identity = (line["invoice_id"], str(line.get("line_identity_within_invoice")))
        _require(identity[1], f"{line['id']} line identity is incomplete")
        _require(identity not in line_identity_keys, f"duplicate invoice line identity {identity}")
        line_identity_keys.add(identity)
    current_line_versions = _current_version_by_owner(line_versions, "invoice_line_id", set(invoice_lines), "invoice line") if invoice_lines else {}

    invoice_evidence_ids: list[str] = []
    for version in invoice_versions.values():
        _require(version.get("invoice_id") in invoices, f"{version['id']} references unknown invoice")
        _require(version.get("currency") == CURRENCY, f"{version['id']} currency must be USD")
        _local_date(version.get("invoice_date"), f"{version['id']}.invoice_date")
        _money(version.get("claimed_total"), f"{version['id']}.claimed_total")
        _require(_instant(version.get("recorded_at"), f"{version['id']}.recorded_at") <= as_of_at, f"{version['id']} is later than audit cutoff")
        if not _reviewed_evidence(
            version.get("evidence_link_id"), evidence_links, document_versions,
            target_kind="INVOICE_VERSION", target_id=version["id"], evidence_role="INVOICE_VERSION_SOURCE",
        ):
            blocked_reasons.append(f"INVOICE_EVIDENCE_MISSING_OR_UNREVIEWED:{version['id']}")
        else:
            invoice_evidence_ids.append(version["evidence_link_id"])

    line_amounts_by_invoice_version: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for version in line_versions.values():
        line = invoice_lines.get(version.get("invoice_line_id"))
        _require(line is not None, f"{version['id']} references unknown invoice line")
        invoice_version = invoice_versions.get(version.get("invoice_version_id"))
        _require(invoice_version is not None, f"{version['id']} references unknown invoice version")
        _require(invoice_version.get("invoice_id") == line.get("invoice_id"), f"{version['id']} crosses invoice identities")
        _require(version.get("currency") == CURRENCY, f"{version['id']} currency must be USD")
        amount = _money(version.get("claimed_amount"), f"{version['id']}.claimed_amount")
        quantity = _decimal(version.get("quantity"), f"{version['id']}.quantity")
        _require(quantity == quantity.to_integral_value(), f"{version['id']}.quantity must be a whole EA count")
        line_amounts_by_invoice_version[invoice_version["id"]] += amount
        if not _reviewed_evidence(
            version.get("evidence_link_id"), evidence_links, document_versions,
            target_kind="INVOICE_LINE_VERSION", target_id=version["id"], evidence_role="INVOICE_LINE_SOURCE",
        ):
            blocked_reasons.append(f"INVOICE_LINE_EVIDENCE_MISSING_OR_UNREVIEWED:{version['id']}")
        else:
            invoice_evidence_ids.append(version["evidence_link_id"])

    for version in invoice_versions.values():
        _require(
            any(line.get("invoice_version_id") == version["id"] for line in line_versions.values()),
            f"{version['id']} has no line versions",
        )
        _require(
            line_amounts_by_invoice_version[version["id"]] == _money(version["claimed_total"], f"{version['id']}.claimed_total"),
            f"{version['id']} total does not equal its line versions",
        )
    for line_id, version in current_line_versions.items():
        current_invoice = current_invoice_versions[invoice_lines[line_id]["invoice_id"]]
        _require(version.get("invoice_version_id") == current_invoice["id"], f"{version['id']} is not attached to the current invoice version")

    accepted_item_lines: list[dict] = []
    for version in current_line_versions.values():
        raw_code = version.get("billing_item_code_text")
        candidate_code = version.get("candidate_service_code")
        if raw_code == ITEM_CODE:
            if version.get("mapping_status") == "ACCEPTED" and version.get("interpretation_decision_id") == INTERPRETATION_DECISION_ID:
                _require(version.get("quantity_unit") == QUANTITY_UNIT, f"{version['id']} quantity unit must be EA")
                accepted_item_lines.append(version)
            else:
                blocked_reasons.append(f"UNRESOLVED_ITEM_28A_MAPPING:{version['id']}")
        elif candidate_code == ITEM_CODE:
            blocked_reasons.append(f"AMBIGUOUS_ITEM_28A_MATCH:{version['id']}")
    if len(accepted_item_lines) > 1:
        blocked_reasons.append("AMBIGUOUS_MULTIPLE_ITEM_28A_LINES")

    payment_evidence_ids: list[str] = []
    for payment in payments.values():
        _require(payment.get("currency") == CURRENCY, f"{payment['id']} currency must be USD")
        _local_date(payment.get("payment_date"), f"{payment['id']}.payment_date")
        _money(payment.get("amount"), f"{payment['id']}.amount")
        _require(_instant(payment.get("recorded_at"), f"{payment['id']}.recorded_at") <= as_of_at, f"{payment['id']} is later than audit cutoff")
        if not _reviewed_evidence(
            payment.get("evidence_link_id"), evidence_links, document_versions,
            target_kind="PAYMENT", target_id=payment["id"], evidence_role="PAYMENT_SOURCE",
        ):
            blocked_reasons.append(f"PAYMENT_EVIDENCE_MISSING_OR_UNREVIEWED:{payment['id']}")
        else:
            payment_evidence_ids.append(payment["evidence_link_id"])

    allocations_by_key: dict[str, list[dict]] = defaultdict(list)
    for allocation in allocations.values():
        key = allocation.get("allocation_key")
        _require(isinstance(key, str) and key, f"{allocation['id']} allocation_key is required")
        _require(allocation.get("payment_id") in payments, f"{allocation['id']} references unknown payment")
        _require(allocation.get("invoice_line_id") in invoice_lines, f"{allocation['id']} references unknown invoice line")
        _require(allocation.get("currency") == CURRENCY, f"{allocation['id']} currency must be USD")
        _money(allocation.get("allocated_amount"), f"{allocation['id']}.allocated_amount")
        allocations_by_key[key].append(allocation)
        if not _reviewed_evidence(
            allocation.get("evidence_link_id"), evidence_links, document_versions,
            target_kind="PAYMENT_ALLOCATION", target_id=allocation["id"], evidence_role="PAYMENT_ALLOCATION_SOURCE",
        ):
            blocked_reasons.append(f"PAYMENT_ALLOCATION_EVIDENCE_MISSING_OR_UNREVIEWED:{allocation['id']}")
        else:
            payment_evidence_ids.append(allocation["evidence_link_id"])

    current_allocations: list[dict] = []
    for key, rows in allocations_by_key.items():
        ordered = sorted(rows, key=lambda row: row.get("version_number", 0))
        _require([row.get("version_number") for row in ordered] == list(range(1, len(ordered) + 1)), f"allocation {key} version numbers must be contiguous")
        for previous, current in zip(ordered, ordered[1:]):
            _require(current.get("supersedes_id") == previous["id"], f"{current['id']} does not directly supersede {previous['id']}")
            _require(current.get("payment_id") == previous.get("payment_id") and current.get("invoice_line_id") == previous.get("invoice_line_id"), f"allocation {key} changed payment or invoice line")
        current_allocations.append(ordered[-1])

    for payment in payments.values():
        allocated = sum(
            (_money(row["allocated_amount"], f"{row['id']}.allocated_amount") for row in current_allocations if row["payment_id"] == payment["id"]),
            Decimal("0"),
        )
        _require(allocated == _money(payment["amount"], f"{payment['id']}.amount"), f"{payment['id']} current allocations do not balance")

    snapshot = {
        "shipment_id": shipment_id,
        "expected_result_case_id": upstream["expected_result_case_id"],
        "current_invoice_version_ids": sorted(version["id"] for version in current_invoice_versions.values()),
        "current_invoice_line_version_ids": sorted(version["id"] for version in current_line_versions.values()),
        "current_payment_allocation_ids": sorted(row["id"] for row in current_allocations),
        "invoice_evidence_link_ids": sorted(set(invoice_evidence_ids)),
        "payment_evidence_link_ids": sorted(set(payment_evidence_ids)),
        "completeness_assertion_ids": sorted(assertion["id"] for assertion in assertion_by_scope.values()),
    }
    if blocked_reasons:
        return {
            **common,
            "status": "BLOCKED",
            "human_review_required": True,
            "blocked_reasons": sorted(set(blocked_reasons)),
            "input_snapshot": snapshot,
            "audit_finding": {"finding_code": "AUDIT_BLOCKED", "finding_status": "OPEN"},
        }

    expected_amount = upstream["amount"]
    expected_quantity = Decimal(upstream["count"])
    matched = accepted_item_lines[0] if accepted_item_lines else None
    invoiced_amount = _money(matched["claimed_amount"], f"{matched['id']}.claimed_amount") if matched else Decimal("0")
    invoiced_quantity = _decimal(matched["quantity"], f"{matched['id']}.quantity") if matched else Decimal("0")
    matched_line_id = matched["invoice_line_id"] if matched else None
    paid_amount = sum(
        (_money(row["allocated_amount"], f"{row['id']}.allocated_amount") for row in current_allocations if row["invoice_line_id"] == matched_line_id),
        Decimal("0"),
    )

    billing_variance = invoiced_amount - expected_amount
    payment_variance = paid_amount - invoiced_amount
    realized_variance = paid_amount - expected_amount
    quantity_variance = invoiced_quantity - expected_quantity

    if expected_amount > 0 and matched is None:
        billing_code = "MISSING_EXPECTED_CHARGE"
    elif expected_amount == 0 and matched is not None:
        billing_code = "UNSUPPORTED_BILLED_CHARGE"
    elif expected_amount == 0 and matched is None:
        billing_code = "NO_CHARGE_EXPECTED_OR_BILLED"
    elif billing_variance < 0:
        billing_code = "UNDERBILLED"
    elif billing_variance > 0:
        billing_code = "OVERBILLED"
    else:
        billing_code = "CORRECTLY_BILLED"

    if matched is None:
        payment_code = "NO_MATCHED_INVOICE_LINE"
    elif payment_variance == 0:
        payment_code = "PAID_AS_INVOICED"
    elif paid_amount == 0:
        payment_code = "UNPAID"
    elif payment_variance < 0:
        payment_code = "PARTIALLY_PAID"
    else:
        payment_code = "OVERPAID"

    quantity_code = "QUANTITY_MATCH" if quantity_variance == 0 else "QUANTITY_MISMATCH"
    no_exception = billing_code in {"CORRECTLY_BILLED", "NO_CHARGE_EXPECTED_OR_BILLED"} and payment_code in {
        "PAID_AS_INVOICED",
        "NO_MATCHED_INVOICE_LINE",
    } and quantity_code == "QUANTITY_MATCH"
    return {
        **common,
        "status": "FINAL",
        "human_review_required": False,
        "input_snapshot": snapshot,
        "match": {
            "match_status": "EXACT" if matched else "NO_MATCH",
            "invoice_line_id": matched_line_id,
            "invoice_line_version_id": matched["id"] if matched else None,
            "matching_rationale": "Accepted raw 28A mapping under INT-0001" if matched else "No current accepted Item 28A line in complete invoice history",
        },
        "comparison": {
            "expected_amount": _money_text(expected_amount),
            "invoiced_amount": _money_text(invoiced_amount),
            "paid_amount": _money_text(paid_amount),
            "currency": CURRENCY,
            "billing_variance": _money_text(billing_variance),
            "payment_variance": _money_text(payment_variance),
            "realized_variance": _money_text(realized_variance),
            "expected_quantity": str(upstream["count"]),
            "invoiced_quantity": str(int(invoiced_quantity)),
            "quantity_unit": QUANTITY_UNIT,
            "quantity_variance": str(int(quantity_variance)),
        },
        "audit_finding": {
            "billing_finding_code": billing_code,
            "quantity_finding_code": quantity_code,
            "payment_finding_code": payment_code,
            "finding_status": "CLOSED_NO_EXCEPTION" if no_exception else "OPEN",
        },
    }

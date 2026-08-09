"""Reconcile a final Item 28B expected charge with invoice/payment history."""

from __future__ import annotations

from rules.item_28a_post_audit import (
    AUDIT_SOURCE_PROVENANCE,
    AuditInputError,
    audit_occurrence_charge,
)
from rules.item_28b_extra_delivery import (
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


AUDIT_POLICY_ID = "AUDIT-DP3-ITEM-28B-RECONCILIATION-V1"
AUDIT_POLICY_VERSION = "2026-08-04.1"
AUDIT_POLICY_PROVENANCE = (
    {
        "source_id": "GOAL-RATIFIED-2026-08-03",
        "document_path": "goal.md",
        "document_version": "ratified 2026-08-03",
        "effective_period": "2026-08-03/open",
        "locator": "Outcome; Version-one boundary; Quality bar; Completion verifier",
        "retrieval_date": "2026-08-04",
        "interpretation_status": "ratified_internal_policy",
    },
    {
        "source_id": "ITEM-28B-POST-AUDIT-POLICY",
        "document_path": "docs/item-28b-post-audit-policy.md",
        "document_version": AUDIT_POLICY_VERSION,
        "effective_period": "2026-08-04/open",
        "locator": "Required inputs through Blocked results and AI boundary",
        "retrieval_date": "2026-08-04",
        "interpretation_status": "approved_internal_policy",
    },
    {
        "source_id": "LOGICAL-SCHEMA-2026-08-03",
        "document_path": "docs/logical-schema.md",
        "document_version": "draft logical contract 2026-08-03",
        "effective_period": "DESIGN_CONTRACT",
        "locator": "sections 10 through 12",
        "retrieval_date": "2026-08-04",
        "interpretation_status": "reviewed_design_contract",
    },
)

ITEM_28B_AUDIT_CONTRACT = {
    "item_code": ITEM_CODE,
    "item_token": "ITEM_28B",
    "item_label": "Item 28B",
    "quantity_unit": QUANTITY_UNIT,
    "currency": CURRENCY,
    "interpretation_decision_id": INTERPRETATION_DECISION_ID,
    "expected_charge_rule_ids": EXPECTED_CHARGE_RULE_IDS,
    "expected_charge_rule_package_id": EXPECTED_CHARGE_RULE_PACKAGE_ID,
    "expected_charge_provenance": EXPECTED_CHARGE_PROVENANCE,
    "unit_rate": UNIT_RATE,
    "rate_date_role": "ACTUAL_PICKUP",
    "rate_effective_from": RATE_EFFECTIVE_FROM,
    "rate_effective_to": RATE_EFFECTIVE_TO,
    "rate_source_cell": RATE_SOURCE_CELL,
    "approval_requirement_id": APPROVAL_REQUIREMENT_ID,
    "performance_requirement_id": PERFORMANCE_REQUIREMENT_ID,
    "rate_date_requirement_id": RATE_DATE_REQUIREMENT_ID,
    "audit_policy_id": AUDIT_POLICY_ID,
    "audit_policy_version": AUDIT_POLICY_VERSION,
    "audit_scope": "DOMESTIC_DP3_ITEM_28B_POST_AUDIT",
    "audit_policy_provenance": AUDIT_POLICY_PROVENANCE,
}


def audit_item_28b(case: dict) -> dict:
    """Return a deterministic Item 28B billing/payment finding or review block."""

    return audit_occurrence_charge(case, ITEM_28B_AUDIT_CONTRACT)


__all__ = [
    "AUDIT_POLICY_ID",
    "AUDIT_POLICY_PROVENANCE",
    "AUDIT_POLICY_VERSION",
    "AUDIT_SOURCE_PROVENANCE",
    "AuditInputError",
    "audit_item_28b",
]

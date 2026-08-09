#!/usr/bin/env python3
"""Verify the proposed CF-0004 dossier and its exact boundary matrix."""

from __future__ import annotations

import copy
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "docs" / "decisions" / "0006-cf-0004-reweigh-tolerance-dossier.json"
REGISTRY = ROOT / "rules" / "registry" / "registry.json"
TARIFF_TEXT = ROOT / "sources" / "derived" / "2026" / "2026-400ng-final.txt"
ACCEPTED = ROOT / "docs" / "decisions" / "0006-cf-0004-initial-net-scoped.md"

CANDIDATES = (
    "INITIAL_NET",
    "COMPLETED_REWEIGH_NET",
    "LOWER_NET",
    "CONTAINERIZED_PROVISIONAL_NET",
    "REVIEWED_ACCEPTED_WEIGHT",
)
ZERO = Decimal("0")
FIVE_PERCENT = Decimal("0.05")
ONE_HUNDRED_FIFTY = Decimal("150")
FIVE_THOUSAND = Decimal("5000")


class ValidationError(Exception):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ValidationError(message)


def load(path: Path) -> dict:
    def no_float(value: str) -> None:
        raise ValidationError(f"{path.name} contains JSON float {value}")

    with path.open(encoding="utf-8") as handle:
        value = json.load(handle, parse_float=no_float)
    require(isinstance(value, dict), f"{path.name} must contain an object")
    return value


def decimal(case: dict, field: str) -> Decimal:
    value = case.get(field)
    require(isinstance(value, str), f"{case.get('id')} {field} must be an exact decimal string")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValidationError(f"{case.get('id')} {field} is not decimal") from exc
    require(result.is_finite() and result >= ZERO, f"{case.get('id')} {field} must be finite and nonnegative")
    return result


def candidate_fields(dossier: dict) -> dict[str, str]:
    definitions = dossier.get("candidate_definitions", [])
    require([value.get("id") for value in definitions] == list(CANDIDATES), "candidate order or set mismatch")
    fields = {value["id"]: value.get("case_field") for value in definitions}
    require(all(isinstance(value, str) and value.endswith("_lb") for value in fields.values()), "candidate case field missing")
    return fields


def fee_result(case: dict, branch_weight: Decimal) -> bool:
    initial = decimal(case, "initial_net_lb")
    reweigh = decimal(case, "completed_reweigh_net_lb")
    lower = decimal(case, "lower_net_lb")
    require(lower == min(initial, reweigh), f"{case['id']} lower net mismatch")
    if reweigh >= initial:
        return True
    difference = initial - reweigh
    if branch_weight <= FIVE_THOUSAND:
        return difference < ONE_HUNDRED_FIFTY
    return difference < lower * FIVE_PERCENT


def reimbursement_result(case: dict, branch_weight: Decimal) -> bool:
    original_tare = decimal(case, "original_tare_lb")
    reweigh_tare = decimal(case, "reweigh_tare_lb")
    if reweigh_tare <= original_tare:
        return False
    increase = reweigh_tare - original_tare
    lower_tare = min(original_tare, reweigh_tare)
    if branch_weight <= FIVE_THOUSAND:
        return increase > ONE_HUNDRED_FIFTY
    return increase >= lower_tare * FIVE_PERCENT


def validate_cases(dossier: dict) -> None:
    fields = candidate_fields(dossier)
    groups = dossier.get("boundary_cases", {})
    require(set(groups) == {"reweigh_fee", "containerized_reimbursement"}, "boundary group mismatch")
    require(len(groups["reweigh_fee"]) == 7, "fee boundary case count mismatch")
    require(len(groups["containerized_reimbursement"]) == 6, "reimbursement boundary case count mismatch")
    seen: set[str] = set()
    for group_name, cases in groups.items():
        calculator = fee_result if group_name == "reweigh_fee" else reimbursement_result
        for case in cases:
            case_id = case.get("id")
            require(isinstance(case_id, str) and case_id not in seen, "boundary case id missing or duplicate")
            seen.add(case_id)
            require(isinstance(case.get("purpose"), str) and case["purpose"], f"{case_id} lacks purpose")
            actual = []
            for candidate in CANDIDATES:
                branch_weight = decimal(case, fields[candidate])
                if calculator(case, branch_weight):
                    actual.append(candidate)
            require(actual == case.get("expected_eligible_candidate_ids"), f"{case_id} expected outcome mismatch: {actual}")

    fee = {value["id"]: value for value in groups["reweigh_fee"]}
    reimbursement = {value["id"]: value for value in groups["containerized_reimbursement"]}
    require(decimal(fee["FEE-003"], "initial_net_lb") == FIVE_THOUSAND, "exact 5000 fee boundary missing")
    require(decimal(fee["FEE-004"], "initial_net_lb") - decimal(fee["FEE-004"], "completed_reweigh_net_lb") == ONE_HUNDRED_FIFTY, "exact 150 fee boundary missing")
    require((decimal(fee["FEE-005"], "initial_net_lb") - decimal(fee["FEE-005"], "completed_reweigh_net_lb")) == decimal(fee["FEE-005"], "lower_net_lb") * FIVE_PERCENT, "exact 5 percent fee boundary missing")
    require(decimal(reimbursement["REIMB-001"], "reweigh_tare_lb") - decimal(reimbursement["REIMB-001"], "original_tare_lb") == ONE_HUNDRED_FIFTY, "exact 150 reimbursement boundary missing")
    require(decimal(reimbursement["REIMB-003"], "reweigh_tare_lb") - decimal(reimbursement["REIMB-003"], "original_tare_lb") == decimal(reimbursement["REIMB-003"], "original_tare_lb") * FIVE_PERCENT, "exact 5 percent reimbursement boundary missing")


def validate(dossier: dict, registry: dict) -> None:
    require(dossier.get("schema_version") == "interpretation-decision-dossier.v1", "dossier schema mismatch")
    require(dossier.get("decision_number") == "0006", "decision number mismatch")
    require(dossier.get("status") == "PROPOSED_OWNER_OR_COUNSEL_APPROVAL_REQUIRED", "dossier was accepted without approval")
    require(dossier.get("prepared_on") == "2026-08-07", "prepared date mismatch")
    require(all(value is None for value in dossier.get("approval", {}).values()), "approval fields must remain empty")
    require(dossier.get("conflict_ids") == ["CF-0004"], "conflict scope mismatch")

    conflicts = {value["id"]: value for value in registry["conflict_cases"]}
    conflict = conflicts.get("CF-0004")
    require(isinstance(conflict, dict) and conflict.get("status") == "resolved", "CF-0004 scoped resolution is not registered")
    require(conflict.get("affected_rule_ids") == dossier.get("affected_rule_ids"), "affected rule scope mismatch")
    decisions = [value for value in registry["interpretation_decisions"] if value.get("conflict_case_id") == "CF-0004"]
    require(len(decisions) == 1, "CF-0004 must have exactly one scoped interpretation")
    decision = decisions[0]
    require(decision.get("id") == "INT-0003" and decision.get("decision_status") == "approved", "INT-0003 approval mismatch")
    require(decision.get("decided_on") == "2026-08-07" and "Decision 0006 Alternative A" in decision.get("decided_by", ""), "approval provenance mismatch")
    require(decision.get("authorized_rule_ids") == dossier.get("affected_rule_ids"), "authorized rule scope mismatch")
    require(len(decision.get("required_regression_tests", [])) == 13, "INT-0003 regression-test contract mismatch")

    versions = {value["id"]: value for value in registry["source_versions"]}
    claims = {value["id"]: value for value in registry["source_claims"]}
    require(len(dossier.get("source_basis", [])) == 2, "source basis count mismatch")
    for source in dossier["source_basis"]:
        version = versions.get(source.get("source_version_id"))
        require(isinstance(version, dict) and version.get("source_id") == source.get("source_id"), "source/version mismatch")
        require(version.get("interpretation_status") == "reviewed", "source version is not reviewed")
        require(all(claim_id in claims for claim_id in source.get("claim_ids", [])), "unknown source claim")
        for field in ("document_version", "effective_period", "locator", "retrieval_date", "interpretation_status"):
            require(isinstance(source.get(field), str) and source[field], f"source lacks {field}")

    contract = dossier.get("proposed_contract", {})
    require(contract.get("selector_candidate_id") == "INITIAL_NET", "provisional selector changed")
    require(contract.get("arithmetic") == "exact_decimal_no_rounding", "exact arithmetic gate missing")
    require(contract.get("missing_or_unreviewed_selector_behavior") == "BLOCK_HUMAN_REVIEW", "missing selector must block")
    require([value.get("id") for value in dossier.get("alternatives", [])] == ["A_APPROVE_INITIAL_NET_SCOPED", "B_APPROVE_LOWER_NET_SCOPED", "C_DEFER_FOR_PUBLISHER"], "decision alternatives mismatch")
    require(len(dossier.get("mandatory_tests", [])) == 13 and len(set(dossier["mandatory_tests"])) == 13, "mandatory test set mismatch")
    require(dossier.get("implementation_gate", "").startswith("DO_NOT_REGISTER"), "implementation stop gate missing")
    require(dossier.get("unresolved_assumptions") == ["The governing sources do not expressly identify the tolerance branch weight fact."], "source ambiguity must remain explicit")

    rules = {value["id"]: value for value in registry["rules"]}
    packages = {value["id"]: value for value in registry["rule_packages"]}
    package = packages.get("RP-DP3-2026-REWEIGH-TOLERANCE-1")
    require(isinstance(package, dict) and package.get("publication_status") == "published", "tolerance package is not published")
    for rule_id in dossier["affected_rule_ids"]:
        rule = rules.get(rule_id)
        require(isinstance(rule, dict), f"unknown affected rule {rule_id}")
        require(rule.get("rule_package_id") == package["id"], f"{rule_id} package mismatch")
        require(rule.get("implementation_status") == "implemented" and rule.get("publication_status") == "published", f"{rule_id} is not implemented and published")
        require(rule.get("blocked_by_conflict_ids") == ["CF-0004"], f"{rule_id} conflict gate mismatch")
        require(rule.get("approved_interpretation_decision_ids") == ["INT-0003"], f"{rule_id} interpretation link mismatch")

    accepted_text = ACCEPTED.read_text(encoding="utf-8")
    for fragment in ("Status: Accepted", "A_APPROVE_INITIAL_NET_SCOPED", "INT-0003", "final reviewed initial net"):
        require(fragment in accepted_text, f"accepted decision lacks {fragment}")

    tariff = " ".join(TARIFF_TEXT.read_text(encoding="utf-8").split())
    required_fragments = (
        "Shipments weighing 5,000 pounds or less; the initial net scale weight minus reweigh net scale weight is less than 150 pounds",
        "Shipments weighing more than 5,000 pounds; the initial net scale weight minus reweigh net scale weight is less than 5% of the lower net scale weight",
        "5,000 lbs or less; the reweigh tare scale weight minus the initial tare scale weight is more than 150 lbs overall",
        "Over 5,000 lbs; the reweigh tare scale weight minus the initial tare scale weight is 5% or more than the overall lower tare scale weight",
    )
    require(all(value in tariff for value in required_fragments), "archived tariff tolerance text changed")
    validate_cases(dossier)


def main() -> int:
    try:
        dossier, registry = load(DOSSIER), load(REGISTRY)
        validate(dossier, registry)
        probes = (
            ("status", lambda value: value.__setitem__("status", "ACCEPTED")),
            ("selector", lambda value: value["proposed_contract"].__setitem__("selector_candidate_id", "LOWER_NET")),
            ("fee boundary", lambda value: value["boundary_cases"]["reweigh_fee"][3].__setitem__("expected_eligible_candidate_ids", ["INITIAL_NET"])),
            ("reimbursement boundary", lambda value: value["boundary_cases"]["containerized_reimbursement"][2].__setitem__("reweigh_tare_lb", "4199.99")),
            ("approval", lambda value: value["approval"].__setitem__("selected_alternative", "A_APPROVE_INITIAL_NET_SCOPED")),
        )
        for label, mutate in probes:
            changed = copy.deepcopy(dossier)
            mutate(changed)
            try:
                validate(changed, registry)
            except ValidationError:
                print(f"PASS CF-0004 dossier tamper rejected: {label}")
                continue
            raise ValidationError(f"accepted CF-0004 dossier tamper: {label}")
        print("PASS preserved CF-0004 proposal and accepted INT-0003 package: 5 candidates, 13 exact boundary cases, 13 mandatory tests, and 5 tamper probes")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

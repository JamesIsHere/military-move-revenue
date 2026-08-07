#!/usr/bin/env python3
"""Validate immutable history and the current Item 130 coverage audit."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "docs" / "decisions" / "0005-item-130-mandatory-test-coverage-audit.json"
V2_PATH = ROOT / "docs" / "decisions" / "0005-item-130-mandatory-test-coverage-audit-2.json"
CURRENT_PATH = ROOT / "docs" / "decisions" / "0005-item-130-mandatory-test-coverage-audit-3.json"
DOSSIER_PATH = ROOT / "docs" / "decisions" / "0005-item-130-fact-model-dossier.json"
ITEM_FIXTURE_DIR = ROOT / "tests" / "fixtures" / "logical-schema"
V1_SHA256 = "F9D1D6CCB65DD79260060AEA8D3B128135F98029725E0442E1485EFF2C291CC4"
V2_SHA256 = "FCCE6929D05D99EC3BEBF04EFE7F899003549F19F26CE84EC7A2858A8B78A41E"
EXPECTED_PROBE_FIELDS = [
    "rate_date_role",
    "quantity_for_billing",
    "rateDateRole",
    "billingQuantity",
    "derived_output.rate-date",
    "financial_output.expectedAmount",
]


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


def load_module(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(audit: dict, v1: dict, v2: dict) -> None:
    require(hashlib.sha256(V1_PATH.read_bytes()).hexdigest().upper() == V1_SHA256, "coverage audit v1 changed")
    require(hashlib.sha256(V2_PATH.read_bytes()).hexdigest().upper() == V2_SHA256, "coverage audit v2 changed")
    require(v1.get("audit_id") == "ITEM-130-MANDATORY-COVERAGE-2026-08-07-1", "coverage audit v1 id mismatch")
    require(v2.get("audit_id") == "ITEM-130-MANDATORY-COVERAGE-2026-08-07-2", "coverage audit v2 id mismatch")
    require(v1.get("summary") == {"covered_count": 16, "partial_count": 2, "missing_count": 0, "overall_status": "PARTIAL_REMEDIATION_REQUIRED"}, "coverage audit v1 summary mismatch")
    require(v2.get("effective_coverage_summary") == {"covered_count": 17, "partial_count": 1, "missing_count": 0, "overall_status": "PARTIAL_REMEDIATION_REQUIRED"}, "coverage audit v2 summary mismatch")

    require(audit.get("schema_version") == "item-130-mandatory-test-coverage-audit.v3", "current coverage schema mismatch")
    require(audit.get("audit_id") == "ITEM-130-MANDATORY-COVERAGE-2026-08-07-3", "current coverage audit id mismatch")
    require(audit.get("audit_date") == "2026-08-07", "current coverage audit date mismatch")
    require(audit.get("scope") == "RATIFIED_ITEM_130_NON_MONETARY_FACT_MODEL_ONLY", "current coverage scope mismatch")
    require(audit.get("financial_authority") == "UNCHANGED_PROHIBITED", "coverage audit expanded financial authority")
    require(audit.get("unresolved_assumptions") == [], "coverage audit carries a silent assumption")

    supersedes = audit.get("supersedes")
    require(supersedes == {"audit_id": v2["audit_id"], "path": "docs/decisions/0005-item-130-mandatory-test-coverage-audit-2.json", "sha256": V2_SHA256}, "current coverage supersession mismatch")
    require(audit.get("history") == [
        {"audit_id": v1["audit_id"], "path": "docs/decisions/0005-item-130-mandatory-test-coverage-audit.json", "sha256": V1_SHA256},
        {"audit_id": v2["audit_id"], "path": "docs/decisions/0005-item-130-mandatory-test-coverage-audit-2.json", "sha256": V2_SHA256},
    ], "coverage history mismatch")

    dossier = load_json(DOSSIER_PATH)
    contract = audit.get("contract")
    require(isinstance(contract, dict) and contract.get("decision_number") == "0005", "coverage contract mismatch")
    require(contract.get("mandatory_category_count") == 18, "coverage contract count mismatch")
    require(contract.get("base_dossier_sha256") == hashlib.sha256(DOSSIER_PATH.read_bytes()).hexdigest().upper(), "coverage base dossier hash mismatch")
    require(len(dossier.get("mandatory_tests", [])) == 18, "ratified mandatory-test list mismatch")

    provenance = audit.get("provenance_catalog")
    require(isinstance(provenance, dict) and len(provenance) == 3, "current coverage provenance catalog mismatch")
    for provenance_id, record in provenance.items():
        require(provenance_id.startswith("P-130-COVERAGE3-"), f"invalid coverage provenance id {provenance_id}")
        for field in ("source_id", "document_version", "effective_period", "locator", "retrieval_date", "interpretation_status"):
            require(isinstance(record.get(field), str) and record[field], f"{provenance_id} lacks {field}")

    inventory = audit.get("artifact_inventory")
    require(isinstance(inventory, list) and len(inventory) == 13, "current coverage artifact inventory mismatch")
    seen_paths: set[str] = set()
    for artifact in inventory:
        path_text = artifact.get("path")
        require(isinstance(path_text, str) and path_text not in seen_paths, "coverage artifact path missing or duplicated")
        seen_paths.add(path_text)
        path = ROOT / path_text
        require(path.is_file(), f"coverage artifact does not exist: {path_text}")
        require(artifact.get("sha256") == hashlib.sha256(path.read_bytes()).hexdigest().upper(), f"coverage artifact hash mismatch: {path_text}")

    logical = load_module(ROOT / "scripts" / "validate_logical_schema_fixtures.py", "item130_logical_coverage_v3")
    fixture_paths = sorted(ITEM_FIXTURE_DIR.glob("item-130-*.json"))
    require(len(fixture_paths) == 7, "Item 130 fixture inventory must contain seven files")
    fixtures: dict[str, dict] = {}
    for path in fixture_paths:
        fixture = load_json(path)
        logical.validate_fixture(fixture)
        fixtures[fixture["fixture_id"]] = fixture
    require(set(fixtures) == {f"SYNTH-LS-{number:03d}" for number in range(13, 20)}, "Item 130 fixture id set mismatch")

    inheritance = audit.get("coverage_inheritance")
    require(isinstance(inheritance, dict), "coverage inheritance missing")
    require(inheritance.get("unchanged_ordinals") == list(range(1, 18)), "unchanged coverage ordinals mismatch")
    updates = inheritance.get("updates")
    require(isinstance(updates, list) and len(updates) == 1, "coverage update set mismatch")
    update = updates[0]
    require(update.get("ordinal") == 18 and update.get("category") == dossier["mandatory_tests"][17], "forbidden-output coverage category mismatch")
    require(update.get("previous_status") == "PARTIAL" and update.get("current_status") == "COVERED", "forbidden-output coverage status mismatch")
    require(update.get("closed_gap_id") == "GAP-130-TEST-FORBIDDEN-FIELD-ALIASES", "closed alias gap id mismatch")
    require(update.get("guard_scope") == "ALL_RECORDS_IN_EVERY_ITEM_130_SCENARIO_RECURSIVELY", "forbidden-output guard scope mismatch")
    require(update.get("key_normalization") == "LOWERCASE_REMOVE_NON_ALPHANUMERIC", "forbidden-output key normalization mismatch")
    require(update.get("canonical_forbidden_key_count") == len(logical.ITEM_130_FORBIDDEN_OUTPUT_KEYS) == 50, "forbidden-output key count mismatch")
    require(update.get("focused_probe_fixture_id") == "SYNTH-LS-019", "forbidden-output probe fixture mismatch")
    require(update.get("focused_probe_count") == 6, "forbidden-output probe count mismatch")
    require(update.get("focused_probe_fields") == EXPECTED_PROBE_FIELDS, "forbidden-output probe field set mismatch")
    require(set(update.get("provenance_ids", [])) == set(provenance), "forbidden-output update provenance mismatch")

    probe_mutations = [
        lambda value: value["records"]["shipment_articles"][0].__setitem__("rate_date_role", "ACTUAL_PICKUP"),
        lambda value: value["records"]["shipment_articles"][0].__setitem__("quantity_for_billing", "1"),
        lambda value: value["records"]["shipment_articles"][0].__setitem__("rateDateRole", "ACTUAL_PICKUP"),
        lambda value: value["records"]["shipment_articles"][0].__setitem__("billingQuantity", "1"),
        lambda value: value["records"]["shipment_articles"][0].__setitem__("derived_output", {"rate-date": "2026-06-12"}),
        lambda value: value["records"]["evidence_links"][0].__setitem__("financial_output", {"expectedAmount": "297.78"}),
    ]
    for mutate in probe_mutations:
        changed = copy.deepcopy(fixtures["SYNTH-LS-019"])
        mutate(changed)
        try:
            logical.validate_fixture(changed)
        except logical.ValidationError:
            continue
        raise ValidationError("current forbidden-output guard accepted an alias probe")

    statuses = {row["ordinal"]: row["status"] for row in v1["coverage"]}
    v2_update = v2["coverage_inheritance"]["updates"][0]
    require(v2_update.get("ordinal") == 17 and v2_update.get("current_status") == "COVERED", "coverage audit v2 update mismatch")
    statuses[17] = "COVERED"
    statuses[18] = update["current_status"]
    summary = audit.get("effective_coverage_summary")
    require(summary == {"covered_count": 18, "partial_count": 0, "missing_count": 0, "overall_status": "COMPLETE_FOR_RATIFIED_NON_MONETARY_SYNTHETIC_CONTRACT"}, "current coverage summary mismatch")
    require(all(status == "COVERED" for status in statuses.values()), "not every mandatory category is covered")
    require(audit.get("remaining_test_gap_ids") == [], "current audit retains a test gap")
    require(audit.get("unresolved_source_gap_ids") == ["GAP-130-LAWNMOWER-ROW", "GAP-130E-SUBTYPE-ROWS", "GAP-130F-BOTO-BOUNDARY", "GAP-130-COMBINED-VS-OD"], "source gaps were changed")
    require(audit.get("open_conflict_ids") == ["CF-0001", "CF-0003"], "Item 130 conflict gates were changed")
    require("does not approve" in audit.get("completion_boundary", ""), "completion boundary is overstated")
    require(isinstance(audit.get("next_action"), str) and audit["next_action"], "coverage audit lacks next action")


def main() -> int:
    try:
        v1 = load_json(V1_PATH)
        v2 = load_json(V2_PATH)
        audit = load_json(CURRENT_PATH)
        validate(audit, v1, v2)
        probes = [
            ("v2 history hash", lambda value: value["supersedes"].__setitem__("sha256", "0" * 64)),
            ("false alias status", lambda value: value["coverage_inheritance"]["updates"][0].__setitem__("current_status", "PARTIAL")),
            ("guard scope", lambda value: value["coverage_inheritance"]["updates"][0].__setitem__("guard_scope", "ONE_FIXTURE_ONLY")),
            ("artifact hash", lambda value: value["artifact_inventory"][0].__setitem__("sha256", "0" * 64)),
            ("source gap removal", lambda value: value["unresolved_source_gap_ids"].pop()),
            ("financial authority", lambda value: value.__setitem__("financial_authority", "ITEM_130_FINANCIAL_RULES_AUTHORIZED")),
        ]
        for label, mutate in probes:
            changed = copy.deepcopy(audit)
            mutate(changed)
            try:
                validate(changed, v1, v2)
            except ValidationError:
                print(f"PASS Item 130 coverage v3 tamper rejected: {label}")
                continue
            raise ValidationError(f"Item 130 coverage v3 tamper accepted: {label}")
        print("PASS Item 130 mandatory coverage audit v3: 18 covered, 0 partial, 0 missing, immutable v1/v2 history, 6 forbidden-output probes, and 6 tamper probes")
        return 0
    except (OSError, StopIteration, json.JSONDecodeError, KeyError, TypeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

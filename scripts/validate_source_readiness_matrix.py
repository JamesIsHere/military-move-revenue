#!/usr/bin/env python3
"""Validate monetary source-readiness references and all-gates-pass logic."""

from __future__ import annotations

import copy
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "docs" / "monetary-source-readiness-matrix.json"
REGISTRY_PATH = ROOT / "rules" / "registry" / "registry.json"
MANIFEST_PATH = ROOT / "sources" / "source-manifest.csv"
GATES = ["governing_rule", "numeric_rate", "effective_date_selector", "billing_item_contract", "evidence_contract", "audit_matching_support"]
ASSESSMENT_ID = "DP3-MONETARY-READINESS-2026-08-04-2"


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


def registry_ids(registry: dict) -> set[str]:
    result: set[str] = set()
    for value in registry.values():
        if isinstance(value, list):
            result.update(record["id"] for record in value if isinstance(record, dict) and isinstance(record.get("id"), str))
    return result


def validate(matrix: dict, registry: dict, manifest_ids: set[str]) -> None:
    require(matrix.get("schema_version") == "monetary-source-readiness.v1", "matrix schema version mismatch")
    require(matrix.get("gate_policy_id") == "MONETARY-SOURCE-READINESS-GATE-V1", "gate policy id mismatch")
    require(matrix.get("gate_policy_version") == "2026-08-04.1", "gate policy version mismatch")
    require(matrix.get("assessment_id") == ASSESSMENT_ID, "assessment id mismatch")
    require(matrix.get("assessment_date") == "2026-08-04", "assessment date mismatch")
    require(matrix.get("required_gates") == GATES, "required gate sequence mismatch")
    require(matrix.get("unresolved_assumptions") == [], "matrix contains unresolved assumptions")

    source_versions = {value["id"]: value for value in registry["source_versions"]}
    all_registry_ids = registry_ids(registry)
    conflicts = {value["id"]: value for value in registry["conflict_cases"]}
    provenance = matrix.get("provenance_catalog")
    require(isinstance(provenance, dict) and provenance, "provenance catalog is missing")
    for provenance_id, record in provenance.items():
        require(isinstance(provenance_id, str) and provenance_id.startswith("P-"), "invalid provenance id")
        require(isinstance(record, dict), f"{provenance_id} must be an object")
        source_id = record.get("source_id")
        version_id = record.get("source_version_id")
        require(source_id in manifest_ids, f"{provenance_id} source is absent from manifest")
        require(version_id in source_versions and source_versions[version_id]["source_id"] == source_id, f"{provenance_id} source version mismatch")
        for field in ("document_version", "effective_period", "locator", "retrieval_date", "interpretation_status"):
            require(isinstance(record.get(field), str) and record[field], f"{provenance_id} lacks {field}")

    blockers = matrix.get("blockers")
    require(isinstance(blockers, dict) and blockers, "blocker catalog is missing")
    for blocker_id, blocker in blockers.items():
        require(isinstance(blocker.get("closure_target"), str) and blocker["closure_target"], f"{blocker_id} lacks closure target")
        has_conflict = "conflict_id" in blocker
        has_gap = "internal_gap_id" in blocker
        require(has_conflict != has_gap, f"{blocker_id} must identify exactly one blocker kind")
        if has_conflict:
            conflict_id = blocker["conflict_id"]
            require(conflict_id in conflicts and conflicts[conflict_id]["status"] == "open", f"{blocker_id} does not reference an open conflict")
        else:
            require(isinstance(blocker["internal_gap_id"], str) and blocker["internal_gap_id"].startswith("GAP-"), f"{blocker_id} gap id is invalid")

    candidates = matrix.get("candidates")
    require(isinstance(candidates, list) and candidates, "candidate list is missing")
    candidate_ids: set[str] = set()
    ranked: list[int] = []
    for candidate in candidates:
        candidate_id = candidate.get("candidate_id")
        require(isinstance(candidate_id, str) and candidate_id not in candidate_ids, "candidate id is missing or duplicated")
        candidate_ids.add(candidate_id)
        require(isinstance(candidate.get("selection_rationale"), str) and candidate["selection_rationale"], f"{candidate_id} lacks rationale")
        gates = candidate.get("gates")
        require(isinstance(gates, dict) and list(gates) == GATES, f"{candidate_id} gate set/order mismatch")
        all_pass = True
        for gate_name, gate in gates.items():
            require(isinstance(gate, dict) and gate.get("status") in {"PASS", "BLOCKED"}, f"{candidate_id}/{gate_name} status invalid")
            provenance_ids = gate.get("provenance_ids")
            blocker_ids = gate.get("blocker_ids")
            require(isinstance(provenance_ids, list) and provenance_ids and len(set(provenance_ids)) == len(provenance_ids), f"{candidate_id}/{gate_name} provenance invalid")
            require(all(value in provenance for value in provenance_ids), f"{candidate_id}/{gate_name} references unknown provenance")
            require(isinstance(blocker_ids, list) and len(set(blocker_ids)) == len(blocker_ids), f"{candidate_id}/{gate_name} blockers invalid")
            require(all(value in blockers for value in blocker_ids), f"{candidate_id}/{gate_name} references unknown blocker")
            refs = gate.get("registry_refs", [])
            require(isinstance(refs, list) and all(value in all_registry_ids for value in refs), f"{candidate_id}/{gate_name} registry reference invalid")
            if gate["status"] == "PASS":
                require(not blocker_ids, f"{candidate_id}/{gate_name} passes with a blocker")
            else:
                require(blocker_ids, f"{candidate_id}/{gate_name} blocks without a blocker")
                all_pass = False
        expected_readiness = "READY_IMPLEMENTED" if all_pass else "BLOCKED"
        require(candidate.get("readiness") == expected_readiness, f"{candidate_id} readiness contradicts gates")
        if expected_readiness == "READY_IMPLEMENTED":
            require(candidate.get("implementation_status") == "published_and_audited", f"{candidate_id} ready status is not published and audited")
        else:
            require(candidate.get("implementation_status") != "published_and_audited", f"{candidate_id} blocked status claims published audit coverage")
        rank = candidate.get("rank")
        if expected_readiness == "READY_IMPLEMENTED":
            require(rank is None, f"{candidate_id} implemented reference must be unranked")
        else:
            require(isinstance(rank, int) and rank > 0, f"{candidate_id} blocked rank is invalid")
            ranked.append(rank)
    require(sorted(ranked) == list(range(1, len(ranked) + 1)), "blocked candidate ranks are not contiguous")
    selected = matrix.get("recommended_next_candidate_id")
    selected_rows = [value for value in candidates if value["candidate_id"] == selected]
    require(len(selected_rows) == 1 and selected_rows[0]["rank"] == 1 and selected_rows[0]["readiness"] == "BLOCKED", "recommended candidate must be rank-one blocked family")
    require(isinstance(matrix.get("recommended_next_action"), str) and matrix["recommended_next_action"], "recommended action is missing")


def set_path(target: dict, path: str, value: object) -> None:
    current: object = target
    parts = path.split(".")
    for part in parts[:-1]:
        current = current[int(part)] if isinstance(current, list) else current[part]  # type: ignore[index]
    if isinstance(current, list):
        current[int(parts[-1])] = value
    else:
        current[parts[-1]] = value  # type: ignore[index]


def main() -> int:
    try:
        matrix = load_json(MATRIX_PATH)
        registry = load_json(REGISTRY_PATH)
        with MANIFEST_PATH.open(encoding="utf-8-sig", newline="") as handle:
            manifest_ids = {row["source_id"] for row in csv.DictReader(handle)}
        validate(matrix, registry, manifest_ids)
        probes = [
            ("false readiness", "candidates.2.readiness", "READY_IMPLEMENTED"),
            ("pass with blocker", "candidates.2.gates.billing_item_contract.status", "PASS"),
            ("unknown provenance", "candidates.1.gates.numeric_rate.provenance_ids.0", "P-UNKNOWN"),
            ("missing closure", "blockers.BLK-CF-0003.closure_target", ""),
            ("rank gap", "candidates.3.rank", 9),
            ("wrong recommendation", "recommended_next_candidate_id", "ITEM-130-LIGHT-BULKY"),
        ]
        for label, path, value in probes:
            tampered = copy.deepcopy(matrix)
            set_path(tampered, path, value)
            try:
                validate(tampered, registry, manifest_ids)
            except ValidationError:
                print(f"PASS readiness tamper rejected: {label}")
                continue
            raise ValidationError(f"readiness tamper accepted: {label}")
        print(f"PASS {len(matrix['candidates'])} readiness candidates, {len(matrix['provenance_catalog'])} provenance records, {len(matrix['blockers'])} blockers, and 6 tamper probes")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

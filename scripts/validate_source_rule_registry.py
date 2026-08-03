#!/usr/bin/env python3
"""Validate the file-backed source/rule registry and its regression cases."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "rules" / "registry" / "registry.json"
CASE_PATH = ROOT / "tests" / "fixtures" / "source-rule-registry" / "registry-cases.json"
INTERPRETATION_STATUSES = {"candidate", "reviewed", "disputed", "approved", "superseded"}
PUBLICATION_STATUSES = {"draft", "published", "retired"}
SHA256_RE = re.compile(r"^[0-9A-Fa-f]{64}$")


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def records(registry: dict, collection: str) -> list[dict]:
    value = registry.get(collection)
    require(isinstance(value, list), f"{collection} must be a list")
    require(all(isinstance(record, dict) for record in value), f"{collection} records must be objects")
    return value


def index_by_id(registry: dict, collection: str) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for record in records(registry, collection):
        record_id = record.get("id")
        require(isinstance(record_id, str) and record_id, f"{collection} record lacks id")
        require(record_id not in result, f"duplicate {collection} id {record_id}")
        result[record_id] = record
    return result


def parse_date(value: object, label: str) -> date:
    require(isinstance(value, str) and value, f"{label} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(f"{label} must be an ISO date: {value!r}") from exc


def nonempty(record: dict, fields: tuple[str, ...], label: str) -> None:
    for field in fields:
        value = record.get(field)
        require(isinstance(value, str) and value.strip(), f"{label}.{field} is required")


def load_manifest(registry: dict) -> dict[str, dict[str, str]]:
    relative = registry.get("source_manifest_path")
    require(isinstance(relative, str) and relative, "source_manifest_path is required")
    manifest_path = (ROOT / relative).resolve()
    require(manifest_path.is_relative_to(ROOT), "source_manifest_path must remain inside the repository")
    require(manifest_path.is_file(), f"source manifest does not exist: {relative}")

    with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(rows, "source manifest must not be empty")

    result: dict[str, dict[str, str]] = {}
    required = {
        "source_id",
        "file_name",
        "issuer",
        "title",
        "version_or_publication",
        "effective_from",
        "effective_to",
        "retrieved_on",
        "bytes",
        "sha256",
        "canonical_url",
        "status",
    }
    require(required.issubset(rows[0]), "source manifest is missing required columns")
    for row in rows:
        source_id = row["source_id"]
        require(source_id and source_id not in result, f"duplicate manifest source_id {source_id!r}")
        for field in (
            "file_name",
            "issuer",
            "title",
            "version_or_publication",
            "retrieved_on",
            "bytes",
            "sha256",
            "canonical_url",
            "status",
        ):
            require(row[field].strip(), f"manifest[{source_id}].{field} is required")
        require(row["bytes"].isdigit() and int(row["bytes"]) > 0, f"manifest[{source_id}].bytes must be positive")
        require(SHA256_RE.fullmatch(row["sha256"]) is not None, f"manifest[{source_id}].sha256 must be 64 hexadecimal characters")
        result[source_id] = row
    return result


def validate_source_versions(registry: dict, manifest: dict[str, dict[str, str]]) -> dict[str, dict]:
    versions = index_by_id(registry, "source_versions")
    by_source: dict[str, list[str]] = defaultdict(list)

    for version_id, version in versions.items():
        label = f"source_versions[{version_id}]"
        nonempty(
            version,
            (
                "source_id",
                "source_kind",
                "authoritativeness_class",
                "raw_artifact_path",
                "media_type",
                "extraction_method",
                "interpretation_status",
            ),
            label,
        )
        source_id = version["source_id"]
        require(source_id in manifest, f"{label} references unknown manifest source {source_id}")
        by_source[source_id].append(version_id)
        require(
            version["interpretation_status"] in INTERPRETATION_STATUSES,
            f"{label} has invalid interpretation_status",
        )

        manifest_row = manifest[source_id]
        require(manifest_row["status"] == "archived", f"{label} manifest status must be archived")
        parse_date(manifest_row["retrieved_on"], f"manifest[{source_id}].retrieved_on")
        for field in ("effective_from", "effective_to"):
            if manifest_row[field]:
                parse_date(manifest_row[field], f"manifest[{source_id}].{field}")
        if manifest_row["effective_from"] and manifest_row["effective_to"]:
            require(
                date.fromisoformat(manifest_row["effective_from"])
                <= date.fromisoformat(manifest_row["effective_to"]),
                f"manifest[{source_id}] has an inverted effective period",
            )

        relative = Path(version["raw_artifact_path"])
        require(not relative.is_absolute() and ".." not in relative.parts, f"{label} artifact path must be repository-relative")
        artifact_path = (ROOT / relative).resolve()
        require(artifact_path.is_relative_to(ROOT), f"{label} artifact path escapes the repository")
        require(artifact_path.is_file(), f"{label} artifact does not exist: {relative.as_posix()}")
        require(relative.name == manifest_row["file_name"], f"{label} file name differs from the manifest")

        content = artifact_path.read_bytes()
        actual_hash = hashlib.sha256(content).hexdigest().upper()
        require(str(len(content)) == manifest_row["bytes"], f"{label} byte length differs from the manifest")
        require(actual_hash == manifest_row["sha256"].upper(), f"{label} SHA-256 differs from the manifest")

    archived_sources = {source_id for source_id, row in manifest.items() if row["status"] == "archived"}
    require(set(by_source) == archived_sources, "each archived manifest source must have exactly one physical source version")
    for source_id, version_ids in by_source.items():
        require(len(version_ids) == 1, f"manifest source {source_id} has multiple unversioned registry entries")
    return versions


def validate_registry(registry: dict) -> None:
    require(registry.get("schema_version") == "source-rule-registry-v1", "unsupported registry schema_version")
    require(registry.get("scope_code") == "DOMESTIC_DP3_TSP_GOV_POST_AUDIT", "registry scope exceeds v1")
    require(registry.get("data_status") == "PUBLIC_SOURCE_ONLY", "registry data status must remain public-source-only")

    manifest = load_manifest(registry)
    versions = validate_source_versions(registry, manifest)
    observations = index_by_id(registry, "publication_observations")
    locators = index_by_id(registry, "source_locators")
    claims = index_by_id(registry, "source_claims")
    conflicts = index_by_id(registry, "conflict_cases")
    decisions = index_by_id(registry, "interpretation_decisions")
    packages = index_by_id(registry, "rule_packages")
    rules = index_by_id(registry, "rules")
    dependencies = index_by_id(registry, "rule_dependencies")
    evidence_requirements = index_by_id(registry, "evidence_requirements")

    for observation_id, observation in observations.items():
        label = f"publication_observations[{observation_id}]"
        nonempty(
            observation,
            (
                "source_id",
                "canonical_url",
                "observed_on",
                "observation",
                "artifact_status",
                "interpretation_status",
                "provenance_note",
            ),
            label,
        )
        parse_date(observation["observed_on"], f"{label}.observed_on")
        require(observation["interpretation_status"] == "candidate", f"{label} must remain candidate until its artifact is archived")
        require(not observation["artifact_status"].startswith("archived"), f"{label} must be promoted to a source version if archived")

    for locator_id, locator in locators.items():
        label = f"source_locators[{locator_id}]"
        nonempty(locator, ("source_version_id", "locator_kind", "locator_value"), label)
        require(locator["source_version_id"] in versions, f"{label} references unknown source version")

    for claim_id, claim in claims.items():
        label = f"source_claims[{claim_id}]"
        nonempty(
            claim,
            (
                "source_locator_id",
                "subject_kind",
                "subject_key",
                "predicate",
                "claim_value",
                "value_type",
                "claim_derivation_kind",
                "interpretation_status",
            ),
            label,
        )
        require(claim["source_locator_id"] in locators, f"{label} references unknown locator")
        require(claim["interpretation_status"] in INTERPRETATION_STATUSES, f"{label} has invalid interpretation_status")
        if claim.get("value_type") == "integer":
            require(str(claim["claim_value"]).isdigit(), f"{label} integer claim must contain digits")
            require(isinstance(claim.get("unit"), str) and claim["unit"], f"{label} integer quantity requires a unit")

    decisions_by_conflict: dict[str, list[dict]] = defaultdict(list)
    for decision_id, decision in decisions.items():
        label = f"interpretation_decisions[{decision_id}]"
        nonempty(decision, ("conflict_case_id", "decision_status", "rationale", "decided_on", "decided_by"), label)
        require(decision["conflict_case_id"] in conflicts, f"{label} references unknown conflict")
        parse_date(decision["decided_on"], f"{label}.decided_on")
        decisions_by_conflict[decision["conflict_case_id"]].append(decision)

    for conflict_id, conflict in conflicts.items():
        label = f"conflict_cases[{conflict_id}]"
        nonempty(conflict, ("topic", "status", "opened_on", "material_effect"), label)
        parse_date(conflict["opened_on"], f"{label}.opened_on")
        require(conflict["status"] in {"open", "resolved"}, f"{label} has invalid status")
        evidence_refs = conflict.get("evidence_refs")
        require(isinstance(evidence_refs, list) and len(evidence_refs) >= 2, f"{label} requires at least two evidence references")
        distinct_refs: set[tuple[str, str]] = set()
        for evidence in evidence_refs:
            require(isinstance(evidence, dict), f"{label} evidence reference must be an object")
            nonempty(evidence, ("record_kind", "record_id", "claim_role"), f"{label}.evidence_ref")
            kind = evidence["record_kind"]
            record_id = evidence["record_id"]
            require(kind in {"source_claim", "publication_observation"}, f"{label} has invalid evidence record_kind")
            if kind == "source_claim":
                require(record_id in claims, f"{label} references unknown source claim {record_id}")
            else:
                require(record_id in observations, f"{label} references unknown publication observation {record_id}")
            distinct_refs.add((kind, record_id))
        require(len(distinct_refs) >= 2, f"{label} evidence references must be distinct")

        affected_rule_ids = conflict.get("affected_rule_ids")
        require(isinstance(affected_rule_ids, list) and affected_rule_ids, f"{label} requires affected_rule_ids")
        for rule_id in affected_rule_ids:
            require(rule_id in rules, f"{label} references unknown affected rule {rule_id}")
            require(conflict_id in rules[rule_id].get("blocked_by_conflict_ids", []), f"{label} is not reciprocal on rule {rule_id}")
        if conflict["status"] == "resolved":
            approved = [decision for decision in decisions_by_conflict[conflict_id] if decision["decision_status"] == "approved"]
            require(approved, f"{label} cannot resolve without an approved interpretation decision")

    rules_by_package: dict[str, list[dict]] = defaultdict(list)
    for package_id, package in packages.items():
        label = f"rule_packages[{package_id}]"
        nonempty(package, ("package_code", "version", "scope_code", "effective_from", "publication_status"), label)
        require(package["scope_code"] == registry["scope_code"], f"{label} scope differs from registry scope")
        require(package["publication_status"] in PUBLICATION_STATUSES, f"{label} has invalid publication_status")
        start = parse_date(package["effective_from"], f"{label}.effective_from")
        if package.get("effective_to"):
            require(start <= parse_date(package["effective_to"], f"{label}.effective_to"), f"{label} has inverted effective period")
        if package["publication_status"] == "published":
            parse_date(package.get("published_on"), f"{label}.published_on")

    sources_by_rule: dict[str, list[dict]] = defaultdict(list)
    seen_rule_source_pairs: set[tuple[str, str]] = set()
    for index, rule_source in enumerate(records(registry, "rule_sources")):
        label = f"rule_sources[{index}]"
        nonempty(rule_source, ("rule_id", "source_claim_id", "source_role"), label)
        require(rule_source["rule_id"] in rules, f"{label} references unknown rule")
        require(rule_source["source_claim_id"] in claims, f"{label} references unknown archived source claim")
        pair = (rule_source["rule_id"], rule_source["source_claim_id"])
        require(pair not in seen_rule_source_pairs, f"duplicate rule/source pair {pair}")
        seen_rule_source_pairs.add(pair)
        sources_by_rule[rule_source["rule_id"]].append(rule_source)

    dependencies_by_rule: dict[str, list[dict]] = defaultdict(list)
    for dependency_id, dependency in dependencies.items():
        label = f"rule_dependencies[{dependency_id}]"
        nonempty(
            dependency,
            ("rule_id", "input_fact_type", "cardinality", "unit", "default_prohibited_reason"),
            label,
        )
        require(dependency["rule_id"] in rules, f"{label} references unknown rule")
        dependencies_by_rule[dependency["rule_id"]].append(dependency)

    evidence_by_rule: dict[str, list[dict]] = defaultdict(list)
    for requirement_id, requirement in evidence_requirements.items():
        label = f"evidence_requirements[{requirement_id}]"
        nonempty(
            requirement,
            ("rule_id", "requirement_code", "target_kind", "document_or_fact_type"),
            label,
        )
        require(requirement["rule_id"] in rules, f"{label} references unknown rule")
        minimum_count = requirement.get("minimum_count")
        require(isinstance(minimum_count, int) and minimum_count >= 0, f"{label}.minimum_count must be a nonnegative integer")
        if requirement.get("condition_rule_id"):
            require(requirement["condition_rule_id"] in rules, f"{label} references unknown condition rule")
        evidence_by_rule[requirement["rule_id"]].append(requirement)

    for rule_id, rule in rules.items():
        label = f"rules[{rule_id}]"
        nonempty(
            rule,
            (
                "rule_package_id",
                "rule_kind",
                "expression_language",
                "expression",
                "outcome_type",
                "implementation_status",
                "publication_status",
            ),
            label,
        )
        require(rule["rule_package_id"] in packages, f"{label} references unknown package")
        rules_by_package[rule["rule_package_id"]].append(rule)
        require(rule["publication_status"] in PUBLICATION_STATUSES, f"{label} has invalid publication_status")
        require(rule["implementation_status"] in {"not_implemented", "implemented"}, f"{label} has invalid implementation_status")
        require(sources_by_rule[rule_id], f"{label} lacks source provenance")

        blocked = rule.get("blocked_by_conflict_ids", [])
        require(isinstance(blocked, list), f"{label}.blocked_by_conflict_ids must be a list")
        for conflict_id in blocked:
            require(conflict_id in conflicts, f"{label} references unknown conflict {conflict_id}")
            require(rule_id in conflicts[conflict_id]["affected_rule_ids"], f"{label} conflict {conflict_id} is not reciprocal")

        if rule["publication_status"] == "published":
            open_conflicts = [conflict_id for conflict_id in blocked if conflicts[conflict_id]["status"] == "open"]
            require(not open_conflicts, f"{label} cannot publish through open conflict(s): {', '.join(open_conflicts)}")
            require(rule["implementation_status"] == "implemented", f"{label} must be implemented before publication")
            require(dependencies_by_rule[rule_id], f"{label} must declare every input dependency before publication")
            require(
                packages[rule["rule_package_id"]]["publication_status"] == "published",
                f"{label} cannot publish inside a non-published package",
            )
            for source in sources_by_rule[rule_id]:
                status = claims[source["source_claim_id"]]["interpretation_status"]
                require(status in {"reviewed", "approved"}, f"{label} relies on non-accepted claim {source['source_claim_id']}")

            if rule["rule_kind"] == "evidence_validation":
                require(evidence_by_rule[rule_id], f"{label} must declare an evidence requirement")

    for package_id, package in packages.items():
        package_rules = rules_by_package[package_id]
        require(package_rules, f"rule_packages[{package_id}] must contain at least one rule")
        if package["publication_status"] == "published":
            require(
                all(rule["publication_status"] == "published" for rule in package_rules),
                f"rule_packages[{package_id}] cannot publish with non-published rules",
            )


def apply_mutation(registry: dict, mutation: dict) -> None:
    operation = mutation.get("op")
    collection = mutation.get("collection")
    require(isinstance(collection, str), "fixture mutation collection is required")
    collection_records = records(registry, collection)

    if operation == "set":
        record_id = mutation.get("id")
        matches = [record for record in collection_records if record.get("id") == record_id]
        require(len(matches) == 1, f"fixture set mutation could not find {collection} id {record_id}")
        field = mutation.get("field")
        require(isinstance(field, str) and field, "fixture set mutation field is required")
        matches[0][field] = mutation.get("value")
        return

    if operation == "remove_where":
        field = mutation.get("field")
        value = mutation.get("value")
        before = len(collection_records)
        collection_records[:] = [record for record in collection_records if record.get(field) != value]
        require(len(collection_records) < before, f"fixture remove_where mutation removed no {collection} records")
        return

    raise ValidationError(f"unsupported fixture mutation operation {operation!r}")


def run_cases(base_registry: dict) -> None:
    suite = load_json(CASE_PATH)
    cases = suite.get("cases")
    require(isinstance(cases, list) and cases, "registry fixture suite requires cases")

    for case in cases:
        nonempty(case, ("id", "description"), "fixture_case")
        expected_valid = case.get("expected_valid")
        require(isinstance(expected_valid, bool), f"fixture {case['id']} expected_valid must be boolean")
        candidate = copy.deepcopy(base_registry)
        mutations = case.get("mutations", [])
        require(isinstance(mutations, list), f"fixture {case['id']} mutations must be a list")
        for mutation in mutations:
            require(isinstance(mutation, dict), f"fixture {case['id']} mutation must be an object")
            apply_mutation(candidate, mutation)

        try:
            validate_registry(candidate)
        except ValidationError as exc:
            if expected_valid:
                raise ValidationError(f"fixture {case['id']} unexpectedly failed: {exc}") from exc
            expected_error = case.get("error_contains")
            require(
                isinstance(expected_error, str) and expected_error in str(exc),
                f"fixture {case['id']} failed for the wrong reason: {exc}",
            )
            print(f"PASS {case['id']} rejected: {exc}")
        else:
            require(expected_valid, f"fixture {case['id']} unexpectedly passed")
            print(f"PASS {case['id']} accepted")


def main() -> int:
    try:
        registry = load_json(REGISTRY_PATH)
        validate_registry(registry)
        print("PASS physical source/rule registry")
        run_cases(registry)
        print("PASS all source/rule registry cases")
        return 0
    except (OSError, csv.Error, json.JSONDecodeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

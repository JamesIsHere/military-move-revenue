#!/usr/bin/env python3
"""Validate the revised Item 130 fact-model architecture and preserved v1 base."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import validate_item_130_fact_model_dossier as v1


ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "docs" / "decisions" / "0005-item-130-fact-model-dossier.json"
REVISED_PATH = ROOT / "docs" / "decisions" / "0005-item-130-fact-model-dossier-v2.json"
REGISTRY_PATH = ROOT / "rules" / "registry" / "registry.json"
DECISION_PATH = ROOT / "docs" / "decisions" / "0005-item-130-fact-model-revision-decision.md"
RATIFICATION_PATH = ROOT / "docs" / "decisions" / "0005-item-130-revised-fact-model-approval.md"
BASE_SHA256 = "68B5A485FF086F02DE466606E5A2FAE55462D40B8AE21020C3AD6F08AF435C4E"
INHERITED_SECTIONS = [
    "source_basis", "internal_basis", "conflict_ids", "financial_contract",
    "tariff_classifications", "candidate_item_code_observation", "source_mismatches",
    "mandatory_tests", "excluded_scope", "implementation_gate", "unresolved_assumptions",
]
COMMON_FIELDS = {
    "id", "recorded_at", "recorded_by", "record_source_kind", "source_version_id",
    "source_locator_id", "interpretation_status", "sensitivity_class",
    "sanitization_status", "supersedes_id", "correction_reason",
}
NEW_ENTITIES = {
    "shipment_article": {"shipment_id", "article_kind_observed", "tariff_classification_candidate", "associated_trailer_status", "source_description", "classification_review_status"},
    "article_measurement_observation": {"article_id", "measurement_kind", "measurement_value", "measurement_unit", "measurement_method", "observed_at", "review_status", "evidence_link_id"},
    "article_condition_observation": {"article_id", "condition_kind", "condition_value", "observed_at", "evidence_link_id"},
    "article_service_context_observation": {"article_id", "context_kind", "context_value_text", "context_review_status", "observed_at", "evidence_link_id"},
    "combined_handling_pair_candidate": {"article_id", "loading_service_performance_id", "unloading_service_performance_id", "pairing_status", "pairing_basis", "sit_episode_id", "evidence_link_id"},
}
PROFILES = {
    "ITEM_130_ARTICLE_HANDLING_SERVICE_PERFORMANCE_PROFILE": {
        "reuses_entity": "service_performance",
        "fields": {"article_id", "candidate_service_family", "observed_handling_kind", "mapping_status", "service_definition_id", "performed_at", "performance_status", "shipment_stop_id", "sit_episode_id", "tsp_convenience_status", "evidence_link_id"},
        "prohibited_fields": {"quantity", "quantity_unit", "billing_item_code", "rate_version", "expected_amount"},
    },
    "ITEM_130_GOVERNMENT_PREAPPROVAL_PROFILE": {
        "reuses_entity": "service_approval_event",
        "fields": {"service_performance_id", "approval_event_type", "decision_status", "occurred_at", "approver_role_text", "approver_role_mapping_status", "authorization_reference", "evidence_link_id"},
        "prohibited_fields": {"standardized_approver_role", "billing_item_code", "financial_eligibility", "expected_amount"},
    },
}


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict:
    def reject_float(value: str) -> None:
        raise ValidationError(f"{path.name} contains non-exact JSON number {value}")

    with path.open(encoding="utf-8") as handle:
        value = json.load(handle, parse_float=reject_float)
    require(isinstance(value, dict), f"{path.name} must contain an object")
    return value


def field_contract(fields: object, expected: set[str], known_provenance: set[str], owner: str) -> int:
    require(isinstance(fields, list), f"{owner} fields are missing")
    names = [field.get("field") for field in fields]
    require(set(names) == expected and len(names) == len(set(names)), f"{owner} field set mismatch")
    for field in fields:
        for key in ("logical_type", "cardinality", "evidence_requirement", "interpretation_status"):
            require(isinstance(field.get(key), str) and field[key], f"{owner}.{field.get('field')} lacks {key}")
        provenance = field.get("provenance_ids")
        require(isinstance(provenance, list) and provenance and len(provenance) == len(set(provenance)), f"{owner}.{field.get('field')} provenance is invalid")
        require(all(value in known_provenance for value in provenance), f"{owner}.{field.get('field')} references unknown provenance")
    return len(fields)


def validate(revised: dict, base: dict, registry: dict, *, validate_preserved_base: bool = True) -> tuple[int, int]:
    if validate_preserved_base:
        try:
            v1.validate(base, registry)
        except v1.ValidationError as exc:
            raise ValidationError(f"preserved v1 base is invalid: {exc}") from exc

    actual_hash = hashlib.sha256(BASE_PATH.read_bytes()).hexdigest().upper()
    require(actual_hash == BASE_SHA256, "preserved v1 dossier hash changed")
    require(revised.get("schema_version") == "non-monetary-fact-model-dossier.v2", "revised schema version mismatch")
    require(revised.get("decision_number") == "0005" and revised.get("dossier_version") == "2", "revised dossier identity mismatch")
    require(revised.get("status") == "REVISED_PROPOSAL_OWNER_REVIEW_REQUIRED", "revised proposal status advanced without review")
    require(revised.get("scope") == "DOMESTIC_400NG_ITEM_130_FACT_AND_EVIDENCE_MODEL_ONLY", "revised scope mismatch")
    require(revised.get("approval") == {"selected_alternative": None, "approved_by": None, "approved_on": None, "interpretation_decision_id": None}, "revised approval fields must remain empty")

    revision = revised.get("revision_basis")
    require(isinstance(revision, dict) and revision.get("selected_prior_alternative") == "B_REVISE_FACT_MODEL", "owner revision selection mismatch")
    require(revision.get("interpretation_decision_id") is None, "revision created an interpretation decision")
    decision_text = DECISION_PATH.read_text(encoding="utf-8")
    require("Status: **Accepted revision request**" in decision_text and "`B_REVISE_FACT_MODEL`" in decision_text, "revision decision record is incomplete")
    ratification_text = RATIFICATION_PATH.read_text(encoding="utf-8")
    require("Status: **Ratified**" in ratification_text, "revised Alternative A is not ratified")
    require("`A_APPROVE_REVISED_FACT_MODEL_ONLY`" in ratification_text, "ratified alternative mismatch")
    require("Interpretation decision ID: none" in ratification_text, "ratification improperly creates an interpretation")

    base_contract = revised.get("base_contract")
    require(isinstance(base_contract, dict), "base contract is missing")
    require(base_contract.get("path") == "docs/decisions/0005-item-130-fact-model-dossier.json", "base path mismatch")
    require(base_contract.get("sha256") == BASE_SHA256, "base hash contract mismatch")
    require(base_contract.get("inherited_unchanged_sections") == INHERITED_SECTIONS, "inherited section contract mismatch")

    known_provenance = {record["provenance_id"] for record in base["source_basis"] + base["internal_basis"]}
    common = revised.get("common_record_contract")
    require(isinstance(common, dict) and common.get("applies_to") == "EVERY_NEW_ENTITY_AND_EXISTING_ENTITY_PROFILE", "common record scope mismatch")
    common_fields = common.get("fields")
    require(isinstance(common_fields, list), "common fields are missing")
    require({field.get("field") for field in common_fields} == COMMON_FIELDS and len(common_fields) == len(COMMON_FIELDS), "common record field contract mismatch")
    for field in common_fields:
        require(field.get("logical_type") and field.get("cardinality") and field.get("validation"), f"common field {field.get('field')} is incomplete")
        require(all(value in known_provenance for value in field.get("provenance_ids", [])), f"common field {field.get('field')} provenance mismatch")
    require(common.get("status_change_semantics") == "SUPERSEDE_RECORD_NO_IN_PLACE_UPDATE", "status changes are not append-only")
    require(common.get("current_status_semantics") == "DERIVED_FROM_LATEST_VALID_SUPERSESSION_CHAIN", "current status is not derived")

    entities = revised.get("new_entities")
    require(isinstance(entities, list) and len(entities) == len(NEW_ENTITIES), "new entity count mismatch")
    entity_names = [entity.get("entity") for entity in entities]
    require(set(entity_names) == set(NEW_ENTITIES) and len(entity_names) == len(set(entity_names)), "new entity names mismatch")
    require("article_handling_event" not in entity_names and "item_130_preapproval_event" not in entity_names, "v1 duplicate service entities survived revision")
    new_field_count = 0
    for entity in entities:
        name = entity["entity"]
        require(entity.get("change_semantics") == "SUPERSEDE_RECORD_NO_IN_PLACE_UPDATE", f"{name} is not append-only")
        require(isinstance(entity.get("purpose"), str) and entity["purpose"], f"{name} lacks purpose")
        new_field_count += field_contract(entity.get("fields"), NEW_ENTITIES[name], known_provenance, name)

    profiles = revised.get("existing_entity_profiles")
    require(isinstance(profiles, list) and len(profiles) == len(PROFILES), "profile count mismatch")
    profile_ids = [profile.get("profile_id") for profile in profiles]
    require(set(profile_ids) == set(PROFILES) and len(profile_ids) == len(set(profile_ids)), "profile identity mismatch")
    profile_field_count = 0
    for profile in profiles:
        profile_id = profile["profile_id"]
        expected = PROFILES[profile_id]
        require(profile.get("reuses_entity") == expected["reuses_entity"], f"{profile_id} canonical entity mismatch")
        require(isinstance(profile.get("schema_delta"), str) and profile["schema_delta"], f"{profile_id} schema delta is missing")
        require(profile.get("change_semantics") in {"SUPERSEDE_RECORD_NO_IN_PLACE_UPDATE", "APPEND_NEW_EVENT_NO_IN_PLACE_UPDATE"}, f"{profile_id} change semantics invalid")
        require(set(profile.get("prohibited_fields", [])) == expected["prohibited_fields"], f"{profile_id} prohibited field contract mismatch")
        profile_field_count += field_contract(profile.get("fields"), expected["fields"], known_provenance, profile_id)

    performance = next(profile for profile in profiles if profile["reuses_entity"] == "service_performance")
    service_definition = next(field for field in performance["fields"] if field["field"] == "service_definition_id")
    require("prohibited while unmapped" in service_definition["cardinality"], "unmapped service definition is not prohibited")
    approval_profile = next(profile for profile in profiles if profile["reuses_entity"] == "service_approval_event")
    approver_mapping = next(field for field in approval_profile["fields"] if field["field"] == "approver_role_mapping_status")
    require(approver_mapping["logical_type"] == "CODE<UNMAPPED,CONFLICTING>", "approver mapping was prematurely approved")

    alternatives = revised.get("revised_decision_alternatives")
    require([value.get("id") for value in alternatives] == ["A_APPROVE_REVISED_FACT_MODEL_ONLY", "B_REVISE_AGAIN"], "revised alternatives mismatch")
    financial = revised.get("financial_and_mapping_gate")
    require(isinstance(financial, dict) and financial.get("status") == "PROHIBITED", "revised financial gate is not prohibited")
    for field in ("rate_version_date_fact", "billing_item_contract", "billable_quantity", "rate", "expected_amount", "audit_adapter", "interpretation_decision_id"):
        require(financial.get(field) is None, f"revised financial field {field} must remain null")
    require(revised.get("unresolved_assumptions") == [], "revised dossier carries a silent assumption")
    return new_field_count, profile_field_count


def main() -> int:
    try:
        base = load_json(BASE_PATH)
        revised = load_json(REVISED_PATH)
        registry = load_json(REGISTRY_PATH)
        new_fields, profile_fields = validate(revised, base, registry)
        probes = [
            ("base hash", lambda value: value["base_contract"].__setitem__("sha256", "0" * 64)),
            ("approval", lambda value: value["approval"].__setitem__("selected_alternative", "A_APPROVE_REVISED_FACT_MODEL_ONLY")),
            ("duplicate service entity", lambda value: value["new_entities"][0].__setitem__("entity", "article_handling_event")),
            ("in-place status", lambda value: value["common_record_contract"].__setitem__("status_change_semantics", "UPDATE_CURRENT_ROW")),
            ("service definition", lambda value: next(field for field in value["existing_entity_profiles"][0]["fields"] if field["field"] == "service_definition_id").__setitem__("cardinality", "1")),
            ("money", lambda value: value["financial_and_mapping_gate"].__setitem__("expected_amount", "297.78")),
        ]
        for label, mutate in probes:
            changed = copy.deepcopy(revised)
            mutate(changed)
            try:
                validate(changed, base, registry, validate_preserved_base=False)
            except ValidationError:
                print(f"PASS Item 130 v2 tamper rejected: {label}")
                continue
            raise ValidationError(f"Item 130 v2 tamper accepted: {label}")
        print(f"PASS ratified Item 130 revised dossier: 5 new entities/{new_fields} fields, 2 canonical profiles/{profile_fields} fields, 11 common fields, preserved v1 source contract, and 6 tamper probes")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

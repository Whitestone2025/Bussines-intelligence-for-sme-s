#!/usr/bin/env python3
"""Contract checks for Codex Business OS MX schemas."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schemas"

SCHEMA_FILES = {
    "company": "company.schema.json",
    "research_profile": "research-profile.schema.json",
    "evidence_entry": "evidence-entry.schema.json",
    "market_model": "market-model.schema.json",
    "competitor": "competitor.schema.json",
    "pricing_model": "pricing-model.schema.json",
    "decision_memo": "decision-memo.schema.json",
    "execution_plan": "execution-plan.schema.json",
}

TRUTH_FIELDS = {
    "status",
    "confidence",
    "source_origin",
    "evidence_refs",
    "source_refs",
    "created_at",
    "updated_at",
}

REFERENCE_SEPARATION_FIELDS = {
    "market_model": {"assumption_refs", "finding_refs", "validated_fact_refs"},
    "competitor": {"assumption_refs", "finding_refs", "validated_fact_refs"},
    "pricing_model": {"assumption_refs", "finding_refs", "validated_fact_refs"},
    "decision_memo": {"assumption_refs", "finding_refs", "validated_fact_refs"},
}

STRATEGIC_MODEL_FIELDS = {
    "decision_memo": {"strategic_stack"},
    "execution_plan": {"initiative_roadmap", "decision_checkpoints", "no_regret_moves", "strategic_alternatives"},
}


def load_schema(filename: str) -> dict:
    path = SCHEMA_DIR / filename
    assert path.exists(), f"Missing schema file: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def assert_core_shape(name: str, schema: dict) -> None:
    assert schema.get("$schema"), f"{name}: missing $schema"
    assert schema.get("title"), f"{name}: missing title"
    assert schema.get("type") == "object", f"{name}: top-level type must be object"
    assert isinstance(schema.get("required"), list), f"{name}: required must be a list"
    assert isinstance(schema.get("properties"), dict), f"{name}: properties must be an object"


def assert_identifier_contract(name: str, schema: dict) -> None:
    properties = schema["properties"]
    required = set(schema["required"])
    identifier_keys = [key for key in properties if key.endswith("_id") or key == "company_id"]
    assert identifier_keys, f"{name}: no identifier field found"
    for key in identifier_keys:
        prop = properties[key]
        assert prop.get("type") == "string", f"{name}: {key} must be a string"
    primary_key = next((key for key in required if key.endswith("_id")), None)
    assert primary_key is not None, f"{name}: required primary id is missing"


def assert_truth_fields(name: str, schema: dict) -> None:
    properties = schema["properties"]
    required = set(schema["required"])
    missing = sorted(TRUTH_FIELDS - properties.keys())
    assert not missing, f"{name}: missing truth fields: {', '.join(missing)}"
    required_missing = sorted(TRUTH_FIELDS - required)
    assert not required_missing, f"{name}: required truth fields missing: {', '.join(required_missing)}"
    status_enum = properties["status"].get("enum", [])
    for expected in ("draft", "inferred", "needs_validation", "validated", "confirmed", "stale", "rejected"):
        assert expected in status_enum, f"{name}: status enum missing {expected}"
    assert properties["confidence"].get("type") == "number", f"{name}: confidence must be numeric"


def assert_reference_separation(name: str, schema: dict) -> None:
    expected_fields = REFERENCE_SEPARATION_FIELDS.get(name)
    if not expected_fields:
        return
    properties = schema["properties"]
    required = set(schema["required"])
    missing = sorted(expected_fields - properties.keys())
    assert not missing, f"{name}: missing separation fields: {', '.join(missing)}"
    required_missing = sorted(expected_fields - required)
    assert not required_missing, f"{name}: required separation fields missing: {', '.join(required_missing)}"


def assert_strategic_model_fields(name: str, schema: dict) -> None:
    expected_fields = STRATEGIC_MODEL_FIELDS.get(name)
    if not expected_fields:
        return
    properties = schema["properties"]
    required = set(schema["required"])
    missing = sorted(expected_fields - properties.keys())
    assert not missing, f"{name}: missing strategic model fields: {', '.join(missing)}"
    required_missing = sorted(expected_fields - required)
    assert not required_missing, f"{name}: required strategic model fields missing: {', '.join(required_missing)}"


def main() -> int:
    for name, filename in SCHEMA_FILES.items():
        schema = load_schema(filename)
        assert_core_shape(name, schema)
        assert_identifier_contract(name, schema)
        assert_truth_fields(name, schema)
        assert_reference_separation(name, schema)
        assert_strategic_model_fields(name, schema)
    print("Schema contract checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

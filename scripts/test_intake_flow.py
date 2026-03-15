#!/usr/bin/env python3
"""Checks for the intake engine contracts."""

from __future__ import annotations

import json
from pathlib import Path

from intake import company_seed_record, intake_summary_markdown, normalize_intake_payload, research_profile_seed_record


ROOT = Path(__file__).resolve().parent.parent


def required_fields(schema_name: str) -> set[str]:
    path = ROOT / "schemas" / schema_name
    schema = json.loads(path.read_text(encoding="utf-8"))
    return set(schema["required"])


def main() -> int:
    session = normalize_intake_payload(
        {
            "company_name": "Acme MX",
            "intake_mode": "existing",
            "industry": "Professional services",
            "business_model": "Service business",
            "website": "https://example.mx",
            "seed_summary": "We help local businesses improve sales conversations.",
            "current_state_summary": "Revenue is inconsistent and positioning is weak.",
            "geography_focus": ["Monterrey, Nuevo Leon", "Mexico"],
            "available_sources": ["sales notes", "landing page"],
            "competitors": ["Competidor Uno", "Competidor Dos"],
            "known_constraints": ["Low marketing budget"],
        }
    )

    assert session["company_id"] == "acme-mx"
    assert session["intake_mode"] == "existing"
    assert session["currency_code"] == "MXN"

    company = company_seed_record(session)
    profile = research_profile_seed_record(session)

    assert required_fields("company.schema.json").issubset(company.keys())
    assert required_fields("research-profile.schema.json").issubset(profile.keys())
    assert company["business_mode"] == "existing"
    assert profile["research_stage"] == "seeded"

    summary = intake_summary_markdown(session)
    assert "Acme MX" in summary
    assert "Monterrey, Nuevo Leon" in summary
    assert "sales notes" in summary

    print("Intake flow checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

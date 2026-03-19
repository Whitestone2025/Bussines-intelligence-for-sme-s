#!/usr/bin/env python3
"""Checks that WSC findings stay specific to the site instead of collapsing into generic categories."""

from __future__ import annotations

from serve_ui import list_findings, refresh_company_knowledge


COMPANY_ID = "wsc-lat"


def main() -> int:
    refresh_company_knowledge(COMPANY_ID)
    findings = list_findings(company_id=COMPANY_ID)

    by_category = {}
    for finding in findings:
        by_category.setdefault(finding["category"], []).append(finding)

    service = by_category["service"][0]
    assert "ai lab" in service["statement"].lower()
    assert "venture capital hybrid" in service["statement"].lower()

    strategic_tension = by_category["strategic_tension"][0]
    assert "plataforma abierta de inteligencia" in strategic_tension["statement"].lower()
    assert "venture capital" in strategic_tension["statement"].lower()
    assert "cuña comercial dominante" in strategic_tension["statement"].lower()
    assert set(strategic_tension["evidence_refs"]) >= {
        "2026-03-18-wsc-positioning-hybrid",
        "2026-03-18-wsc-open-intel-platform",
        "2026-03-18-wsc-active-units",
    }

    offer_anchor = by_category["offer_anchor"][0]
    assert "1,500 usd" in offer_anchor["statement"].lower()
    assert "ai lab" in offer_anchor["statement"].lower()
    assert "portafolio" in offer_anchor["statement"].lower()

    proof_gap = by_category["proof_gap"][0]
    assert "80/20" in proof_gap["statement"]
    assert "no muestra prueba publica" in proof_gap["statement"].lower()

    statements = {item["statement"] for item in findings}
    assert "WhatsApp" not in statements, "WSC should not infer WhatsApp from homepage-only ambiguity."
    assert "Fundadores y duenos" not in statements, "WSC should not collapse to a fixed ICP from homepage-only ambiguity."

    print("WSC site-specificity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

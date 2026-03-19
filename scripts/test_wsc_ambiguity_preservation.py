#!/usr/bin/env python3
"""Checks that a homepage-only WSC-style case preserves ambiguity instead of collapsing to one crisp identity."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from serve_ui import ROOT, create_evidence, create_research_profile, create_source, list_findings, refresh_company_knowledge


COMPANY_ID = "wsc-webonly-ambiguity"
SOURCE_ID = "2026-03-18-ws-capital-homepage"


def cleanup() -> None:
    targets = [
        ROOT / "data" / "companies" / COMPANY_ID,
        ROOT / "data" / "research" / COMPANY_ID,
        ROOT / "data" / "sources" / COMPANY_ID,
        ROOT / "data" / "findings" / COMPANY_ID,
        ROOT / "data" / "validation" / COMPANY_ID,
        ROOT / "data" / "evidence" / COMPANY_ID,
        ROOT / "data" / "corpus" / "raw" / COMPANY_ID,
        ROOT / "data" / "corpus" / "clean" / COMPANY_ID,
        ROOT / "data" / "insights" / COMPANY_ID,
        ROOT / "data" / "experiments" / COMPANY_ID,
        ROOT / "data" / "patterns" / COMPANY_ID,
        ROOT / "data" / "reports" / COMPANY_ID,
    ]
    for target in targets:
        if target.exists():
            shutil.rmtree(target)
    index_path = ROOT / "data" / "corpus" / "index" / f"{COMPANY_ID}.tsv"
    if index_path.exists():
        index_path.unlink()


def seed_case() -> None:
    create_research_profile(
        {
            "company_name": "WS Capital Ambiguity",
            "company_id": COMPANY_ID,
            "website": "https://wsc.lat/",
            "seed_summary": "Firma que se presenta como AI Lab y Venture Capital Hybrid para Latinoamerica, con foco en infraestructura agentic e inteligencia abierta.",
            "available_sources": ["website"],
        }
    )
    create_source(
        {
            "company_id": COMPANY_ID,
            "source_id": SOURCE_ID,
            "source_kind": "website",
            "origin": "public_web",
            "title": "WS Capital homepage",
            "uri_or_path": "https://wsc.lat/",
            "body": "The AI Lab & Venture Capital Hybrid. 80% Agentic | 20% Human. McKinsey-Level Data for All. Open-source platform for research.",
        }
    )
    snippets = [
        ("2026-03-18-wsc-positioning-hybrid", "Posicionamiento visible", "La portada mezcla AI Lab, Venture Capital Hybrid e infraestructura.", ["The AI Lab & Venture Capital Hybrid."]),
        ("2026-03-18-wsc-agentic-ratio", "Modelo operativo", "El sitio declara 80% agentic y 20% human.", ["80% Agentic | 20% Human"]),
        ("2026-03-18-wsc-open-intel-platform", "Plataforma abierta", "Tambien promete McKinsey-Level Data for All mediante una plataforma abierta.", ["McKinsey-Level Data for All"]),
        ("2026-03-18-wsc-active-units", "Unidades activas", "Ademas muestra unidades activas que van desde asistentes de voz hasta redes agentic.", ["Voice Personal Assistants", "Agentic Networks"]),
        ("2026-03-18-wsc-problem-latam", "Problema regional", "Enmarca un retraso estructural en Latinoamerica y la necesidad de infraestructura.", ["Latin America remains underdeveloped."]),
        ("2026-03-18-wsc-ai-lab-offer", "Oferta visible", "La parte mas concreta es un AI Lab con precio y duracion publicados.", ["Lab Subscription: $1,500 USD/Mo | Duration: 6 Months"]),
    ]
    for entry_id, title, summary, quotes in snippets:
        create_evidence(
            {
                "company_id": COMPANY_ID,
                "entry_id": entry_id,
                "source_id": SOURCE_ID,
                "source_type": "website",
                "channel": "website",
                "date": "2026-03-18",
                "title": title,
                "evidence_type": "claim",
                "summary": summary,
                "quotes": quotes,
                "observations": ["Web publica solamente."],
                "source_origin": "public_web_capture",
                "confidence": 0.9,
                "status": "confirmed",
            }
        )


def main() -> int:
    cleanup()
    try:
        seed_case()
        refresh_company_knowledge(COMPANY_ID)

        findings = list_findings(company_id=COMPANY_ID)
        service = next(item for item in findings if item.get("category") == "service")
        assert "ai lab" in service["statement"].lower()
        assert "venture capital hybrid" in service["statement"].lower()
        assert "tentativa" in service.get("uncertainty_note", "").lower()

        icp_findings = [item for item in findings if item.get("category") == "icp"]
        assert not icp_findings, "Homepage-only ambiguity should not collapse into an ICP finding."

        channel_findings = [item for item in findings if item.get("category") == "channel"]
        assert not channel_findings, "Homepage-only ambiguity should not infer a working channel from website existence alone."

        profile = json.loads((ROOT / "data" / "research" / COMPANY_ID / "profile.json").read_text(encoding="utf-8"))
        assumptions_blob = "\n".join(profile.get("open_assumptions", []))
        assert "no confirma quien compra" in assumptions_blob.lower()
        assert "puede mezclar varias identidades" in assumptions_blob.lower()
        print("WSC ambiguity preservation checks passed.")
        return 0
    finally:
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main())

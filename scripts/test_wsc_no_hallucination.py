#!/usr/bin/env python3
"""Checks that a web-only WSC-style case does not get over-promoted into fake certainty."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from serve_ui import (
    ROOT,
    create_evidence,
    create_research_profile,
    create_source,
    list_findings,
    list_validation_questions,
    readiness_for_company,
    refresh_company_knowledge,
)


COMPANY_ID = "wsc-webonly-hallucination"
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
            "company_name": "WS Capital Web Only",
            "company_id": COMPANY_ID,
            "website": "https://wsc.lat/",
            "industry": "AI lab and venture capital hybrid",
            "seed_summary": "Firma que se presenta como AI Lab y Venture Capital Hybrid para Latinoamerica, con foco en infraestructura agentic e inteligencia abierta.",
            "primary_goal": "Entender con precision que negocio visible existe hoy y que sigue siendo ambiguo.",
            "available_sources": ["website"],
            "known_constraints": ["Solo se usa la web publica como fuente inicial."],
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
            "body": "The AI Lab & Venture Capital Hybrid. 80% Agentic | 20% Human. McKinsey-Level Data for All. Lab Subscription: $1,500 USD/Mo | Duration: 6 Months.",
            "tags": ["public-site", "homepage", "manifesto"],
        }
    )

    evidence_rows = [
        (
            "2026-03-18-wsc-positioning-hybrid",
            "Posicionamiento visible: AI Lab y Venture Capital Hybrid",
            "La portada presenta a WS Capital como una mezcla de AI Lab y Venture Capital Hybrid enfocada en construir herramientas, infraestructura e invertir en personas clave para escalar negocios en Latinoamerica.",
            [
                "The AI Lab & Venture Capital Hybrid.",
                "We are an AI Lab and a Venture Capital Hybrid. We build the tools, create the infrastructure, and then we invest in the key people to scale businesses in Latin America.",
            ],
        ),
        (
            "2026-03-18-wsc-problem-latam",
            "Tesis del problema regional y del rol operativo",
            "El sitio define el problema como un retraso estructural de Latinoamerica y presenta a WS Capital como el cerebro operativo que elimina ruido administrativo.",
            [
                "Latin America remains underdeveloped.",
                "We handle the noise—Legal, Accounting, Admin.",
            ],
        ),
        (
            "2026-03-18-wsc-agentic-ratio",
            "Modelo operativo 80% agentic y 20% human",
            "La web declara un modelo operativo 80% agentic y 20% human como parte de su forma de ejecucion.",
            ["80% Agentic | 20% Human"],
        ),
        (
            "2026-03-18-wsc-open-intel-platform",
            "Promesa de plataforma abierta de inteligencia",
            "La web promete McKinsey-Level Data for All y presenta una plataforma abierta para research.",
            ["McKinsey-Level Data for All"],
        ),
        (
            "2026-03-18-wsc-ai-lab-offer",
            "Oferta visible del AI Lab con capacidad y precio publicados",
            "La web muestra una oferta visible de AI Lab con precio publicado de 1,500 USD al mes por 6 meses y capacidad restringida.",
            [
                "Lab Subscription: $1,500 USD/Mo | Duration: 6 Months",
                "LAB CAPACITY (FULL MARCH): 0 / 2 (SOLD OUT)",
            ],
        ),
        (
            "2026-03-18-wsc-active-units",
            "Unidades activas y areas de inversion visibles",
            "La web muestra unidades activas que mezclan asistentes de voz, extensiones profesionales, redes agentic e inteligencia abierta.",
            ["Voice Personal Assistants", "Professional Extensions", "Agentic Networks"],
        ),
    ]

    for entry_id, title, summary, quotes in evidence_rows:
        create_evidence(
            {
                "company_id": COMPANY_ID,
                "entry_id": entry_id,
                "source_id": SOURCE_ID,
                "source_type": "website",
                "channel": "website",
                "date": "2026-03-18",
                "title": title,
                "evidence_type": "artifact",
                "summary": summary,
                "quotes": quotes,
                "observations": ["Fuente publica web-only."],
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

        services = list((ROOT / "data" / "companies" / COMPANY_ID / "services").glob("*.json"))
        icps = list((ROOT / "data" / "companies" / COMPANY_ID / "icps").glob("*.json"))
        channels = list((ROOT / "data" / "companies" / COMPANY_ID / "channels").glob("*.json"))
        if services:
            service_record = json.loads(services[0].read_text(encoding="utf-8"))
            assert service_record["status"] in {"inferred", "needs_validation"}
            assert service_record.get("unresolved_questions"), "Tentative web-only service records should keep unresolved questions."
        assert not icps, "Web-only case should not materialize an ICP from homepage-only evidence."
        assert not channels, "Web-only case should not materialize a priority channel from homepage presence alone."

        findings = list_findings(company_id=COMPANY_ID)
        service = next(item for item in findings if item.get("category") == "service")
        assert "tentativa" in service.get("uncertainty_note", "").lower()

        questions = list_validation_questions(company_id=COMPANY_ID, status="open")
        question_ids = {item["question_id"] for item in questions}
        assert "auto-service-clarify" in question_ids
        assert "auto-icp-clarify" in question_ids
        assert "auto-service-confirmation" not in question_ids
        assert "auto-icp-confirmation" not in question_ids

        readiness = readiness_for_company(COMPANY_ID)
        assert readiness["status"] == "not_ready"
        assert not readiness["service_defined"]
        assert not readiness["icp_defined"]
        assert not readiness["channel_defined"]
        print("WSC no-hallucination checks passed.")
        return 0
    finally:
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Checks that executive UI payloads expose structured reasoning for founders."""

from __future__ import annotations

import json
from pathlib import Path

from render_report import render_bundle
from serve_ui import build_decision_summary_payload


ROOT = Path(__file__).resolve().parent.parent


def decision_fixture() -> dict:
    return {
        "status": "inferred",
        "confidence": 0.81,
        "decision_summary": "Elegir la ruta de preventa con mayor credibilidad comercial",
        "recommended_action": "Entrar por alianzas con brokers premium con una oferta acotada de preventa visual para desarrolladoras boutique.",
        "why_now": "Esta ruta gana porque concentra aprendizaje en un canal con confianza prestada y reduce el riesgo de vender una solucion demasiado amplia demasiado pronto.",
        "fact_base": [
            "Tres entrevistas repiten que la friccion principal es vender preventa sin suficientes materiales visuales.",
            "Dos brokers confirmaron que una pieza visual concreta acelera la primera conversacion con inversionistas.",
        ],
        "assumptions": [
            "La red actual de brokers puede abrir suficientes conversaciones en 30 dias.",
            "La oferta acotada mantiene margen sin volverse commodity.",
        ],
        "key_risks": [
            "Los brokers pueden pedir prueba adicional antes de recomendar el servicio.",
        ],
        "validation_gaps": [
            "Falta confirmar que las desarrolladoras paguen por un paquete inicial y no solo por produccion suelta.",
        ],
        "next_steps": [
            "Definir la pieza inicial de preventa visual.",
            "Validar el guion con dos brokers aliados.",
        ],
        "strategic_stack": {
            "problem_statement": {
                "headline": "La desarrolladora necesita acelerar preventa sin inflar una estructura comercial todavia inmadura.",
                "situation": "El caso tiene producto visual defendible pero una ruta comercial aun dispersa.",
                "complication": "La confianza del comprador depende de prueba concreta y relaciones del ecosistema.",
                "decision_tension": "Escalar un canal frio hoy elevaria el riesgo antes de confirmar narrativa y precio.",
                "key_question": "Que ruta da aprendizaje y credibilidad mas rapido?",
            },
            "case_for_change": {
                "why_change": "La empresa ya no necesita mas ideas sueltas sino una apuesta clara de entrada.",
                "cost_of_inaction": "Seguir vendiendo de forma oportunista alarga el ciclo y deja la propuesta sin tesis comercial.",
                "transformation_story": "El cambio consiste en pasar de produccion suelta a solucion de preventa defendible.",
            },
            "what_must_be_true": [
                "Los brokers deben ver valor suficiente como para abrir conversaciones en menos de 30 dias.",
                "La oferta acotada debe percibirse como paso inicial hacia una venta mayor.",
            ],
        },
    }


def main() -> int:
    bundle = json.loads((ROOT / "data" / "tests" / "fixtures" / "deliverables" / "report-input.json").read_text(encoding="utf-8"))
    deliverables = render_bundle(bundle)
    assert "Memo Ejecutivo" in deliverables["executive-memo"]
    assert "## Para que sirve este documento" in deliverables["executive-memo"]
    assert "Memo de Problema Estructurado" in deliverables["problem-structuring-memo"]
    assert "## Para que sirve este documento" in deliverables["problem-structuring-memo"]
    assert "Memo de Opciones Estrategicas" in deliverables["strategic-options-memo"]
    assert "Documento de Decision" in deliverables["decision-document"]
    assert "Roadmap de Iniciativas" in deliverables["initiative-roadmap"]
    assert "Narrativa del Founder" in deliverables["founder-narrative"]
    assert "## Limites de evidencia hoy" in deliverables["executive-memo"]
    assert "## Limites de evidencia hoy" in deliverables["decision-document"]

    payload = build_decision_summary_payload(
        decision_fixture(),
        {
            "milestones": [
                {"timeframe": "Dias 1-30", "name": "Validar la ruta con brokers", "success_metric": "Dos conversaciones calificadas"}
            ]
        },
        [],
    )

    structuring = payload["problem_structuring"]
    assert "te dice" in payload["summary"].lower()
    assert structuring["headline"]
    assert structuring["facts"]
    assert structuring["assumptions"]
    assert structuring["recommendation"] == payload["memo"]["recommended_action"]
    assert structuring["what_must_be_true"]
    assert any("Por que cambiar:" in item for item in structuring["case_for_change"])
    assert any("Costo de no hacer nada:" in item for item in structuring["case_for_change"])

    print("Corporate deliverables quality checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

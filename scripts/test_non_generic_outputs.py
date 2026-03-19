#!/usr/bin/env python3
"""Checks that different business inputs do not collapse into the same messaging output."""

from __future__ import annotations

from customer_model import build_customer_outputs


def founder_payload() -> dict:
    return {
        "company_id": "generic-check-founder",
        "service_name": "Sprint de claridad comercial",
        "mechanism_hint": "un sprint donde se aclara que se entrega, como funciona y que prueba necesita ver el comprador",
        "evidence_items": [
            {
                "id": "e1",
                "source_id": "s1",
                "summary": "Fundadores quieren dejar de sonar genericos y necesitan explicar el servicio antes de pedir confianza.",
                "quotes": ["Necesito entender exactamente que hacen antes de confiar."],
                "observations": ["La confianza depende de explicar el proceso."],
                "candidate_pains": ["El servicio suena abstracto."],
                "candidate_outcomes": ["Mas claridad antes de vender."],
                "candidate_objections": ["Suena como cualquier agencia."],
                "trust_signals": ["Proceso visible"],
            }
        ],
    }


def ops_payload() -> dict:
    return {
        "company_id": "generic-check-ops",
        "service_name": "Validacion operativa de eventos",
        "mechanism_hint": "una revision de layout, flujo y riesgo operativo antes del evento",
        "evidence_items": [
            {
                "id": "e2",
                "source_id": "s2",
                "summary": "Equipos de operaciones quieren bajar riesgo de montaje y coordinar personal con menos improvisacion.",
                "quotes": ["Lo que necesito es validar flujo y montaje antes del evento."],
                "observations": ["La prioridad es reducir riesgo operativo."],
                "candidate_pains": ["Hay demasiada improvisacion en la entrega."],
                "candidate_outcomes": ["Menor riesgo durante el evento."],
                "candidate_objections": ["Temen agregar complejidad al proceso."],
                "trust_signals": ["Checklist operativo"],
            }
        ],
    }


def main() -> int:
    founder = build_customer_outputs(founder_payload())
    ops = build_customer_outputs(ops_payload())

    assert founder["icp"]["label"] != ops["icp"]["label"] or founder["offer"]["core_promise"] != ops["offer"]["core_promise"]
    assert founder["messaging"]["headline"] != ops["messaging"]["headline"], "Different cases should not share the same headline."
    assert "partner de crecimiento" not in founder["messaging"]["headline"].lower()
    assert "partner de crecimiento" not in ops["messaging"]["headline"].lower()

    print("Non-generic output checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

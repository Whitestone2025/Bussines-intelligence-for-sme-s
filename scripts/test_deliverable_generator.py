#!/usr/bin/env python3
"""Checks for deterministic deliverable generation."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from render_report import persist_bundle, render_bundle
from render_tables import render_tables


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    bundle = json.loads((ROOT / "data" / "tests" / "fixtures" / "deliverables" / "report-input.json").read_text(encoding="utf-8"))

    first = render_bundle(bundle)
    second = render_bundle(bundle)
    assert first == second, "Render output must be deterministic"
    for expected in (
        "executive-memo",
        "business-diagnosis",
        "problem-structuring-memo",
        "strategic-options-memo",
        "decision-document",
        "initiative-roadmap",
        "founder-narrative",
        "deck-outline",
        "risk-memo",
    ):
        assert expected in first, f"Expected deliverable: {expected}"
    assert "## Pregunta de decision" in first["executive-memo"], "Executive memo should frame the decision explicitly"
    assert "## Problema estructurado" in first["executive-memo"], "Executive memo should surface the problem structure"
    assert "## Hechos validados" in first["executive-memo"], "Executive memo should separate validated facts"
    assert "## Inferencias principales" in first["executive-memo"], "Executive memo should separate inferences"
    assert "## Supuestos de trabajo" in first["executive-memo"], "Executive memo should expose assumptions"
    assert "## Opciones consideradas" in first["executive-memo"], "Executive memo should compare options"
    assert "## Ruta provisional recomendada" in first["executive-memo"], "Executive memo should isolate the strategic route"
    assert "## Trazabilidad" in first["executive-memo"], "Executive memo should expose traceability"
    assert "Evidencia:" in first["executive-memo"], "Executive memo should include evidence references"
    assert "## Lo que sabemos" in first["business-diagnosis"], "Diagnosis should separate fact base"
    assert "## Lo que inferimos" in first["business-diagnosis"], "Diagnosis should separate inference"
    assert "## Supuestos de trabajo" in first["business-diagnosis"], "Diagnosis should expose assumptions explicitly"
    assert "## Lo que aun necesita validacion" in first["business-diagnosis"], "Diagnosis should show validation gaps"
    assert "## Recomendacion actual" in first["business-diagnosis"], "Diagnosis should separate recommendation"
    assert "## Realidades de ejecucion" in first["business-diagnosis"], "Diagnosis should stay implementation-aware"
    assert "## Pregunta que estamos resolviendo" in first["problem-structuring-memo"], "Problem structuring memo should anchor the core question"
    assert "## Tension de decision" in first["problem-structuring-memo"], "Problem structuring memo should expose the tension"
    assert "## Criterios de decision" in first["strategic-options-memo"], "Strategic options memo should expose criteria"
    assert "## Ruta recomendada" in first["strategic-options-memo"], "Strategic options memo should expose the chosen route"
    assert "## Decision central" in first["decision-document"], "Decision document should isolate the central decision"
    assert "## Condiciones de invalidez" in first["decision-document"], "Decision document should expose invalidation conditions"
    assert "## Objetivo del roadmap" in first["initiative-roadmap"], "Roadmap should expose its objective"
    assert "## Como explicar la ruta elegida" in first["founder-narrative"], "Founder narrative should help explain the route"
    assert "## Que no sobreprometer" in first["founder-narrative"], "Founder narrative should include restraint guidance"
    assert "Opciones consideradas" in first["deck-outline"], "Deck should include strategic options"
    assert "## Evidencia en contra y alertas" in first["risk-memo"], "Risk memo should include contrary evidence"
    assert "## Registro de riesgos" in first["risk-memo"], "Risk memo should include a risk register"
    for artifact in first.values():
        assert "Recommended" not in artifact
        assert "Alternative" not in artifact
        assert "Tradeoff" not in artifact

    tables = render_tables(bundle)
    assert "price_target" in tables["pricing-options.tsv"]
    assert "Sprint de claridad comercial primero" in tables["decision-options.tsv"]
    assert "Se asume" in tables["assumption-register.tsv"]
    assert "Dias 1-30" in tables["plan-milestones.tsv"]
    assert "Fundador" in tables["plan-milestones.tsv"]

    with TemporaryDirectory() as temp_dir:
        outputs = persist_bundle(Path(temp_dir), bundle["company"]["company_id"], bundle)
        assert all(path.exists() for path in outputs.values())

    print("Deliverable generator checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

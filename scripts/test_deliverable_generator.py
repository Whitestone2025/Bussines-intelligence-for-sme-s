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
    assert "## Pregunta de decision" in first["executive-memo"], "Executive memo should frame the decision explicitly"
    assert "## Tesis actual" in first["executive-memo"], "Executive memo should surface the current thesis"
    assert "## Supuestos clave" in first["executive-memo"], "Executive memo should expose assumptions"
    assert "## Opciones consideradas" in first["executive-memo"], "Executive memo should compare options"
    assert "2026-03-14-founder-clarity" in first["executive-memo"], "Traceability should include evidence refs"
    assert "## Lo que sabemos" in first["business-diagnosis"], "Diagnosis should separate fact base"
    assert "## Lo que inferimos" in first["business-diagnosis"], "Diagnosis should separate inference"
    assert "## Lo que aun necesita validacion" in first["business-diagnosis"], "Diagnosis should show validation gaps"
    assert "## Realidades de ejecucion" in first["business-diagnosis"], "Diagnosis should stay implementation-aware"
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

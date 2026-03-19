#!/usr/bin/env python3
"""Checks that the founder narrative is specific, restrained, and useful."""

from __future__ import annotations

import json
from pathlib import Path

from render_report import render_bundle


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    bundle = json.loads((ROOT / "data" / "tests" / "fixtures" / "deliverables" / "report-input.json").read_text(encoding="utf-8"))
    narrative = render_bundle(bundle)["founder-narrative"]

    assert "Sprint de claridad comercial" in narrative, "Founder narrative should mention the specific offer"
    assert "## Como explicar el problema" in narrative
    assert "## Como explicar la ruta elegida" in narrative
    assert "## Que decir en conversaciones" in narrative
    assert "## Que no sobreprometer" in narrative
    assert "## La siguiente conversacion correcta" in narrative
    assert "haz una landing" not in narrative.lower()
    assert "verdad final" in narrative.lower(), "Founder narrative should teach restraint"
    assert "escalar rapido" in narrative.lower(), "Founder narrative should frame tradeoffs, not hype"

    print("Founder narrative quality checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

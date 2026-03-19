#!/usr/bin/env python3
"""Checks that the public guide now references the real WSC validation case instead of the old composite demo."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMPANY_ID = "wsc-lat"


def main() -> int:
    company = json.loads((ROOT / "data" / "companies" / COMPANY_ID / "company.json").read_text(encoding="utf-8"))
    decision = json.loads((ROOT / "data" / "decisions" / COMPANY_ID / f"{COMPANY_ID}-viability-memo.json").read_text(encoding="utf-8"))
    guide = (ROOT / "docs" / "founder" / "wsbi-public-guide.md").read_text(encoding="utf-8").lower()

    assert company["name"] == "WS Capital"
    assert "ai lab and venture capital hybrid" in company["industry"].lower()
    assert "wsc.lat" in company["website"].lower()
    assert "80% agentic | 20% human".lower() in json.dumps(decision, ensure_ascii=False).lower()
    assert "mckinsey-level data for all".lower() in json.dumps(decision, ensure_ascii=False).lower()
    assert "ruta de cuña comercial ai lab".lower() in json.dumps(decision, ensure_ascii=False).lower()
    assert "ws capital" in guide
    assert "levantado solo desde informacion publica" in guide
    assert "wsc.lat" in guide
    assert "service clarity demo" not in guide
    assert "luma preventa studio" not in guide

    print("Public case specificity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

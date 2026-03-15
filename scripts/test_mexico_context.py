#!/usr/bin/env python3
"""Checks for Mexico-first context behavior."""

from __future__ import annotations

import json
from pathlib import Path

from mexico_context import apply_mexico_defaults, mexico_readiness_context, recommend_channels


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "mexico" / "context.json").read_text(encoding="utf-8"))

    defaults = apply_mexico_defaults(payload)
    assert defaults["currency_code"] == "MXN"
    assert defaults["geography"] == ["Mexico"]

    channels = recommend_channels(payload)
    assert "WhatsApp" in channels
    assert "Referrals" in channels

    readiness = mexico_readiness_context(payload)
    assert readiness["trust_signals"]
    assert readiness["operating_realities"]

    print("Mexico context checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

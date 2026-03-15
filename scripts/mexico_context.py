#!/usr/bin/env python3
"""Mexico-first context helpers for Codex Business OS MX."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REFERENCE_PATH = ROOT / "data" / "reference" / "mexico" / "channel-playbook.json"


def load_mexico_reference() -> dict:
    return json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))


def apply_mexico_defaults(payload: dict) -> dict:
    reference = load_mexico_reference()
    return {
        "currency_code": str(payload.get("currency_code", "")).strip() or reference["default_currency"],
        "geography": [str(item).strip() for item in payload.get("geography", []) if str(item).strip()] or [reference["default_geography"]],
    }


def recommend_channels(payload: dict) -> list[str]:
    reference = load_mexico_reference()
    business_tags = {str(item).strip().lower() for item in payload.get("business_tags", []) if str(item).strip()}
    if not business_tags:
        business_tags = {"service"}

    scored = []
    for channel in reference["channels"]:
        fit = {item.lower() for item in channel["fit_for"]}
        score = len(business_tags & fit)
        if score:
            scored.append((score, channel["name"]))
    scored.sort(key=lambda item: (-item[0], item[1]))
    names = [name for _, name in scored]
    return names or ["WhatsApp", "Referrals"]


def mexico_readiness_context(payload: dict) -> dict:
    reference = load_mexico_reference()
    defaults = apply_mexico_defaults(payload)
    channels = recommend_channels(payload)
    return {
        "currency_code": defaults["currency_code"],
        "geography": defaults["geography"],
        "recommended_channels": channels,
        "trust_signals": reference["trust_signals"],
        "operating_realities": reference["operating_realities"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Show Mexico-first defaults and recommended channels from a JSON payload.")
    parser.add_argument("input", help="JSON fixture path")
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    print(json.dumps(mexico_readiness_context(payload), indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

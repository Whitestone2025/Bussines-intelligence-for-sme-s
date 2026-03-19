#!/usr/bin/env python3
"""Checks that public outputs stay in Spanish and avoid leaked English defaults."""

from __future__ import annotations

import json
from pathlib import Path

from customer_model import build_customer_outputs
from decision_engine import build_decision_memo
from market_model import build_market_models


ROOT = Path(__file__).resolve().parent.parent
BANNED_PUBLIC_TERMS = [
    "launch the first",
    "partially_ready",
    "core offer",
    "clarity-first support",
    "focused pilot",
    "validation-first niche test",
    "what is the next best move",
    "traceability",
]


def assert_clean(text: str, label: str) -> None:
    lowered = text.lower()
    for term in BANNED_PUBLIC_TERMS:
        assert term not in lowered, f"{label} leaked banned public term: {term}"


def main() -> int:
    guide = (ROOT / "docs" / "founder" / "wsbi-public-guide.md").read_text(encoding="utf-8")
    reddit = (ROOT / "docs" / "founder" / "wsbi-reddit-post.md").read_text(encoding="utf-8")
    founder_frontend = (ROOT / "docs" / "founder" / "03-ver-tu-frontend.md").read_text(encoding="utf-8")
    assert_clean(guide, "guide")
    assert_clean(reddit, "reddit guide")
    assert_clean(founder_frontend, "founder frontend doc")

    customer_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "customer" / "customer-offer.json").read_text(encoding="utf-8"))
    decision_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "decisions" / "readiness.json").read_text(encoding="utf-8"))
    market_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "market" / "mexico-service.json").read_text(encoding="utf-8"))

    assert_clean(json.dumps(build_customer_outputs(customer_payload), ensure_ascii=False), "customer outputs")
    assert_clean(json.dumps(build_decision_memo(decision_payload), ensure_ascii=False), "decision memo")
    assert_clean(json.dumps(build_market_models(market_payload), ensure_ascii=False), "market outputs")

    print("Language purity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

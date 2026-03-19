#!/usr/bin/env python3
"""Checks for ICP, offer, and messaging intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from customer_model import build_customer_outputs, persist_customer_outputs


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "customer" / "customer-offer.json").read_text(encoding="utf-8"))
    outputs = build_customer_outputs(payload)

    icp = outputs["icp"]
    offer = outputs["offer"]
    messaging = outputs["messaging"]

    assert icp["label"], "ICP label should be inferred"
    assert icp["pains"], "Expected pains from evidence"
    assert icp["desired_outcomes"], "Expected outcomes from evidence"
    assert icp["common_objections"], "Expected objections from evidence"
    assert icp["trust_signals"], "Expected trust signals from evidence"

    assert offer["core_promise"], "Offer should have a core promise"
    assert offer["mechanism"], "Offer should have a mechanism"
    assert offer["proof_points"], "Offer should have proof points"

    assert messaging["headline"], "Messaging brief should have a headline"
    assert messaging["subheadline"], "Messaging brief should have a subheadline"
    forbidden = [phrase.lower() for phrase in messaging["forbidden_phrases"]]
    assert "partner de crecimiento" in forbidden
    whitespace = json.dumps(outputs, ensure_ascii=False).lower()
    assert "clarity-first" not in whitespace
    assert "growth partner" not in whitespace

    with TemporaryDirectory() as temp_dir:
        result = persist_customer_outputs(Path(temp_dir), payload)
        assert result["icp_path"].exists()
        assert result["offer_path"].exists()
        assert result["messaging_path"].exists()

    print("Customer offer engine checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

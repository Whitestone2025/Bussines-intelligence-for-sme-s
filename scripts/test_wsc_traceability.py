#!/usr/bin/env python3
"""Validates that the WSC web-only case is grounded on traceable homepage evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMPANY_PATH = ROOT / "data" / "companies" / "wsc-lat" / "company.json"
PROFILE_PATH = ROOT / "data" / "research" / "wsc-lat" / "profile.json"
SOURCE_PATH = ROOT / "data" / "sources" / "wsc-lat" / "2026-03-18-ws-capital-homepage.json"
EVIDENCE_DIR = ROOT / "data" / "evidence" / "wsc-lat"
INDEX_PATH = ROOT / "data" / "corpus" / "index" / "wsc-lat.tsv"

EXPECTED_EVIDENCE_IDS = {
    "2026-03-18-wsc-positioning-hybrid",
    "2026-03-18-wsc-problem-latam",
    "2026-03-18-wsc-agentic-ratio",
    "2026-03-18-wsc-open-intel-platform",
    "2026-03-18-wsc-ai-lab-offer",
    "2026-03-18-wsc-active-units",
}

EXPECTED_QUOTES = (
    "AI Lab & Venture Capital Hybrid",
    "80% Agentic | 20% Human",
    "McKinsey-Level Data for All",
    "Lab Subscription: $1,500 USD/Mo | Duration: 6 Months",
)


def load_json(path: Path) -> dict:
    assert path.exists(), f"Missing expected file: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    company = load_json(COMPANY_PATH)
    profile = load_json(PROFILE_PATH)
    source = load_json(SOURCE_PATH)

    assert company["company_id"] == "wsc-lat"
    assert company["name"] == "WS Capital"
    assert company["website"] == "https://wsc.lat/"
    assert set(company["evidence_refs"]) == EXPECTED_EVIDENCE_IDS

    assert profile["company_id"] == "wsc-lat"
    assert profile["available_sources"] == ["website"]
    assert profile["website"] == "https://wsc.lat/"

    assert source["source_id"] == "2026-03-18-ws-capital-homepage"
    assert source["source_kind"] == "website"
    assert source["uri_or_path"] == "https://wsc.lat/"
    assert "AI Lab & Venture Capital Hybrid" in source["title"]

    evidence_files = sorted(EVIDENCE_DIR.glob("*.json"))
    assert len(evidence_files) >= len(EXPECTED_EVIDENCE_IDS), "Expected at least the six homepage evidence entries."

    observed_ids: set[str] = set()
    combined_quotes: list[str] = []
    for path in evidence_files:
        entry = load_json(path)
        entry_id = entry["entry_id"]
        if entry_id not in EXPECTED_EVIDENCE_IDS:
            continue
        observed_ids.add(entry_id)
        assert entry["company_id"] == "wsc-lat"
        assert entry["source_id"] == "2026-03-18-ws-capital-homepage"
        assert "2026-03-18-ws-capital-homepage" in entry["source_refs"]
        assert entry["source_type"] == "website"
        assert entry["channel"] == "website"
        assert entry["summary"].strip(), f"{entry_id} should include a summary."
        assert entry["quotes"], f"{entry_id} should include quotes."
        combined_quotes.extend(entry["quotes"])

    assert observed_ids == EXPECTED_EVIDENCE_IDS, "WSC evidence set is incomplete or drifted unexpectedly."
    quote_blob = "\n".join(combined_quotes)
    for phrase in EXPECTED_QUOTES:
        assert phrase in quote_blob, f"Missing expected grounded phrase: {phrase}"

    index_text = INDEX_PATH.read_text(encoding="utf-8")
    for evidence_id in EXPECTED_EVIDENCE_IDS:
        assert evidence_id in index_text, f"Index is missing evidence entry: {evidence_id}"

    print("WSC traceability checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

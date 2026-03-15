#!/usr/bin/env python3
"""Competitive intelligence engine for Codex Business OS MX."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from workspace import WorkspaceLayout, slugify_id


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def build_competitor_records(payload: dict) -> list[dict]:
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")
    geography = [str(item).strip() for item in payload.get("geography", []) if str(item).strip()] or ["Mexico"]
    evidence_refs = [str(item).strip() for item in payload.get("evidence_refs", []) if str(item).strip()]
    source_refs = [str(item).strip() for item in payload.get("source_refs", []) if str(item).strip()]
    timestamp = now_iso()

    records = []
    for raw in payload.get("competitors", []):
        name = str(raw.get("name", "")).strip()
        if not name:
            continue
        competitor_id = f"{company_id}-{slugify_id(name)}"
        records.append(
            {
                "competitor_id": competitor_id,
                "company_id": company_id,
                "name": name,
                "website": str(raw.get("website", "")).strip(),
                "competitor_type": str(raw.get("competitor_type", "direct")).strip() or "direct",
                "geography": geography,
                "positioning_summary": str(raw.get("positioning_summary", "")).strip(),
                "pricing_summary": str(raw.get("pricing_summary", "")).strip(),
                "channels": [str(item).strip() for item in raw.get("channels", []) if str(item).strip()],
                "strengths": [str(item).strip() for item in raw.get("strengths", []) if str(item).strip()],
                "weaknesses": [str(item).strip() for item in raw.get("weaknesses", []) if str(item).strip()],
                "trust_signals": [str(item).strip() for item in raw.get("trust_signals", []) if str(item).strip()],
                "status": "inferred",
                "confidence": round(min(0.9, 0.5 + 0.05 * len(evidence_refs) + 0.03 * len(source_refs)), 2),
                "source_origin": "competitor_engine",
                "evidence_refs": evidence_refs,
                "source_refs": source_refs,
                "assumption_refs": [f"{competitor_id}-assumption-pricing" if not raw.get("website") else f"{competitor_id}-assumption-positioning"],
                "finding_refs": [],
                "validated_fact_refs": [],
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        )
    return records


def infer_whitespace(records: list[dict], target_whitespace: list[str]) -> list[str]:
    covered = set()
    for record in records:
        text = " ".join(
            [record.get("positioning_summary", ""), record.get("pricing_summary", "")]
            + record.get("strengths", [])
            + record.get("trust_signals", [])
        ).lower()
        for item in target_whitespace:
            if item.lower() in text:
                covered.add(item.lower())
    return [item for item in target_whitespace if item.lower() not in covered]


def persist_competitor_records(root: Path, payload: dict) -> dict:
    layout = WorkspaceLayout(root=root)
    company_id = str(payload.get("company_id", "")).strip()
    layout.ensure_company_workspace(company_id)

    records = build_competitor_records(payload)
    paths = []
    for record in records:
        path = layout.record_path("competitors", company_id, record["competitor_id"])
        layout.write_json_atomic(path, record)
        paths.append(path)

    whitespace = infer_whitespace(records, [str(item).strip() for item in payload.get("target_whitespace", []) if str(item).strip()])
    return {"paths": paths, "whitespace": whitespace}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build competitor records from a fixture or JSON payload.")
    parser.add_argument("input", help="JSON file with competitor assumptions")
    parser.add_argument("--root", default=".", help="Project root for persistence")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = persist_competitor_records(Path(args.root).resolve(), payload)
    for path in result["paths"]:
        print(path)
    if result["whitespace"]:
        print("whitespace:", ", ".join(result["whitespace"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

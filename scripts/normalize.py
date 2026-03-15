#!/usr/bin/env python3
"""Normalize raw evidence markdown files into clean JSON records."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


PAIN_CUES = ("problem", "pain", "struggle", "confus", "wast", "friction", "hard", "difficult", "unclear")
OUTCOME_CUES = ("want", "need", "result", "outcome", "clarity", "trust", "qualified", "predictable", "booked")
OBJECTION_CUES = ("don't", "do not", "skeptic", "agency", "expensive", "before", "trust", "worried", "risk")
TRUST_CUES = ("process", "proof", "transparent", "exact", "show", "real", "example", "before launch")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].strip().splitlines()
    meta: dict[str, object] = {}
    current_key: str | None = None
    for line in raw:
        if not line.strip():
            continue
        if line.lstrip().startswith("- ") and current_key:
            meta.setdefault(current_key, [])
            if isinstance(meta[current_key], list):
                meta[current_key].append(line.split("- ", 1)[1].strip())
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        meta[key] = value if value else []
    body = text[end + 5 :]
    return meta, body


def extract_section(body: str, heading: str) -> list[str]:
    targets = {f"# {heading}", f"## {heading}", f"### {heading}"}
    lines = body.splitlines()
    capture = False
    collected: list[str] = []
    for line in lines:
        if line.strip() in targets:
            capture = True
            continue
        if capture and re.match(r"^#{1,6}\s+", line):
            break
        if capture:
            stripped = line.strip()
            if stripped.startswith("- "):
                collected.append(stripped[2:].strip())
            elif stripped:
                collected.append(stripped)
    return collected


def infer_signal_lines(lines: list[str], cues: tuple[str, ...]) -> list[str]:
    matches = []
    seen = set()
    for line in lines:
        lower = line.lower()
        if any(cue in lower for cue in cues):
            normalized = line.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                matches.append(normalized)
    return matches[:5]


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def normalize_text(text: str, source: Path) -> dict:
    meta, body = parse_frontmatter(text)
    summary_lines = extract_section(body, "Summary")
    quotes = extract_section(body, "Verbatim Quotes")
    observations = extract_section(body, "Observations")
    signal_lines = summary_lines + quotes + observations
    entry_id = meta.get("entry_id", source.stem)
    created_at = str(meta.get("created_at", "")).strip() or now_iso()
    source_id = str(meta.get("source_id", "")).strip()
    record = {
        "entry_id": entry_id,
        "evidence_id": entry_id,
        "source_id": meta.get("source_id", ""),
        "company_id": meta.get("company_id", ""),
        "service_id": meta.get("service_id", ""),
        "icp_id": meta.get("icp_id", ""),
        "title": meta.get("title", ""),
        "evidence_type": meta.get("evidence_type", "artifact"),
        "source_type": meta.get("source_type", ""),
        "channel": meta.get("channel", ""),
        "date": meta.get("date", ""),
        "tags": meta.get("tags", []),
        "summary": "\n".join(summary_lines).strip(),
        "verbatim_quotes": quotes,
        "quotes": quotes,
        "observations": observations,
        "candidate_pains": infer_signal_lines(signal_lines, PAIN_CUES),
        "candidate_outcomes": infer_signal_lines(signal_lines, OUTCOME_CUES),
        "candidate_objections": infer_signal_lines(signal_lines, OBJECTION_CUES),
        "trust_signals": infer_signal_lines(signal_lines, TRUST_CUES),
        "status": meta.get("status", "inferred"),
        "confidence": float(meta.get("confidence", 0.55) or 0.55),
        "source_origin": meta.get("source_origin", "normalized_markdown"),
        "evidence_refs": [entry_id],
        "source_refs": [source_id] if source_id else [],
        "created_at": created_at,
        "updated_at": str(meta.get("updated_at", "")).strip() or created_at,
        "raw_path": str(source),
    }
    return record


def normalize_file(source: Path, dest: Path) -> str:
    text = source.read_text(encoding="utf-8")
    record = normalize_text(text, source)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(record, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return str(record["entry_id"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize raw evidence markdown files into JSON.")
    parser.add_argument("source", help="Source markdown file or directory")
    parser.add_argument("dest", help="Destination JSON file or directory")
    args = parser.parse_args()

    source = Path(args.source)
    dest = Path(args.dest)
    if source.is_file():
        normalize_file(source, dest)
        return 0

    dest.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(text)
        entry_id = meta.get("entry_id", path.stem)
        out = dest / f"{entry_id}.json"
        normalize_file(path, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

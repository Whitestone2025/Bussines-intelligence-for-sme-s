#!/usr/bin/env python3
"""Source and evidence ingestion pipeline helpers."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from normalize import normalize_file
from workspace import WorkspaceLayout, slugify_id


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def create_source_record(payload: dict, fetched_title: str = "", fetched_body: str = "") -> dict:
    title = fetched_title or str(payload.get("title", "")).strip()
    if not title:
        raise ValueError("title is required")
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")
    source_kind = str(payload.get("source_kind", "")).strip()
    if not source_kind:
        raise ValueError("source_kind is required")

    timestamp = now_iso()
    source_id = str(payload.get("source_id", "")).strip() or f"{date.today().isoformat()}-{slugify_id(title)}"
    body = str(payload.get("body", "")).strip() or fetched_body.strip()
    summary = " ".join((body or title).split())[:280].strip()
    return {
        "source_id": source_id,
        "company_id": company_id,
        "source_kind": source_kind,
        "origin": str(payload.get("origin", "user")).strip() or "user",
        "title": title,
        "uri_or_path": str(payload.get("uri_or_path", "")).strip(),
        "status": "processed" if body else "captured",
        "source_origin": str(payload.get("origin", "user")).strip() or "user",
        "source_refs": [source_id],
        "evidence_refs": [],
        "summary": summary,
        "body": body,
        "tags": [str(item).strip() for item in payload.get("tags", []) if str(item).strip()],
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def compose_evidence_markdown(payload: dict, entry_id: str) -> str:
    tags = [str(item).strip() for item in payload.get("tags", []) if str(item).strip()]
    quotes = [str(item).strip() for item in payload.get("quotes", []) if str(item).strip()]
    observations = [str(item).strip() for item in payload.get("observations", []) if str(item).strip()]
    summary = str(payload.get("summary", "")).strip()
    timestamp = str(payload.get("created_at", "")).strip() or now_iso()
    lines = [
        "---",
        f"entry_id: {entry_id}",
        f"source_id: {payload.get('source_id', '')}",
        f"company_id: {payload.get('company_id', '')}",
        f"service_id: {payload.get('service_id', '')}",
        f"icp_id: {payload.get('icp_id', '')}",
        f"title: {payload.get('title', '')}",
        f"evidence_type: {payload.get('evidence_type', 'artifact')}",
        f"source_type: {payload.get('source_type', '')}",
        f"channel: {payload.get('channel', '')}",
        f"date: {payload.get('date', date.today().isoformat())}",
        f"status: {payload.get('status', 'inferred')}",
        f"confidence: {payload.get('confidence', 0.55)}",
        f"source_origin: {payload.get('source_origin', 'user_input')}",
        f"created_at: {timestamp}",
        f"updated_at: {timestamp}",
        "tags:",
    ]
    for tag in tags:
        lines.append(f"  - {tag}")
    lines.extend(["---", "", "# Summary", "", summary, "", "# Verbatim Quotes", ""])
    for quote in quotes:
        lines.append(f'- "{quote}"')
    lines.extend(["", "# Observations", ""])
    for note in observations:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def ingest_evidence(root: Path, payload: dict) -> dict:
    layout = WorkspaceLayout(root=root)
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")
    layout.ensure_company_workspace(company_id)

    title_seed = str(payload.get("title", "") or str(payload.get("summary", ""))[:60]).strip()
    entry_id = str(payload.get("entry_id", "")).strip() or f"{payload.get('date', date.today().isoformat())}-{slugify_id(title_seed or 'evidence')}"
    raw_dir = root / "data" / "corpus" / "raw" / company_id
    clean_dir = root / "data" / "corpus" / "clean" / company_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    clean_dir.mkdir(parents=True, exist_ok=True)

    raw_path = raw_dir / f"{entry_id}.md"
    canonical_path = layout.record_path("evidence", company_id, entry_id)
    raw_path.write_text(compose_evidence_markdown(payload, entry_id), encoding="utf-8")
    normalize_file(raw_path, canonical_path)
    normalize_file(raw_path, clean_dir / f"{entry_id}.json")

    source_id = str(payload.get("source_id", "")).strip()
    if source_id:
        source_path = layout.record_path("sources", company_id, source_id)
        if source_path.exists():
            record = json.loads(source_path.read_text(encoding="utf-8"))
            refs = list(record.get("evidence_refs", []))
            if entry_id not in refs:
                refs.append(entry_id)
            record["evidence_refs"] = refs
            record["status"] = "normalized"
            record["updated_at"] = now_iso()
            layout.write_json_atomic(source_path, record)

    return {
        "entry_id": entry_id,
        "raw_path": rel(raw_path, root),
        "clean_path": rel(clean_dir / f"{entry_id}.json", root),
        "canonical_path": rel(canonical_path, root),
    }


__all__ = ["compose_evidence_markdown", "create_source_record", "ingest_evidence"]

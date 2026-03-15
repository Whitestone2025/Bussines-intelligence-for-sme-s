#!/usr/bin/env python3
"""Checks for source and evidence ingestion."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from evidence_ingest import create_source_record, ingest_evidence
from workspace import WorkspaceLayout


def main() -> int:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        layout = WorkspaceLayout(root=root)
        layout.ensure_company_workspace("acme-mx")

        source_payload = {
            "company_id": "acme-mx",
            "source_kind": "sales_notes",
            "title": "Founder interview notes",
            "origin": "user",
            "body": "Prospects say they want clarity before trusting an agency.",
            "tags": ["trust", "clarity"],
        }
        source_record = create_source_record(source_payload)
        source_path = layout.record_path("sources", "acme-mx", source_record["source_id"])
        layout.write_json_atomic(source_path, source_record)

        result = ingest_evidence(
            root,
            {
                "company_id": "acme-mx",
                "source_id": source_record["source_id"],
                "service_id": "service-clarity",
                "icp_id": "founders",
                "source_type": "sales_call",
                "evidence_type": "quote",
                "channel": "whatsapp",
                "date": "2026-03-14",
                "title": "Founder wants clarity before hype",
                "tags": ["trust", "objection"],
                "summary": "The buyer wants clarity before promises and worries about generic agency language.",
                "quotes": [
                    "I need to know exactly what gets done before I trust the process."
                ],
                "observations": [
                    "Specificity reduces skepticism.",
                    "Trust depends on visible process."
                ],
            },
        )

        canonical_path = root / result["canonical_path"]
        clean_path = root / result["clean_path"]
        raw_path = root / result["raw_path"]
        assert canonical_path.exists(), "Canonical evidence record was not written"
        assert clean_path.exists(), "Legacy clean evidence record was not written"
        assert raw_path.exists(), "Raw evidence markdown was not written"

        canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
        assert canonical["evidence_id"] == result["entry_id"]
        assert canonical["source_refs"] == [source_record["source_id"]]
        assert canonical["quotes"], "Normalized evidence should preserve quotes"
        assert canonical["candidate_objections"], "Expected objection signal extraction"
        assert canonical["trust_signals"], "Expected trust signal extraction"

        updated_source = json.loads(source_path.read_text(encoding="utf-8"))
        assert result["entry_id"] in updated_source["evidence_refs"], "Source asset should link back to evidence"
        assert updated_source["status"] == "normalized", "Source status should advance after evidence ingestion"

    print("Evidence ingestion checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

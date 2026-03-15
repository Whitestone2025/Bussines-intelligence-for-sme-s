#!/usr/bin/env python3
"""Build TSV indexes from clean corpus JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HEADER = ["entry_id", "date", "source_type", "channel", "service_id", "icp_id", "tags", "title"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build corpus TSV indexes.")
    parser.add_argument("clean_dir", help="Directory with clean JSON corpus entries")
    parser.add_argument("output", help="Output TSV path")
    args = parser.parse_args()

    clean_dir = Path(args.clean_dir)
    output = Path(args.output)
    rows = ["\t".join(HEADER)]
    for path in sorted(clean_dir.rglob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        title = record.get("title") or record.get("summary", "").splitlines()[0][:80]
        row = [
            str(record.get("entry_id", "")),
            str(record.get("date", "")),
            str(record.get("source_type", "")),
            str(record.get("channel", "")),
            str(record.get("service_id", "")),
            str(record.get("icp_id", "")),
            "|".join(record.get("tags", [])),
            title.replace("\t", " "),
        ]
        rows.append("\t".join(row))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

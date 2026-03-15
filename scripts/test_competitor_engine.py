#!/usr/bin/env python3
"""Checks for the competitive intelligence engine."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from competitors import build_competitor_records, infer_whitespace, persist_competitor_records


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "competitors" / "mexico-smb-services.json").read_text(encoding="utf-8"))
    records = build_competitor_records(payload)
    assert len(records) == 3, "Expected three competitor records"

    direct = [record for record in records if record["competitor_type"] == "direct"]
    assert len(direct) == 2
    assert all(record["pricing_summary"] for record in records)
    assert all(record["channels"] for record in records)

    whitespace = infer_whitespace(records, payload["target_whitespace"])
    assert "transparent delivery process" in whitespace
    assert "operator-led implementation" in whitespace

    with TemporaryDirectory() as temp_dir:
        result = persist_competitor_records(Path(temp_dir), payload)
        assert len(result["paths"]) == 3
        stored = json.loads(result["paths"][0].read_text(encoding="utf-8"))
        assert stored["competitor_id"]
        assert stored["company_id"] == payload["company_id"]

    print("Competitor engine checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Workspace foundation checks for Codex Business OS MX."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from workspace import DEFAULT_DOMAINS, WorkspaceLayout, slugify_id, validate_company_id


def main() -> int:
    assert slugify_id("Acme MX Launch") == "acme-mx-launch"

    try:
        validate_company_id("Acme MX")
    except ValueError:
        pass
    else:
        raise AssertionError("validate_company_id should reject non-slug-safe ids")

    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        layout = WorkspaceLayout(root=root)
        layout.ensure_workspace_roots()

        for domain in DEFAULT_DOMAINS:
            assert layout.domain_dir(domain).exists(), f"Missing domain directory: {domain}"

        company_id = "acme-mx"
        paths = layout.ensure_company_workspace(company_id)
        expected_keys = {
            "company_base",
            "services",
            "icps",
            "channels",
            "research",
            "sources",
            "evidence",
            "findings",
            "market",
            "competitors",
            "pricing",
            "financials",
            "decisions",
            "plans",
            "deliverables",
            "validation",
        }
        assert expected_keys == set(paths.keys()), "Canonical company path map is incomplete"
        for key, path in paths.items():
            assert path.exists(), f"Workspace path was not created for {key}: {path}"

        market_path = layout.record_path("market", company_id, "Market Overview")
        assert market_path == root / "data" / "market" / company_id / "market-overview.json"

        payload = {"market_model_id": "market-overview", "company_id": company_id}
        layout.write_json_atomic(market_path, payload)
        loaded = layout.load_json(market_path)
        assert loaded == payload, "Atomic write/load roundtrip failed"

        layout.write_json_atomic(market_path, {"market_model_id": "market-overview", "company_id": company_id, "version": 2})
        loaded_again = json.loads(market_path.read_text(encoding="utf-8"))
        assert loaded_again["version"] == 2, "Atomic overwrite did not preserve the latest payload"
        leftover_temp = list(market_path.parent.glob("tmp*"))
        assert not leftover_temp, "Atomic writes left temp files behind"

    print("Workspace foundation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Checks that founder reasoning stays traceable and non-generic."""

from __future__ import annotations

import shutil
from pathlib import Path

from serve_ui import (
    ROOT,
    create_research_profile,
    create_source,
    list_findings,
    list_validation_questions,
    refresh_company_knowledge,
)


COMPANIES = ("reasoning-sparse-lab", "reasoning-founder-lab", "reasoning-ops-lab")


def cleanup(company_id: str) -> None:
    targets = [
        ROOT / "data" / "companies" / company_id,
        ROOT / "data" / "research" / company_id,
        ROOT / "data" / "sources" / company_id,
        ROOT / "data" / "findings" / company_id,
        ROOT / "data" / "validation" / company_id,
        ROOT / "data" / "evidence" / company_id,
        ROOT / "data" / "corpus" / "raw" / company_id,
        ROOT / "data" / "corpus" / "clean" / company_id,
        ROOT / "data" / "insights" / company_id,
        ROOT / "data" / "experiments" / company_id,
        ROOT / "data" / "patterns" / company_id,
        ROOT / "data" / "reports" / company_id,
    ]
    for target in targets:
        if target.exists():
            shutil.rmtree(target)
    index_path = ROOT / "data" / "corpus" / "index" / f"{company_id}.tsv"
    if index_path.exists():
        index_path.unlink()


def assert_sparse_input_stays_cautious() -> None:
    company_id = COMPANIES[0]
    cleanup(company_id)
    create_research_profile(
        {
            "company_name": "Reasoning Sparse Lab",
            "company_id": company_id,
            "seed_summary": "We help businesses grow.",
            "workspace_mode": "in_place_business_folder",
            "existing_material_summary": "One vague note copied into the folder.",
            "existing_file_manifest": ["note.txt"],
            "available_sources": ["notes"],
        }
    )
    refresh_company_knowledge(company_id)

    icp_findings = [item for item in list_findings(company_id=company_id) if item.get("category") == "icp"]
    assert not icp_findings or max(item.get("confidence", 0) for item in icp_findings) < 0.7, "Sparse input should not over-assert an ICP"

    questions = list_validation_questions(company_id=company_id, status="open")
    assert any(item["question_id"] == "auto-icp-clarify" for item in questions), "Sparse input should trigger an ICP clarification question"
    cleanup(company_id)


def assert_distinct_companies_diverge() -> None:
    founder_id = COMPANIES[1]
    ops_id = COMPANIES[2]
    cleanup(founder_id)
    cleanup(ops_id)

    create_research_profile(
        {
            "company_name": "Reasoning Founder Lab",
            "company_id": founder_id,
            "seed_summary": "We help founder-led service firms explain what gets done before buyers are asked to trust the process.",
            "available_sources": ["sales notes"],
        }
    )
    create_source(
        {
            "company_id": founder_id,
            "source_kind": "sales_notes",
            "origin": "user",
            "title": "Founder friction",
            "body": "Founders say agencies sound generic. Owners want to see the process and know exactly what gets done before they trust the offer.",
        }
    )
    refresh_company_knowledge(founder_id)

    create_research_profile(
        {
            "company_name": "Reasoning Ops Lab",
            "company_id": ops_id,
            "seed_summary": "We help venue operations teams validate layouts, staff flow and technical delivery before large events.",
            "available_sources": ["ops notes"],
        }
    )
    create_source(
        {
            "company_id": ops_id,
            "source_kind": "ops_notes",
            "origin": "user",
            "title": "Operations friction",
            "body": "Operations leaders care about delivery process, staff coordination, venue validation and execution risk during the event window.",
        }
    )
    refresh_company_knowledge(ops_id)

    founder_icp = next(item for item in list_findings(company_id=founder_id) if item.get("category") == "icp")
    ops_icp = next(item for item in list_findings(company_id=ops_id) if item.get("category") == "icp")
    assert founder_icp["statement"] != ops_icp["statement"], "Different companies should not collapse into the same ICP finding"

    founder_pains = [item for item in list_findings(company_id=founder_id) if item.get("category") == "pain"]
    assert founder_pains and all(item.get("source_refs") or item.get("evidence_refs") for item in founder_pains), "Evidence-derived pains should remain traceable"

    cleanup(founder_id)
    cleanup(ops_id)


def main() -> int:
    assert_sparse_input_stays_cautious()
    assert_distinct_companies_diverge()
    print("Reasoning quality checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

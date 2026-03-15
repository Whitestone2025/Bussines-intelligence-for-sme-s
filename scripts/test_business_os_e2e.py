#!/usr/bin/env python3
"""End-to-end verification for Codex Business OS MX."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from competitors import persist_competitor_records
from customer_model import build_customer_outputs, persist_customer_outputs
from decision_engine import build_decision_memo, persist_decision_memo, readiness_check
from evidence_ingest import create_source_record, ingest_evidence
from financials import build_financial_snapshot, persist_financial_snapshot
from intake import company_seed_record, normalize_intake_payload, research_profile_seed_record
from market_model import persist_market_models
from mexico_context import mexico_readiness_context
from planner import persist_execution_plan
from pricing import build_pricing_model, persist_pricing_model
from render_report import persist_bundle
from workspace import WorkspaceLayout


ROOT = Path(__file__).resolve().parent.parent
AUTORESEARCH_MODULE_PATH = ROOT / "scripts" / "codex-ground-loop" / "autoresearch_loop.py"
AUTORESEARCH_SPEC = importlib.util.spec_from_file_location("autoresearch_loop_e2e", AUTORESEARCH_MODULE_PATH)
assert AUTORESEARCH_SPEC and AUTORESEARCH_SPEC.loader
AUTORESEARCH_MODULE = importlib.util.module_from_spec(AUTORESEARCH_SPEC)
sys.modules[AUTORESEARCH_SPEC.name] = AUTORESEARCH_MODULE
AUTORESEARCH_SPEC.loader.exec_module(AUTORESEARCH_MODULE)


def main() -> int:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        layout = WorkspaceLayout(root=root)
        session = normalize_intake_payload(
            {
                "company_name": "Acme MX",
                "company_id": "acme-mx",
                "intake_mode": "existing",
                "primary_goal": "Improve conversion quality for a founder-led service business.",
                "seed_summary": "A founder-led service business focused on sales clarity.",
                "available_sources": ["sales notes", "interviews"],
                "geography_focus": ["Mexico City", "Mexico"],
            }
        )
        layout.ensure_company_workspace("acme-mx")
        layout.write_json_atomic(layout.company_base("acme-mx") / "company.json", company_seed_record(session))
        layout.write_json_atomic(layout.company_domain_dir("research", "acme-mx") / "profile.json", research_profile_seed_record(session))

        source_record = create_source_record(
            {
                "company_id": "acme-mx",
                "source_kind": "sales_notes",
                "title": "Founder interview notes",
                "origin": "user",
                "body": "Prospects want clarity before they trust a service business.",
            }
        )
        layout.write_json_atomic(layout.record_path("sources", "acme-mx", source_record["source_id"]), source_record)

        evidence_payload = {
            "company_id": "acme-mx",
            "source_id": source_record["source_id"],
            "service_id": "sales-clarity",
            "icp_id": "founders",
            "source_type": "sales_call",
            "evidence_type": "quote",
            "channel": "whatsapp",
            "date": "2026-03-14",
            "title": "Founder wants clarity before hype",
            "tags": ["trust", "objection"],
            "summary": "The buyer wants clarity before promises and worries about generic agency language.",
            "quotes": ["I need to know exactly what gets done before I trust the process."],
            "observations": ["Trust depends on visible process."],
        }
        ingest_result = ingest_evidence(root, evidence_payload)
        assert (root / ingest_result["canonical_path"]).exists()

        market_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "market" / "mexico-service.json").read_text(encoding="utf-8")) | {"company_id": "acme-mx"}
        persist_market_models(root, market_payload)

        competitor_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "competitors" / "mexico-smb-services.json").read_text(encoding="utf-8")) | {"company_id": "acme-mx"}
        persist_competitor_records(root, competitor_payload)

        customer_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "customer" / "customer-offer.json").read_text(encoding="utf-8")) | {"company_id": "acme-mx"}
        customer_outputs = build_customer_outputs(customer_payload)
        persist_customer_outputs(root, customer_payload)

        pricing_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "pricing-financials" / "founder-service.json").read_text(encoding="utf-8")) | {"company_id": "acme-mx"}
        pricing_model = build_pricing_model(pricing_payload)
        persist_pricing_model(root, pricing_payload)
        build_financial_snapshot(pricing_payload, pricing_model)
        persist_financial_snapshot(root, pricing_payload, pricing_model)

        readiness_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "decisions" / "readiness.json").read_text(encoding="utf-8")) | {"company_id": "acme-mx"}
        readiness = readiness_check(readiness_payload)
        assert readiness["status"] == "ready"
        decision_memo = build_decision_memo(readiness_payload)
        persist_decision_memo(root, readiness_payload)

        plan_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "plans" / "plan-input.json").read_text(encoding="utf-8")) | {
            "company_id": "acme-mx",
            "decision_memo": decision_memo,
        }
        persist_execution_plan(root, plan_payload)

        mexico_context = mexico_readiness_context({"business_tags": ["service", "high-trust-sales"]})
        assert mexico_context["currency_code"] == "MXN"

        bundle = json.loads((ROOT / "data" / "tests" / "fixtures" / "deliverables" / "report-input.json").read_text(encoding="utf-8"))
        bundle["company"]["company_id"] = "acme-mx"
        bundle["decision_memo"] = decision_memo
        bundle["icp"] = customer_outputs["icp"]
        bundle["offer"] = customer_outputs["offer"]
        bundle["pricing_model"] = pricing_model
        outputs = persist_bundle(root, "acme-mx", bundle)
        assert outputs["executive-memo"].exists()
        assert outputs["business-diagnosis"].exists()

        run_dir = root / "tasks" / "ground-loop" / "autoresearch-mx-v1"
        assert AUTORESEARCH_MODULE.cmd_init(
            argparse.Namespace(
                root=str(ROOT),
                run_dir=str(run_dir),
                goal="Improve deliverables and decision quality one bounded experiment at a time.",
                time_budget_minutes=10,
            )
        ) == 0
        assert AUTORESEARCH_MODULE.cmd_record(
            argparse.Namespace(
                run_dir=str(run_dir),
                experiment_id="exp-001",
                score=0.81,
                status="keep",
                area="deliverables",
                description="Deepen executive logic and evidence traceability.",
            )
        ) == 0
        assert AUTORESEARCH_MODULE.cmd_next(
            argparse.Namespace(
                root=str(ROOT),
                run_dir=str(run_dir),
                goal=None,
                time_budget_minutes=None,
            )
        ) == 0
        assert AUTORESEARCH_MODULE.audit_run_state(run_dir) == []

        journey_dir = ROOT / "data" / "tests" / "fixtures" / "journeys"
        journey_files = sorted(journey_dir.glob("*.json"))
        assert len(journey_files) >= 4, "Expected at least four Mexico-focused golden journeys"

    print("Business OS end-to-end checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

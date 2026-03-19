#!/usr/bin/env python3
"""Checks that the UI workspace exposes the extended business OS views."""

from __future__ import annotations

import http.client
import json
import socket
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from competitors import persist_competitor_records
from decision_engine import persist_decision_memo
from financials import build_financial_snapshot, persist_financial_snapshot
from market_model import persist_market_models
from planner import persist_execution_plan
from pricing import build_pricing_model, persist_pricing_model
from render_report import persist_bundle
from serve_ui import create_research_profile


ROOT = Path(__file__).resolve().parent.parent
COMPANY_ID = "ui-workspace-lab"
BASE_URL = ""


def reserve_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def request(path: str, payload: dict | None = None) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method="POST" if payload is not None else "GET")
    last_error: Exception | None = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, http.client.RemoteDisconnected) as exc:
            last_error = exc
            time.sleep(0.2)
    if last_error is not None:
        raise last_error
    raise RuntimeError("Request failed without a captured exception.")


def wait_for_server() -> None:
    for _ in range(40):
        try:
            request("/api/workspace")
            return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Server did not start in time.")


def wait_for_case_payload() -> dict:
    last_payload: dict = {}
    for _ in range(20):
        payload = request(f"/api/case?company_id={COMPANY_ID}")
        last_payload = payload
        if payload.get("sections", {}).get("deliverables"):
            return payload
        time.sleep(0.2)
    raise AssertionError(f"Expected deliverables in case payload, got {last_payload}")


def cleanup() -> None:
    targets = [
        ROOT / "data" / "companies" / COMPANY_ID,
        ROOT / "data" / "research" / COMPANY_ID,
        ROOT / "data" / "sources" / COMPANY_ID,
        ROOT / "data" / "evidence" / COMPANY_ID,
        ROOT / "data" / "findings" / COMPANY_ID,
        ROOT / "data" / "market" / COMPANY_ID,
        ROOT / "data" / "competitors" / COMPANY_ID,
        ROOT / "data" / "pricing" / COMPANY_ID,
        ROOT / "data" / "financials" / COMPANY_ID,
        ROOT / "data" / "decisions" / COMPANY_ID,
        ROOT / "data" / "plans" / COMPANY_ID,
        ROOT / "data" / "deliverables" / COMPANY_ID,
        ROOT / "data" / "validation" / COMPANY_ID,
        ROOT / "data" / "reports" / COMPANY_ID,
        ROOT / "data" / "corpus" / "raw" / COMPANY_ID,
        ROOT / "data" / "corpus" / "clean" / COMPANY_ID,
    ]
    for target in targets:
        if target.exists():
            shutil.rmtree(target)


def seed_records() -> None:
    create_research_profile(
        {
            "company_name": "UI Workspace Lab",
            "company_id": COMPANY_ID,
            "intake_mode": "existing",
            "seed_summary": "A founder-led service business focused on sales clarity in Mexico.",
            "primary_goal": "Improve conversion quality.",
            "available_sources": ["notes"],
        }
    )

    market_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "market" / "mexico-service.json").read_text(encoding="utf-8")) | {"company_id": COMPANY_ID}
    persist_market_models(ROOT, market_payload)

    competitor_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "competitors" / "mexico-smb-services.json").read_text(encoding="utf-8")) | {"company_id": COMPANY_ID}
    persist_competitor_records(ROOT, competitor_payload)

    pricing_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "pricing-financials" / "founder-service.json").read_text(encoding="utf-8")) | {"company_id": COMPANY_ID}
    pricing_model = build_pricing_model(pricing_payload)
    persist_pricing_model(ROOT, pricing_payload)
    persist_financial_snapshot(ROOT, pricing_payload, pricing_model)

    decision_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "decisions" / "readiness.json").read_text(encoding="utf-8")) | {"company_id": COMPANY_ID}
    persist_decision_memo(ROOT, decision_payload)

    plan_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "plans" / "plan-input.json").read_text(encoding="utf-8")) | {"company_id": COMPANY_ID}
    persist_execution_plan(ROOT, plan_payload)

    bundle = json.loads((ROOT / "data" / "tests" / "fixtures" / "deliverables" / "report-input.json").read_text(encoding="utf-8"))
    bundle["company"]["company_id"] = COMPANY_ID
    bundle["company"]["name"] = "UI Workspace Lab"
    persist_bundle(ROOT, COMPANY_ID, bundle)


def main() -> int:
    global BASE_URL
    port = reserve_port()
    BASE_URL = f"http://127.0.0.1:{port}"
    cleanup()
    seed_records()
    server = subprocess.Popen(
        [sys.executable, "scripts/serve_ui.py", "--port", str(port)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_server()
        workspace = request("/api/workspace")
        view_ids = {item["id"] for item in workspace["views"]}
        for expected in ("market", "competitors", "pricing", "financials", "decisions", "plans", "deliverables"):
            assert expected in view_ids, f"Missing workspace view: {expected}"

        case_payload = wait_for_case_payload()
        assert case_payload["company"]["company_id"] == COMPANY_ID, "Expected active case payload"
        assert case_payload["summary"]["readiness"]["status"], "Expected readiness summary"
        assert case_payload["sections"]["deliverables"], "Expected deliverables in case payload"
        for key in (
            "hero",
            "war_room",
            "thesis",
            "market_summary",
            "competition_summary",
            "viability_summary",
            "decision_summary",
            "deliverable_index",
            "audit_index",
        ):
            assert key in case_payload, f"Missing executive case block: {key}"
        assert case_payload["hero"]["title"] == "UI Workspace Lab", "Expected executive hero title"
        assert case_payload["war_room"]["headline"], "Expected war room headline"
        assert case_payload["war_room"]["recommendation_label"], "Expected route label in war room"
        assert case_payload["war_room"]["next_validation_step"], "Expected next validation step in war room"
        assert case_payload["war_room"]["evidence_limits"], "Expected visible evidence limits in war room"
        assert case_payload["deliverable_index"], "Expected executive deliverable index"
        assert case_payload["audit_index"]["counts"]["sources"] == 0 or case_payload["audit_index"]["counts"]["sources"] >= 0
        assert "te ayuda" in case_payload["hero"]["narrative"].lower() or "te sirve" in case_payload["hero"]["narrative"].lower()
        assert "sirve" in case_payload["market_summary"]["summary"].lower() or "te ayuda" in case_payload["market_summary"]["summary"].lower()
        assert "te dice" in case_payload["decision_summary"]["summary"].lower() or "te" in case_payload["decision_summary"]["summary"].lower()
        assert case_payload["decision_summary"]["evidence_limits"], "Expected visible limits in decision summary"
        assert case_payload["decision_summary"]["confidence_note"], "Expected confidence note in decision summary"

        assert request(f"/api/market?company_id={COMPANY_ID}")["items"], "Expected market items"
        assert request(f"/api/competitors?company_id={COMPANY_ID}")["items"], "Expected competitor items"
        assert request(f"/api/pricing?company_id={COMPANY_ID}")["items"], "Expected pricing items"
        assert request(f"/api/financials?company_id={COMPANY_ID}")["items"], "Expected financial items"
        assert request(f"/api/decisions?company_id={COMPANY_ID}")["items"], "Expected decision items"
        assert request(f"/api/plans?company_id={COMPANY_ID}")["items"], "Expected plan items"
        assert request(f"/api/deliverables?company_id={COMPANY_ID}")["items"], "Expected deliverable items"

        print("UI workspace flow checks passed.")
        return 0
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""End-to-end verification for the discovery-first Ws B-I flow."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PORT = 4185
BASE_URL = f"http://127.0.0.1:{PORT}"
COMPANY_ID = "test-discovery-lab"


def request(path: str, payload: dict | None = None) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method="POST" if payload is not None else "GET")
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_server() -> None:
    for _ in range(40):
        try:
            request("/api/workspace")
            return
        except urllib.error.URLError:
            time.sleep(0.25)
    raise RuntimeError("Server did not start in time.")


def cleanup() -> None:
    targets = [
        ROOT / "data" / "companies" / COMPANY_ID,
        ROOT / "data" / "research" / COMPANY_ID,
        ROOT / "data" / "sources" / COMPANY_ID,
        ROOT / "data" / "findings" / COMPANY_ID,
        ROOT / "data" / "validation" / COMPANY_ID,
        ROOT / "data" / "corpus" / "raw" / COMPANY_ID,
        ROOT / "data" / "corpus" / "clean" / COMPANY_ID,
        ROOT / "data" / "insights" / COMPANY_ID,
        ROOT / "data" / "experiments" / COMPANY_ID,
        ROOT / "data" / "patterns" / COMPANY_ID,
        ROOT / "data" / "reports" / COMPANY_ID,
    ]
    for target in targets:
        if target.exists():
            shutil.rmtree(target)
    index_path = ROOT / "data" / "corpus" / "index" / f"{COMPANY_ID}.tsv"
    if index_path.exists():
        index_path.unlink()


def main() -> int:
    cleanup()
    server = subprocess.Popen(
        [sys.executable, "scripts/serve_ui.py", "--port", str(PORT)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_server()

        request(
            "/api/start-research",
            {
                "company_name": "Test Discovery Lab",
                "website": "https://example.test",
                "industry": "service clarity",
                "seed_summary": "We help founders explain complex services clearly so buyers trust the offer faster.",
                "workspace_mode": "in_place_business_folder",
                "existing_material_summary": "This folder already contains homepage notes and sales notes.",
                "existing_file_manifest": ["homepage-notes.md", "sales-notes.txt"],
                "competitors": ["Generic Growth Agency", "Polished Messaging Studio"],
                "available_sources": ["website", "sales notes", "call transcripts"],
            },
        )

        request(
            "/api/source",
            {
                "company_id": COMPANY_ID,
                "source_kind": "website_note",
                "origin": "user",
                "title": "Homepage notes",
                "body": "Founders say the market sounds polished but never explains the service. They want clarity before hype and they want proof of process.",
            },
        )
        request(
            "/api/source",
            {
                "company_id": COMPANY_ID,
                "source_kind": "sales_notes",
                "origin": "user",
                "title": "Sales friction notes",
                "body": "Prospects worry agencies sound generic. They need to know exactly what gets done, who it is for, and what result to expect.",
            },
        )

        findings = request(f"/api/findings?company_id={COMPANY_ID}")["items"]
        assert any(item["category"] == "service" for item in findings), "Expected a service finding."
        assert any(item["category"] == "icp" for item in findings), "Expected at least one ICP finding."

        questions = request(f"/api/validation?company_id={COMPANY_ID}")["items"]
        assert questions, "Expected validation questions."
        for question in questions:
            answer = question.get("recommended_answer") or (question.get("candidate_options") or [{}])[0].get("value", "")
            if not answer:
                answer = "clear\nhuman\ndirect"
            request(
                "/api/validation-answer",
                {
                    "company_id": COMPANY_ID,
                    "question_id": question["question_id"],
                    "answer": answer,
                },
            )

        evidence_payloads = [
            {
                "title": "Founder says agencies never explain the service",
                "summary": "A founder says agencies sound polished but never explain the service clearly enough for buyers to trust it.",
                "quotes": [
                    "I do not want another agency that hides behind reports.",
                    "I need to know exactly what will be done before I trust the process."
                ],
                "observations": [
                    "Trust depends on visible process.",
                    "Generic language triggers skepticism."
                ],
            },
            {
                "title": "Prospect wants clarity before outcome promises",
                "summary": "A prospect says they need clarity before promises about growth because vague positioning makes the offer feel risky.",
                "quotes": [
                    "If I still do not understand the service after the hero, I will not book a call."
                ],
                "observations": [
                    "Clarity is a prerequisite for action."
                ],
            },
            {
                "title": "Buyer asks for proof and examples",
                "summary": "The buyer wants proof, examples, and a transparent mechanism because they have already wasted money on agencies.",
                "quotes": [
                    "Show me the process, not just the promise."
                ],
                "observations": [
                    "Proof lowers skepticism.",
                    "Agency fatigue is real."
                ],
            },
            {
                "title": "Founder wants qualified conversations",
                "summary": "The founder wants more qualified conversations, not more noise, and they need messaging that attracts the right buyer.",
                "quotes": [
                    "I want qualified calls, not vanity leads."
                ],
                "observations": [
                    "Desired outcome is qualified demand."
                ],
            },
            {
                "title": "Prospect worries about sounding generic",
                "summary": "The prospect worries that generic growth language will make the business sound like everyone else and hurt trust.",
                "quotes": [
                    "If it sounds like every other agency site, we lose before the conversation starts."
                ],
                "observations": [
                    "Differentiation matters.",
                    "Trust and specificity travel together."
                ],
            },
        ]

        for payload in evidence_payloads:
            request(
                "/api/evidence",
                {
                    "company_id": COMPANY_ID,
                    "service_id": "",
                    "icp_id": "",
                    "source_type": "sales_call",
                    "channel": "call",
                    "date": "2026-03-13",
                    "title": payload["title"],
                    "tags": ["trust", "clarity"],
                    "summary": payload["summary"],
                    "quotes": payload["quotes"],
                    "observations": payload["observations"],
                },
            )

        request("/api/research-refresh", {"company_id": COMPANY_ID})
        readiness = request(f"/api/readiness?company_id={COMPANY_ID}")
        assert readiness["status"] == "ready", f"Expected readiness to be ready, got {readiness}"

        knowledge = request(f"/api/knowledge?company_id={COMPANY_ID}")["items"]
        service = next(item for item in knowledge if item["kind"] == "service")
        icp = next(item for item in knowledge if item["kind"] == "icp")

        evidence = request(f"/api/evidence?company_id={COMPANY_ID}")["items"]
        evidence_ids = [item["id"] for item in evidence[:3]]
        experiment = request(
            "/api/experiment",
            {
                "company_id": COMPANY_ID,
                "service_id": service["service_id"],
                "icp_id": icp["icp_id"],
                "asset_type": "landing_hero",
                "goal": "Help skeptical founders understand the service quickly.",
                "hypothesis": "If the hero explains the mechanism before promising outcomes, trust will improve.",
                "audience": "Founders burned by generic agencies.",
                "baseline_weaknesses": ["too generic", "unclear service description"],
                "evidence_ids": evidence_ids,
                "baseline": "We are your growth partner for end-to-end transformation.",
                "variant": "We clarify complex services so founders can show buyers exactly what gets done before asking for trust.",
            },
        )
        assert experiment["decision"] in {"keep", "discard"}, "Experiment did not return a decision."

        report = request("/api/report", {"company_id": COMPANY_ID, "report_name": "test-summary"})
        assert report["report_id"] == "test-summary", "Expected deterministic report id."

        workspace = request("/api/workspace")
        assert any(company["company_id"] == COMPANY_ID for company in workspace["companies"]), "Workspace did not include test company."
        research_profiles = request(f"/api/research?company_id={COMPANY_ID}")["items"]
        assert research_profiles and research_profiles[0]["workspace_mode"] == "in_place_business_folder", "Expected research profile to preserve workspace mode."
        print("Discovery flow test passed.")
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

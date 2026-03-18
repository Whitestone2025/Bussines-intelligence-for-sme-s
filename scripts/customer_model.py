#!/usr/bin/env python3
"""ICP, offer, and messaging intelligence for Codex Business OS MX."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from workspace import WorkspaceLayout, slugify_id


ICP_KEYWORDS = {
    "Founder-led service businesses": {"founder", "owner", "ceo", "principal"},
    "Marketing leads at SMBs": {"marketing", "brand", "growth", "demand"},
    "Sales-led operators": {"sales", "pipeline", "closer", "revenue"},
    "Operations-focused teams": {"operations", "ops", "delivery", "process"},
}

FORBIDDEN_PHRASES = {
    "growth partner",
    "end-to-end solution",
    "results-driven",
    "full-service",
    "scale to the next level",
}


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def unique_preserve(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        normalized = " ".join(str(item).split()).strip()
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        result.append(normalized)
    return result


def evidence_haystack(evidence_items: list[dict]) -> str:
    return " ".join(
        [
            str(item.get("summary", "")) + " " + " ".join(item.get("quotes", [])) + " " + " ".join(item.get("observations", []))
            for item in evidence_items
        ]
    ).lower()


def infer_icp_label(target_customer: str, evidence_items: list[dict]) -> tuple[str, int]:
    if target_customer.strip():
        return target_customer.strip(), 4
    haystack = evidence_haystack(evidence_items)
    scores = {}
    for label, keywords in ICP_KEYWORDS.items():
        scores[label] = sum(1 for keyword in keywords if keyword in haystack)
    best = max(scores.items(), key=lambda item: item[1])
    if best[1]:
        return best[0], best[1]
    return "Primary buyer still needs validation", 0


def top_phrases(values: list[str], limit: int = 3) -> list[str]:
    counter = Counter(unique_preserve(values))
    return [item for item, _ in counter.most_common(limit)]


def build_customer_outputs(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")

    evidence_items = payload.get("evidence_items", [])
    pains = top_phrases([item for evidence in evidence_items for item in evidence.get("candidate_pains", [])], 4)
    outcomes = top_phrases([item for evidence in evidence_items for item in evidence.get("candidate_outcomes", [])], 4)
    objections = top_phrases([item for evidence in evidence_items for item in evidence.get("candidate_objections", [])], 4)
    trust_signals = top_phrases([item for evidence in evidence_items for item in evidence.get("trust_signals", [])], 4)
    supporting_quotes = unique_preserve([quote for evidence in evidence_items for quote in evidence.get("quotes", [])])[:4]
    evidence_refs = unique_preserve([evidence.get("id") or evidence.get("evidence_id", "") for evidence in evidence_items])[:6]
    source_refs = unique_preserve([evidence.get("source_id", "") for evidence in evidence_items if evidence.get("source_id")])[:6]
    timestamp = now_iso()

    label, icp_signal_score = infer_icp_label(str(payload.get("target_customer", "")), evidence_items)
    icp_id = slugify_id(label)
    uncertain_icp = label == "Primary buyer still needs validation"
    confidence = round(min(0.92, 0.28 + 0.06 * len(evidence_refs) + 0.03 * len(source_refs) + 0.05 * icp_signal_score), 2)
    icp_status = "needs_validation" if uncertain_icp or confidence < 0.65 else "inferred"

    service_name = str(payload.get("service_name", "")).strip() or "Core Offer"
    core_outcome = outcomes[0] if outcomes else "buy with more confidence"
    main_pain = pains[0] if pains else "confusion about what gets done"
    mechanism = str(payload.get("mechanism_hint", "")).strip() or "a transparent process that explains exactly what gets done and why"

    icp_record = {
        "icp_id": icp_id,
        "company_id": company_id,
        "label": label,
        "pains": pains,
        "desired_outcomes": outcomes,
        "common_objections": objections,
        "trust_signals": trust_signals,
        "status": icp_status,
        "confidence": confidence,
        "source_origin": "customer_model_engine",
        "evidence_refs": evidence_refs,
        "source_refs": source_refs,
        "supporting_quotes": supporting_quotes,
        "unresolved_questions": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    offer_id = f"{company_id}-{slugify_id(service_name)}-offer"
    audience_phrase = label.lower() if not uncertain_icp else "the current buyer profile"
    offer_status = "needs_validation" if uncertain_icp else "inferred"

    offer_record = {
        "offer_id": offer_id,
        "company_id": company_id,
        "service_id": slugify_id(service_name),
        "name": service_name,
        "core_promise": f"Help {audience_phrase} avoid {main_pain.lower()} and reach {core_outcome.lower()}.",
        "mechanism": mechanism,
        "proof_points": trust_signals or ["clear process", "specific deliverables"],
        "anti_claims": sorted(FORBIDDEN_PHRASES),
        "status": offer_status,
        "confidence": confidence,
        "source_origin": "customer_model_engine",
        "evidence_refs": evidence_refs,
        "source_refs": source_refs,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    headline = (
        f"Clarity-first support for {label.lower()} who are tired of vague promises."
        if not uncertain_icp
        else "Clarity-first support built around the buyer signals we have so far."
    )
    subheadline = f"We use {mechanism} so buyers understand the work before they are asked to trust the result."
    messaging_record = {
        "brief_id": f"{offer_id}-messaging",
        "company_id": company_id,
        "offer_id": offer_id,
        "audience_label": label,
        "headline": headline,
        "subheadline": subheadline,
        "proof_points": trust_signals or ["Specific process", "Visible proof", "Human language"],
        "objection_handlers": objections or ["Explain what gets done before promising outcomes."],
        "forbidden_phrases": sorted(FORBIDDEN_PHRASES),
        "status": offer_status,
        "confidence": confidence,
        "source_origin": "customer_model_engine",
        "evidence_refs": evidence_refs,
        "source_refs": source_refs,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    return {"icp": icp_record, "offer": offer_record, "messaging": messaging_record}


def persist_customer_outputs(root: Path, payload: dict) -> dict:
    layout = WorkspaceLayout(root=root)
    company_id = str(payload.get("company_id", "")).strip()
    layout.ensure_company_workspace(company_id)
    outputs = build_customer_outputs(payload)

    icp_path = layout.root / "data" / "companies" / company_id / "icps" / f"{outputs['icp']['icp_id']}.json"
    icp_path.parent.mkdir(parents=True, exist_ok=True)
    layout.write_json_atomic(icp_path, outputs["icp"])

    offer_path = layout.record_path("research", company_id, outputs["offer"]["offer_id"])
    messaging_path = layout.record_path("research", company_id, outputs["messaging"]["brief_id"])
    layout.write_json_atomic(offer_path, outputs["offer"])
    layout.write_json_atomic(messaging_path, outputs["messaging"])
    return {"icp_path": icp_path, "offer_path": offer_path, "messaging_path": messaging_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build customer, offer, and messaging outputs from a JSON fixture.")
    parser.add_argument("input", help="JSON fixture path")
    parser.add_argument("--root", default=".", help="Project root for persistence")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = persist_customer_outputs(Path(args.root).resolve(), payload)
    for path in result.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Minimal intake engine for Codex Business OS MX."""

from __future__ import annotations

from datetime import datetime

from workspace import slugify_id


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def _normalize_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.splitlines() if item.strip()]
    return []


def _normalize_workspace_mode(payload: dict) -> str:
    explicit = str(payload.get("workspace_mode", "")).strip().lower()
    if explicit in {"clean_bootstrap", "in_place_business_folder"}:
        return explicit
    existing_material_summary = str(payload.get("existing_material_summary", "")).strip()
    existing_file_manifest = _normalize_list(payload.get("existing_file_manifest"))
    if payload.get("existing_business_material") or existing_material_summary or existing_file_manifest:
        return "in_place_business_folder"
    return "clean_bootstrap"


def normalize_intake_payload(payload: dict) -> dict:
    company_name = str(payload.get("company_name", "")).strip()
    if not company_name:
        raise ValueError("company_name is required")

    raw_mode = str(payload.get("intake_mode", "")).strip().lower()
    intake_mode = raw_mode if raw_mode in {"idea", "existing"} else "idea"
    company_id = slugify_id(str(payload.get("company_id") or company_name))
    timestamp = now_iso()
    workspace_mode = _normalize_workspace_mode(payload)
    geography_focus = _normalize_list(payload.get("geography_focus")) or ["Mexico"]
    available_sources = _normalize_list(payload.get("available_sources")) or ["notes"]
    competitors = _normalize_list(payload.get("competitors"))
    known_constraints = _normalize_list(payload.get("known_constraints"))
    existing_file_manifest = _normalize_list(payload.get("existing_file_manifest"))
    existing_material_summary = str(payload.get("existing_material_summary", "")).strip()

    primary_goal = str(payload.get("primary_goal", "")).strip()
    if not primary_goal:
        primary_goal = (
            "Validate whether this business idea is worth pursuing in Mexico."
            if intake_mode == "idea"
            else "Diagnose and improve the current business in Mexico."
        )

    session = {
        "session_id": f"{company_id}-intake",
        "company_id": company_id,
        "company_name": company_name,
        "intake_mode": intake_mode,
        "primary_goal": primary_goal,
        "industry": str(payload.get("industry", "")).strip(),
        "business_model": str(payload.get("business_model", "")).strip(),
        "website": str(payload.get("website", "")).strip(),
        "seed_summary": str(payload.get("seed_summary", "")).strip() or f"{company_name} business in Mexico.",
        "current_state_summary": str(payload.get("current_state_summary", "")).strip(),
        "geography_focus": geography_focus,
        "currency_code": str(payload.get("currency_code", "")).strip() or "MXN",
        "competitors": competitors,
        "available_sources": available_sources,
        "known_constraints": known_constraints,
        "workspace_mode": workspace_mode,
        "existing_material_summary": existing_material_summary,
        "existing_file_manifest": existing_file_manifest,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    return session


def intake_summary_markdown(session: dict) -> str:
    def render_list(items: list[str]) -> str:
        return ", ".join(items) if items else "[none provided]"

    return "\n".join(
        [
            "# Intake Summary",
            "",
            "## Company",
            f"- Name: {session['company_name']}",
            f"- Company ID: {session['company_id']}",
            f"- Mode: {session['intake_mode']}",
            f"- Geography: {render_list(session['geography_focus'])}",
            f"- Currency: {session['currency_code']}",
            "",
            "## Goal",
            "",
            session["primary_goal"],
            "",
            "## Business Context",
            f"- Industry: {session.get('industry') or '[not provided]'}",
            f"- Business model: {session.get('business_model') or '[not provided]'}",
            f"- Website: {session.get('website') or '[not provided]'}",
            f"- Seed summary: {session['seed_summary']}",
            f"- Current state: {session.get('current_state_summary') or '[not provided]'}",
            "",
            "## Evidence Inputs",
            f"- Competitors: {render_list(session['competitors'])}",
            f"- Available sources: {render_list(session['available_sources'])}",
            f"- Known constraints: {render_list(session['known_constraints'])}",
            f"- Workspace mode: {session.get('workspace_mode') or '[not provided]'}",
            f"- Existing files: {render_list(session.get('existing_file_manifest', []))}",
            f"- Existing material summary: {session.get('existing_material_summary') or '[not provided]'}",
            "",
        ]
    )


def company_seed_record(session: dict) -> dict:
    return {
        "company_id": session["company_id"],
        "name": session["company_name"],
        "business_mode": session["intake_mode"],
        "primary_country": "MX",
        "primary_region": session["geography_focus"][0] if session["geography_focus"] else "Mexico",
        "currency_code": session["currency_code"],
        "industry": session.get("industry", ""),
        "website": session.get("website", ""),
        "seed_summary": session["seed_summary"],
        "current_state_summary": session.get("current_state_summary", ""),
        "known_constraints": session.get("known_constraints", []),
        "tone_constraints": [],
        "forbidden_phrases": [],
        "status": "draft",
        "confidence": 0.35,
        "source_origin": "existing_folder_seed" if session.get("workspace_mode") == "in_place_business_folder" else "user_seed",
        "evidence_refs": [],
        "source_refs": [],
        "notes": session.get("existing_material_summary", ""),
        "created_at": session["created_at"],
        "updated_at": session["updated_at"],
    }


def research_profile_seed_record(session: dict) -> dict:
    return {
        "profile_id": session["session_id"],
        "company_id": session["company_id"],
        "intake_mode": session["intake_mode"],
        "seed_summary": session["seed_summary"],
        "primary_goal": session["primary_goal"],
        "website": session.get("website", ""),
        "geography_focus": session.get("geography_focus", []),
        "currency_code": session["currency_code"],
        "competitors": session.get("competitors", []),
        "available_sources": session.get("available_sources", []),
        "known_constraints": session.get("known_constraints", []),
        "workspace_mode": session.get("workspace_mode", "clean_bootstrap"),
        "existing_material_summary": session.get("existing_material_summary", ""),
        "existing_file_manifest": session.get("existing_file_manifest", []),
        "open_assumptions": [],
        "research_stage": "seeded",
        "status": "draft",
        "confidence": 0.35,
        "source_origin": "existing_folder_seed" if session.get("workspace_mode") == "in_place_business_folder" else "user_seed",
        "evidence_refs": [],
        "source_refs": [],
        "readiness_score": 0,
        "open_questions_count": 0,
        "next_step": "Inspect the existing business files first." if session.get("workspace_mode") == "in_place_business_folder" else "Add at least one source asset.",
        "created_at": session["created_at"],
        "updated_at": session["updated_at"],
    }


__all__ = [
    "company_seed_record",
    "intake_summary_markdown",
    "normalize_intake_payload",
    "research_profile_seed_record",
]

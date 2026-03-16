#!/usr/bin/env python3
"""Serve the Ws B-I UI and expose a local business-intelligence workspace API."""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import urllib.error
import urllib.request
from datetime import date, datetime
from html import unescape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from evidence_ingest import create_source_record, ingest_evidence
from evaluate import evaluate_messages
from intake import company_seed_record, intake_summary_markdown, normalize_intake_payload, research_profile_seed_record
from normalize import normalize_file

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
UI_DIR = ROOT / "ui"
RESEARCH_DIR = DATA_DIR / "research"
SOURCES_DIR = DATA_DIR / "sources"
FINDINGS_DIR = DATA_DIR / "findings"
VALIDATION_DIR = DATA_DIR / "validation"
TEXT_EXTENSIONS = {".md", ".json", ".txt", ".tsv", ".css", ".js", ".html"}

STATUS_VALUES = ["draft", "inferred", "needs_validation", "validated", "confirmed", "stale"]
READY_STATUSES = {"validated", "confirmed"}
QUESTION_LIMIT = 4

PAIN_CUES = ("problem", "pain", "struggle", "friction", "waste", "confus", "difficult", "hard", "slow", "unclear")
OUTCOME_CUES = ("want", "need", "result", "outcome", "clarity", "trust", "predictable", "qualified", "booked", "confidence")
OBJECTION_CUES = ("don't", "do not", "skeptic", "agency", "expensive", "risk", "worry", "trust", "before", "burned")
TRUST_CUES = ("proof", "process", "transparent", "exact", "real", "specific", "show", "before launch", "example")
GENERIC_MARKET_CUES = ("growth partner", "end-to-end solution", "scale to the next level", "results-driven", "full-service")

ICP_KEYWORDS = {
    "Founders And Owners": {"founder", "owner", "ceo", "principal"},
    "Marketing Leaders": {"marketing", "brand", "demand", "growth lead", "head of marketing"},
    "Sales Leaders": {"sales", "pipeline", "outbound", "closer", "revenue"},
    "Operations Leaders": {"operations", "delivery", "process", "ops", "fulfillment"},
}

CHANNEL_OPTIONS = [
    ("landing-page", "Landing Page"),
    ("email", "Email"),
    ("whatsapp", "WhatsApp"),
    ("sales-call", "Sales Call"),
]


def safe_path(raw_path: str) -> Path:
    candidate = (ROOT / raw_path).resolve()
    if not str(candidate).startswith(str(ROOT)):
        raise ValueError("Path escapes project root.")
    return candidate


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "untitled"


def load_json(path: Path, default: dict | list | None = None):
    default = default if default is not None else {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    meta_lines = text[4:end].strip().splitlines()
    body = text[end + 5 :]
    meta: dict[str, object] = {}
    current_key: str | None = None
    for line in meta_lines:
        if not line.strip():
            continue
        if line.lstrip().startswith("- ") and current_key:
            meta.setdefault(current_key, [])
            if isinstance(meta[current_key], list):
                meta[current_key].append(line.split("- ", 1)[1].strip())
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        meta[key] = value if value else []
    return meta, body


def extract_section_list(body: str, heading: str) -> list[str]:
    targets = {f"# {heading}", f"## {heading}", f"### {heading}"}
    lines = body.splitlines()
    found = False
    collected: list[str] = []
    for line in lines:
        if line.strip() in targets:
            found = True
            continue
        if found and re.match(r"^#{1,6}\s+", line):
            break
        if found:
            stripped = line.strip()
            if stripped.startswith("- "):
                collected.append(stripped[2:].strip())
            elif stripped:
                collected.append(stripped)
    return collected


def section_summary(path: Path) -> str:
    text = read_text(path)
    if not text:
        return ""
    meta, body = parse_frontmatter(text)
    if isinstance(meta.get("title"), str) and meta["title"]:
        return str(meta["title"])
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped[:180]
    return path.stem.replace("-", " ").replace("_", " ").title()


def first_sentence(text: str) -> str:
    text = " ".join(text.split())
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text)
    return parts[0][:220].strip()


def clean_excerpt(text: str) -> str:
    return " ".join(text.split())[:280].strip()


def split_candidate_lines(text: str) -> list[str]:
    chunks = []
    for line in re.split(r"[\n\r]+", text):
        for sentence in re.split(r"(?<=[.!?])\s+", line):
            stripped = " ".join(sentence.split()).strip(" -")
            if 18 <= len(stripped) <= 280:
                chunks.append(stripped)
    return chunks


def unique_preserve(items: list[str]) -> list[str]:
    seen = set()
    output = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized.lower() in seen:
            continue
        seen.add(normalized.lower())
        output.append(normalized)
    return output


def default_status_confidence(record: dict, fallback_status: str = "draft", fallback_confidence: float = 0.3) -> dict:
    if record.get("status") not in STATUS_VALUES:
        record["status"] = fallback_status
    try:
        record["confidence"] = float(record.get("confidence", fallback_confidence))
    except (TypeError, ValueError):
        record["confidence"] = fallback_confidence
    record.setdefault("evidence_refs", [])
    record.setdefault("source_origin", "system")
    return record


def company_base(company_id: str) -> Path:
    return DATA_DIR / "companies" / company_id


def research_profile_path(company_id: str) -> Path:
    return RESEARCH_DIR / company_id / "profile.json"


def source_dir(company_id: str) -> Path:
    return SOURCES_DIR / company_id


def findings_dir(company_id: str) -> Path:
    return FINDINGS_DIR / company_id


def validation_dir(company_id: str) -> Path:
    return VALIDATION_DIR / company_id


def ensure_company_structure(company_id: str) -> None:
    base = company_base(company_id)
    (base / "services").mkdir(parents=True, exist_ok=True)
    (base / "icps").mkdir(parents=True, exist_ok=True)
    (base / "channels").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "corpus" / "raw" / company_id).mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "corpus" / "clean" / company_id).mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "insights" / company_id).mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "experiments" / company_id).mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "patterns" / company_id).mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "reports" / company_id).mkdir(parents=True, exist_ok=True)
    research_profile_path(company_id).parent.mkdir(parents=True, exist_ok=True)
    source_dir(company_id).mkdir(parents=True, exist_ok=True)
    findings_dir(company_id).mkdir(parents=True, exist_ok=True)
    validation_dir(company_id).mkdir(parents=True, exist_ok=True)


def bootstrap_research_profile(company_id: str) -> dict:
    ensure_company_structure(company_id)
    path = research_profile_path(company_id)
    if path.exists():
        return load_json(path, {})
    company = load_json(company_base(company_id) / "company.json", {})
    services = sorted((company_base(company_id) / "services").glob("*.json"))
    seed_parts = [company.get("seed_summary", "")]
    if not seed_parts[0] and services:
        service = load_json(services[0], {})
        seed_parts = [service.get("one_sentence_description", ""), service.get("core_outcome", "")]
    seed_summary = next((part for part in seed_parts if part), f"{company.get('name', company_id)} service business.")
    now = now_iso()
    profile = {
        "profile_id": f"{company_id}-intake",
        "company_id": company_id,
        "intake_mode": company.get("business_mode", "existing"),
        "seed_summary": seed_summary,
        "primary_goal": "Diagnose and improve the current business in Mexico.",
        "website": company.get("website", ""),
        "geography_focus": [company.get("primary_region", "Mexico")],
        "currency_code": company.get("currency_code", "MXN"),
        "competitors": [],
        "available_sources": ["website", "notes"] if company.get("website") else ["notes"],
        "known_constraints": company.get("known_constraints", []),
        "open_assumptions": [],
        "research_stage": "seeded",
        "status": "draft",
        "confidence": float(company.get("confidence", 0.35) or 0.35),
        "source_origin": company.get("source_origin", "system"),
        "evidence_refs": list(company.get("evidence_refs", [])),
        "source_refs": list(company.get("source_refs", [])),
        "readiness_score": 0,
        "open_questions_count": 0,
        "next_step": "Add at least one source asset.",
        "created_at": now,
        "updated_at": now,
    }
    write_json(path, profile)
    return profile


def company_record(company_id: str) -> dict:
    ensure_company_structure(company_id)
    company = default_status_confidence(load_json(company_base(company_id) / "company.json", {"company_id": company_id, "name": company_id.replace("-", " ").title()}), "draft", 0.35)
    profile = bootstrap_research_profile(company_id)
    services = [default_status_confidence(load_json(path, {}) | {"path": rel(path)}, "draft", 0.4) for path in sorted((company_base(company_id) / "services").glob("*.json"))]
    icps = [default_status_confidence(load_json(path, {}) | {"path": rel(path)}, "draft", 0.4) for path in sorted((company_base(company_id) / "icps").glob("*.json"))]
    channels = [default_status_confidence(load_json(path, {}) | {"path": rel(path)}, "draft", 0.4) for path in sorted((company_base(company_id) / "channels").glob("*.json"))]
    readiness = readiness_for_company(company_id)
    return company | {
        "company_id": company.get("company_id", company_id),
        "path": rel(company_base(company_id) / "company.json"),
        "research_profile": profile,
        "services": services,
        "icps": icps,
        "channels": channels,
        "readiness": readiness,
    }


def list_companies() -> list[dict]:
    base = DATA_DIR / "companies"
    if not base.exists():
        return []
    items = []
    for path in sorted(base.iterdir()):
        if path.is_dir() and (path / "company.json").exists():
            items.append(company_record(path.name))
    return items


def list_research_profiles(company_id: str = "") -> list[dict]:
    items = []
    for company in list_companies():
        if company_id and company["company_id"] != company_id:
            continue
        profile = bootstrap_research_profile(company["company_id"])
        readiness = readiness_for_company(company["company_id"])
        items.append(
            profile
            | {
                "company_name": company.get("name", company["company_id"]),
                "company_path": company.get("path", ""),
                "readiness": readiness,
            }
        )
    return items


def filter_match(value: str, expected: str) -> bool:
    return not expected or value == expected


def list_sources(company_id: str = "", source_kind: str = "", status: str = "") -> list[dict]:
    items: list[dict] = []
    if not SOURCES_DIR.exists():
        return items
    for path in sorted(SOURCES_DIR.rglob("*.json")):
        record = load_json(path, {})
        if not filter_match(record.get("company_id", ""), company_id):
            continue
        if not filter_match(record.get("source_kind", ""), source_kind):
            continue
        if not filter_match(record.get("status", ""), status):
            continue
        items.append(record | {"path": rel(path)})
    return items


def list_evidence(
    company_id: str = "",
    service_id: str = "",
    icp_id: str = "",
    source_type: str = "",
    channel: str = "",
) -> list[dict]:
    clean_dir = DATA_DIR / "evidence" if (DATA_DIR / "evidence").exists() else DATA_DIR / "corpus" / "clean"
    items: list[dict] = []
    if not clean_dir.exists():
        return items
    for path in sorted(clean_dir.rglob("*.json")):
        record = load_json(path, {})
        if not filter_match(record.get("company_id", ""), company_id):
            continue
        if not filter_match(record.get("service_id", ""), service_id):
            continue
        if not filter_match(record.get("icp_id", ""), icp_id):
            continue
        record_source_type = record.get("source_type", record.get("evidence_type", ""))
        if not filter_match(record_source_type, source_type):
            continue
        if not filter_match(record.get("channel", ""), channel):
            continue
        title = record.get("title") or record.get("summary", "").splitlines()[0][:100] or record.get("entry_id", path.stem)
        items.append(
            {
                "id": record.get("evidence_id", record.get("entry_id", path.stem)),
                "title": title,
                "company_id": record.get("company_id", ""),
                "service_id": record.get("service_id", ""),
                "icp_id": record.get("icp_id", ""),
                "source_id": record.get("source_id", ""),
                "source_type": record_source_type,
                "evidence_type": record.get("evidence_type", "artifact"),
                "channel": record.get("channel", ""),
                "date": record.get("date", ""),
                "tags": record.get("tags", []),
                "summary": record.get("summary", ""),
                "quotes": record.get("quotes", record.get("verbatim_quotes", [])),
                "observations": record.get("observations", []),
                "candidate_pains": record.get("candidate_pains", []),
                "candidate_outcomes": record.get("candidate_outcomes", []),
                "candidate_objections": record.get("candidate_objections", []),
                "trust_signals": record.get("trust_signals", []),
                "raw_path": record.get("raw_path", ""),
                "clean_path": rel(path),
            }
        )
    return items


def list_insights(company_id: str = "", service_id: str = "") -> list[dict]:
    base = DATA_DIR / "insights"
    items: list[dict] = []
    if not base.exists():
        return items
    for path in sorted(base.rglob("*.md")):
        relative_parts = path.relative_to(base).parts
        current_company = relative_parts[0] if len(relative_parts) >= 1 else ""
        current_service = relative_parts[1] if len(relative_parts) >= 2 else ""
        if not filter_match(current_company, company_id):
            continue
        if not filter_match(current_service, service_id):
            continue
        text = read_text(path)
        pattern = "\n".join(extract_section_list(text, "Pattern")).strip()
        evidence_ids = extract_section_list(text, "Evidence")
        why = "\n".join(extract_section_list(text, "Why It Matters")).strip()
        items.append(
            {
                "id": path.stem,
                "title": path.stem.replace("-", " ").title(),
                "company_id": current_company,
                "service_id": current_service,
                "pattern": pattern,
                "evidence_ids": evidence_ids,
                "why_it_matters": why,
                "path": rel(path),
            }
        )
    return items


def list_findings(company_id: str = "", category: str = "", status: str = "") -> list[dict]:
    items: list[dict] = []
    if not FINDINGS_DIR.exists():
        return items
    for path in sorted(FINDINGS_DIR.rglob("*.json")):
        record = load_json(path, {})
        if not filter_match(record.get("company_id", ""), company_id):
            continue
        if not filter_match(record.get("category", ""), category):
            continue
        if not filter_match(record.get("status", ""), status):
            continue
        items.append(record | {"path": rel(path)})
    return items


def list_validation_questions(company_id: str = "", status: str = "") -> list[dict]:
    items: list[dict] = []
    if not VALIDATION_DIR.exists():
        return items
    for path in sorted(VALIDATION_DIR.rglob("*.json")):
        record = load_json(path, {})
        if not filter_match(record.get("company_id", ""), company_id):
            continue
        if not filter_match(record.get("status", ""), status):
            continue
        items.append(record | {"path": rel(path)})
    return items


def experiment_folder_records(company_id: str = "", service_id: str = "", icp_id: str = "") -> list[dict]:
    base = DATA_DIR / "experiments"
    items: list[dict] = []
    if not base.exists():
        return items
    for brief_path in sorted(base.rglob("brief.md")):
        folder = brief_path.parent
        meta, body = parse_frontmatter(read_text(brief_path))
        exp_company = str(meta.get("company_id", ""))
        exp_service = str(meta.get("service_id", ""))
        current_icp = str(meta.get("icp_id", ""))
        if not filter_match(exp_company, company_id):
            continue
        if not filter_match(exp_service, service_id):
            continue
        if not filter_match(current_icp, icp_id):
            continue
        evaluation_path = folder / "evaluation.json"
        evaluation = load_json(evaluation_path, {})
        items.append(
            {
                "id": str(meta.get("experiment_id", folder.name)),
                "title": str(meta.get("experiment_id", folder.name)).replace("-", " ").title(),
                "company_id": exp_company,
                "service_id": exp_service,
                "icp_id": current_icp,
                "asset_type": str(meta.get("asset_type", "")),
                "status": str(meta.get("status", evaluation.get("decision", "unknown"))),
                "goal": "\n".join(extract_section_list(body, "Goal")).strip(),
                "hypothesis": "\n".join(extract_section_list(body, "Hypothesis")).strip(),
                "audience": "\n".join(extract_section_list(body, "Audience")).strip(),
                "evidence_ids": extract_section_list(body, "Evidence Used"),
                "brief_path": rel(brief_path),
                "baseline_path": rel(folder / "baseline.md"),
                "variant_path": rel(folder / "variant-a.md"),
                "evaluation_path": rel(evaluation_path) if evaluation_path.exists() else "",
                "result_path": rel(folder / "result.md") if (folder / "result.md").exists() else "",
                "baseline_text": read_text(folder / "baseline.md"),
                "variant_text": read_text(folder / "variant-a.md"),
                "evaluation": evaluation,
                "result_text": read_text(folder / "result.md"),
                "folder_path": rel(folder),
            }
        )
    return items


def list_patterns(company_id: str = "") -> list[dict]:
    items: list[dict] = []
    base = DATA_DIR / "patterns"
    if not base.exists():
        return items
    for path in sorted(base.rglob("*.md")):
        current_company = path.relative_to(base).parts[0] if len(path.relative_to(base).parts) else ""
        if not filter_match(current_company, company_id):
            continue
        items.append(
            {
                "id": path.stem,
                "title": path.stem.replace("-", " ").replace("_", " ").title(),
                "company_id": current_company,
                "path": rel(path),
                "summary": section_summary(path),
                "content": read_text(path),
            }
        )
    return items


def list_reports(company_id: str = "") -> list[dict]:
    items: list[dict] = []
    base = DATA_DIR / "reports"
    if not base.exists():
        return items
    for path in sorted(base.rglob("*.md")):
        current_company = path.relative_to(base).parts[0] if len(path.relative_to(base).parts) else ""
        if not filter_match(current_company, company_id):
            continue
        items.append(
            {
                "id": path.stem,
                "title": path.stem.replace("-", " ").replace("_", " ").title(),
                "company_id": current_company,
                "path": rel(path),
                "summary": section_summary(path),
                "content": read_text(path),
            }
        )
    return items


def list_json_domain(domain: str, company_id: str = "") -> list[dict]:
    items: list[dict] = []
    base = DATA_DIR / domain
    if not base.exists():
        return items
    for path in sorted(base.rglob("*.json")):
        relative = path.relative_to(base).parts
        current_company = relative[0] if len(relative) else ""
        if company_id and current_company != company_id:
            continue
        record = load_json(path, {})
        title = (
            record.get("name")
            or record.get("label")
            or record.get("segment_name")
            or record.get("recommended_action")
            or record.get("objective")
            or path.stem.replace("-", " ").replace("_", " ").title()
        )
        summary = (
            record.get("positioning_summary")
            or record.get("decision_summary")
            or record.get("objective")
            or record.get("methodology_summary")
            or record.get("core_promise")
            or record.get("summary")
            or ""
        )
        items.append(
            {
                "id": record.get("market_model_id")
                or record.get("competitor_id")
                or record.get("pricing_model_id")
                or record.get("snapshot_id")
                or record.get("decision_id")
                or record.get("plan_id")
                or path.stem,
                "title": title,
                "company_id": record.get("company_id", current_company),
                "path": rel(path),
                "summary": summary,
                "record": record,
                **record,
            }
        )
    return items


def list_deliverables(company_id: str = "") -> list[dict]:
    items: list[dict] = []
    base = DATA_DIR / "deliverables"
    if not base.exists():
        return items
    for path in sorted(base.rglob("*.md")):
        current_company = path.relative_to(base).parts[0] if len(path.relative_to(base).parts) else ""
        if not filter_match(current_company, company_id):
            continue
        items.append(
            {
                "id": path.stem,
                "title": path.stem.replace("-", " ").replace("_", " ").title(),
                "company_id": current_company,
                "path": rel(path),
                "summary": section_summary(path),
                "content": read_text(path),
            }
        )
    return items


def list_research_records(company_id: str = "") -> list[dict]:
    items: list[dict] = []
    if not RESEARCH_DIR.exists():
        return items
    for path in sorted(RESEARCH_DIR.rglob("*.json")):
        if path.name == "profile.json":
            continue
        relative = path.relative_to(RESEARCH_DIR).parts
        current_company = relative[0] if len(relative) else ""
        if company_id and current_company != company_id:
            continue
        record = load_json(path, {})
        items.append(record | {"path": rel(path)})
    return items


def list_files() -> list[dict]:
    items: list[dict] = []
    skip_prefixes = {".git", "__pycache__"}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_EXTENSIONS:
            continue
        if any(part in skip_prefixes for part in path.parts):
            continue
        if "last-message.txt" in path.name:
            continue
        items.append(
            {
                "id": rel(path),
                "title": path.name,
                "path": rel(path),
                "summary": section_summary(path),
            }
        )
    return items


def build_context_options(companies: list[dict]) -> dict:
    services = []
    icps = []
    channels = []
    for company in companies:
        services.extend(company.get("services", []))
        icps.extend(company.get("icps", []))
        channels.extend(company.get("channels", []))
    return {"services": services, "icps": icps, "channels": channels}


def preferred_company_id() -> str:
    companies = list_companies()
    if not companies:
        return ""
    ids = {company["company_id"] for company in companies}
    if "the-preview" in ids:
        return "the-preview"
    ready = [company for company in companies if company.get("readiness", {}).get("status") == "ready"]
    if ready:
        return ready[0]["company_id"]
    return companies[0]["company_id"]


def choose_primary_record(items: list[dict]) -> dict:
    if not items:
        return {}
    return sorted(
        items,
        key=lambda item: (
            item.get("status") in READY_STATUSES,
            float(item.get("confidence", 0) or 0),
            item.get("updated_at", "") or item.get("created_at", ""),
        ),
        reverse=True,
    )[0]


def markdown_excerpt(text: str, limit: int = 360) -> str:
    cleaned = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        cleaned.append(stripped)
    return " ".join(cleaned)[:limit].strip()


def is_signal_noise(text: str, company_name: str = "") -> bool:
    lowered = text.strip().lower()
    if not lowered:
        return True
    if company_name and lowered.startswith(company_name.lower()):
        return True
    if lowered.startswith("the offer ") or lowered.startswith("our offer "):
        return True
    if lowered.startswith("the main outcome is"):
        return True
    if "helps planners" in lowered or "helps founders" in lowered:
        return True
    if len(lowered.split()) > 20:
        return True
    return False


def curated_then_supporting(
    primary_items: list[str],
    supporting_items: list[str],
    limit: int,
    company_name: str = "",
    curated_floor: int = 4,
) -> list[str]:
    curated = unique_preserve(primary_items)
    if len(curated) >= min(limit, curated_floor):
        return curated[:limit]

    filtered_supporting = [
        item
        for item in supporting_items
        if item
        and item.strip()
        and not is_signal_noise(item, company_name=company_name)
        and item.strip().lower() not in {value.lower() for value in curated}
    ]
    return unique_preserve(curated + filtered_supporting)[:limit]


def build_signal_board(company: dict, evidence_items: list[dict]) -> dict:
    icps = company.get("icps", [])
    primary_icp = choose_primary_record(icps)
    company_name = company.get("name", "")
    pains = curated_then_supporting(
        primary_icp.get("pains", []),
        [item for evidence in evidence_items for item in evidence.get("candidate_pains", [])],
        6,
        company_name=company_name,
        curated_floor=4,
    )
    outcomes = curated_then_supporting(
        primary_icp.get("desired_outcomes", []),
        [item for evidence in evidence_items for item in evidence.get("candidate_outcomes", [])],
        6,
        company_name=company_name,
        curated_floor=4,
    )
    objections = curated_then_supporting(
        primary_icp.get("common_objections", []),
        [item for evidence in evidence_items for item in evidence.get("candidate_objections", [])],
        6,
        company_name=company_name,
        curated_floor=4,
    )
    trust = curated_then_supporting(
        primary_icp.get("trust_signals", []),
        [item for evidence in evidence_items for item in evidence.get("trust_signals", [])],
        6,
        company_name=company_name,
        curated_floor=4,
    )
    quotes = unique_preserve([quote for evidence in evidence_items for quote in evidence.get("quotes", [])])[:6]
    return {
        "pains": pains,
        "outcomes": outcomes,
        "objections": objections,
        "trust_signals": trust,
        "quotes": quotes,
    }


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def currency_display(value: object, currency_code: str = "MXN") -> str:
    amount = safe_float(value, 0.0)
    if amount <= 0:
        return "Sin dato"
    return f"{currency_code} {amount:,.0f}"


def localized_deliverable_title(item_id: str, fallback: str) -> str:
    mapping = {
        "executive-memo": "Memo Ejecutivo",
        "business-diagnosis": "Diagnostico de Negocio",
        "deck-outline": "Estructura de Presentacion",
        "risk-memo": "Memo de Riesgos",
    }
    return mapping.get(item_id, fallback)


def translate_preview_text(text: str) -> str:
    if not text:
        return text
    translations = {
        "Wedding planners and event designers with premium visual events in Guadalajara and CDMX": "Wedding planners y disenadores de eventos con proyectos premium y altamente visuales en Guadalajara y CDMX",
        "Blended market model using top-down demand assumptions and bottom-up reachable-customer heuristics.": "Modelo de mercado combinado usando supuestos top-down de demanda y heuristicas bottom-up sobre clientes alcanzables.",
        "Attractiveness score balances competitive pressure, urgency of the problem, budget fit, and channel accessibility.": "El score de atractivo balancea presion competitiva, urgencia del problema, encaje de presupuesto y facilidad de acceso al canal.",
        "Annual price per customer assumed at MXN 42,000.00.": "Se asume un ingreso anual por cliente de MXN 42,000.",
        "Target customer ratio set at 18% of the total addressable customer base.": "Se asume que el 18% del mercado total direccionable entra al segmento objetivo.",
        "Serviceable customer ratio set at 35% of target customers.": "Se asume que el 35% del segmento objetivo es realmente atendible.",
        "Obtainable customer ratio set at 8% of serviceable customers.": "Se asume que el 8% del segmento atendible es capturable en el corto plazo.",
        "Bottom-up model uses 140 reachable customers and 12% expected close rate.": "El modelo bottom-up usa 140 clientes alcanzables y una tasa de cierre esperada de 12%.",
        "Competition intensity scored at 6.0/10.": "La intensidad competitiva se estima en 6.0/10.",
        "Urgency scored at 7.0/10, budget fit at 5.0/10, and channel access at 7.0/10.": "La urgencia se estima en 7.0/10, el encaje de presupuesto en 5.0/10 y el acceso al canal en 7.0/10.",
        "An existing render provider already embedded in the planner workflow.": "Un proveedor de renders ya integrado en el flujo del planner.",
        "Usually invisible to the buyer because it is already absorbed or embedded in the project process.": "Normalmente es invisible para el comprador porque ya esta absorbido o integrado al proceso del proyecto.",
        "Existing trust": "Confianza existente",
        "No switching friction": "No hay friccion por cambio de proveedor",
        "The differentiator may be weak or undocumented": "El diferenciador puede ser debil o poco documentado",
        "Not always tied to technical venue validation": "No siempre esta ligado a una validacion tecnica real del venue",
        "Existing relationship": "Relacion previa con el planner",
        "A planner that sells with moodboards and references only.": "Un planner que vende con moodboards y referencias sin validacion tecnica.",
        "Looks good early but leaves execution ambiguity.": "Se ve bien al inicio, pero deja ambiguedad operativa.",
        "Low cost and low friction": "Bajo costo y poca friccion",
        "Low cost": "Bajo costo",
        "Familiar process": "Proceso familiar",
        "No new vendor needed": "No requiere integrar un proveedor nuevo",
        "Familiar to clients": "Formato familiar para el cliente",
        "Weak operational certainty": "Poca certeza operativa",
        "Not enough for highly visual or premium clients": "No alcanza para clientes premium o altamente visuales",
        "Luxury planner with renders already integrated into the full service.": "Planner luxury que ya integra renders dentro de su servicio completo.",
        "Renders are part of a broader premium package.": "Los renders ya vienen integrados en un paquete premium mas amplio.",
        "Strong brand and trust": "Marca fuerte y mayor confianza inicial",
        "Premium clients expect this level": "El cliente premium ya espera este nivel",
        "Not focused on replacing a standalone visualization specialist": "No esta enfocado en sustituir a un especialista dedicado en visualizacion",
        "Higher total service cost": "Costo total mas alto",
        "The planner uses moodboards, references, and imagination instead of technical event visualization.": "El planner vende con moodboards, referencias e imaginacion en lugar de visualizacion tecnica del evento.",
        "Looks cheaper because there is no visible specialist fee.": "Parece mas barato porque no existe un fee visible de especialista.",
        "Leaves doubt unresolved": "Deja dudas sin resolver",
        "Does not validate real dimensions or execution fit": "No valida dimensiones reales ni la ejecucion final",
        "A higher-tier planner who already includes renders inside a premium full-service package.": "Un planner de mayor nivel que ya incluye renders dentro de un servicio premium integral.",
        "The render cost is hidden inside a broader luxury planning fee.": "El costo del render queda oculto dentro de un fee de planeacion luxury mas amplio.",
        "High-end positioning": "Posicionamiento high-end",
        "Integrated process": "Proceso integrado",
        "Not available to planners who need an external specialist partner": "No sirve para planners que necesitan un especialista externo como socio",
        "Less relevant to the mid-premium planner": "Es menos relevante para el planner mid-premium",
        "Brand reputation": "Reputacion de marca",
        "Portfolio": "Portafolio",
        "Useful for a contained scope where the planner needs enough certainty to present and validate one key setup.": "Sirve para un alcance acotado donde el planner necesita suficiente certeza para presentar y validar un montaje clave.",
        "Best fit for a primary salon or event area that needs a credible premium presentation and technical validation.": "Encaja mejor en un salon principal o area del evento que necesita una presentacion premium creible y validacion tecnica.",
        "Best fit for connected areas, deeper detail, and planners serving more demanding or premium clients.": "Encaja mejor cuando hay areas conectadas, mayor detalle y planners con clientes mas exigentes o premium.",
        "Commercial anchors come from one project quote and the public packages page.": "Los anclajes comerciales salen de una cotizacion real y de la pagina publica de paquetes.",
        "Internal delivery cost is still assumption-driven and not yet validated with operating data.": "El costo interno de entrega sigue siendo un supuesto y todavia no esta validado con datos operativos.",
        "The strongest pricing question is when the planner can transfer the cost to the final client.": "La pregunta mas fuerte de pricing es cuando el planner puede trasladar este costo al cliente final.",
        "The service appears most defensible in visual or premium projects, not in every event.": "El servicio parece mas defendible en proyectos visuales o premium, no en cualquier evento.",
    }
    translated = translations.get(text, text)
    replacements = (
        ("Core promise:", "Promesa central:"),
        ("Implicit objection:", "Objecion implicita:"),
        ("Lazaro stayed because execution quality held in real production", "Lazaro se quedo porque la calidad de ejecucion si sostuvo el resultado en produccion real"),
        ("see the event before montaje", "ver el evento antes del montaje"),
        ("who pays for this", "quien paga esto"),
        ("Audit", "Trazabilidad"),
    )
    for source, target in replacements:
        translated = translated.replace(source, target)
    return translated


def translate_preview_list(items: list[str]) -> list[str]:
    return [translate_preview_text(item) for item in items]


def block_payload(
    status: str,
    confidence: float,
    headline: str,
    summary: str,
    highlights: list[str],
    **extra: object,
) -> dict:
    return {
        "status": status or "draft",
        "confidence": round(safe_float(confidence, 0.0), 2),
        "headline": headline.strip() if headline else "Sin titular",
        "summary": summary.strip() if summary else "Sin resumen",
        "highlights": unique_preserve([item for item in highlights if item])[:6],
        **extra,
    }


def collect_reference_cards(
    refs: list[str],
    evidence_lookup: dict[str, dict],
    source_lookup: dict[str, dict],
    limit: int = 6,
) -> list[dict]:
    cards: list[dict] = []
    for ref in refs:
        if ref in evidence_lookup:
            evidence = evidence_lookup[ref]
            cards.append(
                {
                    "id": ref,
                    "kind": "evidence",
                    "title": translate_preview_text(evidence.get("title", ref)),
                    "summary": translate_preview_text(evidence.get("summary", "")),
                    "path": evidence.get("clean_path", ""),
                }
            )
            continue
        if ref in source_lookup:
            source = source_lookup[ref]
            cards.append(
                {
                    "id": ref,
                    "kind": "source",
                    "title": translate_preview_text(source.get("title", ref)),
                    "summary": translate_preview_text(source.get("summary", "")),
                    "path": source.get("path", ""),
                }
            )
    return cards[:limit]


def build_hero_payload(
    company: dict,
    readiness: dict,
    decision: dict,
    channel: dict,
    offer: dict,
    source_count: int,
    evidence_count: int,
    deliverables: list[dict],
) -> dict:
    score = safe_float(readiness.get("score"), 0.0)
    offer_name = offer.get("name") or offer.get("core_promise") or company.get("seed_summary", "")
    hero_badges = [
        {"label": f"Preparacion {int(score)}", "tone": "good" if readiness.get("status") == "ready" else "warn"},
        {"label": f"{source_count} fuentes", "tone": "neutral"},
        {"label": f"{evidence_count} evidencias", "tone": "neutral"},
    ]
    if channel.get("name"):
        hero_badges.append({"label": channel["name"], "tone": "neutral"})
    return block_payload(
        readiness.get("status", "draft"),
        max(safe_float(decision.get("confidence"), 0.0), safe_float(company.get("confidence"), 0.0)),
        company.get("name", "Caso activo"),
        decision.get("decision_summary") or company.get("seed_summary", ""),
        [
            f"{source_count} fuentes",
            f"{evidence_count} evidencias",
            channel.get("name", ""),
            f"{len(deliverables)} entregables",
        ],
        eyebrow="Sala ejecutiva",
        title=company.get("name", "Caso activo"),
        subtitle=decision.get("decision_summary") or company.get("seed_summary", ""),
        narrative=offer_name,
        website=company.get("website", ""),
        badges=hero_badges,
        deliverable_count=len(deliverables),
    )


def build_war_room_payload(
    company: dict,
    readiness: dict,
    decision: dict,
    plan: dict,
    signal_board: dict,
    pricing: dict,
    financials: dict,
    deliverables: list[dict],
    evidence: list[dict],
) -> dict:
    confidence = max(safe_float(decision.get("confidence"), 0.0), safe_float(company.get("confidence"), 0.0))
    next_steps = decision.get("next_steps", []) or plan.get("milestones", [])
    featured_deliverables = [
        {
            "id": item["id"],
            "title": localized_deliverable_title(item["id"], item["title"]),
            "summary": item.get("summary", ""),
            "excerpt": markdown_excerpt(item.get("content", ""), 220),
            "path": item.get("path", ""),
        }
        for item in deliverables[:3]
    ]
    evidence_highlights = [
        {
            "id": item["id"],
            "title": item.get("title", item["id"]),
            "summary": item.get("summary", ""),
            "quote": (item.get("quotes") or [""])[0],
            "source_type": item.get("source_type", ""),
        }
        for item in evidence[:4]
    ]
    commercial_snapshot = {
        "price_target": pricing.get("price_target"),
        "price_floor": pricing.get("price_floor"),
        "price_ceiling": pricing.get("price_ceiling"),
        "currency_code": pricing.get("currency_code", "MXN"),
        "ltv_cac_ratio": financials.get("ltv_cac_ratio"),
        "payback_months": financials.get("payback_months"),
    }
    return block_payload(
        readiness.get("status", "draft"),
        confidence,
        decision.get("recommended_action") or company.get("seed_summary", ""),
        decision.get("why_now") or company.get("seed_summary", ""),
        [
            f"Objecion principal: {signal_board.get('objections', ['Sin dato'])[0] if signal_board.get('objections') else 'Sin dato'}",
            f"Confianza comercial: {signal_board.get('trust_signals', ['Sin dato'])[0] if signal_board.get('trust_signals') else 'Sin dato'}",
            f"Precio objetivo: {currency_display(pricing.get('price_target'), pricing.get('currency_code', 'MXN'))}",
            f"Riesgo clave: {decision.get('key_risks', ['Sin dato'])[0] if decision.get('key_risks') else 'Sin dato'}",
        ],
        recommendation=decision.get("recommended_action", ""),
        rationale=decision.get("why_now", ""),
        readiness=readiness,
        signal_clusters=[
            {"label": "Dolores", "items": signal_board.get("pains", [])[:4]},
            {"label": "Objeciones", "items": signal_board.get("objections", [])[:4]},
            {"label": "Confianza", "items": signal_board.get("trust_signals", [])[:4]},
        ],
        risks=decision.get("key_risks", [])[:4],
        next_steps=next_steps[:4] if isinstance(next_steps, list) else [],
        featured_deliverables=featured_deliverables,
        evidence_highlights=evidence_highlights,
        commercial_snapshot=commercial_snapshot,
    )


def build_thesis_payload(company: dict, service: dict, icp: dict, offer: dict, messaging: dict, signal_board: dict) -> dict:
    service_statement = service.get("one_sentence_description") or company.get("seed_summary", "")
    offer_name = offer.get("name") or "Oferta principal no definida"
    confidence = max(
        safe_float(service.get("confidence"), 0.0),
        safe_float(icp.get("confidence"), 0.0),
        safe_float(offer.get("confidence"), 0.0),
        safe_float(messaging.get("confidence"), 0.0),
    )
    return block_payload(
        offer.get("status") or service.get("status") or "draft",
        confidence,
        offer_name,
        offer.get("core_promise") or service_statement,
        [
            f"Servicio: {service_statement}",
            f"ICP: {icp.get('label', 'Sin ICP validado')}",
            f"Headline: {messaging.get('headline', 'Sin headline')}",
            f"Mecanismo: {offer.get('mechanism', 'Sin mecanismo')}",
        ],
        service_statement=service_statement,
        icp=icp,
        offer=offer,
        messaging=messaging,
        buyer_truths={
            "pains": signal_board.get("pains", [])[:4],
            "outcomes": signal_board.get("outcomes", [])[:4],
            "objections": signal_board.get("objections", [])[:4],
            "trust_signals": signal_board.get("trust_signals", [])[:4],
        },
        proof_points=offer.get("proof_points", [])[:4],
    )


def build_market_summary_payload(market_records: list[dict]) -> dict:
    market_by_type = {record.get("market_type", record.get("id", "")): record for record in market_records}
    attractiveness = market_by_type.get("attractiveness", {})
    ordered = []
    for key, label in (("tam", "TAM"), ("sam", "SAM"), ("som", "SOM"), ("attractiveness", "Atractivo")):
        record = market_by_type.get(key, {})
        ordered.append(
            {
                "label": label,
                "status": record.get("status", "draft"),
                "confidence": safe_float(record.get("confidence"), 0.0),
                "segment_name": translate_preview_text(record.get("segment_name", "")),
                "value": record.get("blended_value"),
                "currency_code": record.get("currency_code", "MXN"),
                "methodology_summary": translate_preview_text(record.get("methodology_summary", "")),
                "key_assumptions": translate_preview_list(record.get("key_assumptions", [])[:4]),
            }
        )
    return block_payload(
        attractiveness.get("status", "draft"),
        attractiveness.get("confidence", 0.0),
        translate_preview_text(attractiveness.get("segment_name", "Mercado y atractivo")),
        translate_preview_text(attractiveness.get("methodology_summary", "Sin resumen metodologico.")),
        [f"{item['label']}: {item['segment_name']}" for item in ordered if item.get("segment_name")][:4],
        records=ordered,
    )


def build_competition_summary_payload(competitor_records: list[dict]) -> dict:
    competitors = [item.get("record", item) for item in competitor_records]
    for competitor in competitors:
        competitor["positioning_summary"] = translate_preview_text(competitor.get("positioning_summary", ""))
        competitor["pricing_summary"] = translate_preview_text(competitor.get("pricing_summary", ""))
        competitor["strengths"] = translate_preview_list(competitor.get("strengths", []))
        competitor["weaknesses"] = translate_preview_list(competitor.get("weaknesses", []))
        competitor["trust_signals"] = translate_preview_list(competitor.get("trust_signals", []))
    primary = choose_primary_record(competitors)
    whitespace = unique_preserve([weakness for item in competitors for weakness in item.get("weaknesses", [])])[:6]
    confidence = max([safe_float(item.get("confidence"), 0.0) for item in competitors] + [0.0])
    return block_payload(
        primary.get("status", "draft"),
        confidence,
        primary.get("positioning_summary", "Mapa competitivo"),
        translate_preview_text(primary.get("summary", primary.get("positioning_summary", "Sin resumen competitivo"))),
        whitespace[:4],
        competitors=competitors,
        whitespace=whitespace,
    )


def build_viability_summary_payload(pricing: dict, financials: dict) -> dict:
    confidence = max(safe_float(pricing.get("confidence"), 0.0), safe_float(financials.get("confidence"), 0.0))
    flags = unique_preserve(
        [financials.get("viability_warning", "")]
        + pricing.get("margin_assumptions", [])[:2]
    )
    return block_payload(
        pricing.get("status") or financials.get("status") or "draft",
        confidence,
        "Pricing y viabilidad",
        financials.get("viability_warning") or "Sin alerta de viabilidad registrada.",
        [
            f"Precio piso: {currency_display(pricing.get('price_floor'), pricing.get('currency_code', 'MXN'))}",
            f"Precio objetivo: {currency_display(pricing.get('price_target'), pricing.get('currency_code', 'MXN'))}",
            f"Precio techo: {currency_display(pricing.get('price_ceiling'), pricing.get('currency_code', 'MXN'))}",
            f"LTV:CAC: {safe_float(financials.get('ltv_cac_ratio'), 0.0):.2f}",
        ],
        pricing=pricing,
        financials=financials,
        flags=flags[:4],
    )


def build_decision_summary_payload(decision: dict, plan: dict, validation: list[dict]) -> dict:
    milestones = plan.get("milestones", []) if isinstance(plan, dict) else []
    return block_payload(
        decision.get("status", "draft"),
        decision.get("confidence", 0.0),
        decision.get("decision_summary", "Decision actual"),
        decision.get("why_now", "Sin fundamento capturado."),
        decision.get("next_steps", [])[:4],
        memo=decision,
        plan=plan,
        milestones=milestones,
        validation=validation,
    )


def build_audit_index_payload(
    company_id: str,
    company: dict,
    sources: list[dict],
    evidence: list[dict],
    findings: list[dict],
    validation: list[dict],
    decision: dict,
    offer: dict,
    pricing: dict,
    market_records: list[dict],
) -> dict:
    evidence_lookup = {item["id"]: item for item in evidence}
    source_lookup = {item.get("source_id", item.get("id", "")): item for item in sources}
    market_refs = [ref for record in market_records for ref in record.get("evidence_refs", []) + record.get("source_refs", [])]
    traceability = {
        "decision": collect_reference_cards(decision.get("evidence_refs", []) + decision.get("source_refs", []), evidence_lookup, source_lookup),
        "offer": collect_reference_cards(offer.get("evidence_refs", []) + offer.get("source_refs", []), evidence_lookup, source_lookup),
        "pricing": collect_reference_cards(pricing.get("evidence_refs", []) + pricing.get("source_refs", []), evidence_lookup, source_lookup),
        "market": collect_reference_cards(market_refs, evidence_lookup, source_lookup),
    }
    return block_payload(
        "ready",
        1.0,
        f"Auditoria de {company.get('name', company_id)}",
        "Inspeccion completa de fuentes, evidencias, findings y trazabilidad del caso.",
        [
            f"{len(sources)} fuentes",
            f"{len(evidence)} evidencias",
            f"{len(findings)} findings",
            f"{len(validation)} preguntas abiertas",
        ],
        counts={
            "sources": len(sources),
            "evidence": len(evidence),
            "findings": len(findings),
            "validation": len(validation),
        },
        sources=[
            item | {
                "title": translate_preview_text(item.get("title", "")),
                "summary": translate_preview_text(item.get("summary", "")),
            }
            for item in sources
        ],
        evidence=[
            item | {
                "title": translate_preview_text(item.get("title", "")),
                "summary": translate_preview_text(item.get("summary", "")),
            }
            for item in evidence
        ],
        findings=findings,
        validation=validation,
        traceability=traceability,
        paths=unique_preserve(
            [item.get("path", "") for item in sources[:6]]
            + [item.get("clean_path", "") for item in evidence[:6]]
            + [item.get("path", "") for item in findings[:6]]
        )[:18],
    )


def build_case_payload(company_id: str = "") -> dict:
    selected_company_id = company_id or preferred_company_id()
    if not selected_company_id:
        return empty_workspace_payload()

    refresh_company_knowledge(selected_company_id)
    companies = list_companies()
    company = next((item for item in companies if item["company_id"] == selected_company_id), company_record(selected_company_id))

    research_profile = choose_primary_record(list_research_profiles(selected_company_id))
    sources = list_sources(company_id=selected_company_id)
    evidence = list_evidence(company_id=selected_company_id)
    findings = list_findings(company_id=selected_company_id)
    validation = list_validation_questions(company_id=selected_company_id, status="open")
    research_records = list_research_records(company_id=selected_company_id)
    offer_record = choose_primary_record([item for item in research_records if item.get("offer_id") and not item.get("brief_id")])
    messaging_record = choose_primary_record([item for item in research_records if item.get("brief_id")])
    market_records = list_json_domain("market", selected_company_id)
    competitor_records = list_json_domain("competitors", selected_company_id)
    pricing_records = list_json_domain("pricing", selected_company_id)
    financial_records = list_json_domain("financials", selected_company_id)
    decision_records = list_json_domain("decisions", selected_company_id)
    plan_records = list_json_domain("plans", selected_company_id)
    deliverables = list_deliverables(selected_company_id)

    market_by_type = {
        record.get("market_type", record.get("id", "")): record
        for record in market_records
    }
    primary_pricing = choose_primary_record([item.get("record", item) for item in pricing_records])
    primary_financial = choose_primary_record([item.get("record", item) for item in financial_records])
    primary_decision = choose_primary_record([item.get("record", item) for item in decision_records])
    primary_plan = choose_primary_record([item.get("record", item) for item in plan_records])
    primary_service = choose_primary_record(company.get("services", []))
    primary_icp = choose_primary_record(company.get("icps", []))
    primary_channel = choose_primary_record(company.get("channels", []))
    signal_board = build_signal_board(company, evidence)
    readiness = company.get("readiness", {})

    summary = {
        "company_name": company.get("name", selected_company_id),
        "industry": company.get("industry", ""),
        "website": company.get("website", ""),
        "region": company.get("primary_region", ""),
        "readiness": readiness,
        "seed_summary": company.get("seed_summary", ""),
        "service": primary_service,
        "icp": primary_icp,
        "channel": primary_channel,
        "offer": offer_record,
        "messaging": messaging_record,
        "decision": primary_decision,
        "plan": primary_plan,
        "pricing": primary_pricing,
        "financials": primary_financial,
        "market": {
            "tam": market_by_type.get("tam", {}),
            "sam": market_by_type.get("sam", {}),
            "som": market_by_type.get("som", {}),
            "attractiveness": market_by_type.get("attractiveness", {}),
        },
        "signals": signal_board,
        "deliverable_previews": [
            {
                "id": item["id"],
                "title": localized_deliverable_title(item["id"], item["title"]),
                "path": item["path"],
                "summary": item.get("summary", ""),
                "excerpt": markdown_excerpt(item.get("content", "")),
            }
            for item in deliverables
        ],
        "source_kinds": unique_preserve([item.get("source_kind", "") for item in sources if item.get("source_kind")]),
        "evidence_count": len(evidence),
        "source_count": len(sources),
    }

    hero = build_hero_payload(
        company,
        readiness,
        primary_decision,
        primary_channel,
        offer_record,
        len(sources),
        len(evidence),
        deliverables,
    )
    war_room = build_war_room_payload(
        company,
        readiness,
        primary_decision,
        primary_plan,
        signal_board,
        primary_pricing,
        primary_financial,
        deliverables,
        evidence,
    )
    thesis = build_thesis_payload(company, primary_service, primary_icp, offer_record, messaging_record, signal_board)
    market_summary = build_market_summary_payload([item.get("record", item) for item in market_records])
    competition_summary = build_competition_summary_payload(competitor_records)
    viability_summary = build_viability_summary_payload(primary_pricing, primary_financial)
    decision_summary = build_decision_summary_payload(primary_decision, primary_plan, validation)
    deliverable_index = [
        {
            "id": item["id"],
            "title": localized_deliverable_title(item["id"], item["title"]),
            "summary": item.get("summary", ""),
            "excerpt": markdown_excerpt(item.get("content", ""), 240),
            "path": item.get("path", ""),
            "content": item.get("content", ""),
        }
        for item in deliverables
    ]
    audit_index = build_audit_index_payload(
        selected_company_id,
        company,
        sources,
        evidence,
        findings,
        validation,
        primary_decision,
        offer_record,
        primary_pricing,
        [item.get("record", item) for item in market_records],
    )

    return {
        "project": {
            "name": "Ws B-I",
            "tagline": "Business intelligence operativo para decisiones en Mexico.",
        },
        "company": company,
        "companies": [
            {
                "company_id": item["company_id"],
                "name": item.get("name", item["company_id"]),
                "industry": item.get("industry", ""),
                "readiness": item.get("readiness", {}),
            }
            for item in companies
        ],
        "hero": hero,
        "war_room": war_room,
        "thesis": thesis,
        "market_summary": market_summary,
        "competition_summary": competition_summary,
        "viability_summary": viability_summary,
        "decision_summary": decision_summary,
        "deliverable_index": deliverable_index,
        "audit_index": audit_index,
        "summary": summary,
        "sections": {
            "research_profile": research_profile,
            "sources": sources,
            "evidence": evidence,
            "findings": findings,
            "validation": validation,
            "offer": offer_record,
            "messaging": messaging_record,
            "market": market_records,
            "competitors": competitor_records,
            "pricing": pricing_records,
            "financials": financial_records,
            "decisions": decision_records,
            "plans": plan_records,
            "deliverables": deliverables,
        },
    }


def empty_workspace_payload() -> dict:
    github_repo_url = "https://github.com/Whitestone2025/Bussines-intelligence-for-sme-s"
    return {
        "project": {
            "name": "Ws B-I",
            "tagline": "Business intelligence operativo para decisiones en Mexico.",
        },
        "company": {},
        "companies": [],
        "sections": {},
        "summary": {},
        "onboarding": {
            "headline": "Workspace listo para iniciar",
            "summary": "Pidele a Codex que tome el repositorio desde GitHub, te haga solo las preguntas necesarias y cargue tu negocio hasta verlo en el frontend.",
            "github_repo_url": github_repo_url,
            "starter_prompt": (
                "Quiero usar Ws B-I para mi negocio. Toma el repositorio desde "
                f"{github_repo_url}, preparalo en una carpeta nueva, guiame paso a paso, hazme solo las preguntas necesarias "
                "sobre mi empresa, carga mi caso y abre el frontend cuando este listo. No soy tecnico, asi que hazte cargo "
                "de los comandos y explicame solo lo necesario."
            ),
            "steps": [
                "Crea o usa una carpeta limpia para el proyecto.",
                "Trae el repositorio desde GitHub a esa carpeta.",
                "Comparte el nombre de tu negocio, lo que vendes y el material real que ya tengas.",
                "Codex convertira eso en evidencia, cargara tu caso y abrira el frontend cuando este listo.",
            ],
            "clean_install_steps": [
                "Abre una carpeta nueva en tu computadora.",
                "Dale a Codex la URL del repositorio.",
                "Pidele que prepare todo y te guie sin tecnicismos.",
                "Responde solo las preguntas de negocio que Codex te haga.",
                "Espera a que Codex te entregue la URL local del frontend.",
            ],
            "success_state": "Tu negocio debe aparecer como caso activo en el frontend, con tesis, decision, plan y documentos.",
        },
    }


def text_fragments_for_company(company_id: str) -> list[dict]:
    company = load_json(company_base(company_id) / "company.json", {})
    profile = bootstrap_research_profile(company_id)
    fragments: list[dict] = []
    if profile.get("seed_summary"):
        fragments.append({"text": str(profile["seed_summary"]), "source_refs": [], "evidence_refs": []})
    if company.get("notes"):
        fragments.append({"text": str(company["notes"]), "source_refs": [], "evidence_refs": []})
    for source in list_sources(company_id=company_id):
        body_parts = [source.get("title", ""), source.get("summary", ""), source.get("body", "")]
        text = " ".join(part for part in body_parts if part)
        if text.strip():
            fragments.append({"text": text, "source_refs": [source["source_id"]], "evidence_refs": []})
    for evidence in list_evidence(company_id=company_id):
        text_parts = [evidence.get("title", ""), evidence.get("summary", "")]
        text_parts.extend(evidence.get("quotes", []))
        text_parts.extend(evidence.get("observations", []))
        text = " ".join(part for part in text_parts if part)
        if text.strip():
            fragments.append({"text": text, "source_refs": [evidence.get("source_id", "")] if evidence.get("source_id") else [], "evidence_refs": [evidence["id"]]})
    return fragments


def make_finding(company_id: str, category: str, statement: str, confidence: float, evidence_refs: list[str], source_refs: list[str], title: str = "", suggested_action: str = "") -> dict:
    normalized_title = title or statement[:90]
    finding_id = f"auto-{slugify(category)}-{slugify(normalized_title)[:48]}"
    status = "validated" if confidence >= 0.95 else "inferred" if confidence >= 0.65 else "needs_validation"
    return {
        "finding_id": finding_id,
        "company_id": company_id,
        "category": category,
        "title": normalized_title,
        "statement": statement,
        "status": status,
        "confidence": round(confidence, 2),
        "evidence_refs": unique_preserve([item for item in evidence_refs if item]),
        "source_refs": unique_preserve([item for item in source_refs if item]),
        "supporting_quotes": [],
        "suggested_action": suggested_action,
    }


def infer_service_finding(company_id: str) -> dict | None:
    profile = bootstrap_research_profile(company_id)
    seed_summary = str(profile.get("seed_summary", "")).strip()
    if not seed_summary:
        return None
    statement = first_sentence(seed_summary)
    confidence = 0.82 if len(statement.split()) >= 5 else 0.6
    return make_finding(
        company_id,
        "service",
        statement,
        confidence,
        [],
        [],
        title="Likely Service Statement",
        suggested_action="Validate whether this describes the core offer accurately.",
    )


def infer_icp_findings(company_id: str, fragments: list[dict]) -> list[dict]:
    combined = " ".join(fragment["text"].lower() for fragment in fragments)
    findings = []
    scored = []
    for label, keywords in ICP_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in combined)
        if score:
            scored.append((score, label))
    scored.sort(reverse=True)
    if not scored:
        return findings
    for score, label in scored[:3]:
        confidence = min(0.9, 0.45 + score * 0.12)
        findings.append(
            make_finding(
                company_id,
                "icp",
                label,
                confidence,
                [],
                [],
                title=f"Likely ICP: {label}",
                suggested_action="Confirm whether this buyer profile matches reality.",
            )
        )
    return findings


def infer_channel_findings(company_id: str, fragments: list[dict]) -> list[dict]:
    profile = bootstrap_research_profile(company_id)
    combined = " ".join(fragment["text"].lower() for fragment in fragments)
    findings = []
    if profile.get("website"):
        findings.append(make_finding(company_id, "channel", "Landing Page", 0.72, [], [], title="Likely Channel: Landing Page"))
    if "email" in combined:
        findings.append(make_finding(company_id, "channel", "Email", 0.68, [], [], title="Likely Channel: Email"))
    if "whatsapp" in combined or "dm" in combined:
        findings.append(make_finding(company_id, "channel", "WhatsApp", 0.66, [], [], title="Likely Channel: WhatsApp"))
    if "call" in combined or "sales call" in combined:
        findings.append(make_finding(company_id, "channel", "Sales Call", 0.7, [], [], title="Likely Channel: Sales Call"))
    return unique_finding_records(findings)[:3]


def infer_signal_findings(company_id: str, fragments: list[dict], category: str, cues: tuple[str, ...], title_prefix: str, suggested_action: str) -> list[dict]:
    findings = []
    seen = set()
    for fragment in fragments:
        for line in split_candidate_lines(fragment["text"]):
            lower = line.lower()
            if not any(cue in lower for cue in cues):
                continue
            if line.lower() in seen:
                continue
            seen.add(line.lower())
            confidence = 0.58
            if fragment["evidence_refs"]:
                confidence += 0.18
            if len(line.split()) >= 8:
                confidence += 0.06
            findings.append(
                make_finding(
                    company_id,
                    category,
                    line,
                    min(confidence, 0.86),
                    fragment["evidence_refs"],
                    fragment["source_refs"],
                    title=f"{title_prefix}: {line[:54]}",
                    suggested_action=suggested_action,
                )
            )
            if len(findings) >= 6:
                return findings
    return findings


def infer_market_claim_findings(company_id: str, fragments: list[dict]) -> list[dict]:
    findings = []
    for fragment in fragments:
        lower = fragment["text"].lower()
        for phrase in GENERIC_MARKET_CUES:
            if phrase in lower:
                findings.append(
                    make_finding(
                        company_id,
                        "market_claim",
                        f"The market around this company appears to lean on the phrase '{phrase}'.",
                        0.62,
                        fragment["evidence_refs"],
                        fragment["source_refs"],
                        title=f"Category cliche: {phrase}",
                        suggested_action="Avoid repeating this category cliche unless evidence proves it matters.",
                    )
                )
    return unique_finding_records(findings)[:4]


def unique_finding_records(findings: list[dict]) -> list[dict]:
    seen = set()
    output = []
    for finding in findings:
        key = (finding.get("category"), finding.get("statement", "").lower())
        if key in seen:
            continue
        seen.add(key)
        output.append(finding)
    return output


def derive_findings(company_id: str) -> list[dict]:
    fragments = text_fragments_for_company(company_id)
    findings: list[dict] = []
    service = infer_service_finding(company_id)
    if service:
        findings.append(service)
    findings.extend(infer_icp_findings(company_id, fragments))
    findings.extend(infer_channel_findings(company_id, fragments))
    findings.extend(infer_signal_findings(company_id, fragments, "pain", PAIN_CUES, "Pain", "Confirm whether this pain repeats often enough to matter."))
    findings.extend(infer_signal_findings(company_id, fragments, "outcome", OUTCOME_CUES, "Outcome", "Validate whether this outcome matters most in buying decisions."))
    findings.extend(infer_signal_findings(company_id, fragments, "objection", OBJECTION_CUES, "Objection", "Confirm whether this objection blocks deals repeatedly."))
    findings.extend(infer_signal_findings(company_id, fragments, "trust_signal", TRUST_CUES, "Trust Signal", "Promote this if it repeatedly lowers skepticism."))
    findings.extend(infer_market_claim_findings(company_id, fragments))
    return unique_finding_records(findings)


def write_auto_records(base: Path, prefix: str, records: list[dict], key: str) -> None:
    base.mkdir(parents=True, exist_ok=True)
    for path in base.glob(f"{prefix}*.json"):
        path.unlink()
    for record in records:
        identifier = record.get(key, slugify(record.get("title", "record")))
        write_json(base / f"{identifier}.json", record)


def update_company_file(company_id: str, **updates: object) -> dict:
    path = company_base(company_id) / "company.json"
    company = load_json(path, {"company_id": company_id, "name": company_id.replace("-", " ").title()})
    company.update({key: value for key, value in updates.items() if value is not None})
    default_status_confidence(company)
    write_json(path, company)
    return company


def upsert_service(company_id: str, statement: str, status: str, confidence: float, evidence_refs: list[str], source_origin: str, unresolved_questions: list[str] | None = None) -> dict:
    service_id = slugify(statement[:60])
    path = company_base(company_id) / "services" / f"{service_id}.json"
    current = load_json(path, {"service_id": service_id, "company_id": company_id})
    current.update(
        {
            "service_id": service_id,
            "company_id": company_id,
            "name": current.get("name") or first_sentence(statement)[:80],
            "one_sentence_description": statement,
            "core_outcome": current.get("core_outcome", ""),
            "status": status,
            "confidence": round(confidence, 2),
            "evidence_refs": unique_preserve(current.get("evidence_refs", []) + evidence_refs),
            "source_origin": source_origin,
            "unresolved_questions": unresolved_questions or current.get("unresolved_questions", []),
        }
    )
    write_json(path, current)
    return current


def upsert_icp(company_id: str, label: str, status: str, confidence: float, evidence_refs: list[str], source_origin: str, pains: list[str] | None = None, desired_outcomes: list[str] | None = None, common_objections: list[str] | None = None, unresolved_questions: list[str] | None = None) -> dict:
    icp_id = slugify(label[:60])
    path = company_base(company_id) / "icps" / f"{icp_id}.json"
    current = load_json(path, {"icp_id": icp_id, "company_id": company_id})
    current.update(
        {
            "icp_id": icp_id,
            "company_id": company_id,
            "label": label,
            "pains": pains or current.get("pains", []),
            "desired_outcomes": desired_outcomes or current.get("desired_outcomes", []),
            "common_objections": common_objections or current.get("common_objections", []),
            "status": status,
            "confidence": round(confidence, 2),
            "evidence_refs": unique_preserve(current.get("evidence_refs", []) + evidence_refs),
            "source_origin": source_origin,
            "unresolved_questions": unresolved_questions or current.get("unresolved_questions", []),
        }
    )
    write_json(path, current)
    return current


def upsert_channel(company_id: str, name: str, status: str, confidence: float, evidence_refs: list[str], source_origin: str, unresolved_questions: list[str] | None = None) -> dict:
    channel_id = slugify(name)
    path = company_base(company_id) / "channels" / f"{channel_id}.json"
    asset_focus_map = {
        "Landing Page": "homepage hero",
        "Email": "outbound email",
        "WhatsApp": "direct message opener",
        "Sales Call": "discovery call framing",
    }
    goal_map = {
        "Landing Page": "clarify the service before abstract promises",
        "Email": "start a relevant conversation with low friction",
        "WhatsApp": "sound human and easy to reply to",
        "Sales Call": "reduce skepticism early in the conversation",
    }
    current = load_json(path, {"channel_id": channel_id, "company_id": company_id})
    current.update(
        {
            "channel_id": channel_id,
            "company_id": company_id,
            "name": name,
            "asset_focus": current.get("asset_focus") or asset_focus_map.get(name, ""),
            "primary_goal": current.get("primary_goal") or goal_map.get(name, ""),
            "status": status,
            "confidence": round(confidence, 2),
            "evidence_refs": unique_preserve(current.get("evidence_refs", []) + evidence_refs),
            "source_origin": source_origin,
            "unresolved_questions": unresolved_questions or current.get("unresolved_questions", []),
        }
    )
    write_json(path, current)
    return current


def create_validation_question(company_id: str, question_id: str, target_entity_type: str, prompt: str, question_type: str, candidate_options: list[dict], recommended_answer: str, why_it_matters: str, resolution: dict) -> dict:
    return {
        "question_id": question_id,
        "company_id": company_id,
        "target_entity_type": target_entity_type,
        "prompt": prompt,
        "question_type": question_type,
        "candidate_options": candidate_options,
        "recommended_answer": recommended_answer,
        "status": "open",
        "answer": "",
        "why_it_matters": why_it_matters,
        "resolution": resolution,
        "created_at": now_iso(),
    }


def top_findings(company_id: str, category: str) -> list[dict]:
    findings = [item for item in list_findings(company_id=company_id) if item.get("category") == category]
    return sorted(findings, key=lambda item: item.get("confidence", 0), reverse=True)


def generate_validation_questions(company_id: str) -> list[dict]:
    questions: list[dict] = []
    companies = {company["company_id"]: company for company in list_companies()}
    company = companies.get(company_id, company_record(company_id))
    service_findings = top_findings(company_id, "service")
    icp_findings = top_findings(company_id, "icp")
    channel_findings = top_findings(company_id, "channel")

    if not any(item.get("status") in READY_STATUSES for item in company.get("services", [])) and service_findings:
        options = [{"label": finding["statement"], "value": finding["statement"]} for finding in service_findings[:3]]
        questions.append(
            create_validation_question(
                company_id,
                "auto-service-confirmation",
                "service",
                "Which of these statements is closest to what the business actually sells?",
                "single_select",
                options,
                options[0]["value"],
                "The system needs a trustworthy service statement before experiments become useful.",
                {"action": "upsert_service", "evidence_refs": service_findings[0].get("evidence_refs", [])},
            )
        )

    if not any(item.get("status") in READY_STATUSES for item in company.get("icps", [])):
        if icp_findings:
            options = [{"label": finding["statement"], "value": finding["statement"]} for finding in icp_findings[:4]]
        else:
            options = [{"label": label, "value": label} for _, label in list(zip(range(4), ICP_KEYWORDS.keys()))]
        questions.append(
            create_validation_question(
                company_id,
                "auto-icp-confirmation",
                "icp",
                "Which buyer profile feels closest to the real customer right now?",
                "single_select",
                options,
                options[0]["value"],
                "A plausible ICP helps the system group pains, objections, and channels correctly.",
                {"action": "upsert_icp"},
            )
        )

    if not any(item.get("status") in READY_STATUSES for item in company.get("channels", [])):
        if channel_findings:
            options = [{"label": finding["statement"], "value": finding["statement"]} for finding in channel_findings[:4]]
            recommended = options[0]["value"]
        else:
            options = [{"label": label, "value": label} for _, label in CHANNEL_OPTIONS]
            recommended = "Landing Page"
        questions.append(
            create_validation_question(
                company_id,
                "auto-channel-priority",
                "channel",
                "Which channel should the system improve first?",
                "single_select",
                options,
                recommended,
                "The first ready channel determines where the first experiments should focus.",
                {"action": "upsert_channel"},
            )
        )

    company_file = load_json(company_base(company_id) / "company.json", {})
    if not company_file.get("tone_constraints"):
        questions.append(
            create_validation_question(
                company_id,
                "auto-tone-constraint",
                "company",
                "How should this company sound when it communicates with buyers?",
                "free_text",
                [],
                "clear\nhuman\ndirect",
                "Tone constraints help the evaluator and future experiments avoid generic marketing language.",
                {"action": "update_tone_constraints"},
            )
        )

    return questions[:QUESTION_LIMIT]


def assemble_knowledge(company_id: str) -> None:
    company = load_json(company_base(company_id) / "company.json", {"company_id": company_id, "name": company_id.replace("-", " ").title()})
    findings = list_findings(company_id=company_id)
    questions = list_validation_questions(company_id=company_id, status="open")

    company["status"] = "validated" if not questions and list_evidence(company_id=company_id) else "needs_validation" if questions else company.get("status", "draft")
    company["confidence"] = round(min(0.95, 0.35 + len(list_evidence(company_id=company_id)) * 0.08 + len(list_sources(company_id=company_id)) * 0.04), 2)
    company["evidence_refs"] = unique_preserve(company.get("evidence_refs", []) + [item["id"] for item in list_evidence(company_id=company_id)[:6]])
    company.setdefault("source_origin", "research_profile")
    write_json(company_base(company_id) / "company.json", company)

    if not any(path for path in (company_base(company_id) / "services").glob("*.json")):
        service_finding = next((item for item in findings if item.get("category") == "service"), None)
        if service_finding:
            upsert_service(company_id, service_finding["statement"], service_finding["status"], service_finding["confidence"], service_finding.get("evidence_refs", []), "finding", [question["prompt"] for question in questions if question["target_entity_type"] == "service"])

    if not any(path for path in (company_base(company_id) / "icps").glob("*.json")):
        icp_finding = next((item for item in findings if item.get("category") == "icp"), None)
        if icp_finding:
            pains = [item["statement"] for item in findings if item.get("category") == "pain"][:3]
            outcomes = [item["statement"] for item in findings if item.get("category") == "outcome"][:3]
            objections = [item["statement"] for item in findings if item.get("category") == "objection"][:3]
            upsert_icp(company_id, icp_finding["statement"], icp_finding["status"], icp_finding["confidence"], icp_finding.get("evidence_refs", []), "finding", pains, outcomes, objections, [question["prompt"] for question in questions if question["target_entity_type"] == "icp"])

    if not any(path for path in (company_base(company_id) / "channels").glob("*.json")):
        channel_finding = next((item for item in findings if item.get("category") == "channel"), None)
        if channel_finding:
            upsert_channel(company_id, channel_finding["statement"], channel_finding["status"], channel_finding["confidence"], channel_finding.get("evidence_refs", []), "finding", [question["prompt"] for question in questions if question["target_entity_type"] == "channel"])


def write_findings(company_id: str, findings: list[dict]) -> None:
    write_auto_records(findings_dir(company_id), "auto-", findings, "finding_id")


def write_validation_questions(company_id: str, questions: list[dict]) -> None:
    base = validation_dir(company_id)
    base.mkdir(parents=True, exist_ok=True)
    answered = {path.name: load_json(path, {}) for path in base.glob("*.json") if load_json(path, {}).get("status") == "answered"}
    for path in base.glob("auto-*.json"):
        path.unlink()
    for question in questions:
        existing_name = f"{question['question_id']}.json"
        if existing_name in answered:
            continue
        write_json(base / existing_name, question)


def research_stage_for_company(company_id: str) -> str:
    source_count = len(list_sources(company_id=company_id))
    evidence_count = len(list_evidence(company_id=company_id))
    open_questions = len(list_validation_questions(company_id=company_id, status="open"))
    readiness = readiness_for_company(company_id)
    if readiness["status"] == "ready":
        return "ready_for_experiments"
    if open_questions:
        return "validating"
    if evidence_count:
        return "building_evidence"
    if source_count:
        return "gathering_sources"
    return "seeded"


def next_step_for_company(company_id: str) -> str:
    readiness = readiness_for_company(company_id)
    open_questions = len(list_validation_questions(company_id=company_id, status="open"))
    if readiness["status"] == "ready":
        return "Run the first experiment."
    if open_questions:
        return "Answer the next validation question."
    if not list_sources(company_id=company_id):
        return "Add at least one source asset."
    if len(list_evidence(company_id=company_id)) < 5:
        return "Add more normalized evidence."
    return "Refresh findings and review readiness blockers."


def refresh_company_knowledge(company_id: str) -> dict:
    ensure_company_structure(company_id)
    profile = bootstrap_research_profile(company_id)
    findings = derive_findings(company_id)
    write_findings(company_id, findings)
    questions = generate_validation_questions(company_id)
    write_validation_questions(company_id, questions)
    assemble_knowledge(company_id)
    readiness = readiness_for_company(company_id)
    profile["research_stage"] = research_stage_for_company(company_id)
    profile["readiness_score"] = readiness["score"]
    profile["open_questions_count"] = len(list_validation_questions(company_id=company_id, status="open"))
    profile["next_step"] = next_step_for_company(company_id)
    write_json(research_profile_path(company_id), profile)
    return {"company_id": company_id, "readiness": readiness, "open_questions": profile["open_questions_count"], "stage": profile["research_stage"]}


def readiness_for_company(company_id: str) -> dict:
    source_items = list_sources(company_id=company_id)
    evidence_items = list_evidence(company_id=company_id)
    findings = list_findings(company_id=company_id)
    company = load_json(company_base(company_id) / "company.json", {})
    services = [default_status_confidence(load_json(path, {}), "draft", 0.3) for path in sorted((company_base(company_id) / "services").glob("*.json"))]
    icps = [default_status_confidence(load_json(path, {}), "draft", 0.3) for path in sorted((company_base(company_id) / "icps").glob("*.json"))]
    channels = [default_status_confidence(load_json(path, {}), "draft", 0.3) for path in sorted((company_base(company_id) / "channels").glob("*.json"))]

    minimum_evidence_met = len(evidence_items) >= 5
    source_diversity_met = len({item.get("source_kind", "") for item in source_items if item.get("source_kind")}) >= 2 or len(source_items) >= 2
    service_defined = any(item.get("status") in READY_STATUSES or item.get("confidence", 0) >= 0.75 for item in services)
    icp_defined = any(item.get("status") in READY_STATUSES or item.get("confidence", 0) >= 0.75 for item in icps)
    channel_defined = any(item.get("status") in READY_STATUSES or item.get("confidence", 0) >= 0.7 for item in channels)
    insight_density = len([item for item in findings if item.get("category") in {"pain", "outcome", "objection"}]) >= 3

    checks = [
        minimum_evidence_met,
        source_diversity_met,
        service_defined,
        icp_defined,
        channel_defined,
        insight_density,
    ]
    score = round(sum(1 for item in checks if item) / len(checks) * 100, 1)
    blocking_reasons = []
    if not minimum_evidence_met:
        blocking_reasons.append("Add at least 5 evidence entries before running experiments.")
    if not source_diversity_met:
        blocking_reasons.append("Add at least 2 source assets or 2 distinct source kinds.")
    if not service_defined:
        blocking_reasons.append("Validate or strengthen the primary service statement.")
    if not icp_defined:
        blocking_reasons.append("Validate or strengthen the primary ICP.")
    if not channel_defined:
        blocking_reasons.append("Validate the first channel to improve.")
    if not insight_density:
        blocking_reasons.append("Collect more pains, outcomes, or objections from evidence.")

    status = "ready" if all(checks) else "partially_ready" if score >= 50 else "not_ready"
    return {
        "company_id": company_id,
        "company_name": company.get("name", company_id),
        "score": score,
        "status": status,
        "minimum_evidence_met": minimum_evidence_met,
        "source_diversity_met": source_diversity_met,
        "service_defined": service_defined,
        "icp_defined": icp_defined,
        "channel_defined": channel_defined,
        "insight_density": insight_density,
        "blocking_reasons": blocking_reasons,
    }


def build_knowledge_items(company_id: str = "") -> list[dict]:
    items: list[dict] = []
    for company in list_companies():
        if company_id and company["company_id"] != company_id:
            continue
        items.append(
            {
                "id": f"company:{company['company_id']}",
                "kind": "company",
                "title": company["name"],
                "company_id": company["company_id"],
                "status": company.get("status", "draft"),
                "confidence": company.get("confidence", 0),
                "summary": company.get("seed_summary", company.get("industry", "")),
                "evidence_refs": company.get("evidence_refs", []),
                "path": company.get("path", ""),
            }
        )
        for service in company.get("services", []):
            items.append(
                {
                    "id": f"service:{service['service_id']}",
                    "kind": "service",
                    "title": service.get("name", service["service_id"]),
                    "company_id": company["company_id"],
                    "service_id": service["service_id"],
                    "status": service.get("status", "draft"),
                    "confidence": service.get("confidence", 0),
                    "summary": service.get("one_sentence_description", ""),
                    "evidence_refs": service.get("evidence_refs", []),
                    "path": service.get("path", ""),
                    "record": service,
                }
            )
        for icp in company.get("icps", []):
            items.append(
                {
                    "id": f"icp:{icp['icp_id']}",
                    "kind": "icp",
                    "title": icp.get("label", icp["icp_id"]),
                    "company_id": company["company_id"],
                    "icp_id": icp["icp_id"],
                    "status": icp.get("status", "draft"),
                    "confidence": icp.get("confidence", 0),
                    "summary": ", ".join((icp.get("pains", []) or [])[:2]),
                    "evidence_refs": icp.get("evidence_refs", []),
                    "path": icp.get("path", ""),
                    "record": icp,
                }
            )
        for channel in company.get("channels", []):
            items.append(
                {
                    "id": f"channel:{channel['channel_id']}",
                    "kind": "channel",
                    "title": channel.get("name", channel["channel_id"]),
                    "company_id": company["company_id"],
                    "channel_id": channel["channel_id"],
                    "status": channel.get("status", "draft"),
                    "confidence": channel.get("confidence", 0),
                    "summary": channel.get("primary_goal", channel.get("asset_focus", "")),
                    "evidence_refs": channel.get("evidence_refs", []),
                    "path": channel.get("path", ""),
                    "record": channel,
                }
            )
    return items


def build_overview(companies: list[dict]) -> dict:
    research = list_research_profiles()
    sources = list_sources()
    evidence = list_evidence()
    findings = list_findings()
    validation = list_validation_questions(status="open")
    experiments = experiment_folder_records()
    reports = list_reports()
    patterns = list_patterns()
    market = list_json_domain("market")
    competitors = list_json_domain("competitors")
    decisions = list_json_domain("decisions")
    plans = list_json_domain("plans")
    deliverables = list_deliverables()
    ready_companies = [item for item in research if item.get("readiness", {}).get("status") == "ready"]
    return {
        "counts": {
            "research_profiles": len(research),
            "sources": len(sources),
            "evidence": len(evidence),
            "findings": len(findings),
            "validation": len(validation),
            "knowledge": len(build_knowledge_items()),
            "ready_companies": len(ready_companies),
            "experiments": len(experiments),
            "market_models": len(market),
            "competitors": len(competitors),
            "decisions": len(decisions),
            "plans": len(plans),
            "patterns": len(patterns),
            "reports": len(reports),
            "deliverables": len(deliverables),
        },
        "highlights": [
            {
                "title": profile.get("company_name", profile["company_id"]),
                "subtitle": f"Stage: {profile.get('research_stage', 'seeded')} · readiness {profile.get('readiness', {}).get('score', 0)}",
                "view": "research",
                "id": profile.get("company_id", ""),
            }
            for profile in research[:4]
        ],
        "recent_reports": reports[:3],
        "recent_deliverables": deliverables[:3],
        "recent_evidence": evidence[:3],
        "recent_findings": findings[:3],
        "recent_questions": validation[:3],
    }


def build_workspace() -> dict:
    companies = list_companies()
    for company in companies:
        refresh_company_knowledge(company["company_id"])
    companies = list_companies()
    overview = build_overview(companies)
    return {
        "project": {
            "name": "Ws B-I",
            "tagline": "Business intelligence operativo para decisiones en Mexico.",
        },
        "overview": overview,
        "companies": companies,
        "contexts": build_context_options(companies),
        "views": [
            {"id": "overview", "label": "Overview", "count": 0},
            {"id": "research", "label": "Research", "count": len(list_research_profiles())},
            {"id": "sources", "label": "Sources", "count": len(list_sources())},
            {"id": "evidence", "label": "Evidence", "count": len(list_evidence())},
            {"id": "findings", "label": "Findings", "count": len(list_findings())},
            {"id": "validation", "label": "Validation", "count": len(list_validation_questions(status="open"))},
            {"id": "knowledge", "label": "Knowledge", "count": len(build_knowledge_items())},
            {"id": "market", "label": "Market", "count": len(list_json_domain("market"))},
            {"id": "competitors", "label": "Competitors", "count": len(list_json_domain("competitors"))},
            {"id": "pricing", "label": "Pricing", "count": len(list_json_domain("pricing"))},
            {"id": "financials", "label": "Financials", "count": len(list_json_domain("financials"))},
            {"id": "decisions", "label": "Decisions", "count": len(list_json_domain("decisions"))},
            {"id": "plans", "label": "Plans", "count": len(list_json_domain("plans"))},
            {"id": "experiments", "label": "Experiments", "count": len(experiment_folder_records())},
            {"id": "deliverables", "label": "Deliverables", "count": len(list_deliverables())},
            {"id": "patterns", "label": "Patterns", "count": len(list_patterns())},
            {"id": "reports", "label": "Reports", "count": len(list_reports())},
            {"id": "files", "label": "Files", "count": len(list_files())},
        ],
    }


def rebuild_company_index(company_id: str) -> None:
    clean_dir = DATA_DIR / "corpus" / "clean" / company_id
    output = DATA_DIR / "corpus" / "index" / f"{company_id}.tsv"
    rows = ["\t".join(["entry_id", "date", "source_type", "channel", "service_id", "icp_id", "tags", "title"])]
    if clean_dir.exists():
        for path in sorted(clean_dir.glob("*.json")):
            record = load_json(path, {})
            title = record.get("title") or record.get("summary", "").splitlines()[0][:80]
            rows.append(
                "\t".join(
                    [
                        str(record.get("entry_id", "")),
                        str(record.get("date", "")),
                        str(record.get("source_type", "")),
                        str(record.get("channel", "")),
                        str(record.get("service_id", "")),
                        str(record.get("icp_id", "")),
                        "|".join(record.get("tags", [])),
                        title.replace("\t", " "),
                    ]
                )
            )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")


def create_research_profile(payload: dict) -> dict:
    session = normalize_intake_payload(payload)
    company_id = session["company_id"]
    ensure_company_structure(company_id)
    company = company_seed_record(session)
    write_json(company_base(company_id) / "company.json", company)
    profile = research_profile_seed_record(session)
    write_json(research_profile_path(company_id), profile)
    refresh_company_knowledge(company_id)
    return {"company_id": company_id}


def fetch_url_body(uri: str) -> tuple[str, str]:
    try:
        with urllib.request.urlopen(uri, timeout=5) as response:
            raw = response.read(60000).decode("utf-8", errors="ignore")
    except (urllib.error.URLError, ValueError):
        return "", ""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", raw, flags=re.IGNORECASE | re.DOTALL)
    title = clean_excerpt(unescape(title_match.group(1))) if title_match else ""
    body = re.sub(r"(?is)<script.*?>.*?</script>|<style.*?>.*?</style>", " ", raw)
    body = re.sub(r"(?s)<[^>]+>", " ", body)
    body = clean_excerpt(unescape(body))
    return title, body


def create_source(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    title = str(payload.get("title", "")).strip()
    source_kind = str(payload.get("source_kind", "")).strip()
    if not company_id or not title or not source_kind:
        raise ValueError("company_id, title, and source_kind are required")
    ensure_company_structure(company_id)
    body = str(payload.get("body", "")).strip()
    uri_or_path = str(payload.get("uri_or_path", "")).strip()
    fetched_title = ""
    if uri_or_path.startswith("http") and not body:
        fetched_title, body = fetch_url_body(uri_or_path)
    record = create_source_record(payload | {"body": body, "uri_or_path": uri_or_path}, fetched_title=fetched_title, fetched_body=body)
    source_id = record["source_id"]
    write_json(source_dir(company_id) / f"{source_id}.json", record)
    refresh_company_knowledge(company_id)
    return {"source_id": source_id, "path": rel(source_dir(company_id) / f"{source_id}.json")}


def create_evidence(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")
    ensure_company_structure(company_id)
    result = ingest_evidence(ROOT, payload | {"source_origin": payload.get("source_origin", "user_input")})
    rebuild_company_index(company_id)
    refresh_company_knowledge(company_id)
    return result


def create_insight(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    service_id = str(payload.get("service_id", "")).strip()
    title = str(payload.get("title", "")).strip()
    if not company_id or not service_id or not title:
        raise ValueError("company_id, service_id, and title are required")
    insight_id = f"{date.today().isoformat()}-{slugify(title)}"
    path = DATA_DIR / "insights" / company_id / service_id / f"{insight_id}.md"
    evidence_ids = payload.get("evidence_ids", [])
    lines = [
        "# Insight",
        "",
        "## Pattern",
        "",
        str(payload.get("pattern", "")).strip(),
        "",
        "## Evidence",
        "",
    ]
    for evidence_id in evidence_ids:
        lines.append(f"- {evidence_id}")
    lines.extend(["", "## Why It Matters", "", str(payload.get("why_it_matters", "")).strip(), ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"insight_id": insight_id, "path": rel(path)}


def next_experiment_id(company_id: str, service_id: str, asset_type: str) -> str:
    base = DATA_DIR / "experiments" / company_id / service_id
    prefix = f"{date.today().isoformat()}-{slugify(asset_type)}"
    existing = sorted(path.name for path in base.iterdir()) if base.exists() else []
    suffix = 1
    while f"{prefix}-{suffix:03d}" in existing:
        suffix += 1
    return f"{prefix}-{suffix:03d}"


def create_result_markdown(payload: dict) -> str:
    lines = [
        "# Result",
        "",
        f"Decision: {payload.get('decision', 'discard')}",
        "",
        "## Why It Won" if payload.get("decision") == "keep" else "## Why It Lost",
        "",
    ]
    for reason in payload.get("reasoning", [])[:5]:
        lines.append(f"- {reason}")
    lines.extend(["", "## What We Learned", ""])
    for key, value in payload.get("subscores", {}).items():
        baseline_value = payload.get("baseline_subscores", {}).get(key, 0)
        if value > baseline_value:
            lines.append(f"- {key.replace('_', ' ').title()} improved from {baseline_value} to {value}.")
    if lines[-1] == "":
        lines.append("- No strong learning was captured.")
    lines.append("")
    return "\n".join(lines)


def ensure_experiment_ready(company_id: str) -> dict:
    readiness = readiness_for_company(company_id)
    if readiness["status"] != "ready":
        reasons = " ".join(readiness["blocking_reasons"]) or "Readiness requirements are not met."
        raise ValueError(reasons)
    return readiness


def create_experiment(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    service_id = str(payload.get("service_id", "")).strip()
    if not company_id or not service_id:
        raise ValueError("company_id and service_id are required")
    readiness = ensure_experiment_ready(company_id)
    experiment_id = str(payload.get("experiment_id", "")).strip() or next_experiment_id(company_id, service_id, str(payload.get("asset_type", "experiment")))
    folder = DATA_DIR / "experiments" / company_id / service_id / experiment_id
    folder.mkdir(parents=True, exist_ok=True)

    evidence_ids = [item.strip() for item in payload.get("evidence_ids", []) if item.strip()]
    baseline = str(payload.get("baseline", "")).strip()
    variant = str(payload.get("variant", "")).strip()
    brief_lines = [
        "---",
        f"experiment_id: {experiment_id}",
        f"company_id: {company_id}",
        f"service_id: {service_id}",
        f"icp_id: {payload.get('icp_id', '')}",
        f"asset_type: {payload.get('asset_type', '')}",
        "status: complete",
        "---",
        "",
        "# Goal",
        "",
        str(payload.get("goal", "")).strip(),
        "",
        "# Hypothesis",
        "",
        str(payload.get("hypothesis", "")).strip(),
        "",
        "# Audience",
        "",
        str(payload.get("audience", "")).strip(),
        "",
        "# Evidence Used",
        "",
    ]
    for evidence_id in evidence_ids:
        brief_lines.append(f"- {evidence_id}")
    brief_lines.extend(["", "# Baseline Weaknesses", ""])
    for weakness in payload.get("baseline_weaknesses", []):
        brief_lines.append(f"- {weakness}")
    brief_lines.extend(["", "# Readiness Snapshot", "", json.dumps(readiness, ensure_ascii=True)])

    (folder / "brief.md").write_text("\n".join(brief_lines) + "\n", encoding="utf-8")
    (folder / "baseline.md").write_text(baseline + "\n", encoding="utf-8")
    (folder / "variant-a.md").write_text(variant + "\n", encoding="utf-8")

    evidence_map = {record["id"]: record for record in list_evidence(company_id=company_id, service_id=service_id)}
    evidence_quotes = []
    for evidence_id in evidence_ids:
        evidence_quotes.extend(evidence_map.get(evidence_id, {}).get("quotes", []))

    evaluation = evaluate_messages(
        baseline_text=baseline,
        variant_text=variant,
        evidence_quotes=evidence_quotes,
        experiment_id=experiment_id,
        company_id=company_id,
        service_id=service_id,
        asset_type=str(payload.get("asset_type", "")),
        evidence_ids=evidence_ids,
    )
    write_json(folder / "evaluation.json", evaluation)
    (folder / "result.md").write_text(create_result_markdown(evaluation), encoding="utf-8")
    return {"experiment_id": experiment_id, "folder_path": rel(folder), "decision": evaluation["decision"]}


def create_pattern(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    title = str(payload.get("title", "")).strip()
    if not company_id or not title:
        raise ValueError("company_id and title are required")
    pattern_id = slugify(title)
    path = DATA_DIR / "patterns" / company_id / f"{pattern_id}.md"
    support = [item.strip() for item in payload.get("support_refs", []) if item.strip()]
    lines = [f"# {title}", "", str(payload.get("statement", "")).strip(), "", "## Support", ""]
    for item in support:
        lines.append(f"- {item}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"pattern_id": pattern_id, "path": rel(path)}


def create_report(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")
    readiness = readiness_for_company(company_id)
    report_name = str(payload.get("report_name", "")).strip() or f"{date.today().isoformat()}-summary"
    report_id = slugify(report_name)
    experiments = experiment_folder_records(company_id=company_id)
    kept = [item for item in experiments if item.get("evaluation", {}).get("decision") == "keep"]
    lines = [
        "# Experiment Summary",
        "",
        f"Company: {company_id}",
        f"Readiness: {readiness['status']} ({readiness['score']})",
        "",
        "## Strongest Learnings",
        "",
    ]
    if kept:
        for item in kept[:5]:
            lines.append(f"- {item['id']}: {item['evaluation'].get('final_judgment', {}).get('summary', '')}")
    else:
        lines.append("- No kept experiments yet.")
    lines.extend(["", "## Readiness Blockers", ""])
    if readiness["blocking_reasons"]:
        for blocker in readiness["blocking_reasons"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- No active blockers.")
    lines.extend(["", "## Recommended Next Steps", ""])
    if experiments:
        for item in experiments[:3]:
            lines.append(f"- Revisit {item['asset_type']} messaging for `{item['service_id']}` with one tighter hypothesis.")
    else:
        lines.append(f"- {next_step_for_company(company_id)}")
    lines.append("")
    path = DATA_DIR / "reports" / company_id / f"{report_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"report_id": report_id, "path": rel(path)}


def answer_validation_question(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    question_id = str(payload.get("question_id", "")).strip()
    answer = str(payload.get("answer", "")).strip()
    if not company_id or not question_id or not answer:
        raise ValueError("company_id, question_id, and answer are required")
    path = validation_dir(company_id) / f"{question_id}.json"
    question = load_json(path, {})
    if not question:
        raise ValueError("Validation question not found")
    question["status"] = "answered"
    question["answer"] = answer
    question["answered_at"] = now_iso()
    write_json(path, question)

    findings = list_findings(company_id=company_id)
    pain_findings = [item["statement"] for item in findings if item.get("category") == "pain"][:3]
    outcome_findings = [item["statement"] for item in findings if item.get("category") == "outcome"][:3]
    objection_findings = [item["statement"] for item in findings if item.get("category") == "objection"][:3]
    resolution = question.get("resolution", {})
    action = resolution.get("action", "")
    if action == "upsert_service":
        upsert_service(company_id, answer, "validated", 1.0, resolution.get("evidence_refs", []), "validation", [])
    elif action == "upsert_icp":
        upsert_icp(company_id, answer, "validated", 1.0, [], "validation", pain_findings, outcome_findings, objection_findings, [])
    elif action == "upsert_channel":
        upsert_channel(company_id, answer, "validated", 1.0, [], "validation", [])
    elif action == "update_tone_constraints":
        company = load_json(company_base(company_id) / "company.json", {})
        company["tone_constraints"] = [line.strip() for line in answer.splitlines() if line.strip()]
        company["status"] = "validated"
        write_json(company_base(company_id) / "company.json", company)

    refresh_company_knowledge(company_id)
    return {"question_id": question_id, "status": "answered"}


class Handler(BaseHTTPRequestHandler):
    server_version = "WsBIUI/0.4"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        try:
            if parsed.path == "/api/workspace":
                self.send_json(build_workspace())
                return
            if parsed.path == "/api/case":
                self.send_json(build_case_payload(params.get("company_id", [""])[0]))
                return
            if parsed.path == "/api/research":
                self.send_json({"items": list_research_profiles(company_id=params.get("company_id", [""])[0])})
                return
            if parsed.path == "/api/companies":
                self.send_json({"items": list_companies()})
                return
            if parsed.path == "/api/sources":
                self.send_json({"items": list_sources(company_id=params.get("company_id", [""])[0], source_kind=params.get("source_kind", [""])[0], status=params.get("status", [""])[0])})
                return
            if parsed.path == "/api/evidence":
                self.send_json(
                    {
                        "items": list_evidence(
                            company_id=params.get("company_id", [""])[0],
                            service_id=params.get("service_id", [""])[0],
                            icp_id=params.get("icp_id", [""])[0],
                            source_type=params.get("source_type", [""])[0],
                            channel=params.get("channel", [""])[0],
                        )
                    }
                )
                return
            if parsed.path == "/api/findings":
                self.send_json({"items": list_findings(company_id=params.get("company_id", [""])[0], category=params.get("category", [""])[0], status=params.get("status", [""])[0])})
                return
            if parsed.path == "/api/validation":
                self.send_json({"items": list_validation_questions(company_id=params.get("company_id", [""])[0], status=params.get("status", [""])[0])})
                return
            if parsed.path == "/api/knowledge":
                self.send_json({"items": build_knowledge_items(company_id=params.get("company_id", [""])[0])})
                return
            if parsed.path == "/api/market":
                self.send_json({"items": list_json_domain("market", company_id=params.get("company_id", [""])[0])})
                return
            if parsed.path == "/api/competitors":
                self.send_json({"items": list_json_domain("competitors", company_id=params.get("company_id", [""])[0])})
                return
            if parsed.path == "/api/pricing":
                self.send_json({"items": list_json_domain("pricing", company_id=params.get("company_id", [""])[0])})
                return
            if parsed.path == "/api/financials":
                self.send_json({"items": list_json_domain("financials", company_id=params.get("company_id", [""])[0])})
                return
            if parsed.path == "/api/decisions":
                self.send_json({"items": list_json_domain("decisions", company_id=params.get("company_id", [""])[0])})
                return
            if parsed.path == "/api/plans":
                self.send_json({"items": list_json_domain("plans", company_id=params.get("company_id", [""])[0])})
                return
            if parsed.path == "/api/insights":
                self.send_json({"items": list_insights(company_id=params.get("company_id", [""])[0], service_id=params.get("service_id", [""])[0])})
                return
            if parsed.path == "/api/readiness":
                company_id = params.get("company_id", [""])[0]
                if not company_id:
                    self.send_error(HTTPStatus.BAD_REQUEST, "company_id is required")
                    return
                self.send_json(readiness_for_company(company_id))
                return
            if parsed.path == "/api/experiments":
                self.send_json({"items": experiment_folder_records(company_id=params.get("company_id", [""])[0], service_id=params.get("service_id", [""])[0], icp_id=params.get("icp_id", [""])[0])})
                return
            if parsed.path == "/api/patterns":
                self.send_json({"items": list_patterns(company_id=params.get("company_id", [""])[0])})
                return
            if parsed.path == "/api/reports":
                self.send_json({"items": list_reports(company_id=params.get("company_id", [""])[0])})
                return
            if parsed.path == "/api/deliverables":
                self.send_json({"items": list_deliverables(company_id=params.get("company_id", [""])[0])})
                return
            if parsed.path == "/api/files":
                self.send_json({"items": list_files()})
                return
            if parsed.path == "/api/file":
                raw_path = params.get("path", [""])[0]
                if not raw_path:
                    self.send_error(HTTPStatus.BAD_REQUEST, "Missing path parameter.")
                    return
                path = safe_path(raw_path)
                if not path.exists() or not path.is_file():
                    self.send_error(HTTPStatus.NOT_FOUND, "File not found.")
                    return
                if path.suffix not in TEXT_EXTENSIONS:
                    self.send_error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Unsupported file type.")
                    return
                self.send_json({"path": raw_path, "name": path.name, "extension": path.suffix, "content": path.read_text(encoding="utf-8")})
                return
            self.serve_static(parsed.path)
        except ValueError as exc:
            self.send_error(HTTPStatus.BAD_REQUEST, str(exc))

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            if parsed.path == "/api/file":
                self.handle_file_save(payload)
                return
            if parsed.path == "/api/start-research":
                self.send_json(create_research_profile(payload))
                return
            if parsed.path == "/api/intake-summary":
                session = normalize_intake_payload(payload)
                self.send_json({"session": session, "summary": intake_summary_markdown(session)})
                return
            if parsed.path == "/api/source":
                self.send_json(create_source(payload))
                return
            if parsed.path == "/api/research-refresh":
                company_id = str(payload.get("company_id", "")).strip()
                if not company_id:
                    raise ValueError("company_id is required")
                self.send_json(refresh_company_knowledge(company_id))
                return
            if parsed.path == "/api/evidence":
                self.send_json(create_evidence(payload))
                return
            if parsed.path == "/api/insight":
                self.send_json(create_insight(payload))
                return
            if parsed.path == "/api/validation-answer":
                self.send_json(answer_validation_question(payload))
                return
            if parsed.path == "/api/experiment":
                self.send_json(create_experiment(payload))
                return
            if parsed.path == "/api/pattern":
                self.send_json(create_pattern(payload))
                return
            if parsed.path == "/api/report":
                self.send_json(create_report(payload))
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint.")
        except ValueError as exc:
            self.send_error(HTTPStatus.BAD_REQUEST, str(exc))

    def handle_file_save(self, payload: dict) -> None:
        raw_path = payload.get("path", "")
        content = payload.get("content", "")
        if not raw_path:
            raise ValueError("Missing path.")
        path = safe_path(raw_path)
        if path.suffix not in TEXT_EXTENSIONS:
            self.send_error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Unsupported file type.")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.send_json({"ok": True, "path": raw_path})

    def serve_static(self, raw_path: str) -> None:
        if raw_path == "/favicon.ico":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if raw_path in {"", "/"}:
            path = UI_DIR / "index.html"
        else:
            relative = raw_path.lstrip("/")
            path = (UI_DIR / relative).resolve()
            if not str(path).startswith(str(UI_DIR.resolve())):
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid asset path.")
                return
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Asset not found.")
            return
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the Ws B-I local UI.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=4173, help="Port to bind")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Ws B-I UI available at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

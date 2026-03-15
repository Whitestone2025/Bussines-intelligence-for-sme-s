#!/usr/bin/env python3
"""Workspace layout helpers for Codex Business OS MX."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DOMAINS = (
    "companies",
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
)


def slugify_id(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "untitled"


def validate_company_id(company_id: str) -> str:
    normalized = slugify_id(company_id)
    if normalized != company_id:
        raise ValueError(f"company_id must already be slug-safe: {company_id!r}")
    return company_id


@dataclass(frozen=True)
class WorkspaceLayout:
    root: Path = ROOT

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    def domain_dir(self, domain: str) -> Path:
        return self.data_dir / domain

    def ensure_workspace_roots(self, domains: tuple[str, ...] = DEFAULT_DOMAINS) -> None:
        for domain in domains:
            self.domain_dir(domain).mkdir(parents=True, exist_ok=True)

    def company_base(self, company_id: str) -> Path:
        return self.domain_dir("companies") / validate_company_id(company_id)

    def company_domain_dir(self, domain: str, company_id: str) -> Path:
        validate_company_id(company_id)
        return self.domain_dir(domain) / company_id

    def canonical_company_paths(self, company_id: str) -> dict[str, Path]:
        validate_company_id(company_id)
        base = self.company_base(company_id)
        return {
            "company_base": base,
            "services": base / "services",
            "icps": base / "icps",
            "channels": base / "channels",
            "research": self.company_domain_dir("research", company_id),
            "sources": self.company_domain_dir("sources", company_id),
            "evidence": self.company_domain_dir("evidence", company_id),
            "findings": self.company_domain_dir("findings", company_id),
            "market": self.company_domain_dir("market", company_id),
            "competitors": self.company_domain_dir("competitors", company_id),
            "pricing": self.company_domain_dir("pricing", company_id),
            "financials": self.company_domain_dir("financials", company_id),
            "decisions": self.company_domain_dir("decisions", company_id),
            "plans": self.company_domain_dir("plans", company_id),
            "deliverables": self.company_domain_dir("deliverables", company_id),
            "validation": self.company_domain_dir("validation", company_id),
        }

    def ensure_company_workspace(self, company_id: str) -> dict[str, Path]:
        self.ensure_workspace_roots()
        paths = self.canonical_company_paths(company_id)
        for path in paths.values():
            path.mkdir(parents=True, exist_ok=True)
        return paths

    def record_path(self, domain: str, company_id: str, record_id: str, extension: str = ".json") -> Path:
        validate_company_id(company_id)
        record_slug = slugify_id(record_id)
        if not extension.startswith("."):
            extension = f".{extension}"
        return self.company_domain_dir(domain, company_id) / f"{record_slug}{extension}"

    def write_json_atomic(self, path: Path, payload: dict | list) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            handle.write(json.dumps(payload, indent=2, ensure_ascii=True) + "\n")
            temp_path = Path(handle.name)
        temp_path.replace(path)

    def load_json(self, path: Path, default: dict | list | None = None):
        if not path.exists():
            return {} if default is None else default
        return json.loads(path.read_text(encoding="utf-8"))


__all__ = ["DEFAULT_DOMAINS", "ROOT", "WorkspaceLayout", "slugify_id", "validate_company_id"]

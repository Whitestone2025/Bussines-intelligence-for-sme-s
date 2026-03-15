#!/usr/bin/env python3
"""Build a small PRD JSON file from a markdown plan."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].strip().splitlines()
    body = text[end + 5 :]
    data: dict[str, object] = {}
    current_key: str | None = None
    for line in raw:
        if not line.strip():
            continue
        if re.match(r"^\s*-\s+", line) and current_key:
            data.setdefault(current_key, [])
            casted = line.split("-", 1)[1].strip().strip('"')
            if isinstance(data[current_key], list):
                data[current_key].append(casted)
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        current_key = key
        if value:
            data[key] = value
        else:
            data[key] = []
    return data, body


def parse_story_blocks(body: str) -> list[dict]:
    pattern = re.compile(r"^## Story:\s*(?P<id>[^|]+)\|\s*(?P<title>.+)$", re.MULTILINE)
    matches = list(pattern.finditer(body))
    stories: list[dict] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        chunk = body[start:end].strip()
        story = {
            "id": match.group("id").strip(),
            "title": match.group("title").strip(),
            "status": "pending",
            "goal": extract_section(chunk, "Goal"),
            "deliverables": extract_list(chunk, "Deliverables"),
            "acceptance": extract_list(chunk, "Acceptance"),
            "checks": extract_list(chunk, "Checks"),
        }
        stories.append(story)
    return stories


def extract_section(chunk: str, name: str) -> str:
    pattern = re.compile(rf"^### {re.escape(name)}\n(?P<body>.*?)(?=^### |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(chunk)
    return match.group("body").strip() if match else ""


def extract_list(chunk: str, name: str) -> list[str]:
    body = extract_section(chunk, name)
    lines = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            lines.append(stripped[2:].strip())
    return lines


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: build_prd.py <plan.md> <prd.json>", file=sys.stderr)
        return 1

    plan_path = Path(sys.argv[1])
    prd_path = Path(sys.argv[2])
    text = plan_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    stories = parse_story_blocks(body)
    prd = {
        "project": meta.get("project", "unknown"),
        "runId": meta.get("runId", prd_path.parent.name),
        "commitPolicy": meta.get("commitPolicy", "no-commit"),
        "qualityChecks": meta.get("qualityChecks", []),
        "stories": stories,
    }
    prd_path.write_text(json.dumps(prd, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Wrote {prd_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

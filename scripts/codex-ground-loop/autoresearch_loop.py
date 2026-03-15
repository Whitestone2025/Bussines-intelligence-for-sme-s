#!/usr/bin/env python3
"""Lightweight autoresearch-style loop for Codex Business OS MX.

This adapts Karpathy's autoresearch operating pattern to a Codex-driven,
Mexico-first business intelligence system. Instead of training runs on GPU,
the loop manages short software/product experiments, records keep/discard
decisions, and generates the next bounded brief for the agent.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEADER = ["experiment_id", "score", "status", "area", "description"]
DEFAULT_TIME_BUDGET_MINUTES = 10


@dataclass
class ExperimentRow:
    experiment_id: str
    score: float
    status: str
    area: str
    description: str


def results_path(run_dir: Path) -> Path:
    return run_dir / "results.tsv"


def last_message_path(run_dir: Path) -> Path:
    return run_dir / "last-message.txt"


def config_path(run_dir: Path) -> Path:
    return run_dir / "loop-config.json"


def ensure_results_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(HEADER)


def write_config(run_dir: Path, goal: str, time_budget_minutes: int) -> None:
    config = {
        "goal": goal,
        "time_budget_minutes": time_budget_minutes,
    }
    config_path(run_dir).write_text(
        json.dumps(config, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def read_config(run_dir: Path) -> dict:
    path = config_path(run_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_header_value(text: str, label: str) -> str:
    pattern = re.compile(rf"^{re.escape(label)}:\s*(.+)$", re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def read_results(path: Path) -> list[ExperimentRow]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = []
        for raw in reader:
            if not raw:
                continue
            rows.append(
                ExperimentRow(
                    experiment_id=str(raw.get("experiment_id", "")).strip(),
                    score=float(raw.get("score", 0) or 0),
                    status=str(raw.get("status", "")).strip(),
                    area=str(raw.get("area", "")).strip(),
                    description=str(raw.get("description", "")).strip(),
                )
            )
        return rows


def append_result(path: Path, row: ExperimentRow) -> None:
    ensure_results_file(path)
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(
            [
                row.experiment_id,
                f"{row.score:.4f}",
                row.status,
                row.area,
                row.description,
            ]
        )


def latest_release_report(root: Path) -> Path | None:
    report_dir = root / "data" / "reports" / "release-readiness"
    reports = sorted(report_dir.glob("*.md"))
    return reports[-1] if reports else None


def parse_release_report(path: Path | None) -> dict:
    if path is None or not path.exists():
        return {
            "path": "",
            "passed": 0,
            "failed": 0,
            "risks": [],
        }
    text = path.read_text(encoding="utf-8")
    passed_match = re.search(r"- Passed checks:\s*(\d+)", text)
    failed_match = re.search(r"- Failed checks:\s*(\d+)", text)
    risks_block = re.search(r"## Unresolved Risks\n\n(?P<body>.*)", text, re.DOTALL)
    risks: list[str] = []
    if risks_block:
        for line in risks_block.group("body").splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                risks.append(stripped[2:].strip())
            elif stripped.startswith("## "):
                break
    return {
        "path": str(path),
        "passed": int(passed_match.group(1)) if passed_match else 0,
        "failed": int(failed_match.group(1)) if failed_match else 0,
        "risks": risks,
    }


def summarize_history(rows: list[ExperimentRow]) -> dict:
    kept = [row for row in rows if row.status == "keep"]
    discarded = [row for row in rows if row.status == "discard"]
    crashed = [row for row in rows if row.status == "crash"]
    best = max(rows, key=lambda row: row.score) if rows else None
    latest = rows[-1] if rows else None
    return {
        "count": len(rows),
        "kept": len(kept),
        "discarded": len(discarded),
        "crashed": len(crashed),
        "best": best,
        "latest": latest,
    }


def audit_run_state(run_dir: Path) -> list[str]:
    issues: list[str] = []
    cfg = read_config(run_dir)
    goal = str(cfg.get("goal", "")).strip()
    budget = cfg.get("time_budget_minutes")

    if not goal:
        issues.append("Missing persisted run goal in loop-config.json.")
    if budget in (None, ""):
        issues.append("Missing persisted time budget in loop-config.json.")

    results_file = results_path(run_dir)
    if not results_file.exists():
        issues.append("Missing results.tsv.")
    else:
        lines = results_file.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0].strip() != "\t".join(HEADER):
            issues.append("results.tsv header is missing or malformed.")

    last_message_file = last_message_path(run_dir)
    if not last_message_file.exists():
        issues.append("Missing last-message.txt.")
        return issues

    last_message = last_message_file.read_text(encoding="utf-8")
    message_goal = parse_header_value(last_message, "Goal")
    if goal and message_goal != goal:
        issues.append("last-message.txt goal does not match loop-config.json.")

    message_budget = parse_header_value(last_message, "Fixed experiment budget")
    expected_budget = f"{budget} minutes" if budget not in (None, "") else ""
    if expected_budget and message_budget != expected_budget:
        issues.append("last-message.txt time budget does not match loop-config.json.")

    return issues


def initial_message(goal: str, time_budget_minutes: int, release_info: dict) -> str:
    lines = [
        "# Autoresearch Mode",
        "",
        f"Goal: {goal}",
        f"Fixed experiment budget: {time_budget_minutes} minutes",
        "",
        "First experiment:",
        "- Establish the baseline with the current repo state.",
        "- Run `python3 scripts/release_check.py`.",
        "- Inspect one thin module and one real deliverable before editing.",
        "- Change only one variable in this experiment.",
        "",
        "Priority modules to inspect first:",
        "- `scripts/render_report.py`",
        "- `scripts/market_model.py`",
        "- `scripts/decision_engine.py`",
        "- `ui/app.js`",
        "",
        "Keep / discard rules:",
        "- Keep only changes that improve decision quality, evidence traceability, or founder usefulness.",
        "- Discard changes that only add polish without better business judgment.",
        "- Do not introduce proprietary backends or hardware-heavy dependencies.",
    ]
    if release_info["path"]:
        lines.extend(
            [
                "",
                "Latest release gate:",
                f"- Report: {release_info['path']}",
                f"- Passed checks: {release_info['passed']}",
                f"- Failed checks: {release_info['failed']}",
            ]
        )
    if release_info["risks"]:
        lines.append("- Focus on one unresolved risk, not all of them at once.")
    return "\n".join(lines) + "\n"


def next_message(goal: str, time_budget_minutes: int, release_info: dict, rows: list[ExperimentRow]) -> str:
    history = summarize_history(rows)
    latest = history["latest"]
    best = history["best"]
    lines = [
        "# Next Autoresearch Experiment",
        "",
        f"Goal: {goal}",
        f"Fixed experiment budget: {time_budget_minutes} minutes",
        f"Experiments logged: {history['count']}",
        f"Kept: {history['kept']} | Discarded: {history['discarded']} | Crashed: {history['crashed']}",
        "",
    ]
    if best:
        lines.append(
            f"Best kept result so far: `{best.experiment_id}` | score {best.score:.4f} | area `{best.area}`"
        )
    if latest:
        lines.append(
            f"Latest result: `{latest.experiment_id}` | status `{latest.status}` | area `{latest.area}`"
        )
    lines.extend(
        [
            "",
            "Direction for the next experiment:",
        ]
    )
    if latest and latest.status == "keep":
        lines.extend(
            [
                f"- Compound the kept gain around `{latest.area}` without widening scope.",
                "- Improve one adjacent weakness only if it preserves simplicity.",
            ]
        )
    elif latest and latest.status == "discard":
        lines.extend(
            [
                f"- Stay in `{latest.area}` but narrow the hypothesis to one lever.",
                "- Prefer deleting, clarifying, or grounding over adding new abstraction.",
            ]
        )
    elif latest and latest.status == "crash":
        lines.extend(
            [
                f"- Move away from the failed pattern in `{latest.area}`.",
                "- Choose a safer experiment with deterministic validation.",
            ]
        )
    else:
        lines.append("- Pick the highest-value thin area and run a baseline-improving experiment.")

    if release_info["path"]:
        lines.extend(
            [
                "",
                "Latest release gate:",
                f"- Report: {release_info['path']}",
                f"- Passed checks: {release_info['passed']}",
                f"- Failed checks: {release_info['failed']}",
            ]
        )
    if release_info["risks"]:
        lines.extend(
            [
                "",
                "Unresolved risks to target:",
            ]
        )
        for risk in release_info["risks"][:3]:
            lines.append(f"- {risk}")

    lines.extend(
        [
            "",
            "Execution rules:",
            "- Read the relevant module and one real output before editing.",
            "- Modify the smallest viable surface.",
            "- Run the narrowest validation that proves the hypothesis.",
            "- Record the result in `results.tsv` as keep, discard, or crash.",
        ]
    )
    return "\n".join(lines) + "\n"


def cmd_init(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    ensure_results_file(results_path(run_dir))
    goal = args.goal or "Improve the business intelligence system with one bounded experiment at a time."
    time_budget_minutes = args.time_budget_minutes or DEFAULT_TIME_BUDGET_MINUTES
    write_config(run_dir, goal, time_budget_minutes)
    release_info = parse_release_report(latest_release_report(Path(args.root).resolve()))
    message = initial_message(goal, time_budget_minutes, release_info)
    last_message_path(run_dir).write_text(message, encoding="utf-8")
    print(message, end="")
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    row = ExperimentRow(
        experiment_id=args.experiment_id.strip(),
        score=float(args.score),
        status=args.status.strip(),
        area=args.area.strip(),
        description=args.description.strip(),
    )
    append_result(results_path(Path(args.run_dir)), row)
    print(f"Recorded {row.experiment_id} ({row.status}, {row.score:.4f})")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    ensure_results_file(results_path(run_dir))
    config = read_config(run_dir)
    goal = args.goal or str(config.get("goal", "")).strip() or "Improve the business intelligence system with one bounded experiment at a time."
    time_budget_minutes = args.time_budget_minutes or int(config.get("time_budget_minutes", DEFAULT_TIME_BUDGET_MINUTES))
    rows = read_results(results_path(run_dir))
    release_info = parse_release_report(latest_release_report(Path(args.root).resolve()))
    message = (
        initial_message(goal, time_budget_minutes, release_info)
        if not rows
        else next_message(goal, time_budget_minutes, release_info, rows)
    )
    last_message_path(run_dir).write_text(message, encoding="utf-8")
    print(message, end="")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    issues = audit_run_state(Path(args.run_dir))
    if issues:
        for item in issues:
            print(item)
        return 1
    print("Autoresearch run-state audit passed.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Autoresearch-style loop for Codex Business OS MX.")
    parser.add_argument("--root", default=str(ROOT), help="Project root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a run directory")
    init_parser.add_argument("run_dir", help="Run directory")
    init_parser.add_argument("--goal", default=None)
    init_parser.add_argument("--time-budget-minutes", type=int, default=None)
    init_parser.set_defaults(func=cmd_init)

    record_parser = subparsers.add_parser("record", help="Append one experiment result")
    record_parser.add_argument("run_dir", help="Run directory")
    record_parser.add_argument("--experiment-id", required=True)
    record_parser.add_argument("--score", required=True, type=float)
    record_parser.add_argument("--status", required=True, choices=["keep", "discard", "crash"])
    record_parser.add_argument("--area", required=True)
    record_parser.add_argument("--description", required=True)
    record_parser.set_defaults(func=cmd_record)

    next_parser = subparsers.add_parser("next", help="Write the next experiment brief")
    next_parser.add_argument("run_dir", help="Run directory")
    next_parser.add_argument("--goal", default=None)
    next_parser.add_argument("--time-budget-minutes", type=int, default=None)
    next_parser.set_defaults(func=cmd_next)

    audit_parser = subparsers.add_parser("audit", help="Audit run-state consistency")
    audit_parser.add_argument("run_dir", help="Run directory")
    audit_parser.set_defaults(func=cmd_audit)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

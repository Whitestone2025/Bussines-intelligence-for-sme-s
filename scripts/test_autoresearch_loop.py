#!/usr/bin/env python3
"""Checks for the lightweight autoresearch loop."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "scripts" / "codex-ground-loop" / "autoresearch_loop.py"
SPEC = importlib.util.spec_from_file_location("autoresearch_loop", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

append_result = MODULE.append_result
ensure_results_file = MODULE.ensure_results_file
initial_message = MODULE.initial_message
next_message = MODULE.next_message
parse_release_report = MODULE.parse_release_report
read_results = MODULE.read_results
summarize_history = MODULE.summarize_history
audit_run_state = MODULE.audit_run_state
ExperimentRow = MODULE.ExperimentRow


def main() -> int:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        run_dir = root / "tasks" / "ground-loop" / "autoresearch-mx-v1"
        results_file = run_dir / "results.tsv"
        ensure_results_file(results_file)
        assert results_file.exists()
        assert results_file.read_text(encoding="utf-8").startswith("experiment_id\tscore\tstatus\tarea\tdescription")

        release_report = root / "data" / "reports" / "release-readiness" / "2026-03-14-999999-release-readiness.md"
        release_report.parent.mkdir(parents=True, exist_ok=True)
        release_report.write_text(
            "\n".join(
                [
                    "# Release Readiness",
                    "",
                    "- Passed checks: 16",
                    "- Failed checks: 0",
                    "",
                    "## Unresolved Risks",
                    "",
                    "- Deliverables are still thin.",
                    "- Market logic is still too heuristic.",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        release_info = parse_release_report(release_report)
        assert release_info["passed"] == 16
        assert len(release_info["risks"]) == 2

        message = initial_message("Improve deliverable quality.", 10, release_info)
        assert "First experiment" in message
        assert "render_report.py" in message

        append_result(
            results_file,
            ExperimentRow(
                experiment_id="exp-001",
                score=0.81,
                status="keep",
                area="deliverables",
                description="Add deeper recommendation structure.",
            ),
        )
        append_result(
            results_file,
            ExperimentRow(
                experiment_id="exp-002",
                score=0.79,
                status="discard",
                area="market",
                description="Tried a wider model without better evidence grounding.",
            ),
        )
        rows = read_results(results_file)
        assert len(rows) == 2
        history = summarize_history(rows)
        assert history["kept"] == 1
        assert history["discarded"] == 1
        assert history["best"].experiment_id == "exp-001"

        next_brief = next_message("Improve deliverable quality.", 10, release_info, rows)
        assert "Latest result: `exp-002` | status `discard` | area `market`" in next_brief
        assert "Unresolved risks to target" in next_brief
        assert "Record the result in `results.tsv`" in next_brief

        init_code = MODULE.main.__globals__["cmd_init"]
        next_code = MODULE.main.__globals__["cmd_next"]

        init_args = argparse.Namespace(
            root=str(root),
            run_dir=str(run_dir),
            goal="Persist this goal",
            time_budget_minutes=12,
        )
        assert init_code(init_args) == 0
        stored_config = (run_dir / "loop-config.json").read_text(encoding="utf-8")
        assert "Persist this goal" in stored_config

        next_args = argparse.Namespace(
            root=str(root),
            run_dir=str(run_dir),
            goal=None,
            time_budget_minutes=None,
        )
        assert next_code(next_args) == 0
        persisted_message = (run_dir / "last-message.txt").read_text(encoding="utf-8")
        assert "Goal: Persist this goal" in persisted_message
        assert "Fixed experiment budget: 12 minutes" in persisted_message
        assert audit_run_state(run_dir) == []

        (run_dir / "last-message.txt").write_text(
            persisted_message.replace("Goal: Persist this goal", "Goal: Wrong goal"),
            encoding="utf-8",
        )
        drift_issues = audit_run_state(run_dir)
        assert "last-message.txt goal does not match loop-config.json." in drift_issues

    print("Autoresearch loop checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

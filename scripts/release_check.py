#!/usr/bin/env python3
"""Run the release gate checks and write a readiness report."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "data" / "reports" / "release-readiness"


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H%M%S")


def run_check(command: str) -> tuple[bool, str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        shell=True,
        text=True,
        capture_output=True,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output.strip()


def build_checks() -> list[str]:
    checks = [
        "PYTHONPYCACHEPREFIX=.pycache python3 -m compileall scripts",
        "python3 scripts/test_autoresearch_loop.py",
        "python3 scripts/test_schema_contracts.py",
        "python3 scripts/test_founder_bootstrap_flow.py",
        "python3 scripts/test_reasoning_quality.py",
        "python3 scripts/test_case_view_model.py",
        "python3 scripts/test_workspace_foundation.py",
        "python3 scripts/test_intake_flow.py",
        "python3 scripts/test_evidence_ingestion.py",
        "python3 scripts/test_market_model.py",
        "python3 scripts/test_competitor_engine.py",
        "python3 scripts/test_customer_offer_engine.py",
        "python3 scripts/test_pricing_financials.py",
        "python3 scripts/test_mexico_context.py",
        "python3 scripts/test_decision_engine.py",
        "python3 scripts/test_execution_planner.py",
        "python3 scripts/test_deliverable_generator.py",
        "python3 scripts/test_ui_workspace_flow.py",
        "python3 scripts/test_business_os_e2e.py",
        "python3 scripts/test_discovery_flow.py",
        "python3 scripts/test_language_purity.py",
        "python3 scripts/test_founder_usefulness.py",
        "python3 scripts/test_non_generic_outputs.py",
        "python3 scripts/test_case_specific_decision.py",
        "python3 scripts/test_public_guide_quality.py",
        "python3 scripts/test_public_case_specificity.py",
    ]
    autoresearch_run = ROOT / "tasks" / "ground-loop" / "autoresearch-mx-v1"
    if (autoresearch_run / "loop-config.json").exists() and (autoresearch_run / "last-message.txt").exists():
        checks.insert(2, "python3 scripts/codex-ground-loop/autoresearch_loop.py audit tasks/ground-loop/autoresearch-mx-v1")
    return checks


def detect_method_risks() -> list[str]:
    risks: list[str] = []

    render_report_path = ROOT / "scripts" / "render_report.py"
    if render_report_path.exists():
        render_report = render_report_path.read_text(encoding="utf-8").lower()
        if "assumptions" not in render_report:
            risks.append("Deliverable generator still lacks explicit assumptions sections in executive outputs.")
        if "option" not in render_report:
            risks.append("Deliverables still do not present credible alternative options for material decisions.")

    rubric_path = ROOT / "rubrics" / "mexico-business-quality.md"
    if rubric_path.exists():
        rubric_text = rubric_path.read_text(encoding="utf-8").lower()
        if "contrary evidence" not in rubric_text:
            risks.append("La rubrica aun no exige con suficiente fuerza el manejo explicito de evidencia en contra.")

    return risks


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for command in build_checks():
        ok, output = run_check(command)
        results.append({"command": command, "ok": ok, "output": output})

    passed = [item for item in results if item["ok"]]
    failed = [item for item in results if not item["ok"]]

    lines = [
        "# Release Readiness",
        "",
        f"Generated: {datetime.now().replace(microsecond=0).isoformat()}",
        "",
        f"- Passed checks: {len(passed)}",
        f"- Failed checks: {len(failed)}",
        "",
        "## Results",
        "",
    ]

    for item in results:
        status = "PASS" if item["ok"] else "FAIL"
        lines.append(f"- [{status}] `{item['command']}`")
        if item["output"]:
            excerpt = item["output"].splitlines()[-1]
            lines.append(f"  Output: {excerpt}")
    lines.extend(["", "## Blockers", ""])
    if failed:
        for item in failed:
            lines.append(f"- {item['command']}")
    else:
        lines.append("- No active blockers.")
    lines.extend(["", "## Unresolved Risks", ""])
    unresolved_risks = [
        "La composicion de la UI ya funciona, pero todavia conserva rasgos de un flujo local-first mas cercano a un operador tecnico que a un founder puro.",
        "Los entregables siguen saliendo en markdown y TSV deterministas; formatos mas ricos pueden agregarse despues.",
        "Los motores ya exponen hechos, supuestos, opciones y riesgos, pero siguen siendo sintetizadores por reglas y no una capa de benchmarking externo vivo.",
        *detect_method_risks(),
    ]
    for risk in unresolved_risks:
        lines.append(f"- {risk}")
    lines.append("")

    report_path = REPORT_DIR / f"{now_stamp()}-release-readiness.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(report_path)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

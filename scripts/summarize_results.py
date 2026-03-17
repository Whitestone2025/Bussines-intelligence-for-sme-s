#!/usr/bin/env python3
"""Summarize experiment results into a markdown report with next steps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def strongest_learnings(evaluations: list[dict]) -> list[str]:
    learnings: list[str] = []
    for item in evaluations:
        for reason in item.get("reasoning", []):
            if reason not in learnings:
                learnings.append(reason)
    return learnings[:6]


def next_steps(evaluations: list[dict]) -> list[str]:
    steps: list[str] = []
    if not evaluations:
        return ["Corre el primer experimento para esta empresa."]
    kept = [item for item in evaluations if item.get("decision") == "keep"]
    discarded = [item for item in evaluations if item.get("decision") == "discard"]
    if kept:
        steps.append("Convierte las variantes ganadoras mas fuertes en patrones reutilizables.")
    if discarded:
        steps.append("Revisa las variantes perdedoras y ajusta una variable a la vez.")
    asset_types = sorted({item.get("asset_type", "") for item in evaluations if item.get("asset_type")})
    for asset in asset_types[:3]:
        steps.append(f"Corre otro experimento enfocado para `{asset}` con una hipotesis mas cerrada.")
    return steps[:5]


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize experiment results into markdown.")
    parser.add_argument("experiments_dir", help="Directory containing evaluation.json files")
    parser.add_argument("output", help="Markdown report path")
    args = parser.parse_args()

    experiments_dir = Path(args.experiments_dir)
    output = Path(args.output)
    evaluations = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(experiments_dir.rglob("evaluation.json"))
    ]

    lines = ["# Resumen de Experimentos", ""]
    if not evaluations:
        lines.append("No se encontraron evaluaciones.")
    else:
        lines.extend(
            [
                "## Aprendizajes mas fuertes",
                "",
            ]
        )
        for item in strongest_learnings(evaluations):
            lines.append(f"- {item}")
        lines.extend(["", "## Siguientes pasos recomendados", ""])
        for item in next_steps(evaluations):
            lines.append(f"- {item}")
        lines.extend(["", "## Bitacora de experimentos", ""])

    for data in evaluations:
        lines.extend(
            [
                f"### {data.get('experiment_id', 'unknown-experiment')}",
                "",
                f"- Decision: {data.get('decision', 'unknown')}",
                f"- Ganador: {data.get('winner', 'unknown')}",
                f"- Tipo de activo: {data.get('asset_type', 'unknown')}",
                f"- Puntaje base: {data.get('baseline_score', 0)}",
                f"- Puntaje variante: {data.get('variant_score', 0)}",
                f"- IDs de evidencia: {', '.join(data.get('evidence_ids', [])) or 'ninguno'}",
                "",
            ]
        )
        reasoning = data.get("reasoning", [])
        if reasoning:
            lines.append("Razonamiento:")
            for item in reasoning:
                lines.append(f"- {item}")
            lines.append("")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

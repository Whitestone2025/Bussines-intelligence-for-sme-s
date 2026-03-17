#!/usr/bin/env python3
"""Render deterministic tabular deliverables from canonical objects."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def unique_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        normalized = str(item).strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            ordered.append(normalized)
    return ordered


def translate_assumption(text: str) -> str:
    translated = str(text or "").strip()
    direct = {
        "Annual price per customer assumed at MXN 42,000.00.": "Se asume un ingreso anual por cliente de MXN 42,000.00.",
        "Target customer ratio set at 18% of the total addressable customer base.": "Se asume que el 18% del mercado total direccionable entra al segmento objetivo.",
        "Serviceable customer ratio set at 35% of target customers.": "Se asume que el 35% del segmento objetivo es realmente atendible.",
        "Obtainable customer ratio set at 8% of serviceable customers.": "Se asume que el 8% del segmento atendible es capturable en el corto plazo.",
        "Bottom-up model uses 140 reachable customers and 12% expected close rate.": "El modelo bottom-up usa 140 clientes alcanzables y una tasa de cierre esperada de 12%.",
    }
    translated = direct.get(translated, translated)
    translated = re.sub(
        r"Annual price per customer assumed at (MXN [0-9,]+(?:\.[0-9]{2})?)\.",
        r"Se asume un ingreso anual por cliente de \1.",
        translated,
    )
    translated = re.sub(
        r"Target customer ratio set at ([0-9]+%) of the total addressable customer base\.",
        r"Se asume que el \1 del mercado total direccionable entra al segmento objetivo.",
        translated,
    )
    translated = re.sub(
        r"Serviceable customer ratio set at ([0-9]+%) of target customers\.",
        r"Se asume que el \1 del segmento objetivo es realmente atendible.",
        translated,
    )
    translated = re.sub(
        r"Obtainable customer ratio set at ([0-9]+%) of serviceable customers\.",
        r"Se asume que el \1 del segmento atendible es capturable en el corto plazo.",
        translated,
    )
    translated = re.sub(
        r"Bottom-up model uses ([0-9,]+) reachable customers and ([0-9]+%) expected close rate\.",
        r"El modelo bottom-up usa \1 clientes alcanzables y una tasa de cierre esperada de \2.",
        translated,
    )
    return translated


def pricing_table(bundle: dict) -> str:
    pricing = bundle["pricing_model"]
    rows = [
        ["type", "name", "value", "summary"],
        ["metric", "price_floor", f"{pricing['currency_code']} {pricing['price_floor']:.2f}", "Precio minimo viable para proteger el margen objetivo."],
        ["metric", "price_target", f"{pricing['currency_code']} {pricing['price_target']:.2f}", "Precio de trabajo recomendado para la primera prueba comercial."],
        ["metric", "price_ceiling", f"{pricing['currency_code']} {pricing['price_ceiling']:.2f}", "Limite superior antes de necesitar mas prueba o una entrega de mayor involucramiento."],
    ]
    for tier in pricing.get("tier_summaries", []):
        rows.append(["tier", tier["name"], f"{pricing['currency_code']} {tier['price']:.2f}", tier["value_summary"]])
    return "\n".join("\t".join(row) for row in rows) + "\n"


def milestone_table(bundle: dict) -> str:
    rows = [["timeframe", "milestone", "owner", "dependencies", "success_metric"]]
    for item in bundle["execution_plan"].get("milestones", []):
        rows.append(
            [
                item["timeframe"],
                item["name"],
                item.get("owner", "Fundador"),
                ",".join(item.get("dependencies", [])),
                item["success_metric"],
            ]
        )
    return "\n".join("\t".join(row) for row in rows) + "\n"


def decision_options_table(bundle: dict) -> str:
    decision = bundle["decision_memo"]
    options = bundle.get("options", [])
    rows = [["label", "summary", "recommended"]]
    if options:
        for option in options:
            rows.append(
                [
                    str(option.get("label", "")).strip(),
                    str(option.get("summary", option.get("action", ""))).strip(),
                    "si" if bool(option.get("recommended", False)) else "no",
                ]
            )
    else:
        rows.append(["Ruta recomendada", decision["recommended_action"], "si"])
        for index, action in enumerate(decision.get("alternative_actions", []), start=1):
            rows.append([f"Alternativa {index}", action, "no"])
    return "\n".join("\t".join(row) for row in rows) + "\n"


def assumption_register_table(bundle: dict) -> str:
    market = bundle["market_model"]
    pricing = bundle["pricing_model"]
    assumptions = []
    assumptions.extend(("market", translate_assumption(item)) for item in market.get("key_assumptions", []))
    assumptions.extend(("pricing", translate_assumption(item)) for item in pricing.get("margin_assumptions", []))
    assumptions.extend(("decision", translate_assumption(item)) for item in bundle.get("assumptions", []))
    rows = [["category", "assumption"]]
    parsed_rows = [row.split("\t", 1) for row in unique_preserve([f"{category}\t{text}" for category, text in assumptions])]
    rows.extend(parsed_rows)
    return "\n".join("\t".join(row) for row in rows) + "\n"


def render_tables(bundle: dict) -> dict[str, str]:
    return {
        "pricing-options.tsv": pricing_table(bundle),
        "decision-options.tsv": decision_options_table(bundle),
        "assumption-register.tsv": assumption_register_table(bundle),
        "plan-milestones.tsv": milestone_table(bundle),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render TSV tables from a JSON bundle.")
    parser.add_argument("input", help="JSON bundle fixture")
    args = parser.parse_args()
    bundle = json.loads(Path(args.input).read_text(encoding="utf-8"))
    for name, content in render_tables(bundle).items():
        print(f"== {name} ==")
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

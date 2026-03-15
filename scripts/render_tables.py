#!/usr/bin/env python3
"""Render deterministic tabular deliverables from canonical objects."""

from __future__ import annotations

import argparse
import json
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


def pricing_table(bundle: dict) -> str:
    pricing = bundle["pricing_model"]
    rows = [
        ["type", "name", "value", "summary"],
        ["metric", "price_floor", f"{pricing['currency_code']} {pricing['price_floor']:.2f}", "Minimum viable price to protect the target margin."],
        ["metric", "price_target", f"{pricing['currency_code']} {pricing['price_target']:.2f}", "Recommended working price for the first commercial test."],
        ["metric", "price_ceiling", f"{pricing['currency_code']} {pricing['price_ceiling']:.2f}", "Upper bound before stronger proof or higher-touch delivery is needed."],
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
                item.get("owner", "Founder"),
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
                    "yes" if bool(option.get("recommended", False)) else "no",
                ]
            )
    else:
        rows.append(["Recommended path", decision["recommended_action"], "yes"])
        for index, action in enumerate(decision.get("alternative_actions", []), start=1):
            rows.append([f"Alternative {index}", action, "no"])
    return "\n".join("\t".join(row) for row in rows) + "\n"


def assumption_register_table(bundle: dict) -> str:
    market = bundle["market_model"]
    pricing = bundle["pricing_model"]
    assumptions = []
    assumptions.extend(("market", item) for item in market.get("key_assumptions", []))
    assumptions.extend(("pricing", item) for item in pricing.get("margin_assumptions", []))
    assumptions.extend(("decision", item) for item in bundle.get("assumptions", []))
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

#!/usr/bin/env python3
"""Evaluate baseline vs variant messaging with a clearer CQS model."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


GENERIC_PHRASES = {
    "unlock your potential",
    "scale to the next level",
    "results-driven",
    "end-to-end solution",
    "transform your business",
    "growth partner",
    "innovative solution",
    "full-service strategy",
}

TRUST_WORDS = {"proof", "process", "example", "transparent", "exactly", "show", "real", "specific", "before"}
CTA_WORDS = {"book", "reply", "schedule", "talk", "see", "review", "send", "start"}

CHANNEL_RULES = {
    "landing_hero": {
        "good": {"clarify", "exactly", "service", "before", "what", "who"},
        "bad": {"agency", "partner", "solution"},
        "notes": [
            "Landing heroes should explain the service before promising abstract outcomes.",
            "Fast clarity matters more than polish.",
        ],
    },
    "email": {
        "good": {"reply", "specific", "because", "quick", "simple"},
        "bad": {"synergy", "transform"},
        "notes": [
            "Emails should feel direct and low-friction.",
        ],
    },
    "whatsapp": {
        "good": {"quick", "simple", "look", "send", "see"},
        "bad": {"strategy", "framework"},
        "notes": [
            "WhatsApp copy should sound human and lightweight.",
        ],
    },
}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def sentence_count(text: str) -> int:
    return max(1, len(re.findall(r"[.!?]+", text)) or 1)


def unique_token_ratio(tokens: list[str]) -> float:
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def extract_signal_bundle(text: str, evidence_quotes: list[str], asset_type: str) -> dict:
    lower = text.lower()
    tokens = tokenize(text)
    evidence_tokens = set(token for quote in evidence_quotes for token in tokenize(quote))
    overlap_tokens = sorted(set(tokens) & evidence_tokens)
    generic_hits = sorted(phrase for phrase in GENERIC_PHRASES if phrase in lower)
    trust_hits = sorted({token for token in tokens if token in TRUST_WORDS})
    cta_hits = sorted({token for token in tokens if token in CTA_WORDS})
    number_hits = re.findall(r"\b\d+\b", text)

    channel = CHANNEL_RULES.get(asset_type, {})
    channel_good = sorted({token for token in tokens if token in channel.get("good", set())})
    channel_bad = sorted({token for token in tokens if token in channel.get("bad", set())})

    return {
        "token_count": len(tokens),
        "sentence_count": sentence_count(text),
        "unique_token_ratio": round(unique_token_ratio(tokens), 3),
        "evidence_overlap_count": len(overlap_tokens),
        "evidence_overlap_tokens": overlap_tokens,
        "generic_phrase_hits": generic_hits,
        "trust_word_hits": trust_hits,
        "cta_hits": cta_hits,
        "numeric_detail_hits": number_hits,
        "channel_positive_hits": channel_good,
        "channel_negative_hits": channel_bad,
    }


def score_signal_bundle(bundle: dict) -> tuple[dict[str, int], list[str]]:
    token_count = bundle["token_count"]
    sentence_total = bundle["sentence_count"]
    overlap_count = bundle["evidence_overlap_count"]
    generic_total = len(bundle["generic_phrase_hits"])
    trust_total = len(bundle["trust_word_hits"])
    cta_total = len(bundle["cta_hits"])
    numeric_total = len(bundle["numeric_detail_hits"])
    positive_total = len(bundle["channel_positive_hits"])
    negative_total = len(bundle["channel_negative_hits"])
    unique_ratio = bundle["unique_token_ratio"]

    clarity = max(0, min(10, 8 - max(0, sentence_total - 3) + (1 if token_count <= 80 else 0) - negative_total))
    specificity = max(0, min(10, 2 + numeric_total + min(3, int(unique_ratio * 10)) + positive_total - generic_total))
    credibility = max(0, min(10, 3 + trust_total + (1 if overlap_count >= 3 else 0) - generic_total - negative_total))
    differentiation = max(0, min(10, 5 + min(3, overlap_count) + positive_total - generic_total))
    customer_language_fit = max(0, min(10, 2 + overlap_count))
    offer_strength = max(0, min(10, 3 + positive_total + (1 if "for" in bundle["evidence_overlap_tokens"] else 0) + numeric_total))
    anti_hype = max(0, min(10, 10 - generic_total - negative_total))
    response_potential = max(0, min(10, 3 + cta_total + (1 if "?" in "".join(bundle["cta_hits"]) else 0)))

    scores = {
        "clarity": clarity,
        "specificity": specificity,
        "credibility": credibility,
        "differentiation": differentiation,
        "customer_language_fit": customer_language_fit,
        "offer_strength": offer_strength,
        "anti_hype": anti_hype,
        "response_potential": response_potential,
    }

    notes = []
    if overlap_count:
        notes.append("Uses language that overlaps with real customer evidence.")
    if generic_total:
        notes.append("Contains generic marketing phrasing that weakens trust.")
    if trust_total:
        notes.append("Includes trust-building language.")
    if numeric_total:
        notes.append("Includes concrete detail.")
    if negative_total:
        notes.append("Uses words that weaken this channel's best-practice style.")
    return scores, notes


def total_score(scores: dict[str, int]) -> int:
    return sum(scores.values())


def channel_notes(asset_type: str) -> list[str]:
    return CHANNEL_RULES.get(asset_type, {}).get("notes", [])


def compare_reasoning(
    baseline_scores: dict[str, int],
    variant_scores: dict[str, int],
    baseline_notes: list[str],
    variant_notes: list[str],
) -> list[str]:
    reasoning: list[str] = []
    baseline_total = total_score(baseline_scores)
    variant_total = total_score(variant_scores)
    if variant_total > baseline_total:
        reasoning.append("Variant scored higher than the baseline.")
    elif variant_total == baseline_total:
        reasoning.append("Variant tied the baseline, so no clear improvement was found.")
    else:
        reasoning.append("Variant scored lower than the baseline.")

    for key, value in variant_scores.items():
        delta = value - baseline_scores.get(key, 0)
        if delta >= 2:
            reasoning.append(f"Variant improved {key.replace('_', ' ')} meaningfully.")
        elif delta <= -2:
            reasoning.append(f"Variant weakened {key.replace('_', ' ')} meaningfully.")

    for note in variant_notes:
        if note not in reasoning:
            reasoning.append(note)
    for note in baseline_notes:
        if note.startswith("Contains generic") and note not in reasoning:
            reasoning.append("Baseline relies on generic phrasing.")
    return reasoning


def evaluate_messages(
    baseline_text: str,
    variant_text: str,
    evidence_quotes: list[str],
    experiment_id: str,
    company_id: str = "",
    service_id: str = "",
    asset_type: str = "",
    evidence_ids: list[str] | None = None,
) -> dict:
    evidence_ids = evidence_ids or []
    baseline_signals = extract_signal_bundle(baseline_text, evidence_quotes, asset_type)
    variant_signals = extract_signal_bundle(variant_text, evidence_quotes, asset_type)
    baseline_scores, baseline_notes = score_signal_bundle(baseline_signals)
    variant_scores, variant_notes = score_signal_bundle(variant_signals)

    baseline_total = total_score(baseline_scores)
    variant_total = total_score(variant_scores)
    winner = "variant_a" if variant_total >= baseline_total else "baseline"
    decision = "keep" if winner == "variant_a" and variant_total > baseline_total else "discard"

    return {
        "experiment_id": experiment_id,
        "company_id": company_id,
        "service_id": service_id,
        "asset_type": asset_type,
        "baseline_score": baseline_total,
        "variant_score": variant_total,
        "winner": winner,
        "decision": decision,
        "subscores": variant_scores,
        "baseline_subscores": baseline_scores,
        "heuristic_signals": {
            "baseline": baseline_signals,
            "variant": variant_signals,
        },
        "channel_notes": channel_notes(asset_type),
        "reasoning": compare_reasoning(baseline_scores, variant_scores, baseline_notes, variant_notes),
        "baseline_notes": baseline_notes,
        "variant_notes": variant_notes,
        "evidence_ids": evidence_ids,
        "final_judgment": {
            "summary": "Keep the variant." if decision == "keep" else "Discard the variant.",
            "why": "The variant is stronger on balance according to the current Communication Quality Score."
            if decision == "keep"
            else "The variant does not clearly outperform the baseline.",
        },
    }


def read_quotes(paths: list[Path]) -> list[str]:
    quotes: list[str] = []
    for path in paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        quotes.extend(record.get("verbatim_quotes", []))
    return quotes


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate baseline and variant messaging.")
    parser.add_argument("--baseline", required=True, help="Baseline markdown file")
    parser.add_argument("--variant", required=True, help="Variant markdown file")
    parser.add_argument("--evidence", nargs="*", default=[], help="Evidence JSON files")
    parser.add_argument("--output", required=True, help="Destination evaluation JSON")
    parser.add_argument("--experiment-id", required=True, help="Experiment identifier")
    parser.add_argument("--company-id", default="", help="Company identifier")
    parser.add_argument("--service-id", default="", help="Service identifier")
    parser.add_argument("--asset-type", default="", help="Asset type")
    args = parser.parse_args()

    baseline_path = Path(args.baseline)
    variant_path = Path(args.variant)
    evidence_paths = [Path(p) for p in args.evidence]
    output_path = Path(args.output)

    payload = evaluate_messages(
        baseline_text=baseline_path.read_text(encoding="utf-8"),
        variant_text=variant_path.read_text(encoding="utf-8"),
        evidence_quotes=read_quotes(evidence_paths),
        experiment_id=args.experiment_id,
        company_id=args.company_id,
        service_id=args.service_id,
        asset_type=args.asset_type,
        evidence_ids=[path.stem for path in evidence_paths],
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

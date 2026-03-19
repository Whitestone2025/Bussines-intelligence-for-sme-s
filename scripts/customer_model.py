#!/usr/bin/env python3
"""ICP, offer, and messaging intelligence for Codex Business OS MX."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from workspace import WorkspaceLayout, slugify_id


ICP_KEYWORDS = {
    "Fundadores y duenos de negocios de servicio": {"founder", "owner", "ceo", "principal", "fundador", "dueno"},
    "Lideres de marketing en PyMEs": {"marketing", "brand", "growth", "demand", "marca", "demanda"},
    "Lideres comerciales": {"sales", "pipeline", "closer", "revenue", "ventas", "comercial"},
    "Lideres de operaciones": {"operations", "ops", "delivery", "process", "operaciones", "entrega"},
}

FORBIDDEN_PHRASES = {
    "partner de crecimiento",
    "solucion integral",
    "orientado a resultados",
    "servicio full-service",
    "llevar al siguiente nivel",
}


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def unique_preserve(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        normalized = " ".join(str(item).split()).strip()
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        result.append(normalized)
    return result


def evidence_haystack(evidence_items: list[dict]) -> str:
    return " ".join(
        [
            str(item.get("summary", "")) + " " + " ".join(item.get("quotes", [])) + " " + " ".join(item.get("observations", []))
            for item in evidence_items
        ]
    ).lower()


def infer_icp_label(target_customer: str, evidence_items: list[dict]) -> tuple[str, int]:
    if target_customer.strip():
        return target_customer.strip(), 4
    haystack = evidence_haystack(evidence_items)
    scores = {}
    for label, keywords in ICP_KEYWORDS.items():
        scores[label] = sum(1 for keyword in keywords if keyword in haystack)
    best = max(scores.items(), key=lambda item: item[1])
    if best[1]:
        return best[0], best[1]
    return "Comprador principal por validar", 0


def top_phrases(values: list[str], limit: int = 3) -> list[str]:
    counter = Counter(unique_preserve(values))
    return [item for item, _ in counter.most_common(limit)]


def first_present(values: list[str], fallback: str) -> str:
    for value in values:
        normalized = " ".join(str(value).split()).strip()
        if normalized:
            return normalized
    return fallback


def build_core_promise(label: str, uncertain_icp: bool, main_pain: str, core_outcome: str, mechanism: str) -> str:
    if uncertain_icp:
        return (
            "Aclarar que se entrega, como funciona y por que eso reduce el riesgo percibido antes de prometer resultados."
        )
    return (
        f"Ayudar a {label.lower()} a pasar de {main_pain.lower()} a {core_outcome.lower()} "
        f"con {mechanism.lower()}."
    )


def build_headline(service_name: str, label: str, uncertain_icp: bool, main_pain: str, trust_signals: list[str]) -> str:
    trust_signal = first_present(trust_signals, "pruebas claras del servicio")
    if uncertain_icp:
        return "Todavia estamos afinando para quien es esta oferta y que prueba necesita ver primero."
    return (
        f"{service_name}: menos {main_pain.lower()} y mas claridad para {label.lower()} "
        f"con {trust_signal.lower()}."
    )


def build_subheadline(uncertain_icp: bool, mechanism: str, objections: list[str], supporting_quotes: list[str]) -> str:
    if supporting_quotes:
        return f'El mensaje debe responder a una senal real del comprador: "{supporting_quotes[0]}".'
    if objections:
        return (
            f"El sistema detecta que una objecion importante es '{objections[0]}', por eso el mensaje debe explicar "
            f"{mechanism.lower()} antes de empujar una promesa."
        )
    if uncertain_icp:
        return "Todavia hace falta validar mejor a quien compra, que duda tiene y que evidencia necesita ver primero."
    return f"El mensaje principal debe mostrar {mechanism.lower()} antes de pedir confianza."


def build_customer_outputs(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")

    evidence_items = payload.get("evidence_items", [])
    pains = top_phrases([item for evidence in evidence_items for item in evidence.get("candidate_pains", [])], 4)
    outcomes = top_phrases([item for evidence in evidence_items for item in evidence.get("candidate_outcomes", [])], 4)
    objections = top_phrases([item for evidence in evidence_items for item in evidence.get("candidate_objections", [])], 4)
    trust_signals = top_phrases([item for evidence in evidence_items for item in evidence.get("trust_signals", [])], 4)
    supporting_quotes = unique_preserve([quote for evidence in evidence_items for quote in evidence.get("quotes", [])])[:4]
    evidence_refs = unique_preserve([evidence.get("id") or evidence.get("evidence_id", "") for evidence in evidence_items])[:6]
    source_refs = unique_preserve([evidence.get("source_id", "") for evidence in evidence_items if evidence.get("source_id")])[:6]
    timestamp = now_iso()

    label, icp_signal_score = infer_icp_label(str(payload.get("target_customer", "")), evidence_items)
    icp_id = slugify_id(label)
    uncertain_icp = label == "Comprador principal por validar"
    confidence = round(min(0.92, 0.28 + 0.06 * len(evidence_refs) + 0.03 * len(source_refs) + 0.05 * icp_signal_score), 2)
    icp_status = "needs_validation" if uncertain_icp or confidence < 0.65 else "inferred"

    service_name = str(payload.get("service_name", "")).strip() or "Oferta principal por validar"
    core_outcome = first_present(outcomes, "entender con mas claridad que se entrega antes de comprar")
    main_pain = first_present(pains, "no entender con claridad que se hace y que se entrega")
    mechanism = (
        str(payload.get("mechanism_hint", "")).strip()
        or "un proceso visible que muestra que se hace, como se hace y que puede esperar el comprador"
    )

    icp_record = {
        "icp_id": icp_id,
        "company_id": company_id,
        "label": label,
        "pains": pains,
        "desired_outcomes": outcomes,
        "common_objections": objections,
        "trust_signals": trust_signals,
        "status": icp_status,
        "confidence": confidence,
        "source_origin": "customer_model_engine",
        "evidence_refs": evidence_refs,
        "source_refs": source_refs,
        "supporting_quotes": supporting_quotes,
        "unresolved_questions": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    offer_id = f"{company_id}-{slugify_id(service_name)}-offer"
    audience_phrase = label.lower() if not uncertain_icp else "el comprador mas probable identificado hasta ahora"
    offer_status = "needs_validation" if uncertain_icp else "inferred"

    offer_record = {
        "offer_id": offer_id,
        "company_id": company_id,
        "service_id": slugify_id(service_name),
        "name": service_name,
        "core_promise": build_core_promise(label, uncertain_icp, main_pain, core_outcome, mechanism),
        "mechanism": mechanism,
        "proof_points": trust_signals or ["proceso claro", "entregables especificos"],
        "anti_claims": sorted(FORBIDDEN_PHRASES),
        "status": offer_status,
        "confidence": confidence,
        "source_origin": "customer_model_engine",
        "evidence_refs": evidence_refs,
        "source_refs": source_refs,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    headline = build_headline(service_name, label, uncertain_icp, main_pain, trust_signals)
    subheadline = build_subheadline(uncertain_icp, mechanism, objections, supporting_quotes)
    messaging_record = {
        "brief_id": f"{offer_id}-messaging",
        "company_id": company_id,
        "offer_id": offer_id,
        "audience_label": label,
        "headline": headline,
        "subheadline": subheadline,
        "proof_points": trust_signals or ["proceso visible", "prueba concreta", "lenguaje humano"],
        "objection_handlers": objections or ["Explica que se hace antes de prometer resultados."],
        "forbidden_phrases": sorted(FORBIDDEN_PHRASES),
        "status": offer_status,
        "confidence": confidence,
        "source_origin": "customer_model_engine",
        "evidence_refs": evidence_refs,
        "source_refs": source_refs,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    return {"icp": icp_record, "offer": offer_record, "messaging": messaging_record}


def persist_customer_outputs(root: Path, payload: dict) -> dict:
    layout = WorkspaceLayout(root=root)
    company_id = str(payload.get("company_id", "")).strip()
    layout.ensure_company_workspace(company_id)
    outputs = build_customer_outputs(payload)

    icp_path = layout.root / "data" / "companies" / company_id / "icps" / f"{outputs['icp']['icp_id']}.json"
    icp_path.parent.mkdir(parents=True, exist_ok=True)
    layout.write_json_atomic(icp_path, outputs["icp"])

    offer_path = layout.record_path("research", company_id, outputs["offer"]["offer_id"])
    messaging_path = layout.record_path("research", company_id, outputs["messaging"]["brief_id"])
    layout.write_json_atomic(offer_path, outputs["offer"])
    layout.write_json_atomic(messaging_path, outputs["messaging"])
    return {"icp_path": icp_path, "offer_path": offer_path, "messaging_path": messaging_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build customer, offer, and messaging outputs from a JSON fixture.")
    parser.add_argument("input", help="JSON fixture path")
    parser.add_argument("--root", default=".", help="Project root for persistence")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = persist_customer_outputs(Path(args.root).resolve(), payload)
    for path in result.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

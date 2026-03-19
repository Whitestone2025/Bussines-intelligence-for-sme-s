#!/usr/bin/env python3
"""Checks that founder-facing copy explains practical usefulness, not only structure."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def require_phrases(text: str, phrases: list[str], label: str) -> None:
    lowered = text.lower()
    for phrase in phrases:
        assert phrase in lowered, f"{label} is missing required phrase: {phrase}"


def main() -> int:
    frontend_doc = (ROOT / "docs" / "founder" / "03-ver-tu-frontend.md").read_text(encoding="utf-8")
    guide = (ROOT / "docs" / "founder" / "wsbi-public-guide.md").read_text(encoding="utf-8")
    reddit = (ROOT / "docs" / "founder" / "wsbi-reddit-post.md").read_text(encoding="utf-8")

    require_phrases(
        frontend_doc,
        [
            "para que sirve cada bloque",
            "te sirve para",
            "portada",
            "decision",
            "auditoria",
        ],
        "frontend doc",
    )
    require_phrases(
        guide,
        [
            "te sirve para",
            "decision",
            "auditoria",
            "precio y viabilidad",
        ],
        "public guide",
    )
    require_phrases(
        reddit,
        [
            "que obtiene",
            "como se usa si no eres tecnico",
            "si te pide permisos, daselos",
            "como razono",
        ],
        "reddit guide",
    )

    assert guide.lower().count("te sirve para") >= 4, "Guide should repeatedly explain practical usefulness."

    print("Founder usefulness checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

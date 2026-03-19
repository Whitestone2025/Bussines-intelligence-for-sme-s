#!/usr/bin/env python3
"""Checks that the public short guide explains the system with practical value and without leaked generic English output."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    guide = (ROOT / "docs" / "founder" / "wsbi-public-guide.md").read_text(encoding="utf-8").lower()
    reddit = (ROOT / "docs" / "founder" / "wsbi-reddit-post.md").read_text(encoding="utf-8").lower()
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    founder_readme = (ROOT / "docs" / "founder" / "README.md").read_text(encoding="utf-8").lower()
    required_sections = [
        "portada ejecutiva",
        "decision",
        "auditoria",
        "te sirve para",
        "precio y viabilidad",
        "ws capital",
        "desorden organizado que tienes en tu cabeza",
    ]
    for section in required_sections:
        assert section in guide, f"Guide is missing section or phrase: {section}"

    reddit_required = [
        "la brecha es conocimiento y estructura",
        "piensa en ese desorden organizado que tienes en tu cabeza",
        "si te pide permisos, daselos",
        "que obtienes",
    ]
    for section in reddit_required:
        assert section in reddit, f"Reddit post is missing section or phrase: {section}"

    assert (ROOT / "docs" / "founder" / "assets" / "wsbi-public-guide.pdf").exists(), "PDF guide is missing."
    assert "docs/founder/assets/wsbi-public-guide.pdf" in root_readme, "README is missing a visible link to the PDF guide."
    assert "assets/wsbi-public-guide.pdf" in founder_readme, "Founder README is missing a visible link to the PDF guide."

    banned = ["launch the first", "partially_ready", "traceability", "service clarity demo", "luma preventa studio"]
    for term in banned:
        assert term not in guide, f"Guide leaked banned term: {term}"
        assert term not in reddit, f"Reddit post leaked banned term: {term}"

    print("Public guide quality checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

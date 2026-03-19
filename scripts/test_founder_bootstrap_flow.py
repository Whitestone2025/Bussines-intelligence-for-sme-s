#!/usr/bin/env python3
"""Checks for the founder bootstrap flow from an empty workspace."""

from __future__ import annotations

from serve_ui import empty_workspace_payload


def main() -> int:
    payload = empty_workspace_payload()

    project = payload.get("project", {})
    assert project.get("name") == "Ws B-I", "Expected Ws B-I project branding"

    onboarding = payload.get("onboarding", {})
    assert onboarding.get("headline"), "Expected onboarding headline"
    assert onboarding.get("summary"), "Expected onboarding summary"
    assert onboarding.get("github_repo_url") == "https://github.com/Whitestone2025/Bussines-intelligence-for-sme-s"
    starter_prompt = onboarding.get("starter_prompt", "").lower()
    assert "carpeta nueva" in starter_prompt, "Starter prompt should support a clean-folder bootstrap"
    assert "esta carpeta ya tiene informacion de mi negocio" in starter_prompt, "Starter prompt should support the in-place business-folder bootstrap"
    assert "analizala detenidamente antes de preguntarme cosas" in starter_prompt, "Starter prompt should require analysis before questions"
    assert "github.com" in starter_prompt, "Starter prompt should include the repository URL"
    assert onboarding.get("steps"), "Expected guided startup steps"
    assert any("revisa primero" in step.lower() or "analiza" in step.lower() for step in onboarding.get("steps", [])), "Guided steps should emphasize analysis before questions"
    assert onboarding.get("clean_install_steps"), "Expected clean-install steps"
    assert onboarding.get("success_state"), "Expected founder success criteria"

    assert payload.get("company") == {}, "Empty workspace should not pretend an active case"
    assert payload.get("companies") == [], "Empty workspace should not list companies"

    print("Founder bootstrap flow checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

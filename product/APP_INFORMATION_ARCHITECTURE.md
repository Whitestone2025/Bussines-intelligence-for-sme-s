# Ws B-I App Information Architecture

## 1. Purpose

This document defines the discovery-first information architecture for Ws B-I.
It exists to prevent the app from behaving like a static file browser or a marketer-style intake tool.

## 2. IA Principles

- Organize by research phase first, file structure second.
- Preserve traceability to repo artifacts.
- Keep company, service, ICP, channel, status, and confidence visible.
- Make uncertainty explicit.
- Let the user move from raw material to validated knowledge without losing context.
- Keep experiments downstream from readiness, not upstream from guesswork.

## 3. Primary Navigation

### Top-Level Navigation

1. Overview
2. Research
3. Sources
4. Evidence
5. Findings
6. Validation
7. Knowledge
8. Experiments
9. Patterns
10. Reports
11. Files

### Why This Navigation

- `Overview` shows progress and blockers.
- `Research` shows seeded companies and research stage.
- `Sources` is the raw material layer.
- `Evidence` is the structured truth layer.
- `Findings` is the inference layer.
- `Validation` is the human-correction queue.
- `Knowledge` is the assembled business understanding.
- `Experiments` is the lab, gated by readiness.
- `Patterns` is reusable memory.
- `Reports` is summary and recommendation.
- `Files` is an advanced fallback.

## 4. Screen Model

### 4.1 Overview

Purpose:

- orient the user,
- show readiness,
- show what is blocked,
- and highlight the next best action.

Must include:

- total research profiles,
- source count,
- evidence count,
- findings count,
- open validation questions,
- ready companies,
- recent experiments,
- recent reports,
- quick actions.

### 4.2 Research

Purpose:

- show all companies in discovery.

Subviews:

- Research list
- Research profile detail

Research detail must show:

- seed summary,
- website,
- competitors,
- available source material,
- current stage,
- readiness score,
- open questions,
- next recommended step.

### 4.3 Sources

Purpose:

- capture and inspect source assets before they become evidence.

Subviews:

- Source list
- Source detail

Required filters:

- company,
- source kind,
- status.

Source detail must show:

- title,
- origin,
- URL or local path,
- source body or notes,
- ingestion status,
- related findings or evidence.

### 4.4 Evidence

Purpose:

- show normalized, reusable market evidence.

Subviews:

- Evidence list
- Evidence detail
- Raw vs normalized comparison

Required filters:

- company,
- service,
- ICP,
- source type,
- channel,
- date.

Evidence detail must show:

- metadata,
- summary,
- verbatim quotes,
- observations,
- extracted candidate signals,
- links to related findings and experiments.

### 4.5 Findings

Purpose:

- expose what the system currently believes about the business.

Subviews:

- Finding list
- Finding detail

Required filters:

- company,
- category,
- status,
- confidence band.

Finding detail must show:

- category,
- statement,
- confidence,
- status,
- supporting evidence,
- related sources,
- suggested next action.

### 4.6 Validation

Purpose:

- ask the smallest useful set of questions.

Subviews:

- Question queue
- Question detail / answer form

Question detail must show:

- prompt,
- why it matters,
- related finding or entity,
- candidate options if available,
- recommended answer,
- answer status.

### 4.7 Knowledge

Purpose:

- show the assembled business documentation.

Subviews:

- Company detail
- Service detail
- ICP detail
- Channel detail

Each knowledge object must show:

- current value,
- status,
- confidence,
- evidence references,
- unresolved questions.

### 4.8 Experiments

Purpose:

- run experiments only after readiness requirements are met.

Subviews:

- Experiment list
- Experiment builder
- Experiment review

Experiment builder must include:

- readiness state,
- blocking reasons,
- company selector,
- service selector,
- ICP selector,
- channel selector,
- asset type,
- evidence picker,
- hypothesis field,
- baseline editor,
- variant editor.

Experiment review must include:

- brief,
- selected evidence,
- baseline,
- variant,
- evaluation summary,
- subscore comparison,
- decision,
- reasoning,
- result summary.

### 4.9 Patterns

Purpose:

- preserve communication intelligence that keeps proving useful.

Subviews:

- Winning patterns
- Anti-patterns
- Trust signals
- Repeated objections

Pattern detail must show:

- statement,
- category,
- company scope,
- supporting evidence or experiments,
- confidence,
- last touched date.

### 4.10 Reports

Purpose:

- summarize progress and recommend the next move.

Subviews:

- Report list
- Report detail

Report detail should show:

- readiness state,
- strongest learnings,
- unresolved gaps,
- recommended next questions or experiments.

### 4.11 Files

Purpose:

- preserve direct repo access without making it the primary experience.

## 5. Core Objects

### Research Profile

Fields:

- company_id
- seed_summary
- website
- competitors
- available_sources
- research_stage
- readiness_score
- open_questions_count

### Source Asset

Fields:

- source_id
- company_id
- source_kind
- origin
- title
- uri_or_path
- status
- summary
- body

### Evidence Entry

Fields:

- entry_id
- company_id
- service_id
- icp_id
- source_type
- channel
- date
- summary
- verbatim quotes
- observations
- extracted signals

### Finding

Fields:

- finding_id
- company_id
- category
- statement
- status
- confidence
- evidence refs
- source refs
- suggested action

### Validation Question

Fields:

- question_id
- company_id
- target entity type
- prompt
- question type
- candidate options
- recommended answer
- status
- answer

### Knowledge Entities

Company, Service, ICP, and Channel each expose:

- status
- confidence
- evidence refs
- source origin
- unresolved questions

### Readiness Check

Fields:

- company_id
- score
- status
- minimum evidence met
- source diversity met
- service defined
- icp defined
- channel defined
- insight density
- blocking reasons

## 6. Global Context

The persistent context bar should still expose:

- selected company
- selected service
- selected ICP
- selected channel

But the views should not assume that all of these exist from day one.

## 7. Primary User Journeys

### Journey A: Discovery Start

1. Open the app.
2. Click `Start Research`.
3. Add seed context.
4. See the research profile created immediately.

### Journey B: Import Reality

1. Open `Sources`.
2. Add notes, URLs, or transcript snippets.
3. Watch the source queue populate.

### Journey C: Build Understanding

1. Add normalized evidence.
2. Open `Findings`.
3. Review the system’s inferred understanding.
4. Open `Validation`.
5. Answer only the key questions.
6. Open `Knowledge` to see the assembled profile.

### Journey D: Earn Readiness

1. Open `Overview` or `Experiments`.
2. Review blockers.
3. Add missing evidence or answer missing questions.
4. Wait until the company is experiment-ready.

### Journey E: Run A Lab Cycle

1. Open `Experiments`.
2. Select a ready company.
3. Pick evidence and run one hypothesis.
4. Review outcome.
5. Save patterns and generate a report.

## 8. Empty-State Rules

Empty states should always explain:

- what is missing,
- why it matters,
- and the next recommended action.

Examples:

- No sources yet -> add source material.
- No evidence yet -> normalize notes or calls.
- No findings yet -> refresh research from current corpus.
- No validation questions -> either the company is already validated enough or more evidence is needed.
- Not ready for experiments -> show exact blockers.

## 9. Success Criteria For IA

The IA is successful when:

- a new user can understand the product flow in under 15 seconds,
- the app clearly separates raw material, inferred understanding, and validated knowledge,
- the user always knows what step comes next,
- and experiments feel like the last phase of research, not the first.

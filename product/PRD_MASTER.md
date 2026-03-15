# Ws B-I Product Requirements Document

## 1. Product Identity

### Product Name

Ws B-I

### One-Line Definition

Ws B-I is a local-first communication discovery system for service businesses that helps Codex turn raw business material into evidence, inferred business understanding, validated knowledge, and readiness-gated messaging experiments.

### Product Category

- Discovery-first communication research workspace
- Evidence-backed messaging intelligence system
- Local operating system for service-business communication

## 2. Vision

Most marketing systems ask the operator to behave like a marketer before the system has done any real investigation.
Ws B-I should reverse that relationship.

The product should let an operator start with minimal context and raw business material, then progressively build:

- a clearer understanding of what the business actually sells,
- a grounded picture of who the likely buyers are,
- a map of pains, outcomes, objections, trust signals, and category cliches,
- and a reusable body of communication intelligence that gets stronger over time.

The long-term vision is a system that treats communication understanding as an accumulative research process instead of a form-filling exercise.

## 3. Problem

### Core Problem

The current manual onboarding model assumes the operator already knows how to define services, ICPs, pains, objections, tone, and channels in marketer language.
That is unrealistic for founder-operators who want the system to help them discover those truths.

### Observed Failure Modes

- The onboarding process asks for strategic clarity before research has happened.
- The corpus stays under-populated because the first step is too abstract.
- Users are forced to guess ICPs and pains instead of deriving them from evidence.
- The system behaves more like a structured editor than an investigator.
- Experiments can be created before enough evidence exists to support them.

### Why Existing Tools Fail

- They ask for polished marketing inputs instead of raw business truth.
- They treat investigation as optional.
- They do not model uncertainty or confidence.
- They do not distinguish between inferred knowledge and validated knowledge.

## 4. Product Goal

Make it possible for one operator to start with only a few basic answers and some raw materials, then let Ws B-I incrementally build a useful communication corpus that supports stronger business understanding and better experiments.

## 5. Non-Goals

- Ws B-I will not train a local LLM.
- Ws B-I will not replace CRM, analytics, or ad platforms.
- Ws B-I will not require the user to define a complete marketing strategy up front.
- Ws B-I will not treat inferred findings as confirmed truth without validation.
- Ws B-I will not allow experiments to run before the corpus is sufficiently mature.

## 6. Primary Users

### Primary User

Founder-operator of one or more service businesses who:

- knows the business better than they know marketing language,
- has raw business material such as notes, calls, proposals, pages, chats, or testimonials,
- wants a system that discovers communication truth instead of demanding it,
- prefers local control and incremental research.

### Secondary User

Strategist or operator supporting a founder-led service business who wants a disciplined way to turn messy market inputs into evidence-backed messaging decisions.

## 7. Jobs To Be Done

### Functional Jobs

- Start a new company research thread with only basic context.
- Import source material without first classifying everything.
- Convert raw material into structured evidence.
- Infer likely services, ICPs, pains, outcomes, objections, and trust signals.
- Validate only the minimum set of unknowns needed to continue.
- Assemble living business documentation from evidence-backed findings.
- Run messaging experiments only when the system is ready.

### Emotional Jobs

- Reduce the feeling of “I have to become a marketer before I can use this.”
- Replace uncertainty with a visible path of discovery.
- Build trust that the system is learning from reality rather than inventing frameworks.

### Social Jobs

- Help a founder communicate like a grounded expert rather than a generic marketer.
- Build messaging that sounds human and credible instead of formulaic.

## 8. Product Principles

- Evidence before forms.
- Inference before manual classification.
- Validation before permanence.
- Confidence before certainty theater.
- Clarity before polish.
- Readiness before experimentation.
- Local-first by default.
- Small questions before large operator burden.

## 9. Core System Model

Ws B-I now follows a discovery-first loop:

1. capture a minimal seed,
2. ingest source material,
3. structure evidence,
4. infer provisional business understanding,
5. ask only the questions that matter,
6. assemble validated knowledge,
7. check readiness,
8. run one experiment,
9. preserve the learning.

The difference from the previous model is that company, service, ICP, and channel records are no longer assumed to be complete on day one.
They are assembled incrementally.

## 10. Functional Modules

### 10.1 Seed Capture

Collects the minimum information required to start research:

- company name,
- website,
- seed description of the business,
- competitors,
- known available source material.

### 10.2 Source Intake

Handles raw business materials before they become normalized evidence:

- notes,
- page URLs,
- transcripts,
- proposals,
- testimonials,
- competitor references,
- internal observations.

### 10.3 Evidence Structuring

Converts raw material into normalized evidence records that include:

- summaries,
- quotes,
- observations,
- metadata,
- source traceability.

### 10.4 Inference Engine

Generates provisional findings such as:

- likely service statements,
- likely ICP candidates,
- candidate pains,
- desired outcomes,
- objections,
- trust signals,
- market cliches and anti-patterns.

### 10.5 Validation Queue

Creates small, targeted questions for the operator only when a missing answer blocks useful progress.

### 10.6 Knowledge Assembly

Promotes validated or high-confidence findings into business records:

- company profile,
- service profiles,
- ICP profiles,
- channel profiles.

### 10.7 Readiness Gate

Determines whether the company has enough evidence and context quality to justify running communication experiments.

### 10.8 Experiment Lab

Runs evidence-backed messaging experiments only after readiness thresholds are met.

### 10.9 Pattern Memory

Stores durable learnings:

- winning patterns,
- anti-patterns,
- trust signals,
- recurring objections,
- channel-specific lessons,
- ICP-specific lessons.

### 10.10 Reporting Layer

Summarizes:

- what has been learned,
- what remains uncertain,
- how ready the company is,
- and what the next best action should be.

## 11. Data Model

### Core Entities

- Company
- Research Profile
- Source Asset
- Evidence Entry
- Finding
- Validation Question
- Service
- ICP
- Channel
- Experiment
- Evaluation
- Pattern
- Report
- Readiness Check

### Entity Relationships

- A company has one research profile.
- A company has many source assets.
- A company has many evidence entries.
- Findings are inferred from one or more source assets and/or evidence entries.
- Validation questions resolve uncertain findings into usable business context.
- Knowledge entities inherit confidence, status, and evidence references.
- Readiness checks depend on source depth, evidence depth, and validated context.
- Experiments require a passing readiness state.

### Status Model

Entities that can be inferred or validated use:

- `draft`
- `inferred`
- `needs_validation`
- `validated`
- `confirmed`
- `stale`

### Confidence Model

Every inferred or assembled entity should expose:

- `confidence` as a 0-1 float,
- `evidence_refs`,
- `source_origin`,
- `status`.

## 12. Key User Flows

### Flow A: Start Research

1. Enter company name.
2. Enter website.
3. Describe the business in plain language.
4. Add competitors.
5. List which materials are available.
6. Create the research profile.

### Flow B: Import Sources

1. Add one or more source assets.
2. Capture raw notes, URLs, or transcript snippets.
3. Store them without requiring full classification.

### Flow C: Structure Evidence

1. Convert source material or manual notes into normalized evidence.
2. Attach summaries, quotes, and observations.
3. Make the material searchable and reusable.

### Flow D: Review Findings

1. Let the system propose candidate services, ICPs, pains, outcomes, objections, and trust signals.
2. Review confidence and supporting evidence.
3. Promote only what is well-supported.

### Flow E: Answer Questions

1. See the smallest set of blocking questions.
2. Answer with a short choice or simple text.
3. Let the system update the knowledge base.

### Flow F: Reach Readiness

1. Review readiness score and blockers.
2. Add more evidence or answer pending questions.
3. Wait until the company becomes experiment-ready.

### Flow G: Run A Messaging Experiment

1. Choose asset type and context.
2. Select supporting evidence.
3. Create baseline and variant.
4. Evaluate with CQS.
5. Keep or discard.
6. Save the learning into patterns and reports.

## 13. UX Requirements

The product should feel like a research desk with a guided operator, not a marketing intake form.

### UX Goals

- A new user can begin with only basic business context.
- The app shows what it has inferred and how confident it is.
- The app asks a small number of useful questions instead of demanding full strategy.
- The user can see progress from raw material to usable knowledge.
- The experiment view explains why the system is or is not ready.

### UX Constraints

- Must run well on a MacBook Air M2 with 8 GB RAM.
- Must remain useful without any external API.
- Must preserve direct file access for Codex.
- Must degrade gracefully when evidence is sparse.

## 14. UI Requirements

The app must include these first-class views:

- Overview
- Research
- Sources
- Evidence
- Findings
- Validation
- Knowledge
- Experiments
- Patterns
- Reports
- Files

The app must also support:

- discovery-first onboarding,
- readiness visualization,
- contextual filtering,
- side-by-side experiment review,
- explicit status and confidence display,
- clear blockers and next steps.

## 15. Readiness Requirements

A company should be `ready` only when it meets a minimum threshold such as:

- at least 5 evidence entries,
- at least 2 source kinds,
- at least 1 service in `validated` or strong `inferred` state,
- at least 1 ICP in `validated` or strong `inferred` state,
- at least 1 channel in `validated` or strong `inferred` state,
- at least 3 pain/outcome/objection findings with evidence support.

When these conditions are not met, the UI must explain why and block experiment creation.

## 16. MVP Success Criteria

- A user can start research without defining a service or ICP manually.
- The system can accumulate source assets and evidence.
- The system can infer provisional findings and confidence.
- The system can generate validation questions and update knowledge.
- The system can compute readiness and gate experiments.
- The system can run one successful experiment after readiness is met.

## 17. Metrics

- Time to first research profile
- Time to first source asset
- Time to first normalized evidence entry
- Time to first validated service
- Time to first validated ICP
- Time to readiness
- Number of blocking questions per company
- Number of experiments run after readiness

## 18. Risks

- Weak heuristics may create noisy findings.
- Over-questioning may recreate operator burden.
- Under-questioning may freeze low-quality assumptions into the knowledge base.
- Readiness gates that are too strict may prevent progress.
- Readiness gates that are too weak may allow bad experiments.

## 19. Near-Term Roadmap

1. Introduce discovery-first onboarding and source intake.
2. Add inference and validation layers.
3. Assemble knowledge incrementally.
4. Gate experiments by readiness.
5. Improve finding quality and question quality over time.

## 20. Definition Of Success

Ws B-I is successful when a founder can begin with rough business inputs, watch the system progressively build a truthful corpus, answer only a handful of important questions, and then run experiments that are clearly grounded in evidence rather than guesswork.

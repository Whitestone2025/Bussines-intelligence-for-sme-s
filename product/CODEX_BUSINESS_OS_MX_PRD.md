# Codex Business OS MX Product Requirements Document

## 1. Product Identity

### Product Name

Codex Business OS MX

### One-Line Definition

Codex Business OS MX is a Codex-native, Mexico-first, evidence-driven business intelligence operating system that helps solopreneurs and small business operators discover viable opportunities, understand their market, design a stronger offer, and execute decisions with consulting-grade rigor.

### Product Category

- Business intelligence operating system for solopreneurs
- Research-to-decision workspace
- Codex-native strategic execution platform

## 2. Vision

Most founders in Mexico do not need generic startup advice.
They need a system that can help them answer the hard questions:

- Is this business worth starting or improving?
- Who will actually buy?
- What problem is urgent enough to pay for?
- What should I charge?
- Which local channels can generate trust quickly?
- What should I do in the next 30, 60, and 90 days?

Codex Business OS MX should act like a disciplined strategy team, a local market analyst, a financial sanity checker, and an execution planner that runs inside Codex.

The long-term goal is to give entrepreneurs in Mexico and later Latin America access to decision quality that feels closer to McKinsey, BCG, and Bain, but translated into the realities of owner-operators, smaller budgets, local channels, and messy real-world evidence.

## 3. Problem

### Core Problem

Existing founder tools fail because they usually do one of four things:

- ask for strategic clarity before any research has happened,
- generate polished output without evidence,
- optimize for investors and operators in the United States instead of Mexico,
- or depend on proprietary external research backends that reduce portability and local control.

### User Reality In Mexico

The target user often has:

- a rough business idea or an underperforming existing business,
- limited budget,
- partial evidence from sales chats, WhatsApp, social media, competitors, referrals, or local observation,
- no time to produce consultant-style inputs,
- and no trusted system that can turn messy signals into decisions.

### Failure Modes To Avoid

- long reports with weak recommendations,
- market sizing that is detached from local reality,
- strategic language that sounds impressive but cannot guide execution,
- no distinction between evidence, assumption, inference, and validated knowledge,
- no readiness gate before action,
- and no repeatable tests proving the system works.

## 4. Product Goal

Enable one operator to go from rough business context to validated business decisions through a repeatable loop:

1. start with minimal context,
2. ingest evidence,
3. infer business truth,
4. validate critical unknowns,
5. estimate market and viability,
6. prioritize actions,
7. generate execution-ready deliverables,
8. preserve the learning.

## 5. Primary Users

### Primary User

Mexico-based solopreneur or micro business operator who:

- wants to start a new business or improve an existing one,
- needs practical business intelligence, not theory,
- has limited resources,
- works across channels like WhatsApp, Instagram, Facebook, Google Maps, marketplaces, local referrals, and simple websites,
- and wants Codex to become the system of record for strategy and operating decisions.

### Secondary Users

- boutique advisors serving founder-led businesses,
- agencies serving SMBs in Mexico,
- operators evaluating adjacent expansion opportunities,
- later-stage Latin American users once localization expands.

## 6. Jobs To Be Done

### Functional Jobs

- Evaluate whether a business idea is viable in a specific Mexican market.
- Understand likely customer segments, pains, and buying triggers.
- Map competitors and local alternatives.
- Estimate TAM, SAM, SOM in a grounded way.
- Pressure-test pricing and unit economics.
- Recommend the best first acquisition channels.
- Produce an action plan with priorities and sequencing.
- Generate deliverables usable in partner, investor, or operator conversations.

### Emotional Jobs

- Replace fog with structured clarity.
- Reduce fear of wasting time on the wrong market or channel.
- Give the founder confidence that decisions are grounded, not invented.

### Social Jobs

- Help the founder communicate with authority.
- Help the founder sound specific and credible with customers, partners, and stakeholders.

## 7. Product Principles

- Evidence before opinion.
- Mexico-first before global-general.
- Decision-ready before presentation-ready.
- Inference before forcing manual classification.
- Validation before permanence.
- Readiness before recommendation.
- Simplicity for the operator, rigor in the system.
- Local-first and Codex-native by default.

## 7.1 Consulting Method Standard

Codex Business OS MX should borrow the useful working habits of top-tier consulting firms without copying enterprise theater that does not help a founder operator.

The system standard should be:

- structured problem solving instead of generic brainstorming,
- hypothesis-led analysis instead of disconnected facts,
- robust fact base instead of unsupported confidence,
- explicit assumptions instead of hidden leaps,
- realistic execution logic instead of slideware,
- and rapid learning loops instead of long reports with no operating consequence.

This means the system should:

- frame the decision question explicitly,
- make the current thesis visible,
- test the thesis against evidence and contrary evidence,
- compare at least one credible alternative when the decision is material,
- assess execution feasibility and implementation ownership,
- and explain why the recommendation wins.

## 8. Non-Goals

- The system will not depend on a proprietary research backend for core functionality.
- The system will not require the user to complete a large consultant-style intake before value appears.
- The system will not pretend confidence where evidence is weak.
- The system will not become a generic CRM, accounting system, or ad manager.
- The system will not optimize for enterprise procurement over founder usability.

## 9. Product Scope

### In Scope For V1

- codex-native intake and research orchestration,
- evidence capture and normalization,
- market discovery for Mexico,
- competitive intelligence,
- ICP and offer design,
- pricing and basic financial viability,
- decision engine and 30/60/90 planning,
- deliverable generation,
- local UI workspace,
- repeatable automated tests and release gates.

### Out Of Scope For V1

- live transactional accounting sync,
- direct paid media buying,
- CRM automation,
- cross-country LatAm rollout beyond architecture hooks,
- enterprise permissions and multi-tenant billing.

## 10. Product Architecture

The system should be designed as six layers.

### 10.1 Core Workspace Layer

Responsible for:

- canonical entities,
- repo-backed local storage,
- schema contracts,
- indexing,
- project memory,
- history and traceability,
- run state,
- report persistence.

### 10.2 Evidence And Research Layer

Responsible for:

- source intake,
- evidence normalization,
- quote and observation extraction,
- source linking,
- confidence scoring,
- freshness tracking.

### 10.3 Intelligence Engine Layer

Responsible for:

- market sizing,
- competitor mapping,
- ICP design,
- pain and outcome inference,
- pricing logic,
- viability calculations,
- risk detection,
- strategy synthesis.

### 10.4 Mexico Operating Layer

Responsible for:

- currency in MXN by default,
- Mexico geography assumptions,
- local buying channels,
- local trust and payment behaviors,
- tax and compliance awareness at a founder-sanity level,
- language defaults in Spanish with business-quality English as optional output.

### 10.5 Decision Layer

Responsible for:

- readiness assessment,
- priority ranking,
- next best action selection,
- decision memos,
- 30/60/90 planning,
- scenario comparison.

### 10.6 Delivery Layer

Responsible for:

- markdown reports,
- executive memo,
- deck outline,
- CSV/TSV tables,
- action checklists,
- downloadable artifacts.

The delivery layer must not optimize only for presentation polish.
Its job is to make the decision legible, defensible, and executable.

## 10.7 Deliverable Quality Standard

The minimum consulting-grade contract for important outputs is:

- `decision question`: what exact choice or uncertainty is being addressed,
- `current thesis`: the leading answer right now,
- `fact base`: evidence and benchmarks supporting the thesis,
- `assumptions`: what is still estimated or inferred,
- `options`: at least one alternative path when the decision is non-trivial,
- `recommendation`: the preferred path and why it wins,
- `risk view`: execution, market, pricing, competitor, and capability risks where relevant,
- `implementation`: immediate next actions, owners, timing, and success metrics where relevant.

If the available evidence is weak, the system should downgrade confidence and say what the next learning move should be instead of pretending certainty.

## 11. Canonical System Model

The system should distinguish between these object types:

- Input
- Source
- Evidence
- Assumption
- Finding
- Validation Question
- Validated Fact
- Market Model
- Competitor Record
- ICP Record
- Offer Record
- Pricing Model
- Financial Snapshot
- Risk Register
- Decision Memo
- Execution Plan
- Deliverable
- Test Fixture
- Quality Gate

### Required States

Objects that represent truth claims must support:

- draft
- inferred
- needs_validation
- validated
- confirmed
- stale
- rejected

### Confidence Model

Every major claim should carry:

- confidence score,
- evidence refs,
- source refs,
- last updated date,
- owner or origin,
- validation state.

## 12. Core User Flows

### Flow 1: Evaluate A New Business Idea

1. User provides rough business idea, location, target customer, budget, and any known constraints.
2. System asks only the missing questions required to produce a first hypothesis.
3. System generates a market and offer hypothesis pack.
4. System highlights weak assumptions.
5. System recommends next research actions or go/no-go direction.

### Flow 2: Improve An Existing Business

1. User provides current business summary and performance pain.
2. System ingests evidence from site, notes, chats, testimonials, and competitor references.
3. System identifies ICP, offer, channel, pricing, and trust gaps.
4. System outputs prioritized decisions and execution plan.

### Flow 3: Prepare For Launch

1. System uses validated market and offer data.
2. System selects a GTM path.
3. System generates channel-specific messaging and action plan.
4. System produces launch deliverables and measurable success criteria.

## 13. Capability Requirements

### 13.1 Intake

The intake system must:

- work with minimal required fields,
- support idea-stage and existing-business modes,
- support Spanish-first prompts,
- capture geography down to city/state when available,
- and classify missing data without overwhelming the user.

### 13.2 Evidence Intake

The evidence system must support:

- notes,
- URLs,
- transcripts,
- PDFs,
- screenshots,
- competitor pages,
- user quotes,
- operator observations,
- structured manual entries.

### 13.3 Market Discovery

The market module must:

- estimate TAM, SAM, SOM with explicit assumptions,
- separate top-down and bottom-up logic,
- note weak assumptions clearly,
- and prefer locally relevant evidence when the target geography is Mexico.

### 13.4 Competitive Intelligence

The competitor module must:

- identify direct, indirect, and substitute competitors,
- compare positioning, pricing, channels, and trust signals,
- extract white space and differentiation opportunities,
- and produce evidence-linked comparisons.

### 13.5 Customer And Offer Design

The system must:

- infer likely ICPs,
- identify pains, desired outcomes, objections, and trigger moments,
- propose offer statements and proof structures,
- and label what is inferred versus validated.

### 13.6 Pricing And Viability

The system must:

- produce basic pricing options,
- estimate cost and margin sanity ranges,
- compute simple unit economics,
- warn when assumptions are too weak,
- and distinguish between service, product, and marketplace businesses.

### 13.7 Decision Engine

The decision engine must:

- rank the highest-value next decisions,
- explain why,
- expose blockers,
- and avoid recommending execution when confidence is insufficient.

### 13.8 Execution Planning

The planning system must:

- generate a 30/60/90 plan,
- include milestones, dependencies, and success metrics,
- distinguish strategic work from immediate operator tasks,
- and propose sequencing grounded in readiness.

### 13.9 Deliverables

The system must produce:

- executive memo,
- business diagnosis,
- market brief,
- competitor table,
- ICP and offer pack,
- pricing options,
- financial snapshot,
- risk memo,
- 30/60/90 execution plan,
- deck-ready summary.

## 14. Mexico-First Requirements

The first production version must treat Mexico as the default operating context.

### Required Mexico Context

- MXN as default currency
- city/state aware market framing
- local channels:
  - WhatsApp
  - Instagram
  - Facebook
  - Google Maps
  - Mercado Libre when relevant
  - local referrals
  - marketplaces of services
- local trust signals:
  - testimonials
  - before/after proof
  - transparent process
  - clear deliverables
  - payment clarity
- local operational realities:
  - informal vs formal business setup
  - SAT and invoice sensitivity at a basic planning level
  - lower-ticket experimentation
  - limited marketing budget assumptions

### Language Requirements

- Internal system language may remain English where useful for consistency.
- User-facing outputs must support Spanish-first.
- System must avoid stiff translation and prefer natural Mexican business language.

## 15. Data And File Contracts

### Repo-Backed Contracts

The system should maintain project-owned folders for:

- companies
- research
- sources
- evidence
- findings
- validation
- market models
- competitors
- pricing
- financials
- risks
- decisions
- plans
- deliverables
- tests
- reports

### File Standards

- JSON for structured canonical objects
- Markdown for narrative outputs
- TSV or CSV for comparison and tabular export
- Deterministic filenames and IDs
- No silent overwrites without traceability

## 16. Quality Model

The product must define quality at four levels:

### 16.1 Truth Quality

- claims are evidence-backed,
- assumptions are visible,
- and confidence is explicit.

### 16.2 Decision Quality

- recommendations are specific,
- tradeoffs are visible,
- and the next action is clear.

### 16.3 Product Quality

- flows are reproducible,
- artifacts are consistent,
- and the system degrades gracefully with partial data.

### 16.4 Local Relevance Quality

- Mexico-specific realities are respected,
- local channels are not treated as afterthoughts,
- and output is useful for the actual operator.

## 17. Test Strategy

The product is not done without a full quality system.

### 17.1 Test Pyramid

- Unit tests for pure logic, scoring, schema validation, and pricing calculations
- Contract tests for JSON shapes and file naming rules
- Integration tests for API and orchestration flows
- Golden tests for deterministic output structures
- End-to-end tests for user journeys
- Manual QA scripts for final release review

### 17.2 Required Automated Test Suites

- schema validation suite
- intake normalization suite
- evidence ingestion suite
- market model suite
- competitor extraction suite
- ICP and offer synthesis suite
- pricing and financial sanity suite
- readiness and decision ranking suite
- artifact generation suite
- end-to-end Mexico journey suite

### 17.3 Golden Journeys

The system must include at least these fixture-driven flows:

- new idea in Mexico City
- existing local service business with weak positioning
- ecommerce or catalog business with pricing confusion
- operator with sparse evidence and high uncertainty

### 17.4 Regression Rules

- Every bug that affects output quality must produce a new test.
- Every release candidate must run the full automated suite.
- No story is complete without acceptance evidence.

## 18. Non-Functional Requirements

### Performance

- Local-first operations should remain usable on a typical developer machine.
- Indexing and synthesis must support incremental refresh.
- Long-running research tasks must expose visible progress.

### Reliability

- Partial failures must not corrupt core company records.
- Interrupted runs must be resumable.
- Deliverable generation must be deterministic where expected.

### Security And Privacy

- The system must avoid storing secrets in repo artifacts.
- Sensitive local business inputs should remain local by default.
- Any external fetch or browse activity must be explicit and traceable.

### Maintainability

- Modules must be separable and testable.
- Schemas must be versionable.
- Core flows must be scriptable from Codex.

## 19. Success Metrics

### User Outcome Metrics

- time to first useful diagnosis,
- time to first actionable 30/60/90 plan,
- percentage of sessions ending with a clear next action,
- usefulness score from real Mexican founder pilots.

### Product Quality Metrics

- end-to-end pass rate,
- regression rate,
- artifact consistency score,
- percentage of recommendations with evidence refs.

### Business Quality Metrics

- recommendation adoption rate,
- perceived decision clarity,
- reduction in founder uncertainty,
- number of viable no-go decisions caught early.

## 20. Final Deliverables For V1

V1 is only complete when the repo contains:

- a stable codex-native core workspace,
- canonical schemas for all major business entities,
- a working evidence ingestion and findings pipeline,
- market, competitor, ICP, offer, pricing, and viability modules,
- a Mexico-first decision engine,
- a 30/60/90 planner,
- a deliverable generator,
- a local UI,
- a full automated test harness,
- fixture-backed end-to-end journeys,
- and release readiness documentation.

## 21. Release Gates

The product must not be considered production-ready unless:

- all planned automated test suites pass,
- all golden journeys pass,
- the full end-to-end local flow passes,
- no blocker remains in the release checklist,
- and a manual review confirms output quality, local relevance, and operator usefulness.

## 22. Definition Of Done

The product is done for V1 only when:

- a founder in Mexico can start with rough business context,
- the system turns that into evidence-backed strategic intelligence,
- the output is usable without a consultant translating it,
- the next best actions are obvious,
- and the quality is proven by tests rather than claimed in prose.

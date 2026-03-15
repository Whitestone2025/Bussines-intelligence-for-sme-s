# Ws B-I

Ws B-I is a Codex-native business intelligence system for founders, solopreneurs, and small business operators in Mexico.
Its job is to help a business move from rough context to evidence, decisions, plans, and a local frontend that the owner can review with Codex.

## Choose Your Path

### I am a business owner

Start here:

- [Founder Guide](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/docs/founder/README.md)
- [Prepare Your Information](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/docs/founder/01-preparar-informacion.md)
- [Work With Codex](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/docs/founder/02-trabajar-con-codex.md)
- [See Your Frontend](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/docs/founder/03-ver-tu-frontend.md)
- [Founder FAQ](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/docs/founder/04-faq.md)

### I am technical and want to modify the system

Start here:

- [Technical Guide](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/docs/technical/README.md)
- [Architecture](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/docs/technical/01-arquitectura.md)
- [Setup And Commands](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/docs/technical/02-setup-y-comandos.md)
- [How To Modify](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/docs/technical/03-como-modificar.md)
- [Validation](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/docs/technical/04-validacion.md)

## What Ws B-I Does

- starts from minimal business context,
- stores source material and evidence,
- infers business signals and open questions,
- validates key unknowns,
- generates market, pricing, decision, plan, and deliverable outputs,
- and serves a local frontend for case review.

## Default Founder Prompt

If you are using Codex as a business owner, start with this:

```text
Corre Ws B-I para mi negocio y guíame paso a paso hasta que pueda ver mi información en el frontend. No soy técnico, así que hazte cargo de los comandos y explícame solo lo necesario.
```

## Product Sources Of Truth

- [CODEX_BUSINESS_OS_MX_PRD.md](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/product/CODEX_BUSINESS_OS_MX_PRD.md)
- [PRD_MASTER.md](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/product/PRD_MASTER.md)
- [APP_INFORMATION_ARCHITECTURE.md](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/product/APP_INFORMATION_ARCHITECTURE.md)
- [program.md](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/program.md)

## Core Commands

Run the frontend:

```bash
python3 scripts/serve_ui.py
```

Run the main verification gate:

```bash
python3 scripts/release_check.py
```

Run the discovery flow:

```bash
python3 scripts/test_discovery_flow.py
```

# Ws B-I

Ws B-I is a Codex-native business intelligence system for founders, solopreneurs, and small business operators in Mexico.
Its job is to help a business move from rough context to evidence, decisions, plans, and a local frontend that the owner can review with Codex.

## Choose Your Path

### I am a business owner

Start here:

- [Founder Guide](docs/founder/README.md)
- [Clean Install On Another Computer](docs/founder/05-instalacion-limpia.md)
- [Prepare Your Information](docs/founder/01-preparar-informacion.md)
- [Work With Codex](docs/founder/02-trabajar-con-codex.md)
- [See Your Frontend](docs/founder/03-ver-tu-frontend.md)
- [Founder FAQ](docs/founder/04-faq.md)

### I am technical and want to modify the system

Start here:

- [Technical Guide](docs/technical/README.md)
- [Clean Install Readiness](docs/technical/05-prueba-en-instalacion-limpia.md)
- [Architecture](docs/technical/01-arquitectura.md)
- [Setup And Commands](docs/technical/02-setup-y-comandos.md)
- [How To Modify](docs/technical/03-como-modificar.md)
- [Validation](docs/technical/04-validacion.md)

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
Quiero usar Ws B-I para mi negocio. Toma el repositorio desde https://github.com/Whitestone2025/Bussines-intelligence-for-sme-s, prepáralo en una carpeta nueva, guíame paso a paso, hazme solo las preguntas necesarias sobre mi empresa, carga mi caso y abre el frontend cuando esté listo. No soy técnico, así que hazte cargo de los comandos y explícame solo lo necesario.
```

## Product Sources Of Truth

- [CODEX_BUSINESS_OS_MX_PRD.md](product/CODEX_BUSINESS_OS_MX_PRD.md)
- [PRD_MASTER.md](product/PRD_MASTER.md)
- [APP_INFORMATION_ARCHITECTURE.md](product/APP_INFORMATION_ARCHITECTURE.md)
- [program.md](program.md)

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

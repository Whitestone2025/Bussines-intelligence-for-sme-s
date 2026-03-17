# Ws B-I

Ws B-I es un sistema de inteligencia de negocio pensado para emprendedores, duenos de PyME y solopreneurs en Mexico.
Su objetivo es tomar contexto real del negocio, convertirlo en evidencia, generar decisiones y abrir un frontend local que puedas revisar junto con Codex.

## Elige tu ruta

### Soy dueno de negocio

Empieza aqui:

- [Guia para founders](docs/founder/README.md)
- [Instalacion limpia en otra computadora](docs/founder/05-instalacion-limpia.md)
- [Prepara tu informacion](docs/founder/01-preparar-informacion.md)
- [Trabaja con Codex](docs/founder/02-trabajar-con-codex.md)
- [Ve tu frontend](docs/founder/03-ver-tu-frontend.md)
- [Preguntas frecuentes](docs/founder/04-faq.md)

### Soy tecnico y quiero modificar el sistema

Empieza aqui:

- [Guia tecnica](docs/technical/README.md)
- [Prueba en instalacion limpia](docs/technical/05-prueba-en-instalacion-limpia.md)
- [Arquitectura](docs/technical/01-arquitectura.md)
- [Setup y comandos](docs/technical/02-setup-y-comandos.md)
- [Como modificar](docs/technical/03-como-modificar.md)
- [Validacion](docs/technical/04-validacion.md)

## Que hace Ws B-I

- arranca con contexto minimo del negocio,
- guarda material fuente y evidencia,
- infiere senales, riesgos y preguntas abiertas,
- valida los desconocidos importantes,
- genera salidas de mercado, precio, decision, plan y entregables,
- y sirve un frontend local para revisar el caso.

## Prompt recomendado para founders

Si vas a usar Codex como dueno de negocio, empieza con este mensaje:

```text
Quiero usar Ws B-I para mi negocio. Toma el repositorio desde https://github.com/Whitestone2025/Bussines-intelligence-for-sme-s, preparalo en una carpeta nueva, guiame paso a paso, hazme solo las preguntas necesarias sobre mi empresa, carga mi caso y abre el frontend cuando este listo. No soy tecnico, asi que hazte cargo de los comandos y explicame solo lo necesario.
```

## Fuentes de verdad del producto

- [CODEX_BUSINESS_OS_MX_PRD.md](product/CODEX_BUSINESS_OS_MX_PRD.md)
- [PRD_MASTER.md](product/PRD_MASTER.md)
- [APP_INFORMATION_ARCHITECTURE.md](product/APP_INFORMATION_ARCHITECTURE.md)
- [program.md](program.md)

## Comandos base

Levantar el frontend:

```bash
python3 scripts/serve_ui.py
```

Correr el gate principal:

```bash
python3 scripts/release_check.py
```

Correr el flujo de discovery:

```bash
python3 scripts/test_discovery_flow.py
```

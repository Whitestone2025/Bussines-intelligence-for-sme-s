---
project: Ws B-I
runId: wsbi-public-case-v2
commitPolicy: "no-commit"
qualityChecks:
  - python3 -m compileall scripts
  - node --check ui/app.js
  - python3 scripts/codex-ground-loop/build_prd.py tasks/ground-loop/wsbi-public-case-v2/plan.md tasks/ground-loop/wsbi-public-case-v2/prd.json
  - python3 scripts/test_reasoning_quality.py
  - python3 scripts/test_case_view_model.py
  - python3 scripts/test_public_guide_quality.py
  - python3 scripts/release_check.py
---

# Goal

Reemplazar el caso demo publico actual por un caso compuesto mucho mas especifico, plausible y util para founders; usarlo para validar que Ws B-I produce una lectura menos generica, mas trazable y mas cercana a un consultor estrategico serio, y regenerar la guia publica con capturas nuevas y verificadas.

## Story: P1 | Auditoria Del Caso Publico Actual

### Goal

Documentar por que el caso `guide-demo-lab` y la guia actual no son suficientemente especificos, utiles ni publicables como demostracion de alto nivel.

### Deliverables

- data/companies/guide-demo-lab/company.json
- data/decisions/guide-demo-lab/guide-demo-lab-go-to-market-memo.json
- data/research/guide-demo-lab/guide-demo-lab-clarity-sprint-offer.json
- output/pdf/wsbi-founder-guide-understanding.md
- tasks/ground-loop/wsbi-public-case-v2/progress.txt

### Acceptance

- Queda registrada una auditoria corta de problemas reales de idioma, genericidad, credibilidad y utilidad.
- El loop deja claro si el problema nace del caso, de los motores o de ambos.

### Checks

- python3 scripts/test_public_guide_quality.py

## Story: P2 | Diseno Del Nuevo Caso Publico Compuesto

### Goal

Disenar un caso compuesto y publicable, basado en una categoria de servicio concreta y apoyado en referencias publicas reales cuando haga falta.

### Deliverables

- data/companies/public-case-real-estate-studio/company.json
- data/research/public-case-real-estate-studio/profile.json
- data/sources/public-case-real-estate-studio/
- tasks/ground-loop/wsbi-public-case-v2/progress.txt

### Acceptance

- El nuevo caso define una empresa de servicio clara, buyer claro, geografia clara y problema comercial tangible.
- La naturaleza del caso queda explicada como caso compuesto basado en referencias publicas, no como empresa real ficticia disfrazada.

### Checks

- python3 scripts/test_language_purity.py

## Story: P3 | Corpus Y Evidencia Del Nuevo Caso

### Goal

Construir un corpus mas rico y especifico para el caso nuevo, con fuentes, evidencia y competidores suficientemente concretos para forzar mejores salidas del sistema.

### Deliverables

- data/corpus/raw/public-case-real-estate-studio/
- data/corpus/clean/public-case-real-estate-studio/
- data/evidence/public-case-real-estate-studio/
- data/competitors/public-case-real-estate-studio/
- data/findings/public-case-real-estate-studio/

### Acceptance

- El caso tiene varias fuentes y evidencias concretas, no solo frases abstractas.
- Las objeciones, pains y trust signals son mas especificos al servicio y al buyer.

### Checks

- python3 scripts/test_non_generic_outputs.py
- python3 scripts/test_reasoning_quality.py

## Story: P4 | Ajuste De Motores Contra El Caso Nuevo

### Goal

Usar el nuevo caso como prueba dura para detectar y corregir cualquier salida todavia generica o residual en cliente, oferta, mercado o decision.

### Deliverables

- scripts/customer_model.py
- scripts/decision_engine.py
- scripts/market_model.py
- scripts/financials.py
- scripts/serve_ui.py

### Acceptance

- El caso nuevo ya no dispara promesas plantilla ni recomendaciones intercambiables.
- Si algo sigue incierto, el sistema lo declara con cautela en vez de rellenar.

### Checks

- python3 scripts/test_customer_offer_engine.py
- python3 scripts/test_decision_engine.py
- python3 scripts/test_market_model.py
- python3 scripts/test_case_specific_decision.py

## Story: P5 | Regeneracion Del Caso Ejecutivo Completo

### Goal

Regenerar empresa, findings, pricing, mercado, decision, plan y reportes del nuevo caso para que el frontend muestre una lectura ejecutiva realmente defendible.

### Deliverables

- data/market/public-case-real-estate-studio/
- data/pricing/public-case-real-estate-studio/
- data/financials/public-case-real-estate-studio/
- data/decisions/public-case-real-estate-studio/
- data/plans/public-case-real-estate-studio/
- data/reports/public-case-real-estate-studio/

### Acceptance

- El caso queda visible de punta a punta en el sistema.
- Precio, mercado, decision y plan se leen como negocio concreto y no como framework.

### Checks

- python3 scripts/test_case_view_model.py
- python3 scripts/test_ui_workspace_flow.py

## Story: P6 | Capturas Reales Del Frontend

### Goal

Abrir el frontend con el nuevo caso y tomar capturas reales de las vistas clave que luego iran a la guia publica.

### Deliverables

- output/playwright/public-case-real-estate-studio-overview.png
- output/playwright/public-case-real-estate-studio-customer.png
- output/playwright/public-case-real-estate-studio-market.png
- output/playwright/public-case-real-estate-studio-pricing.png
- output/playwright/public-case-real-estate-studio-decision.png
- output/playwright/public-case-real-estate-studio-audit.png

### Acceptance

- Las capturas salen del sistema corriendo de verdad.
- El contenido visible en pantallas ya no se siente generico ni contaminado por ingles.

### Checks

- node --check ui/app.js

## Story: P7 | Nueva Guia Publica Basada En El Caso Nuevo

### Goal

Reescribir la guia corta para que explique el sistema a traves del caso nuevo y no a traves de una descripcion abstracta del producto.

### Deliverables

- output/pdf/wsbi-founder-guide-understanding.md
- output/pdf/wsbi-founder-guide-understanding.pdf

### Acceptance

- La guia explica que negocio es, que encontro el sistema, que decision propone y por que eso ayuda al founder.
- La guia declara con honestidad que es un caso compuesto basado en referencias publicas.

### Checks

- python3 scripts/test_founder_usefulness.py
- python3 scripts/test_public_guide_quality.py

## Story: P8 | Verificacion Final Y Cierre Del Loop

### Goal

Correr la bateria completa, verificar que el caso nuevo aguanta como demo publica y cerrar el Ralph loop con estado persistido.

### Deliverables

- tasks/ground-loop/wsbi-public-case-v2/progress.txt
- tasks/ground-loop/wsbi-public-case-v2/prd.json
- tasks/ground-loop/wsbi-public-case-v2/last-message.txt
- data/reports/release-readiness/

### Acceptance

- El loop queda cerrado con todas las historias completadas.
- La suite pasa y la guia nueva refleja el mejor estado real del sistema.
- El caso nuevo sirve como prueba de especificidad, trazabilidad y utilidad del producto.

### Checks

- python3 -m compileall scripts
- node --check ui/app.js
- python3 scripts/test_customer_offer_engine.py
- python3 scripts/test_reasoning_quality.py
- python3 scripts/test_decision_engine.py
- python3 scripts/test_market_model.py
- python3 scripts/test_pricing_financials.py
- python3 scripts/test_case_view_model.py
- python3 scripts/test_ui_workspace_flow.py
- python3 scripts/test_language_purity.py
- python3 scripts/test_founder_usefulness.py
- python3 scripts/test_non_generic_outputs.py
- python3 scripts/test_case_specific_decision.py
- python3 scripts/test_public_guide_quality.py
- python3 scripts/release_check.py
- scripts/codex-ground-loop/ground-loop.sh tasks/ground-loop/wsbi-public-case-v2

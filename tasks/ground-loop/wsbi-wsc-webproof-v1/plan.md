---
project: Ws B-I
runId: wsbi-wsc-webproof-v1
commitPolicy: "no-commit"
qualityChecks:
  - python3 -m compileall scripts
  - node --check ui/app.js
  - python3 scripts/codex-ground-loop/build_prd.py tasks/ground-loop/wsbi-wsc-webproof-v1/plan.md tasks/ground-loop/wsbi-wsc-webproof-v1/prd.json
  - python3 scripts/test_reasoning_quality.py
  - python3 scripts/test_case_view_model.py
  - python3 scripts/test_ui_workspace_flow.py
  - python3 scripts/release_check.py
---

# Goal

Usar `https://wsc.lat/` como prueba real y dura del sistema completo de Ws B-I, partiendo solo de la web publica, para validar si el flujo actual sabe:

- extraer evidencia sin inventar;
- preservar ambiguedad cuando el negocio aun no esta del todo definido;
- estructurar problema, opciones, criterios, recomendacion y roadmap sin colapsar en una sola tactica;
- y producir entregables y UI utiles para pensar un negocio real, no solo para resumir un sitio web.

## Story: W1 | Captura Y Grounding Del Sitio

### Goal

Recolectar y estructurar toda la evidencia publica visible de `wsc.lat` sin interpretarla todavia como verdad cerrada del negocio.

### Deliverables

- data/companies/wsc-lat/
- data/sources/wsc-lat/
- data/evidence/wsc-lat/
- scripts/test_wsc_traceability.py
- tasks/ground-loop/wsbi-wsc-webproof-v1/progress.txt

### Acceptance

- Se captura el sitio con trazabilidad suficiente para distinguir entre texto literal, claims, promesas, unidades activas y vacios de informacion.
- Ningun dato clave del caso queda inventado o inferido sin marcarse como tal.

### Checks

- python3 scripts/test_wsc_traceability.py

## Story: W2 | Intake Web-Only Y Reglas De Cautela

### Goal

Adaptar el flujo para casos que arrancan solo con una web publica y no con entrevistas, pricing o evidencia interna.

### Deliverables

- scripts/intake.py
- scripts/serve_ui.py
- scripts/test_wsc_no_hallucination.py
- scripts/test_wsc_ambiguity_preservation.py

### Acceptance

- El sistema distingue explicitamente entre lo que sabe, lo que infiere y lo que no sabe.
- El readiness y los findings no se sobrepromueven solo por tener una web llamativa.

### Checks

- python3 scripts/test_wsc_no_hallucination.py
- python3 scripts/test_wsc_ambiguity_preservation.py

## Story: W3 | Hallazgos Especificos Del Caso WS Capital

### Goal

Generar hallazgos utiles y no genericos sobre WS Capital a partir de la web, sin colapsar AI lab, venture capital, open source platform y operator model en una sola categoria falsa.

### Deliverables

- data/findings/wsc-lat/
- scripts/test_wsc_site_specificity.py
- scripts/test_non_generic_outputs.py

### Acceptance

- Los findings identifican tensiones reales del caso.
- El sistema refleja la mezcla de identidades del negocio sin simplificarla artificialmente demasiado pronto.

### Checks

- python3 scripts/test_wsc_site_specificity.py
- python3 scripts/test_non_generic_outputs.py

## Story: W4 | Problem Structuring Web-Only

### Goal

Construir un problema central y un caso para cambiar usando solo evidencia web publica y dejando visibles las ambiguedades del caso.

### Deliverables

- scripts/decision_engine.py
- scripts/render_report.py
- scripts/test_problem_structuring_quality.py
- scripts/test_wsc_ambiguity_preservation.py

### Acceptance

- El problema central de WS Capital queda expresado como tension estrategica y no como slogan.
- El sistema muestra claramente que partes del caso siguen siendo hipotesis.

### Checks

- python3 scripts/test_problem_structuring_quality.py
- python3 scripts/test_wsc_ambiguity_preservation.py

## Story: W5 | Alternativas Estrategicas Reales Para WSC

### Goal

Forzar al sistema a producir rutas reales para WSC en vez de una sola accion tactica.

### Deliverables

- scripts/decision_engine.py
- data/decisions/wsc-lat/
- scripts/test_case_specific_decision.py
- scripts/test_no_single_action_collapse.py
- scripts/test_wsc_strategic_breadth.py

### Acceptance

- El caso WSC produce entre 2 y 4 rutas plausibles.
- La recomendacion explica por que gana una ruta y que condiciones la podrian invalidar.

### Checks

- python3 scripts/test_case_specific_decision.py
- python3 scripts/test_no_single_action_collapse.py
- python3 scripts/test_wsc_strategic_breadth.py

## Story: W6 | Deliverables Corporativos Para Un Caso Web-Only

### Goal

Generar una suite de entregables corporativos para WSC que sirva para decidir mejor con informacion incompleta, no para aparentar certeza.

### Deliverables

- data/deliverables/wsc-lat/
- scripts/render_report.py
- scripts/test_corporate_deliverables_quality.py
- scripts/test_wsc_case_usefulness.py

### Acceptance

- Los documentos explican problema, opciones, criterio, riesgos y roadmap.
- Los documentos declaran donde hay evidencia insuficiente.

### Checks

- python3 scripts/test_corporate_deliverables_quality.py
- python3 scripts/test_wsc_case_usefulness.py

## Story: W7 | UI Ejecutiva Para Un Caso Incompleto Pero Real

### Goal

Verificar que la sala ejecutiva de Ws B-I sepa mostrar un caso real con vacios, ambiguedades y arquitectura estrategica sin volverlo humo.

### Deliverables

- scripts/serve_ui.py
- ui/app.js
- scripts/test_case_view_model.py
- scripts/test_ui_workspace_flow.py

### Acceptance

- El founder puede leer por pantalla que se sabe, que no se sabe, que alternativas existen y que decision provisional tiene mas sentido.
- La UI no exagera confianza ni resume el caso como una sola jugada.

### Checks

- node --check ui/app.js
- python3 scripts/test_case_view_model.py
- python3 scripts/test_ui_workspace_flow.py

## Story: W8 | Correccion Iterativa Del Motor Con WSC Como Stress Test

### Goal

Usar el caso WSC para detectar si todavia hay genericidad, falsa seguridad, angostamiento de alternativas o microcopy demasiado consultor sin sustancia.

### Deliverables

- scripts/customer_model.py
- scripts/decision_engine.py
- scripts/render_report.py
- scripts/serve_ui.py
- tasks/ground-loop/wsbi-wsc-webproof-v1/progress.txt

### Acceptance

- Si la salida sigue siendo generica o sobreconcluyente, se corrige la logica antes de pasar a guia o demo publica.
- El progreso deja documentado que se ajusto y por que.

### Checks

- python3 scripts/test_reasoning_quality.py
- python3 scripts/test_wsc_no_hallucination.py
- python3 scripts/test_wsc_case_usefulness.py

## Story: W9 | Validacion Final Del Caso WSC

### Goal

Regenerar el caso completo y validarlo como prueba seria del sistema.

### Deliverables

- data/companies/wsc-lat/
- data/decisions/wsc-lat/
- data/plans/wsc-lat/
- data/deliverables/wsc-lat/
- data/reports/wsc-lat/
- scripts/test_wsc_traceability.py
- scripts/test_wsc_site_specificity.py
- scripts/test_wsc_strategic_breadth.py

### Acceptance

- El caso WSC muestra problema, opciones, criterios y roadmap.
- La recomendacion ya no se reduce a una sola tarea.
- El sistema conserva cautela donde la web no basta para concluir.

### Checks

- python3 scripts/test_wsc_traceability.py
- python3 scripts/test_wsc_site_specificity.py
- python3 scripts/test_wsc_strategic_breadth.py
- python3 scripts/test_wsc_case_usefulness.py

## Story: W10 | Guia Derivada Solo Si El Caso Aguanta

### Goal

Si y solo si el caso WSC final pasa bien, generar una guia corta que muestre como Ws B-I piensa con una sola web real y que decisiones ayuda a tomar.

### Deliverables

- output/pdf/wsbi-wsc-webproof-guide.md
- output/pdf/wsbi-wsc-webproof-guide.pdf
- scripts/test_public_guide_quality.py
- scripts/test_founder_usefulness.py

### Acceptance

- La guia muestra utilidad real de negocio.
- La guia deja claro que el caso parte solo de una web publica y por eso mantiene hipotesis abiertas donde corresponde.
- Si el caso no aguanta, esta historia no se marca como completa.

### Checks

- python3 scripts/test_public_guide_quality.py
- python3 scripts/test_founder_usefulness.py

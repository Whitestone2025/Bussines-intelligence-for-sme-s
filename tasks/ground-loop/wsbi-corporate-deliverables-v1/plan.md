---
project: Ws B-I
runId: wsbi-corporate-deliverables-v1
commitPolicy: "no-commit"
qualityChecks:
  - python3 -m compileall scripts
  - node --check ui/app.js
  - python3 scripts/codex-ground-loop/build_prd.py tasks/ground-loop/wsbi-corporate-deliverables-v1/plan.md tasks/ground-loop/wsbi-corporate-deliverables-v1/prd.json
  - python3 scripts/test_reasoning_quality.py
  - python3 scripts/test_case_view_model.py
  - python3 scripts/test_public_guide_quality.py
  - python3 scripts/release_check.py
---

# Goal

Reparar el flujo completo de Ws B-I para que deje de colapsar la estrategia en una sola accion tactica, adopte una logica mas parecida a consultoria corporativa seria, y produzca entregables ejecutivos comparables a un trabajo hypothesis-driven al estilo McKinsey o BCG: problema estructurado, alternativas reales, criterios, recomendacion, riesgos, roadmap e implicaciones.

## Story: C1 | Auditoria Del Flujo Estrategico Actual

### Goal

Mapear de punta a punta donde el sistema pierde riqueza del caso y termina reduciendo toda la lectura a una sola jugada operativa.

### Deliverables

- scripts/decision_engine.py
- scripts/planner.py
- scripts/render_report.py
- scripts/serve_ui.py
- tasks/ground-loop/wsbi-corporate-deliverables-v1/progress.txt

### Acceptance

- Queda documentado donde el flujo actual colapsa de evidencia a accion sin pasar por arquitectura estrategica.
- Se identifican cuellos de botella concretos en decision, plan, deliverables y vista ejecutiva.

### Checks

- python3 scripts/test_reasoning_quality.py

## Story: C2 | Benchmark Externo De Metodologias Corporativas

### Goal

Investigar y sintetizar marcos publicos y oficiales de McKinsey, BCG y consultoria strategica similar para definir que debe contener una recomendacion ejecutiva seria.

### Deliverables

- tasks/ground-loop/wsbi-corporate-deliverables-v1/progress.txt
- scripts/decision_engine.py
- scripts/render_report.py

### Acceptance

- El loop deja trazados los marcos y conceptos que se adoptaran: problem structuring, issue tree, hypothesis-driven, where to play, how to win, right to win, initiative roadmap, case for change.
- Se distingue claramente que se toma como inspiracion metodologica y que no se pretende copiar literalmente.

### Checks

- python3 scripts/test_public_guide_quality.py

## Story: C3 | Redefinicion Del Modelo Canonico De Estrategia

### Goal

Crear un modelo de datos estrategico intermedio entre evidencia y accion para que el sistema piense en tesis, opciones, criterios, riesgos y dependencias antes de emitir una recomendacion.

### Deliverables

- scripts/decision_engine.py
- scripts/render_report.py
- scripts/planner.py
- scripts/test_schema_contracts.py

### Acceptance

- Existe un stack canonico con bloques como: problema, caso para cambiar, where to play, how to win, right to win, opciones, criterios, what must be true, no-regret moves y roadmap.
- El sistema deja de depender solo de `recommended_action` y `next_steps`.

### Checks

- python3 scripts/test_schema_contracts.py

## Story: C4 | Decision Engine Con Alternativas Reales

### Goal

Reescribir la logica de decision para producir opciones estrategicas reales, evaluarlas y recomendar una tesis, no solo una accion unica.

### Deliverables

- scripts/decision_engine.py
- scripts/test_decision_engine.py
- scripts/test_case_specific_decision.py
- scripts/test_no_single_action_collapse.py

### Acceptance

- Cada caso produce entre 2 y 4 alternativas estrategicas reales.
- La recomendacion explicita por que gana una opcion y que condiciones la invalidarian.
- La salida ya no se reduce a "haz una landing" o equivalente.

### Checks

- python3 scripts/test_decision_engine.py
- python3 scripts/test_case_specific_decision.py
- python3 scripts/test_no_single_action_collapse.py

## Story: C5 | Problem Structuring Y Tesis Ejecutiva

### Goal

Incorporar una capa de problem structuring para que los deliverables expliquen problema central, tensiones, hechos, hipotesis y what-must-be-true antes de bajar a accion.

### Deliverables

- scripts/render_report.py
- scripts/serve_ui.py
- scripts/test_problem_structuring_quality.py
- scripts/test_corporate_deliverables_quality.py

### Acceptance

- El memo ejecutivo y el diagnostico muestran problema estructurado y no solo recomendacion.
- El sistema separa claramente hechos, inferencias, supuestos y recomendaciones.

### Checks

- python3 scripts/test_problem_structuring_quality.py
- python3 scripts/test_corporate_deliverables_quality.py

## Story: C6 | Planner Como Initiative Roadmap

### Goal

Transformar el planner para que pase de una lista lineal de 3 pasos a un roadmap con iniciativas, dependencias, hitos, metricas, riesgos y triggers de decision.

### Deliverables

- scripts/planner.py
- scripts/test_execution_planner.py
- scripts/test_initiative_roadmap_quality.py

### Acceptance

- El 30/60/90 deja de ser el motor principal y pasa a ser una vista resumida de un roadmap mas rico.
- El roadmap identifica workstreams, dependencies, leading indicators, stage-gates y riesgos por iniciativa.

### Checks

- python3 scripts/test_execution_planner.py
- python3 scripts/test_initiative_roadmap_quality.py

## Story: C7 | Suite De Entregables Corporativos

### Goal

Rediseñar los entregables para que funcionen como documentos corporativos utiles: memo ejecutivo, problema estructurado, opciones, roadmap, riesgos, narrativa del founder y documento de decision.

### Deliverables

- scripts/render_report.py
- data/deliverables/
- scripts/test_corporate_deliverables_quality.py
- scripts/test_founder_narrative_quality.py

### Acceptance

- Los entregables ya no se leen como markdown tecnico con una accion al final.
- Cada documento tiene una funcion directiva clara y muestra criterio, no solo resumen.

### Checks

- python3 scripts/test_corporate_deliverables_quality.py
- python3 scripts/test_founder_narrative_quality.py

## Story: C8 | Frontend Ejecutivo Y Lectura De Decision

### Goal

Actualizar la UI para mostrar arquitectura estrategica real: problema, alternativas, criterios, recomendacion, riesgos, roadmap y confianza.

### Deliverables

- scripts/serve_ui.py
- ui/app.js
- ui/index.html
- scripts/test_case_view_model.py
- scripts/test_ui_workspace_flow.py

### Acceptance

- La vista de decision deja de ser un resumen de una sola jugada.
- El founder puede leer en pantalla por que una ruta gana, que podria salir mal y que se debe validar despues.

### Checks

- node --check ui/app.js
- python3 scripts/test_case_view_model.py
- python3 scripts/test_ui_workspace_flow.py

## Story: C9 | Caso Publico V3 Y Guia Regenerada

### Goal

Usar el caso publico como prueba final del nuevo enfoque: regenerar outputs, validar que la recomendacion ya no sea angosta y rehacer la guia publica si es necesario.

### Deliverables

- data/companies/public-case-real-estate-studio/
- data/decisions/public-case-real-estate-studio/
- data/plans/public-case-real-estate-studio/
- data/deliverables/public-case-real-estate-studio/
- output/pdf/wsbi-founder-guide-understanding.md
- output/pdf/wsbi-founder-guide-understanding.pdf

### Acceptance

- El caso publico ya muestra problema, opciones, criterios y roadmap; no solo una tarea.
- La guia demuestra que el sistema sirve para pensar mejor, no solo para producir una recomendacion vistosa.

### Checks

- python3 scripts/test_public_case_specificity.py
- python3 scripts/test_public_guide_quality.py
- python3 scripts/test_founder_usefulness.py

## Story: C10 | Verificacion Final Y Cierre Del Loop

### Goal

Correr la bateria final, verificar que los outputs se comporten como entregables corporativos utiles y cerrar el Ralph loop con estado persistido.

### Deliverables

- tasks/ground-loop/wsbi-corporate-deliverables-v1/progress.txt
- tasks/ground-loop/wsbi-corporate-deliverables-v1/prd.json
- tasks/ground-loop/wsbi-corporate-deliverables-v1/last-message.txt
- data/reports/release-readiness/

### Acceptance

- El loop queda cerrado con `C1-C10` completadas.
- La suite demuestra que ya no hay colapso a una sola accion, que existen alternativas estrategicas y que los entregables son mas corporativos y utiles.

### Checks

- python3 -m compileall scripts
- node --check ui/app.js
- python3 scripts/test_reasoning_quality.py
- python3 scripts/test_decision_engine.py
- python3 scripts/test_execution_planner.py
- python3 scripts/test_case_view_model.py
- python3 scripts/test_ui_workspace_flow.py
- python3 scripts/test_language_purity.py
- python3 scripts/test_founder_usefulness.py
- python3 scripts/test_non_generic_outputs.py
- python3 scripts/test_case_specific_decision.py
- python3 scripts/test_public_guide_quality.py
- python3 scripts/test_public_case_specificity.py
- python3 scripts/test_problem_structuring_quality.py
- python3 scripts/test_strategic_options_are_real.py
- python3 scripts/test_no_single_action_collapse.py
- python3 scripts/test_where_to_play_how_to_win.py
- python3 scripts/test_what_must_be_true.py
- python3 scripts/test_initiative_roadmap_quality.py
- python3 scripts/test_corporate_deliverables_quality.py
- python3 scripts/test_case_for_change_quality.py
- python3 scripts/test_founder_narrative_quality.py
- python3 scripts/release_check.py
- scripts/codex-ground-loop/ground-loop.sh tasks/ground-loop/wsbi-corporate-deliverables-v1

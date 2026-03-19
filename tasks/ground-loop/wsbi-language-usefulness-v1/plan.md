---
project: Ws B-I
runId: wsbi-language-usefulness-v1
commitPolicy: "no-commit"
qualityChecks:
  - python3 -m compileall scripts
  - node --check ui/app.js
  - python3 scripts/codex-ground-loop/build_prd.py tasks/ground-loop/wsbi-language-usefulness-v1/plan.md tasks/ground-loop/wsbi-language-usefulness-v1/prd.json
  - python3 scripts/test_reasoning_quality.py
  - python3 scripts/test_ui_workspace_flow.py
  - python3 scripts/test_case_view_model.py
  - python3 scripts/release_check.py
---

# Goal

Corregir Ws B-I para que deje de mezclar ingles y spanglish en superficies publicas, explique con claridad para que le sirve cada bloque al emprendedor y produzca resultados menos genericos, mas trazables y mas especificos al caso.

## Story: C1 | Auditoria De Idioma Y Superficies Publicas

### Goal

Inventariar y corregir el ingles, spanglish y los terminos internos expuestos al usuario en documentacion, guia, frontend y payloads visibles.

### Deliverables

- README.md
- docs/founder/README.md
- docs/founder/03-ver-tu-frontend.md
- output/pdf/wsbi-founder-guide-understanding.md
- scripts/serve_ui.py
- ui/app.js

### Acceptance

- Las superficies publicas principales quedan en espanol consistente.
- No se exponen estados internos o recomendaciones en ingles en la guia ni en el frontend.
- El sistema usa terminos legibles para un emprendedor y no jerga tecnica innecesaria.

### Checks

- python3 -m compileall scripts
- node --check ui/app.js

## Story: C2 | Motor De Cliente Y Oferta Menos Generico

### Goal

Reducir la dependencia de plantillas universales en cliente, oferta y mensaje principal para que las salidas nazcan mas del caso y menos del framework.

### Deliverables

- scripts/customer_model.py
- scripts/serve_ui.py

### Acceptance

- Los defaults de ICP, oferta y mensaje dejan de nacer en ingles.
- Cuando hay poca evidencia, el sistema declara incertidumbre en lugar de fabricar una promesa elegante.
- Dos negocios distintos no colapsan en la misma lectura de cliente y oferta salvo soporte claro.

### Checks

- python3 scripts/test_reasoning_quality.py

## Story: C3 | Motor De Decision Especifico Al Caso

### Goal

Hacer que las recomendaciones y bloqueadores del motor de decision dejen de sonar a playbook universal y reflejen mejor el contexto concreto del caso.

### Deliverables

- scripts/decision_engine.py
- scripts/render_report.py
- ui/app.js

### Acceptance

- Las preguntas, criterios, riesgos y recomendaciones salen en espanol.
- La recomendacion principal explica por que sirve para ese negocio, no solo para "cualquier PyME".
- El memo de decision deja visible que haria cambiar la recomendacion.

### Checks

- python3 scripts/test_decision_engine.py
- python3 scripts/test_case_view_model.py

## Story: C4 | Mercado, Precio Y Viabilidad En Lenguaje De Negocio

### Goal

Traducir y aterrizar las salidas de mercado, precio y viabilidad para que sirvan como lectura de negocio y no como bloque semi tecnico.

### Deliverables

- scripts/market_model.py
- scripts/pricing.py
- scripts/render_tables.py
- scripts/render_report.py

### Acceptance

- Los hechos, supuestos, escenarios y posturas quedan en espanol claro.
- Mercado, precio y viabilidad explican utilidad practica y limites.
- Los textos ya no suenan a spreadsheet comentado sino a lectura ejecutiva usable.

### Checks

- python3 scripts/test_market_model.py
- python3 scripts/test_pricing_financials.py

## Story: C5 | Frontend Que Explique Para Que Sirve Cada Bloque

### Goal

Reescribir el microcopy y los summaries del frontend para que cada capitulo responda "que es" y "para que te sirve" desde la perspectiva del emprendedor.

### Deliverables

- ui/app.js
- ui/index.html
- ui/styles.css
- scripts/serve_ui.py

### Acceptance

- Portada, cliente, mercado, precio, decision, plan, documentos y auditoria explican utilidad real.
- La interfaz ayuda a interpretar el caso, no solo a navegar datos.
- Los subtitulos y narrativas de cada bloque reducen ambiguedad para usuarios no tecnicos.

### Checks

- node --check ui/app.js
- python3 scripts/test_ui_workspace_flow.py

## Story: C6 | Guia Founder Y Guia Corta Reescritas Con Utilidad Real

### Goal

Reescribir las guias para que expliquen que hace cada modulo, que entrega y como ayuda al negocio, evitando descripcion generica del sistema.

### Deliverables

- README.md
- docs/founder/README.md
- docs/founder/03-ver-tu-frontend.md
- output/pdf/wsbi-founder-guide-understanding.md
- output/pdf/wsbi-founder-guide-understanding.pdf

### Acceptance

- La guia corta deja claro para que sirve cada bloque del sistema.
- La documentacion founder explica resultados concretos y no solo el flujo.
- El caso demo publicado se entiende como herramienta de negocio, no como demo tecnica.

### Checks

- python3 scripts/test_founder_usefulness.py
- python3 scripts/test_public_guide_quality.py

## Story: C7 | Suite Nueva Contra Idioma Y Genericidad

### Goal

Agregar pruebas que fallen si reaparece ingles visible innecesario, explicaciones sin utilidad real o resultados demasiado plantilla.

### Deliverables

- scripts/test_language_purity.py
- scripts/test_founder_usefulness.py
- scripts/test_non_generic_outputs.py
- scripts/test_case_specific_decision.py
- scripts/test_public_guide_quality.py
- scripts/release_check.py

### Acceptance

- La release gate incluye idioma, utilidad founder y no genericidad.
- Las pruebas capturan errores en docs, view models y motores principales.
- El repo deja de depender solo de revision manual para detectar estos problemas.

### Checks

- python3 scripts/test_language_purity.py
- python3 scripts/test_founder_usefulness.py
- python3 scripts/test_non_generic_outputs.py
- python3 scripts/test_case_specific_decision.py
- python3 scripts/test_public_guide_quality.py

## Story: C8 | Regeneracion Del Caso Demo Y Verificacion Final

### Goal

Regenerar el caso publico y la guia final con la logica corregida, ejecutar la bateria completa y dejar el loop listo para continuar sin perder estado.

### Deliverables

- output/pdf/wsbi-founder-guide-understanding.md
- output/pdf/wsbi-founder-guide-understanding.pdf
- tasks/ground-loop/wsbi-language-usefulness-v1/progress.txt
- tasks/ground-loop/wsbi-language-usefulness-v1/prd.json

### Acceptance

- El caso demo ya no muestra frases plantilla en ingles.
- La guia publica queda alineada con la UI y con los motores corregidos.
- Todos los checks del loop pasan y el estado persistido refleja cada historia cerrada.

### Checks

- python3 -m compileall scripts
- node --check ui/app.js
- python3 scripts/test_reasoning_quality.py
- python3 scripts/test_decision_engine.py
- python3 scripts/test_market_model.py
- python3 scripts/test_pricing_financials.py
- python3 scripts/test_ui_workspace_flow.py
- python3 scripts/test_case_view_model.py
- python3 scripts/test_language_purity.py
- python3 scripts/test_founder_usefulness.py
- python3 scripts/test_non_generic_outputs.py
- python3 scripts/test_case_specific_decision.py
- python3 scripts/test_public_guide_quality.py
- python3 scripts/release_check.py
- scripts/codex-ground-loop/ground-loop.sh tasks/ground-loop/wsbi-language-usefulness-v1

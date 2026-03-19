---
project: Ws B-I
runId: wsbi-public-guide-v1
commitPolicy: "no-commit"
qualityChecks:
  - python3 -m compileall scripts
  - node --check ui/app.js
  - python3 scripts/codex-ground-loop/build_prd.py tasks/ground-loop/wsbi-public-guide-v1/plan.md tasks/ground-loop/wsbi-public-guide-v1/prd.json
  - python3 scripts/test_language_purity.py
  - python3 scripts/test_founder_usefulness.py
  - python3 scripts/test_public_guide_quality.py
  - python3 scripts/test_case_view_model.py
  - python3 scripts/test_ui_workspace_flow.py
  - python3 scripts/release_check.py
---

# Goal

Crear una guia publica completa de Ws B-I de punta a punta, en dos formatos:

- una guia larga en PDF con screenshots reales y explicacion paso a paso para personas no tecnicas;
- una version en Markdown pensada para Reddit, mas corta pero igual de clara.

La guia debe conservar la historia de origen y las ideas del texto base sin rebajarlas a copy generico, explicar para que sirve cada paso y cada bloque del sistema, y cerrar con una actualizacion del repositorio publico en GitHub que incluya un enlace visible al PDF final.

## Story: G1 | Reconstruccion Del Texto Fuente Y Mapa Editorial

### Goal

Reconstruir el texto base del usuario sin perder ideas, separar historia, tesis, instrucciones, narrativa comunitaria y llamados a la accion, y convertirlo en una base editorial util para la guia larga y la version Reddit.

### Deliverables

- tasks/ground-loop/wsbi-public-guide-v1/progress.txt
- base editorial consolidada en memoria de trabajo del loop

### Acceptance

- Quedan preservadas las ideas clave del texto original.
- Se identifican secciones que deben mantenerse casi literales y secciones que requieren reescritura para claridad.
- Queda registrado que no se deben disminuir ideas ni convertir el texto en marketing generico.

### Checks

- python3 scripts/test_founder_usefulness.py

## Story: G2 | Arquitectura De La Guia PDF Y Del Post Para Reddit

### Goal

Definir la estructura exacta de ambos entregables antes de escribirlos: portada, historia, explicacion de Ws B-I, preparacion de carpeta, prompt, permisos, revision del frontend, aprendizaje con Codex y cierre comunitario.

### Deliverables

- output/pdf/wsbi-public-guide-master.md
- output/pdf/wsbi-reddit-post.md

### Acceptance

- El PDF queda planteado como una guia para no tecnicos con secciones claras y progresivas.
- El Markdown para Reddit queda planteado como una adaptacion fiel, no como resumen vacio.
- La estructura deja espacio para screenshots y pies de figura utiles.

### Checks

- python3 scripts/test_public_guide_quality.py

## Story: G3 | Redaccion Del Master Draft Largo

### Goal

Escribir el master draft completo de la guia larga incorporando el texto del usuario con la mayor fidelidad posible, corrigiendo solo claridad, ortografia y orden narrativo.

### Deliverables

- output/pdf/wsbi-public-guide-master.md

### Acceptance

- La historia de McKinsey, BCG, la brecha de LatAm y la solopreneur de eventos siguen presentes con fuerza.
- Se explica claramente que hace Ws B-I, como usarlo y para que sirve cada paso.
- El prompt exacto queda incluido de forma visible y completa.
- El tono sigue siendo humano, claro y no tecnico.

### Checks

- python3 scripts/test_language_purity.py
- python3 scripts/test_founder_usefulness.py

## Story: G4 | Adaptacion Del Texto A Version Reddit

### Goal

Crear una version mas corta en Markdown para Reddit que conserve la historia, la utilidad real del sistema y el paso a paso minimo para usarlo.

### Deliverables

- output/pdf/wsbi-reddit-post.md

### Acceptance

- El post se entiende sin contexto tecnico previo.
- Mantiene la historia, el problema, la solucion, el prompt y el valor practico.
- No suena a lanzamiento vacio ni a hilo genérico de AI.

### Checks

- python3 scripts/test_founder_usefulness.py

## Story: G5 | Capturas Reales Del Flujo Y Del Frontend

### Goal

Tomar screenshots reales del flujo que la guia necesita mostrar: Codex instalado, carpeta de empresa organizada, prompt pegado, permisos, frontend abierto y las vistas principales del caso.

### Deliverables

- output/playwright/wsbi-guide-codex-install.png
- output/playwright/wsbi-guide-codex-session.png
- output/playwright/wsbi-guide-folder-structure.png
- output/playwright/wsbi-guide-prompt.png
- output/playwright/wsbi-guide-permissions.png
- output/playwright/wsbi-guide-frontend-overview.png
- output/playwright/wsbi-guide-frontend-customer.png
- output/playwright/wsbi-guide-frontend-market.png
- output/playwright/wsbi-guide-frontend-decision.png
- output/playwright/wsbi-guide-frontend-documents.png
- output/playwright/wsbi-guide-frontend-audit.png

### Acceptance

- Las capturas salen del sistema real o del entorno real del uso de Codex.
- Cada captura es legible y sirve para explicar una accion o una pantalla concreta.
- El caso visible en frontend no cae en genericidad ni en humo.

### Checks

- node --check ui/app.js
- python3 scripts/test_case_view_model.py
- python3 scripts/test_ui_workspace_flow.py

## Story: G6 | PDF Final Con Explicacion Paso A Paso

### Goal

Convertir el master draft en un PDF final con screenshots, jerarquia visual clara y explicacion precisa de que hace el sistema en cada paso y para que le sirve al emprendedor.

### Deliverables

- output/pdf/wsbi-public-guide.pdf
- output/pdf/wsbi-public-guide-master.md

### Acceptance

- El PDF se puede leer sin saber cuestiones tecnicas.
- Cada paso explica no solo que hacer, sino para que sirve.
- Los screenshots tienen contexto y pies utiles.
- El texto del usuario sigue reconocible y fuerte.

### Checks

- python3 scripts/test_public_guide_quality.py
- python3 scripts/test_founder_usefulness.py

## Story: G7 | QA Visual, Editorial Y De Utilidad

### Goal

Revisar el PDF y el Markdown final para detectar ingles residual, ideas perdidas, pasos ambiguos, capturas poco utiles o explicaciones demasiado tecnicas.

### Deliverables

- output/pdf/wsbi-public-guide.pdf
- output/pdf/wsbi-public-guide-master.md
- output/pdf/wsbi-reddit-post.md
- tasks/ground-loop/wsbi-public-guide-v1/progress.txt

### Acceptance

- El PDF final queda limpio en idioma y legibilidad.
- La version Reddit conserva la esencia y no pierde claridad.
- El loop documenta cualquier correccion final de copy, layout o screenshots.

### Checks

- python3 scripts/test_language_purity.py
- python3 scripts/test_founder_usefulness.py
- python3 scripts/test_public_guide_quality.py

## Story: G8 | Actualizacion Del Repositorio Publico Y Enlace Al PDF

### Goal

Actualizar el repositorio publico de GitHub para que la guia final sea visible desde la documentacion principal y la gente pueda acceder facilmente al PDF.

### Deliverables

- README.md
- docs/founder/README.md
- docs/founder/02-trabajar-con-codex.md
- docs/founder/03-ver-tu-frontend.md
- output/pdf/wsbi-public-guide.pdf
- output/pdf/wsbi-reddit-post.md

### Acceptance

- El README y la guia founder incluyen un enlace claro al PDF final.
- La documentacion del repo apunta a la nueva guia sin contradicciones.
- El cierre del loop deja listo el material para publicarlo o subirlo a GitHub.

### Checks

- python3 scripts/test_language_purity.py
- python3 scripts/test_founder_usefulness.py
- python3 scripts/test_public_guide_quality.py
- python3 scripts/release_check.py

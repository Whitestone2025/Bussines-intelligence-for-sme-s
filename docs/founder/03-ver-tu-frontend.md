# Ve tu frontend

Tu frontend es la superficie local donde revisas tu caso.

Si quieres un recorrido visual completo antes de abrirlo, puedes apoyarte tambien en la [guia publica paso a paso en PDF](assets/wsbi-public-guide.pdf).

## Como deberia funcionar

Cuando Codex ya cargo tu negocio, debe correr:

```bash
python3 scripts/serve_ui.py
```

Despues debe darte la URL local.

En una instalacion limpia, Codex tambien debe explicarte que el setup ya quedo listo y que el frontend ahora corresponde a tu negocio.

## Que deberias ver

- tu negocio como caso activo,
- tesis y recomendacion,
- resumen de cliente y mercado,
- vista de precio y viabilidad,
- decision y plan,
- lector de documentos,
- y modo de trazabilidad si quieres revisar el soporte.

## Para que sirve cada bloque

### Portada

Te sirve para ubicarte rapido.
En una sola vista deberias poder responder:

- en que estado esta el caso,
- si ya hay suficiente sustento para actuar,
- cual es el foco comercial actual,
- y que siguiente movimiento sugiere el sistema.

### Tesis

Te sirve para condensar la lectura actual del negocio.
No es "la verdad final".
Es la mejor explicacion provisional de:

- que parece vender realmente la empresa,
- para quien parece ser,
- y que mensaje conviene poner al frente.

### Cliente

Te sirve para ver a quien vale la pena perseguir y por que compra.
Tambien te muestra:

- objeciones reales,
- dolores que se repiten,
- resultados que el comprador si busca,
- y que prueba necesita ver para confiar.

### Mercado

Te sirve para responder una pregunta simple:

"hay suficiente espacio comercial para justificar una prueba?"

No solo muestra numeros.
Tambien muestra el nivel de confianza de esos supuestos.

### Precio y viabilidad

Te sirve para leer si el rango de precio actual parece defendible y si la economia del caso aguanta una prueba comercial razonable.

No significa que el precio ya sea definitivo.
Significa que ya existe un rango de trabajo para discutir.

### Decision

Te sirve para saber cual es el siguiente movimiento sugerido y por que.
Esa vista deberia ayudarte a decidir:

- que hacer primero,
- que riesgo estas aceptando,
- y que validacion falta antes de comprometer mas tiempo o dinero.

### Plan

Te sirve para bajar la decision a pasos concretos.
Si el sistema recomienda algo pero no puede convertirlo en pasos ejecutables, entonces la recomendacion todavia esta verde.

### Documentos

Te sirve para leer el caso completo con mas calma, compartirlo, revisarlo con socios o discutirlo con el equipo.

### Auditoria

Te sirve para revisar cuanto confiar en el caso.
Es la capa que responde:

- de donde sale esta conclusion,
- cuanta evidencia la respalda,
- y que sigue abierto.

## Si el frontend esta vacio

Eso significa que tu negocio todavia no se ha cargado.
Dile a Codex que continue el onboarding en lugar de intentar arreglar el repo tu mismo.

Si ya habias dejado archivos de tu negocio en la carpeta, recuerda decirle que revise esos archivos antes de volver a preguntarte cosas.

Ejemplo:

```text
Sigue con Ws B-I, revisa la informacion que ya deje en esta carpeta y no te detengas hasta que mi negocio aparezca en el frontend.
```

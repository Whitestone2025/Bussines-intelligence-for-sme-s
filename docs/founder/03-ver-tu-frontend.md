# Ve tu frontend

Tu frontend es la superficie local donde revisas tu caso.

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

## Si el frontend esta vacio

Eso significa que tu negocio todavia no se ha cargado.
Dile a Codex que continue el onboarding en lugar de intentar arreglar el repo tu mismo.

Si ya habias dejado archivos de tu negocio en la carpeta, recuerda decirle que revise esos archivos antes de volver a preguntarte cosas.

Ejemplo:

```text
Sigue con Ws B-I, revisa la informacion que ya deje en esta carpeta y no te detengas hasta que mi negocio aparezca en el frontend.
```

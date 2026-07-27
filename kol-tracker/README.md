# KOL Tracker — GenLayer Ambassadors & Rally

`KOL_Tracker.xlsx` es la hoja de seguimiento de KOLs/embajadores: posts publicados, dinero invertido, pagado y pendiente.

Se puede usar en Excel o subir tal cual a Google Sheets (Archivo → Importar).

## Hojas

| Hoja | Qué contiene |
|---|---|
| **Guía** | Instrucciones y código de colores |
| **Dashboard** | Totales generales y desglose por programa (GenLayer Ambassador vs Rally) — todo automático |
| **KOLs** | Alta de cada embajador: handle de X, programa, tipo de acuerdo, tarifa. Incluye columnas calculadas (nº posts, views, pagado, pendiente, CPM) |
| **Posts** | Un registro por publicación: fecha, KOL, link, tipo, métricas (views/likes/RTs) y coste atribuido |
| **Pagos** | Un registro por pago: fecha, KOL, importe, concepto y estado (Pagado / Pendiente) |

## Uso

1. Da de alta al KOL en **KOLs** (el programa y el estado tienen desplegable).
2. Añade cada publicación en **Posts** — el KOL se elige de un desplegable y el programa se rellena solo.
3. Registra cada pago en **Pagos** con estado `Pagado` o `Pendiente`.
4. El **Dashboard** y las columnas calculadas se actualizan solos.

Las filas marcadas `(ejemplo)` son de muestra: bórralas o sobreescríbelas.

Las fórmulas cubren hasta la fila 300 de cada hoja. Las métricas de X se introducen a mano (la API de X es de pago).

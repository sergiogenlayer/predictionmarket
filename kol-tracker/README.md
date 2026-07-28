# KOL Tracker — GenLayer Ambassadors & Rally

Seguimiento automatizado de KOLs/embajadores: posts publicados en X, métricas (views/likes/RTs), dinero invertido, pagado y pendiente.

## Cómo funciona

```
kols.csv (roster) ──┐
                    ├─► update_tracker.py ──► posts.csv + pagos.csv ──► KOL_Tracker.xlsx (informe)
API de X ───────────┘        ▲
(oficial o twitterapi.io)    └── GitHub Action, cada noche a las 03:00 UTC
```

- **`data/*.csv` son la fuente de verdad.** El Excel `KOL_Tracker.xlsx` es un informe que se regenera solo — no lo edites a mano.
- El script vigila el timeline de cada KOL **Activo**, añade los posts que mencionan las keywords de campaña (`automation/config.json`), refresca métricas de los últimos 30 días y genera las filas de pago del mes.
- Sin API key configurada, funciona en modo manual: solo ingiere los links de `data/submitted_links.csv` y genera pagos.

## Puesta en marcha (5 minutos)

1. **Rellena `data/kols.csv`** con los embajadores reales (las filas "(ejemplo)" se borran). Columnas clave: `tipo_acuerdo` (`Fijo mensual`, `Por post`, `Por hilo`, `Mixto`), `tarifa` (en $) y `estado` (`Activo`/`Inactivo`).
2. **Consigue una API key** (una de las dos):
   - **twitterapi.io** (~$5–30/mes según volumen): date de alta en https://twitterapi.io, copia la key.
   - **API oficial de X** (tier Basic, ~$200/mes): https://developer.x.com, crea un proyecto y copia el *Bearer Token*.
3. **Añádela como secret del repo**: Settings → Secrets and variables → Actions → New repository secret, con nombre `TWITTERAPI_IO_KEY` o `X_BEARER_TOKEN`.
4. **Ajusta las keywords** de campaña en `automation/config.json`.
5. Listo: la Action corre cada noche (o lánzala a mano desde la pestaña **Actions → KOL Tracker → Run workflow**).

## Operativa del día a día

- **Pagos**: el script crea cada mes las filas `Fijo mensual YYYY-MM` (tarifa fija) y `Posts YYYY-MM` (nº posts × tarifa, recalculado mientras esté `Pendiente`). Cuando pagues, cambia `estado` a `Pagado` en `data/pagos.csv` (los pagados no se tocan nunca).
- **Posts que el script no pilla** (p. ej. un Space, u otro idioma sin keyword): añade el link a `data/submitted_links.csv` y el script hará el resto, métricas incluidas.
- **Dashboard**: abre `KOL_Tracker.xlsx` (o impórtalo a Google Sheets) — totales, desglose GenLayer vs Rally, coste por post y CPM, todo calculado.

## Ejecutar en local

```bash
pip install -r kol-tracker/automation/requirements.txt
export TWITTERAPI_IO_KEY=...   # o X_BEARER_TOKEN=...
python kol-tracker/automation/update_tracker.py
```

## Estructura

| Fichero | Qué es |
|---|---|
| `data/kols.csv` | Roster de embajadores (lo editas tú) |
| `data/posts.csv` | Posts detectados con métricas (lo mantiene el script) |
| `data/pagos.csv` | Pagos generados/registrados (el script crea, tú marcas `Pagado`) |
| `data/submitted_links.csv` | Links reportados a mano (opcional) |
| `automation/config.json` | Keywords de campaña y parámetros |
| `automation/update_tracker.py` | Orquestador (ingesta → descubrimiento → métricas → pagos → Excel) |
| `automation/sources.py` | Clientes de la API oficial de X y de twitterapi.io |
| `automation/build_xlsx.py` | Generador del informe Excel |
| `KOL_Tracker.xlsx` | Informe generado (no editar a mano) |

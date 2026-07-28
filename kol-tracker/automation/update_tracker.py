#!/usr/bin/env python3
"""Actualiza el KOL tracker.

Pasos (los que dependen de una API key se saltan solos si no hay key):
  1. Ingesta de links reportados (data/submitted_links.csv) -> data/posts.csv
  2. Descubrimiento: vigila el timeline de cada KOL activo y anade los posts
     que mencionen las keywords de campana (config.json)
  3. Refresco de metricas (views/likes/RTs/replies) de los posts recientes
  4. Coste automatico de posts para acuerdos "Por post" / "Por hilo"
  5. Generacion de filas de pago del mes (fijos mensuales y devengo por post)
  6. Regenera el informe KOL_Tracker.xlsx

Fuente de datos de X: variable de entorno X_BEARER_TOKEN (API oficial)
o TWITTERAPI_IO_KEY (twitterapi.io). Ver sources.py.
"""

import csv
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_xlsx
from sources import get_source, tweet_id_from_url

BASE = Path(__file__).resolve().parent
DATA = BASE.parent / "data"
XLSX = BASE.parent / "KOL_Tracker.xlsx"
CONFIG = json.loads((BASE / "config.json").read_text(encoding="utf-8"))

KOLS_F = ["nombre", "handle", "link", "programa", "tipo_acuerdo", "tarifa",
          "fecha_inicio", "estado", "pago_metodo", "notas"]
POSTS_F = ["tweet_id", "fecha", "kol", "link", "tipo", "views", "likes",
           "rts", "replies", "coste", "notas"]
PAGOS_F = ["fecha", "kol", "importe", "concepto", "estado", "metodo", "notas"]

TODAY = dt.date.today()
MES = TODAY.strftime("%Y-%m")


def read_csv(path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def num(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def ingest_submitted(posts):
    """Anade a posts los links reportados que aun no esten registrados."""
    known = {p["link"] for p in posts} | {p["tweet_id"] for p in posts if p.get("tweet_id")}
    added = 0
    for s in read_csv(DATA / "submitted_links.csv"):
        link = (s.get("link") or "").strip()
        tid = tweet_id_from_url(link)
        if not link or link in known or (tid and tid in known):
            continue
        posts.append({
            "tweet_id": tid,
            "fecha": (s.get("fecha") or "").strip() or TODAY.isoformat(),
            "kol": (s.get("kol") or "").strip(),
            "link": link,
            "tipo": (s.get("tipo") or "").strip() or "Post",
            "notas": ((s.get("notas") or "").strip() + " [reportado]").strip(),
        })
        known |= {link, tid}
        added += 1
    return added


def discover_timelines(src, kols, posts):
    """Vigila el timeline de cada KOL activo y anade posts con keywords."""
    keywords = [k.lower() for k in CONFIG.get("keywords", [])]
    known_ids = {p["tweet_id"] for p in posts if p.get("tweet_id")}
    added = 0
    for k in kols:
        if (k.get("estado") or "").strip() != "Activo" or not (k.get("handle") or "").strip():
            continue
        handle = k["handle"].strip().lstrip("@")
        try:
            tweets = src.user_recent(handle, CONFIG.get("max_tweets_timeline", 20))
        except Exception as e:  # un KOL caido no debe parar al resto
            print(f"  aviso: timeline de @{handle} fallo: {e}")
            continue
        for t in tweets:
            texto = (t.get("texto") or "").lower()
            if t["id"] in known_ids or not any(kw in texto for kw in keywords):
                continue
            posts.append({
                "tweet_id": t["id"],
                "fecha": t["fecha"] or TODAY.isoformat(),
                "kol": k["nombre"],
                "link": f"https://x.com/{handle}/status/{t['id']}",
                "tipo": "Post",
                "views": t["views"], "likes": t["likes"],
                "rts": t["rts"], "replies": t["replies"],
                "notas": "[auto]",
            })
            known_ids.add(t["id"])
            added += 1
    return added


def refresh_metrics(src, posts):
    """Actualiza metricas de los posts de los ultimos N dias."""
    limite = TODAY - dt.timedelta(days=CONFIG.get("dias_refresco_metricas", 30))
    ids = []
    for p in posts:
        if not p.get("tweet_id"):
            continue
        try:
            reciente = dt.date.fromisoformat(p.get("fecha") or "") >= limite
        except ValueError:
            reciente = True
        if reciente:
            ids.append(p["tweet_id"])
    if not ids:
        return 0
    info = src.tweets_by_ids(ids)
    updated = 0
    for p in posts:
        t = info.get(p.get("tweet_id") or "")
        if not t:
            continue
        p.update({"views": t["views"], "likes": t["likes"],
                  "rts": t["rts"], "replies": t["replies"]})
        if t["fecha"]:
            p["fecha"] = t["fecha"]
        updated += 1
    return updated


def autocost(kols, posts):
    """Rellena el coste de posts para acuerdos por post / por hilo."""
    deals = {k["nombre"]: k for k in kols}
    for p in posts:
        if str(p.get("coste") or "").strip():
            continue
        k = deals.get(p.get("kol") or "")
        if not k:
            continue
        acuerdo, tarifa = (k.get("tipo_acuerdo") or "").strip(), num(k.get("tarifa"))
        if not tarifa:
            continue
        if acuerdo == "Por post" or (acuerdo == "Por hilo" and (p.get("tipo") or "") == "Hilo"):
            p["coste"] = f"{tarifa:g}"


def generate_pagos(kols, posts, pagos):
    """Crea/actualiza las filas de pago del mes en curso."""
    existing = {((p.get("kol") or ""), (p.get("concepto") or "")): p for p in pagos}
    added = 0
    for k in kols:
        if (k.get("estado") or "").strip() != "Activo":
            continue
        nombre, acuerdo, tarifa = k["nombre"], (k.get("tipo_acuerdo") or "").strip(), num(k.get("tarifa"))
        if acuerdo == "Fijo mensual" and tarifa:
            concepto = f"Fijo mensual {MES}"
            if (nombre, concepto) not in existing:
                pagos.append({"fecha": TODAY.isoformat(), "kol": nombre, "importe": f"{tarifa:g}",
                              "concepto": concepto, "estado": "Pendiente",
                              "metodo": k.get("pago_metodo", ""), "notas": "[auto]"})
                added += 1
        elif acuerdo in ("Por post", "Por hilo"):
            devengado = sum(num(p.get("coste")) for p in posts
                            if p.get("kol") == nombre and (p.get("fecha") or "").startswith(MES))
            concepto = f"Posts {MES}"
            row = existing.get((nombre, concepto))
            if row is not None:
                if (row.get("estado") or "") == "Pendiente":  # los pagados no se tocan
                    row["importe"] = f"{devengado:g}"
            elif devengado > 0:
                pagos.append({"fecha": TODAY.isoformat(), "kol": nombre, "importe": f"{devengado:g}",
                              "concepto": concepto, "estado": "Pendiente",
                              "metodo": k.get("pago_metodo", ""), "notas": "[auto]"})
                added += 1
    return added


def main():
    kols = read_csv(DATA / "kols.csv")
    posts = read_csv(DATA / "posts.csv")
    pagos = read_csv(DATA / "pagos.csv")

    print(f"KOLs: {len(kols)} | posts: {len(posts)} | pagos: {len(pagos)}")
    print(f"+{ingest_submitted(posts)} posts desde links reportados")

    src = get_source()
    if src is None:
        print("Sin API key (X_BEARER_TOKEN / TWITTERAPI_IO_KEY): salto descubrimiento y metricas")
    else:
        print(f"Fuente de datos: {type(src).__name__}")
        if CONFIG.get("descubrir_timelines"):
            print(f"+{discover_timelines(src, kols, posts)} posts descubiertos en timelines")
        print(f"{refresh_metrics(src, posts)} posts con metricas refrescadas")

    autocost(kols, posts)
    print(f"+{generate_pagos(kols, posts, pagos)} filas de pago generadas")

    posts.sort(key=lambda p: (p.get("fecha") or "", p.get("kol") or ""))
    pagos.sort(key=lambda p: (p.get("fecha") or "", p.get("kol") or ""))
    write_csv(DATA / "posts.csv", posts, POSTS_F)
    write_csv(DATA / "pagos.csv", pagos, PAGOS_F)

    build_xlsx.build(kols, posts, pagos, XLSX)
    print(f"Informe regenerado: {XLSX}")


if __name__ == "__main__":
    main()

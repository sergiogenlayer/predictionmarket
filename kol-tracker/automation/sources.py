"""Fuentes de datos de X (Twitter), enchufables por variable de entorno.

- X_BEARER_TOKEN     -> API oficial de X (tier Basic o superior)
- TWITTERAPI_IO_KEY  -> twitterapi.io (API de terceros, mas barata)

Si no hay ninguna key definida, get_source() devuelve None y el tracker
funciona en modo manual (solo ingesta de links reportados, sin metricas).
"""

import datetime as dt
import email.utils
import os
import re

import requests

TWEET_ID_RE = re.compile(r"(?:twitter|x)\.com/[^/]+/status/(\d+)")


def tweet_id_from_url(url):
    m = TWEET_ID_RE.search(url or "")
    return m.group(1) if m else ""


def parse_created(s):
    """Acepta fecha ISO (API oficial) o formato clasico de Twitter."""
    if not s:
        return ""
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        pass
    try:
        return email.utils.parsedate_to_datetime(str(s)).date().isoformat()
    except (TypeError, ValueError):
        return ""


def get_source():
    if os.getenv("X_BEARER_TOKEN"):
        return XOficial(os.environ["X_BEARER_TOKEN"])
    if os.getenv("TWITTERAPI_IO_KEY"):
        return TwitterApiIO(os.environ["TWITTERAPI_IO_KEY"])
    return None


def _walk_tweets(payload):
    """Busca listas de tweets en respuestas con estructuras variables."""
    if isinstance(payload, list):
        return [t for t in payload if isinstance(t, dict) and ("id" in t or "id_str" in t)]
    if isinstance(payload, dict):
        for key in ("tweets", "data", "results", "statuses"):
            if key in payload:
                found = _walk_tweets(payload[key])
                if found:
                    return found
        for v in payload.values():
            if isinstance(v, (dict, list)):
                found = _walk_tweets(v)
                if found:
                    return found
    return []


class TwitterApiIO:
    """Cliente minimo de twitterapi.io."""

    BASE = "https://api.twitterapi.io"

    def __init__(self, key):
        self.headers = {"X-API-Key": key}

    def _get(self, path, params):
        r = requests.get(self.BASE + path, params=params, headers=self.headers, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _info(t):
        return {
            "id": str(t.get("id") or t.get("id_str") or ""),
            "texto": t.get("text") or t.get("fullText") or "",
            "fecha": parse_created(t.get("createdAt") or t.get("created_at")),
            "views": int(t.get("viewCount") or t.get("views") or 0),
            "likes": int(t.get("likeCount") or t.get("favorite_count") or 0),
            "rts": int(t.get("retweetCount") or t.get("retweet_count") or 0),
            "replies": int(t.get("replyCount") or t.get("reply_count") or 0),
        }

    def tweets_by_ids(self, ids):
        out = {}
        for i in range(0, len(ids), 100):
            data = self._get("/twitter/tweets", {"tweet_ids": ",".join(ids[i:i + 100])})
            for t in _walk_tweets(data):
                info = self._info(t)
                if info["id"]:
                    out[info["id"]] = info
        return out

    def user_recent(self, handle, n=20):
        data = self._get("/twitter/user/last_tweets", {"userName": handle.lstrip("@")})
        tweets = [self._info(t) for t in _walk_tweets(data)]
        return [t for t in tweets if t["id"]][:n]


class XOficial:
    """Cliente minimo de la API oficial de X v2 (app-only bearer)."""

    BASE = "https://api.twitter.com/2"
    FIELDS = "public_metrics,created_at"

    def __init__(self, bearer):
        self.headers = {"Authorization": f"Bearer {bearer}"}
        self._user_ids = {}

    def _get(self, path, params):
        r = requests.get(self.BASE + path, params=params, headers=self.headers, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _info(t):
        pm = t.get("public_metrics") or {}
        return {
            "id": str(t.get("id") or ""),
            "texto": t.get("text") or "",
            "fecha": parse_created(t.get("created_at")),
            "views": int(pm.get("impression_count") or 0),
            "likes": int(pm.get("like_count") or 0),
            "rts": int(pm.get("retweet_count") or 0),
            "replies": int(pm.get("reply_count") or 0),
        }

    def tweets_by_ids(self, ids):
        out = {}
        for i in range(0, len(ids), 100):
            data = self._get("/tweets", {"ids": ",".join(ids[i:i + 100]), "tweet.fields": self.FIELDS})
            for t in data.get("data") or []:
                info = self._info(t)
                out[info["id"]] = info
        return out

    def _user_id(self, handle):
        handle = handle.lstrip("@")
        if handle not in self._user_ids:
            data = self._get(f"/users/by/username/{handle}", {})
            self._user_ids[handle] = str((data.get("data") or {}).get("id") or "")
        return self._user_ids[handle]

    def user_recent(self, handle, n=20):
        uid = self._user_id(handle)
        if not uid:
            return []
        data = self._get(
            f"/users/{uid}/tweets",
            {"max_results": max(5, min(n, 100)), "tweet.fields": self.FIELDS, "exclude": "retweets"},
        )
        return [self._info(t) for t in data.get("data") or []]

#!/usr/bin/env python3
"""Filtra iptv-org (ES/UK/US/JP + anime) y valida cada enlace.

- Descarga iptv-org, filtra por pais/anime.
- Prueba cada enlace en paralelo con ffprobe.
- Conserva: los que funcionan + los geo-bloqueados (para usar con VPN).
- Descarta: enlaces caidos (timeout, 404, 5xx, datos invalidos...).
- Cada dia se parte del listado fresco, asi que un canal que hoy cae y
  manana vuelve a funcionar se re-incluye automaticamente.

Uso:
    python3 filtra_final.py            # completo
    FILTRA_LIMIT=50 python3 filtra_final.py   # solo 50 canales (prueba)
"""
import os
import re
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

URL = "https://iptv-org.github.io/iptv/index.m3u"
BASE = os.path.expanduser("~/xteve")
OUT = os.environ.get("FILTRA_OUT", os.path.join(BASE, "iptv_filtrado.m3u"))
LOG = os.path.join(BASE, "filtro.log")

# Sufijos de pais en tvg-id (iptv-org usa .es@, .uk@, .gb@, .us@, .jp@...)
PAISES_ID = {".es@", ".es ", ".es]", ".uk@", ".gb@", ".us@", ".jp@", ".jp ", ".jp]"}
# Anime por nombre
ANIME_RE = re.compile(
    r"(anime|crunchyroll|animax|toonami|ghibli|wakanim|animetime|animeplus|anione|animeone)",
    re.I,
)

PROBE_TIMEOUT = 7          # segundos por enlace (ffprobe)
WORKERS = 32               # pruebas en paralelo
LIMIT = int(os.environ.get("FILTRA_LIMIT", "0"))  # 0 = sin limite


def log(msg):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def download():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", errors="replace")


def parse(data):
    """Devuelve lista de tuplas (extinf, url, name, geo)."""
    entries = []
    extinf = None
    for raw in data.splitlines():
        line = raw.rstrip("\n")
        if line.startswith("#EXTINF"):
            extinf = line
        elif line and not line.startswith("#") and extinf is not None:
            m_id = re.search(r'tvg-id="([^"]*)"', extinf)
            tid = m_id.group(1) if m_id else ""
            name = extinf[extinf.rfind(",") + 1:].strip() if "," in extinf else ""
            if any(s in tid for s in PAISES_ID) or ANIME_RE.search(name):
                geo = "geo-blocked" in name.lower()
                entries.append((extinf, line.strip(), name, geo))
            extinf = None
    return entries


def probe(entry):
    """Devuelve (entry, 'ok'|'geo'|'dead')."""
    _extinf, url, _name, geo = entry
    if geo:
        return (entry, "geo")  # los geo-bloqueados no se prueban: se conservan (VPN)
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-rw_timeout", str(PROBE_TIMEOUT * 1_000_000),
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name",
                "-of", "csv=p=0",
                "-i", url,
            ],
            capture_output=True, text=True, timeout=PROBE_TIMEOUT + 6,
        )
        if r.stdout.strip():
            return (entry, "ok")
        err = r.stderr or ""
        # 401/403 suele ser geobloqueo/permiso, no enlace muerto -> se conserva
        if "403" in err or "Forbidden" in err or "401" in err or "Unauthorized" in err:
            return (entry, "geo")
        return (entry, "dead")
    except Exception:
        return (entry, "dead")


def main():
    log("=== inicio filtrado + validacion ===")
    data = download()
    entries = parse(data)
    if LIMIT:
        entries = entries[:LIMIT]
    log(f"tras filtro pais/anime: {len(entries)} canales (probando enlaces...)")

    ok = geo = dead = 0
    kept = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for i, (entry, status) in enumerate(ex.map(probe, entries), 1):
            if status == "ok":
                ok += 1
                kept.append(entry)
            elif status == "geo":
                geo += 1
                kept.append(entry)
            else:
                dead += 1
            if i % 250 == 0:
                log(f"  progreso {i}/{len(entries)} (ok={ok} geo={geo} dead={dead})")

    out = ["#EXTM3U"]
    for extinf, url, _name, _geo in kept:
        out.append(extinf)
        out.append(url)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    log(f"RESULTADO: vivos={ok} geo={geo} muertos={dead} -> guardados={len(kept)}")
    log("=== fin ===")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Lista maestra: une la TDT (listas\TDT.m3u) con canales_buenos.m3u (iptv-org filtrado)
y deja UN enlace por canal. La TDT va primero: sus enlaces suelen ser los oficiales.

Dos canales son el mismo si:
  - tienen el mismo nombre (sin "(1080p)" ni "[Geo-blocked]"...), y
  - sus países, cuando los dos lo traen, coinciden. "MTV (UK)" y "MTV (US)" no se fusionan.
También se descarta la misma URL repetida. No hace peticiones de red.
"""
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent   # raíz del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent))
from filtrar_canales import parse  # noqa: E402
from listas_por_proveedor import escribir  # noqa: E402

CALIDAD = re.compile(r"\((?:\d{3,4}p|\d+k|hd|sd|fhd|uhd)\)|\[[^\]]*\]", re.I)


def clave(c):
    n = CALIDAD.sub("", c.nombre).lower()
    return re.sub(r"[^a-z0-9]+", " ", n).strip()


def deduplicar(canales):
    """Conserva el primero de cada canal. Devuelve (lista, cuántos quitó)."""
    por_nombre, urls, salida = {}, set(), []
    for c in canales:
        if c.url in urls:
            continue
        k = clave(c)
        iguales = por_nombre.setdefault(k, []) if k else []
        if any(not c.pais or not p.pais or c.pais == p.pais for p in iguales):
            continue
        iguales.append(c)
        urls.add(c.url)
        salida.append(c)
    return salida, len(canales) - len(salida)


def main():
    tdt = parse(AQUI / "listas" / "TDT.m3u")
    buenos = parse(AQUI / "datos" / "canales_buenos.m3u")
    maestra, quitados = deduplicar(tdt + buenos)
    escribir(AQUI / "datos" / "canales_maestra.m3u", maestra)
    print(f"TDT {len(tdt)} + iptv-org {len(buenos)} -> maestra {len(maestra)} (quitados {quitados})")


if __name__ == "__main__":
    main()

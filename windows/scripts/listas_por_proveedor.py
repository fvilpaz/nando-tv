#!/usr/bin/env python3
"""
Reparte los canales en una lista por proveedor (Rakuten, Samsung, Tubi...) dentro de listas\.
- Los proveedores normales salen de canales_buenos.m3u (ya comprobados desde España).
- Pluto sale de la lista completa SIN comprobar: desde España no da imagen,
  pero con una VPN de EE. UU. sí. Mismo filtro de idioma/fútbol que filtrar_canales.py.
No hace peticiones de red.
"""
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent   # raíz del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent))
from filtrar_canales import parse, decide  # noqa: E402

# (nombre de la lista, patrón sobre URL + nombre + logo)
PROVEEDORES = [
    ("Pluto TV",        re.compile(r"pluto|jmp2\.uk/plu", re.I)),
    ("Rakuten TV",      re.compile(r"rakuten", re.I)),
    ("Samsung TV Plus", re.compile(r"jmp2\.uk/sam|samsung", re.I)),
    ("Plex",            re.compile(r"plex", re.I)),
    ("Tubi",            re.compile(r"tubi", re.I)),
    ("Roku",            re.compile(r"roku", re.I)),
    ("Otras FAST",      re.compile(r"stirr|xumo|distro|redbox|vizio|localnow|frndly", re.I)),
]
SIN_COMPROBAR = {"Pluto TV"}


def proveedor(c):
    texto = f"{c.url} {c.nombre} {c.extinf}"          # el EXTINF lleva el tvg-logo
    for nombre, patron in PROVEEDORES:
        if patron.search(texto):
            return nombre
    return None


def escribir(ruta: Path, canales):
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write("#EXTM3U\n")
        for c in canales:
            f.write(c.extinf + "\n")
            for e in c.extras:
                f.write(e + "\n")
            f.write(c.url + "\n")


def main():
    buenos = parse(AQUI / "datos" / "canales_maestra.m3u")
    todos = [c for c in parse(AQUI / "datos" / "iptv-org_all.m3u") if decide(c)]
    salida = AQUI / "listas"
    salida.mkdir(exist_ok=True)
    for nombre, _ in PROVEEDORES:
        origen = todos if nombre in SIN_COMPROBAR else buenos
        grupo = [c for c in origen if proveedor(c) == nombre]
        escribir(salida / f"{nombre}.m3u", grupo)
        marca = "sin comprobar" if nombre in SIN_COMPROBAR else "vivos"
        print(f"{nombre:18s}{len(grupo):5d}  ({marca})")


if __name__ == "__main__":
    main()

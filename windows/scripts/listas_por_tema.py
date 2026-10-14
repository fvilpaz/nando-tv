#!/usr/bin/env python3
"""
Reparte canales_buenos.m3u (ya comprobados) en listas por temática dentro de listas\.
Usa el group-title de cada canal (puede traer varios: "Movies;Family").
Deportes incluye además lo que coincida con la regex de fútbol por nombre.
No hace peticiones de red.
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent   # raíz del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent))
from filtrar_canales import parse, FUTBOL  # noqa: E402
from listas_por_proveedor import escribir  # noqa: E402

# nombre de la lista -> grupos de iptv-org que entran
TEMAS = {
    "Deportes":     {"sports"},
    "Musica":       {"music"},
    "Cine y series": {"movies", "series"},
}


def grupos(c):
    return {x.strip().lower() for x in c.grupo.split(";")}


def main():
    buenos = parse(AQUI / "datos" / "canales_maestra.m3u")
    salida = AQUI / "listas"
    salida.mkdir(exist_ok=True)
    for tema, gs in TEMAS.items():
        sel = [c for c in buenos if grupos(c) & gs
               or (tema == "Deportes" and FUTBOL.search(c.nombre))]
        escribir(salida / f"{tema}.m3u", sel)
        print(f"{tema:15s}{len(sel):5d}")


if __name__ == "__main__":
    main()

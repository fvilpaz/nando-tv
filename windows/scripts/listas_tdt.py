#!/usr/bin/env python3
"""
Lista de la TDT española (TDTChannels): comprueba cada stream y deja solo los vivos
en listas\TDT.m3u. Excluye el grupo "Religiosos". Reutiliza el comprobador de
filtrar_canales.py. Descarga antes: tdtchannels_tv.m3u
   curl -A "Mozilla/5.0" https://www.tdtchannels.com/lists/tv.m3u8 -o tdtchannels_tv.m3u
"""
import asyncio
import sys
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent   # raíz del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent))
from filtrar_canales import parse, comprobar, UA_POR_DEFECTO  # noqa: E402
from listas_por_proveedor import escribir  # noqa: E402
from maestra import deduplicar  # noqa: E402

URL = "https://www.tdtchannels.com/lists/tv.m3u8"
ORIGEN = AQUI / "datos" / "tdtchannels_tv.m3u"
GRUPOS_FUERA = {"religiosos"}


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": UA_POR_DEFECTO})
    ORIGEN.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    todos = parse(ORIGEN)
    candidatos = [c for c in todos if c.grupo.strip().lower() not in GRUPOS_FUERA]
    print(f"Leídos {len(todos)}; sin religiosos {len(candidatos)}. Comprobando...")
    asyncio.run(comprobar(candidatos, 40, 20))
    vivos = [c for c in candidatos if c.vivo]
    vivos, repetidos = deduplicar(vivos)   # TDTChannels trae varias fuentes por canal
    (AQUI / "listas").mkdir(exist_ok=True)
    escribir(AQUI / "listas" / "TDT.m3u", vivos)
    print(f"OK: {len(vivos)} vivos ({repetidos} repetidos quitados) -> listas\\TDT.m3u")


if __name__ == "__main__":
    main()

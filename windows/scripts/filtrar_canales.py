#!/usr/bin/env python3
"""
Filtra una lista M3U grande:
  1. Se queda con canales en español, inglés y japonés (por el país del tvg-id).
  2. Excepción: si el canal es de fútbol, se queda sea cual sea el idioma.
  3. Comprueba que el stream responde de verdad (lee solo los primeros KB).
Escribe una lista nueva y un informe CSV. No modifica la lista de entrada.
"""

import argparse
import asyncio
import csv
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin

import aiohttp

# --- Qué idiomas quiero (país del tvg-id -> idioma). Edita aquí. -------------
ESPANOL = {"es", "mx", "ar", "cl", "co", "pe", "ve", "ec", "do", "hn", "gt",
           "cr", "bo", "py", "uy", "pa", "sv", "ni", "cu", "pr"}
INGLES = {"us", "uk", "gb", "ie", "au", "nz", "ca"}
JAPONES = {"jp"}
PAISES_OK = ESPANOL | INGLES | JAPONES

# Región del feed (lo que va tras la @ del tvg-id) que es de otro idioma.
# Un canal "es" o "us" puede venir doblado al alemán, italiano, etc.
# No afecta a la excepción del fútbol.
FEEDS_FUERA = {"germany", "italy", "it", "finland", "poland",
               "czechia", "ukraine"}

# Grupos que no quiero nunca
GRUPOS_FUERA = {"religious"}
# Grupos donde una coincidencia de "fútbol" por nombre no cuenta (ninguno)
GRUPOS_NO_FUTBOL = set()

FUTBOL = re.compile(
    r"\b(f[uú]tbol|football|soccer|la\s?liga|laliga|premier league|champions|"
    r"uefa|libertadores|sudamericana|copa america|bundesliga|serie a|ligue 1|"
    r"eredivisie|\bmls\b|dazn|sky sports|bein|eleven sports|tnt sports|espn|"
    r"fox sports|directv sports|win sports|golazo|goltv|gol tv|teledeporte|"
    r"tyc sports|movistar|real madrid|fc barcelona|bar[cç]a tv|mutv|chelsea tv|"
    r"lfc tv|benfica tv|sporting tv|futv|canal\+ foot|ligue)\b",
    re.IGNORECASE,
)

UA_POR_DEFECTO = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@dataclass
class Canal:
    extinf: str
    extras: list = field(default_factory=list)   # líneas '#...' entre EXTINF y URL
    url: str = ""
    nombre: str = ""
    grupo: str = ""
    pais: str = ""
    feed: str = ""
    motivo: str = ""        # 'idioma' | 'futbol'
    vivo: bool = False
    detalle: str = ""


def parse(path: Path) -> list[Canal]:
    """Cada #EXTINF se empareja con la primera línea que NO empieza por '#'."""
    canales, actual = [], None
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        linea = raw.strip()
        if not linea:
            continue
        if linea.startswith("#EXTINF:"):
            actual = Canal(extinf=linea)
        elif linea.startswith("#"):
            if actual is not None and not linea.startswith("#EXTM3U"):
                actual.extras.append(linea)
        elif actual is not None:
            actual.url = linea
            m = re.search(r',([^,]*)$', actual.extinf)
            actual.nombre = m.group(1).strip() if m else ""
            m = re.search(r'group-title="([^"]*)"', actual.extinf)
            actual.grupo = m.group(1).strip() if m else ""
            m = re.search(r'tvg-id="[^"@]*\.([a-z]{2,3})(?:@[^"]*)?"', actual.extinf)
            actual.pais = m.group(1) if m else ""
            m = re.search(r'tvg-id="[^"@]*@([^"]*)"', actual.extinf)
            actual.feed = m.group(1).strip().lower() if m else ""
            canales.append(actual)
            actual = None
    return canales


def decide(c: Canal) -> str:
    """Devuelve el motivo para conservarlo, o '' si se descarta."""
    # un canal puede traer varios grupos: "Music;Religious"
    g = {x.strip().lower() for x in c.grupo.split(";")}
    if g & GRUPOS_FUERA:
        return ""
    if c.pais in PAISES_OK and c.feed not in FEEDS_FUERA:
        return "idioma"
    if not (g & GRUPOS_NO_FUTBOL) and FUTBOL.search(c.nombre):
        return "futbol"
    return ""


def cabeceras(c: Canal) -> tuple[str, str]:
    ua = re.search(r'http-user-agent="([^"]*)"', c.extinf)
    ref = re.search(r'http-referrer="([^"]*)"', c.extinf)
    ua = ua.group(1) if ua else ""
    ref = ref.group(1) if ref else ""
    for e in c.extras:
        if e.lower().startswith("#extvlcopt:http-user-agent="):
            ua = e.split("=", 1)[1]
        if e.lower().startswith("#extvlcopt:http-referrer="):
            ref = e.split("=", 1)[1]
    return ua, ref


async def _leer(sesion, url: str, cab: dict, n: int) -> tuple[bytes, str]:
    """GET que lee solo los primeros n bytes (un directo no termina nunca)."""
    async with sesion.get(url, headers=cab, allow_redirects=True) as r:
        if r.status not in (200, 206):
            raise RuntimeError(f"HTTP {r.status}")
        return await r.content.read(n), str(r.url)


async def sondear(sesion, url: str, ua: str, ref: str) -> tuple[bool, str]:
    """Sigue master -> media -> primer segmento. Una lista que responde pero
    está vacía (p. ej. Pluto fuera de EE. UU.) cuenta como caída."""
    cab = {"User-Agent": ua or UA_POR_DEFECTO}
    if ref:
        cab["Referer"] = ref
    try:
        cuerpo, base = await _leer(sesion, url, cab, 65536)
        if not cuerpo:
            return False, "vacio"
        texto = cuerpo.decode("utf-8", "ignore")
        if texto.lstrip()[:1] == "<":
            return False, "html"
        if not texto.lstrip().lower().startswith("#extm3u"):
            return True, "bytes"
        for _ in range(3):
            lineas = [x.strip() for x in texto.splitlines() if x.strip() and not x.startswith("#")]
            if not lineas:
                return False, "playlist-vacia"
            destino = urljoin(base, lineas[0])
            if ".m3u8" in destino.split("?")[0].lower():
                cuerpo, base = await _leer(sesion, destino, cab, 65536)
                texto = cuerpo.decode("utf-8", "ignore")
                if not texto.lstrip().lower().startswith("#extm3u"):
                    return False, "variante-invalida"
                continue
            seg, _ = await _leer(sesion, destino, cab, 2048)
            return (True, "hls") if seg else (False, "segmento-vacio")
        return False, "demasiados-saltos"
    except asyncio.TimeoutError:
        return False, "timeout"
    except Exception as e:  # noqa: BLE001
        return False, str(e) if isinstance(e, RuntimeError) else type(e).__name__


async def comprobar(canales: list[Canal], concurrentes: int, timeout: int):
    sem = asyncio.Semaphore(concurrentes)
    conector = aiohttp.TCPConnector(limit=concurrentes, ssl=False)
    t = aiohttp.ClientTimeout(total=timeout, connect=6)
    hechos = 0
    inicio = time.time()

    async with aiohttp.ClientSession(connector=conector, timeout=t) as s:
        async def uno(c: Canal):
            nonlocal hechos
            async with sem:
                ua, ref = cabeceras(c)
                c.vivo, c.detalle = await sondear(s, c.url, ua, ref)
            hechos += 1
            if hechos % 200 == 0:
                print(f"  {hechos}/{len(canales)}  ({time.time() - inicio:.0f}s)", flush=True)
        await asyncio.gather(*(uno(c) for c in canales))


async def modo_probar(urls: list[str]):
    t = aiohttp.ClientTimeout(total=12, connect=6)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=t) as s:
        for u in urls:
            ok, d = await sondear(s, u, "", "")
            print(f"{'VIVO ' if ok else 'CAIDO'} {d:10s} {u}")


def main():
    ap = argparse.ArgumentParser(description="Filtra canales por idioma/fútbol y funcionamiento")
    ap.add_argument("entrada", nargs="?", default="datos/iptv-org_all.m3u")
    ap.add_argument("-o", "--salida", default="datos/canales_buenos.m3u")
    ap.add_argument("-c", "--concurrentes", type=int, default=40)
    ap.add_argument("-t", "--timeout", type=int, default=20)
    ap.add_argument("--sin-comprobar", action="store_true", help="solo filtrar por idioma/fútbol")
    ap.add_argument("--probar", nargs="+", metavar="URL", help="comprobar URLs sueltas y salir")
    a = ap.parse_args()

    if a.probar:
        asyncio.run(modo_probar(a.probar))
        return

    entrada, salida = Path(a.entrada), Path(a.salida)
    if not entrada.exists():
        sys.exit(f"No encontrado: {entrada}")

    todos = parse(entrada)
    print(f"Leídos: {len(todos)} canales")
    candidatos = []
    for c in todos:
        c.motivo = decide(c)
        if c.motivo:
            candidatos.append(c)
    n_fut = sum(1 for c in candidatos if c.motivo == "futbol")
    print(f"Pasan idioma/fútbol: {len(candidatos)} (de ellos por fútbol: {n_fut})")

    if a.sin_comprobar:
        for c in candidatos:
            c.vivo, c.detalle = True, "sin comprobar"
    else:
        print(f"Comprobando {len(candidatos)} streams ({a.concurrentes} a la vez)...")
        asyncio.run(comprobar(candidatos, a.concurrentes, a.timeout))

    buenos = [c for c in candidatos if c.vivo]
    with open(salida, "w", encoding="utf-8", newline="\n") as f:
        f.write("#EXTM3U\n")
        for c in buenos:
            f.write(c.extinf + "\n")
            for e in c.extras:
                f.write(e + "\n")
            f.write(c.url + "\n")

    informe = salida.with_name(salida.stem + "_informe.csv")
    with open(informe, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["nombre", "pais", "grupo", "motivo", "vivo", "detalle", "url"])
        for c in todos:
            w.writerow([c.nombre, c.pais, c.grupo, c.motivo or "descartado-idioma",
                        "si" if c.vivo else ("no" if c.motivo else ""), c.detalle, c.url])

    print(f"\nOK: {len(buenos)} canales -> {salida}")
    print(f"Informe: {informe}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Regenera todo, en orden. Si un paso falla, se para y deja lo anterior como estaba.
  1. descarga iptv-org (solo si la descarga es válida)
  2. filtrar_canales.py   -> canales_buenos.m3u
  3. listas_tdt.py        -> listas\TDT.m3u
  4. maestra.py           -> canales_maestra.m3u
  5. listas_por_proveedor.py y listas_por_tema.py -> listas\*.m3u
Log: actualizar.log
"""
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent   # raíz del proyecto
LOG = AQUI / "datos" / "actualizar.log"
URL = "https://iptv-org.github.io/iptv/index.m3u"
PASOS = [
    ["filtrar_canales.py", "datos/iptv-org_all.m3u", "-o", "datos/canales_buenos.m3u"],
    ["listas_tdt.py"],
    ["maestra.py"],
    ["listas_por_proveedor.py"],
    ["listas_por_tema.py"],
]


def log(msg):
    linea = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(linea, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def descargar():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    datos = urllib.request.urlopen(req, timeout=60).read()
    if not datos.startswith(b"#EXTM3U") or datos.count(b"#EXTINF") < 5000:
        raise RuntimeError(f"descarga no válida ({len(datos)} bytes)")
    (AQUI / "datos" / "iptv-org_all.m3u").write_bytes(datos)
    log(f"iptv-org descargado: {datos.count(b'#EXTINF')} canales")


def main():
    log("=== inicio ===")
    try:
        descargar()
    except Exception as e:  # noqa: BLE001
        log(f"AVISO: no se pudo descargar ({e}); se usa la copia anterior")
    for paso in PASOS:
        r = subprocess.run([sys.executable, "-I", str(AQUI / "scripts" / paso[0]), *paso[1:]], cwd=AQUI,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        ultima = (r.stdout.strip().splitlines() or [""])[-1]
        if r.returncode != 0:
            log(f"FALLO en {paso[0]}: {(r.stderr or r.stdout)[-300:]}")
            sys.exit(1)
        log(f"{paso[0]}: {ultima}")
    log("=== fin ===")


if __name__ == "__main__":
    main()

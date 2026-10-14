# Nandoflix — Implementación completa (handoff)

Documento maestro con **todo lo montado** en el PC `nando-pc` para ver TV/deporte/anime en
directo (Jellyfin + IPTV + mpv + TDT), **qué se hizo, por qué y cómo reproducirlo desde cero
en otro ordenador**. Los scripts van incrustados tal cual.

> TL;DR: Jellyfin sirve TV en directo con dos sintonizadores M3U (TDT español oficial + una
> lista internacional propia filtrada/validada cada día). Además hay dos lanzadores de escritorio
> ("pins") que abren las listas en **mpv** (más ligero que Jellyfin en este hardware). En este
> PC, para el día a día, **mpv gana**.

---

## 1. Contexto (hardware y sistema)

| Dato | Valor |
|---|---|
| Equipo | `nando-pc` (usuario `nando`) |
| CPU | AMD Ryzen 3 3250U (2C/4T) |
| RAM | ~5.2 GiB |
| GPU | iGPU **AMD Radeon Vega 3** (Picasso, `1002:15D8`) |
| SO | Ubuntu con GNOME, sesión **Wayland** |
| IP LAN | `192.168.1.128` |
| Jellyfin | 12.2.0 (`jellyfin-server`/`-web`/`-ffmpeg8` 12.2+ubu2604) |
| mpv | del sistema (VA-API operativo: HEVC/H.264 por hardware) |
| Python | 3.14 (stdlib) + Pillow 12 para los iconos |

Limitación clave: poca RAM y GPU integrada → **evitar transcodificar**. mpv reproduce
directo (hardware); Jellyfin transcodifica y consume más.

---

## 2. Arquitectura

```
                        ┌────────────────────────────────────────────┐
   iptv-org (diario)    │  filtra_final.py  (cron 04:00)              │
   https://iptv-org...  │  1) descarga index.m3u                      │
        │               │  2) filtra ES/UK/US/JP + anime             │
        └──────────────>│  3) valida cada enlace con ffprobe (paralelo)│
                        │  4) descarta muertos, conserva vivos + geo  │
                        └───────────────┬────────────────────────────┘
                                        │ escribe
                                        v
                        ~/xteve/iptv_filtrado.m3u   (~2051 canales)
                                        │
              ┌─────────────────────────┼──────────────────────────┐
              │ servir                   │ Jellyfin                 │ mpv (pins)
              v                          v                          v
   python3 -m http.server 8899   Tuner M3U "IPTV Internacional"   iptv.sh / tdt.sh
   http://192.168.1.128:8899/…   (Live TV)                        abren listas en mpv
```

TDTChannels (español, 576 canales) entra **directo** a Jellyfin y a su propio pin mpv, sin
pasar por el filtro.

---

## 3. Componentes

### 3.1 Jellyfin (servidor de medios / Live TV)
- Escucha en `0.0.0.0:8096` → UI: `http://localhost:8096` o `http://192.168.1.128:8096`.
- **Live TV** con dos sintonizadores M3U (`TunerHosts` en `/etc/jellyfin/livetv.xml`):
  1. **TDTChannels** — `https://www.tdtchannels.com/lists/tv.m3u8` (576 canales ES).
  2. **IPTV Internacional** — `http://192.168.1.128:8899/iptv_filtrado.m3u` (lista propia).
- **EPG**: XMLTV `https://www.tdtchannels.com/epg/TV.xml.gz` (guía de TDT).
- La app "Nandoflix" es una **PWA con Epiphany** apuntando a `http://localhost:8096/web/index.html#/livetv`.

> Nota UI: en Jellyfin 12.2 el campo **"Nombre amigable"** del tuner solo aparece al **editar**
> un tuner existente (clic en su fila), no al añadirlo. Si queda vacío, el tuner se muestra como `m3u`.

### 3.2 Pipeline IPTV internacional (`filtra_final.py`)
- Fuente: `https://iptv-org.github.io/iptv/index.m3u` (listado comunitario mundial).
- Filtra por `tvg-id` con sufijos de país (`.es@ .uk@ .gb@ .us@ .jp@ …`) **o** por nombre de anime.
- **Valida cada enlace** con `ffprobe` en paralelo (32 workers, timeout 7 s):
  - `ok`  → tiene vídeo → se conserva.
  - `geo` → geo-bloqueado por etiqueta **o** error 401/403 → se conserva (**para usar con VPN**).
  - `dead`→ timeout/404/5xx/datos inválidos → **se descarta**.
- Como cada día parte del listado fresco, un canal caído **que mañana funcione se re-incluye solo**
  (no hay lista negra permanente).
- Salida: `~/xteve/iptv_filtrado.m3u`. Log: `~/xteve/filtro.log`.
- Se sirve por HTTP en el puerto `8899` (cron `@reboot`) para que Jellyfin lo consuma.
- **Cron**: `0 4 * * *` re-ejecuta el filtro+validación cada madrugada.

### 3.3 Pins de mpv (TDT e IPTV)
Dos lanzadores `.desktop` en el dock, con iconos distintos:

| Pin | Abre | Lista | Icono |
|---|---|---|---|
| **TDT Nandoflix** | mpv | TDT español (descarga fresca de TDTChannels) | azul |
| **IPTV Nandoflix** | mpv | lista internacional filtrada/validada | violeta (globo) |

Ambos usan la misma mecánica: limpian la lista a `#EXTM3U` + pares `#EXTINF:-1,Nombre` / url y
lanzan mpv con **caja OSD de fondo negro** (`--osd-back-color=#FF000000`), `--force-window` y un
`--wayland-app-id` propio (para el icono/ventana).

### 3.4 (Apéndice) Stremio — diagnóstico del lag
- El lag/buffer de Stremio en este PC es el **bug upstream #63** de `stremio-linux-shell`
  (app-id `mpv-set-gpu-video-processing` no soportado): el `libmpv` que trae la app tiene el
  **hwdec desactivado** → **HEVC se decodifica por software** (CPU a tope). El H.264 va bien.
- VA-API **sí** funciona en el sistema (mpv/ffmpeg decodifican HEVC por hardware). El problema
  es exclusivo de la app Stremio en AMD.
- Actualizar Stremio **no** lo arregló. Se descartó el parche externo (frágil ante updates).
- Conclusión: para directo, **mpv/Jellyfin**; para VOD/anime con subs, Stremio + Real-Debrid /
  Anime Kitsu sigue valiendo, asumiendo el coste de CPU en HEVC.

---

## 4. Scripts (código completo)

### 4.1 `~/xteve/filtra_final.py`
```python
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
```

### 4.2 `~/.local/share/nandoflix/tdt.sh` (pin TDT)
```bash
#!/usr/bin/env bash
# TDT Nandoflix - refresca la lista oficial, la limpia y la abre en mpv.
# (esquema consensuado con la otra instancia: app-id en minusculas + nombres limpios)
LIST_URL="https://www.tdtchannels.com/lists/tv.m3u8"
OUT="$HOME/.local/share/nandoflix/tdt_channels.m3u"
tmp=$(mktemp /tmp/tdt-dl-XXXXXX.m3u8)

curl -s -m 25 "$LIST_URL" -o "$tmp" || { rm -f "$tmp"; exit 1; }
# Deja solo "#EXTM3U" + pares "#EXTINF:-1,Nombre" / url (fuera logos y cabecera url-tvg)
{ printf '#EXTM3U\n'; awk '/^#EXTINF/ { n = substr($0, index($0, ",") + 1); if (getline u > 0) printf "#EXTINF:-1,%s\n%s\n", n, u }' "$tmp"; } > "$OUT"
rm -f "$tmp"

exec mpv --force-window=yes \
  --wayland-app-id=tdt-nandoflix --x11-name=tdt-nandoflix \
  --osd-border-style=background-box --osd-back-color=#FF000000 --osd-color=#FFFFFFFF \
  --playlist="$OUT"
```

### 4.3 `~/.local/share/nandoflix/iptv.sh` (pin IPTV internacional)
```bash
#!/usr/bin/env bash
# IPTV Nandoflix - lista internacional filtrada y validada, abierta en mpv.
# (esquema consensuado con la otra instancia: app-id en minusculas + nombres limpios)
SRC="$HOME/xteve/iptv_filtrado.m3u"
OUT="$HOME/.local/share/nandoflix/iptv_channels.m3u"

# Limpia la lista: deja sólo "#EXTM3U" + pares "#EXTINF:-1,Nombre" / url
python3 - "$SRC" "$OUT" <<'PY'
import sys
src, out = sys.argv[1], sys.argv[2]
res = ["#EXTM3U"]
extinf = None
with open(src, encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.rstrip("\n")
        if line.startswith("#EXTINF"):
            extinf = line
        elif line and not line.startswith("#") and extinf is not None:
            name = extinf[extinf.rfind(",") + 1:].strip()
            res.append(f"#EXTINF:-1,{name}")
            res.append(line)
            extinf = None
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(res) + "\n")
PY

exec mpv --force-window=yes \
  --wayland-app-id=iptv-nandoflix --x11-name=iptv-nandoflix \
  --osd-border-style=background-box --osd-back-color=#FF000000 --osd-color=#FFFFFFFF \
  --playlist="$OUT"
```

### 4.4 `make_icons.py` (genera los iconos)
Ver `media/iptv/make_icons.py` (Pillow). Dibuja el icono azul "pantalla" de TDT y el violeta
"globo" de IPTV, 512×512.

### 4.5 Scripts históricos (superseded)
`media/iptv/legacy/filtra_iptv.py` (filtro por `tvg-country`) y `filtra_iptv_v2.py` (filtro por
`group-title`). Evolucionaron a `filtra_final.py`. Se conservan por historial.

---

## 5. Lanzadores `.desktop`

### `~/.local/share/applications/tdt-nandoflix.desktop`
```ini
[Desktop Entry]
Name=TDT Nandoflix
GenericName=Televisión en directo
Comment=576 canales TDT — lista oficial TDTChannels con EPG
Exec=/home/nando/.local/share/nandoflix/tdt.sh
Icon=/home/nando/.local/share/icons/tdt-nandoflix.png
Terminal=false
Type=Application
Categories=AudioVideo;TV;Video;
Keywords=tv;tdt;canal;television;nandoflix;
StartupNotify=true
StartupWMClass=tdt-nandoflix
```

### `~/.local/share/applications/iptv-nandoflix.desktop`
```ini
[Desktop Entry]
Name=IPTV Nandoflix
GenericName=Televisión internacional
Comment=2051 canales internacionales filtrados y validados — lista propia (ES/UK/US/JP + Anime)
Exec=/home/nando/.local/share/nandoflix/iptv.sh
Icon=/home/nando/.local/share/icons/iptv-nandoflix.png
Terminal=false
Type=Application
Categories=AudioVideo;TV;Video;
Keywords=iptv;internacional;anime;tv;canal;nandoflix;
StartupNotify=true
StartupWMClass=iptv-nandoflix
```

> Para que aparezcan en el dock (GNOME) se añaden a `org.gnome.shell favorite-apps`:
> ```bash
> gsettings get org.gnome.shell favorite-apps
> # insertar 'iptv-nandoflix.desktop' justo después de 'tdt-nandoflix.desktop'
> ```
> Si el icono no aparece al instante: cerrar/abrir sesión.

También existe `jellyfin-nandoflix.desktop` (PWA Epiphany → Jellyfin Live TV).

---

## 6. Config de Jellyfin — `/etc/jellyfin/livetv.xml` (extracto clave)

```xml
<TunerHosts>
  <!-- 1) TDT español -->
  <TunerHostInfo>
    <Id>3a54f97a1998402183d1acce3e41ed4d</Id>
    <Url>https://www.tdtchannels.com/lists/tv.m3u8</Url>
    <Type>m3u</Type>
    <FriendlyName>TDTChannels</FriendlyName>
    <AllowHWTranscoding>true</AllowHWTranscoding>
    <TunerCount>0</TunerCount>
  </TunerHostInfo>
  <!-- 2) IPTV internacional (lista propia filtrada/validada) -->
  <TunerHostInfo>
    <Id>5daa5e6a2a2244e1a55db31a76941a45</Id>
    <Url>http://192.168.1.128:8899/iptv_filtrado.m3u</Url>
    <Type>m3u</Type>
    <AllowHWTranscoding>false</AllowHWTranscoding>
    <TunerCount>0</TunerCount>
  </TunerHostInfo>
</TunerHosts>
<ListingProviderInfo>
  <Type>xmltv</Type>
  <Path>https://www.tdtchannels.com/epg/TV.xml.gz</Path>
</ListingProviderInfo>
```
(El `FriendlyName` del 2º tuner quedó sin poner; por eso se muestra como `m3u`. Se puede editar
desde la UI: **clic en la fila del tuner** → "Nombre amigable".)

---

## 7. Cron y servicio HTTP

```cron
# 1) Validación diaria de la lista internacional
0 4 * * * /usr/bin/python3 /home/nando/xteve/filtra_final.py >> /home/nando/xteve/filtro.log 2>&1
# 2) Servidor HTTP local que sirve el M3U a Jellyfin
@reboot cd /home/nando/xteve && python3 -m http.server 8899 --bind 0.0.0.0 >/dev/null 2>&1 &
```

---

## 8. Reproducir desde cero (otro PC)

1. **Jellyfin** (Ubuntu/Debian):
   ```bash
   curl -fsSL https://repo.jellyfin.org/install-debuntu.sh | sudo bash
   ```
   · Abre `http://localhost:8096`, crea la cuenta admin.
2. **Scripts**:
   ```bash
   mkdir -p ~/xteve ~/.local/share/nandoflix ~/.local/share/applications ~/.local/share/icons
   cp media/iptv/filtra_final.py            ~/xteve/
   cp media/iptv/launchers/tdt.sh           ~/.local/share/nandoflix/
   cp media/iptv/launchers/iptv.sh          ~/.local/share/nandoflix/
   cp media/iptv/desktop/*.desktop          ~/.local/share/applications/
   cp media/iptv/icons/*.png                ~/.local/share/icons/
   chmod +x ~/.local/share/nandoflix/*.sh ~/xteve/filtra_final.py
   ```
3. **Primera generación de la lista** (tarda ~8-10 min, valida ~2500 enlaces):
   ```bash
   python3 ~/xteve/filtra_final.py       # deja ~/xteve/iptv_filtrado.m3u
   ```
4. **Servidor HTTP** (o usa systemd/servicio propio):
   ```bash
   cd ~/xteve && python3 -m http.server 8899 --bind 0.0.0.0 &
   ```
   Comprueba: `curl -s http://localhost:8899/iptv_filtrado.m3u | head -3`
5. **Cron**: edita `crontab -e` y añade las dos líneas del apartado 7 (ajusta IP/rutas).
6. **Jellyfin → Live TV**:
   - Ajustes → **Live TV** → añade sintonizador **M3U** con
     `http://TU_IP:8899/iptv_filtrado.m3u`.
   - Añade otro con `https://www.tdtchannels.com/lists/tv.m3u8` (TDT).
   - EPG XMLTV: `https://www.tdtchannels.com/epg/TV.xml.gz`.
   - Pulsa **Escanear canales**.
7. **Pins mpv**: copia los `.desktop` a `~/.local/share/applications/`, los iconos a
   `~/.local/share/icons/` y edita las rutas internas si tu `$HOME` difiere.
   Añádelos al dock con `gsettings` (apartado 5). Verifica `mpv` instalado (`sudo apt install mpv`).
8. **Iconos** (opcional): `python3 media/iptv/make_icons.py` (requiere `pip install pillow`).

**Dependencias**: `python3`, `ffmpeg`/`ffprobe`, `mpv`, (opcional) Docker para xTeVe.

---

## 9. Mapa de rutas (este PC)

| Ruta | Qué es |
|---|---|
| `~/xteve/filtra_final.py` | filtro + validación (cron) |
| `~/xteve/iptv_filtrado.m3u` | lista internacional resultante |
| `~/xteve/filtro.log` | log del filtro |
| `~/xteve/docker-compose.yml`, `~/xteve/xteve/` | xTeVe (docker, ensayo) |
| `~/.local/share/nandoflix/tdt.sh` | lanzador TDT (mpv) |
| `~/.local/share/nandoflix/iptv.sh` | lanzador IPTV (mpv) |
| `~/.local/share/nandoflix/*_channels.m3u` | listas limpias que abre mpv |
| `~/.local/share/applications/*-nandoflix.desktop` | pins del dock |
| `~/.local/share/icons/*-nandoflix.png` | iconos de los pins |
| `/etc/jellyfin/livetv.xml` | sintonizadores + EPG |
| `/var/lib/jellyfin/data/jellyfin.db` | BD SQLite (canales tipo `LiveTvChannel`) |

---

## 10. Estado / métricas (2026-10-10)

- Filtro tras país/anime: **2502 canales**.
- Validación: **vivos 1216 + geo 835 = 2051 guardados**, **451 muertos descartados**.
- ~52 % de la lista cruda de iptv-org estaba caída o geo-bloqueada (la fuente no verifica enlaces).
- Jellyfin: tras escanear, ~3057 `LiveTvChannel` (2481 internacionales + 576 TDT).

---

## 11. Pendientes / ideas

- **Auto-refresco al abrir el pin** (lanzar `filtra_final.py` antes de mpv, sin esperar a las 4:00).
- **Favoritos / orden / número de canal** en el OSD de mpv.
- **EPG** también para la lista internacional.
- **Auto-escaneo de Jellyfin** tras regenerar el M3U (API key) — hoy hay que pulsar "Escanear canales".
- Renombrar el 2º tuner a "IPTV Internacional" (poner el *Nombre amigable*).

---

## 12. Decisiones y aprendizajes

- **mpv > Jellyfin** para este hardware (no transcodifica; Jellyfin sí come CPU/RAM).
- **Validar los enlaces** es imprescindible: iptv-org refresca la lista pero no comprueba que
  los streams sigan vivos.
- **Conservar geo-bloqueados** (no descartarlos): pueden funcionar con VPN.
- Re-validar diario desde el listado fresco ⇒ auto-recuperación de canales que vuelven.
- El pin y sus archivos **no pisan** los de TDT (nombres y `app-id` independientes).

---

*Generado como handoff. Repo: `github.com/fvilpaz/nando-tv`.*

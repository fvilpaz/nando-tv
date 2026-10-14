# Nandoflix — IPTV Internacional (ES/UK/US/JP + Anime) — 2026-10-09

## Qué se ha montado
- **Lista M3U filtrada** (2481 canales): España (`.es`), UK (`.uk`), US (`.us`), Japón (`.jp`) + canales de anime (Crunchyroll, Animax, Toonami, Pluto TV Anime, etc.).
- **Fuente**: iptv-org (GitHub) — se actualiza diario.
- **Script de filtrado**: `~/xteve/filtra_final.py` (usa `tvg-id` sufijos `.es@`, `.uk@`, `.us@`, `.jp@` + regex anime).
- **Servidor HTTP** en puerto **8899** sirviendo el M3U filtrado: `http://192.168.1.128:8899/iptv_filtrado.m3u`
- **Cron instalado**:
  - `0 4 * * *` → refresca la lista cada madrugada (`filtra_final.py`)
  - `@reboot` → levanta el server HTTP en puerto 8899

## Archivos clave
| Archivo | Qué hace |
|---------|----------|
| `~/xteve/filtra_final.py` | Descarga iptv-org, filtra por sufijo país en `tvg-id` + anime, genera `iptv_filtrado.m3u` |
| `~/xteve/iptv_filtrado.m3u` | M3U resultante (2481 canales) |
| `~/xteve/filtro.log` | Log del cron diario |
| `crontab -l` | Ver tareas programadas |

## Probar AHORA (antes de irte)
1. **Verifica que el M3U sirve**:
   ```bash
   curl -s http://192.168.1.128:8899/iptv_filtrado.m3u | head -5
   # Debe salir #EXTM3U y primeras líneas #EXTINF
   ```

2. **Añade el tuner en Jellyfin (UI web, 30 seg)**:
   - Abre Jellyfin → **Live TV** → **Tuners** → **Add M3U Tuner**
   - Name: `IPTV Internacional (ES/UK/US/JP + Anime)`
   - M3U URL: `http://192.168.1.128:8899/iptv_filtrado.m3u`
   - ☑ Enable auto channel mapping / numbering → **Save**
   - **Scan channels** → **Refresh Guide**

3. **Comprueba en la guía de TV** (Live TV → Guía): deberías ver canales 3Cat, BBC, Pluto TV, Crunchyroll, Animax, Toonami, etc. mezclados con tu TDT.

## Si algo falla al volver
- Logs del filtro: `cat ~/xteve/filtro.log`
- Regenera a mano: `python3 ~/xteve/filtra_final.py`
- Verifica server: `curl -s http://localhost:8899/iptv_filtrado.m3u | head -3`
- Revisa cron: `crontab -l`

## Notas
- El EPG de iptv-org no está disponible (404 en su repo). Jellyfin mostrará solo nombres de canal; para guía completa necesitarías EPG externo (xmltv) o xTeVe funcionando (se intentó pero su BD interna dio problemas).
- Para anime con subs en castellano, **Stremio + Anime Kitsu / Comet / MediaFusion** sigue siendo la mejor vía; esto es solo canales lineales FAST.
- Si quieres afinar el filtro (quitar religiosos, solo ciertos géneros), edita `filtra_final.py` (lista `PAISES_ID` / `ANIME_RE`).

## Actualización 2026-10-10 — validación de enlaces
- Problema detectado: ~50% de los 2481 canales estaban caídos/geo-bloqueados (iptv-org refresca la lista pero NO verifica que los enlaces sigan vivos).
- `filtra_final.py` reescrito: ahora **prueba cada enlace con `ffprobe`** (paralelo, timeout 7s) y descarta los muertos. Conserva vivos + **geo-bloqueados** (para usar con VPN). Como parte del listado fresco a diario, un canal caído que mañana funcione se re-incluye solo.
- Backup del script: `filtra_final.py.bak-20261010`. Backup del M3U: `iptv_filtrado.m3u.bak-*`.
- Cron sin cambios (`0 4 * * *`), así que la validación corre cada madrugada.
- **Pendiente**: tras regenerar el M3U, Jellyfin NO re-escanea solo → hay que pulsar "Escanear canales" del tuner `IPTV Internacional`, o automatizarlo vía API (requiere API key de Jellyfin).

## Pin de escritorio / dock (2026-10-10)
- Creado pin **"IPTV Nandoflix"** en el dock, **justo a la derecha del de TDT** (`tdt-nandoflix.desktop`). No pisa nada.
- Abre con **mpv** la lista internacional, con la misma funcionalidad que el de TDT (caja OSD **fondo negro**, nombres limpios, `--force-window`).
- Archivos:
  - `~/.local/share/applications/iptv-nandoflix.desktop`
  - `~/.local/share/nandoflix/iptv.sh` → limpia `~/xteve/iptv_filtrado.m3u` a `~/.local/share/nandoflix/iptv_channels.m3u` y lo abre en mpv.
  - `~/.local/share/icons/iptv-nandoflix.png` (globo **violeta**; el de TDT es azul).
- El pin TDT (`tdt.sh`, `tdt_channels.m3u`, icono) queda **intacto**.
- Conclusión del usuario: **mpv va mejor que Jellyfin en este PC** (Jellyfin transcodifica y come CPU/RAM; mpv reproduce directo con la Vega 3).

## Ideas pendientes (para la próxima)
- **Auto-refresco** al abrir el pin (lanzar `filtra_final.py` antes de mpv, sin esperar al cron de las 4:00).
- **Favoritos / orden / número de canal** mostrado en el OSD.
- **EPG (guía)** para TDT y/o internacional.
- Automatizar el re-escaneo de Jellyfin tras regenerar el M3U (API key).
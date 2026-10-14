# nandflix — versión Windows

Lo mismo que el montaje de Linux de este repo (`media/iptv`), pero para **Windows + mpv**,
sin Jellyfin ni cron: listas comprobadas, sin repetidos, abiertas directamente en mpv.

## Qué hace
1. Descarga `iptv-org` (índice completo) y la lista TDT de TDTChannels.
2. Filtra por idioma (español, inglés, japonés; fútbol de cualquier idioma) y excluye
   religiosos y feeds en alemán, italiano, finés, polaco, checo y ucraniano.
3. **Comprueba cada stream de verdad**: sigue master → media → primer segmento. Una lista que
   responde pero está vacía (Pluto fuera de EE. UU.) cuenta como caída.
4. Une TDT + iptv-org y deja un enlace por canal.
5. Reparte en listas por temática (Deportes, Música, Cine y series) y por proveedor
   (Rakuten, Samsung, Tubi, Roku, Plex, Pluto…).

## Archivos
| Script | Qué hace |
|---|---|
| `scripts/actualizar.py` | Lanza los pasos en orden y escribe `datos/actualizar.log` |
| `scripts/filtrar_canales.py` | Idioma + fútbol + comprobación real. `--probar URL` prueba enlaces sueltos |
| `scripts/listas_tdt.py` | TDTChannels comprobado, sin religiosos, sin repetidos |
| `scripts/maestra.py` | Une y quita repetidos (mismo nombre y mismo país) |
| `scripts/listas_por_tema.py` · `listas_por_proveedor.py` | Reparto en listas |
| `scripts/ver_canales.bat` · `ver_lista.bat` | Abren mpv con la maestra o con una lista |

## Cómo se usa
```bat
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python scripts\actualizar.py      :: ~3 min
scripts\ver_canales.bat                        :: abre mpv con datos\canales_maestra.m3u
scripts\ver_lista.bat "Deportes"               :: abre listas\Deportes.m3u
```
Estructura esperada junto a `scripts/`: `datos/` y `listas/` (se crean solas al ejecutar).
Requisitos: Python 3, `aiohttp`, y mpv (`winget install shinchiro.mpv`).

## Límites conocidos
- Un canal con etiqueta `SD`/`HD` no dice su idioma: puede colarse alguno en otra lengua.
- Pluto TV solo da imagen con salida en EE. UU.; su lista va **sin comprobar**.
- El resultado varía unos canales entre ejecuciones (streams que tardan en responder).
- Las listas generadas no se versionan: se regeneran.

## Pendiente
- Pasar a Linux las mejoras de aquí (comprobar los "geo", quitar repetidos, excluir religiosos)
  en una rama y probándolas en `nando-pc`.

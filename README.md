# nando-tv

Colección de herramientas y configuraciones caseras de `nando-pc`. Incluye el montaje de
**TV en directo** (Jellyfin + IPTV internacional filtrada + TDT + reproductor mpv) y la
documentación del proyecto `Nandflix`.

## Contenido

```
.
├── NANDOFLIX_IMPLEMENTACION.md   # ⭐ Documento maestro: qué se hizo y cómo reproducirlo
├── media/                        # Montaje de TV / medios
│   ├── iptv/
│   │   ├── filtra_final.py        # filtra iptv-org y valida enlaces (ffprobe)
│   │   ├── legacy/                # versiones anteriores del filtro (histórico)
│   │   ├── launchers/             # tdt.sh, iptv.sh (abren listas en mpv)
│   │   ├── desktop/               # pins .desktop para el dock
│   │   ├── icons/                 # iconos de los pins
│   │   ├── make_icons.py          # genera los iconos (Pillow)
│   │   └── xteve/                 # docker-compose + settings de xTeVe (ensayo)
│   └── jellyfin/
│       └── livetv.xml             # sintonizadores M3U + EPG
└── project/                      # Metodología SDD + docs del proyecto Nandflix
```

## Resumen del montaje

- **Jellyfin** (Live TV) con dos sintonizadores M3U: **TDT español** (TDTChannels, 576 canales)
  y **IPTV internacional** (lista propia: ES/UK/US/JP + anime).
- La lista internacional la genera `filtra_final.py` cada día (cron) desde `iptv-org`,
  **descartando enlaces muertos** y conservando los que funcionan + los geo-bloqueados (VPN).
- Se sirve por HTTP en el puerto `8899` y Jellyfin la consume.
- Dos "pins" de escritorio abren las listas en **mpv** (más ligero que Jellyfin en este PC),
  con OSD de fondo negro.

Los detalles, el código completo y los pasos de instalación están en
**[`NANDOFLIX_IMPLEMENTACION.md`](NANDOFLIX_IMPLEMENTACION.md)**.

## Requisitos

`python3`, `ffmpeg`/`ffprobe`, `mpv`. Opcional: Pillow para los iconos, Docker para xTeVe.

## Aviso

Configuración personal de un equipo concreto (Rutas `$HOME`, IP LAN `192.168.1.128`). Ajústalas
al reproducir en otro PC. Las listas M3U en sí no se versionan (se regeneran).

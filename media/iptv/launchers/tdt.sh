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
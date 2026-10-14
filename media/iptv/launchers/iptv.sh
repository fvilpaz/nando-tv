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

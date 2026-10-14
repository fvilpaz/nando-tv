#!/usr/bin/env python3
import re, urllib.request, os

URL = "https://iptv-org.github.io/iptv/index.m3u"
OUT = os.path.expanduser("~/xteve/iptv_filtrado.m3u")

# Países por group-title / nombre (IPTV-org usa group-title como "News", "Sports", "Entertainment", "Animation", etc.)
# y a veces tvg-country con códigos ISO
PAISES_GRUPO = {"Spain", "UK", "United Kingdom", "USA", "United States", "Japan", "Japanese"}
PAISES_TVG = {"ES", "GB", "UK", "US", "JP"}
ANIME_RE = re.compile(r"(anime|crunchyroll|animax|toonami|ghibli|wakanim|animetime|animeplus|anione|animeone)", re.I)

# También incluimos grupos genéricos de habla inglesa/española que no sean solo anime
GRUPOS_UTILES = {"News", "Sports", "Entertainment", "General", "Music", "Kids", "Documentary", "Movies", "Series"}

data = urllib.request.urlopen("https://iptv-org.github.io/iptv/index.m3u", timeout=60).read().decode("utf-8", errors="replace")
lines = data.splitlines()
out = ["#EXTM3U"]
keep = False

for line in lines:
    line = line.rstrip("\n")
    if line.startswith("#EXTINF"):
        m_grp = re.search(r'group-title="([^"]*)"', line)
        grupo = m_grp.group(1) if m_grp else ""
        m_ctry = re.search(r'tvg-country="([^"]*)"', line)
        ctry = m_ctry.group(1) if m_ctry else ""
        name = line[line.rfind(",")+1:].strip() if "," in line else ""
        # Criterios:
        keep = (
            ctry in PAISES_TVG or
            grupo in PAISES_GRUPO or
            grupo in GRUPOS_UTILES or
            ANIME_RE.search(name)
        )
        if keep:
            out.append(line)
    elif line and not line.startswith("#"):
        if keep:
            out.append(line)
            keep = False
    elif line.startswith("#EXTM3U"):
        continue

with open(os.path.expanduser("~/xteve/iptv_filtrado.m3u"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

n = len([l for l in out if l.startswith("#EXTINF")])
print(f"OK: {n} canales")

#!/usr/bin/env python3
"""
Filtra la lista iptv-org M3U:
- Países: ES, GB, US, JP (tvg-country)
- Anime: regex sobre nombre (crunchyroll, animax, toonami, ghibli, wakanim, etc.)
Genera M3U filtrado listo para Jellyfin.
"""
import re, sys, urllib.request, gzip, os

URL_M3U = "https://iptv-org.github.io/iptv/index.m3u"
PAISES = {"ES", "GB", "US", "JP"}
ANIME_RE = re.compile(r"(anime|crunchyroll|animax|toonami|ghibli|wakanim|animetime|animeplus|anione|animeone)", re.I)

OUT_M3U = os.path.expanduser("~/xteve/iptv_filtrado.m3u")

def main():
    print("Descargando M3U...")
    data = urllib.request.urlopen(URL_M3U, timeout=60).read().decode("utf-8", errors="replace")
    lines = data.splitlines()
    out = ["#EXTM3U"]
    keep = False
    name = ""
    country = ""
    
    for line in lines:
        line = line.rstrip("\n")
        if line.startswith("#EXTINF"):
            # Extraer tvg-country y nombre
            m_country = re.search(r'tvg-country="([^"]*)"', line)
            country = m_country.group(1) if m_country else ""
            # Nombre = texto tras la última coma
            name = line[line.rfind(",")+1:].strip() if "," in line else ""
            keep = (country in PAISES) or bool(ANIME_RE.search(name))
            if keep:
                out.append(line)
        elif line and not line.startswith("#"):
            if keep:
                out.append(line)
                keep = False
        elif line.startswith("#EXTM3U"):
            continue  # reescribimos cabecera
    with open(OUT_M3U, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"OK: {len([l for l in out if l.startswith('#EXTINF')])} canales → {OUT_M3U}")

if __name__ == "__main__":
    main()

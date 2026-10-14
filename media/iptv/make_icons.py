#!/usr/bin/env python3
"""Genera los iconos de los pins Nandoflix (512x512) con Pillow.

- tdt-nandoflix.png  : degradado AZUL (TDT español)
- iptv-nandoflix.png : degradado VIOLETA con globo (IPTV internacional)

Uso:  python3 make_icons.py
Instala Pillow si falta: pip install pillow
"""
from PIL import Image, ImageDraw

W = H = 512


def gradient(c1, c2):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        for x in range(W):
            t = (x + y) / (W + H - 2)
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return img


def tv_icon():  # TDT (azul)
    img = gradient((23, 50, 125), (17, 100, 176))
    d = ImageDraw.Draw(img)
    w = (255, 255, 255)  # glifo blanco simple tipo pantalla
    d.rectangle([136, 176, 376, 336], outline=w, width=22)
    d.line([196, 336, 120, 400], fill=w, width=22)
    d.line([316, 336, 392, 400], fill=w, width=22)
    return img


def globe_icon():  # IPTV internacional (violeta)
    img = gradient((46, 16, 82), (176, 46, 158))
    d = ImageDraw.Draw(img)
    cx = cy = 256
    R, lw = 152, 24
    w = (255, 255, 255)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=w, width=lw)
    d.ellipse([cx - R // 2, cy - R, cx + R // 2, cy + R], outline=w, width=lw)
    d.ellipse([cx - R, cy - R // 2, cx + R, cy + R // 2], outline=w, width=lw)
    d.line([cx - R, cy, cx + R, cy], fill=w, width=lw)
    return img


if __name__ == "__main__":
    tv_icon().save("icons/tdt-nandoflix.png")
    globe_icon().save("icons/iptv-nandoflix.png")
    print("Iconos generados en icons/")

#!/usr/bin/env python3
"""Prancha do concept com GRADE de coordenadas (xf ao longo do comprimento, z altura).

Uso: python3 grid_concept.py <view> <saida.png>
Deixa legivel "onde" cada peca esta, em fracao do comprimento e da altura.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw
try:
    RES = Image.Resampling
except AttributeError:
    RES = Image
LANCZOS = RES.LANCZOS
D = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/"
view = sys.argv[1]; out = sys.argv[2]
m = np.load("/tmp/g2_%s.npy" % view).astype(bool)
im = Image.open(D + view + ".jpg").convert("RGB")
if im.size != (m.shape[1], m.shape[0]):
    im = im.resize((m.shape[1], m.shape[0]), LANCZOS)
ys, xs = np.where(m)
x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
c = im.crop((x0, y0, x1 + 1, y1 + 1))
H = 900
c = c.resize((int(c.width * H / c.height), H), LANCZOS)
W, Hc = c.size
img = Image.new("RGB", (W + 120, Hc + 60), (16, 16, 20))
img.paste(c, (60, 30))
d = ImageDraw.Draw(img)
for k in range(0, 21):
    f = k / 20.0
    x = 60 + int(f * W)
    d.line([(x, 30), (x, Hc + 30)], fill=(255, 90, 90) if k % 2 == 0 else (90, 90, 130), width=1)
    d.text((x - 8, 8), "%.2f" % f, fill=(255, 140, 140))
for k in range(0, 11):
    f = k / 10.0
    y = Hc + 30 - int(f * Hc)
    d.line([(60, y), (W + 60, y)], fill=(90, 200, 255) if k % 2 == 0 else (60, 80, 110), width=1)
    d.text((6, y - 6), "z%.1f" % f, fill=(140, 220, 255))
d.text((66, Hc + 36), "xf: 0=frente (esq) -> 1=traseira (dir)   |   z: 0=chao -> 1=topo", fill=(230, 230, 120))
img.save(out)
print("OK", out, img.size)

#!/usr/bin/env python3
"""Gerador de pranchas CONCEPT | MODELO para a auditoria de vision por regiao.

Uso:  python3 zones.py <versao> <saida.png> <view:f0:f1> [<view:f0:f1> ...]
Ex:   python3 zones.py w286 /tmp/el/z1.png side:0.18:0.62 top:0.25:0.45

Cada linha da prancha e uma vista recortada em alta resolucao, CONCEPT a esquerda
e MODELO a direita (passada PLANA, para comparar forma e cor, nao iluminacao).
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw

try:
    RES = Image.Resampling
except AttributeError:
    RES = Image
LANCZOS = RES.LANCZOS

D = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/"
P = "/opt/blender-runner/outputs/"


def crop_mask(m):
    ys, xs = np.where(m)
    return int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())


def pair(view, ver, f0, f1, hh=520):
    m = np.load("/tmp/g2_%s.npy" % view).astype(bool)
    im = Image.open(D + view + ".jpg").convert("RGB")
    if im.size != (m.shape[1], m.shape[0]):
        im = im.resize((m.shape[1], m.shape[0]), LANCZOS)
    y0, y1, x0, x1 = crop_mask(m)
    W = x1 - x0 + 1
    c1 = im.crop((x0 + int(f0 * W), y0, x0 + int(f1 * W), y1 + 1))
    c1 = c1.resize((max(1, int(c1.width * hh / c1.height)), hh), LANCZOS)
    mm = np.array(Image.open(P + "%sm-%s.png" % (ver, view)).convert("RGBA"))[:, :, 3] > 128
    y0m, y1m, x0m, x1m = crop_mask(mm)
    W2 = x1m - x0m + 1
    src = P + "%sf-%s.png" % (ver, view)
    if not os.path.exists(src):
        src = P + "%s-%s.png" % (ver, view)
    im2 = Image.open(src).convert("RGB").crop(
        (x0m + int(f0 * W2), y0m, x0m + int(f1 * W2), y1m + 1))
    c2 = im2.resize((max(1, int(im2.width * hh / im2.height)), hh), LANCZOS)
    return c1, c2


def main():
    ver = sys.argv[1]
    out = sys.argv[2]
    specs = []
    for a in sys.argv[3:]:
        p = a.split(":")
        specs.append((p[0], float(p[1]), float(p[2])))
    hh = 520
    cs = [pair(v, ver, a, b, hh) for v, a, b in specs]
    w = max(c1.width + c2.width for c1, c2 in cs) + 60
    img = Image.new("RGB", (w, len(cs) * (hh + 30) + 6), (16, 16, 20))
    d = ImageDraw.Draw(img)
    y = 0
    for (v, a, b), (c1, c2) in zip(specs, cs):
        d.text((6, y + hh // 2), "%s %.2f-%.2f" % (v.upper(), a, b), fill=(255, 255, 90))
        d.text((92, y + 4), "CONCEPT", fill=(255, 255, 90))
        d.text((c1.width + 116, y + 4), "MODELO " + ver.upper(), fill=(120, 220, 255))
        img.paste(c1, (88, y + 26))
        img.paste(c2, (c1.width + 112, y + 26))
        y += hh + 30
    img.save(out)
    print("OK %s %s" % (out, img.size))


if __name__ == "__main__":
    main()

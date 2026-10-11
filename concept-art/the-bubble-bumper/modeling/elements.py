#!/usr/bin/env python3
"""Pranchas de ELEMENTO: uma peca por prancha, concept | modelo, em alta resolucao.

Regra (concept-driven-3d-modeling): um veredito por VISTA esconde qual elemento esta
falhando. Cada elemento ganha seu proprio recorte, com ~7% de padding (recorte no bbox
corta a base das rodas/para-choque e o revisor responde "nao avaliavel").

Uso:  python3 elements.py <versao> <dir_saida> [elemento ...]
Sem elementos: gera todos.

Cada saida: EL-<nome>.png  (uma linha por vista do elemento, concept | modelo)
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw

try:
    RES = Image.Resampling
except AttributeError:
    RES = Image
LANCZOS, NEAREST = RES.LANCZOS, RES.NEAREST

D = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/"
P = "/opt/blender-runner/outputs/"

# elemento -> lista de (view, f0, f1, recolher_na_vertical)
ELEMENTS = {
    "bico":      [("side", 0.00, 0.22), ("top", 0.00, 0.22), ("front", 0.0, 1.0)],
    "parachoque":[("front", 0.0, 1.0), ("top", 0.05, 0.30), ("side", 0.02, 0.20)],
    "piloto":    [("side", 0.34, 0.64), ("front", 0.0, 1.0), ("top", 0.34, 0.64)],
    "sidepod":   [("top", 0.34, 0.66), ("side", 0.46, 0.76), ("front", 0.0, 1.0)],
    "roda_diant":[("side", 0.16, 0.36), ("front", 0.0, 1.0)],
    "roda_tras": [("side", 0.64, 0.92), ("front", 0.0, 1.0)],
    "traseira":  [("side", 0.80, 1.00), ("top", 0.78, 1.00), ("rear", 0.0, 1.0)],
    "motor":     [("rear", 0.30, 1.00), ("top", 0.62, 0.96), ("side", 0.70, 0.96)],
}


def crop_mask(m):
    ys, xs = np.where(m)
    return int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())


def cell(view, ver, f0, f1, hh, pad=0.07):
    """Recorta a faixa [f0,f1] do COMPRIMENTO (x) com padding vertical, para concept e modelo."""
    m = np.load("/tmp/g2_%s.npy" % view).astype(bool)
    im = Image.open(D + view + ".jpg").convert("RGB")
    if im.size != (m.shape[1], m.shape[0]):
        im = im.resize((m.shape[1], m.shape[0]), LANCZOS)
    y0, y1, x0, x1 = crop_mask(m)
    W = x1 - x0 + 1
    ph = int((y1 - y0 + 1) * pad)
    box = (x0 + int(f0 * W), max(0, y0 - ph), x0 + int(f1 * W), min(im.height, y1 + 1 + ph))
    a = im.crop(box)
    a = a.resize((max(1, int(a.width * hh / a.height)), hh), LANCZOS)

    mm = np.array(Image.open(P + "%sm-%s.png" % (ver, view)).convert("RGBA"))[:, :, 3] > 128
    # BEAUTY (com luz). O "f-" e o passe FLAT (sem luzes) usado p/ medir cor:
    # usa-lo aqui faz o revisor ler "chapado/sem volume" — artefato de render.
    src = P + "%s-%s.png" % (ver, view)
    if not os.path.exists(src):
        src = P + "%sf-%s.png" % (ver, view)
    im2 = Image.open(src).convert("RGB")
    yy0, yy1, xx0, xx1 = crop_mask(mm)
    W2 = xx1 - xx0 + 1
    ph2 = int((yy1 - yy0 + 1) * pad)
    box2 = (xx0 + int(f0 * W2), max(0, yy0 - ph2), xx0 + int(f1 * W2), min(im2.height, yy1 + 1 + ph2))
    b = im2.crop(box2)
    b = b.resize((max(1, int(b.width * hh / b.height)), hh), LANCZOS)
    return a, b


def build(ver, name, specs, outdir, hh=560):
    cells = [cell(v, ver, f0, f1, hh) for v, f0, f1 in specs]
    w = max(a.width + b.width for a, b in cells) + 200
    img = Image.new("RGB", (w, len(cells) * (hh + 34) + 10), (14, 14, 18))
    d = ImageDraw.Draw(img)
    y = 0
    for (v, f0, f1), (a, b) in zip(specs, cells):
        d.text((6, y + hh // 2), "%s\n%.2f-%.2f" % (v.upper(), f0, f1), fill=(255, 255, 90))
        d.text((120, y + 6), "CONCEPT", fill=(255, 255, 90))
        d.text((a.width + 148, y + 6), "MODELO " + ver.upper(), fill=(120, 220, 255))
        img.paste(a, (116, y + 28))
        img.paste(b, (a.width + 144, y + 28))
        y += hh + 34
    # estampa a revisao DENTRO da imagem (um veredito vale para UMA revisao)
    d.text((w - 150, 4), ver.upper(), fill=(255, 120, 120))
    p = os.path.join(outdir, "EL-%s.png" % name)
    img.save(p)
    return p, img.size


def main():
    ver = sys.argv[1].lower()
    outdir = sys.argv[2]
    names = sys.argv[3:] or list(ELEMENTS.keys())
    os.makedirs(outdir, exist_ok=True)
    for n in names:
        p, sz = build(ver, n, ELEMENTS[n], outdir)
        print("OK %s %s" % (p, sz))


if __name__ == "__main__":
    main()

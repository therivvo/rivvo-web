#!/usr/bin/env python3
"""Comparador de PERFIL fractional: concept vs modelo, por vista, 40 estacoes.

IMPORTANTE (bug corrigido): a mascara do concept contem pixels ISOLADOS de 1-2 px
(linhas de cota / artefato de contorno). Medir extensao por (max-min) inflava o
perfil (ex.: em xf 0.52 do side, picos falsos em z0.81 davam 0.813 quando a
silhueta real e 0.567). Aqui a extensao usa o RUN PRINCIPAL (maior segmento
continuo) da coluna, que e a silhueta de fato.

Auto-normalizado: cada mascara e dividida pela sua propria extensao maxima, entao
o numero compara FORMA (fracao 0..1). A frente fica a esquerda nas duas.

Uso: python3 prof_cmp.py <versao> [view ...]
"""
import sys
import numpy as np
from PIL import Image

try:
    RES = Image.Resampling
except AttributeError:
    RES = Image
NEAREST = RES.NEAREST

D = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/"
P = "/opt/blender-runner/outputs/"


def crop(m):
    ys, xs = np.where(m)
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def runs_of(v, gap=2):
    idx = np.where(v)[0]
    if len(idx) == 0:
        return []
    runs = []
    s = idx[0]
    p = idx[0]
    for y in idx[1:]:
        if y - p <= gap:
            p = y
        else:
            runs.append((s, p))
            s = y
            p = y
    runs.append((s, p))
    return runs


def prof(mask, nb=40):
    """Extensao da silhueta = do TOPO do run mais alto ao FUNDO do run mais baixo,
    contando apenas runs com comprimento >= minlen. Isso exclui os pixels isolados
    de contorno/cota (1-2 px) que inflavam o perfil, sem descartar pecas reais
    soltas (ex.: o capacete, que e um run separado e curto)."""
    m = crop(mask.astype(bool))
    H, W = m.shape
    minlen = max(3, int(H * 0.010))
    tops = np.zeros(nb)
    bots = np.zeros(nb)
    for b in range(nb):
        pa = int(b / nb * W)
        pb = max(pa + 1, int((b + 1) / nb * W))
        t = None
        bo = None
        for j in range(pa, pb):
            for (a, z) in runs_of(m[:, j]):
                if (z - a + 1) < minlen:
                    continue
                t = z if t is None else max(t, z)
                bo = a if bo is None else min(bo, a)
        tops[b] = t if t is not None else np.nan
        bots[b] = bo if bo is not None else np.nan
    ext = tops - bots
    ext = np.nan_to_num(ext, nan=0.0)
    return ext / max(1e-9, ext.max())


def main():
    ver = sys.argv[1].lower()
    views = sys.argv[2:] or ["side", "top"]
    for view in views:
        mc = crop(np.load("/tmp/g2_%s.npy" % view).astype(bool))
        mm = crop(np.array(Image.open(P + "%sm-%s.png" % (ver, view)).convert("RGBA"))[:, :, 3] > 128)
        pc = prof(mc)
        pm = prof(mm)
        d = pm - pc
        worst = sorted(range(40), key=lambda i: -abs(d[i]))[:6]
        print("=== %s (fracional, 0=frente) :: %s ===" % (view.upper(), ver))
        print("  pior: " + " ".join("xf%.2f %+.3f" % (i / 40.0, d[i]) for i in sorted(worst)))
        for i in range(0, 40, 2):
            fl = "  <<<" if abs(d[i]) > 0.15 else ("  <" if abs(d[i]) > 0.08 else "")
            print("   xf %.2f  c=%.3f  m=%.3f  %+.3f%s" % (i / 40.0, pc[i], pm[i], d[i], fl))
        print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""QA executavel do Bubble Bumper — saida greppable para os gates do unlazy.

Uso:  python3 qa_bb.py <versao>            (ex: w233)
Saida: linhas CHAVE=valor, uma por metrica. Codigo de saida 0 sempre
       (o gate-check.mjs e quem decide FAIL/PASS pelo EXPECT).
"""
import sys, os, json, subprocess
import numpy as np
from PIL import Image

VER = (sys.argv[1] if len(sys.argv) > 1 else "w233").lower()
D = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/"
P = "/opt/blender-runner/outputs/"

# ---------- 1. metricas globais (reusa measure_bb.py) ----------
r = subprocess.run(["python3", "/opt/blender-runner/measure_bb.py", VER],
                   capture_output=True, text=True)
for ln in r.stdout.splitlines():
    if "=" in ln and ln.split("=")[0].isupper():
        print(ln.strip())

def crop(m):
    ys, xs = np.where(m)
    return m[ys.min():ys.max()+1, xs.min():xs.max()+1]

def rez(m, W, H):
    return np.array(Image.fromarray((m*255).astype(np.uint8)).resize((W, H), Image.NEAREST)) > 127

def region(view, a, b, axis="x"):
    A_ = np.array(Image.open(P+"%sm-%s.png" % (VER, view.lower())).convert("RGBA"))[:, :, 3] > 128
    c = np.load("/tmp/g2_%s.npy" % view.lower())
    r, cc = crop(A_), crop(c)
    H = max(r.shape[0], cc.shape[0]); W = max(r.shape[1], cc.shape[1])
    A, A2 = rez(cc, W, H), rez(r, W, H)
    best = 0.0
    for fh in (False, True):
        A3 = A[:, ::-1] if fh else A
        A4 = A2[:, ::-1] if fh else A2
        if axis == "x":
            s = A3[:, int(a*W):int(b*W)]; t = A4[:, int(a*W):int(b*W)]
        else:
            s = A3[int(a*H):int(b*H), :]; t = A4[int(a*H):int(b*H), :]
        inter = (s & t).sum()
        best = max(best, inter / max(1, (s | t).sum()))
    return best

REGS = {
    # eixo "x" = faixas ao longo do COMPRIMENTO (imagem horizontal): side, top
    # eixo "y" = faixas ao longo da ALTURA (imagem vertical): front, rear
    "SIDE":  ("x", [(0.00,0.14,"BICO"),(0.14,0.24,"PARACH_RODA"),(0.24,0.38,"COWL"),
                    (0.38,0.52,"PILOTO"),(0.52,0.66,"SIDEPOD"),(0.66,0.80,"MOTOR"),
                    (0.80,1.00,"TRASEIRA")]),
    "TOP":   ("x", [(0.00,0.18,"BICO_U"),(0.18,0.36,"RODAS_DIANT"),(0.36,0.62,"SIDEPODS"),
                    (0.62,0.80,"MOTOR"),(0.80,1.00,"ASA")]),
    "FRONT": ("y", [(0.00,0.22,"RODAS_BAIXO"),(0.22,0.42,"PARACH"),(0.42,0.58,"NARIZ"),
                    (0.58,0.70,"PILOTO"),(0.70,0.84,"CAPACETE"),(0.84,1.00,"ASA_AIRBOX")]),
    "REAR":  ("y", [(0.00,0.25,"PARACH_BAIXO"),(0.25,0.45,"DIFUSOR"),(0.45,0.62,"ESCAPES"),
                    (0.62,0.78,"PILOTO_COSTAS"),(0.78,1.00,"ASA_CAPACETE")]),
}
vals = []
for view, (ax, rs) in REGS.items():
    for a, b, tag in rs:
        v = region(view, a, b, ax)
        vals.append((v, view, tag))
        print("IOU_%s_%s=%.3f" % (view, tag, v))
vals.sort()
print("IOU_PIOR=%.3f@%s_%s" % (vals[0][0], vals[0][1], vals[0][2]))
print("IOU_P10_MEDIA=%.3f" % (sum(v for v, _, _ in vals[:10]) / 10.0))
print("IOU_MENOR_REGIAO=%.3f" % vals[0][0])

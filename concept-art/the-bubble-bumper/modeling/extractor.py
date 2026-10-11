#!/usr/bin/env python3
"""EXTRATOR DE REFERENCIA (Fase A do plano Sol). Reemite os numeros da FONTE.

Cada painel tem ZOOM PROPRIO (erro 5.1 do parecer): calibrar por painel, nunca
tratar os 4 arquivos como se tivessem a mesma escala.
Uso: python3 extractor.py   ->  imprime landmarks e grava reference-landmarks.json
"""
import json, numpy as np
from collections import deque
from PIL import Image

import os
_BS = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(_BS, "..", "assets", "reference-orthographic") + "/"
L_CANON = 2.35

def erode3(m):
    r = m.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            r &= np.roll(np.roll(m, dy, 0), dx, 1)
    return r

def maior_comp(m):
    m2 = m[::2, ::2]; H, W = m2.shape
    lab = np.zeros((H, W), int); n = 0; best = (0, 0)
    for i in range(H):
        for j in range(W):
            if m2[i, j] and lab[i, j] == 0:
                n += 1; q = deque([(i, j)]); lab[i, j] = n; sz = 0
                while q:
                    y, x = q.popleft(); sz += 1
                    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny, nx = y+dy, x+dx
                        if 0 <= ny < H and 0 <= nx < W and m2[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = n; q.append((ny, nx))
                if sz > best[0]: best = (sz, n)
    return (lab == best[1]) if best[1] else m2

def mascara(v):
    a = np.asarray(Image.open(A + v + ".jpg").convert("RGB")).astype(int)
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat, lum = mx - mn, a.mean(axis=2)
    m = ((sat > 26) & (lum < 250)) | (lum < 110)   # arte = colorido ou contorno escuro
    m = erode3(m)
    m = erode3(np.kron(maior_comp(m), np.ones((2,2), bool)))
    return m

def main():
    out = {}
    for v in ("front", "side", "rear", "top"):
        m = mascara(v); ys, xs = np.where(m)
        bb = (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()))
        out[v] = {"bbox_px": list(bb), "W_px": bb[1]-bb[0], "H_px": bb[3]-bb[2], "px": int(m.sum())}
    # SIDE governa COMPRIMENTO -> calibra a escala do SIDE
    esc_side = L_CANON / out["side"]["W_px"]
    out["side"]["escala_m_por_px"] = esc_side
    out["side"]["altura_m" if False else "H_m"] = round(out["side"]["H_px"] * esc_side, 4)
    # TOP: W do painel e o COMPRIMENTO (mesmo eixo) -> escala propria
    esc_top = L_CANON / out["top"]["W_px"]
    out["top"]["escala_m_por_px"] = esc_top
    out["top"]["largura_m"] = round(out["top"]["H_px"] * esc_top, 4)
    # FRONT/REAR: calibra pela LARGURA emitida pelo TOP (autoridade de largura) ou pelo TOP
    largura_ref = out["top"]["largura_m"]
    for v in ("front", "rear"):
        out[v]["escala_m_por_px"] = round(largura_ref / out[v]["W_px"], 8)
        out[v]["H_m"] = round(out[v]["H_px"] * out[v]["escala_m_por_px"], 4)
        out[v]["W_m"] = round(largura_ref, 4)
    d = {
        "length_m": L_CANON,
        "height_m": out["side"]["H_m"],
        "width_m": out["top"]["largura_m"],
        "L_H": round(L_CANON / out["side"]["H_m"], 4),
        "W_H": round(out["top"]["largura_m"] / out["side"]["H_m"], 4),
        "por_painel": out,
        "_nota": "REEMITIDO DA FONTE. Cada painel tem zoom proprio; calibracao por painel.",
    }
    json.dump(d, open(os.path.join(_BS, "reference-landmarks.json"), "w"), indent=1)
    print(json.dumps({k: d[k] for k in ("length_m","height_m","width_m","L_H","W_H")}, indent=1))
    return d

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Colore a malha do hull amostrando a COR do proprio concept nos 3 ortograficos.
Amostra a vista que olha a face de frente (|nx| -> FRONT, |ny| -> SIDE, |nz| -> TOP),
classifica na paleta do modelo e grava /tmp/vh_fmat.npy (indice de material por face).
Paleta (ordem = indice): 0 M_Dark 1 M_Silver 2 M_Plate 3 M_White 4 M_Blue 5 M_BlueDk
                         6 M_Yellow 7 M_Gold 8 M_Pilot 9 M_Visor 10 M_Face
"""
import numpy as np, sys

VER = sys.argv[1] if len(sys.argv) > 1 else "VH1"
OBJ = sys.argv[2] if len(sys.argv) > 2 else "/tmp/vh.obj"
L, Wd, Ht = 2.35, 1.494, 1.207
X0, Y0, Z0 = 1.175, 0.747, 1.207

def load(view):
    m = np.load("/tmp/c_%s.npy" % view).astype(bool)
    a = np.load("/tmp/cc_%s.npy" % view).astype(np.int16)
    r = np.where(m.any(1))[0]; c = np.where(m.any(0))[0]
    return m, a, (r[0], r[-1], c[0], c[-1])

M = {v: load(v) for v in ("front", "side", "top")}

def sample(view, u, w):
    """(u,w) em metro -> RGB do concept naquela vista. u = eixo horizontal da vista."""
    m, a, (r0, r1, c0, c1) = M[view]
    if view == "front":     # horizontal = y (de +Y a -Y), vertical = z (de Z0 a 0)
        cu = c0 + (Y0 - u) / Wd * (c1 - c0); rw = r0 + (Z0 - w) / Ht * (r1 - r0)
    elif view == "side":    # horizontal = x (+X a -X), vertical = z
        cu = c0 + (X0 - u) / L * (c1 - c0);  rw = r0 + (Z0 - w) / Ht * (r1 - r0)
    else:                   # top: horizontal = x, vertical = y (+Y a -Y)
        cu = c0 + (X0 - u) / L * (c1 - c0);  rw = r0 + (Y0 - w) / Wd * (r1 - r0)
    ci = int(round(cu)); ri = int(round(rw))
    ci = min(max(ci, 0), a.shape[1] - 1); ri = min(max(ri, 0), a.shape[0] - 1)
    return a[ri, ci], m[ri, ci]

def classify(rgb):
    """MESMAS faixas do cls_family do auditor, para a cor do modelo cair na mesma
    familia que a do concept (senao a metrica acusa desvio por artefato de material)."""
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    mx, mn = max(r, g, b), min(r, g, b)
    sat = mx - mn
    yellow = (r > 140) and (g > 105) and (b < 140) and ((r - b) > 55)
    if yellow: return 6
    blue = (b > r + 18) and (sat > 12)
    if blue:
        if mx < 95:  return 5          # azul_esq  -> M_BlueDk
        if mx < 170: return 4          # azul_med  -> M_Blue
        return 8                       # azul_clr  -> M_BlueLt
    if mx < 70:  return 0              # escuro
    if mx < 145: return 1              # cinza
    return 2                            # claro


def main():
    V = []; F = []
    with open(OBJ) as f:
        for ln in f:
            t = ln.split()
            if not t: continue
            if t[0] == "v": V.append((float(t[1]), float(t[2]), float(t[3])))
            elif t[0] == "f": F.append([int(x.split("/")[0]) - 1 for x in t[1:]])
    V = np.array(V, np.float64)
    print("malha: %d verts %d faces" % (len(V), len(F)))
    # normais por face
    mat = np.zeros(len(F), np.int8)
    dbg = np.zeros((len(F), 3), np.int16)
    for i, f in enumerate(F):
        p = V[f]
        n = np.cross(p[1] - p[0], p[2] - p[0])
        ln = np.linalg.norm(n)
        if ln < 1e-12: mat[i] = 2; continue
        n = n / ln
        c = p.mean(0)
        ax = int(np.argmax(np.abs(n)))
        if ax == 0:   rgb, ok = sample("front", c[1], c[2])
        elif ax == 1: rgb, ok = sample("side", c[0], c[2])
        else:         rgb, ok = sample("top", c[0], c[1])
        if not ok:    # caiu fora da silhueta: tenta a segunda vista dominante
            order = np.argsort(-np.abs(n))
            for a2 in order[1:]:
                if a2 == 0: rgb, ok = sample("front", c[1], c[2])
                elif a2 == 1: rgb, ok = sample("side", c[0], c[2])
                else: rgb, ok = sample("top", c[0], c[1])
                if ok: break
        dbg[i] = rgb if ok else (-1, -1, -1)
        mat[i] = classify(rgb) if ok else 1
    np.save("/tmp/vh_fmat.npy", mat)
    np.save("/tmp/vh_fdbg.npy", dbg)
    cls, cnt = np.unique(mat, return_counts=True)
    NOMES = ["M_Dark", "M_Silver", "M_Plate", "M_White", "M_Blue", "M_BlueDk", "M_Yellow", "M_Gold", "M_Pilot", "M_Visor", "M_Face"]
    print("distribuicao de material por face:")
    for c, n in zip(cls, cnt): print("   %-9s %6d  (%.1f%%)" % (NOMES[c], n, 100.0 * n / len(F)))
    fora = (dbg[:, 0] < 0).sum()
    print("faces fora de todas as silhuetas: %d (%.1f%%)" % (fora, 100.0 * fora / len(F)))

if __name__ == "__main__":
    main()

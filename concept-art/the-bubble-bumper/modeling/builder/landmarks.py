#!/usr/bin/env python3
"""landmarks.py — metrica de erro de LANDMARKS (prescricao do Sol 2026-09-20).

Substitui a caca a EMA do perfil. Regra: NUNCA um numero unico (Goodhart).
Normaliza cada landmark pela extensao da propria vista e compara concept x modelo.

GATES: E_landmark mediana <= 0.025 e nenhum P0 > 0.050.

Uso:  python3 landmarks.py <VER>            # ex. W518
      python3 landmarks.py <VER> --json
"""
import sys, json, os
import numpy as np
from PIL import Image

MD = os.path.dirname(os.path.abspath(__file__))
REF = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/"
P = "/opt/blender-runner/outputs/"
GATE_MED, GATE_PIOR = 0.025, 0.050

def erode3(m, p=2):
    for _ in range(p):
        e = m.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                e &= np.roll(np.roll(m, dy, 0), dx, 1)
        m = e
    return m

def sil_concept(path, sat=45, dark=85, er=2):
    """Silhueta do concept por COR (a mascara .npy inclui o quadro/rebuas do blueprint)."""
    c = np.array(Image.open(path).convert("RGB")).astype(int)
    mx, mn = c.max(2), c.min(2)
    s = ((mx - mn) > sat) | (mx < dark)
    s[:6, :] = False; s[-6:, :] = False; s[:, :6] = False; s[:, -6:] = False
    core = erode3(s, er)
    return (core if core.sum() > 500 else s), c

def sil_model(alpha, flat):
    """Modelo: alpha e EXATO. Nunca usar cor aqui (o render tem fundo escuro)."""
    a = np.array(Image.open(alpha).convert("RGBA"))
    return a[:, :, 3] > 128, np.array(Image.open(flat).convert("RGB")).astype(int)

def landmarks(sil, col):
    ys, xs = np.where(sil); r0, r1, c0, c1 = ys.min(), ys.max(), xs.min(), xs.max()
    H, W = float(r1 - r0 + 1), float(c1 - c0 + 1)
    A, C = sil[r0:r1+1, c0:c1+1], col[r0:r1+1, c0:c1+1]
    o = {}
    top = np.full(int(W), np.nan)
    for i in range(int(W)):
        idx = np.where(A[:, i])[0]
        if len(idx): top[i] = r1 - (r0 + idx.min())
    gd = ~np.isnan(top)
    if gd.sum() > 5:
        xs_, tv = np.arange(int(W))[gd], top[gd]
        k = int(np.argmax(tv)); o["topo_z"], o["topo_x"] = tv[k]/H, xs_[k]/W
        gr = np.abs(np.diff(tv)); k2 = int(np.argmax(gr))
        o["degrau_amp"], o["degrau_x"] = gr[k2]/H, xs_[k2]/W
    for nm, cm in (("bico", int(W)-1), ("rabeira", 0)):
        idx = np.where(A[:, cm])[0]
        if len(idx): o[nm + "_z"] = (r1 - (r0 + idx.max())) / H
    r, g, b = C[:, :, 0], C[:, :, 1], C[:, :, 2]
    dk = (np.maximum(np.maximum(r, g), b) < 85) & A
    yl = (r > 140) & (g > 100) & (b < 115) & A
    low = dk[int(H*0.45):, :]; cs_ = low.sum(0)
    if cs_.sum() > 50:
        on = cs_ > cs_.max()*0.15; ix = np.where(on)[0]; mid = (ix.min()+ix.max())/2.0
        f, rr = ix[ix > mid], ix[ix <= mid]
        if len(f): o["roda_f_x"] = f.mean()/W
        if len(rr): o["roda_r_x"] = rr.mean()/W
    if yl.sum() > 80:
        _, xx = np.where(yl)
        o["pod_x0"], o["pod_x1"] = xx.min()/W, xx.max()/W
        o["pod_area_frac"] = float(yl.sum())/float(A.sum())
    return o

def run(ver):
    sc, cc = sil_concept(REF + "side.jpg")
    sm, cm = sil_model(P + ver + "m-side.png", P + ver + "f-side.png")
    conc, mod = landmarks(sc, cc), landmarks(sm, cm)
    keys = sorted(set(conc) & set(mod))
    rows = [(k, conc[k], mod[k], abs(mod[k] - conc[k])) for k in keys]
    ds = [d for _, _, _, d in rows]
    em, pw = float(np.median(ds)), max(ds)
    wn = keys[int(np.argmax(ds))]
    return {"ver": ver, "rows": rows, "E_mediana": em, "pior": pw, "pior_nome": wn,
            "ok_mediana": em <= GATE_MED, "ok_pior": pw <= GATE_PIOR}

if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "w518"
    res = run(ver)
    if "--json" in sys.argv:
        print(json.dumps(res, indent=2)); sys.exit(0)
    print("%-14s %9s %9s %9s" % ("landmark", "concept", ver, "|dif|"))
    for k, cv, mv, d in res["rows"]:
        flag = "  <== P0" if d > GATE_PIOR else ""
        print("%-14s %9.4f %9.4f %9.4f%s" % (k, cv, mv, d, flag))
    print("\nE_landmark mediana = %.4f (gate <=%.3f) %s" % (res["E_mediana"], GATE_MED, "PASSA" if res["ok_mediana"] else "FALHA"))
    print("pior landmark      = %.4f (gate <=%.3f) [%s] %s" % (res["pior"], GATE_PIOR, res["pior_nome"], "PASSA" if res["ok_pior"] else "FALHA"))

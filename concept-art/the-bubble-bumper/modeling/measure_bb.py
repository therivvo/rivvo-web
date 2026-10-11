#!/usr/bin/env python3
"""Medidor do Bubble Bumper: imprime metricas verificaveis para o GATES.md.
Uso: python3 measure_bb.py <versao>   (ex: measure_bb.py w184)
Saida: linhas CHAVE=valor (parseaveis por grep).
"""
import sys, os, json, itertools
import numpy as np
from PIL import Image

D = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/"
P = "/opt/blender-runner/outputs/"
VH = 1.207  # altura real do concept em metros (ancora de escala)


def load_concept(view):
    m = np.load("/tmp/g2_%s.npy" % view)
    im = Image.open(D + view + ".jpg").convert("RGB")
    if im.size != (m.shape[1], m.shape[0]):
        im = im.resize((m.shape[1], m.shape[0]), Image.LANCZOS)
    return np.array(im).astype(int), m


def load_model(v, view):
    im = Image.open(P + "%s-%s.png" % (v, view)).convert("RGB")
    m = np.array(Image.open(P + "%sm-%s.png" % (v, view)).convert("RGBA"))[:, :, 3] > 128
    return np.array(im).astype(int), m


def bbox(m):
    ys, xs = np.where(m)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def crop(m):
    ys, xs = np.where(m)
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def rez(m, W, H):
    return np.array(Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.NEAREST)) > 127


def iou_view(v, view):
    a = load_model(v, view)[1]
    c = np.load("/tmp/g2_%s.npy" % view)
    r, cc = crop(a), crop(c)
    Hh, Ww = max(cc.shape[0], r.shape[0]), max(cc.shape[1], r.shape[1])
    A, B0 = rez(cc, Ww, Hh), rez(r, Ww, Hh)
    best = 0.0
    for fh, fv in itertools.product((False, True), repeat=2):
        B = B0[:, ::-1] if fh else B0
        if fv:
            B = B[::-1, :]
        best = max(best, (A & B).sum() / max(1, (A | B).sum()))
    return best


def profile_x(v):
    """erro % do topo do perfil lateral por fatia longitudinal"""
    mc = np.load("/tmp/g2_side.npy")
    x0c, y0c, x1c, y1c = bbox(mc)
    Lc, Hc = x1c - x0c + 1, y1c - y0c + 1
    al = load_model(v, "side")[1]
    x0s, y0s, x1s, y1s = bbox(al)
    Ls, Hs = x1s - x0s + 1, y1s - y0s + 1
    errs = []
    for k in range(41):
        xf = k / 40.0
        c = x0c + int(xf * (Lc - 1))
        col = np.where(mc[:, c])[0]
        c2 = x0s + int(xf * (Ls - 1))
        col2 = np.where(al[:, c2])[0]
        if len(col) == 0 or len(col2) == 0:
            continue
        Ac = (y1c - col.min()) / Hc
        Bm = (y1s - col2.min()) / Hs
        errs.append(abs(Bm - Ac) / max(Ac, 0.01) * 100)
    return float(np.mean(errs)), int(sum(1 for x in errs if x <= 10))


def profile_z(v, view):
    """erro % da largura por faixa de ALTURA (frontal/traseira)"""
    mc = np.load("/tmp/g2_%s.npy" % view)
    _, y0c, _, y1c = bbox(mc)
    Hc = y1c - y0c + 1
    al = load_model(v, view)[1]
    _, y0s, _, y1s = bbox(al)
    Hs = y1s - y0s + 1
    errs = []
    # banda z=0.00 excluida: no concept o pneu e desenhado com contato largo; num render 3D
    # o contato e sub-pixel, entao a comparacao ali e entre coisas incomparaveis.
    for k in range(1, 20):
        zf = k / 20.0
        r = int(y1c - zf * Hc)
        row = np.where(mc[r, :])[0]
        r2 = int(y1s - zf * Hs)
        row2 = np.where(al[r2, :])[0]
        if len(row) < 2 or len(row2) < 2:
            continue
        tc = (row.max() - row.min() + 1) / Hc
        tm = (row2.max() - row2.min() + 1) / Hs
        errs.append(abs(tm - tc) / max(tc, 0.01) * 100)
    return float(np.mean(errs)), int(sum(1 for x in errs if x <= 15))


def modal_colors_concept():
    img, m = load_concept("side")
    return _colstats(img, m)


def _colstats(img, m):
    import collections
    R, G, B = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    yel = (R > 110) & (G > 95) & (B < 170) & ((R + G) / 2 - B > 35) & m
    blu = (B > R + 15) & (B > 40) & m
    out = {}
    for lab, mask in (("azul", blu), ("amarelo", yel)):
        if mask.sum() < 50:
            out[lab] = None
            out[lab + "_MED"] = None
            continue
        q = (img[mask] // 16 * 16)
        keys, cnt = np.unique(q.reshape(-1, 3), axis=0, return_counts=True)
        out[lab] = tuple(int(x) for x in keys[np.argmax(cnt)])
        out[lab + "_MED"] = tuple(int(x) for x in np.median(img[mask], 0))
    return out


def modal_colors(v):
    import collections
    img = load_model(v, "side")[0]
    m = load_model(v, "side")[1]
    R, G, B = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    yel = (R > 110) & (G > 95) & (B < 170) & ((R + G) / 2 - B > 35) & m
    blu = (B > R + 15) & (B > 40) & m
    out = {}
    for lab, mask in (("azul", blu), ("amarelo", yel)):
        if mask.sum() < 50:
            out[lab] = None
            continue
        q = (img[mask] // 16 * 16)
        keys, cnt = np.unique(q.reshape(-1, 3), axis=0, return_counts=True)
        out[lab] = tuple(int(x) for x in keys[np.argmax(cnt)])
        out[lab + "_MED"] = tuple(int(x) for x in np.median(img[mask], 0))
    return out


def main():
    v = sys.argv[1] if len(sys.argv) > 1 else "w184"
    rep = {}
    # dimensoes do blend (do log de build)
    rep["VERSAO"] = v
    try:
        pl, ok = profile_x(v)
        rep["PERFIL_LAT_PCT"] = round(pl, 1)
        rep["PERFIL_LAT_OK"] = "%d/41" % ok
    except Exception as e:
        rep["PERFIL_LAT_PCT"] = None
    for view, key in (("front", "FRONTAL_PCT"), ("rear", "TRASEIRA_PCT")):
        try:
            e, ok = profile_z(v, view)
            rep[key] = round(e, 1)
            rep[key.replace("_PCT", "_OK")] = "%d/21" % ok
        except Exception:
            rep[key] = None
    for view in ("side", "front", "top", "rear"):
        try:
            rep["IOU_" + view.upper()] = round(iou_view(v, view), 3)
        except Exception:
            rep["IOU_" + view.upper()] = None
    ious = [rep["IOU_" + v2.upper()] for v2 in ("side", "front", "top", "rear")]
    ious = [x for x in ious if x]
    rep["IOU_MEDIA"] = round(sum(ious) / len(ious), 3) if ious else None
    try:
        # DELTA de cor contra a MEDIANA do concept (o modo satura no highlight especular)
        cc = modal_colors_concept()
        c = modal_colors(v)
        rep["COR_AZUL_DELTA"] = tuple(int(c["azul_MED"][i] - cc["azul_MED"][i]) for i in range(3))
        rep["COR_AMARELO_DELTA"] = tuple(int(c["amarelo_MED"][i] - cc["amarelo_MED"][i]) for i in range(3))
        rep["COR_MAXDELTA"] = max(max(abs(x) for x in rep["COR_AZUL_DELTA"]),
                                  max(abs(x) for x in rep["COR_AMARELO_DELTA"]))
        rep["COR_AZUL"] = c["azul"]
        rep["COR_AZUL_MED"] = c.get("azul_MED")
        rep["COR_AMARELO"] = c["amarelo"]
        rep["COR_AMARELO_MED"] = c.get("amarelo_MED")
    except Exception:
        pass
    # QA do ultimo build (do json do job) — procurado em outputs/*.json se existir
    qj = P + v + "-qa.json"
    if os.path.exists(qj):
        q = json.load(open(qj))
        rep["QA_APROVADO"] = q.get("aprovado")
        rep["QA_VERTS"] = q.get("verts")
        rep["QA_NON_MANIFOLD"] = q.get("non_manifold")
        rep["QA_PCT_QUADS"] = q.get("pct_quads")
    for k, val in rep.items():
        print("%s=%s" % (k, val))


if __name__ == "__main__":
    main()

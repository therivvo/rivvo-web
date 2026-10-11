#!/usr/bin/env python3
"""Auditor ESTRITO do Bubble Bumper.

Substitui a logica leniente do qa_bb.py. O que o qa_bb.py fazia de errado:
  1. testava o concept ESPELHADO e tomava max() sobre o flip (inflava tudo);
  2. esticava as duas mascaras para o MESMO bounding box, destruindo a informacao
     de proporcao (modelo largo demais era espremido ate "casar").
Aqui: alinhamento por ESCALA UNICA (media geometrica das razoes de largura e
altura), sem flip. Erro de escala e de aspect ratio aparece na metrica.

Por regiao reporta:
  IoU      — sobreposicao no canvas em escala unica
  EXCESSO  — fracao do volume do concept que o modelo INVADE (gordo demais)
  FALTA    — fracao do volume do concept que o modelo NAO tem (magro demais)
  corTV    — distancia total-variation das classes de cor
  runs c/m — n de aberturas numa fatia interna (1 = macico, >1 = pecas separadas)

A paleta foi MEDIDA do concept (clusters dominantes), nao chutada: ver
cls_family(). O concept e dominado por neutros e azuis em varias luminancias.

Uso:  python3 audit_bb.py <versao>       (ex: w282)
Saida: CHAVE=valor + tabela. Sempre exit 0.
"""
import sys, os
import numpy as np
from PIL import Image

try:
    RES = Image.Resampling
except AttributeError:
    RES = Image
LANCZOS, NEAREST = RES.LANCZOS, RES.NEAREST

VER = (sys.argv[1] if len(sys.argv) > 1 else "w282").lower()
D = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/"
P = "/opt/blender-runner/outputs/"

NOMES = ["escuro", "cinza", "claro", "azul_esq", "azul_med", "azul_clr", "outro", "amarelo"]
NCLS = len(NOMES)


def cls_family(px):
    """Classifica por FAMILIA de cor + faixa de luminancia (robusto p/ render vs desenho)."""
    px = px.astype(float)
    r, g, b = px[:, 0], px[:, 1], px[:, 2]
    mx = px.max(1); mn = px.min(1); sat = mx - mn
    lab = np.full(len(px), 6, dtype=np.int8)
    yellow = (r > 140) & (g > 105) & (b < 140) & ((r - b) > 55)
    blue = (b > r + 18) & (sat > 12) & ~yellow
    neut = ~yellow & ~blue
    lab[neut & (mx < 70)] = 0
    lab[neut & (mx >= 70) & (mx < 145)] = 1
    lab[neut & (mx >= 145)] = 2
    lab[blue & (mx < 95)] = 3
    lab[blue & (mx >= 95) & (mx < 170)] = 4
    lab[blue & (mx >= 170)] = 5
    lab[yellow] = 7
    return lab


def bbox(m):
    ys, xs = np.where(m)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def load_c(view):
    """Referencia LIMPA. As masks g2_* cruas tinham uma linha de chao de 2 px ao longo
    de todo o comprimento (~0.6 cm) e runs finos de cota: medir contra elas penalizava o
    modelo com FALTA sistematica no fundo. c_*/cc_* sao as mesmas views com runs finos
    removidos, apenas a maior componente mantida e recortadas no bbox do conteudo."""
    m = np.load("/tmp/c_%s.npy" % view).astype(bool)
    im = np.load("/tmp/cc_%s.npy" % view)
    return np.array(im), m


def load_m(ver, view, mode=None):
    """mode='flat' -> usa <ver>f-<view>.png (sem luzes, ambiente uniforme).
    A COR e medida sempre no flat: o beauty tem key/fill/rim + especular e clareia a
    cor por construcao (comparava a minha luz, nao o modelo). A MASCARA vem do
    beauty (<ver>m-<view>.png), que tem alpha limpo."""
    mode = mode or os.environ.get("BB_MODE", "flat")
    col = P + ("%sf-%s.png" % (ver, view) if mode == "flat" else "%s-%s.png" % (ver, view))
    g = P + "%sm-%s.png" % (ver, view)
    if not (os.path.exists(col) and os.path.exists(g)):
        return None, None
    im = np.array(Image.open(col).convert("RGB"))
    m = np.array(Image.open(g).convert("RGBA"))[:, :, 3] > 128
    if im.shape[:2] != m.shape[:2]:
        im = np.array(Image.fromarray(im).resize((m.shape[1], m.shape[0]), LANCZOS))
    return im, m


def crop_to_bbox(im, m):
    x0, y0, x1, y1 = bbox(m)
    return im[y0:y1 + 1, x0:x1 + 1], m[y0:y1 + 1, x0:x1 + 1]


def paint(arr, mask, scale, CW, CH, is_class=False):
    """Leva a mascara (ou o mapa de classes) para o canvas com escala uniforme."""
    h, w = mask.shape
    nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    if is_class:
        # classes: NEAREST para nao inventar indices; fora da mascara = 6 (outro)
        src = np.where(mask, arr, 6).astype(np.uint8)
        r = np.array(Image.fromarray(src).resize((nw, nh), NEAREST))
        out = np.full((CH, CW), 6, np.uint8)
    else:
        r = np.array(Image.fromarray((mask * 255).astype(np.uint8)).resize((nw, nh), NEAREST)) > 127
        out = np.zeros((CH, CW), bool)
    ox, oy = (CW - nw) // 2, (CH - nh) // 2
    if nw > CW or nh > CH:
        ox, oy = 0, 0
        nw, nh = min(CW, nw), min(CH, nh)
    out[oy:oy + nh, ox:ox + nw] = r[:nh, :nw]
    return out


def hist(cl, valid):
    h = np.bincount(cl[valid].ravel(), minlength=NCLS).astype(float)
    return h / max(1.0, h.sum())


def tv(a, b):
    return float(0.5 * np.abs(a - b).sum())


def runs_of(col):
    idx = np.where(col)[0]
    if len(idx) == 0:
        return 0
    n = 1
    for k in range(1, len(idx)):
        if idx[k] - idx[k - 1] > 3:
            n += 1
    return n


REGIONS = {
    "side":  ("x", [(0.00, 0.14, "BICO"), (0.14, 0.24, "PARACH_RODA"), (0.24, 0.38, "COWL"),
                    (0.38, 0.52, "PILOTO"), (0.52, 0.66, "SIDEPOD"), (0.66, 0.80, "MOTOR"),
                    (0.80, 1.00, "TRASEIRA")]),
    "top":   ("x", [(0.00, 0.18, "BICO_U"), (0.18, 0.36, "RODAS_DIANT"), (0.36, 0.62, "SIDEPODS"),
                    (0.62, 0.80, "MOTOR"), (0.80, 1.00, "ASA")]),
    "front": ("z", [(0.00, 0.22, "RODAS_BAIXO"), (0.22, 0.42, "PARACH"), (0.42, 0.58, "NARIZ"),
                    (0.58, 0.70, "PILOTO"), (0.70, 0.84, "CAPACETE"), (0.84, 1.00, "ASA_AIRBOX")]),
    "rear":  ("z", [(0.00, 0.25, "PARACH_BAIXO"), (0.25, 0.45, "DIFUSOR"), (0.45, 0.62, "ESCAPES"),
                    (0.62, 0.78, "PILOTO_COSTAS"), (0.78, 1.00, "ASA_CAPACETE")]),
}


def canvas_bbox(m):
    ys, xs = np.where(m)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def band(ax, a, b, Mc):
    """Faixa definida pelo bbox do CONCEPT e aplicada aos dois (mesma regiao fisica)."""
    x0, y0, x1, y1 = canvas_bbox(Mc)
    if ax == "x":
        return "c", slice(int(x0 + a * (x1 - x0 + 1)), int(x0 + b * (x1 - x0 + 1)))
    return "r", slice(int(y1 - b * (y1 - y0 + 1)), int(y1 - a * (y1 - y0 + 1)))


def main():
    rows = []
    fam_c = np.zeros(NCLS); fam_m = np.zeros(NCLS); nfam = 0
    # AUDIT_SKIP: vistas com mascara de referencia NAO confiavel (ex.: top, cujo source tem grid+cotas+sombra
    # e cuja segmentacao nao fecha -> fill 0.765 vs 0.48-0.58 das vistas boas; vision reprovou as duas versoes)
    import os as _os
    _skip=set(x for x in _os.environ.get('AUDIT_SKIP','').split(',') if x)
    for view, (ax, rs) in REGIONS.items():
        if view in _skip:
            print('SKIP %s (mascara de referencia nao confiavel)' % view)
            continue
        ic, mc = load_c(view)
        im, mm = load_m(VER, view)
        if im is None:
            print("MISSING %s-%s" % (VER, view))
            continue
        icc, mcc = crop_to_bbox(ic, mc)
        imm, mmm = crop_to_bbox(im, mm)
        Hc, Wc = mcc.shape
        Hm, Wm = mmm.shape
        scale = float(np.sqrt((Wc / float(Wm)) * (Hc / float(Hm))))
        CW, CH = int(Wc * 1.30) + 8, int(Hc * 1.30) + 8
        Mc = paint(np.zeros_like(mcc, np.uint8), mcc, 1.0, CW, CH)
        Mm = paint(np.zeros_like(mmm, np.uint8), mmm, scale, CW, CH)
        Cc = paint(cls_family(icc.reshape(-1, 3)).reshape(mcc.shape), mcc, 1.0, CW, CH, True)
        Cm = paint(cls_family(imm.reshape(-1, 3)).reshape(mmm.shape), mmm, scale, CW, CH, True)
        # classes validas (dentro da mascara)
        Cc[~Mc] = 6
        Cm[~Mm] = 6
        iou_all = (Mc & Mm).sum() / max(1, (Mc | Mm).sum())
        hc, hm = hist(Cc, Mc), hist(Cm, Mm)
        fam_c += hc; fam_m += hm; nfam += 1
        print("VIEW=%s IoU=%.3f escala=%.3f Wc/Hc=%.3f Wm/Hm=%.3f" % (
            view.upper(), iou_all, scale, Wc / float(Hc), Wm / float(Hm)))
        print("VIEW=%s corTV=%.3f %s" % (view.upper(), tv(hc, hm),
              " ".join("%s=%.3f/%.3f" % (NOMES[i], hc[i], hm[i]) for i in range(NCLS))))
        if ax == "x":
            _, sl = band(ax, 0, 1, Mc)
            span = sl.stop - sl.start
            for n in range(1, 4):
                row = min(CH - 1, max(0, sl.start + n * span // 4))
                print("VIEW=%s fatia_z%.2f runs_c=%d runs_m=%d" % (
                    view.upper(), 1.0 - n / 4.0, runs_of(Mc[row, :]), runs_of(Mm[row, :])))
        for a, b, tag in rs:
            k, sl = band(ax, a, b, Mc)
            if k == "c":
                sc, sm = Mc[:, sl], Mm[:, sl]
                dcor = tv(hist(Cc[:, sl], Mc[:, sl]), hist(Cm[:, sl], Mm[:, sl]))
            else:
                sc, sm = Mc[sl, :], Mm[sl, :]
                dcor = tv(hist(Cc[sl, :], Mc[sl, :]), hist(Cm[sl, :], Mm[sl, :]))
            iou = (sc & sm).sum() / max(1, (sc | sm).sum())
            excess = (sm & ~sc).sum() / max(1, sc.sum())
            missing = (sc & ~sm).sum() / max(1, sc.sum())
            nr = (0, 0)
            if min(sc.shape[0], sm.shape[0]) > 1:
                hb = min(sc.shape[0] // 2, sm.shape[0] - 1)
                nr = (runs_of(sc[hb, :]), runs_of(sm[hb, :]))
            rows.append([iou, view, tag, excess, missing, dcor, nr])
    rows.sort(key=lambda r: r[0])
    print()
    print("%-17s %6s %8s %7s %6s %s" % ("REGIAO", "IoU", "EXCESSO", "FALTA", "corTV", "runs c/m"))
    for iou, view, tag, ex, mi, dc, nr in rows:
        print("%-17s %6.3f %7.1f%% %6.1f%% %6.3f %d/%d" % (
            "%s/%s" % (view, tag), iou, ex * 100, mi * 100, dc, nr[0], nr[1]))
    n = max(1, nfam)
    hc, hm = fam_c / n, fam_m / n
    print()
    print("FAMILIA (media das vistas): %s" % " ".join(
        "%s=%.3f/%.3f" % (NOMES[i], hc[i], hm[i]) for i in range(NCLS)))
    print("FAM_NEUTRO_C=%.3f FAM_NEUTRO_M=%.3f" % (hc[0] + hc[1] + hc[2], hm[0] + hm[1] + hm[2]))
    print("FAM_AZUL_C=%.3f FAM_AZUL_M=%.3f" % (hc[3] + hc[4] + hc[5], hm[3] + hm[4] + hm[5]))
    print("FAM_AMARELO_C=%.3f FAM_AMARELO_M=%.3f" % (hc[7], hm[7]))
    print("FAM_AZULCLR_C=%.3f FAM_AZULCLR_M=%.3f" % (hc[5], hm[5]))
    print()
    print("AUD_IOU_MEDIA=%.3f" % (sum(r[0] for r in rows) / len(rows)))
    print("AUD_IOU_P10=%.3f" % (sum(r[0] for r in rows[:10]) / min(10, len(rows))))
    print("AUD_IOU_PIOR=%.3f@%s_%s" % (rows[0][0], rows[0][1], rows[0][2]))
    print("AUD_COR_TV=%.3f" % (sum(r[5] for r in rows) / len(rows)))
    print("AUD_EXCESSO=%.1f" % (sum(r[3] for r in rows) / len(rows) * 100))
    print("AUD_FALTA=%.1f" % (sum(r[4] for r in rows) / len(rows) * 100))
    print("AUD_N_REGIOES=%d" % len(rows))
    print("AUD_ABAIXO_090=%d" % sum(1 for r in rows if r[0] < 0.90))
    print("AUD_ABAIXO_080=%d" % sum(1 for r in rows if r[0] < 0.80))


if __name__ == "__main__":
    main()

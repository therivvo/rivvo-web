#!/usr/bin/env python3
"""Sonda de ZONA: pergunta 'o que exatamente difere aqui?' entre concept e modelo.

Uso: python3 zone_probe.py <versao> <view> <a> <b> [axis]
  view: side|top|front|rear      a,b: fracao 0..1 do bbox do CONCEPT
  axis: x (comprimento, default p/ side/top) | z (altura, default p/ front/rear)

Imprime, por coluna (ou linha) da zona: extent do concept, extent do modelo em
coords do canvas, EXCESSO, FALTA e as classes de cor dominantes de cada lado.
"""
import sys, os, importlib.util
import numpy as np

MD = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("aud", os.path.join(MD, "audit_bb.py"))
mod = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "w284"]
spec.loader.exec_module(mod)

VER = sys.argv[1].lower() if len(sys.argv) > 1 else "w284"
VIEW = sys.argv[2].lower() if len(sys.argv) > 2 else "top"
A = float(sys.argv[3]) if len(sys.argv) > 3 else 0.80
B = float(sys.argv[4]) if len(sys.argv) > 4 else 1.00
AX = sys.argv[5] if len(sys.argv) > 5 else ("x" if VIEW in ("side", "top") else "z")

ic, mc = mod.load_c(VIEW)
im, mm = mod.load_m(VER, VIEW)
icc, mcc = mod.crop_to_bbox(ic, mc)
imm, mmm = mod.crop_to_bbox(im, mm)
Hc, Wc = mcc.shape
Hm, Wm = mmm.shape
scale = float(np.sqrt((Wc / float(Wm)) * (Hc / float(Hm))))
CW, CH = int(Wc * 1.30) + 8, int(Hc * 1.30) + 8
Mc = mod.paint(np.zeros_like(mcc, np.uint8), mcc, 1.0, CW, CH)
Mm = mod.paint(np.zeros_like(mmm, np.uint8), mmm, scale, CW, CH)
Cc = mod.paint(mod.cls_family(icc.reshape(-1, 3)).reshape(mcc.shape), mcc, 1.0, CW, CH, True)
Cm = mod.paint(mod.cls_family(imm.reshape(-1, 3)).reshape(mmm.shape), mmm, scale, CW, CH, True)
Cc[~Mc] = 6
Cm[~Mm] = 6
print("VER=%s VIEW=%s zona %.2f-%.2f eixo %s | canvas %dx%d escala=%.3f" % (VER, VIEW.upper(), A, B, AX, CW, CH, scale))
k, sl = mod.band(AX, A, B, Mc)
print("fatia: %s %d..%d" % (k, sl.start, sl.stop))
print()
if AX == "x":
    print("  col  ext_c  ext_m   d_ext | excess%  falta% | domin_c            domin_m")
    for j in range(sl.start, sl.stop, max(1, (sl.stop - sl.start) // 12)):
        sc = Mc[:, j:j + 1][:, 0]
        sm = Mm[:, j:j + 1][:, 0]
        def ext(a):
            r = np.where(a)[0]
            return (r.max() - r.min() + 1) / CH if len(r) else 0.0
        ex = 0.0 if sc.sum() == 0 else (sm & ~sc).sum() / float(sc.sum())
        fa = 0.0 if sc.sum() == 0 else (sc & ~sm).sum() / float(sc.sum())
        iou = (sc & sm).sum() / max(1, (sc | sm).sum())
        dc = mod.hist(Cc[:, j:j + 1], Mc[:, j:j + 1])
        dm = mod.hist(Cm[:, j:j + 1], Mm[:, j:j + 1])
        top_c = mod.NOMES[int(dc.argmax())]
        top_m = mod.NOMES[int(dm.argmax())]
        print("  %.3f %.3f  %.3f  %+.3f | %6.1f%% %7.1f%% | %-9s(%.2f) IoU %.2f  %-9s(%.2f)" % (
            j / float(CW), ext(sc), ext(sm), ext(sm) - ext(sc), ex * 100, fa * 100,
            top_c, dc.max(), iou, top_m, dm.max()))
else:
    print("  lin  ext_c  ext_m   d_ext | excess%  falta% | IoU | domin_c / domin_m")
    for j in range(sl.start, sl.stop, max(1, (sl.stop - sl.start) // 12)):
        sc = Mc[j:j + 1, :][0]
        sm = Mm[j:j + 1, :][0]
        def ext(a):
            r = np.where(a)[0]
            return (r.max() - r.min() + 1) / CW if len(r) else 0.0
        ex = 0.0 if sc.sum() == 0 else (sm & ~sc).sum() / float(sc.sum())
        fa = 0.0 if sc.sum() == 0 else (sc & ~sm).sum() / float(sc.sum())
        iou = (sc & sm).sum() / max(1, (sc | sm).sum())
        dc = mod.hist(Cc[j:j + 1, :], Mc[j:j + 1, :])
        dm = mod.hist(Cm[j:j + 1, :], Mm[j:j + 1, :])
        print("  %.3f %.3f  %.3f  %+.3f | %6.1f%% %7.1f%% | %.2f | %-9s / %-9s" % (
            (CH - j) / float(CH), ext(sc), ext(sm), ext(sm) - ext(sc), ex * 100, fa * 100,
            iou, mod.NOMES[int(dc.argmax())], mod.NOMES[int(dm.argmax())]))

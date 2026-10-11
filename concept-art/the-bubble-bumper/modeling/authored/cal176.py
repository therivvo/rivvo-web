import numpy as np
exec(open('/tmp/visor.py').read().split("LIGHT = []")[0])

CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'


def perfil(p, g):
    a, f, k = M(p, g)
    cnt, (X0, X1, Y0, Y1) = bbox_comp(k)
    KX = 2.354 / (X1 - X0 + 1); KZ = 1.2523 / (Y1 - Y0 + 1)
    top = np.full(a.shape[1], -1)
    for col in range(X0, X1 + 1):
        colv = np.where(k[:, col])[0]
        if len(colv):
            top[col] = colv.min()
    return a, k, X1, Y1, KX, KZ, top


ac, kc, X1c, Y1c, KXc, KZc, tc = perfil(CP, True)
am, km, X1m, Y1m, KXm, KZm, tm = perfil('/tmp/R174_SIDE.png', False)
print('###CAL### concept X1=%d KX=%.6f KZ=%.6f | modelo X1=%d KX=%.6f KZ=%.6f' %
      (X1c, KXc, KZc, X1m, KXm, KZm))

# offset de registro por zona: para cada coluna-ancora do modelo (em x), acha o shift d que melhor
# alinha o perfil de TOPO do modelo com o do concept numa janela de +-18 colunas
print('###CAL### x        col_m  shift_px  x_efetivo_concept  erro_medio_px')
for x in (-0.34, -0.30, -0.26, -0.22, -0.18, -0.15, -0.12, -0.08, -0.04, 0.00, 0.10):
    colm = int(round(X1m - (x + 1.178) / KXm))
    melhor, melhord = None, 0
    for d in range(-12, 13):
        errs = []
        for dc in range(-18, 19):
            c = colm + dc
            cc = c + d
            if 0 <= c < len(tm) and 0 <= cc < len(tc) and tm[c] >= 0 and tc[cc] >= 0:
                errs.append(abs(int(tm[c]) - int(tc[cc])))
        if errs:
            e = sum(errs) / len(errs)
            if melhor is None or e < melhor:
                melhor, melhord = e, d
    xc = (X1c - (colm + melhord)) * KXc - 1.178
    print('###CAL### %+.2f   %5d   %+4d      %+.4f            %.2f' % (x, colm, melhord, xc, melhor))

# landmarks absolutos: coluna mais a esquerda e mais a direita da silhueta em cada imagem
for lbl, k, X1, KX in (('CONCEPT', kc, X1c, KXc), ('MODELO', km, X1m, KXm)):
    cols = [c for c in range(k.shape[1]) if k[:, c].any()]
    rows = [r for r in range(k.shape[0]) if k[r, :].any()]
    print('###CAL### %-8s silhueta: col %d..%d  row %d..%d  (larg=%d px, alt=%d px) -> L=%.3f H=%.3f' %
          (lbl, min(cols), max(cols), min(rows), max(rows), max(cols) - min(cols) + 1,
           max(rows) - min(rows) + 1, (max(cols) - min(cols) + 1) * KX, (max(rows) - min(rows) + 1) * KZ))

import sys
import numpy as np
from PIL import Image

RENDER = sys.argv[1] if len(sys.argv) > 1 else '/tmp/R156_SIDE.png'
CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'

exec(open('/tmp/visor.py').read().split("LIGHT = []")[0])


def cls(c, f):
    if np.abs(c - f).sum() < 40:
        return '.'
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    s = r + g + b
    if abs(r - g) < 34 and abs(g - b) < 34 and s > 300:
        return 'L'
    if b > r + 12 and b > g:
        return 'B'
    if s < 200:
        return 'D'
    if r > 130 and g > 105 and b < 0.62 * r and (r + g) > 2.05 * b:
        return 'Y'
    return 'o'


zs = [1.12, 1.10, 1.08, 1.06, 1.04, 1.02, 1.00, 0.98, 0.96, 0.94]
cols = {'borda -0.14': [-0.34, -0.30, -0.26, -0.22, -0.18, -0.14],
        'dentro -0.15': [-0.34, -0.30, -0.26, -0.22, -0.18, -0.15]}
res = {}
for lbl, p, g in (('CONCEPT', CP, True), ('MODELO', RENDER, False)):
    a, f, k = M(p, g)
    cnt, (X0, X1, Y0, Y1) = bbox_comp(k)
    KX = 2.354 / (X1 - X0 + 1)
    KZ = 1.2523 / (Y1 - Y0 + 1)
    res[lbl] = {tag: {z: [cls(a[int(round(Y1 - z / KZ)), int(round(X1 - (xw + 1.178) / KX))], f)
                          for xw in xs] for z in zs} for tag, xs in cols.items()}
for tag in cols:
    C = res['CONCEPT'][tag]
    Mm = res['MODELO'][tag]
    tot = hit = totL = hitL = 0
    for z in zs:
        for i in range(6):
            tot += 1
            hit += (C[z][i] == Mm[z][i])
            if C[z][i] == 'L':
                totL += 1
                hitL += (Mm[z][i] == 'L')
    print('%-12s GLOBAL %d/%d = %.0f%%   CLARO concept=%d modelo=%d acerto=%d'
          % (tag, hit, tot, 100. * hit / tot, totL,
             sum(1 for z in zs for v in Mm[z] if v == 'L'), hitL))

xsb = [-0.30, -0.26, -0.22, -0.18, -0.16, -0.15]
print()
print('###BORDA### borda inferior do claro:  ' + '  '.join('%+.2f' % x for x in xsb))
for lbl, p, g in (('CONCEPT', CP, True), ('MODELO ' + RENDER.split('/')[-1], RENDER, False)):
    a, f, k = M(p, g)
    cnt, (X0, X1, Y0, Y1) = bbox_comp(k)
    KX = 2.354 / (X1 - X0 + 1)
    KZ = 1.2523 / (Y1 - Y0 + 1)
    linha = []
    for xw in xsb:
        col = int(round(X1 - (xw + 1.178) / KX))
        achou = None
        for z in np.arange(1.14, 0.84, -0.005):
            row = int(round(Y1 - z / KZ))
            if 0 <= row < a.shape[0] and abs(a[row, col] - f).sum() >= 40 and cls(a[row, col], f) == 'L':
                achou = z
        linha.append(achou if achou else float('nan'))
    print('###BORDA### %-24s' % lbl + '  '.join(('%.3f' % v if v == v else '  -- ') for v in linha))

print()
print('erros restantes (amostra "dentro -0.15"):')
C = res['CONCEPT']['dentro -0.15']
Mm = res['MODELO']['dentro -0.15']
n = 0
for z in zs:
    for i, x in enumerate(cols['dentro -0.15']):
        if C[z][i] != Mm[z][i]:
            n += 1
            print('   z=%.2f x=%+.2f  concept=%s  modelo=%s' % (z, x, C[z][i], Mm[z][i]))
print('   TOTAL DE ERROS: %d de 60' % n)

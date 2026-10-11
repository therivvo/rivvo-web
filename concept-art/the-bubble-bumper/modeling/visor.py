import re
import numpy as np
from PIL import Image
from collections import deque

def M(path, use_grade):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    f = a[3, 3]
    d = np.abs(a - f).sum(axis=2)
    if use_grade:
        gr = (np.abs(a[:, :, 0] - a[:, :, 1]) < 12) & (np.abs(a[:, :, 1] - a[:, :, 2]) < 12) & (a.mean(axis=2) > 120) & (a.mean(axis=2) < 240)
        k = (d > 45) & (~gr)
    else:
        k = d > 45
    return a, f, k

def bbox_comp(k):
    H, W = k.shape
    seen = np.zeros_like(k, dtype=bool)
    best = (0, None)
    ys, xs = np.where(k)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)]); seen[y0, x0] = True
        cnt = 0; mnx = mxx = x0; mny = mxy = y0
        while q:
            y, x = q.popleft(); cnt += 1
            mnx = min(mnx, x); mxx = max(mxx, x); mny = min(mny, y); mxy = max(mxy, y)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and k[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True; q.append((ny, nx))
        if cnt > best[0]:
            best = (cnt, (mnx, mxx, mny, mxy))
    return best

CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'
a, f, k = M(CP, True)
cnt, (X0, X1, Y0, Y1) = bbox_comp(k)
KX = 2.354 / (X1 - X0 + 1); KZ = 1.2523 / (Y1 - Y0 + 1)

LIGHT = []
print('VARREDURA DO CAPACETE NO CONCEPT (px -> RGB; L=claro/cromado, B=azul, D=escuro, .=fundo)')
print('      x:  ' + ' '.join('%+.3f' % (-0.34 + 0.02 * i) for i in range(11)))
for z in [1.14, 1.12, 1.10, 1.08, 1.06, 1.04, 1.02, 1.00, 0.98, 0.96]:
    yp = int(round(Y1 - z / KZ))
    row = []
    for i in range(11):
        xw = -0.34 + 0.02 * i
        xp = int(round(X1 - (xw + 1.178) / KX))
        c = a[yp, xp]
        if np.abs(c - f).sum() < 40:
            row.append('  .   ')
            continue
        r, g, b = int(c[0]), int(c[1]), int(c[2])
        s = r + g + b
        if abs(r - g) < 30 and abs(g - b) < 30 and s > 300:
            t = 'L'
            LIGHT.append((round(xw, 3), z, (r, g, b)))
        elif b > r + 12:
            t = 'B'
        elif s < 260:
            t = 'D'
        else:
            t = 'o'
        row.append('%s%3d,%3d,%3d' % (t, r, g, b))
    print('z=%.2f ' % z + ' '.join(row))

print()
print('PIXELS CLAROS/CROMADOS (L) no capacete: %d' % len(LIGHT))
if LIGHT:
    xs = [p[0] for p in LIGHT]; zs = [p[1] for p in LIGHT]
    print('  extensao: x %.3f..%.3f | z %.2f..%.2f' % (min(xs), max(xs), min(zs), max(zs)))
    for p in LIGHT[:12]:
        print('    x=%+.3f z=%.2f RGB=%s' % p)

src = open('/tmp/v135.py').read()
print()
print('OBJETOS/MATERIAIS DE VISOR NO BUILD:')
for m in re.finditer(r'^.*(?:Visor|VISOR|Vis|VIS)[^\n]*$', src, re.M):
    print('  ' + m.group(0).strip()[:150])
print()
print('DEFINICOES DE MATERIAL CLARO/CHROME:')
for name in ('M_CHROME', 'M_VISL', 'M_VISD', 'M_GLASS'):
    for m in re.finditer(r'^.*' + name + r'\s*=.*$', src, re.M):
        print('  ' + m.group(0).strip()[:160])

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

def cls(c, f):
    if np.abs(c - f).sum() < 40:
        return '.'
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    s = r + g + b
    if s < 200:
        return 'D'
    if b > r + 12 and b > g:
        return 'B'
    if r > 130 and g > 105 and b < 0.62 * r and (r + g) > 2.05 * b:
        return 'Y'
    if abs(r - g) < 26 and abs(g - b) < 26 and s > 330:
        return 'C'
    return 'o'

def grid(path, use_grade, xs, zs, label):
    a, f, k = M(path, use_grade)
    cnt, (X0, X1, Y0, Y1) = bbox_comp(k)
    KX = 2.354 / (X1 - X0 + 1); KZ = 1.2523 / (Y1 - Y0 + 1)
    print('--- %s | comp=%dpx x %d..%d y %d..%d | KX=%.6f KZ=%.6f ---' % (label, cnt, X0, X1, Y0, Y1, KX, KZ))
    print('      z\\x  ' + ' '.join('%+.2f' % x for x in xs))
    for z in zs:
        yp = int(round(Y1 - z / KZ))
        row = []
        for xw in xs:
            xp = int(round(X1 - (xw + 1.178) / KX))
            row.append(cls(a[yp, xp], f) if 0 <= yp < a.shape[0] and 0 <= xp < a.shape[1] else '?')
        print('   z=%.2f    ' % z + '     '.join(row))

xs = [-0.46, -0.42, -0.38, -0.34, -0.30, -0.26, -0.22, -0.18, -0.14]
zs = [1.05, 1.00, 0.95, 0.90, 0.85, 0.80]
CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'
grid(CP, True, xs, zs, 'CONCEPT side CORRIGIDO')
grid('/tmp/R137_SIDE.png', False, xs, zs, 'MODELO v137')

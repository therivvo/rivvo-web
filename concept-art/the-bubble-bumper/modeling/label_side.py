import numpy as np
from PIL import Image
from collections import deque

def build(path, use_grade):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    f = a[3, 3]
    d = np.abs(a - f).sum(axis=2)
    if use_grade:
        gr = (np.abs(a[:, :, 0] - a[:, :, 1]) < 12) & (np.abs(a[:, :, 1] - a[:, :, 2]) < 12) & (a.mean(axis=2) > 120) & (a.mean(axis=2) < 240)
        k = (d > 45) & (~gr)
    else:
        k = d > 45
    return a, f, k

def strip_grid(k, thr=0.80):
    H, W = k.shape
    rowfill = k.sum(axis=1) / float(W)
    colfill = k.sum(axis=0) / float(H)
    bad_r = rowfill > thr
    bad_c = colfill > thr
    k2 = k.copy()
    k2[bad_r, :] = False
    k2[:, bad_c] = False
    return k2, int(bad_r.sum()), int(bad_c.sum())

def largest_comp_bbox(k):
    H, W = k.shape
    seen = np.zeros_like(k, dtype=bool)
    best = (0, None)
    ys, xs = np.where(k)
    pts = set(zip(ys.tolist(), xs.tolist()))
    for (y0, x0) in zip(ys.tolist(), xs.tolist()):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        cnt = 0
        miny = maxy = y0
        minx = maxx = x0
        while q:
            y, x = q.popleft()
            cnt += 1
            if y < miny: miny = y
            if y > maxy: maxy = y
            if x < minx: minx = x
            if x > maxx: maxx = x
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and k[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if cnt > best[0]:
            best = (cnt, (minx, maxx, miny, maxy))
    return best

CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'
a, f, k = build(CP, True)
k2, nr, nc = strip_grid(k)
print('concept side: grade removida -> %d linhas, %d colunas' % (nr, nc))
cnt, (X0, X1, Y0, Y1) = largest_comp_bbox(k2)
print('maior componente: %d px | x %d..%d (%d) | y %d..%d (%d)' % (cnt, X0, X1, X1 - X0 + 1, Y0, Y1, Y1 - Y0 + 1))
KX = 2.354 / (X1 - X0 + 1); KZ = 1.2523 / (Y1 - Y0 + 1)
print('CALIBRACAO CORRETA: KX=%.6f KZ=%.6f (razao KX/KZ=%.4f)' % (KX, KZ, KX / KZ))
print('calibracao anterior (mascara inteira): KX=%.6f KZ=%.6f' % (2.354 / 993.0, 1.2523 / 490.0))
print('=> erro anterior: KX %.0f%% menor, KZ %.0f%% menor' % (
    100 * (1 - (2.354 / 993.0) / KX), 100 * (1 - (1.2523 / 490.0) / KZ)))
np.save('/tmp/calib_concept_side.npy', np.array([X0, X1, Y0, Y1, KX, KZ]))

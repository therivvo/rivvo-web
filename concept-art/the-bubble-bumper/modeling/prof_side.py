import numpy as np
from PIL import Image

def prof(path, use_grade):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    f = a[3, 3]
    d = np.abs(a - f).sum(axis=2)
    if use_grade:
        gr = (np.abs(a[:, :, 0] - a[:, :, 1]) < 12) & (np.abs(a[:, :, 1] - a[:, :, 2]) < 12) & (a.mean(axis=2) > 120) & (a.mean(axis=2) < 240)
        k = (d > 45) & (~gr)
    else:
        k = d > 45
    ysx = np.where(k.sum(axis=1) > 3)[0]
    xsx = np.where(k.sum(axis=0) > 3)[0]
    X0, X1, Y0, Y1 = xsx[0], xsx[-1], ysx[0], ysx[-1]
    KX = 2.354 / (X1 - X0 + 1)
    KZ = 1.2523 / (Y1 - Y0 + 1)
    out = {}
    for xw in np.arange(-1.30, 1.31, 0.05):
        xp = int(round(X1 - (xw + 1.178) / KX))
        if xp < 0 or xp >= a.shape[1]:
            continue
        col = k[:, xp]
        idx = np.where(col)[0]
        if len(idx) == 0:
            out[round(xw, 2)] = None
            continue
        out[round(xw, 2)] = ((Y1 - idx.min()) * KZ, (Y1 - idx.max()) * KZ)
    return out

CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'
c = prof(CP, True)
m = prof('/tmp/R136_SIDE.png', False)
print('  x    | concept topo | modelo topo | delta topo | concept base | modelo base')
for x in sorted(c.keys()):
    cc = c[x]; mm = m.get(x)
    if cc is None and mm is None:
        continue
    cs = '%.3f' % cc[0] if cc else '  --  '
    ms = '%.3f' % mm[0] if mm else '  --  '
    dl = '%+.3f' % (mm[0] - cc[0]) if (cc and mm) else '  --  '
    cb = '%.3f' % cc[1] if cc else '  --  '
    mb = '%.3f' % mm[1] if mm else '  --  '
    flag = ''
    if cc and mm and abs(mm[0] - cc[0]) > 0.04:
        flag = ' <<<' if mm[0] < cc[0] else ' >>>'
    print(' %+.2f | %s       | %s      | %s  | %s       | %s%s' % (x, cs, ms, dl, cb, mb, flag))

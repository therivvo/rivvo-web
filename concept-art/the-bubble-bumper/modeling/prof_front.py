import numpy as np
from PIL import Image

def prof(path, use_grade, width_m=1.4411):
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
    cx = (X0 + X1) / 2.0
    KX = width_m / (X1 - X0 + 1)
    KZ = 1.2523 / (Y1 - Y0 + 1)
    out = {}
    for z in np.arange(0.05, 1.30, 0.05):
        yp = int(round(Y1 - z / KZ))
        if yp < 0 or yp >= a.shape[0]:
            continue
        row = k[yp]
        idx = np.where(row)[0]
        if len(idx) == 0:
            out[round(z, 2)] = None
            continue
        out[round(z, 2)] = (max(abs(idx.min() - cx), abs(idx.max() - cx)) * KX, (idx.max() - idx.min() + 1) * KX)
    return out

CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/front.jpg'
c = prof(CP, True)
m = prof('/tmp/R135_FRONT.png', False)
print(' z    | concept meio | modelo meio | delta   | concept vao | modelo vao')
for z in sorted(c.keys()):
    cc = c[z]; mm = m.get(z)
    if cc is None and mm is None:
        continue
    cs = '%.3f' % cc[0] if cc else '  --  '
    ms = '%.3f' % mm[0] if mm else '  --  '
    dl = '%+.3f' % (mm[0] - cc[0]) if (cc and mm) else '  --  '
    cv = '%.3f' % cc[1] if cc else '  --  '
    mv = '%.3f' % mm[1] if mm else '  --  '
    flag = ''
    if cc and mm and abs(mm[0] - cc[0]) > 0.05:
        flag = ' <<<' if mm[0] < cc[0] else ' >>>'
    print(' %.2f | %s        | %s       | %s | %s      | %s%s' % (z, cs, ms, dl, cv, mv, flag))

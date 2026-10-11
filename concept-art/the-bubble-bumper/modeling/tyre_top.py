import numpy as np
from PIL import Image

def tyre_top(path, use_grade, wm=1.4411):
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
    KX = wm / (X1 - X0 + 1)
    KZ = 1.2523 / (Y1 - Y0 + 1)
    print('--- %s ---' % path.split('/')[-1])
    for yw in (0.72, 0.70, 0.68, 0.66, 0.62, 0.58, 0.54):
        xp = int(round(cx + yw / KX))
        col = k[:, xp]
        idx = np.where(col)[0]
        if len(idx) == 0:
            print('   |y|=%.2f -> vazio' % yw)
            continue
        ztop = (Y1 - idx.min()) * KZ
        zbot = (Y1 - idx.max()) * KZ
        print('   |y|=%.2f -> objeto de z=%.3f a z=%.3f (altura %.3f m)' % (yw, zbot, ztop, ztop - zbot))

CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/front.jpg'
tyre_top(CP, True)
tyre_top('/tmp/R136_FRONT.png', False)

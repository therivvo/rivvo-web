import numpy as np
from PIL import Image

try:
    from scipy import ndimage
    HAVE = True
except Exception:
    HAVE = False

def mask_of(path, use_grade):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    f = a[3, 3]
    d = np.abs(a - f).sum(axis=2)
    if use_grade:
        gr = (np.abs(a[:, :, 0] - a[:, :, 1]) < 12) & (np.abs(a[:, :, 1] - a[:, :, 2]) < 12) & (a.mean(axis=2) > 120) & (a.mean(axis=2) < 240)
        k = (d > 45) & (~gr)
    else:
        k = d > 45
    return a, f, k

def largest_bbox(k):
    if not HAVE:
        ysx = np.where(k.sum(axis=1) > 3)[0]
        xsx = np.where(k.sum(axis=0) > 3)[0]
        return xsx[0], xsx[-1], ysx[0], ysx[-1], None
    lab, n = ndimage.label(k)
    if n == 0:
        return None
    sizes = ndimage.sum(k, lab, range(1, n + 1))
    big = int(np.argmax(sizes)) + 1
    comp = (lab == big)
    ys = np.where(comp.any(axis=1))[0]
    xs = np.where(comp.any(axis=0))[0]
    return xs[0], xs[-1], ys[0], ys[-1], (sizes[big - 1], n)

print('scipy disponivel:', HAVE)
CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'
for lbl, p, g in (('CONCEPT side', CP, True), ('MODELO v136 SIDE', '/tmp/R136_SIDE.png', False)):
    a, f, k = mask_of(p, g)
    X0, X1, Y0, Y1, extra = largest_bbox(k)
    ysx = np.where(k.sum(axis=1) > 3)[0]
    xsx = np.where(k.sum(axis=0) > 3)[0]
    print('%s: mascara-inteira x %d..%d y %d..%d | MAIOR COMPONENTE x %d..%d y %d..%d' % (
        lbl, xsx[0], xsx[-1], ysx[0], ysx[-1], X0, X1, Y0, Y1))
    KX = 2.354 / (X1 - X0 + 1)
    KZ_c = 1.2523 / (Y1 - Y0 + 1)
    KZ_old = 1.2523 / (ysx[-1] - ysx[0] + 1)
    print('   KX=%.6f | KZ (maior comp)=%.6f | KZ (mascara inteira)=%.6f | diferenca=%.2f%%' % (
        KX, KZ_c, KZ_old, 100 * abs(KZ_c - KZ_old) / KZ_old))
    if extra:
        print('   tamanho da maior componente: %d px de %d componentes' % (extra[0], extra[1]))

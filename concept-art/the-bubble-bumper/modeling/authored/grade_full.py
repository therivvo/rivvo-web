import numpy as np
from PIL import Image

# CORRECAO: CADA IMAGEM TEM ESCALA DE PIXEL PROPRIA -> cada uma usa SEUS proprios ancoras.
# (foi este o erro do medidor "A'": apliquei X1=886/KX=0.003146 -- do concept -- ao render do modelo,
#  que mede 478x253 px. Por isso o modelo deu '.' em toda a grade.)
# medidor anterior (med_fair.py) ja fazia isso certo; o que estava sujo era a MASCARA do concept.
CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'
MP = '/tmp/R174_SIDE.png'
concept = np.array(Image.open(CP).convert('RGB')).astype(int)
modelo = np.array(Image.open(MP).convert('RGB')).astype(int)
mask_c = np.load('/tmp/mask_side_clean2.npy')

yc, xc = np.where(mask_c)
CX0, CX1, CY0, CY1 = xc.min(), xc.max(), yc.min(), yc.max()
KXc = 2.354 / (CX1 - CX0 + 1)
KZc = 1.2523 / (CY1 - CY0 + 1)

fm = modelo[5, 5]
km = np.abs(modelo - fm).sum(2) > 40
ym, xm = np.where(km)
MX0, MX1, MY0, MY1 = xm.min(), xm.max(), ym.min(), ym.max()
KXm = 2.354 / (MX1 - MX0 + 1)
KZm = 1.2523 / (MY1 - MY0 + 1)
print('###F### CONCEPT bbox col %d..%d row %d..%d KX=%.6f KZ=%.6f raz=L/H %.3f' %
      (CX0, CX1, CY0, CY1, KXc, KZc, (CX1 - CX0 + 1) / (CY1 - CY0 + 1)))
print('###F### MODELO  bbox col %d..%d row %d..%d KX=%.6f KZ=%.6f raz=L/H %.3f' %
      (MX0, MX1, MY0, MY1, KXm, KZm, (MX1 - MX0 + 1) / (MY1 - MY0 + 1)))


def px(X1, Y1, KX, KZ, shape, x, z):
    col = int(round(X1 - (x + 1.178) / KX)); row = int(round(Y1 - z / KZ))
    return max(0, min(shape[0] - 1, row)), max(0, min(shape[1] - 1, col))


def cls(px_):
    r, g, b = int(px_[0]), int(px_[1]), int(px_[2]); s = r + g + b
    if abs(r - g) < 35 and abs(g - b) < 35 and s > 300:
        return 'L'
    if b > r + 12 and b > g:
        return 'B'
    if s < 200:
        return 'D'
    if r > 130 and g > 105 and b < 0.62 * r and (r + g) > 2.05 * b:
        return 'Y'
    return 'o'


XCOLS = [-0.30, -0.26, -0.22, -0.18, -0.16, -0.15, -0.14, -0.12, -0.10]
ZROWS = [round(0.90 + 0.02 * i, 3) for i in range(16)]

print('###F###        ' + ' '.join('%+.2f' % x for x in XCOLS))
erros = []
totc = acerto = claro_c = claro_m = 0
for z in ZROWS:
    lc = lm = ''
    for x in XCOLS:
        rc, cc = px(CX1, CY1, KXc, KZc, concept.shape, x, z)
        rm, cm = px(MX1, MY1, KXm, KZm, modelo.shape, x, z)
        cfundo = not mask_c[rc, cc]
        mfundo = np.abs(modelo[rm, cm] - fm).sum() < 40
        a = '.' if cfundo else cls(concept[rc, cc])
        b = '.' if mfundo else cls(modelo[rm, cm])
        lc += a; lm += b
        if cfundo:
            continue
        totc += 1
        if a == 'L':
            claro_c += 1
            if b == 'L':
                claro_m += 1; acerto += 1
        if a != b:
            erros.append((z, x, a, b, tuple(int(v) for v in concept[rc, cc]), tuple(int(v) for v in modelo[rm, cm])))
    print('###F### z=%.2f C:%s  M:%s' % (z, lc, lm))
print('###F### dentro(concept nao-fundo)=%d | claro concept=%d modelo=%d acerto=%d | ERROS=%d' %
      (totc, claro_c, claro_m, acerto, len(erros)))
for e in erros:
    print('###F###   z=%.2f x=%+.2f C=%s %s | M=%s %s' % e)

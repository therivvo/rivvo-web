import numpy as np
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


CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'
img = {}
for lbl, p, g in (('CONCEPT', CP, True), ('MODELO', '/tmp/R175_SIDE.png', False)):
    a, f, k = M(p, g)
    cnt, (X0, X1, Y0, Y1) = bbox_comp(k)
    img[lbl] = (a, f, X1, Y1, 2.354 / (X1 - X0 + 1), 1.2523 / (Y1 - Y0 + 1))

print('###NB175### vizinhanca 9x5 px em (z=1.06, x=-0.15) — a linha preta e ESTREITA')
for lbl in ('CONCEPT', 'MODELO'):
    a, f, X1, Y1, KX, KZ = img[lbl]
    col = int(round(X1 - (-0.15 + 1.178) / KX))
    row = int(round(Y1 - 1.06 / KZ))
    print('###NB175###   %-8s col=%d row=%d' % (lbl, col, row))
    for dr in (-2, -1, 0, 1, 2):
        linha = ''.join(cls(a[row + dr, col + dc], f) for dc in (-4, -3, -2, -1, 0, 1, 2, 3, 4))
        rgb = a[row + dr, col]
        print('###NB175###     %s  centro_rgb=(%d,%d,%d) soma=%d' %
              (linha, int(rgb[0]), int(rgb[1]), int(rgb[2]), int(rgb.sum())))

# onde estao os pixels PRETOS (soma<120) em cada imagem na janela x -0.17..-0.14, z 1.03..1.09
print('###NB175### mapa de PRETOS (soma<120) na janela x -0.17..-0.14 (0.005), z 1.03..1.09 (0.005)')
for lbl in ('CONCEPT', 'MODELO'):
    a, f, X1, Y1, KX, KZ = img[lbl]
    linhas = []
    for j in range(13):
        z = 1.03 + 0.005 * j
        row = int(round(Y1 - z / KZ))
        s = ''
        for i in range(7):
            x = -0.17 + 0.005 * i
            col = int(round(X1 - (x + 1.178) / KX))
            s += '#' if a[row, col].sum() < 120 else '.'
        linhas.append('z=%.3f %s' % (z, s))
    print('###NB175###   %s: %s' % (lbl, ' | '.join(linhas)))

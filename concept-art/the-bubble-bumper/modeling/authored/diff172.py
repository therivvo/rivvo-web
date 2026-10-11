import numpy as np
exec(open('/tmp/visor.py').read().split("LIGHT = []")[0])


def carrega(p):
    a, f, k = M(p, False)
    cnt, (X0, X1, Y0, Y1) = bbox_comp(k)
    return a, f, 2.354 / (X1 - X0 + 1), 1.2523 / (Y1 - Y0 + 1), X1, Y1


a8, f8, KX, KZ, X1, Y1 = carrega('/tmp/R168_SIDE.png')
a2, f2, _, _, _, _ = carrega('/tmp/R172_SIDE.png')
print('###DIFF### zona do topo-traseiro (x -0.19..-0.13, z 1.08..1.17) - luminancia media')
for tag, a, f in (('v168', a8, f8), ('v172', a2, f2)):
    vals = []
    for i in range(13):
        xw = -0.19 + 0.005 * i
        col = int(round(X1 - (xw + 1.178) / KX))
        for j in range(19):
            z = 1.08 + 0.005 * j
            row = int(round(Y1 - z / KZ))
            c = a[row, col]
            if np.abs(c - f).sum() < 40:
                continue
            vals.append(float(c.mean()))
    print('###DIFF###   %s: n=%d | luminancia media=%.1f | max=%.1f' %
          (tag, len(vals), np.mean(vals) if vals else -1, np.max(vals) if vals else -1))

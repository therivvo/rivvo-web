import numpy as np
from PIL import Image
from collections import deque

CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'
img = np.array(Image.open(CP).convert('RGB')).astype(int)
H, W = img.shape[:2]
r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
mx = np.maximum(np.maximum(r, g), b)
mn = np.minimum(np.minimum(r, g), b)
sat = mx - mn

# 1) máscara BRUTA como o medidor velho: distância do fundo
fundo = img[H // 2, 0]
dist = np.abs(img - fundo).sum(axis=2)
mask_velha = dist > 40
print('###CLEAN### fundo=%s' % (fundo.tolist(),))


def comp_principal(mask):
    vis = np.zeros(mask.shape, bool)
    melhor = []
    for y in range(H):
        for x in range(W):
            if mask[y, x] and not vis[y, x]:
                f = []
                fila = deque([(y, x)]); vis[y, x] = True
                while fila:
                    yy, xx = fila.popleft(); f.append((yy, xx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = yy + dy, xx + dx
                            if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not vis[ny, nx]:
                                vis[ny, nx] = True; fila.append((ny, nx))
                if len(f) > len(melhor):
                    melhor = f
    return melhor


mp = comp_principal(mask_velha)
ys = [p[0] for p in mp]; xs = [p[1] for p in mp]
print('###CLEAN### VELHA (dist>40): componente %d px | bbox col %d..%d row %d..%d (larg=%d alt=%d)' %
      (len(mp), min(xs), max(xs), min(ys), max(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
# quantos px da máscara velha são 100% grade (cinza neutro 140..230)?
npc = 0
for (yy, xx) in mp:
    v = img[yy, xx]
    if int(v.max() - v.min()) < 12 and 140 < int(v.mean()) < 230:
        npc += 1
print('###CLEAN### VELHA: %d px = GRADE (cinza neutro 140..230) -> %.1f%%' % (npc, 100.0 * npc / len(mp)))

# 2) máscara LIMPA: SATURAÇÃO (objeto é colorido/brilhante/escuro; grade é cinza neutro)
#    inclui: pixels saturados (cor) OU muito escuros (pneu/sombra do objeto) OU muito claros (visor)
obj = (sat > 25) | (mx < 60)   # cor viva ou quase-preto (pneu)
obj &= (dist > 40)             # e diferente do fundo
mo = comp_principal(obj)
ys = [p[0] for p in mo]; xs = [p[1] for p in mo]
print('###CLEAN### LIMPA (sat>25 | max<60): componente %d px | bbox col %d..%d row %d..%d (larg=%d alt=%d)' %
      (len(mo), min(xs), max(xs), min(ys), max(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
npc = 0
for (yy, xx) in mo:
    v = img[yy, xx]
    if int(v.max() - v.min()) < 12 and 140 < int(v.mean()) < 230:
        npc += 1
print('###CLEAN### LIMPA: %d px = GRADE -> %.2f%%' % (npc, 100.0 * npc / max(1, len(mo))))

# 3) revalidar ÂNCORAS com a máscara limpa (dimensões em px; o zoom por px vem do contrato)
larg = max(xs) - min(xs) + 1; alt = max(ys) - min(ys) + 1
print('###CLEAN### razao L/H limpa = %.3f (contrato 1.877) | razao W/H esperada 1.151 (p/ TOP)' %
      (larg / alt))
KX = 2.354 / larg; KZ = 1.2523 / alt
print('###CLEAN### KX=%.6f KZ=%.6f  (KX*LARG=%.4f, KZ*ALT=%.4f)' % (KX, KZ, KX * larg, KZ * alt))
# topo/coluna nas colunas do nariz e da traseira com a máscara limpa
km = np.zeros((H, W), bool)
for (yy, xx) in mo:
    km[yy, xx] = True
X1 = max(xs)
for nome, x in (('x=-1.00 (frente)', -1.0), ('x=+1.00 (tras)', 1.0)):
    col = int(round(X1 - (x + 1.178) / KX)); col = max(0, min(W - 1, col))
    colv = np.where(km[:, col])[0]
    if len(colv):
        print('###CLEAN###   %s col=%d z_topo=%.3f altura_coluna=%.3f m' %
              (nome, col, (max(ys) - colv.min()) * KZ, (colv.max() - colv.min() + 1) * KZ))
    else:
        print('###CLEAN###   %s col=%d VAZIO' % (nome, col))
# salvar a máscara limpa p/ reutilizar
Image.fromarray((km * 255).astype(np.uint8)).save('/tmp/mask_side_clean.png')
np.save('/tmp/mask_side_clean.npy', km)
print('###CLEAN### mascara salva em /tmp/mask_side_clean.(png|npy)')

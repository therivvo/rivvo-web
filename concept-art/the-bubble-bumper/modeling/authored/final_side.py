import numpy as np
from PIL import Image

# MASK LIMPA + ANCHOR CALIBRADO (A'/compass): KX=KZ=0.003146, X1=886, Y0=85, Y1=482
KX = KZ = 0.003146
X1, Y0, Y1 = 886, 85, 482


def load(p):
    return np.array(Image.open(p).convert('RGB')).astype(int)


def cls(copt, cmod=None):
    # classifica pixel por familia; concept e modelo usam fundos diferentes —
    # passa os dois pixels para julgar '.' como 'ambos fundo' apenas
    r, g, b = int(copt[0]), int(copt[1]), int(copt[2])
    s = r + g + b
    if abs(r - g) < 35 and abs(g - b) < 35 and s > 300:
        return 'L'
    if b > r + 12 and b > g:
        return 'B'
    if s < 200:
        return 'D'
    if r > 130 and g > 105 and b < 0.62 * r and (r + g) > 2.05 * b:
        return 'Y'
    return 'o'


CP = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'
MP = '/tmp/R174_SIDE.png'
concept = load(CP)
modelo = load(MP)
mask = np.load('/tmp/mask_side_clean2.npy')

# fundo do modelo (medido uma vez): canto superior esquerdo do render
fundo_mod = modelo[5, 5]

# raycast por (x,z) -> pixel do CONCEPT (anchors A') e do MODELO (mesmo anchors — mesmo contrato)
# a grade de medicao: colunas de x e linhas de z usadas desde v151
XCOLS = [-0.30, -0.26, -0.22, -0.18, -0.16, -0.15, -0.14, -0.12, -0.10]
ZROWS = [round(0.90 + 0.02 * i, 3) for i in range(16)]  # 0.90..1.20


def pxc(img, x, z):
    col = int(round(X1 - (x + 1.178) / KX))
    row = int(round(Y1 - z / KZ))
    col = max(0, min(img.shape[1] - 1, col))
    row = max(0, min(img.shape[0] - 1, row))
    return row, col


print('###FINAL### grade SIDE com MASCARA LIMPA + anchors A\'')
print('###FINAL###       ' + '  '.join('x=%+.2f' % x for x in XCOLS))
erros = []
totc = totm = acerto = 0
for z in ZROWS:
    lc, lm = '', ''
    for x in XCOLS:
        rc, cc = pxc(concept, x, z)
        rm, cm = pxc(modelo, x, z)
        # concept é 'fundo' se pixel NAO pertence a mascara limpa
        pc = concept[rc, cc]
        pm = modelo[rm, cm]
        concept_fundo = not mask[rc, cc]
        pm_rgi = np.abs(pm - fundo_mod).sum() < 40
        if concept_fundo:
            cl_concept = '.'  # fundo do concept — excluido da metrica justa
        else:
            cl_concept = cls(pc)
        cl_modelo = '.' if pm_rgi else cls(pm)
        lc += cl_concept; lm += cl_modelo
        if cl_concept == '.':
            continue  # celula de fundo: fora do denominador (regra justa)
        totc += 1
        if cl_concept == 'L':
            totm += 1 if cl_modelo == 'L' else 0
        if cl_modelo == 'L' and cl_concept == 'L':
            acerto += 1
        if cl_modelo != cl_concept:
            erros.append((z, x, cl_concept, cl_modelo,
                          tuple(int(v) for v in pc), tuple(int(v) for v in pm)))
    print('###FINAL### z=%.2f  C:%s   M:%s' % (z, lc, lm))

print('###FINAL### dentro (concept nao-fundo): %d' % totc)
print('###FINAL### claro: concept=(ver abaixo) acertos=%d' % acerto)
print('###FINAL### ERROS (%d):' % len(erros))
for e in erros:
    print('###FINAL###   z=%.2f x=%+.2f concept=%s rgb=%s | modelo=%s rgb=%s' % e)

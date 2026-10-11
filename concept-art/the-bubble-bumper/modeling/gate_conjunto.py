#!/usr/bin/env python3
"""Gate de fidelidade do CONJUNTO (3 eixos medidos contra o concept).

USO:
  blender -b --factory-startup --python gate_conjunto.py -- <render_SIDE.png> [<blend>]

EIXOS (todos comparados contra o concept medido, mesma vista SIDE):
  1. PERFIL  — altura do topo da silhueta por estacao (10..90% da frente), em metros.
               Instrumento: chao em y=484 px, topo em y=84, escala 1.2523/400 m/px;
               trim na cota de comprimento x 122..885 (a linha de cota infla o comprimento).
  2. VAZIO   — fracao VAZIA da coluna entre topo e base, por estacao. Pega "casco continuo"
               que o perfil sozinho nao pega (regra 204).
  3. CONTATO — pares estruturais com intersecao volumetrica REAL (BVH overlap), nao bbox.
               Pega "blobs desconectados" (regra 213).

POR QUE OS TRES: o perfil pode ser otimizado por overfitting de contorno (delta 4,2 cm com o
modelo ainda solido); o vazio pega isso; e o contato pega o que nenhum dos dois ve.

SAIDA: ###GC### linhas com cada eixo + SCORE. Quanto MENOR o SCORE, melhor.
"""
import sys, os, json
import numpy as np
from PIL import Image

R = '/mnt/storage2TB/Coding-Projects/super-kart-3djs/'
REF = R + 'concept-art/the-bubble-bumper/assets/reference-orthographic/side.jpg'
H = 1.2523
GY, HY = 484, 84                 # chao e topo do concept em pixels
SC = H / (GY - HY)               # metros por pixel
XL = (122, 885)                  # span da cota de comprimento do concept
PESO_CONTATO = 0.05              # cada par flutuante vale 5 cm de penalidade no SCORE


def kart_concept():
    a = np.asarray(Image.open(REF).convert('RGB')).astype(int)
    lum = a[:, :, 0] * .299 + a[:, :, 1] * .587 + a[:, :, 2] * .114
    sat = a.max(axis=2) - a.min(axis=2)
    k = (sat > 45) | (lum < 70)
    k[:, :XL[0]] = False; k[:, XL[1] + 1:] = False; k[GY + 2:, :] = False
    return k


def kart_render(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    bg = np.median(a[:6, :6].reshape(-1, 3), axis=0)
    return np.abs(a - bg).sum(axis=2) > 42


def eixos(k, x0, x1, base, esc, n=9):
    tops, voids = [], []
    for i in range(1, n + 1):
        u = max(x0, min(int(x0 + (i / 10) * (x1 - x0 + 1)) - 1, x1))
        col = np.where(k[:base + 1, u])[0]
        if len(col) == 0:
            tops.append(None); voids.append(None); continue
        tops.append(round((base - col.min()) * esc, 3))
        h = col.max() - col.min() + 1
        voids.append(round((h - len(col)) / max(h, 1), 3))
    return tops, voids


def main(render_path, contato_json=None, blend=None):
    a = kart_concept(); ys, xs = np.where(a)
    ct, cv = eixos(a, xs.min(), xs.max(), GY, SC)
    b = kart_render(render_path); ys2, xs2 = np.where(b)
    mt, mv = eixos(b, xs2.min(), xs2.max(), ys2.max(), H / (ys2.max() - ys2.min() + 1))
    dp = [abs(x - y) for x, y in zip(ct, mt) if x is not None and y is not None]
    dv = [abs(x - y) for x, y in zip(cv, mv) if x is not None and y is not None]
    e_perfil = sum(dp) / len(dp)
    e_vazio = sum(dv) / len(dv)
    flut = 0; total_pares = 0
    if contato_json and os.path.exists(contato_json):
        d = json.load(open(contato_json))
        flut = d.get("flutuando", 0); total_pares = d.get("pares", 0)
    score = e_perfil + e_vazio + PESO_CONTATO * flut
    print("###GC### perfil : erro medio = %.3f m  (estacoes 10..90%%)" % e_perfil)
    print("###GC###   concept:", ct)
    print("###GC###   modelo :", mt)
    print("###GC### vazio  : erro medio = %.3f    (concept %.3f vs modelo %.3f)" % (
        e_vazio, sum(v for v in cv if v is not None) / len([v for v in cv if v is not None]),
        sum(v for v in mv if v is not None) / len([v for v in mv if v is not None])))
    if total_pares:
        print("###GC### contato: %d de %d pares FLUTUANDO" % (flut, total_pares))
    else:
        print("###GC### contato: nao medido (rode contato_v.py e passe o json)")
    print("###GC### SCORE = %.3f  (= perfil + vazio + %.2f*flutuantes)" % (score, PESO_CONTATO))
    return score


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a.endswith('.png') or a.endswith('.json') or a.endswith('.blend')]
    if not args:
        print("uso: --python gate_conjunto.py -- <render_SIDE.png> [contato.json]")
        sys.exit(1)
    main(args[0], args[1] if len(args) > 1 else None)

#!/usr/bin/env python3
"""Mask v2 do concept — corrige 2 defeitos medidos do mask antigo:
  (1) FRONT/REAR: cortava a BASE dos pneus (corte reto em vez de seguir a roda);
  (2) TOP: incluia uma LINHA DE COTA como "rabo" fantasma + respingos do grid.

Metodo: fundo = cinza claro de baixa saturacao (o grid). fg = resto. Depois:
  - maior componente conexa (o kart) via BFS com fila;
  - fecha buracos (olhos/face claros que ficam dentro);
  - REMENDO ESCURO: pixel escuro (max<118) a <=2 px da componente entra
    (recupera a base do pneu que o mask antigo amputava);
  - abertura para matar saliencias finas (regua/cota).

Sem scipy: morfologia e rotulagem em numpy puro.
Saida: /tmp/g2b_<view>.npy  + overlay /tmp/el/MASKV2-<view>.png
"""
import sys
from collections import deque
import numpy as np
from PIL import Image

D = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/"


def dil(m, it=1):
    for _ in range(it):
        o = m.copy()
        o[1:, :] |= m[:-1, :]; o[:-1, :] |= m[1:, :]
        o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]
        m = o
    return m


def ero(m, it=1):
    return ~dil(~m, it)


def label_sizes(m):
    """rotula 4-conectado por BFS; devolve (labels, n)."""
    H, W = m.shape
    lab = np.full(m.shape, -1, np.int32)
    idx = np.argwhere(m)
    n = 0
    for y0, x0 in idx:
        if lab[y0, x0] != -1:
            continue
        n += 1
        q = deque([(y0, x0)]); lab[y0, x0] = n
        while q:
            y, x = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and lab[yy, xx] == -1:
                    lab[yy, xx] = n; q.append((yy, xx))
    return lab, n


def outside(m):
    """fundo externo (BFS a partir da borda sobre ~m)."""
    H, W = m.shape
    inv = ~m
    seen = np.zeros(m.shape, bool)
    q = deque()
    for x in range(W):
        for y in (0, H - 1):
            if inv[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
    for y in range(H):
        for x in (0, W - 1):
            if inv[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and inv[yy, xx] and not seen[yy, xx]:
                seen[yy, xx] = True; q.append((yy, xx))
    return seen


def build(view, save=True):
    im = Image.open(D + view + ".jpg").convert("RGB")
    a = np.array(im).astype(np.int16)
    mx = a.max(2); mn = a.min(2); sat = mx - mn
    bg = (mn > 190) & (sat < 26)            # grid cinza claro
    fg = ~bg
    lab, n = label_sizes(fg)
    f = lab.ravel(); f = f[f >= 0]
    sizes = np.bincount(f); sizes[0] = 0
    kart = lab == int(np.argmax(sizes))
    # remendo escuro: pneu/base amputados pelo mask antigo
    for _ in range(3):
        add = dil(kart, 2) & (mx < 118)
        if not add.any():
            break
        kart |= add
    kart = kart | (fg & ~outside(kart))     # fecha buracos internos
    kart = ero(kart, 2)                     # mata reguas/cotas finas
    kart = dil(kart, 2)
    if not kart.any():
        raise SystemExit("mask vazia em " + view)
    ys, xs = np.where(kart)
    print("%s: v2 %dx%d area=%.1f%% bbox=%dx%d (y %d-%d x %d-%d)" % (
        view.upper(), a.shape[1], a.shape[0], 100.0 * kart.mean(),
        xs.max() - xs.min() + 1, ys.max() - ys.min() + 1, ys.min(), ys.max(), xs.min(), xs.max()))
    if save:
        np.save("/tmp/g2b_%s.npy" % view, kart)
        o = np.array(im).copy()
        b = np.zeros(kart.shape, bool)
        b[1:, :] |= kart[1:, :] & ~kart[:-1, :]
        b[:-1, :] |= kart[:-1, :] & ~kart[1:, :]
        b[:, 1:] |= kart[:, 1:] & ~kart[:, :-1]
        b[:, :-1] |= kart[:, :-1] & ~kart[:, 1:]
        o[dil(b, 1)] = (255, 0, 0)
        Image.fromarray(o).save("/tmp/el/MASKV2-%s.png" % view)
    return kart


if __name__ == "__main__":
    for v in (sys.argv[1:] or ["front", "rear", "side", "top"]):
        build(v)

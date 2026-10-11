#!/usr/bin/env python3
"""GATE QUANTITATIVO (plano Sol): contorno por faixa, modelo x concept, nas 4 vistas orto.

Reporta mediana, p95, MAXIMO e o LOCAL do pior erro, com EXCESSO e FALTA separados.
Nao usa VLM: e medicao. Uso: python3 gate_contorno.py <blend_ou_png> [--ver B0xx]
"""
import sys, os, json, subprocess
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
REF  = os.path.join(BASE, "..", "assets", "reference-orthographic")
N_EST = 100          # estacoes (o Sol pede >=100)

def mascara_concept(v):
    a = np.asarray(Image.open(os.path.join(REF, v + ".jpg")).convert("RGB")).astype(int)
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat, lum = mx - mn, a.mean(axis=2)
    m = ((sat > 26) & (lum < 250)) | (lum < 110)
    # LIMPEZA ROBUSTA: erosao 3x3 + FAIXA do veiculo (linhas/colunas com arte continua).
    # NAO usar "maior componente": no painel REAR a arte clara fragmenta o mask e o maior
    # pedaco e apenas as rodas/para-choque (foi a causa de um W/H=2,83 impossivel).
    r = m.copy()
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            r &= np.roll(np.roll(m, dy, 0), dx, 1)
    por_linha = r.sum(axis=1); por_col = r.sum(axis=0)
    lim_l = max(20, int(0.06 * por_linha.max()))
    lim_c = max(5,  int(0.03 * por_col.max()))
    linhas = por_linha > lim_l; colunas = por_col > lim_c
    # a maior faixa CONTIGUA de linhas (o veiculo) — evita pegar reguas soltas
    # MERGE de faixas separadas por VAZIOS PEQUENOS (a arte clara do painel REAR abre buracos
    # de ~20 linhas no mask; cortar ali perdia metade do veiculo)
    GAP = 40
    ini=None; faixas=[]
    for i,v in enumerate(linhas):
        if v and ini is None: ini=i
        elif not v and ini is not None: faixas.append([ini,i-1]); ini=None
    if ini is not None: faixas.append([ini,len(linhas)-1])
    juntos=[]
    for f in faixas:
        if juntos and f[0]-juntos[-1][1] <= GAP: juntos[-1][1]=f[1]
        else: juntos.append(f)
    melhor=max(juntos, key=lambda f: f[1]-f[0]) if juntos else (0,len(linhas)-1)
    y0,y1 = melhor[0], melhor[1]
    saida = np.zeros_like(r); saida[y0:y1+1, :] = r[y0:y1+1, :]
    # dentro da faixa, mantem so as colunas com arte (remove reguas verticais)
    cs = np.where(saida.sum(axis=0) > lim_c)[0]
    z = np.zeros_like(saida)
    if cs.size: z[:, cs.min():cs.max()+1] = saida[:, cs.min():cs.max()+1]
    return z

def mascara_modelo(png):
    a = np.asarray(Image.open(png).convert("RGBA"))
    return a[:,:,3] > 30

def perfil(m, vista):
    """Devolve (eixo, superior[], inferior[]) normalizado em 0..1 no eixo dominante."""
    ys, xs = np.where(m)
    if len(xs) < 50: return None
    if vista in ("side", "top"):      # eixo dominante = X da imagem
        eixo = xs; lo, hi = xs.min(), xs.max()
        sup, inf = [], []
        for k in range(N_EST):
            x = int(lo + (hi-lo)*k/(N_EST-1))
            col = np.where(m[:, x])[0]
            if len(col): sup.append(col.min()); inf.append(col.max())
            else: sup.append(np.nan); inf.append(np.nan)
    else:                              # FRONT/REAR: eixo dominante = Y da imagem (altura)
        eixo = ys; lo, hi = ys.min(), ys.max()
        sup, inf = [], []
        for k in range(N_EST):
            y = int(lo + (hi-lo)*k/(N_EST-1))
            row = np.where(m[y, :])[0]
            if len(row): sup.append(row.min()); inf.append(row.max())
            else: sup.append(np.nan); inf.append(np.nan)
    sup, inf = np.array(sup, float), np.array(inf, float)
    # NORMALIZA pelo EIXO DOMINANTE (estavel: o comprimento do veiculo), nao pela altura —
    # senao mexer na geometria desloca a escala e a metrica deixa de ser invariante.
    eixo_span = float(hi - lo)
    base = np.nanmin(sup)
    return (sup - base) / eixo_span, (inf - base) / eixo_span

def compara(vista, mc, mm):
    pc, pm = perfil(mc, vista), perfil(mm, vista)
    if pc is None or pm is None: return None
    erros_sup = pm[0] - pc[0]; erros_inf = pm[1] - pc[1]
    ambos = np.concatenate([np.abs(erros_sup), np.abs(erros_inf)])
    ambos = ambos[~np.isnan(ambos)]
    if len(ambos) == 0: return None
    # excesso = modelo MAIOR que o concept; falta = modelo MENOR (separados, como o Sol pede)
    exc_vals = np.concatenate([-erros_sup[erros_sup < -0.005], erros_inf[erros_inf > 0.005]])
    fal_vals = np.concatenate([ erros_sup[erros_sup >  0.005], -erros_inf[erros_inf < -0.005]])
    exc = float(np.mean(exc_vals)) if exc_vals.size else 0.0
    fal = float(np.mean(fal_vals)) if fal_vals.size else 0.0
    pior_k = int(np.nanargmax(np.abs(erros_sup) + np.abs(erros_inf)))
    return {"mediana_%": round(100*float(np.median(ambos)), 2),
            "p95_%": round(100*float(np.percentile(ambos, 95)), 2),
            "max_%": round(100*float(np.max(ambos)), 2),
            "pior_estacao": pior_k,
            "pior_pos_%": round(100*pior_k/(N_EST-1), 1),
            "excesso_%": round(100*float(exc), 2),
            "falta_%": round(100*float(fal), 2),
            "PASS_mediana": bool(np.median(ambos) <= 0.05),
            "PASS_p95": bool(np.percentile(ambos, 95) <= 0.10),
            "PASS_pior_faixa": bool(np.max(ambos) <= 0.12)}

def main():
    alvo = sys.argv[1]
    ver = sys.argv[3] if len(sys.argv) > 3 else "atual"
    pngs = {}
    for v in ("front","side","rear","top"):
        if alvo.endswith(".blend"):
            p = "/tmp/GATE_%s_%s.png" % (ver, v)
            if not os.path.exists(p): pngs[v] = None
            else: pngs[v] = p
        else:
            pngs[v] = alvo.replace("VISTA", v)
    res, falhas = {}, []
    for v in ("front","side","rear","top"):
        if not pngs[v]: continue
        r = compara(v, mascara_concept(v), mascara_modelo(pngs[v]))
        res[v] = r
        if r:
            st = "PASS" if (r["PASS_mediana"] and r["PASS_p95"] and r["PASS_pior_faixa"]) else "FALHA"
            if st == "FALHA": falhas.append("%s (pior faixa %.1f%% na estacao %.0f%% do comprimento)" % (v, r["max_%"], r["pior_pos_%"]))
            print("  %-6s mediana %5.2f%%  p95 %5.2f%%  MAX %5.2f%%  (pior em %4.1f%% do eixo)  excesso %s  falta %s  %s" % (
                v.upper(), r["mediana_%"], r["p95_%"], r["max_%"], r["pior_pos_%"], r["excesso_%"], r["falta_%"], st))
    json.dump(res, open(os.path.join(BASE, "gate_contorno.json"), "w"), indent=1)
    print("\n  VEREDITO: %s" % ("APROVADO" if not falhas else "REPROVADO em: " + " | ".join(falhas)))
    return res

if __name__ == "__main__":
    main()

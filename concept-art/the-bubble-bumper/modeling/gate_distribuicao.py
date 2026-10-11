#!/usr/bin/env python3
"""GATE DE DISTRIBUICAO (instrumento 39) — densidade por faixa, concept vs modelo.
O gate de contorno mede so a SILHUETA externa; este mede a DISTRIBUICAO de massa e vazios,
que e o defeito real do FRONT (modelo solido onde o concept tem vao entre rodas e corpo)."""
import sys, numpy as np
from PIL import Image
import importlib.util
spec=importlib.util.spec_from_file_location('g', __file__.replace('gate_distribuicao','gate_contorno'))
g=importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

def densidade(mask, n=20):
    """fracao preenchida por faixa do eixo, normalizada pela LARGURA da propria linha (0=linha vazia, 1=linha cheia)"""
    ys,xs=np.where(mask)
    if not len(ys): return np.zeros(n)
    to,bo=ys.min(),ys.max(); out=[]
    for k in range(n):
        y0=int(to+(bo-to)*k/n); y1=max(y0+1,int(to+(bo-to)*(k+1)/n))
        band=mask[y0:y1,:]
        if not band.any(): out.append(0.0); continue
        # densidade = px preenchidos / largura do bbox da faixa (mede se ha VAZIO dentro da silhueta)
        bx=np.where(band.any(axis=0))[0]
        largura=bx.max()-bx.min()+1
        out.append(band.sum()/(band.shape[0]*largura))
    return np.array(out)

def compara(vista, mc, mm, n=20):
    dc, dm = densidade(mc,n), densidade(mm,n)
    err=np.abs(dc-dm)*100
    return {"vista":vista, "concept":np.round(dc,3).tolist(), "modelo":np.round(dm,3).tolist(),
            "erro_pct":np.round(err,1).tolist(), "mediana":round(float(np.median(err)),2),
            "pior_faixa":int(np.argmax(err)), "pior_pct":round(float(err.max()),1)}

if __name__=="__main__":
    base=sys.argv[1]
    for vista in ("front","side","rear","top"):
        mc=g.mascara_concept(vista); mm=g.mascara_modelo(base.replace("VISTA",vista))
        r=compara(vista,mc,mm)
        print("%-6s mediana %.2f%%  pior faixa %d (%.1f%%)"%(r["vista"],r["mediana"],r["pior_faixa"]+1,r["pior_pct"]))
        print("       concept %s"%(" ".join("%.2f"%v for v in r["concept"])))
        print("       modelo  %s"%(" ".join("%.2f"%v for v in r["modelo"])))

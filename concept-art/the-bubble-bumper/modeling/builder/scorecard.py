
"""Scorecard de landmarks BB — metodo limpo (validado 2026-09-20).
REGRA: flood fill no mask RAW (mantem rodas conectadas) + filtro de RUN vertical >=8px por coluna
(mata linhas de cota/reua) + mediana movel de 5 colunas antes de qualquer gradiente.
NUNCA erodir antes do flood: remove as rodas (baixa saturacao) e estraga as normalizacoes z/H.
Uso: python3 scorecard.py <variante>   (ex: python3 scorecard.py w522)
"""
import sys, os, json
import numpy as np
from PIL import Image
from collections import deque

REF="/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/"
P="/opt/blender-runner/outputs/"
GATE_MED=0.025; GATE_P0=0.050; TOPO_TETO=0.40

def flood(mask,seed):
    vis=np.zeros_like(mask,dtype=bool); q=deque([seed]); vis[seed]=True
    while q:
        y,x=q.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<mask.shape[0] and 0<=nx<mask.shape[1] and mask[ny,nx] and not vis[ny,nx]:
                vis[ny,nx]=True; q.append((ny,nx))
    return vis

def centro(mask):
    ys,xs=np.where(mask)
    if len(ys)==0: return 0,0
    cy,cx=int(np.median(ys)),int(np.median(xs))
    if not mask[cy,cx]:
        d=np.hypot(ys-cy,xs-cx); cy,cx=int(ys[np.argmin(d)]),int(xs[np.argmin(d)])
    return cy,cx

def mask_concept(vista):
    c=np.array(Image.open(REF+vista+".jpg").convert("RGB")).astype(int)
    mx,mn=c.max(2),c.min(2)
    raw=((mx-mn)>45)|(mx<85)
    core=flood(raw,centro(raw))
    return core

def mask_modelo(v):
    a=np.array(Image.open(P+v+"m-side.png").convert("RGBA"))
    return a[:,:,3]>128

def top_rob(mask,runmin=8):
    ys,xs=np.where(mask); r0,r1,c0,c1=ys.min(),ys.max(),xs.min(),xs.max()
    A=mask[r0:r1+1,c0:c1+1]; Hh,Ww=A.shape
    t=np.full(Ww,np.nan)
    for i in range(Ww):
        col=A[:,i]; n=len(col); j=0
        while j<n:
            if col[j]:
                k=j
                while k<n and col[k]: k+=1
                if k-j>=runmin: break
                j=k
            else: j+=1
        if j<n: t[i]=(n-1)-j   # ALTURA ACIMA DA BASE DO CROP (nao distancia do topo)
    return t,Hh,Ww

def smooth(tv,k=5):
    ts=np.copy(tv); h=k//2
    for i in range(h,len(ts)-h): ts[i]=np.median(tv[i-h:i+h+1])
    return ts

def landmarks(mask,t,H,W):
    o={}; val=~np.isnan(t); idx=np.where(val)[0]
    b=max(2,int(W*0.05))
    L=[t[i] for i in idx[:b]]; R=[t[i] for i in idx[-b:]]
    o["L_topo_z"]=float(np.median(L))/H
    o["R_topo_z"]=float(np.median(R))/H
    o["topo_global_z"]=float(np.nanmax(t))/H
    o["topo_global_x"]=float(np.nanargmax(t))/W
    tv=t[val]; ts=smooth(tv,5); g=np.abs(np.diff(ts)); k=int(np.argmax(g))
    o["degrau_x"]=float(k)/W; o["degrau_amp"]=float(g[k])/H
    o["_degrau_flag"]="ARTEFATO" if o["degrau_amp"]>TOPO_TETO else "ok"
    # base das extremidades: por coluna, ultimo pixel com run>=8px
    ys,xs=np.where(mask); r0,r1,c0,c1=ys.min(),ys.max(),xs.min(),xs.max()
    A=mask[r0:r1+1,c0:c1+1]
    def base_col(i):
        col=A[:,i]; n=len(col); j=n-1
        while j>=0:
            if col[j]:
                k=j
                while k>=0 and col[k]: k-=1
                if j-k>=8: return r1-(r0+j)
                j=k
            else: j-=1
        return None
    Lb=[base_col(int(i)) for i in idx[:b] if base_col(int(i)) is not None]
    Rb=[base_col(int(i)) for i in idx[-b:] if base_col(int(i)) is not None]
    if Lb: o["L_base_z"]=float(np.median(Lb))/H
    if Rb: o["R_base_z"]=float(np.median(Rb))/H
    return o

def amarelo_frac(v, maskmod=None):
    if maskmod is None:
        c=np.array(Image.open(REF+"side.jpg").convert("RGB")).astype(int)
        m=mask_concept("side"); R,G,B=c[:,:,0],c[:,:,1],c[:,:,2]
    else:
        f=np.array(Image.open(P+v+"f-side.png").convert("RGB")).astype(int)
        m=maskmod; R,G,B=f[:,:,0],f[:,:,1],f[:,:,2]
    y=((R>150)&(G>130)&(B<110)&(R-B>60))&m
    return 100.0*y.sum()/m.sum()

def main():
    v=sys.argv[1]
    mc=mask_concept("side"); tc,Hc,Wc=top_rob(mc)
    mm=mask_modelo(v);      tm,Hm,Wm=top_rob(mm)
    # AUTO-TESTE DO INSTRUMENTO: o topo da silhueta TEM de dar ~1.0. Se nao der, o medidor esta errado.
    for nome,t,H in (("concept",tc,Hc),("modelo",tm,Hm)):
        tv=t[~np.isnan(t)]; pico=float(np.max(tv))/H
        if pico<0.99:
            print("ABORTADO: auto-teste do instrumento falhou em %s (pico=%.4f, esperado ~1.0)"%(nome,pico))
            sys.exit(2)
    C=landmarks(mc,tc,Hc,Wc); M=landmarks(mm,tm,Hm,Wm)
    C["pod_area_frac"]=amarelo_frac(None)/100.0
    M["pod_area_frac"]=amarelo_frac(v,mm)/100.0
    print("="*78)
    print("SCORECARD %s  (metodo limpo: flood raw + run>=8px + mediana5)"%v.upper())
    print("  concept W=%d H=%d | modelo W=%d H=%d"%(Wc,Hc,Wm,Hm))
    print("="*78)
    print("%-16s %9s %9s %9s  %s"%("landmark","concept","modelo","erro","gate"))
    erros=[]
    for k in sorted(set(C)&set(M)):
        if k.startswith("_"): continue
        e=abs(C[k]-M[k]); erros.append(e)
        g="OK" if e<=GATE_P0 else "FALHA P0"
        print("%-16s %9.4f %9.4f %9.4f  %s"%(k,C[k],M[k],e,g))
    med=float(np.median(erros)); pior=max(erros)
    print("-"*78)
    print("  mediana %.4f (gate <= %.3f) %s"%(med,GATE_MED,"OK" if med<=GATE_MED else "FALHA"))
    print("  pior    %.4f (gate <= %.3f) %s"%(pior,GATE_P0,"OK" if pior<=GATE_P0 else "FALHA"))
    print("  soma    %.4f"%sum(erros))
    print("  flag degrau: concept=%s modelo=%s"%(C.get("_degrau_flag"),M.get("_degrau_flag")))
    out={"variante":v,"concept":{k:C[k] for k in C if not k.startswith("_")},
         "modelo":{k:M[k] for k in M if not k.startswith("_")},"mediana":med,"pior":pior}
    json.dump(out,open(os.path.dirname(os.path.abspath(__file__))+"/../contracts/scorecard-"+v+".json","w"),indent=2)

if __name__=="__main__": main()

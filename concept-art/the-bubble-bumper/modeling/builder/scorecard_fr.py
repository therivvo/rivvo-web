
"""Scorecard FRONT/REAR v2 — com os 3 gates de instrumento e BUSCA DE EXTRACAO guiada pelo gate cross-view.
Gates: (a) perfil coerente  (b) W_max <= W_bbox  (c) W_bbox/H concorda com a W/H do SIDE (1.238) em <=0.05
Uso: python3 scorecard_fr.py <variante>
"""
import sys, os, json
import numpy as np
from PIL import Image
from collections import deque
REF="/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/assets/reference-orthographic/"
P="/opt/blender-runner/outputs/"
W_H_SIDE=1.238; TOL=0.050; GATE=0.050
def flood(mask,seed):
    vis=np.zeros_like(mask,dtype=bool); q=deque([seed]); vis[seed]=True
    while q:
        y,x=q.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<mask.shape[0] and 0<=nx<mask.shape[1] and mask[ny,nx] and not vis[ny,nx]:
                vis[ny,nx]=True; q.append((ny,nx))
    return vis
def centro(m):
    ys,xs=np.where(m)
    if len(ys)==0: return 0,0
    cy,cx=int(np.median(ys)),int(np.median(xs))
    if not m[cy,cx]:
        d=np.hypot(ys-cy,xs-cx); cy,cx=int(ys[np.argmin(d)]),int(xs[np.argmin(d)])
    return cy,cx
def erode(m,k=2):
    for _ in range(k):
        e=m.copy()
        for dy in(-1,0,1):
            for dx in(-1,0,1): e&=np.roll(np.roll(m,dy,0),dx,1)
        m=e
    return m
def candidatos(raw):
    out={}
    out["raw"]=raw
    out["flood_centro"]=flood(raw,centro(raw))
    e=erode(raw,1)
    if e.sum()>500:
        out["erode1"]=e; out["erode1+flood"]=flood(e,centro(e))
    e2=erode(raw,2)
    if e2.sum()>500: out["erode2+flood"]=flood(e2,centro(e2))
    return out
def bbox_wh(m):
    ys,xs=np.where(m)
    if len(ys)==0: return 0.0,0,0
    return (xs.max()-xs.min()+1)/(ys.max()-ys.min()+1), (ys.max()-ys.min()+1), (xs.max()-xs.min()+1)
def width_prof(mask,runmin=8):
    ys,xs=np.where(mask); r0,r1,c0,c1=ys.min(),ys.max(),xs.min(),xs.max()
    A=mask[r0:r1+1,c0:c1+1]; Hh,Ww=A.shape
    w=np.full(Hh,np.nan)
    for j in range(Hh):
        row=A[j]; n=len(row); i=0
        while i<n:
            if row[i]:
                k=i
                while k<n and row[k]: k+=1
                if k-i>=runmin: break
                i=k
            else: i+=1
        if i<n:
            i2=n-1
            while i2>=0:
                if row[i2]:
                    k2=i2
                    while k2>=0 and row[k2]: k2-=1
                    if i2-k2>=runmin: break
                    i2=k2
                else: i2-=1
            if i2>i: w[j]=i2-i
    return w,Hh,Ww
def escolhe(vista):
    c=np.array(Image.open(REF+vista+".jpg").convert("RGB")).astype(int)
    mx,mn=c.max(2),c.min(2); raw=((mx-mn)>45)|(mx<85)
    melhor=None
    print("  candidatos de extracao para %s:"%vista.upper())
    for nome,m in candidatos(raw).items():
        wh,H,W=bbox_wh(m)
        if H==0: continue
        w,Hh,Ww=width_prof(m)
        wmax=float(np.nanmax(w)) if not np.all(np.isnan(w)) else 0.0
        gate_b = wmax<=Ww+2          # (b) W_max <= W_bbox
        gate_c = abs(wh-W_H_SIDE)<=TOL  # (c) cross-view
        print("    %-14s W_bbox/H=%.4f | W_max/H=%.4f | (b)%s (c)%s"%(nome,wh,wmax/Hh,"OK" if gate_b else "FALHA","OK" if gate_c else "FALHA"))
        if gate_b and gate_c and melhor is None:
            melhor=(nome,m,wh,w,Hh,Ww); 
    return melhor
v=sys.argv[1]
res={}
for vista in ("front","rear"):
    print("="*76)
    esc=escolhe(vista)
    if esc is None:
        print("  %s: NENHUMA extracao passou os gates (b)+(c) => vista BLOQUEADA para comparacao"%vista.upper())
        res[vista]={"bloqueada":True}; continue
    nome,mc,whc,wc,Hc,Wc=esc
    print("  ACEITA: %s (W_bbox/H=%.4f, gate cross-view OK)"%(nome,whc))
    am=np.array(Image.open(P+v+"m-"+vista+".png").convert("RGBA"))[:,:,3]>128
    whm,Hm,Wm=bbox_wh(am); wm,Hhm,Wwm=width_prof(am)
    print("  modelo: W_bbox/H=%.4f (gate c: %s)"%(whm,"OK" if abs(whm-W_H_SIDE)<=TOL else "FALHA"))
    def lm(w,Hh,Ww):
        o={}; idx=np.where(~np.isnan(w))[0]
        if len(idx)==0: return o
        top,bot=idx[0],idx[-1]; rng=bot-top+1
        def band(lo,hi):
            s=[w[j] for j in idx if lo<=j<=hi and not np.isnan(w[j])]
            return float(np.median(s)) if s else 0.0
        o["W_topo"]=band(top,top+int(0.15*rng))/Hh
        o["W_base"]=band(bot-int(0.15*rng),bot)/Hh
        o["W_max"]=float(np.nanmax(w))/Hh
        o["W_max_z"]=float(np.nanargmax(w))/Hh
        return o
    C=lm(wc,Hc,Wc); M=lm(wm,Hhm,Wwm)
    print("  %-10s %9s %9s %9s  %s"%("landmark","concept","modelo","erro","gate"))
    for k in C:
        if k not in M: continue
        e=abs(C[k]-M[k]); print("  %-10s %9.4f %9.4f %9.4f  %s"%(k,C[k],M[k],e,"OK" if e<=GATE else "FALHA"))
    res[vista]={"extracao":nome,"concept":C,"modelo":M}
json.dump(res,open(os.path.dirname(os.path.abspath(__file__))+"/../contracts/scorecard-"+v+"-fr.json","w"),indent=2)

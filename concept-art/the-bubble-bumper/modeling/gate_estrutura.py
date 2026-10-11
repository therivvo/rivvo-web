#!/usr/bin/env python3
"""GATE ESTRUTURAL (instrumento 53) — o que o gate de contorno NAO ve.
Contorno mede a silhueta externa; este mede FORMA, CONTAGEM e CONEXAO por objeto.
Motivacao: o B072 passou nas 4 vistas de contorno (<=5%) e o vision deu 1,0/10
porque o bumper e um torus de 1,24 m que aparece como anel gigante no TOP."""
import bpy, mathutils, sys, math

L=2.35  # comprimento contratual
falhas=[]; avisos=[]

def bb(o):
    v=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    return (min(x.x for x in v),max(x.x for x in v),min(x.y for x in v),max(x.y for x in v),
            min(x.z for x in v),max(x.z for x in v))

objs=[o for o in bpy.data.objects if o.type=='MESH']
nomes={o.name for o in objs}

# 1) PRIMITIVAS ABSURDAS: torus com diametro > 40% do comprimento
for o in objs:
    x0,x1,y0,y1,z0,z1=bb(o)
    if o.name.startswith(("B_","R_Bumper","SP_")):
        d=max(x1-x0, y1-y0)
        if d > 0.40*L:
            (falhas if d>0.48*L else avisos).append("PRIMITIVA: %s com diametro %.2f m (%.0f%% de L) — torus/anel gigante"%(
                o.name,d,100*d/L))
# 2) FORMA POR CLASSE: nenhum objeto pode ser MAIS LARGO que COMPRIDO e MAIS ALTO que COMPRIDO (blob esferico)
for o in objs:
    x0,x1,y0,y1,z0,z1=bb(o)
    dx,dy,dz=x1-x0,y1-y0,z1-z0
    if dy>dx*1.35 and dy>0.45*L:
        falhas.append("FORMA: %s e mais LARGO (%.2f) que COMPRIDO (%.2f) — nao e um kart, e um blimp"%(o.name,dy,dx))
# 3) CONTAGEM de pecas assinatura
def conta(pref): return sorted(n for n in nomes if n.startswith(pref))
exaust=conta("R_Exh"); volante=conta("P_Wheel")+conta("SW")
if len(exaust)!=3: falhas.append("CONTAGEM: escapes = %d (%s) — o concept tem 3"%(len(exaust),exaust))
if not volante: falhas.append("CONTAGEM: sem volante (o concept tem volante)")
if not conta("P_Seat"): falhas.append("CONTAGEM: sem banco")
if len(conta("AX_"))<2: falhas.append("CONTAGEM: eixos = %d — o concept tem 2"%(len(conta("AX_"))))
roda=[n for n in nomes if n.startswith("W_")]
if len(roda)!=4: falhas.append("CONTAGEM: rodas = %d — deveriam ser 4"%(len(roda)))
# 4) FLUTUANTES: peca pequena cujo centro esta longe de tudo
centros=[]
for o in objs:
    x0,x1,y0,y1,z0,z1=bb(o); centros.append((o.name,(x0+x1)/2,(y0+y1)/2,(z0+z1)/2, max(x1-x0,y1-y0,z1-z0)))
for n,cx,cy,cz,dim in centros:
    if dim<0.30*L: continue
    perto=False
    for m2,ox,oy,oz,od in centros:
        if m2==n: continue
        if abs(ox-cx)<0.55*dim+0.10 and abs(oy-cy)<0.55*dim+0.10 and abs(oz-cz)<0.55*dim+0.10: perto=True; break
    if not perto: falhas.append("CONEXAO: %s (dim %.2f m) nao toca nenhuma outra peca — flutuante"%(n,dim))
# 5) RODA DIANTEIRA vs TRASEIRA (o concept tem traseira MAIOR)
wr=[o for o in objs if o.name.startswith("W_R")]; wf=[o for o in objs if o.name.startswith("W_F")]
if wr and wf:
    dr=max(bb(wr[0])[5]-bb(wr[0])[4], 0); df=max(bb(wf[0])[5]-bb(wf[0])[4], 0)
    if abs(dr-df)<0.02: avisos.append("RODAS: dianteira %.3f == traseira %.3f — o concept tem a TRASEIRA MAIOR"%(df,dr))

print("###GATE_ESTRUTURAL###")
print("  objetos: %d | falhas: %d | avisos: %d"%(len(objs),len(falhas),len(avisos)))
for f in falhas: print("   FALHA  | %s"%f)
for a in avisos: print("   AVISO  | %s"%a)
print("  VEREDITO: %s"%("REPROVADO" if falhas else "APROVADO"))

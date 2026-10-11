#!/usr/bin/env python3
"""Gate de DIRECIONALIDADE: IoU entre FRONT e REAR do modelo vs o concept.
Kart DIRECIONAL (bico em C na frente; motor/3 escapes/asa atras) tem IoU BAIXO.
IoU alto = modelo simetrico frente-tras = nao le como kart.
IMPORTA a mascara validada de gate_contorno.py (regra 104: nunca reimplementar instrumento validado).
Uso: python3 gate_direcionalidade.py /tmp/GG_B129_
"""
import sys, os, importlib.util, numpy as np
from PIL import Image
RAIZ="/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/"
REF=RAIZ+"assets/reference-orthographic/"
MD=RAIZ+"modeling/"
_spec=importlib.util.spec_from_file_location('gc', MD+"gate_contorno.py")
_gc=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_gc)
def carrega(p):
    a=np.asarray(Image.open(p).convert("RGBA")); return a[:,:,3]>0
def norm(m,h=400):
    ys,xs=np.where(m)
    if not len(ys): return np.zeros((h,h),bool)
    c=m[ys.min():ys.max()+1, xs.min():xs.max()+1]
    return np.asarray(Image.fromarray((c*255).astype(np.uint8)).resize((h,h))).astype(bool)
def iou(A,B): return (A&B).sum()/max(1,(A|B).sum())
if __name__=="__main__":
    pre=sys.argv[1] if len(sys.argv)>1 else "/tmp/GG_B129_"
    mf=norm(carrega(pre+"front.png")); mr=norm(carrega(pre+"rear.png"))
    cf=norm(_gc.mascara_concept("front")); cr=norm(_gc.mascara_concept("rear"))
    im_,ic=iou(mf,mr),iou(cf,cr)
    print("FRONT vs REAR — MODELO IoU %.3f | CONCEPT IoU %.3f"%(im_,ic))
    dif=im_-ic
    veredito="FALHA (modelo simetrico frente-tras)" if dif>0.15 else ("ALERTA" if dif>0.08 else "ok")
    print("  diferenca %+.3f  ->  %s"%(dif,veredito))
    sys.exit(1 if dif>0.15 else 0)

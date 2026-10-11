#!/usr/bin/env python3
"""GATE DE SANIDADE DE MALHA v2 (regras 164/168): area NAO basta — tri fino de 2 mm x 0,01 mm passa
no filtro de area e le como FIO. Medir tambem ASPECT RATIO das faces.
Uso: blender -b arquivo.blend --python gate_sanidade.py -- NOME_OBJETO
"""
import bpy, bmesh, sys
args=[a for a in sys.argv if not a.startswith("-") and a.endswith((".blend",)) is False]
NOME = sys.argv[-1] if len(sys.argv)>1 and sys.argv[-1].startswith("T") else "TubCockpit"
o = bpy.data.objects.get(NOME) or bpy.data.objects.get("TubCockpit")
if not o: print("###SANIDADE### objeto AUSENTE"); sys.exit(1)
# REGRA 170: medir o objeto AVALIADO (o que o render mostra), nao o cage
dg=bpy.context.evaluated_depsgraph_get()
ev=o.evaluated_get(dg)
bm=bmesh.new(); bm.from_mesh(ev.to_mesh())
print("###SANIDADE### (medindo o AVALIADO: cage=%d verts -> avaliado=%d verts)"%(len(o.data.vertices),len(ev.to_mesh().vertices)))
bound=sum(1 for e in bm.edges if len(e.link_faces)==1)
nonman=sum(1 for e in bm.edges if len(e.link_faces)>2)
arestas=[e.calc_length() for e in bm.edges]
mediana=sorted(arestas)[len(arestas)//2] if arestas else 1.0
zero=[f for f in bm.faces if f.calc_area()<1e-9]
qzero=[f for f in bm.faces if f.calc_area()<1e-7]
fios=[f for f in bm.faces if min(e.calc_length() for e in f.edges) < 0.15*max(e.calc_length() for e in f.edges)]
doubles=len(bmesh.ops.find_doubles(bm, verts=bm.verts[:], dist=0.003).get("targetmap",{}))
tris=sum(1 for f in bm.faces if len(f.verts)==3); ngons=sum(1 for f in bm.faces if len(f.verts)>4)
print("###SANIDADE### %s"%NOME)
print("  verts=%d faces=%d quads=%d tris=%d ngons=%d  aresta_mediana=%.4f m"%(len(bm.verts),len(bm.faces),len(bm.faces)-tris-ngons,tris,ngons,mediana))
print("  boundary=%d NON-MANIFOLD=%d ZERO-AREA=%d quase-zero=%d doubles=%d"%(
      bound,nonman,len(zero),len(qzero),doubles))
print("  FACES-FIO (aspect extremo: menor/maior aresta < 0,15)=%d"%len(fios))
falhas=[]
if bound: falhas.append("boundary=%d"%bound)
if nonman: falhas.append("non-manifold=%d"%nonman)
if len(zero): falhas.append("zero-area=%d"%len(zero))
if doubles: falhas.append("doubles=%d"%doubles)
if len(fios): falhas.append("faces-fio=%d"%len(fios))
print("###SANIDADE### %s"%("LIMPO OK" if not falhas else "FALHA: "+", ".join(falhas)))
bm.free(); sys.exit(0 if not falhas else 1)

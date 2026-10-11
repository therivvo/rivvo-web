import bpy, math, json
L,H,W = 2.35,1.2523,1.4411
PIL = 0.8703          # ocupacao alvo do piloto (69,5% de H) — valor REEMITIDO da fonte
D=0.703; R=D/2.0
track=0.800*W/2.0; wf,wr=0.4825,-0.6900
def cy(n,x,y,r,d,rot):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=32, location=(x,y,cy_z), rotation=rot)
    bpy.context.object.name=n; return bpy.context.object
# rodas B002
for n,x,y in (("W_FL",wf,track),("W_FR",wf,-track),("W_RL",wr,track),("W_RR",wr,-track)):
    cy_z=R
    cy(n,x,y,R,0.215,(math.radians(90),0,0))
# B003: cages do piloto — cabeca (elipsoide), torso (caixa arredondada), tub
ZTOP=H
ZPIL0=ZTOP-PIL
def esfera(n,loc,rx,ry,rz):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=loc)
    o=bpy.context.object; o.name=n; o.scale=(rx,ry,rz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
# cabeca: chibi -> grande. centro a 0.72 de PIL acima da base do piloto
hc=ZPIL0+PIL*0.72
esfera("P_Head",(-0.16,0,hc), 0.225, 0.225, 0.245)
# torso
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.16,0,ZPIL0+PIL*0.28))
t=bpy.context.object; t.name="P_Torso"; t.scale=(0.20,0.20,PIL*0.30/2)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
# tub (banheira)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15,0,0.28))
b=bpy.context.object; b.name="E_Tub"; b.scale=(L*0.32/2, W*0.44/2, 0.28)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B003_pilot.blend')
print('###B003###', json.dumps({"PIL":PIL,"ZPIL0":ZPIL0,"head_z":hc,"H":H,"frac":PIL/H}))

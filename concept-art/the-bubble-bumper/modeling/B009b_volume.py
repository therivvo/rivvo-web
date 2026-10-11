import bpy, math, json
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
def box(n,x0,x1,y0,y1,z0,z1,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2), rotation=rot)
    o=bpy.context.object; o.name=n; o.scale=(abs(x1-x0),abs(y1-y0),abs(z1-z0))
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
def cil(n,x,y,z,r,d,rot=(math.radians(90),0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=d,vertices=32,location=(x,y,z),rotation=rot)
    o=bpy.context.object; o.name=n; return o
def esf(n,loc,rx,ry,rz):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0,location=loc); o=bpy.context.object; o.name=n
    o.scale=(rx,ry,rz); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
# RODAS: cilindros deitados COM LARGURA e eixo. Bitola ABERTA o bastante para a roda passar do sidepod.
DF,DR,WDF,WDR = 0.440,0.580,0.240,0.320
TF,TR = 0.78,0.96
xf,xr = 0.70,-0.60
cil("W_FL",xf, TF/2,DF/2,DF/2,WDF); cil("W_FR",xf,-TF/2,DF/2,DF/2,WDF)
cil("W_RL",xr, TR/2,DR/2,DR/2,WDR); cil("W_RR",xr,-TR/2,DR/2,DR/2,WDR)
# ASSOALHO ESCURO rebaixado (forja o sombreado de cavidade)
box("C_Floor", -0.80,0.60, -0.24,0.24, 0.13,0.25)
# SIDEPODS com PAREDE VERTICAL INTERNA (face em y=+-0.24) e altura real ate 0.62
box("SP_L", -0.64,0.36,  0.24,0.56, 0.15,0.62)
box("SP_R", -0.64,0.36, -0.56,-0.24, 0.15,0.62)
# BICO AFUNILADO descendo (3 degraus) + traseira alta
box("C_NoseA", 0.60,0.80, -0.18,0.18, 0.13,0.34)
box("C_NoseB", 0.80,0.95, -0.14,0.14, 0.13,0.26)
box("C_NoseC", 0.95,1.05, -0.10,0.10, 0.13,0.20)
box("C_Rear", -0.98,-0.64, -0.34,0.34, 0.13,0.68)
# PARA-CHOQUE EM C COMO TUBO (cilindros com espessura, visivel em todas as vistas)
cil("B_Top", 1.02,0,0.44, 0.075,1.20, rot=(math.radians(90),0,0))
cil("B_ArmL",0.86, 0.56,0.30, 0.075,0.42, rot=(0,math.radians(90),0))
cil("B_ArmR",0.86,-0.56,0.30, 0.075,0.42, rot=(0,math.radians(90),0))
# PILOTO: perna FORA do tijolo (coxa + canela separadas), capacete 18 cm mais BAIXO, tronco reclinado
box("P_Hips", -0.52,-0.20, -0.20,0.20, 0.25,0.47)
box("P_Thigh",-0.22,0.32, -0.17,0.17, 0.27,0.45)
box("P_Shin",  0.26,0.38, -0.14,0.14, 0.13,0.40, rot=(0,math.radians(48),0))
box("P_Torso",-0.66,-0.42, -0.18,0.18, 0.40,0.72, rot=(0,math.radians(-40),0))
esf("P_Head", (-0.42,0,0.80), 0.215,0.215,0.215)
box("P_Seat", -0.88,-0.74, -0.22,0.22, 0.25,0.78)
cil("P_Wheel", 0.10,0,0.48, 0.125,0.05, rot=(0,math.radians(62),0))
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B009b.blend')
print('###B009### ok')

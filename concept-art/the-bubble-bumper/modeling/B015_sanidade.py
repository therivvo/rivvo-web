import bpy, math, json
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
def box(n,x0,x1,y0,y1,z0,z1,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2), rotation=rot)
    o=bpy.context.object; o.name=n; o.scale=(abs(x1-x0),abs(y1-y0),abs(z1-z0))
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
def cil(n,x,y,z,r,d,rot=(math.radians(90),0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=d,vertices=24,location=(x,y,z),rotation=rot)
    o=bpy.context.object; o.name=n; return o
def toro(n,loc,R,r,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=28, minor_segments=10, location=loc, rotation=rot)
    o=bpy.context.object; o.name=n; return o
def esf(n,loc,rx,ry,rz):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0,location=loc); o=bpy.context.object; o.name=n
    o.scale=(rx,ry,rz); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
def cap(n,x0,x1,y0,y1,z0,z1):
    # capsula = cilindro + 2 meias esferas (tronco/braco com ponta arredondada)
    cx,cy,cz=(x0+x1)/2,(y0+y1)/2,(z0+z1)/2
    cil(n,cx,cy,cz,(y1-y0)/2, abs(x1-x0), rot=(0,math.radians(90),0))
    esf(n+"_a",(x0,cy,cz),(x1-x0)*0.0+ (y1-y0)/2,(y1-y0)/2,(y1-y0)/2)
    esf(n+"_b",(x1,cy,cz),(y1-y0)/2,(y1-y0)/2,(y1-y0)/2)
    return bpy.data.objects[n]
# RODAS
DF,DR,WDF,WDR=0.407,0.407,0.150,0.210; TF,TR=0.86,1.06; xf,xr=0.72,-0.65
cil("W_FL",xf, TF/2,DF/2,DF/2,WDF); cil("W_FR",xf,-TF/2,DF/2,DF/2,WDF)
cil("W_RL",xr, TR/2,DR/2,DR/2,WDR); cil("W_RR",xr,-TR/2,DR/2,DR/2,WDR)
# ASSOALHO ESCURO estreito
box("C_Floor",-0.86,0.62, -0.26,0.26, 0.24,0.32)
# SIDEPODS: parte dianteira BAIXA (pernas) + parte traseira ALTA (flanqueia o piloto) — o corte do gate
box("SP_Lf", 0.06,0.42,  0.26,0.52, 0.20,0.32)
box("SP_Rf", 0.06,0.42, -0.52,-0.26, 0.20,0.32)
box("SP_Lr",-0.66,0.06,  0.26,0.56, 0.20,0.54)
box("SP_Rr",-0.66,0.06, -0.56,-0.26, 0.20,0.54)
# BICO em 3 degraus descendo
box("C_NoseA",0.62,0.82, -0.18,0.18, 0.13,0.33)
box("C_NoseB",0.82,0.96, -0.13,0.13, 0.13,0.25)
box("C_NoseC",0.96,1.06, -0.09,0.09, 0.13,0.19)
# PARA-CHOQUE em C (tubo) — 3 cilindros
cil("B_Top",1.03,0,0.34,0.040,1.18)
cil("B_ArmL",0.86, 0.56,0.24,0.040,0.40,(0,math.radians(90),0))
cil("B_ArmR",0.86,-0.56,0.24,0.040,0.40,(0,math.radians(90),0))
# PILOTO: tronco capsula inclinada + 2 bracos + volante toroide + coxa/canela/bota por lado + capacete c/ viseira
box("P_Torso",-0.70,-0.44, -0.19,0.19, 0.40,0.74, rot=(0,math.radians(-38),0))
cil("P_ArmL",-0.24, 0.20,0.50, 0.055,0.52, rot=(0,math.radians(80),0))
cil("P_ArmR",-0.24,-0.20,0.50, 0.055,0.52, rot=(0,math.radians(80),0))
toro("P_Wheel",(0.02,0,0.50),0.125,0.030, rot=(0,math.radians(72),0))
cil("P_Col",0.20,0,0.36,0.030,0.44, rot=(0,math.radians(62),0))
for sy,sn in ((1,"L"),(-1,"R")):
    box("P_Thigh"+sn,-0.20,0.36, sy*0.11-0.09, sy*0.11+0.09, 0.26,0.40)
    box("P_Shin"+sn, 0.26,0.38, sy*0.10-0.07, sy*0.10+0.07, 0.13,0.38, rot=(0,math.radians(48),0))
    box("P_Boot"+sn, 0.40,0.54, sy*0.11-0.09, sy*0.11+0.09, 0.13,0.23)
box("P_Hips",-0.52,-0.20, -0.21,0.21, 0.24,0.46)
esf("P_Head",(-0.48,0,0.72),0.150,0.150,0.150)
box("P_Visor",-0.630,-0.575, -0.140,0.140, 0.690,0.800)
box("P_Seat",-0.90,-0.76, -0.23,0.23, 0.24,0.76, rot=(0,math.radians(-22),0))
# TRASEIRA: motor + 3 escapes + eixo + para-choque em U vazado
box("R_Motor",-1.02,-0.72, -0.26,0.26, 0.14,0.42)
cil("R_Exh1",-1.10,0,0.40,0.080,0.22,(0,math.radians(90),0)); cil("R_Exh2",-1.10,0.20,0.40,0.080,0.22,(0,math.radians(90),0)); cil("R_Exh3",-1.10,-0.20,0.40,0.080,0.22,(0,math.radians(90),0))
cil("R_Axle",-0.65,0,DR/2,0.045,1.08,(0,math.radians(90),0))
cil("R_BTop",-1.14,0,0.26,0.038,1.00)
cil("R_BArmL",-0.98, 0.46,0.20,0.038,0.30,(0,math.radians(90),0))
cil("R_BArmR",-0.98,-0.46,0.20,0.038,0.30,(0,math.radians(90),0))
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B015.blend')
print('###B010### ok')

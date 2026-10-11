import bpy, math, json
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
def box(n,x0,x1,y0,y1,z0,z1,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2), rotation=rot)
    o=bpy.context.object; o.name=n; o.scale=(abs(x1-x0),abs(y1-y0),abs(z1-z0))
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
def cil(n,x,y,z,r,d,rot=(math.radians(90),0,0),v=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=d,vertices=v,location=(x,y,z),rotation=rot)
    o=bpy.context.object; o.name=n; return o
def esf(n,loc,rx,ry,rz,seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0,segments=seg,ring_count=seg//2,location=loc)
    o=bpy.context.object; o.name=n; o.scale=(rx,ry,rz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
def capsula(n,x0,x1,y,z,r,rot=(0,0,0)):
    # capsula orientada em X: cilindro + 2 hemisferios nas pontas
    L=abs(x1-x0); cx=(x0+x1)/2
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=max(L-2*r,0.001), vertices=20, location=(cx,y,z), rotation=(0,math.radians(90),0))
    o=bpy.context.object; o.name=n
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=20, ring_count=10, location=(cx+L/2-r,y,z))
    bpy.context.object.name=n+"_t"
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=20, ring_count=10, location=(cx-L/2+r,y,z))
    bpy.context.object.name=n+"_b"
    for m in (n,n+"_t",n+"_b"):
        for p in bpy.data.objects[m].data.polygons: p.use_smooth=True
    bpy.ops.object.select_all(action='DESELECT')
    for m in (n,n+"_t",n+"_b"): bpy.data.objects[m].select_set(True)
    bpy.context.view_layer.objects.active=bpy.data.objects[n]; bpy.ops.object.join()
    ob=bpy.data.objects[n]
    ob.rotation_euler=rot
    bpy.context.view_layer.objects.active=ob; bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
    return ob
def suave(n, lv=2):
    o=bpy.data.objects[n]
    if lv==0:                                  # CILINDROS: so shade smooth (SubD colapsa para lente)
        for p in o.data.polygons: p.use_smooth=True
        return o
    m=o.modifiers.new('sub','SUBSURF'); m.levels=lv; m.render_levels=lv
    bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier='sub')
    for p in o.data.polygons: p.use_smooth=True
    return o
# ===== RODAS (medidas: diametro igual 0.407, larguras 0.15/0.21, bitolas 0.86/1.06) =====
D=0.53; R=D/2
cil("W_FL",0.72, 0.52,R*0.82,R*0.82,0.150); cil("W_FR",0.72,-0.52,R*0.82,R*0.82,0.150)
cil("HUB_FL",0.72, 0.525,R,R*0.40,0.07); cil("HUB_FR",0.72,-0.525,R,R*0.40,0.07)
cil("AX_F",0.72,0,R/2,0.032,0.72,(0,math.radians(90),0)); suave("AX_F",0)
cil("W_RL",-0.65,0.58,R*1.05,R*1.05,0.220); cil("W_RR",-0.65,-0.58,R*1.05,R*1.05,0.220)
cil("HUB_RL",-0.65,0.555,R,R*0.40,0.07); cil("HUB_RR",-0.65,-0.555,R,R*0.40,0.07)
cil("AX_R",-0.65,0,R/2,0.032,0.94,(0,math.radians(90),0)); suave("AX_R",0)
for n in ("W_FL","W_FR","W_RL","W_RR"): suave(n,1)
# ===== BICO: ELIPSOIDE AFUNILADO (curvo, nao escada) =====
box("C_Nose",0.34,0.86, -0.19,0.19, 0.22,0.52); suave("C_Nose",2); suave("C_Nose",2)
# ===== CHASSI: PERFIL CURVO (cilindro achatado de secao eliptica ao longo de X) =====
cil("C_Spine",-0.10,0,0.30,0.16,1.80,(0,math.radians(90),0)); suave("C_Spine",1)
bpy.data.objects["C_Spine"].scale=(1.0,1.0,0.55)
bpy.context.view_layer.objects.active=bpy.data.objects["C_Spine"]
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
# ===== SIDEPODS EM GOTA (esfera alongada + afinamento) =====
for sy,sn in ((1,"L"),(-1,"R")):
    y0,y1=sorted((sy*0.34, sy*0.60))
    box("SP_"+sn, -0.86, 0.20, y0,y1, 0.15,0.44); suave("SP_"+sn,1)
# ===== BUMPER DIANTEIRO: TORO EM C CONTINUO (corta a metade traseira com boolean) =====
bpy.ops.mesh.primitive_torus_add(major_radius=0.34, minor_radius=0.075, major_segments=40, minor_segments=14,
                                 location=(0.58,0,0.50))
tb=bpy.context.object; tb.name="B_Front"
box("B_Cut",-0.20,0.60, -0.60,0.60, -0.40,0.40)     # deixa so o arco da frente (+x)
m=tb.modifiers.new('cut','BOOLEAN'); m.operation='DIFFERENCE'; m.object=bpy.data.objects['B_Cut']; m.solver='EXACT'
bpy.context.view_layer.objects.active=tb; bpy.ops.object.modifier_apply(modifier='cut')
bpy.data.objects.remove(bpy.data.objects['B_Cut'], do_unlink=True)
suave("B_Front",1)
# ===== TRASEIRA: bumper em C + 2 escapes finos inclinados + motor =====
bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.085, major_segments=36, minor_segments=12,
                                 location=(-0.66,0,0.26))
tr=bpy.context.object; tr.name="R_Bumper"
box("R_Cut",-1.40,-0.86, -0.60,0.60, -0.40,0.40)
m=tr.modifiers.new('cut','BOOLEAN'); m.operation='DIFFERENCE'; m.object=bpy.data.objects['R_Cut']; m.solver='EXACT'
bpy.context.view_layer.objects.active=tr; bpy.ops.object.modifier_apply(modifier='cut')
bpy.data.objects.remove(bpy.data.objects['R_Cut'], do_unlink=True); suave("R_Bumper",1)
esf("R_MotorBlock",(-0.88,0,0.40),0.26,0.20,0.15); suave("R_MotorBlock",1)
# CARENAGEM TRASEIRA: fornece a largura da cauda (estacao 88-96%%) SEM alongar o veiculo
# TRASEIRA EM 3 VOLUMES SEPARADOS COM VAO REAL (vision: deletar e reconstruir)
for sf in (1,-1):
    y0,y1=sorted((sf*0.36, sf*0.68))
    box("R_Pod"+("L" if sf>0 else "R"), -1.12,-0.66, y0,y1, 0.20,0.52); suave("R_Pod"+("L" if sf>0 else "R"),1)
box("R_Motor",-1.02,-0.74, -0.22,0.22, 0.22,0.50); suave("R_Motor",1)   # bloco central, com AR ate os pods; suave("R_Fairing",1)
cil("R_ExhL",-1.04, 0.15,0.46,0.070,0.30,(0,math.radians(72),0)); cil("R_ExhR",-1.04,-0.15,0.46,0.070,0.30,(0,math.radians(72),0))
cil("HOLE_L",-1.08, 0.13,0.44,0.040,0.14,(0,math.radians(72),0)); cil("HOLE_R",-1.08,-0.13,0.44,0.040,0.14,(0,math.radians(72),0))
cil("R_ExhC",-1.10,0,0.52,0.088,0.38,(0,math.radians(72),0)); suave("R_ExhC",1)
for sf in (1,-1): cil("R_ExhT"+("L" if sf>0 else "R"),-1.12,sf*0.20,0.48,0.070,0.34,(0,math.radians(72),0))
box("P_Seat",-0.56,-0.40, -0.20,0.20, 0.33,0.64, rot=(0,math.radians(-18),0))
box("R_Wing",-1.20,-1.06, -0.52,0.52, 0.60,0.68); suave("R_Wing",2)
for sf in (1,-1): box("R_WingSup"+("L" if sf>0 else "R"),-1.15,-1.10, sf*0.14,sf*0.20, 0.44,0.62)

cil("R_HoleC",-1.08,0,0.48,0.042,0.10,(0,math.radians(72),0))
# ===== CHASSI TUBULAR: liga tudo (vision: "tudo flutua, falta chassi") =====
for sf in (1,-1):
    box("C_Rail"+("L" if sf>0 else "R"), -1.10,0.92, sf*0.16,sf*0.26, 0.12,0.22); suave("C_Rail"+("L" if sf>0 else "R"),1)
for cx,nm in ((0.86,"F"),(0.10,"M"),(-0.72,"R")):
    box("C_Cross"+nm, cx-0.06,cx+0.06, -0.26,0.26, 0.12,0.20); suave("C_Cross"+nm,1)
# ===== PILOTO ARTICULADO COM PESCOCO =====
box("P_Hips",-0.24,0.04, -0.19,0.19, 0.24,0.44, rot=(0,math.radians(-8),0)); suave("P_Hips",1)
box("P_Torso",-0.40,-0.10, -0.26,0.26, 0.34,0.94, rot=(0,math.radians(-14),0))
box("P_Shoulder",-0.48,-0.26, -0.32,0.32, 0.76,0.94); suave("P_Torso",1)
cil("P_Neck",-0.24,0,0.92,0.105,0.20,(0,0,math.radians(90))); suave("P_Neck",1)
esf("P_Head",(-0.24,0,1.10),0.200,0.200,0.152)
# FAIXA AMARELA CENTRAL DO CAPACETE (vision: "faixa central longitudinal amarela de frente para tras")
box("P_Stripe",-0.44,-0.04, -0.055,0.055, 1.10,1.253)
for sy,sn in ((1,"L"),(-1,"R")):
    cil("P_Thigh"+sn,-0.02, sy*0.11,0.36,0.078,0.64,(0,math.radians(90),0)); suave("P_Thigh"+sn,1)
    cil("P_Shin"+sn, 0.42, sy*0.11,0.26,0.062,0.40,(0,math.radians(42),0)); suave("P_Shin"+sn,1)
    esf("P_Boot"+sn,(0.58, sy*0.11, 0.16),0.085,0.075,0.055); suave("P_Boot"+sn,1)
    cil("P_Arm"+sn, -0.22, sy*0.19,0.52,0.048,0.46,(0,math.radians(78),0)); suave("P_Arm"+sn,1)
bpy.ops.mesh.primitive_torus_add(major_radius=0.082, minor_radius=0.020, major_segments=28, minor_segments=10,
                                 location=(0.04,0,0.44), rotation=(0,math.radians(58),0))
bpy.context.object.name="P_Wheel"; suave("P_Wheel",1)
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B114.blend')
print('###B017### ok')

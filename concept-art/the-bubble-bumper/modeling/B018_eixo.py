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
def suave(n, lv=2):
    o=bpy.data.objects[n]
    m=o.modifiers.new('sub','SUBSURF'); m.levels=lv; m.render_levels=lv
    bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier='sub')
    for p in o.data.polygons: p.use_smooth=True
    return o
# ===== RODAS (medidas: diametro igual 0.407, larguras 0.15/0.21, bitolas 0.86/1.06) =====
D=0.407; R=D/2
cil("W_FL",0.72, 0.43,R,R,0.150); cil("W_FR",0.72,-0.43,R,R,0.150)
cil("W_RL",-0.65,0.53,R,R,0.210); cil("W_RR",-0.65,-0.53,R,R,0.210)
for n in ("W_FL","W_FR","W_RL","W_RR"): suave(n,1)
# ===== BICO: ELIPSOIDE AFUNILADO (curvo, nao escada) =====
esf("C_Nose",(0.86,0,0.28),0.34,0.22,0.15); suave("C_Nose",2)
# ===== CHASSI: PERFIL CURVO (cilindro achatado de secao eliptica ao longo de X) =====
cil("C_Spine",-0.10,0,0.30,0.16,1.80,(0,math.radians(90),0)); suave("C_Spine",1)
bpy.data.objects["C_Spine"].scale=(1.0,1.0,0.55)
bpy.context.view_layer.objects.active=bpy.data.objects["C_Spine"]
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
# ===== SIDEPODS EM GOTA (esfera alongada + afinamento) =====
for sy,sn in ((1,"L"),(-1,"R")):
    esf("SP_"+sn,(-0.22, sy*0.40, 0.34), 0.52,0.15,0.14); suave("SP_"+sn,2)
# ===== BUMPER DIANTEIRO: TORO EM C CONTINUO (corta a metade traseira com boolean) =====
bpy.ops.mesh.primitive_torus_add(major_radius=0.52, minor_radius=0.062, major_segments=40, minor_segments=14,
                                 location=(0.84,0,0.24))
tb=bpy.context.object; tb.name="B_Front"
box("B_Cut",-0.20,0.60, -0.60,0.60, -0.40,0.40)     # deixa so o arco da frente (+x)
m=tb.modifiers.new('cut','BOOLEAN'); m.operation='DIFFERENCE'; m.object=bpy.data.objects['B_Cut']; m.solver='EXACT'
bpy.context.view_layer.objects.active=tb; bpy.ops.object.modifier_apply(modifier='cut')
bpy.data.objects.remove(bpy.data.objects['B_Cut'], do_unlink=True)
suave("B_Front",1)
# ===== TRASEIRA: bumper em C + 2 escapes finos inclinados + motor =====
bpy.ops.mesh.primitive_torus_add(major_radius=0.50, minor_radius=0.055, major_segments=36, minor_segments=12,
                                 location=(-1.00,0,0.22))
tr=bpy.context.object; tr.name="R_Bumper"
box("R_Cut",-1.40,-0.86, -0.60,0.60, -0.40,0.40)
m=tr.modifiers.new('cut','BOOLEAN'); m.operation='DIFFERENCE'; m.object=bpy.data.objects['R_Cut']; m.solver='EXACT'
bpy.context.view_layer.objects.active=tr; bpy.ops.object.modifier_apply(modifier='cut')
bpy.data.objects.remove(bpy.data.objects['R_Cut'], do_unlink=True); suave("R_Bumper",1)
esf("R_Motor",(-0.86,0,0.34),0.22,0.20,0.16); suave("R_Motor",2)
cil("R_ExhL",-1.00, 0.13,0.44,0.048,0.26,(0,math.radians(72),0)); cil("R_ExhR",-1.00,-0.13,0.44,0.048,0.26,(0,math.radians(72),0))
# ===== PILOTO ARTICULADO COM PESCOCO =====
box("P_Hips",-0.50,-0.22, -0.19,0.19, 0.26,0.46, rot=(0,math.radians(-8),0)); suave("P_Hips",1)
box("P_Torso",-0.64,-0.44, -0.17,0.17, 0.44,0.72, rot=(0,math.radians(-42),0)); suave("P_Torso",1)
cil("P_Neck",-0.58,0,0.72,0.080,0.18,(0,0,0)); suave("P_Neck",1)
esf("P_Head",(-0.58,0,0.80),0.150,0.150,0.150); suave("P_Head",1)
for sy,sn in ((1,"L"),(-1,"R")):
    cil("P_Thigh"+sn,-0.02, sy*0.11,0.34,0.075,0.62,(0,math.radians(90),0)); suave("P_Thigh"+sn,1)
    cil("P_Shin"+sn, 0.36, sy*0.11,0.20,0.062,0.36,(0,0,0)); suave("P_Shin"+sn,1)
    cil("P_Arm"+sn, -0.22, sy*0.19,0.52,0.048,0.46,(0,math.radians(78),0)); suave("P_Arm"+sn,1)
bpy.ops.mesh.primitive_torus_add(major_radius=0.115, minor_radius=0.024, major_segments=28, minor_segments=10,
                                 location=(0.06,0,0.52), rotation=(0,math.radians(70),0))
bpy.context.object.name="P_Wheel"; suave("P_Wheel",1)
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B018.blend')
print('###B017### ok')

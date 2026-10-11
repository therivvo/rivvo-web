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


def pod_unico(n, x0,x1, y0,y1, z0,z1, taper=0.34, borda=0.085, topo_z=None):
    """POD do concept (receita do vision): UMA caixa, TAPER PROGRESSIVO na frente,
    INSET no topo -> azul PLANO afundado + BORDA AMARELA ESPESSA em U.
    Sem capsula. Sem peca sobreposta."""
    import bmesh
    me=bpy.data.meshes.new(n); ob=bpy.data.objects.new(n, me)
    bpy.context.collection.objects.link(ob)
    bm=bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    L=x1-x0
    for v in bm.verts:
        fx = (v.co.x+0.5)               # 0..1 do comprimento
        # TAPER PROGRESSIVO: a frente afina em largura E altura, suave (quadratico)
        t = taper*(fx**2)
        v.co.x = x0 + fx*L
        v.co.y = (y0 if v.co.y<0 else y1) * (1.0-0.42*t)
        v.co.z = (z0 if v.co.z<0 else z1)
        if v.co.z > (z0+z1)/2:          # topo desce na frente (taper)
            v.co.z = z1 - (z1-z0)*0.30*t
    # INSET no topo -> face interna (azul) + anel externo (amarelo/borda)
    tops=[f for f in bm.faces if f.normal.z>0.6]
    res=bmesh.ops.inset_individual(bm, faces=tops, thickness=borda, depth=0.010)
    bm.to_mesh(me); bm.free()
    # materiais: face interna azul, anel amarelo
    bm2=bmesh.new(); bm2.from_mesh(me)
    bm2.faces.ensure_lookup_table()
    am=bpy.data.materials.new("M_Blue_"+n); am.diffuse_color=(0.05,0.15,0.6,1)
    ym=bpy.data.materials.new("M_Yellow_"+n); ym.diffuse_color=(1,0.85,0.1,1)
    me.materials.append(ym); me.materials.append(am)
    import math
    for f in bm2.faces:
        if f.normal.z>0.6 and len(f.verts)==4: f.material_index=0 if f.calc_area()<0.55*(x1-x0)*(y1-y0) else 1
        else: f.material_index=1
    bm2.to_mesh(me); bm2.free()
    for p in me.polygons: p.use_smooth=False
    return ob

def pod(n, x0,x1, y0,y1, z0,z1, chanfro=0.18, bevel=0.035):
    """Pod por MODELAGEM: caixa + chanfro frontal (topo e base) + bevel leve.
    Mantem TOPO PLANO, LATERAIS PLANAS e BASE PLANA (regra 110)."""
    import bmesh, math
    me=bpy.data.meshes.new(n); ob=bpy.data.objects.new(n, me)
    bpy.context.collection.objects.link(ob)
    bm=bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 if v.co.x<0 else x1
        v.co.y = y0 if v.co.y<0 else y1
        v.co.z = z0 if v.co.z<0 else z1
    L=x1-x0; c=L*chanfro
    # chanfro FRONTAL: puxar os 4 verts da frente (x1) para tras nos z extremos
    for v in bm.verts:
        if abs(v.co.x-x1)<1e-6:
            if abs(v.co.z-z0)<1e-6 or abs(v.co.z-z1)<1e-6:
                v.co.x = x1-c
    if bevel>0:
        bmesh.ops.bevel(bm, geom=list(bm.edges)+list(bm.verts), offset=bevel, segments=2, affect="EDGES")
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=False
    return ob

def capsula(n,x0,x1,y,z,r,rot=(0,math.radians(90),0)):
    # capsula ao longo de X: cilindro DEITADO (eixo X) + 2 hemisferios nas pontas
    Lc=abs(x1-x0); cx=(x0+x1)/2
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=max(Lc-2*r,0.001), vertices=20,
                                       location=(cx,y,z), rotation=rot)
    o=bpy.context.object; o.name=n
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=20, ring_count=10, location=(cx+Lc/2-r,y,z))
    bpy.context.object.name=n+"_t"
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=20, ring_count=10, location=(cx-Lc/2+r,y,z))
    bpy.context.object.name=n+"_b"
    for m in (n,n+"_t",n+"_b"):
        for p in bpy.data.objects[m].data.polygons: p.use_smooth=True
    return o

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
RF=R*0.42/0.84; cil("W_FL",0.72, 0.52,RF*0.9412*0.968*0.985,RF,0.150); suave("W_FL",1)
cil("W_FR",0.72,-0.52,RF*0.9412*0.968*0.985,RF,0.150); suave("W_FR",1)
cil("HUB_FL",0.72, 0.525,R,R*0.40,0.07); cil("HUB_FR",0.72,-0.525,R,R*0.40,0.07)
cil("AX_F",0.72,0,R/2,0.032,0.72,(0,math.radians(90),0)); suave("AX_F",0)
RR=R*0.50; RR=R*0.50/0.84; cil("W_RL",-0.65,0.58,RR*0.9412*0.968*0.985,RR,0.240); suave("W_RL",1)
cil("W_RR",-0.65,-0.58,RR*0.9412*0.968*0.985,RR,0.240); suave("W_RR",1)
cil("HUB_RL",-0.65,0.555,R,R*0.40,0.07); cil("HUB_RR",-0.65,-0.555,R,R*0.40,0.07)
cil("AX_R",-0.65,0,R/2,0.032,0.94,(0,math.radians(90),0)); suave("AX_R",0)
for n in ("W_FL","W_FR","W_RL","W_RR"): suave(n,1)
for sf in (1,-1):
    cil("HUB_F"+("L" if sf>0 else "R"),0.72, sf*0.52,R*0.30,R*0.30,0.20,(0,math.radians(90),0)); suave("HUB_F"+("L" if sf>0 else "R"),1)
    cil("HUB_R"+("L" if sf>0 else "R"),-0.65, sf*0.58,R*0.36,R*0.36,0.26,(0,math.radians(90),0)); suave("HUB_R"+("L" if sf>0 else "R"),1)
# ===== BICO: ELIPSOIDE AFUNILADO (curvo, nao escada) =====
box("C_Nose",0.34,0.86, -0.19,0.19, 0.22,0.52); suave("C_Nose",2); suave("C_Nose",2)
# ===== CHASSI: PERFIL CURVO (cilindro achatado de secao eliptica ao longo de X) =====
cil("C_Spine",-0.10,0,0.30,0.16,1.80,(0,math.radians(90),0)); suave("C_Spine",1)
bpy.data.objects["C_Spine"].scale=(1.0,1.0,0.55)
bpy.context.view_layer.objects.active=bpy.data.objects["C_Spine"]
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
# ===== SIDEPODS EM GOTA (esfera alongada + afinamento) =====
# ===== POD UNICO (receita do vision): UMA caixa, TAPER PROGRESSIVO, INSET no topo =====
#   azul PLANO afundado dentro do U amarelo ESPESSO (sem capsula, sem peca sobreposta)
for sy,sn in ((1,"L"),(-1,"R")):
    pod_unico("SP_"+sn, -0.70, 0.42, *sorted((sy*0.115, sy*0.585)), 0.040, 0.330, taper=0.34, borda=0.085)
# ===== BUMPER DIANTEIRO: CARENAGEM (regra 90: troca de PRIMITIVA — tubo -> carenagem chata e larga) =====
box("B_Caren",0.56,1.02, -0.66,0.66, 0.18,0.40); suave("B_Caren",2)
box("B_Nose",0.78,1.10, -0.15,0.15, 0.22,0.34); suave("B_Nose",1)
# GRADE central (lamelas verticais) — assinatura do concept
for gi in range(5):
    box("B_Slat%d"%gi, 0.98,1.02, -0.14+gi*0.07,-0.12+gi*0.07, 0.30,0.44)
# 2 CINTAS AMARELAS NA SUPERFICIE FRONTAL (antes estavam enterradas -> o vision nao as via)
for sf in (1,-1):
    box("B_Strap"+("L" if sf>0 else "R"), 0.90,1.00, sf*0.30,sf*0.52, 0.26,0.48); suave("B_Strap"+("L" if sf>0 else "R"),1)
# ===== TRASEIRA: bumper em C + 2 escapes finos inclinados + motor =====
bpy.ops.mesh.primitive_torus_add(major_radius=0.46, minor_radius=0.052, major_segments=36, minor_segments=12,
                                 location=(-0.66,0,0.26))
tr=bpy.context.object; tr.name="R_Bumper"
box("R_Cut",-1.40,-0.86, -0.60,0.60, -0.40,0.40)
m=tr.modifiers.new('cut','BOOLEAN'); m.operation='DIFFERENCE'; m.object=bpy.data.objects['R_Cut']; m.solver='EXACT'
bpy.context.view_layer.objects.active=tr; bpy.ops.object.modifier_apply(modifier='cut')
bpy.data.objects.remove(bpy.data.objects['R_Cut'], do_unlink=True); suave("R_Bumper",1)
esf("R_MotorBlock",(-0.86,0,0.56),0.26,0.22,0.24); suave("R_MotorBlock",1)
# CARENAGEM TRASEIRA: fornece a largura da cauda (estacao 88-96%%) SEM alongar o veiculo
# TRASEIRA EM 3 VOLUMES SEPARADOS COM VAO REAL (vision: deletar e reconstruir)
for sf in (1,-1):
    y0,y1=sorted((sf*0.36, sf*0.68))
    box("R_Pod"+("L" if sf>0 else "R"), -1.12,-0.66, y0,y1, 0.20,0.52); suave("R_Pod"+("L" if sf>0 else "R"),1)
box("R_Motor",-1.02,-0.74, -0.22,0.22, 0.22,0.50); suave("R_Motor",1)   # bloco central, com AR ate os pods; suave("R_Fairing",1)
cil("R_ExhL",-1.04, 0.15,0.46,0.070,0.30,(0,math.radians(72),0)); cil("R_ExhR",-1.04,-0.15,0.46,0.070,0.30,(0,math.radians(72),0))
cil("HOLE_L",-1.08, 0.13,0.44,0.040,0.14,(0,math.radians(72),0)); cil("HOLE_R",-1.08,-0.13,0.44,0.040,0.14,(0,math.radians(72),0))
cil("R_ExhC",-1.14,0,0.46,0.105,0.40,(0,math.radians(75),0)); suave("R_ExhC",1)
for sf in (1,-1): cil("R_ExhT"+("L" if sf>0 else "R"),-1.12,sf*0.20,0.48,0.070,0.34,(0,math.radians(72),0))
box("P_Seat",-0.56,-0.40, -0.20,0.20, 0.33,0.64, rot=(0,math.radians(-18),0))
box("R_Wing",-1.30,-1.12, -0.52,0.52, 0.50,0.62); suave("R_Wing",2)
for sf in (1,-1): box("R_WingSup"+("L" if sf>0 else "R"),-1.15,-1.10, sf*0.14,sf*0.20, 0.44,0.62)
# ENDPLATES verticais (faltavam — o vision cobrou: 2 tips amarelos verticais)
for sf in (1,-1):
    box("R_EndP"+("L" if sf>0 else "R"),-1.235,-1.03, sf*0.44,sf*0.52, 0.44,0.78); suave("R_EndP"+("L" if sf>0 else "R"),1)

cil("R_HoleC",-1.08,0,0.48,0.042,0.10,(0,math.radians(72),0))
# ===== CHASSI TUBULAR: liga tudo (vision: "tudo flutua, falta chassi") =====
for sf in (1,-1):
    box("C_Rail"+("L" if sf>0 else "R"), -1.10,0.92, sf*0.16,sf*0.26, 0.12,0.22); suave("C_Rail"+("L" if sf>0 else "R"),1)
box("C_Floor",-0.95,0.86, -0.30,0.30, 0.08,0.14); suave("C_Floor",1)
box("C_Bulk",0.60,0.78, -0.24,0.24, 0.10,0.44); suave("C_Bulk",1); suave("C_Rail"+("L" if sf>0 else "R"),1)
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
    
# ===== CAPACETE COM VISEIRA (vision: "capacete com viseira no volume correto") =====
box("P_Visor",-0.42,-0.175, -0.145,0.145, 1.045,1.125); suave("P_Visor",1)
esf("P_HelmBack",(-0.12,0,1.10),0.080,0.185,0.150); suave("P_HelmBack",1)
# ===== BANCO CONCHA (vision: "sem banco") =====
box("P_Seat",-0.30,-0.14, -0.22,0.22, 0.30,0.56); suave("P_Seat",1)
box("P_SeatBack",-0.16,-0.06, -0.22,0.22, 0.50,0.82); suave("P_SeatBack",1)
# ===== PERNAS (vision: "sem pernas") =====
for sf in (1,-1):
    capsula("P_Leg"+("L" if sf>0 else "R"), 0.62,-0.06, sf*0.14, 0.34, 0.095)
    capsula("P_Shin"+("L" if sf>0 else "R"), 0.62,0.86, sf*0.16, 0.235, 0.075)

cil("P_Arm"+sn, -0.22, sy*0.19,0.52,0.048,0.46,(0,math.radians(78),0)); suave("P_Arm"+sn,1)
bpy.ops.mesh.primitive_torus_add(major_radius=0.082, minor_radius=0.020, major_segments=28, minor_segments=10,
                                 location=(0.04,0,0.44), rotation=(0,math.radians(58),0))
bpy.context.object.name="P_Wheel"; suave("P_Wheel",1)
# ===== LIMPEZA (regra 99/100): remover duplicatas .001 e CONFIRMAR a execucao =====
_rem=0
for _d in list(bpy.data.objects):
    if _d.name.endswith(".001") and any(_d.name.startswith(p) for p in ("P_Seat","P_Shin","P_Leg","P_Torso","SP_")):
        bpy.data.objects.remove(_d, do_unlink=True); _rem+=1
print("###LIMPEZA### removidos=%d"%_rem)
print("###FIM### total=%d"%len([o for o in bpy.data.objects if o.type=="MESH"]))

bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B141.blend')
print('###B017### ok')

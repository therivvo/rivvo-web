# Builder V2 do The Bubble Bumper — dirigido pela ENVELOPE MEDIDA do concept.
# Geometria-alvo (medida por segmentacao das 4 ortograficas, H=1.207):
#   L=2.255  W=1.494  H=1.207  (L:W:H = 1.87 : 1.24 : 1)
#   perfil lateral z_topo(xf)/H: 0.025->0.254 0.10->0.321 0.20->0.378 0.25->0.428
#                               0.275->0.520 0.35->0.537 (cowl)  0.375->0.445 (BANHEIRA)
#                               0.425->0.607 0.60->0.990 (CAPACETE topo) 0.75->0.619
#                               0.80->0.540 (traseira) 0.90->0.674 0.975->0.704 (ASA)
#   planta largura(xf)/W: 0.05->0.786 (bumper) 0.20-0.30->0.942 (rodas diant)
#                         0.40-0.70->0.90-0.94 (pods) 0.75-0.85->0.97 (rodas tras)
#   rodas: dianteira d=0.372 larg=0.152 |y|=0.626 ; traseira d=0.565 larg=0.448 |y|=0.523
#   centros: dianteira x=+0.519 ; traseira x=-0.653  (entre-eixos 1.172)
# USO: OVR={'v':'W100'}; exec(open('/opt/blender-runner/build_bb2.py').read())
import traceback, time, math
import numpy as _np
try: Matrix
except NameError:
    from mathutils import Matrix
P={"v":"W000","exp":-0.45,"key":300.0,"fill":150.0,"rim":240.0}
P.update(globals().get("OVR",{}))
V=P["v"]
t0=time.time(); R['v']=V; R['stage']={}; made=[]; QA={}
V3=Vector

def mat_rich(name,color,rough,metal,ns=180.0,bump=0.0016,spec=0.6,coat=0.0):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); bsdf=nt.nodes.new('ShaderNodeBsdfPrincipled')
    tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=ns; tex.inputs['Detail'].default_value=6.0
    bmp=nt.nodes.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value=bump
    nt.links.new(tex.outputs['Fac'],bmp.inputs['Height']); nt.links.new(bmp.outputs['Normal'],bsdf.inputs['Normal'])
    bsdf.inputs['Base Color'].default_value=(color[0],color[1],color[2],1.0)
    bsdf.inputs['Roughness'].default_value=rough; bsdf.inputs['Metallic'].default_value=metal
    for k,v in (('Specular IOR Level',spec),('Coat Weight',coat)):
        if k in bsdf.inputs: bsdf.inputs[k].default_value=v
    nt.links.new(bsdf.outputs['BSDF'],out.inputs['Surface']); return m

# cores amostradas do concept
mat_rich('M_Yellow',(0.680,0.580,0.0280),0.72,0.0,190,0.0016,0.16,0.0)
mat_rich('M_Blue',(0.0300,0.0680,0.174),0.74,0.0,190,0.0014,0.14,0.0)
mat_rich('M_BlueDk',(0.0160,0.0360,0.092),0.78,0.0,210,0.0016,0.12,0.0)
mat_rich('M_Dark',(0.016,0.016,0.019),0.82,0.0,340,0.0026,0.14,0.0)
mat_rich('M_Silver',(0.30,0.31,0.33),0.55,0.85,420,0.0014,0.30,0.0)
mat_rich('M_Visor',(0.46,0.52,0.60),0.22,0.05,600,0.0004,0.75,0.35)
mat_rich('M_Gasket',(0.020,0.020,0.024),0.78,0.0,340,0.0030,0.20,0.0)
mat_rich('M_Cushion',(0.055,0.21,0.60),0.48,0.0,240,0.0032,0.42,0.0)
mat_rich('M_Pilot',(0.0168,0.0400,0.200),0.76,0.0,200,0.0018,0.14,0.0)
mat_rich('M_Pedal',(0.22,0.22,0.24),0.54,1.0,300,0.0020,0.55,0.0)
mat_rich('M_Eye',(0.010,0.010,0.012),0.14,0.0,500,0.0006,0.90,0.4)
mat_rich('M_White',(0.96,0.96,0.96),0.20,0.0,400,0.0008,0.62,0.2)
mat_rich('M_Plate',(0.30,0.32,0.31),0.50,0.80,400,0.0014,0.34,0.0)
mat_rich('M_Gold',(0.44,0.30,0.045),0.45,0.90,380,0.0014,0.42,0.0)
mat_rich('M_Floor',(0.075,0.078,0.088),0.55,0.0,900,0.0006,0.35,0.0)
MG=bpy.data.materials

def safe(k,fn):
    try:
        r=fn(); R['stage'][k]='ok'; return r
    except Exception as e:
        R['stage'][k]='FAIL '+repr(e)[:150]; return None
def assign(ob,name,pred=None):
    m=MG.get(name)
    if m is None: return None
    i=None
    for k,mm in enumerate(ob.data.materials):
        if mm is m: i=k; break
    if i is None: ob.data.materials.append(m); i=len(ob.data.materials)-1
    for p in ob.data.polygons:
        if pred is None or pred(p): p.material_index=i
    return i
def seal(ob,merge=0.0015):
    bm=bm_of(ob)
    if merge>0: bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=merge)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    bnd=[e for e in bm.edges if e.is_boundary]
    if bnd: bmesh.ops.holes_fill(bm,edges=bnd)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm_done(bm,ob,True); return ob
def loft(name,secs,smooth=True,cap=True):
    n=len(secs[0]); verts=[p for s in secs for p in s]; faces=[]
    for i in range(len(secs)-1):
        for k in range(n):
            k2=(k+1)%n; faces.append([i*n+k,i*n+k2,(i+1)*n+k2,(i+1)*n+k])
    if cap:
        faces.append(list(range(n))[::-1]); last=(len(secs)-1)*n; faces.append([last+k for k in range(n)])
    return mesh_from(name,verts,faces,smooth)
def revolve(name,prof,x0,z0,y0=0.0,seg=28,capopen=False):
    K=len(prof); verts=[]
    for j in range(seg):
        a=2*math.pi*j/seg
        for (r,w) in prof: verts.append((x0+r*math.cos(a), y0+r*math.sin(a), z0+w))
    faces=[]
    for j in range(seg):
        j2=(j+1)%seg
        for i in range(K):
            i2=(i+1)%K; faces.append([j*K+i,j*K+i2,j2*K+i2,j2*K+i])
    o=mesh_from(name,verts,faces,True)
    if capopen: seal(o)
    return o
def dome(name,cx,cy,cz,R,sz=1.0,sy=1.0,seg=40,rings=24,pa=1.0):
    # pa<1 = COROA MAIS CHEIA (o perfil do concept nao e esfera; medido no FRONT/CAPACETE)
    prof=[(max(0.0015,R*(math.sin(math.pi*i/rings)**pa)*sy), -R*math.cos(math.pi*i/rings)*sz) for i in range(rings+1)]
    return revolve(name,prof,cx,cz,y0=cy,seg=seg,capopen=True)
def sq(cx,ry,rz,n=24,p=2.0,z0=0.0,zsq=0.90,cy=0.0):
    pts=[]
    for k in range(n):
        a=2*math.pi*k/n; ca=math.cos(a); sa=math.sin(a)
        y=math.copysign(abs(ca)**(2.0/p),ca)*ry; z=math.copysign(abs(sa)**(2.0/p),sa)*rz
        if z<0: z*=zsq
        pts.append((cx,cy+y,z0+z))
    return pts
def sqz(cx,cy,ry,rz,n=24,p=2.8,z0=0.0,zsq=0.90):
    return sq(cx,ry,rz,n,p,z0,zsq,cy)
def tire_tread(t, name, xc, yc, zc, R, hw):
    """BANDA DE RODAGEM em CHEVRON (V). O concept mostra 7-8 'V' empilhados em
    relevo claro sobre pneu escuro -> ribs elevados em material claro.
    Eixo da roda = Y; superficie = cilindro de raio R em torno de Y."""
    NG=int(P.get('tread_n',7))
    if NG<=0: return []
    ang=math.radians(float(P.get('chev_ang',26.0)))
    mat=P.get('tread_mat','M_Plate')
    thick=R*float(P.get('chev_t',0.030))
    wid=hw*2.0*float(P.get('chev_w',0.055))
    L=hw*0.96
    out=[]
    for i in range(NG):
        th=2*math.pi*(i+0.5)/NG
        for side in (1.0,-1.0):
            dth=math.atan(L*math.tan(ang)/R)
            te=th+side*dth
            _ov=L*float(P.get('chev_ov',0.14))*side
            P0=V3((R*math.cos(th),-_ov,R*math.sin(th)))
            P1=V3((R*math.cos(te),side*(L+float(P.get('chev_ext',0.10))*L),R*math.sin(te)))
            C=(P0+P1)*0.5
            u=P1-P0; ln=u.length
            if ln<1e-6: continue
            u=u/ln
            thm=th+side*dth*0.5
            ez=V3((math.cos(thm),0.0,math.sin(thm)))
            ey=ez.cross(u)
            if ey.length<1e-6: continue
            ey=ey.normalized(); ex=u
            b_=box('%s_ch%d%s'%(name,i,'L' if side>0 else 'R'),(0,0,0),(ln*0.5,wid*0.5,thick*0.5),bevel=0.0,segs=1)
            assign(b_,mat)
            M=Matrix(((ex.x,ey.x,ez.x,0.0),(ex.y,ey.y,ez.y,0.0),(ex.z,ey.z,ez.z,0.0),(0.0,0.0,0.0,1.0)))
            b_.data.transform(M)
            b_.data.transform(Matrix.Translation((xc+C.x,yc+C.y,zc+C.z)))
            out.append(b_)
    return out
def wheel_mesh(name,xc,yc,zc,R,hw,seg=48,flip=1):
    """roda de kart: pneu SLICK liso + disco solido (lip prata, prato cinza, anel amarelo,
    3 pinos quadrados amarelos a 120 graus, cubo central)"""
    # carcaca do pneu a 0.955R: a BANDA DE RODAGEM (blocos) passa a ser a superficie externa
    _R=R*1.0
    ri=R*float(P.get('rim_r',0.60))       # raio externo do aro
    sh=R*float(P.get('shoulder',0.11))    # raio do ombro (arco de 90 graus)
    bulge=float(P.get('tread_bulge',0.012))  # abaulamento da banda
    prof=[(ri,-hw*0.98),(R-sh,-hw*0.98)]
    for k in range(1,5):                   # ombro lado -hw
        a=k/4.0*math.pi/2.0
        prof.append((R-sh+sh*math.sin(a),-hw*0.98+sh*0.98*(1.0-math.cos(a))))
    prof.append((R*(1.0+bulge),0.0))       # banda abaulado no centro
    for k in range(4,0,-1):                # ombro lado +hw
        a=k/4.0*math.pi/2.0
        prof.append((R-sh+sh*math.sin(a),hw*0.98-sh*0.98*(1.0-math.cos(a))))
    prof+=[(R-sh,hw*0.98),(ri,hw*0.98),(ri,hw*0.72),(ri,0.0),(ri,-hw*0.72)]
    t=revolve(name,prof,0,0,seg=seg); assign(t,'M_Dark')
    t.data.transform(Matrix.Rotation(math.radians(90),4,'X')); t.data.transform(Matrix.Translation((xc,yc,zc)))
    parts=[t]
    rp=[(R*0.09,-hw*0.995),(R*0.42,-hw*0.995),(R*0.58,-hw*0.94),(R*0.60,-hw*0.84),
        (R*0.60,hw*0.84),(R*0.58,hw*0.94),(R*0.42,hw*0.995),(R*0.09,hw*0.995),
        (R*0.09,hw*0.58),(R*0.09,0.0),(R*0.09,-hw*0.58)]
    rim=revolve(name+'_lip',rp,0,0,seg=max(24,seg//2)); assign(rim,'M_Silver')
    rim.data.transform(Matrix.Rotation(math.radians(90),4,'X')); rim.data.transform(Matrix.Translation((xc,yc,zc)))
    parts.append(rim)
    pl=[(R*0.035,-hw*0.74),(R*0.44,-hw*0.74),(R*0.55,-hw*0.70),(R*0.55,hw*0.70),(R*0.44,hw*0.74),(R*0.035,hw*0.74)]
    plate=revolve(name+'_plate',pl,0,0,seg=max(24,seg//2)); assign(plate,P.get('rim_face','M_Plate'))
    plate.data.transform(Matrix.Rotation(math.radians(90),4,'X')); plate.data.transform(Matrix.Translation((xc,yc,zc)))
    parts.append(plate)
    _r0=float(P.get('ring_r',0.40)); _rw=float(P.get('ring_w',0.045))
    ar=revolve(name+'_ring',[(R*(_r0-_rw),-hw*1.00),(R*(_r0+_rw),-hw*1.00),(R*(_r0+_rw),hw*1.00),(R*(_r0-_rw),hw*1.00)],0,0,seg=max(24,seg//2))
    assign(ar,'M_Yellow')
    ar.data.transform(Matrix.Rotation(math.radians(90),4,'X')); ar.data.transform(Matrix.Translation((xc,yc,zc)))
    parts.append(ar)
    NPIN=int(P.get('pins',5))
    PS=P.get('pin_mat','M_Silver')
    for k in range(NPIN):
        ang=2*math.pi*k/NPIN+math.radians(36)
        pin=box(name+'_pin%d'%k,(0,0,0),(R*0.055,R*0.12*hw,R*0.055),bevel=0.004,segs=1)
        assign(pin,PS)
        pin.data.transform(Matrix.Translation((xc+R*0.285*math.cos(ang), yc+flip*hw*0.99, zc+R*0.285*math.sin(ang))))
        parts.append(pin)
    hp=[(R*0.04,-hw*0.96),(R*0.185,-hw*0.96),(R*0.21,-hw*0.99),(R*0.21,hw*0.99),(R*0.185,hw*0.96),(R*0.04,hw*0.96),
        (R*0.04,hw*0.62),(R*0.04,0.0),(R*0.04,-hw*0.62)]
    hub=revolve(name+'_hub',hp,0,0,seg=26); assign(hub,'M_Silver')
    hub.data.transform(Matrix.Rotation(math.radians(90),4,'X')); hub.data.transform(Matrix.Translation((xc,yc,zc)))
    parts.append(hub)
    # banda de rodagem (concept tem sulcos + chevron; 3 auditorias apontaram "slick liso")
    parts += tire_tread(None,name,xc,yc,zc,R,hw)
    return join(parts,name+'_W')
def blade(name,spine,halfw,halfh,zc,bevel=0.0):
    """extrusa um retangulo (halfw em Y-horizontal normal, halfh em Z) ao longo de uma espinha no plano XY"""
    Pp=[V3((p[0],p[1],0)) for p in spine]; n=len(Pp); secs=[]
    for i,p in enumerate(Pp):
        tg=(Pp[1]-Pp[0]) if i==0 else ((Pp[-1]-Pp[-2]) if i==n-1 else (Pp[i+1]-Pp[i-1]))
        tg=tg.normalized(); nr=V3((-tg.y,tg.x,0)).normalized()
        a=p+nr*halfw; b=p-nr*halfw
        top=(zc+halfh); bot=(zc-halfh)
        secs.append([(a.x,a.y,top),(b.x,b.y,top),(b.x,b.y,bot),(a.x,a.y,bot)])
    return loft(name,secs,cap=True)
def tubevar(name,pts,radii,seg=12):
    Pp=[V3(p) for p in pts]; n=len(Pp); rings=[]
    for i,p in enumerate(Pp):
        r=radii[i]
        tg=(Pp[1]-Pp[0]) if i==0 else ((Pp[-1]-Pp[-2]) if i==n-1 else (Pp[i+1]-Pp[i-1]))
        tg=tg.normalized(); up=V3((0,0,1))
        if abs(tg.dot(up))>0.95: up=V3((1,0,0))
        s_=tg.cross(up).normalized(); nr=s_.cross(tg).normalized()
        rings.append([tuple(p+s_*(math.cos(2*math.pi*k/seg)*r)+nr*(math.sin(2*math.pi*k/seg)*r)) for k in range(seg)])
    verts=[v for rr in rings for v in rr]; faces=[]
    for i in range(n-1):
        for k in range(seg):
            k2=(k+1)%seg; faces.append([i*seg+k,i*seg+k2,(i+1)*seg+k2,(i+1)*seg+k])
    faces.append(list(range(seg))[::-1]); last=(n-1)*seg; faces.append([last+k for k in range(seg)])
    return mesh_from(name,verts,faces,True)
def tube_round(name,pts,r,seg=20,cap=True):
    """tubo de secao CIRCULAR real com frames ao longo da polilinha (sweep() nao passa seg ao tube)"""
    P3=[V3(tuple(p)) for p in pts]
    n=len(P3); secs=[]; ref=V3((0.0,0.0,1.0))
    for i,p in enumerate(P3):
        if i==0: t=(P3[1]-P3[0])
        elif i==n-1: t=(P3[n-1]-P3[n-2])
        else: t=(P3[i+1]-P3[i-1])
        if t.length<1e-9: t=V3((1.0,0.0,0.0))
        t.normalize()
        u=ref.cross(t)
        if u.length<1e-6: u=V3((1.0,0.0,0.0)).cross(t)
        u.normalize(); v=t.cross(u); v.normalize()
        sec=[tuple(p+u*(r*math.cos(2*math.pi*k/seg))+v*(r*math.sin(2*math.pi*k/seg))) for k in range(seg)]
        secs.append(sec)
    o=loft(name,secs,cap=cap)
    return o
def sweep(name,pts,r,seg=10,merge=0.002):
    o=tube(name,[tuple(p) for p in pts],r); c=curve_to_mesh(o)
    if c is not None: o=c
    if merge>0: seal(o,merge)
    return o
def box(name,center,size,bevel=0.02,segs=2):
    bpy.ops.mesh.primitive_cube_add(size=2,location=center)
    o=bpy.context.active_object; o.name=name; o.scale=size
    bpy.ops.object.transform_apply(scale=True)
    b=min(bevel*P.get('inf',1.9),0.47*min(size))
    if b>0.001: add_mod(o,'BEVEL',width=b,segments=segs); apply_mods(o)
    return o
def dome_dir(name,center,R,dirv,sz=1.0,seg=28,rings=16,flat=1.0):
    o=dome(name,0.0,0.0,0.0,R,sz=1.0,sy=1.0,seg=seg,rings=rings)
    o.scale=(1.0,1.0,sz*flat)
    d=V3(dirv).normalized()
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.transform_apply(rotation=True)
    o.location=center
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.transform_apply(location=True)
    return o
def qp(ob):
    try:
        m=qa(ob,exigir_manifold=True); return m['metricas'][list(m['metricas'])[0]]['non_manifold']
    except Exception: return 'ERR'
def reg(nm,ob): QA[nm]=qp(ob); return ob

# ============ GEOMETRIA MEDIDA ============
H=1.207; L=2.255; W=1.494
XFO=+1.128; XRE=-1.128
XF=P.get('x_fw',+0.602); XR=P.get('x_rw',-0.664)
RF=P.get('r_f',0.185); RR=P.get('r_r',0.215)
HWF=P.get('hw_f',0.155); HWR=P.get('hw_r',0.158)
TYF=P.get('ty_f',0.589); TYR=P.get('ty_r',0.5855)

def prof_top(xf):
    """z_topo/H do concept na fracao xf (0=frente)"""
    tab=[(0.00,0.204),(0.025,0.254),(0.05,0.286),(0.075,0.286),(0.10,0.321),(0.125,0.301),
         (0.15,0.323),(0.175,0.356),(0.20,0.378),(0.225,0.410),(0.25,0.428),(0.275,0.520),
         (0.30,0.522),(0.325,0.522),(0.35,0.537),(0.375,0.445),(0.40,0.473),(0.425,0.607),
         (0.45,0.575),(0.475,0.562),(0.50,0.567),(0.525,0.813),(0.55,0.928),(0.575,0.970),
         (0.60,0.990),(0.625,0.998),(0.65,0.993),(0.675,0.978),(0.70,0.940),(0.725,0.813),
         (0.75,0.619),(0.775,0.527),(0.80,0.540),(0.825,0.532),(0.85,0.520),(0.875,0.515),
         (0.90,0.674),(0.925,0.687),(0.95,0.697),(0.975,0.704),(1.00,0.500)]
    if xf<=tab[0][0]: return tab[0][1]
    if xf>=tab[-1][0]: return tab[-1][1]
    for i in range(len(tab)-1):
        a,b=tab[i],tab[i+1]
        if a[0]<=xf<=b[0]:
            u=(xf-a[0])/(b[0]-a[0]); return a[1]+(b[1]-a[1])*u
    return tab[-1][1]
def xf_of(x): return (XFO-x)/L

# ============ 1. NARIZ (seguindo o perfil medido) ============
def nose():
    out=[]; NS=26
    secs=[]
    for i in range(NS):
        xf=0.015+0.235*(i/(NS-1.0))
        x=XFO-xf*L
        zt=prof_top(xf)*H*0.88
        _t=i/(NS-1.0)
        # CONCEPT: bico FINO na frente (frente lida: 'cunha fina estreita'), alargando para trás
        _s2=min(1.0,_t/0.50)**0.75
        ry=0.066+0.104*_s2
        zb=max(0.0,0.0+0.020*(i/(NS-1.0)))
        zc=(zb+zt)/2.0; rz=(zt-zb)/2.0
        secs.append(sq(x,ry,rz,38,2.0,z0=zc,zsq=1.02))
    o=loft('Nose',secs); assign(o,'M_Blue'); add_mod(o,'SUBSURF',levels=1); apply_mods(o); seal(o)
    # ABRE a cavidade da grade (o nariz cobria): boolean DIFFERENCE
    try:
        _cut=box('NoseGrilleCut',(XFO-0.120,0.0,0.150),(0.120,0.260,0.140),bevel=0.012,segs=2)
        o=boolean(o,_cut,'DIFFERENCE')
        # NAO usar seal() aqui: holes_fill fecharia a cavidade
        assign(o,'M_Blue')
        R['nose_cut']='ok'
    except Exception as e:
        R['nose_cut']=repr(e)[:70]
    out.append(reg('nose',o))
    # faixa amarela central = DECAL nas faces do dorso do nariz (rente e reta)
    assign(o,'M_Yellow', lambda q: q.normal.z>0.52 and abs(q.center.y)<0.040 and q.center.x>-0.02)
    return join(out,'NOSE')
NO=safe('nose',nose)
if NO: made.append(NO)

# ============ 2. PARA-CHOQUE DIANTEIRO: lamina baixa em U (nao tubo) ============
def front_bumper():
    out=[]; rb=P.get('bump_h',0.070); zb=P.get('bump_z',0.132)
    # lamina em U que ABRACXA o nariz: |y|<=0.575, recuando para x=XFO-0.42 nas pontas
    spine=[]; NS=41
    for i in range(NS):
        t=i/(NS-1.0); a_=-math.pi/2+math.pi*t
        _sn=math.sin(a_); yy=0.556*math.copysign(abs(_sn)**P.get('bump_py',1.0),_sn)
        xx=(XFO-0.048) - P.get('bump_reach',0.720)*(1.0-math.cos(a_))
        spine.append((xx,yy,0.240+0.020*math.cos(a_*0.5)))
    o=tube_round('Bumper_Ring',spine,rb*1.07,20); assign(o,P.get('ringmat','M_Plate'))
    # (sem topos amarelos: os colares coaxiais ja dao o amarelo do concept)
    for _sy in (1,-1):
        # BLOCO AMARELO integrado SOBRE a barra (concept: 2 blocos amarelos grandes nas laterais)
        _bl=tube_round('Pad_'+('L' if _sy>0 else 'R'),
                       [(XFO-0.028,_sy*0.330,0.2622),(XFO-0.086,_sy*0.400,0.2610),(XFO-0.150,_sy*0.470,0.2596)],
                       0.086,18)
        assign(_bl,'M_Yellow'); out.append(reg('pad_'+('l' if _sy>0 else 'r'),_bl))
    # BARRA TRANSVERSAL FRONTAL: o concept tem run CONTIGUO de 1.31 m em xf 0.175
    # (atravessa os dois lados); so o U com cantos separados deixa 3 runs -> IoU 0.55 ali.
    if P.get('fbar',1):
        fbar=box('FBump_Bar',(P.get('fbar_x',0.755),0.0,P.get('fbar_z',0.085)),
                 (P.get('fbar_c',0.190),0.585,0.048),bevel=0.020,segs=2)
        assign(fbar,'M_Blue'); out.append(reg('fbar',fbar))
    return join(out,'FBUMP')
# ===== F3/F5 =====
# ===== F3: ANEL AMARELO EM VOLTA DA PONTA DO BICO (o concept tem C grosso amarelo) =====
def nose_ring():
    return None

NR=safe('nose_ring',nose_ring)
if NR: made.append(NR)

# ===== F5: FAROL RETANGULAR ACLESO na face frontal do bico =====
def headlight():
    out=[]
    hx=XFO-0.036
    lens=box('Lamp_Lens',(hx,0.0,0.168),(0.015,0.072,0.030),bevel=0.005,segs=2)
    assign(lens,'M_Lamp'); out.append(reg('lamp',lens))
    bez=box('Lamp_Bezel',(hx-0.013,0.0,0.168),(0.016,0.090,0.044),bevel=0.006,segs=2)
    assign(bez,'M_Silver'); out.append(reg('lampbez',bez))
    return join(out,'LAMP')

FB=safe('front_bumper',front_bumper)
if FB: made.append(FB)
HL=safe('headlight',headlight)
if HL: made.append(HL)

# ============ 3. GRADE INFERIOR com 5 aletas ============
def grille():
    out=[]
    gf=box('Grille_Frame',(XFO-0.098,0.0,0.150),(0.052,0.246,0.132),bevel=0.018,segs=2); assign(gf,'M_BlueDk'); out.append(gf)
    # 5 fendas verticais RECUADAS (a 'boca' do kart)
    for j,yy in enumerate((-0.160,-0.080,0.0,0.080,0.160)):
        sl=box('Grille_Slot%d'%j,(XFO-0.072,yy,0.150),(0.046,0.032,0.116),bevel=0.007,segs=1); assign(sl,'M_Dark'); out.append(sl)
    # nervuras entre as fendas (dão a leitura de grade)
    for j,yy in enumerate((-0.120,-0.040,0.040,0.120)):
        rb=box('Grille_Rib%d'%j,(XFO-0.054,yy,0.150),(0.040,0.015,0.110),bevel=0.005,segs=1); assign(rb,'M_BlueDk'); out.append(rb)
    # farol retangular no eixo central
    lz=box('Headlight',(XFO-0.235,0.0,0.330),(0.030,0.074,0.030),bevel=0.014,segs=3); assign(lz,'M_White'); out.append(reg('light',lz))
    return join(out,'GRILLE')
GR=safe('grille',grille)
if GR: made.append(GR)

# ============ 4. NASSAU PANEL + COWL (com banheira ESCAVADA de verdade) ============
def cowl():
    out=[]; NS=22; secs=[]
    for i in range(NS):
        xf=0.225+0.235*(i/(NS-1.0)); x=XFO-xf*L
        zt=prof_top(xf)*H*0.97
        # perfil medido manda: dip em xf~0.375 (0.445H) ja vem do prof_top
        s=math.sin(math.pi*(0.10+0.80*(i/(NS-1.0))))**0.5
        ry=0.098*s+0.030
        zb=0.105
        secs.append(sq(x,ry,(zt-zb)/2.0,36,2.2,z0=(zb+zt)/2.0,zsq=0.98))
    o=loft('Cowl',secs); assign(o,'M_Blue'); add_mod(o,'SUBSURF',levels=1); apply_mods(o); seal(o)
    # ESCAVA A BANHEIRA: subtrai um solido em forma de colher
    cut=box('Cockpit_Cut',(XFO-0.452*L,0,0.640),(0.232,0.150,0.116),bevel=0.055,segs=6)
    boolean(o,cut,'DIFFERENCE'); seal(o)
    try: bpy.data.objects.remove(cut,do_unlink=True)
    except Exception: pass
    out.append(reg('cowl',o))
    # nassau panel: lamina vertical a frente do volante
    ns=box('Nassau',(XFO-0.30*L-0.06,0,0.430),(0.026,0.118,0.130),bevel=0.022,segs=3)
    assign(ns,'M_Blue'); out.append(reg('nassau',ns))
    ns2=box('Nassau_Face',(XFO-0.30*L-0.093,0,0.452),(0.018,0.096,0.084),bevel=0.016,segs=2)
    assign(ns2,'M_Yellow'); out.append(reg('nassau_face',ns2))
    return join(out,'COWL')
CW=safe('cowl',cowl)
if CW: made.append(CW)

# ============ 5. TUBO/CENTRAL: chassi baixo ligando tudo ============
def tub():
    NS=26; secs=[]
    for i in range(NS):
        xf=0.44+0.36*(i/(NS-1.0)); x=XFO-xf*L
        s=math.sin(math.pi*(0.10+0.80*(i/(NS-1.0))))**0.5
        ry=0.235*s+0.050; zt=0.520-0.150*(i/(NS-1.0)); zb=0.100
        secs.append(sq(x,ry,(zt-zb)/2.0,36,2.0,z0=(zb+zt)/2.0,zsq=0.98))
    o=loft('Tub',secs); assign(o,'M_Blue'); add_mod(o,'SUBSURF',levels=2); apply_mods(o); seal(o)
    assign(o,'M_Dark',lambda p: p.center.z<0.175 and abs(p.center.y)<0.20)
    return reg('tub',o)
TU=safe('tub',tub)
if TU: made.append(TU)

# ============ 6. SIDE PODS: cunha LONGA e BAIXA (nao boia) ============
def pods():
    out=[]
    for sy in (1,-1):
        nm='Pod_'+('L' if sy>0 else 'R'); NS=30; secs=[]
        for i in range(NS):
            t=i/(NS-1.0); xf=0.330+0.405*t; x=XFO-xf*L
            s=math.sin(math.pi*(0.06+0.88*t))**0.62
            outy=0.300+P.get('pod_w',0.405)*s   # borda externa: alvo medido no TOP = 1.411 m total -> half 0.705
            iny=0.175+0.115*s       # borda interna
            zb=0.105
            zt=zb+P.get('pod_zt',0.150)+P.get('pod_zt2',0.275)*s   # alvo medido no SIDE: topo ~0.53 m
            cy=sy*(outy+iny)/2.0; ry=abs(outy-iny)/2.0
            # secao retangular-arredondada no plano YZ
            sec=[]
            for k in range(26):
                a=2*math.pi*k/26.0
                ca=math.cos(a); sa=math.sin(a)
                yy=cy+math.copysign(abs(ca)**(2.0/2.0),ca)*ry
                zz=(zb+zt)/2.0+math.copysign(abs(sa)**(2.0/2.0),sa)*(zt-zb)/2.0
                sec.append((x,yy,zz))
            secs.append(sec)
        o=loft(nm,secs); assign(o,'M_Yellow'); add_mod(o,'SUBSURF',levels=1); apply_mods(o); seal(o)
        # SPLIT DE COR medido no concept: pod AMARELO embaixo (z<0.25 = 66% amarelo),
        # AZUL em cima (z>0.25 = 64% azul). Sem isso, subir o pod piora a cor.
        assign(o, P.get('pod_up_mat','M_Blue'),
               lambda p: p.center.z > float(P.get('pod_split',0.25)))
        csec=[]
        for i in range(NS):
            t=i/(NS-1.0); xf=0.330+0.405*t; x=XFO-xf*L
            sc=math.sin(math.pi*(0.05+0.90*t))**0.45
            # CAP INNER-ONLY (como o cover): no TOP o concept mostra AMARELO por fora
            # e AZUL por dentro. Cap full-width pintava o pod todo de azul visto de cima.
            oy=0.175+float(P.get('cover_w',0.265))*sc; iy=0.175
            zt=0.105+P.get('pod_zt',0.150)+P.get('pod_zt2',0.275)*sc   # acompanha o pod (antes era fixo e flutuava)
            csec.append([(x,sy*(iy-0.030),zt+0.008),(x,sy*(oy+0.016),zt-0.008),(x,sy*(oy+0.016),zt-0.074),(x,sy*(iy-0.030),zt-0.060)])
        cap=loft(nm+'_Cap',csec); assign(cap,P.get('pod_cap_mat','M_Blue')); add_mod(cap,'SUBSURF',levels=1); apply_mods(cap)
        out.append(reg(nm+'_cap',cap))
        out.append(reg(nm,o))
        # SIDE_COVER azul: peca MEDIDA (nao suposta) para o vazio acima do pod.
        # concept SIDE xf 0.36-0.62 tem AZUL 64% em z 0.25-0.44 e 71% em z 0.44-0.62;
        # W389 tentou preencher isso INFLANDO o pod (peca errada) -> cor do pod piorou.
        if P.get('side_cover',1):
            vsec=[]
            for i in range(NS):
                t=i/(NS-1.0); xf=0.360+0.260*t; x=XFO-xf*L
                sc=math.sin(math.pi*(0.12+0.76*t))**0.5
                # cover INNER-ONLY: no concept (TOP) o azul e interno e o amarelo e o balao externo.
                # SIDE o mostra acima do pod por ser mais alto, mesmo inboard.
                oy=0.175+float(P.get('cover_w',0.265))*sc; iy=0.175
                zb=0.240
                zt=0.300+float(P.get('cover_zt',0.230))*sc
                cy=sy*(oy+iy)/2.0; ry=abs(oy-iy)/2.0
                sec=[]
                for k in range(22):
                    a=2*math.pi*k/22.0
                    ca=math.cos(a); sa2=math.sin(a)
                    sec.append((x, cy+math.copysign(abs(ca),ca)*ry,
                                  (zb+zt)/2.0+math.copysign(abs(sa2),sa2)*(zt-zb)/2.0))
                vsec.append(sec)
            cov=loft(nm+'_Cvr',vsec); assign(cov,P.get('cover_mat','M_Blue'))
            add_mod(cov,'SUBSURF',levels=1); apply_mods(cov); seal(cov)
            out.append(reg(nm+'_cvr',cov))
    return join(out,'PODS')
PD=safe('pods',pods)
if PD: made.append(PD)

# ============ 7. RODAS ============
def wheels():
    out=[]
    for sy,s in ((1,'L'),(-1,'R')):
        out.append(reg('tire_f'+s,wheel_mesh('Tire_F'+s,XF,sy*TYF,RF,RF,HWF,seg=52)))
    for sy,s in ((1,'L'),(-1,'R')):
        out.append(reg('tire_r'+s,wheel_mesh('Tire_R'+s,XR,sy*TYR,RR,RR,HWR,seg=56)))
    return out
WH=safe('wheels',wheels)
if WH:
    for o in WH: made.append(o)

# ============ 8. CHASSI: eixos, direcao, pedais, banco ============
def chassis():
    out=[]
    # EIXO TRASEIRO: medido no TOP xf 0.72-0.80 — o concept tem 1 RUN CONTIGUO e o modelo tinha 3,
    # com vao em |y| 0.30-0.51. O eixo ia so ate +-0.240 e nao alcancava a face interna do pneu
    # (|y| 0.494). Comprimento vem de AXW.
    _axw=float(P.get('axle_w',0.520))
    a1=sweep('Rear_Axle',[(XR,_axw,RR),(XR+0.02,0.0,RR+0.03),(XR,-_axw,RR)],P.get('axle_r',0.042),16); assign(a1,'M_Blue'); out.append(a1)
    # BANDEJA TRASEIRA ESCURA: medido — no REAR o concept e CONTINUO (1 run, largura toda) em z>=0.16
    # com cor escura (48,48,53) em |y| 0.28-0.45; no TOP e 1 run em xf 0.70-0.78. O modelo tinha vao.
    _ty0=float(P.get('tray_y0',0.28)); _ty1=float(P.get('tray_y1',0.52))
    for sy in (1,-1):
        tr=box('Rear_Tray_'+('L' if sy>0 else 'R'),
               (float(P.get('tray_x',-0.500)), sy*(_ty0+_ty1)/2.0, float(P.get('tray_z',0.250))),
               (float(P.get('tray_lx',0.090)), (_ty1-_ty0)/2.0, float(P.get('tray_lz',0.095))),
               bevel=0.020, segs=3)
        assign(tr,P.get('tray_mat','M_Dark')); out.append(tr)
    for sy in (1,-1):
        a2=sweep('Front_Stub_'+('L' if sy>0 else 'R'),[(XF,sy*0.470,RF),(XF,sy*TYF,RF)],0.030,14); assign(a2,'M_Blue'); out.append(a2)
    for sy in (1,-1):
        st='L' if sy>0 else 'R'
        mg=sweep('Arm_'+st,[(XF,sy*0.30,RF),(XF-0.02,sy*TYF,RF)],0.026,12); assign(mg,'M_BlueDk'); out.append(mg)
        tr=sweep('Tie_'+st,[(0.300,sy*0.115,0.250),(XF,sy*0.520,RF)],0.018,12); assign(tr,'M_Silver'); out.append(tr)
        pd=box('Pedal_'+st,(0.880,sy*0.150,0.150),(0.030,0.050,0.058),bevel=0.010); assign(pd,'M_Pedal'); out.append(pd)
    sc=sweep('Steer_Col',[(P.get('sc_x0',0.340),0,0.410),(0.260,0,0.530),(P.get('sc_x1',0.185),0,0.650)],P.get('sc_r',0.030),16); assign(sc,'M_Silver'); out.append(sc)
    WX=P.get('sw_x',0.185); WZ=P.get('sw_z',0.655); WR=P.get('sw_r',0.115); WT=P.get('sw_tilt',0.040)
    sw=[(WX+0.03,0.0,WZ+0.02),(WX,0.0,WZ)]
    for i in range(29):
        a=2*math.pi*i/28.0
        sw.append((WX-WT*math.sin(a),WR*math.cos(a),WZ+WR*math.sin(a)))
    w1=sweep('Steer_Wheel',sw,P.get('sw_t',0.024),16); assign(w1,'M_Dark'); out.append(w1)
    st1=box('Seat_Base',(-0.060,0,0.348),(0.148,0.188,0.052),bevel=0.052,segs=5); assign(st1,'M_Dark'); out.append(st1)
    # ---- MAOS (luvas) e BOTAS: o concept tem luvas e botas pretas visiveis ----
    for sy in (1,-1):
        # luva na manopla do volante
        gl=revolve('Glove_'+('L' if sy>0 else 'R'),[(0.032,-0.040),(0.082,-0.036),(0.092,0.0),(0.082,0.036),(0.032,0.040)],
                   P.get('gl_x',0.160), P.get('gl_z',0.680), y0=sy*P.get('gl_y',0.105), seg=20)
        assign(gl,'M_Dark'); out.append(reg('glove'+('L' if sy>0 else 'R'),gl))
        # bota apoiada no pedal, a frente
        bt=box('Boot_'+('L' if sy>0 else 'R'),(0.905,sy*0.152,0.128),(0.105,0.052,0.070),bevel=0.020,segs=3)
        assign(bt,'M_Dark'); out.append(reg('boot'+('L' if sy>0 else 'R'),bt))
        # canela ligando joelho a bota
        cn=tubevar('Shin_'+('L' if sy>0 else 'R'),[(0.560,sy*0.150,0.300),(0.720,sy*0.150,0.215),(0.870,sy*0.151,0.165)],
                   [0.056,0.048,0.044],seg=16); assign(cn,'M_Blue'); out.append(cn)
    # ---- COIL-OVER: mola helicoidal dourada visivel a frente da roda traseira ----
    for sy in (1,-1):
        cxx, cyy, z0, z1 = XR+0.215, sy*0.168, 0.300, 0.610
        cd=sweep('Shock_Body_'+('L' if sy>0 else 'R'),[(cxx,cyy,z0),(cxx,cyy,z1)],0.026,14)
        assign(cd,'M_Silver'); out.append(cd)
        coil=[]; NT=44
        for k in range(NT+1):
            f=k/float(NT); ang=2*math.pi*5.0*f
            zz=z0+0.055+(z1-z0-0.115)*f
            coil.append((cxx+0.058*math.cos(ang), cyy+0.058*math.sin(ang), zz))
        sp=sweep('Shock_Spring_'+('L' if sy>0 else 'R'),coil,0.014,10)
        assign(sp,'M_Gold'); out.append(reg('spring'+('L' if sy>0 else 'R'),sp))

    # concha baixa e RECLINADA: sobe para tras em curva (nao e parede vertical)
    st2=tubevar('Seat_Shell',[(-0.150,0,0.368),(-0.234,0,0.432),(-0.322,0,0.500),(-0.412,0,0.560)],
                [0.170,0.196,0.208,0.196],seg=26); assign(st2,'M_Dark'); out.append(reg('seat',st2))
    for sy in (1,-1):
        spk=revolve('Sprocket_'+('L' if sy>0 else 'R'),[(0.014,-0.012),(0.160,-0.012),(0.160,0.012),(0.014,0.012)],XR-0.02,RR,y0=sy*0.215,seg=40)
        assign(spk,'M_Silver'); out.append(spk)
        sp=box('Spring_'+('L' if sy>0 else 'R'),(XR-0.10,sy*0.255,0.300),(0.048,0.048,0.080),bevel=0.016); assign(sp,'M_Silver'); out.append(sp)
        for zz in (0.262,0.300,0.338):
            rr=revolve('Ring_%s_%.3f'%('L' if sy>0 else 'R',zz),[(0.050,-0.008),(0.058,-0.008),(0.058,0.008),(0.050,0.008)],XR-0.10,zz,y0=sy*0.255,seg=24)
            assign(rr,'M_Gold'); out.append(rr)
    return join(out,'CH')
CH=safe('chassis',chassis)
if CH: made.append(CH)

# ============ 9. TRASEIRA: motor + 3 escapamentos + asa ALTA + difusor ============
def rear():
    out=[]
    exb=P.get('exh_x',XRE+0.041)
    EXC=P.get('eng_x',-0.430)          # motor colado atras do banco
    # ---- motor: caixa chanfrada, topo prata / base escura / tampa azul ----
    en=box('Engine',(EXC,0,0.585),(0.128,0.300,0.058),bevel=0.045,segs=5); assign(en,'M_Silver'); out.append(en)
    en2=box('Engine_Bot',(EXC,0,0.500),(0.120,0.292,0.036),bevel=0.026,segs=3); assign(en2,'M_Dark'); out.append(en2)
    ec=box('Engine_Top',(EXC+0.006,0,0.655),(0.112,0.272,0.030),bevel=0.024,segs=4); assign(ec,P.get('ecmat','M_Silver')); out.append(ec)
    # detalhe: tampa de vela (cilindro branco com furo escuro)
    pl=revolve('Plug',[(0.012,-0.032),(0.030,-0.032),(0.030,0.032),(0.012,0.032)],EXC,0.600,y0=0.302,seg=18)
    assign(pl,'M_White'); out.append(pl)
    ph=revolve('Plug_Hole',[(0.004,-0.022),(0.017,-0.022),(0.017,0.022),(0.004,0.022)],EXC,0.600,y0=0.330,seg=14)
    assign(ph,'M_Dark'); out.append(ph)
    for j in range(6):
        fin=box('Efin%d'%j,(EXC,-0.240+j*0.096,0.590),(0.108,0.018,0.026),bevel=0.004,segs=1)
        assign(fin,'M_Silver'); out.append(fin)
    # ---- AIRBOX/scoop atras do capacete (xf 0.72-0.80 no concept = 0.62H/0.53H) ----
    for j,(xx,zz,ry_,rz_) in enumerate([(-0.470,0.652,0.098,0.068),(-0.575,0.596,0.090,0.060),(-0.665,0.540,0.080,0.052)]):
        ab=box('Airbox%d'%j,(xx,0,zz),(0.058,ry_,rz_),bevel=0.020,segs=3); assign(ab,P.get('abmat','M_Silver')); out.append(reg('airbox%d'%j,ab))
    abt=sweep('Airbox_Duct',[(-0.462,0,0.774),(-0.575,0,0.704),(-0.668,0,0.628)],0.054,18)
    assign(abt,'M_BlueDk'); out.append(reg('airbox_duct',abt))
    # ---- 3 escapamentos: Z MEDIDO — o auditor poe rear/ESCAPES em z 0.54-0.75 m (faixa por z:
    # PARACH_BAIXO 0-0.30, DIFUSOR 0.30-0.54, ESCAPES 0.54-0.75, PILOTO_COSTAS 0.75-0.94).
    # Os tubos estavam em z 0.34-0.47 = dentro do DIFUSOR. exh_dz sobe o conjunto inteiro.
    _edz=P.get('exh_dz',0.0)
    e0=tube_round('Exh_C',[(EXC-0.16,0.0,0.340+_edz),(XR-0.20,0.0,0.382+_edz),(exb,0.0,0.412+_edz)],P.get('exh_c_r',0.128),26)
    assign(e0,'M_Silver')
    try:
        _d=V3((exb,0.0,0.412+_edz))-V3((XR-0.20,0.0,0.382+_edz)); _d.normalize()
        _t=V3((exb,0.0,0.412+_edz))
        _c=tube_round('ExhC_cut',[tuple(_t+_d*0.105),tuple(_t-_d*0.020)],0.074,22)
        e0=boolean(e0,_c,'DIFFERENCE')
        _q=V3((0.0,0.0,1.0)).rotation_difference(_d).to_matrix().to_4x4()
        _lip=revolve('ExhC_lip',[(0.074,0.004),(0.106,0.004),(0.106,0.026),(0.074,0.026)],0,0,seg=28)
        assign(_lip,'M_Silver'); _lip.data.transform(_q); _lip.data.transform(Matrix.Translation(tuple(_t-_d*0.026)))
        out.append(_lip)
        _bo=revolve('ExhC_floor',[(0.0,-0.010),(0.076,-0.010),(0.076,0.010),(0.0,0.010)],0,0,seg=26)
        assign(_bo,'M_Eye'); _bo.data.transform(_q); _bo.data.transform(Matrix.Translation(tuple(_t-_d*0.098)))
        out.append(_bo); R['exh_open_C']='ok'
    except Exception as _e: R['exh_open_C']=repr(_e)[:70]
    out.append(e0)
    b0=revolve('Exh_C_bore',[(0.0,-0.012),(0.056,-0.012),(0.056,0.012),(0.0,0.012)],0,0,seg=26); assign(b0,'M_Eye')
    b0.data.transform(Matrix.Rotation(math.radians(90),4,'Y'))
    b0.data.transform(Matrix.Translation((exb+0.020,0.0,0.412+_edz))); out.append(b0)
    for sy in (1,-1):
        st='L' if sy>0 else 'R'
        pt=((exb,sy*0.240,0.472+_edz),(XR-0.20,sy*0.185,0.420+_edz),(EXC-0.16,sy*0.110,0.392+_edz))
        ex=tube_round('Exh_'+st,list(pt)[::-1],0.080,26); assign(ex,'M_Silver')
        try:
            _t=V3((exb,sy*0.240,0.472+_edz)); _d=_t-V3((XR-0.20,sy*0.185,0.420+_edz)); _d.normalize()
            _c=tube_round('Exh'+st+'_cut',[tuple(_t+_d*0.100),tuple(_t-_d*0.020)],0.072,22)
            ex=boolean(ex,_c,'DIFFERENCE')
            _q=V3((0.0,0.0,1.0)).rotation_difference(_d).to_matrix().to_4x4()
            _lip=revolve('Exh'+st+'_lip',[(0.072,0.004),(0.104,0.004),(0.104,0.026),(0.072,0.026)],0,0,seg=28)
            assign(_lip,'M_Silver'); _lip.data.transform(_q); _lip.data.transform(Matrix.Translation(tuple(_t-_d*0.026)))
            out.append(_lip)
            _bo=revolve('Exh'+st+'_floor',[(0.0,-0.010),(0.074,-0.010),(0.074,0.010),(0.0,0.010)],0,0,seg=26)
            assign(_bo,'M_Eye'); _bo.data.transform(_q); _bo.data.transform(Matrix.Translation(tuple(_t-_d*0.094)))
            out.append(_bo); R['exh_open_'+st]='ok'
        except Exception as _e: R['exh_open_'+st]=repr(_e)[:60]
        out.append(ex)
        _d=V3((exb-(XR-0.20), sy*0.240-sy*0.185, 0.472-0.420)).normalized()
        bb=revolve('Exh_%s_bore'%st,[(0.0,-0.009),(0.068,-0.009),(0.068,0.009),(0.0,0.009)],0,0,seg=24); assign(bb,'M_Dark')
        bb.data.transform(_d.to_track_quat('Z','Y').to_matrix().to_4x4())
        bb.data.transform(Matrix.Translation((exb-0.004,sy*0.242,0.474+_edz))); out.append(bb)
    # caixa coletora com rebites atras dos 3 tubos
    cxs=box('Collector',(exb+0.200,0,0.432+_edz),(0.042,0.212,0.072),bevel=0.020,segs=2); assign(cxs,'M_Silver'); out.append(cxs)
    for j in range(4):
        rv=dome_dir('Rivet%d'%j,(exb+0.242,-0.150+j*0.100,0.432),0.020,(-1.0,0.0,0.0),seg=14,rings=8,flat=0.42)
        assign(rv,'M_Dark'); out.append(rv)
    # ---- coilover: amortecedor prata + mola DOURADA (quase vertical, junto ao banco) ----
    for sy in (1,-1):
        st='L' if sy>0 else 'R'
        dm=revolve('Damper_'+st,[(0.015,-0.070),(0.032,-0.070),(0.032,0.072),(0.015,0.072)],XR-0.010,0.352,y0=sy*0.238,seg=18)
        assign(dm,'M_Silver'); out.append(dm)
        ey=revolve('Eye_'+st,[(0.008,-0.020),(0.030,-0.020),(0.030,0.020),(0.008,0.020)],XR-0.010,0.432,y0=sy*0.238,seg=16)
        assign(ey,'M_Silver'); out.append(ey)
        for kk in range(6):
            spr=revolve('Coil_%s_%d'%(st,kk),[(0.034,-0.011),(0.054,-0.011),(0.054,0.011),(0.034,0.011)],
                        XR-0.010,0.300+kk*0.024,y0=sy*0.238,seg=24)
            assign(spr,'M_Gold'); out.append(spr)
    # ---- airbox/carenagem traseira alta: preenche 0.50-0.65 m em xf 0.80-0.87 ----
    ab=box('Airbox',(XRE+0.360,0,0.585),(0.100,0.118,0.078),bevel=0.032,segs=4); assign(ab,P.get('mufmat','M_Silver')); out.append(ab)
    ab2=box('Airbox_Top',(XRE+0.360,0,0.655),(0.082,0.094,0.030),bevel=0.016,segs=3); assign(ab2,P.get('muftmat','M_Silver')); out.append(ab2)
    for sy in (1,-1):
        sp=sweep('Airbox_Strut_'+('L' if sy>0 else 'R'),[(XRE+0.345,sy*0.078,0.596),(XRE+0.330,sy*0.090,0.430)],0.028,14)
        assign(sp,'M_Dark'); out.append(sp)
    # ---- difusor azul com 5 fendas verticais ----
    df=box('Diffuser',(XRE+P.get('dfx',0.200),0,P.get('dfz',0.152)),(P.get('dfc',0.060),0.170,P.get('dfh',0.130)),bevel=0.012,segs=3); assign(df,'M_Blue'); out.append(df)
    if P.get('ramp',1):
        _rs=[]
        _RX0=P.get('rx0',0.380); _RX1=P.get('rx1',0.020)
        _RZ0=P.get('rzb',0.100); _RZ1=P.get('rzt',0.480); _RT=P.get('rth',0.150)
        _RY=P.get('ryw',0.330)
        for _k in range(7):
            _t=_k/6.0
            _x=XRE+_RX0+(_RX1-_RX0)*_t
            _zb=_RZ0+(_RZ1-_RZ0)*_t
            _zt=_zb+_RT
            _rs.append([(_x,_RY,_zt),(_x,-_RY,_zt),(_x,-_RY,_zb),(_x,_RY,_zb)])
        rp=loft('Rear_Ramp',_rs); assign(rp,'M_Silver'); out.append(reg('ramp',rp))
    for j,yy in enumerate((-0.104,-0.052,0.0,0.052,0.104)):
        fn=box('Dslot%d'%j,(XRE+0.060,yy,0.152),(0.046,0.024,0.126),bevel=0.004,segs=1); assign(fn,'M_Dark'); out.append(fn)
    # ---- para-choque tubular prata em U ----
    _bl=[]
    for sy in (1,-1):
        # perna vertical descendo da barra ate o difusor
        _bl.append((XRE+0.135, sy*0.505, 0.288)); _bl.append((XRE+0.168, sy*0.492, 0.150)); _bl.append((XRE+0.190, sy*0.430, 0.070))
    _loop=[(XRE+0.262,0.400,0.150)]+[(XRE+0.235,0.470,0.152)]+[(_bl[0][0],_bl[0][1],_bl[0][2])] if False else []
    # U invertido: barra superior alta + 2 pernas verticais + travessa inferior (concept)
    _bx=XRE+0.010
    scr=[(_bx,0.268,P.get('rz0',0.078)),(_bx,0.268,P.get('rz1',0.598)),(_bx,0.130,P.get('rz1',0.598)+0.004),(_bx,0.0,P.get('rz1',0.598)+0.004),
         (_bx,-0.130,P.get('rz1',0.598)+0.004),(_bx,-0.268,P.get('rz1',0.598)),(_bx,-0.268,P.get('rz0',0.078))]
    rb=tube_round('Rear_Bumper_U',scr,0.042,22); assign(rb,'M_Silver'); out.append(reg('rbump',rb))
    bt=tube_round('Rear_Bumper_Bot',[(_bx,0.268,P.get('rbz',0.300)),(_bx,0.0,P.get('rbz',0.300)-0.008),(_bx,-0.268,P.get('rbz',0.300))],0.038,22)
    assign(bt,'M_Silver'); out.append(bt)
    _c=box('Rear_Clamps',(_bx,0.0,P.get('rbz',0.300)+0.012),(0.030,0.290,0.040),bevel=0.010,segs=2)
    assign(_c,'M_Dark'); out.append(_c)
    # ---- asa traseira: barra GROSSA azul-escura + endplates amarelos ----
    wz=P.get('wing_z',0.570)*H
    wx1=P.get('wing_x1',XRE-0.015); wx2=P.get('wing_x2',XRE+0.235)
    _WS=P.get('wing_span',0.505)
    if P.get('wing_tube',1):
        # TUBO cilindrico fino ao longo de Y (o concept e um tubo, nao uma laje)
        _wc=(wx1+wx2)/2.0
        _wr=P.get('wing_r',0.050)
        _wpts=[(_wc,-_WS,wz),(_wc,-_WS*0.5,wz+0.004),(_wc,0.0,wz+0.006),(_wc,_WS*0.5,wz+0.004),(_wc,_WS,wz)]
        wg=sweep('Wing_Main',_wpts,_wr,P.get('wing_seg',22)); assign(wg,'M_Blue'); out.append(reg('wing',wg))
    else:
        wsec=[]
        for i in range(13):
            u=i/12.0; x=wx1+(wx2-wx1)*u
            zc=wz+0.010*math.sin(math.pi*u)
            hh=P.get('wing_hh',0.075)+0.010*math.sin(math.pi*u)
            wsec.append([(x,_WS,zc+hh),(x,-_WS,zc+hh),(x,-_WS,zc-hh),(x,_WS,zc-hh)])
        wg=loft('Wing_Main',wsec); assign(wg,'M_Blue'); add_mod(wg,'BEVEL',width=0.016,segments=2); apply_mods(wg); out.append(reg('wing',wg))
    for sy in (1,-1):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.mesh.primitive_uv_sphere_add(segments=28,ring_count=16,radius=1.0)
        ep=bpy.context.object; ep.name='Wing_Endplate_'+('L' if sy>0 else 'R')
        _cs=P.get('cap_s',(0.085,0.042,0.085)); ep.scale=_cs
        bpy.ops.object.select_all(action='DESELECT'); ep.select_set(True)
        bpy.context.view_layer.objects.active=ep; bpy.ops.object.transform_apply(scale=True)
        _epx=((wx1+wx2)/2.0) if not P.get('wing_tube',1) else ((wx1+wx2)/2.0)
        _epy=(sy*0.492) if not P.get('wing_tube',1) else (sy*P.get('wing_span',0.505))
        ep.location=(_epx, _epy, wz)
        bpy.ops.object.select_all(action='DESELECT'); ep.select_set(True)
        bpy.context.view_layer.objects.active=ep; bpy.ops.object.transform_apply(location=True)
        assign(ep,'M_Yellow'); out.append(reg('wep_'+('L' if sy>0 else 'R'),ep))
        py=tube_round('Wing_Pylon_'+('L' if sy>0 else 'R'),[(wx1+0.075,sy*0.150,wz-0.030),(wx1+0.130,sy*0.150,0.512)],0.036,14)
        assign(py,'M_Dark'); out.append(py)
    return join(out,'REAR')
RE=safe('rear',rear)
if RE: made.append(RE)

# ============ 10. PILOTO: tronco barril, bracos grossos, pernas, capacete grande ============
def pilot():
    out=[]
    hx=P.get('helm_x',-0.298); hz=P.get('helm_z',0.985)
    HR=P.get('helm_r',0.210); SZ=P.get('helm_sz',0.934)
    # ---- colarinho (HANS) cobrindo a juncao pescoco/capacete ----
    col=revolve('Collar',[(0.152,-0.030),(0.186,-0.030),(0.186,0.030),(0.152,0.030)],hx+0.010,0.788,seg=34)
    assign(col,'M_Gasket'); out.append(col)
    # ---- tronco: barril curto e grosso, encostado no banco ----
    _TRS=P.get('trs',1.0)
    torso=tubevar('Torso',[(0.115,0,0.388),(0.050,0,0.474),(-0.045,0,0.566),(-0.150,0,0.652)],
                  [0.126*_TRS,0.145*_TRS,0.150*_TRS,0.132*_TRS],seg=26); assign(torso,'M_Pilot'); out.append(torso)
    belt=revolve('Belt',[(0.166,-0.024),(0.192,-0.024),(0.192,0.024),(0.166,0.024)],0.118,0.396,seg=32)
    assign(belt,'M_Yellow'); out.append(belt)
    # ---- ombros estreitos (capacete e mais largo que eles) ----
    _SHS=P.get('shs',1.0)
    sh=tubevar('Shoulders',[(-0.140,0.180,0.652),(-0.152,0.0,0.676),(-0.140,-0.180,0.652)],
               [0.070*_SHS,0.090*_SHS,0.070*_SHS],seg=22); assign(sh,'M_Pilot'); out.append(sh)
    for sy in (1,-1):
        st='L' if sy>0 else 'R'
        # PAD MEDIDO no FRONT: o concept em z 0.76-0.80 tem 3 runs (ombro 0.20..0.12 | cabeca 0.07..-0.07 |
        # ombro -0.11..-0.20) com VAO em |y| 0.07-0.12. Pad antigo (centro 0.162, r 0.098) ia ate |y| 0.064
        # e fechava o vao -> 1 run solido e excesso 23.8%. Pad novo: centro |y| 0.176, r 0.062 -> 0.114..0.238.
        pd=dome_dir('PAD_'+st,(-0.150,sy*P.get('pad_y',0.176),P.get('pad_z',0.694)),P.get('pad_r',0.062),(-0.28,sy*0.44,0.85),seg=26,rings=16,flat=0.44)
        assign(pd,'M_Yellow'); out.append(pd)
        # braco: ombro -> cotovelo -> mao NA MANOPLA do volante (sobreposto)
        arm=tubevar('Arm_'+st,[(-0.140,sy*0.175,0.652),(0.020,sy*0.196,0.626),(0.140,sy*0.160,0.594),(0.232,sy*0.112,0.566)],
                    [0.052,0.047,0.040,0.035],seg=20); assign(arm,'M_Pilot'); out.append(arm)
        gl=tubevar('Glove_'+st,[(0.238,sy*0.126,0.570),(0.246,sy*0.126,0.520)],[0.049,0.046],seg=20)
        assign(gl,'M_Dark'); out.append(gl)
        # perna: quadril -> joelho -> canela -> bota no pedal
        leg=tubevar('Leg_'+st,[(0.062,sy*0.142,0.392),(0.262,sy*0.180,0.470),(0.420,sy*0.184,0.412)],
                    [0.086,0.072,0.058],seg=22); assign(leg,'M_Pilot'); out.append(leg)
        bt=tubevar('Boot_'+st,[(0.420,sy*0.184,0.404),(0.540,sy*0.182,0.330),(0.628,sy*0.180,0.284)],
                   [0.062,0.054,0.045],seg=20); assign(bt,'M_Dark'); out.append(bt)
    # NECK MEDIDO no FRONT: o concept em z 0.76-0.80 tem run central de 0.07 m (meia-largura) —
    # e a propria esfera do capacete a essa altura. O pescoco estava com raio 0.140 (0.28 m de
    # diametro) e FECHAVA o vao |y| 0.07-0.11 entre a cabeca e os ombros (excesso 23.8% em
    # front/PILOTO e 23.7% em side/PILOTO). Raio correto = 0.070.
    nk=tubevar('Neck',[(-0.105,0,0.632),(-0.250,0,0.800)],[P.get('neck_r0',0.070),P.get('neck_r1',0.062)],seg=26); assign(nk,'M_Pilot'); out.append(nk)
    # HEADREST acolchoado em U atras do capacete (concept tem; auditor apontou ausencia)
    _hz2=hz-HR*0.34
    hrst=tube_round('Headrest_U',[(hx+HR*0.16, HR*0.92, _hz2),(hx-HR*0.62, HR*0.86, _hz2),
                                  (hx-HR*0.98, 0.0, _hz2),(hx-HR*0.62,-HR*0.86, _hz2),
                                  (hx+HR*0.16,-HR*0.92, _hz2)],0.042,18)
    assign(hrst,'M_Dark'); out.append(reg('headrest',hrst))
    # ---- capacete: mais LARGO que alto ----
    helm=dome('Helmet',hx,0.0,hz,HR,sz=SZ,sy=1.0,seg=104,rings=62); assign(helm,'M_Blue')
    def _h_ang(q):
        dx=q.center.x-hx; dy=q.center.y; dz=(q.center.z-hz)/SZ
        r=math.sqrt(dx*dx+dy*dy+dz*dz)
        if r<1e-9: return None
        return (math.degrees(math.acos(max(-1.0,min(1.0,dz/r)))), math.degrees(math.atan2(dy,dx)))
    def _intake(q):
        a=_h_ang(q)
        if a is None: return False
        th,ph=a
        return (((th-28.0)/5.0)**2 + (ph/10.0)**2 < 1.0)
    assign(helm,'M_Dark',_intake)
    out.append(reg('helmet',helm))
    # RESPIROS LATERAIS como geometria oval (o per-face num mesh de 3.4 graus vira bloco pixelado)
    for _sy in (1,-1):
        _st='L' if _sy>0 else 'R'
        _t=math.radians(62.0); _f=math.radians(_sy*76.0)
        _px=hx+HR*math.sin(_t)*math.cos(_f); _py=HR*math.sin(_t)*math.sin(_f); _pz=hz+HR*math.cos(_t)*SZ
        _d=V3((_px-hx,_py,(_pz-hz)/SZ)); _d.normalize()
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=14,radius=1.0)
        _ob=bpy.context.object; _ob.name='Vent_'+_st
        _ob.scale=(0.032,0.052,0.013)
        bpy.ops.object.transform_apply(scale=True)
        _ob.rotation_euler=_d.to_track_quat('Z','Y').to_euler()
        bpy.ops.object.transform_apply(rotation=True)
        _ob.location=(_px-_d.x*0.011,_py-_d.y*0.011,_pz-_d.z*0.011*SZ)
        bpy.ops.object.transform_apply(location=True)
        assign(_ob,'M_Dark'); out.append(reg('vent_'+_st,_ob))
    # ---- listra amarela central (frente-topo-nuca) ----
    Q=lambda RR,u,yy:(hx+RR*math.cos(u), yy, hz+RR*math.sin(u)*SZ)
    trim=[]
    for i in range(41):
        u=math.radians(19.0+221.0*i/40.0); tt=i/40.0
        w=0.106
        trim.append([Q(HR*1.006,u,w*0.52),Q(HR*1.006,u,-w*0.52),Q(HR*1.001,u,-w*0.52),Q(HR*1.001,u,w*0.52)])
    tr=loft('Helm_Trim',trim,cap=True); assign(tr,'M_Yellow'); out.append(reg('helm_trim',tr))
    PV=lambda RR,th,ph:(hx+RR*math.sin(th)*math.cos(ph), RR*math.sin(th)*math.sin(ph), hz+RR*math.cos(th)*SZ)
    def band(name,R1,R0,t0,t1,p0,p1,NT=14,NP=41):
        secs=[]
        for j in range(NP):
            ph=math.radians(p0+(p1-p0)*j/(NP-1.0)); sec=[]
            for i in range(NT):
                th=math.radians(t0+(t1-t0)*i/(NT-1.0)); sec.append(PV(R1,th,ph))
            for i in range(NT-1,-1,-1):
                th=math.radians(t0+(t1-t0)*i/(NT-1.0)); sec.append(PV(R0,th,ph))
            secs.append(sec)
        return loft(name,secs,cap=True)
    gk=band('Visor_Gasket',HR*1.008,HR*0.994,84,89,-89,89,10,91); assign(gk,'M_Gasket'); out.append(reg('gasket',gk))
    gk2=band('Visor_Gasket2',HR*1.008,HR*0.994,143,148,-89,89,10,91); assign(gk2,'M_Gasket'); out.append(reg('gasket',gk2))
    visb=band('Visor_Band',HR*1.010,HR*0.996,86,150,-89,89,40,109); assign(visb,'M_Visor'); out.append(reg('visor_band',visb))
    # ---- ROSTO: TEXTURA desenhada + UV (per-face em mesh de faces grandes nunca vira oval limpo) ----
    _T0,_T1,_P0,_P1=88.0,142.0,-78.0,78.0
    def _face_tex():
        TW,TH=640,256
        a=_np.zeros((TH,TW,4),dtype=_np.float32)
        for r in range(TH):
            k=1.0-0.30*(r/(TH-1.0))
            a[r,:,0]=0.46*k+0.09; a[r,:,1]=0.52*k+0.09; a[r,:,2]=0.60*k+0.08; a[r,:,3]=1.0
        yy,xx=_np.mgrid[0:TH,0:TW]
        def ell(cx,cy,rx,ry): return ((xx-cx)/rx)**2+((yy-cy)/ry)**2 < 1.0
        DU=(_P1-_P0)/TW; DV=(_T1-_T0)/TH
        def px(ph,th): return ((ph-_P0)/DU,(th-_T0)/DV)
        er=15.0
        for sgn in (-1.0,1.0):
            cx,cy=px(sgn*26.0,112.0); rx,ry=er/DU,er/DV
            a[ell(cx,cy,rx,ry)]=[0.975,0.975,0.975,1.0]
            a[ell(cx,cy+0.18*ry,rx*0.34,ry*0.34)]=[0.03,0.03,0.035,1.0]
            a[ell(cx-rx*0.30,cy-ry*0.30,rx*0.15,ry*0.15)]=[1.0,1.0,1.0,1.0]
            bx,by=px(sgn*25.0,96.0)
            b1=ell(bx,by,rx*1.02,ry*0.55); b2=ell(bx,by+ry*0.55,rx*1.02,ry*0.46)
            a[b1 & ~b2]=[0.03,0.03,0.035,1.0]
        return a,TW,TH
    _ft,_TW,_TH=_face_tex()
    _img=bpy.data.images.new('FaceTex',_TW,_TH,alpha=True)
    _img.pixels=_ft[::-1].ravel().tolist()
    _fmat=bpy.data.materials.get('M_Face')
    if not _fmat:
        _fmat=bpy.data.materials.new('M_Face'); _fmat.use_nodes=True
        _nt=_fmat.node_tree; _nt.nodes.clear()
        _o=_nt.nodes.new('ShaderNodeOutputMaterial'); _e=_nt.nodes.new('ShaderNodeEmission')
        _t=_nt.nodes.new('ShaderNodeTexImage'); _t.image=_img; _t.interpolation='Linear'
        _nt.links.new(_t.outputs['Color'],_e.inputs['Color']); _nt.links.new(_e.outputs['Emission'],_o.inputs['Surface'])
    _fv=[]; _NT2,_NP2=56,150
    for _j in range(_NP2):
        _ph=math.radians(_P0+(_P1-_P0)*_j/(_NP2-1.0))
        for _i in range(_NT2):
            _th=math.radians(_T0+(_T1-_T0)*_i/(_NT2-1.0))
            _fv.append(PV(HR*1.014,_th,_ph))
    _ff=[]
    for _j in range(_NP2-1):
        for _i in range(_NT2-1):
            _a=_j*_NT2+_i; _ff.append((_a,_a+1,_a+_NT2+1,_a+_NT2))
    _fme=bpy.data.meshes.new('Visor_Face_me'); _fme.from_pydata(_fv,[],_ff); _fme.update()
    _fob=bpy.data.objects.new('Visor_Face',_fme); bpy.context.scene.collection.objects.link(_fob)
    _fme.materials.append(_fmat)
    _uvl=_fme.uv_layers.new(name='UVMap')
    for _pi,_poly in enumerate(_fme.polygons):
        _jj=_pi//(_NT2-1); _ii=_pi%(_NT2-1)
        _uv=[(_jj/(_NP2-1.0),1.0-_ii/(_NT2-1.0)),(_jj/(_NP2-1.0),1.0-(_ii+1)/(_NT2-1.0)),
             ((_jj+1)/(_NP2-1.0),1.0-(_ii+1)/(_NT2-1.0)),((_jj+1)/(_NP2-1.0),1.0-_ii/(_NT2-1.0))]
        for _k,_li in enumerate(_poly.loop_indices): _uvl.data[_li].uv=_uv[_k]
    try:
        _sm=_fob.modifiers.new('sol','SOLIDIFY'); _sm.thickness=0.005; _sm.offset=0.0
        bpy.context.view_layer.objects.active=_fob; _fob.select_set(True); apply_mods(_fob)
    except Exception: pass
    out.append(_fob)
    # ---- queixeira/barbicheta: projeta para frente e para baixo, base achatada ----
    chinp=revolve('Chin_Guard',[(0.030,-0.052),(0.108,-0.052),(0.152,-0.026),(0.166,0.010),(0.152,0.044),(0.108,0.062),(0.030,0.062)],
                  hx+0.052, 0.842, seg=34)
    assign(chinp,'M_Yellow')
    chinp.scale=(1.0,1.0,0.80)
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=chinp; chinp.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    out.append(reg('chin_guard',chinp))
    chy=band('Chin_Patch',HR*1.018,HR*0.990,138,172,-50,50,20,57); assign(chy,'M_Yellow')
    def _hang(q):
        dx=q.center.x-hx; dy=q.center.y; dz=(q.center.z-hz)/SZ
        r=math.sqrt(dx*dx+dy*dy+dz*dz)
        if r<1e-9: return None
        return (math.degrees(math.acos(max(-1.0,min(1.0,dz/r)))), math.degrees(math.atan2(dy,dx)))
    def _mouth(pp):
        a3=_hang(pp)
        if a3 is None: return False
        th,ph=a3
        return abs(th-(158.0-0.0150*ph*ph))<2.2 and abs(ph)<22.0
    assign(chy,'M_Eye',_mouth); out.append(reg('chin_patch',chy))
    # base achatada (anel escuro na parte de baixo do casco)
    bse=revolve('Helm_Base',[(HR*0.62,-0.016),(HR*1.006,-0.016),(HR*1.006,0.016),(HR*0.62,0.016)],hx,hz-HR*SZ*0.90,seg=40)
    assign(bse,'M_Gasket'); out.append(reg('helm_base',bse))
    # ---- parafusos de pivo da viseira (laterais, altura da tempora) ----
    for sy in (1,-1):
        st='L' if sy>0 else 'R'
        th=math.radians(80.0); ph=math.radians(90.0*sy)
        ux=math.sin(th)*math.cos(ph); uy=math.sin(th)*math.sin(ph); uz=math.cos(th)
        bv=dome_dir('Bolt_'+st,(hx+HR*0.985*ux,HR*0.985*uy,hz+HR*0.985*uz*SZ),0.032,(ux,uy,uz),seg=20,rings=12,flat=0.45)
        assign(bv,'M_Dark'); out.append(bv)
    return join(out,'PL')
PI=safe('pilot',pilot)
if PI: made.append(PI)

R['QA']=QA; R['t_parts']=round(time.time()-t0,2)
g=box('Ground',(0,0,-0.040),(2.6,2.6,0.040),bevel=0.0); assign(g,'M_Floor')
# --- ACABAMENTO 'INFLADO': bevel POR PECA (global criava 355 non-manifold ao soldar)
_nbev=0
# DEBUG: bbox de cada parte (para nao chutar posicionamento)
try:
    import json as _j
    _d={}
    for _o in made:
        _c=[_o.matrix_world@Vector(v) for v in _o.bound_box]
        _d[_o.name]={"x":[round(min(q.x for q in _c),4),round(max(q.x for q in _c),4)],
                     "y":[round(min(q.y for q in _c),4),round(max(q.y for q in _c),4)],
                     "z":[round(min(q.z for q in _c),4),round(max(q.z for q in _c),4)]}
    R["part_bbox"]=_d
except Exception as _e:
    R["part_bbox_err"]=repr(_e)[:80]
_nss=0
if P.get('subsurf',0):
    _lv=int(P.get('subsurf_lv',1))
    for _o in made:
        if len(_o.data.vertices) < P.get('subsurf_min',120): continue
        try:
            _m=_o.modifiers.new('ss','SUBSURF'); _m.levels=_lv; _m.render_levels=_lv
            bpy.context.view_layer.objects.active=_o; apply_mods(_o); _nss+=1
        except Exception: pass
R['subsurf']=_nss
for _o in made:
    try:
        if len(_o.data.vertices) < P.get('bevel_minverts',999999): continue
        _b=_o.modifiers.new('pb','BEVEL')
        _b.width=P.get('bevel_w',0.018); _b.segments=P.get('bevel_seg',3)
        _b.limit_method='ANGLE'; _b.angle_limit=math.radians(P.get('bevel_ang',24.0))
        bpy.context.view_layer.objects.active=_o; apply_mods(_o); _nbev+=1
    except Exception: pass
R['bevel']='pecas_grandes=%d'%_nbev
_nsm=0
if P.get('smooth',1):
    _sa=math.radians(P.get('smooth_ang',38.0))
    for _o in made:
        try:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active=_o; _o.select_set(True)
            _ok=False
            try:
                bpy.ops.object.shade_auto_smooth(angle=_sa)
                apply_mods(_o)          # APLICA: sem isso o join descarta a suavizacao
                _ok=True
            except Exception:
                try:
                    bpy.ops.object.shade_smooth(); _ok=True
                except Exception: pass
            if _ok:
                try:
                    _o.data.update()
                except Exception: pass
            _nsm+=1
        except Exception: pass
R['smooth']='pecas_suavizadas=%d'%_nsm
if P.get('sep_parts',0):
    # T5 (skill concept-driven-3d-modeling): o join() final apaga a identidade das pecas e os
    # revisores convergem em "monolito / tudo fundido". Manter as pecas como OBJETOS SEPARADOS.
    FINS=list(made); R['sep_parts']=len(FINS)
else:
    FINS=[join(made,V+'_body')]
FIN=FINS[0]
# --- escala absoluta AUTO-CALIBRADA no comprimento-alvo (Hero Kart = 2.35 m) ---
_tl=P.get('target_length',0.0)
if _tl>0:
    _xs=[v.co.x for o in FINS for v in o.data.vertices]
    _cur=max(_xs)-min(_xs); _f=_tl/_cur
    for o in FINS: o.data.transform(Matrix.Diagonal((_f,_f,_f,1.0)))
    R['target_length']=_tl; R['scale_factor']=round(_f,5); R['len_before']=round(_cur,4)
_badn=0
for o in FINS:
    _b=[i for i,mm in enumerate(o.data.materials) if mm is None]
    for i in _b: o.data.materials[i]=MG.get('M_Dark')
    _badn+=len(_b)
R['none_slots']=_badn
# --- REPARO pos-bevel: dissolve as arestas non-manifold criadas pelo bevel ---
try:
    _rep=0
    for o in FINS:
        _bm=bm_of(o)
        _bad=[e for e in _bm.edges if not e.is_manifold]
        if _bad:
            bmesh.ops.dissolve_edges(_bm, edges=_bad, use_verts=False, use_face_split=False); _rep+=len(_bad)
        _bm.verts.ensure_lookup_table(); _bm.edges.ensure_lookup_table(); _bm.faces.ensure_lookup_table()
        bmesh.ops.recalc_face_normals(_bm, faces=list(_bm.faces))
        bm_done(_bm, o, True)
    if _rep: R['reparadas']=_rep
except Exception as e:
    R['reparo_err']=repr(e)[:90]
if len(FINS)==1:
    R['qa']=qa(FIN,exigir_manifold=True,min_pct_quads=60.0)
else:
    _mets={}; _ap=True
    for o in FINS:
        _q=qa(o,exigir_manifold=True,min_pct_quads=60.0)
        _mets.update(_q['metricas'])
        _ap=_ap and bool(_q.get('aprovado'))
    R['qa']={'aprovado':_ap,'falhas':[],'metricas':_mets}
R['verts']=sum(len(o.data.vertices) for o in FINS); R['n_parts']=len(FINS)
xl=[v.co.x for o in FINS for v in o.data.vertices]; zl=[v.co.z for o in FINS for v in o.data.vertices]; yl=[v.co.y for o in FINS for v in o.data.vertices]
R['x_range']=(round(min(xl),3),round(max(xl),3))
R['y_half']=round(max(abs(min(yl)),abs(max(yl))),3)
R['z_range']=(round(min(zl),3),round(max(zl),3))
R['L_over_H']=round((max(xl)-min(xl))/(max(zl)-min(zl)),3)
R['W_over_H']=round(2*max(abs(min(yl)),abs(max(yl)))/(max(zl)-min(zl)),3)
R['alvo_L_H']=round(L/H,3); R['alvo_W_H']=round(W/H,3)
# outline desativado: backface culling do EEVEE Next nao respeitou -> casca cobria o modelo
try:
    ee=bpy.context.scene.eevee
    for a,v in (('use_raytracing',True),('use_gtao',True),('use_shadows',True),('taa_render_samples',96)):
        if hasattr(ee,a): setattr(ee,a,v)
except Exception as e: R['eevee']=repr(e)[:80]
scene_setup(dist=4.2,look=(0,0,0.34),az=40.0,el=16.0)
w=bpy.context.scene.world
if w and w.use_nodes:
    bg=w.node_tree.nodes.get('Background')
    if bg: bg.inputs[0].default_value=(0.045,0.048,0.055,1.0); bg.inputs[1].default_value=1.0
bpy.context.scene.view_settings.view_transform='Standard'; bpy.context.scene.view_settings.exposure=P["exp"]
def plus_light(nm,loc,size,energy,col):
    ld=bpy.data.lights.new(nm,'AREA'); ld.size=size; ld.energy=energy; ld.color=col
    lo=bpy.data.objects.new(nm,ld); bpy.context.scene.collection.objects.link(lo); lo.location=loc
    lo.rotation_euler=(V3((0,0,0.45))-V3(loc)).to_track_quat('-Z','Y').to_euler(); return lo
plus_light('L_key',(3.4,-2.8,4.0),4.4,P["key"],(1.0,0.97,0.93))
plus_light('L_fill',(-3.0,-3.2,1.8),6.0,P["fill"],(0.86,0.91,1.0))
plus_light('L_rim',(-2.0,3.8,2.6),3.0,P["rim"],(0.95,0.97,1.0))
def cam(name,loc,rot,ortho=None,lens=55):
    cd=bpy.data.cameras.new(name); co=bpy.data.objects.new(name,cd)
    bpy.context.scene.collection.objects.link(co); co.location=loc; co.rotation_euler=rot
    if ortho: cd.type='ORTHO'; cd.ortho_scale=ortho
    else: cd.lens=lens
    return co
zc=0.62; OSC=2.42
for nm,loc,rot in [('front',(5.0,0,zc),(math.radians(90),0,math.radians(90))),('rear',(-5.0,0,zc),(math.radians(90),0,math.radians(-90))),
                   ('side',(0.0,5.0,zc),(math.radians(90),0,math.radians(180))),('top',(0,0,5.0),(0,0,math.radians(180)))]:
    bpy.context.scene.camera=cam('CAM_'+nm,loc,rot,ortho=OSC)
    render(os.path.join(OUTDIR,V.lower()+'-%s.png'%nm), w=860, h=860)
for nm,loc,dst,lk in [('isoF',(2.30,-2.30,1.75),3.6,0.42),('isoR',(-2.35,2.35,1.70),3.6,0.42),('head',(1.05,-0.85,1.32),1.95,1.00)]:
    look=V3((0,0,lk)); v=V3(loc).normalized()*dst
    cd=bpy.data.cameras.new('C_'+nm); cd.lens=75 if nm=='head' else 60
    co=bpy.data.objects.new('C_'+nm,cd); bpy.context.scene.collection.objects.link(co)
    co.location=v; co.rotation_euler=(look-v).to_track_quat('-Z','Y').to_euler()
    bpy.context.scene.camera=co
    render(os.path.join(OUTDIR,V.lower()+'-%s.png'%nm), w=880, h=660)
# --- passe de MASCARA (alpha puro, chao e luzes escondidos) ---
try:
    gf=bpy.data.objects.get('Ground')
    if gf: gf.hide_render=True
    for o in list(bpy.data.objects):
        if o.type=='LIGHT': o.hide_render=True
    if w and w.use_nodes:
        bg2=w.node_tree.nodes.get('Background')
        if bg2: bg2.inputs[1].default_value=0.0
    bpy.context.scene.render.film_transparent=True
    bpy.context.scene.render.image_settings.color_mode='RGBA'
    for nm,loc,rot in [('front',(5.0,0,zc),(math.radians(90),0,math.radians(90))),('rear',(-5.0,0,zc),(math.radians(90),0,math.radians(-90))),
                       ('side',(0.0,5.0,zc),(math.radians(90),0,math.radians(180))),('top',(0,0,5.0),(0,0,math.radians(180)))]:
        bpy.context.scene.camera=cam('MK_'+nm,loc,rot,ortho=OSC)
        render(os.path.join(OUTDIR,V.lower()+'m-%s.png'%nm), w=860, h=860)
    R['mask_ok']=True
    # ---- PASSADA PLANA (albedo-ish): comparacao de COR justa com o desenho ----
    # O concept e um desenho chato; o render beauty tem key/fill/rim + especular e
    # por construcao clareia a cor. Medir cor no beauty comparava a MINHA luz, nao
    # o modelo. Aqui: luzes desligadas e ambiente branco uniforme.
    if P.get('flat',1):
        for _o in list(bpy.data.objects):
            if _o.type=='LIGHT': _o.hide_render=True
        bpy.context.scene.render.film_transparent=False
        if w and w.use_nodes:
            _bg=w.node_tree.nodes.get('Background')
            if _bg:
                _bg.inputs[0].default_value=(1.0,1.0,1.0,1.0)
                _bg.inputs[1].default_value=P.get('flat_env',1.00)
        bpy.context.scene.render.image_settings.color_mode='RGB'
        for nm,loc,rot in [('front',(5.0,0,zc),(math.radians(90),0,math.radians(90))),('rear',(-5.0,0,zc),(math.radians(90),0,math.radians(-90))),
                           ('side',(0.0,5.0,zc),(math.radians(90),0,math.radians(180))),('top',(0,0,5.0),(0,0,math.radians(180)))]:
            bpy.context.scene.camera=cam('FLAT_'+nm,loc,rot,ortho=OSC)
            render(os.path.join(OUTDIR,V.lower()+'f-%s.png'%nm), w=860, h=860)
        R['flat_ok']=True
except Exception as e:
    R['mask_err']=repr(e)[:120]
save(V.lower()+'.blend')
R['elapsed_s']=round(time.time()-t0,2); R['ERRO']=traceback.format_exc()[-400:]

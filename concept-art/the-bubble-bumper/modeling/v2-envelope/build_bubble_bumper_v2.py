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
mat_rich('M_Yellow',(0.880,0.760,0.030),0.30,0.0,190,0.0022,0.55,0.25)
mat_rich('M_Blue',(0.045,0.120,0.330),0.32,0.0,190,0.0020,0.55,0.25)
mat_rich('M_BlueDk',(0.022,0.055,0.180),0.36,0.0,210,0.0022,0.50,0.15)
mat_rich('M_Dark',(0.030,0.030,0.034),0.70,0.0,340,0.0032,0.30,0.0)
mat_rich('M_Silver',(0.72,0.73,0.76),0.20,1.0,420,0.0012,0.60,0.0)
mat_rich('M_Visor',(0.36,0.45,0.58),0.30,0.18,600,0.0006,0.55,0.35)
mat_rich('M_Gasket',(0.020,0.020,0.024),0.78,0.0,340,0.0030,0.20,0.0)
mat_rich('M_Cushion',(0.055,0.21,0.60),0.48,0.0,240,0.0032,0.42,0.0)
mat_rich('M_Pilot',(0.050,0.125,0.440),0.44,0.0,200,0.0026,0.48,0.0)
mat_rich('M_Pedal',(0.22,0.22,0.24),0.54,1.0,300,0.0020,0.55,0.0)
mat_rich('M_Eye',(0.010,0.010,0.012),0.14,0.0,500,0.0006,0.90,0.4)
mat_rich('M_White',(0.96,0.96,0.96),0.20,0.0,400,0.0008,0.62,0.2)
mat_rich('M_Plate',(0.47,0.50,0.48),0.34,0.85,400,0.0014,0.62,0.0)
mat_rich('M_Gold',(0.72,0.55,0.13),0.28,1.0,380,0.0014,0.70,0.0)
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
def dome(name,cx,cy,cz,R,sz=1.0,sy=1.0,seg=40,rings=24):
    prof=[(max(0.0015,R*math.sin(math.pi*i/rings)*sy), -R*math.cos(math.pi*i/rings)*sz) for i in range(rings+1)]
    return revolve(name,prof,cx,cz,y0=cy,seg=seg,capopen=True)
def sq(cx,ry,rz,n=24,p=2.8,z0=0.0,zsq=0.90,cy=0.0):
    pts=[]
    for k in range(n):
        a=2*math.pi*k/n; ca=math.cos(a); sa=math.sin(a)
        y=math.copysign(abs(ca)**(2.0/p),ca)*ry; z=math.copysign(abs(sa)**(2.0/p),sa)*rz
        if z<0: z*=zsq
        pts.append((cx,cy+y,z0+z))
    return pts
def sqz(cx,cy,ry,rz,n=24,p=2.8,z0=0.0,zsq=0.90):
    return sq(cx,ry,rz,n,p,z0,zsq,cy)
def wheel_mesh(name,xc,yc,zc,R,hw,seg=48,flip=1):
    """roda de kart: pneu SLICK liso + disco solido (lip prata, prato cinza, anel amarelo,
    3 pinos quadrados amarelos a 120 graus, cubo central)"""
    prof=[(R*0.62,-hw*1.00),(R*0.80,-hw*1.00),(R*0.93,-hw*0.94),(R*0.995,-hw*0.78),
          (R*1.00,-hw*0.56),(R*0.985,-hw*0.34),(R*1.00,-hw*0.12),(R*0.985,0.0),
          (R*1.00,hw*0.12),(R*0.985,hw*0.34),(R*1.00,hw*0.56),(R*0.995,hw*0.78),
          (R*0.93,hw*0.94),(R*0.80,hw*1.00),(R*0.62,hw*1.00),
          (R*0.62,hw*0.80),(R*0.62,hw*0.00),(R*0.62,-hw*0.80)]
    t=revolve(name,prof,0,0,seg=seg); assign(t,'M_Dark')
    t.data.transform(Matrix.Rotation(math.radians(90),4,'X')); t.data.transform(Matrix.Translation((xc,yc,zc)))
    parts=[t]
    rp=[(R*0.09,-hw*0.88),(R*0.42,-hw*0.88),(R*0.58,-hw*0.82),(R*0.60,-hw*0.72),
        (R*0.60,hw*0.72),(R*0.58,hw*0.82),(R*0.42,hw*0.88),(R*0.09,hw*0.88),
        (R*0.09,hw*0.58),(R*0.09,0.0),(R*0.09,-hw*0.58)]
    rim=revolve(name+'_lip',rp,0,0,seg=max(24,seg//2)); assign(rim,'M_Silver')
    rim.data.transform(Matrix.Rotation(math.radians(90),4,'X')); rim.data.transform(Matrix.Translation((xc,yc,zc)))
    parts.append(rim)
    pl=[(R*0.09,-hw*0.70),(R*0.42,-hw*0.70),(R*0.50,-hw*0.66),(R*0.50,hw*0.66),(R*0.42,hw*0.70),(R*0.09,hw*0.70),
        (R*0.09,hw*0.44),(R*0.09,0.0),(R*0.09,-hw*0.44)]
    plate=revolve(name+'_plate',pl,0,0,seg=max(24,seg//2)); assign(plate,'M_Plate')
    plate.data.transform(Matrix.Rotation(math.radians(90),4,'X')); plate.data.transform(Matrix.Translation((xc,yc,zc)))
    parts.append(plate)
    ar=revolve(name+'_ring',[(R*0.335,-hw*0.72),(R*0.385,-hw*0.72),(R*0.385,-hw*0.66),(R*0.335,-hw*0.66),
                             (R*0.335,-hw*0.30),(R*0.335,0.0),(R*0.335,hw*0.30),
                             (R*0.335,hw*0.66),(R*0.385,hw*0.66),(R*0.385,hw*0.72),(R*0.335,hw*0.72)],0,0,seg=max(24,seg//2))
    assign(ar,'M_Yellow')
    ar.data.transform(Matrix.Rotation(math.radians(90),4,'X')); ar.data.transform(Matrix.Translation((xc,yc,zc)))
    parts.append(ar)
    for k in range(3):
        ang=2*math.pi*k/3.0+math.radians(30)
        pin=box(name+'_pin%d'%k,(0,0,0),(R*0.052,R*0.10*hw,R*0.052),bevel=0.004,segs=1)
        assign(pin,'M_Yellow')
        pin.data.transform(Matrix.Translation((xc+R*0.215*math.cos(ang), yc+flip*hw*0.74, zc+R*0.215*math.sin(ang))))
        parts.append(pin)
    hp=[(R*0.04,-hw*0.96),(R*0.155,-hw*0.96),(R*0.175,-hw*0.90),(R*0.175,hw*0.90),(R*0.155,hw*0.96),(R*0.04,hw*0.96),
        (R*0.04,hw*0.62),(R*0.04,0.0),(R*0.04,-hw*0.62)]
    hub=revolve(name+'_hub',hp,0,0,seg=26); assign(hub,'M_Plate')
    hub.data.transform(Matrix.Rotation(math.radians(90),4,'X')); hub.data.transform(Matrix.Translation((xc,yc,zc)))
    parts.append(hub)
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
def sweep(name,pts,r,seg=10,merge=0.002):
    o=tube(name,[tuple(p) for p in pts],r); c=curve_to_mesh(o)
    if c is not None: o=c
    if merge>0: seal(o,merge)
    return o
def box(name,center,size,bevel=0.02,segs=2):
    bpy.ops.mesh.primitive_cube_add(size=2,location=center)
    o=bpy.context.active_object; o.name=name; o.scale=size
    bpy.ops.object.transform_apply(scale=True)
    b=min(bevel,0.40*min(size))
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
XF=P.get('x_fw',+0.519); XR=P.get('x_rw',-0.653)
RF=P.get('r_f',0.186); RR=P.get('r_r',0.265)
HWF=P.get('hw_f',0.076); HWR=P.get('hw_r',0.212)
TYF=P.get('ty_f',0.626); TYR=P.get('ty_r',0.523)

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
        xf=0.02+0.24*(i/(NS-1.0))
        x=XFO-xf*L
        zt=min(prof_top(xf)*H*0.80, 0.395*H*max(0.58,min(1.0,(i/(NS-1.0))*2.0)))
        s=math.sin(math.pi*(0.06+0.90*(i/(NS-1.0))))**0.55
        ry=0.058+0.094*s
        zb=max(0.070,0.040*(1.0-i/(NS-1.0))+0.088)
        zc=(zb+zt)/2.0; rz=(zt-zb)/2.0
        secs.append(sq(x,ry,rz,28,6.0,z0=zc,zsq=0.97))
    o=loft('Nose',secs); assign(o,'M_Blue'); add_mod(o,'SUBSURF',levels=1); apply_mods(o); seal(o)
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
        yy=0.575*math.sin(a_)
        xx=(XFO-0.075) - 0.255*(1.0-math.cos(a_))
        spine.append((xx,yy))
    o=blade('Bumper_Blade',spine,rb*0.86,rb*0.70,zb)
    assign(o,'M_Blue')
    assign(o,'M_Yellow', lambda q: abs(q.center.y)>0.415)
    add_mod(o,'BEVEL',width=0.014,segments=2); apply_mods(o)
    out.append(reg('bumper',o))
    # painel central trapezoidal amarelo (rebaixado)
    cp=loft('Bumper_Center',[[(XFO-0.03,0.135,zb+0.105),(XFO-0.03,-0.135,zb+0.105),(XFO-0.03,-0.108,zb-0.055),(XFO-0.03,0.108,zb-0.055)],
                             [(XFO-0.15,0.130,zb+0.100),(XFO-0.15,-0.130,zb+0.100),(XFO-0.15,-0.104,zb-0.050),(XFO-0.15,0.104,zb-0.050)]])
    assign(cp,'M_Yellow'); out.append(reg('bump_center',cp))
    return join(out,'FBUMP')
FB=safe('front_bumper',front_bumper)
if FB: made.append(FB)

# ============ 3. GRADE INFERIOR com 5 aletas ============
def grille():
    out=[]
    gf=box('Grille_Frame',(XFO-0.44,0.0,0.148),(0.036,0.215,0.062),bevel=0.010,segs=2); assign(gf,'M_BlueDk'); out.append(gf)
    for j,yy in enumerate((-0.150,-0.075,0.0,0.075,0.150)):
        sl=box('Grille_Slat%d'%j,(XFO-0.468,yy,0.148),(0.022,0.016,0.048),bevel=0.003,segs=1); assign(sl,'M_Dark'); out.append(sl)
    return join(out,'GRILLE')
GR=safe('grille',grille)
if GR: made.append(GR)

# ============ 4. NASSAU PANEL + COWL (com banheira ESCAVADA de verdade) ============
def cowl():
    out=[]; NS=22; secs=[]
    for i in range(NS):
        xf=0.245+0.215*(i/(NS-1.0)); x=XFO-xf*L
        zt=prof_top(xf)*H
        if xf>0.365: zt=max(zt,0.500*H)
        s=math.sin(math.pi*(0.10+0.80*(i/(NS-1.0))))**0.5
        ry=0.148*s+0.042
        zb=0.105
        secs.append(sq(x,ry,(zt-zb)/2.0,32,4.4,z0=(zb+zt)/2.0,zsq=0.96))
    o=loft('Cowl',secs); assign(o,'M_Blue'); add_mod(o,'SUBSURF',levels=1); apply_mods(o); seal(o)
    # ESCAVA A BANHEIRA: subtrai um solido em forma de colher
    cut=box('Cockpit_Cut',(XFO-0.40*L,0,0.585),(0.330,0.200,0.130),bevel=0.065,segs=6)
    boolean(o,cut,'DIFFERENCE'); seal(o)
    try: bpy.data.objects.remove(cut,do_unlink=True)
    except Exception: pass
    out.append(reg('cowl',o))
    # nassau panel: lamina vertical a frente do volante
    ns=box('Nassau',(XFO-0.30*L-0.06,0,0.430),(0.026,0.118,0.130),bevel=0.014,segs=3)
    assign(ns,'M_Blue'); out.append(reg('nassau',ns))
    ns2=box('Nassau_Face',(XFO-0.30*L-0.093,0,0.452),(0.018,0.096,0.084),bevel=0.010,segs=2)
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
        secs.append(sq(x,ry,(zt-zb)/2.0,32,2.3,z0=(zb+zt)/2.0,zsq=0.95))
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
            t=i/(NS-1.0); xf=0.355+0.310*t; x=XFO-xf*L
            s=math.sin(math.pi*(0.05+0.90*t))**0.45
            outy=0.300+0.300*s      # borda externa: 0.30 -> 0.60
            iny=0.175+0.115*s       # borda interna
            zb=0.105
            zt=zb+0.150+0.130*s     # pod baixo: altura 0.15 -> 0.28
            cy=sy*(outy+iny)/2.0; ry=abs(outy-iny)/2.0
            # secao retangular-arredondada no plano YZ
            sec=[]
            for k in range(26):
                a=2*math.pi*k/26.0
                ca=math.cos(a); sa=math.sin(a)
                yy=cy+math.copysign(abs(ca)**(2.0/2.8),ca)*ry
                zz=(zb+zt)/2.0+math.copysign(abs(sa)**(2.0/2.8),sa)*(zt-zb)/2.0
                sec.append((x,yy,zz))
            secs.append(sec)
        o=loft(nm,secs); assign(o,'M_Yellow'); add_mod(o,'SUBSURF',levels=1); apply_mods(o); seal(o)
        csec=[]
        for i in range(NS):
            t=i/(NS-1.0); xf=0.355+0.310*t; x=XFO-xf*L
            sc=math.sin(math.pi*(0.05+0.90*t))**0.45
            oy=0.300+0.300*sc; iy=0.175+0.115*sc; zt=0.105+0.150+0.130*sc
            csec.append([(x,sy*iy,zt+0.003),(x,sy*oy,zt-0.010),(x,sy*oy,zt-0.052),(x,sy*iy,zt-0.045)])
        cap=loft(nm+'_Cap',csec); assign(cap,'M_Blue'); add_mod(cap,'SUBSURF',levels=1); apply_mods(cap)
        out.append(reg(nm+'_cap',cap))
        out.append(reg(nm,o))
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
    a1=sweep('Rear_Axle',[(XR,TYR,RR),(XR+0.02,0.0,RR+0.03),(XR,-TYR,RR)],0.042,16); assign(a1,'M_Blue'); out.append(a1)
    for sy in (1,-1):
        a2=sweep('Front_Stub_'+('L' if sy>0 else 'R'),[(XF,sy*0.470,RF),(XF,sy*TYF,RF)],0.030,14); assign(a2,'M_Blue'); out.append(a2)
    for sy in (1,-1):
        st='L' if sy>0 else 'R'
        mg=sweep('Arm_'+st,[(XF,sy*0.30,RF),(XF-0.02,sy*TYF,RF)],0.026,12); assign(mg,'M_BlueDk'); out.append(mg)
        tr=sweep('Tie_'+st,[(0.300,sy*0.115,0.250),(XF,sy*0.520,RF)],0.018,12); assign(tr,'M_Silver'); out.append(tr)
        pd=box('Pedal_'+st,(0.880,sy*0.150,0.150),(0.030,0.050,0.058),bevel=0.010); assign(pd,'M_Pedal'); out.append(pd)
    sc=sweep('Steer_Col',[(0.240,0,0.250),(0.360,0,0.585)],0.024,14); assign(sc,'M_Silver'); out.append(sc)
    sw=[(0.360,0.0,0.700),(0.360,0.0,0.585)]
    for i in range(29):
        a=2*math.pi*i/28.0; sw.append((0.360-0.014*math.cos(a),0.112*math.cos(a),0.585+0.112*math.sin(a)))
    w1=sweep('Steer_Wheel',sw,0.018,14); assign(w1,'M_Dark'); out.append(w1)
    st1=box('Seat_Base',(-0.075,0,0.352),(0.135,0.185,0.048),bevel=0.026,segs=3); assign(st1,'M_Dark'); out.append(st1)
    st2=box('Seat_Back',(-0.235,0,0.455),(0.052,0.185,0.130),bevel=0.030,segs=3); assign(st2,'M_Dark'); out.append(st2)
    st3=box('Seat_Head',(-0.258,0,0.598),(0.045,0.125,0.055),bevel=0.022,segs=3); assign(st3,'M_Dark'); out.append(st3)
    for sy in (1,-1):
        spk=revolve('Sprocket_'+('L' if sy>0 else 'R'),[(0.014,-0.012),(0.160,-0.012),(0.160,0.012),(0.014,0.012)],XR-0.02,RR,y0=sy*0.215,seg=40)
        assign(spk,'M_Silver'); out.append(spk)
        sp=box('Spring_'+('L' if sy>0 else 'R'),(XR-0.10,sy*0.255,0.300),(0.048,0.048,0.080),bevel=0.016); assign(sp,'M_Silver'); out.append(sp)
        for zz in (0.262,0.300,0.338):
            rr=revolve('Ring_%s_%.3f'%('L' if sy>0 else 'R',zz),[(0.050,-0.008),(0.058,-0.008),(0.058,0.008),(0.050,0.008)],XR-0.10,zz,y0=sy*0.255,seg=24)
            assign(rr,'M_Yellow'); out.append(rr)
    return join(out,'CH')
CH=safe('chassis',chassis)
if CH: made.append(CH)

# ============ 9. TRASEIRA: motor + 3 escapamentos + asa ALTA + difusor ============
def rear():
    out=[]
    exb=P.get('exh_x',XRE+0.041)
    EXC=P.get('eng_x',-0.430)          # motor colado atras do banco
    # ---- motor: caixa chanfrada, topo prata / base escura / tampa azul ----
    en=box('Engine',(EXC,0,0.372),(0.122,0.250,0.096),bevel=0.024,segs=3); assign(en,'M_Silver'); out.append(en)
    en2=box('Engine_Bot',(EXC,0,0.300),(0.114,0.238,0.034),bevel=0.010,segs=2); assign(en2,'M_Dark'); out.append(en2)
    ec=box('Engine_Top',(EXC+0.006,0,0.452),(0.108,0.226,0.028),bevel=0.012,segs=3); assign(ec,'M_Blue'); out.append(ec)
    # detalhe: tampa de vela (cilindro branco com furo escuro)
    pl=revolve('Plug',[(0.012,-0.032),(0.030,-0.032),(0.030,0.032),(0.012,0.032)],EXC,0.386,y0=0.235,seg=18)
    assign(pl,'M_White'); out.append(pl)
    ph=revolve('Plug_Hole',[(0.004,-0.022),(0.017,-0.022),(0.017,0.022),(0.004,0.022)],EXC,0.386,y0=0.262,seg=14)
    assign(ph,'M_Dark'); out.append(ph)
    for j in range(6):
        fin=box('Efin%d'%j,(EXC,-0.195+j*0.078,0.428),(0.102,0.016,0.022),bevel=0.004,segs=1)
        assign(fin,'M_Silver'); out.append(fin)
    # ---- 3 escapamentos calibres iguais: 1 central reto (mais baixo/frente) + 2 laterais p/ fora ----
    e0=sweep('Exh_C',[(EXC-0.16,0.0,0.340),(XR-0.20,0.0,0.382),(exb,0.0,0.412)],0.082,26)
    assign(e0,'M_Silver'); out.append(e0)
    b0=revolve('Exh_C_bore',[(0.0,-0.010),(0.070,-0.010),(0.070,0.010),(0.0,0.010)],0,0,seg=24); assign(b0,'M_Dark')
    b0.data.transform(Matrix.Rotation(math.radians(90),4,'Y'))
    b0.data.transform(Matrix.Translation((exb+0.014,0.0,0.412))); out.append(b0)
    for sy in (1,-1):
        st='L' if sy>0 else 'R'
        pt=((exb,sy*0.240,0.472),(XR-0.20,sy*0.185,0.420),(EXC-0.16,sy*0.110,0.392))
        ex=sweep('Exh_'+st,list(pt)[::-1],0.080,26); assign(ex,'M_Silver'); out.append(ex)
        _d=V3((exb-(XR-0.20), sy*0.240-sy*0.185, 0.472-0.420)).normalized()
        bb=revolve('Exh_%s_bore'%st,[(0.0,-0.009),(0.068,-0.009),(0.068,0.009),(0.0,0.009)],0,0,seg=24); assign(bb,'M_Dark')
        bb.data.transform(_d.to_track_quat('Z','Y').to_matrix().to_4x4())
        bb.data.transform(Matrix.Translation((exb-0.004,sy*0.242,0.474))); out.append(bb)
    # caixa coletora com rebites atras dos 3 tubos
    cxs=box('Collector',(exb+0.200,0,0.432),(0.042,0.212,0.072),bevel=0.010,segs=2); assign(cxs,'M_Silver'); out.append(cxs)
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
    # ---- difusor azul com 5 fendas verticais ----
    df=box('Diffuser',(XRE+0.145,0,0.132),(0.088,0.180,0.080),bevel=0.014,segs=3); assign(df,'M_Blue'); out.append(df)
    for j,yy in enumerate((-0.124,-0.062,0.0,0.062,0.124)):
        fn=box('Dslot%d'%j,(XRE+0.181,yy,0.132),(0.020,0.019,0.064),bevel=0.003,segs=1); assign(fn,'M_Dark'); out.append(fn)
    # ---- para-choque tubular prata em U ----
    rb=sweep('Rear_Bumper',[(XRE+0.255,0.415,0.152),(XRE+0.125,0.520,0.148),(XRE+0.075,0.0,0.142),(XRE+0.125,-0.520,0.148),(XRE+0.255,-0.415,0.152)],0.032,16)
    assign(rb,'M_Silver'); out.append(rb)
    # ---- asa traseira: barra GROSSA azul-escura + endplates amarelos ----
    wz=prof_top(0.94)*H
    wx1=XRE+0.223; wx2=XRE+0.390
    wsec=[]
    for i in range(13):
        u=i/12.0; x=wx1+(wx2-wx1)*u
        zc=wz+0.010*math.sin(math.pi*u)
        hh=0.017+0.005*math.sin(math.pi*u)
        wsec.append([(x,0.490,zc+hh),(x,-0.490,zc+hh),(x,-0.490,zc-hh),(x,0.490,zc-hh)])
    wg=loft('Wing_Main',wsec); assign(wg,'M_BlueDk'); add_mod(wg,'BEVEL',width=0.011,segments=2); apply_mods(wg); out.append(reg('wing',wg))
    for sy in (1,-1):
        ep=loft('Wing_Endplate_'+('L' if sy>0 else 'R'),
                [[(wx1+0.040,sy*0.490,wz-0.098),(wx2-0.010,sy*0.490,wz-0.080),(wx2-0.010,sy*0.490,wz+0.044),(wx1+0.040,sy*0.490,wz+0.036)],
                 [(wx1+0.040,sy*0.514,wz-0.098),(wx2-0.010,sy*0.514,wz-0.080),(wx2-0.010,sy*0.514,wz+0.044),(wx1+0.040,sy*0.514,wz+0.036)]])
        assign(ep,'M_Yellow'); out.append(reg('wep_'+('L' if sy>0 else 'R'),ep))
        py=sweep('Wing_Pylon_'+('L' if sy>0 else 'R'),[(wx1+0.055,sy*0.160,wz-0.014),(EXC+0.02,sy*0.160,0.486)],0.026,12)
        assign(py,'M_Dark'); out.append(py)
        ar=sweep('Wing_Strut_'+('L' if sy>0 else 'R'),[(wx1+0.070,sy*0.360,wz-0.020),(EXC+0.05,sy*0.352,0.348)],0.030,12)
        assign(ar,'M_BlueDk'); out.append(ar)
    return join(out,'REAR')
RE=safe('rear',rear)
if RE: made.append(RE)

# ============ 10. PILOTO: tronco barril, bracos grossos, pernas, capacete grande ============
def pilot():
    out=[]
    hx=P.get('helm_x',-0.272); hz=P.get('helm_z',0.996)
    HR=P.get('helm_r',0.206); SZ=P.get('helm_sz',0.879)
    # ---- colarinho fino (HANS) na base do capacete ----
    col=revolve('Collar',[(0.118,-0.032),(0.146,-0.032),(0.146,0.032),(0.118,0.032)],hx+0.026,0.812,seg=32)
    assign(col,'M_Gasket'); out.append(col)
    # ---- tronco: barril curto e grosso (chibi), leve inclinacao para frente ----
    torso=tubevar('Torso',[(0.125,0,0.386),(0.060,0,0.478),(-0.020,0,0.588),(-0.100,0,0.686)],
                  [0.158,0.180,0.184,0.162],seg=26); assign(torso,'M_Pilot'); out.append(torso)
    # ---- cinto amarelo na cintura ----
    belt=revolve('Belt',[(0.168,-0.024),(0.194,-0.024),(0.194,0.024),(0.168,0.024)],0.128,0.398,seg=32)
    assign(belt,'M_Yellow'); out.append(belt)
    # ---- ombros ESTREITOS (capacete e mais largo) ----
    sh=tubevar('Shoulders',[(-0.100,0.186,0.678),(-0.112,0.0,0.700),(-0.100,-0.186,0.678)],
               [0.078,0.098,0.078],seg=22); assign(sh,'M_Pilot'); out.append(sh)
    for sy in (1,-1):
        st='L' if sy>0 else 'R'
        # pastilha amarela no ombro
        pd=dome_dir('PAD_'+st,(-0.112,sy*0.166,0.714),0.094,(-0.30,sy*0.42,0.86),seg=26,rings=16,flat=0.46)
        assign(pd,'M_Yellow'); out.append(pd)
        # braco quase reto (150-160 graus) ate a manopla do volante
        arm=tubevar('Arm_'+st,[(-0.105,sy*0.180,0.664),(0.062,sy*0.192,0.630),(0.234,sy*0.156,0.604),(0.320,sy*0.112,0.586)],
                    [0.090,0.080,0.068,0.058],seg=20); assign(arm,'M_Pilot'); out.append(arm)
        gl=tubevar('Glove_'+st,[(0.320,sy*0.112,0.586),(0.382,sy*0.104,0.586)],[0.064,0.058],seg=20)
        assign(gl,'M_Dark'); out.append(gl)
        # perna: quadril -> joelho alto (~altura do cinto) -> canela -> bota
        leg=tubevar('Leg_'+st,[(0.100,sy*0.140,0.392),(0.302,sy*0.176,0.438),(0.468,sy*0.182,0.362)],
                    [0.132,0.114,0.096],seg=22); assign(leg,'M_Pilot'); out.append(leg)
        bt=tubevar('Boot_'+st,[(0.468,sy*0.182,0.354),(0.596,sy*0.180,0.262),(0.700,sy*0.178,0.202)],
                   [0.102,0.090,0.074],seg=20); assign(bt,'M_Dark'); out.append(bt)
    nk=tubevar('Neck',[(-0.148,0,0.688),(-0.196,0,0.816)],[0.128,0.108],seg=24); assign(nk,'M_Pilot'); out.append(nk)
    # ---- capacete: mais LARGO que alto ----
    helm=dome('Helmet',hx,0.0,hz,HR,sz=SZ,sy=1.0,seg=64,rings=38); assign(helm,'M_Blue')
    def _h_ang(q):
        dx=q.center.x-hx; dy=q.center.y; dz=(q.center.z-hz)/SZ
        r=math.sqrt(dx*dx+dy*dy+dz*dz)
        if r<1e-9: return None
        return (math.degrees(math.acos(max(-1.0,min(1.0,dz/r)))), math.degrees(math.atan2(dy,dx)))
    def _intake(q):
        a=_h_ang(q)
        if a is None: return False
        th,ph=a
        return ((abs(th-62.0)<9.0) and (abs(abs(ph)-76.0)<14.0)) or ((abs(th-28.0)<4.0) and (abs(ph)<12.0))
    assign(helm,'M_Dark',_intake)
    out.append(reg('helmet',helm))
    # ---- listra amarela central (frente-topo-nuca) ----
    Q=lambda RR,u,yy:(hx+RR*math.cos(u), yy, hz+RR*math.sin(u)*SZ)
    trim=[]
    for i in range(41):
        u=math.radians(50.0+160.0*i/40.0); tt=i/40.0
        w=0.090*min(1.0, math.sin(math.pi*min(1.0,max(0.0,(tt-0.01)/0.13)))**0.6 if tt<0.15 else 1.0)*min(1.0, math.sin(math.pi*min(1.0,max(0.0,(0.99-tt)/0.13)))**0.6 if tt>0.85 else 1.0)
        w=max(w,0.013)
        trim.append([Q(HR*1.005,u,w),Q(HR*1.005,u,-w),Q(HR*0.988,u,-w),Q(HR*0.988,u,w)])
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
    gk=band('Visor_Gasket',HR*1.016,HR*0.986,38,136,-92,92,20,61); assign(gk,'M_Gasket'); out.append(reg('gasket',gk))
    # ---- ROSTO: casca frontal com materiais POR-FACE (olhos, sobrancelhas, sorriso em U) ----
    _T0,_T1,_P0,_P1=44.0,164.0,-80.0,80.0
    def _hang(q):
        dx=q.center.x-hx; dy=q.center.y; dz=(q.center.z-hz)/SZ
        r=math.sqrt(dx*dx+dy*dy+dz*dz)
        if r<1e-9: return None
        return (math.degrees(math.acos(max(-1.0,min(1.0,dz/r)))), math.degrees(math.atan2(dy,dx)))
    fb=band('Visor_Face',HR*P.get('face_ro',1.020),HR*P.get('face_ri',1.013),_T0,_T1,_P0,_P1,72,200)
    assign(fb,'M_Visor')
    assign(fb,'M_Yellow', lambda q: (_hang(q) is not None) and _hang(q)[0]>=132.0)
    epc=P.get('eye_ph',17.0); epr=P.get('eye_pr',17.5); etc=P.get('eye_th',88.0)
    def _dec(kind):
        def f(pp):
            a2=_hang(pp)
            if a2 is None: return False
            th,ph=a2
            if kind=='s':
                return abs(th-(150.0-0.0260*ph*ph))<2.2 and abs(ph)<23.0
            for sgn in (1,-1):
                dth=th-etc; dph=ph-sgn*epc
                d=math.sqrt(dth*dth+dph*dph)
                if kind=='w' and d<=epr: return True
                if kind=='p' and d<=epr*0.56: return True
                if kind=='b' and (etc-epr-11.0)<=th<=(etc-epr-3.5) and abs(ph-sgn*epc)<=epr*1.05: return True
            return False
        return f
    assign(fb,'M_White',_dec('w'))
    assign(fb,'M_Eye',_dec('p'))
    assign(fb,'M_Eye',_dec('b'))
    assign(fb,'M_Eye',_dec('s'))
    out.append(reg('face',fb))
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
FIN=join(made,V+'_body')
# --- escala absoluta AUTO-CALIBRADA no comprimento-alvo (Hero Kart = 2.35 m) ---
_tl=P.get('target_length',0.0)
if _tl>0:
    _xs=[v.co.x for v in FIN.data.vertices]
    _cur=max(_xs)-min(_xs); _f=_tl/_cur
    FIN.data.transform(Matrix.Diagonal((_f,_f,_f,1.0)))
    R['target_length']=_tl; R['scale_factor']=round(_f,5); R['len_before']=round(_cur,4)
bad=[i for i,mm in enumerate(FIN.data.materials) if mm is None]
for i in bad: FIN.data.materials[i]=MG.get('M_Dark')
R['none_slots']=len(bad)
R['qa']=qa(FIN,exigir_manifold=True,min_pct_quads=60.0)
R['verts']=len(FIN.data.vertices); R['n_parts']=len(made)
xl=[v.co.x for v in FIN.data.vertices]; zl=[v.co.z for v in FIN.data.vertices]; yl=[v.co.y for v in FIN.data.vertices]
R['x_range']=(round(min(xl),3),round(max(xl),3))
R['y_half']=round(max(abs(min(yl)),abs(max(yl))),3)
R['z_range']=(round(min(zl),3),round(max(zl),3))
R['L_over_H']=round((max(xl)-min(xl))/(max(zl)-min(zl)),3)
R['W_over_H']=round(2*max(abs(min(yl)),abs(max(yl)))/(max(zl)-min(zl)),3)
R['alvo_L_H']=round(L/H,3); R['alvo_W_H']=round(W/H,3)
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
except Exception as e:
    R['mask_err']=repr(e)[:120]
save(V.lower()+'.blend')
R['elapsed_s']=round(time.time()-t0,2); R['ERRO']=traceback.format_exc()[-400:]

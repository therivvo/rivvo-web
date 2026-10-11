import json, os
BASE=json.load(open("/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/BASE_PARAMS.json"))
SRC=open("/tmp/bb25.py").read()
old="        zt=prof_top(xf)*H*0.88"
new=("        _k0=P.get('nose_top_k',0.88); _k1=P.get('nose_top_k2',1.00)\n"
     "        _u=max(0.0,min(1.0,(xf-P.get('nose_k_x0',0.10))/P.get('nose_k_ramp',0.06)))\n"
     "        zt=prof_top(xf)*H*(_k0+(_k1-_k0)*_u)")
assert old in SRC, "patch do nariz nao encontrou o alvo"
SRC=SRC.replace(old,new,1)

# patch 2: endplate com parametro PROPRIO (cap_s e compartilhado com o capacete)
old2="        _cs=P.get('cap_s',(0.085,0.042,0.085)); ep.scale=_cs"
new2="        _cs=P.get('ep_s',P.get('cap_s',(0.085,0.042,0.085))); ep.scale=_cs"
if old2 in SRC:
    SRC=SRC.replace(old2,new2,1)

# patch 3: airbox com meia-largura x parametrizavel (0.058 faz as 3 caixas se SOBREPOREM -> barra solida)
old3="ab=box('Airbox%d'%j,(xx,0,zz),(0.058,ry_,rz_),bevel=0.020,segs=3)"
new3="ab=box('Airbox%d'%j,(xx,0,zz),(P.get('ab_x',0.058),ry_,rz_),bevel=0.020,segs=3)"
if old3 in SRC:
    SRC=SRC.replace(old3,new3,1)

# patch 4: Airbox_Duct com deslocamento z e raio parametrizaveis (o duct em z 0.774 fecha o vao que o
# concept deixa aberto em imagem 0.69-0.73 na linha t 0.66)
old4="abt=sweep('Airbox_Duct',[(-0.462,0,0.774),(-0.575,0,0.704),(-0.668,0,0.628)],0.054,18)"
new4="abt=sweep('Airbox_Duct',[(-0.462,0,0.774+P.get('abt_dz',0.0)),(-0.575,0,0.704+P.get('abt_dz',0.0)),(-0.668,0,0.628+P.get('abt_dz',0.0))],P.get('abt_r',0.054),18)"
if old4 in SRC:
    SRC=SRC.replace(old4,new4,1)

# patch 5: encurtamento dos escapamentos em x (os 3 tubos diferem em Y e se projetam no MESMO x na vista
# lateral -> fundem num run continuo; o concept deixa -0.66..-0.92 VAZIO em z~0.62)
old5="    exb=P.get('exh_x',XRE+0.041)"
new5="    exb=P.get('exh_x',XRE+0.041)+P.get('exh_short',0.0)"
if old5 in SRC:
    SRC=SRC.replace(old5,new5,1)

# patch 6: escapamentos L/R encurtados em X (o CENTRAL mantem o extremo exb -> x_range preservado).
# Os L/R diferem do central so em Y, entao na vista lateral projetam no MESMO x e fundem num run continuo;
# o concept deixa x -0.66..-0.92 vazio em z~0.62.
old6="        pt=((exb,sy*0.240,0.472+_edz),(XR-0.20,sy*0.185,0.420+_edz),(EXC-0.16,sy*0.110,0.392+_edz))"
new6="        _lr=P.get('exh_lr_short',0.0); pt=((exb+_lr,sy*0.240,0.472+_edz),(XR-0.20+_lr*0.5,sy*0.185,0.420+_edz),(EXC-0.16,sy*0.110,0.392+_edz))"
if old6 in SRC:
    SRC=SRC.replace(old6,new6,1)

# patch 7: DUCT com deslocamento em X (o duct ocupa x -0.582..-0.690 = exatamente o vao1 do concept em t0.54)
old7="abt=sweep('Airbox_Duct',[(-0.462,0,0.774+P.get('abt_dz',0.0)),(-0.575,0,0.704+P.get('abt_dz',0.0)),(-0.668,0,0.628+P.get('abt_dz',0.0))],P.get('abt_r',0.054),18)"
new7="abt=sweep('Airbox_Duct',[(-0.462,0,0.774+P.get('abt_dz',0.0)),(-0.575+P.get('abt_dx',0.0)*0.5,0,0.704+P.get('abt_dz',0.0)),(-0.668+P.get('abt_dx',0.0),0,0.628+P.get('abt_dz',0.0))],P.get('abt_r',0.054),18)"
if old7 in SRC:
    SRC=SRC.replace(old7,new7,1)

# patch 8: hastes (Airbox_Strut / Wing_Pylon) encurtadas para baixo — elas se fundem com a asa em z
old8a="sp=sweep('Airbox_Strut_'+('L' if sy>0 else 'R'),[(XRE+0.345,sy*0.078,0.596),(XRE+0.330,sy*0.090,0.430)],0.028,14)"
new8a="sp=sweep('Airbox_Strut_'+('L' if sy>0 else 'R'),[(XRE+0.345,sy*0.078,0.596+P.get('strut_dz',0.0)),(XRE+0.330,sy*0.090,0.430)],0.028,14)"
if old8a in SRC:
    SRC=SRC.replace(old8a,new8a,1)

# patch 9: Airbox de x -0.830 (o box 'Airbox' com half-extent 0.100 HARDCODED) — ocupa vao2 inteiro em t0.54
old9="ab=box('Airbox',(XRE+0.360,0,0.585),(0.100,0.118,0.078),bevel=0.032,segs=4)"
new9="ab=box('Airbox',(XRE+0.360+P.get('ab2_dx',0.0),0,0.585),(P.get('ab2_x',0.100),0.118,0.078),bevel=0.032,segs=4)"
if old9 in SRC:
    SRC=SRC.replace(old9,new9,1)

# patch 10: frente dos escapamentos em X (o material em -0.77..-0.84 e o residuo do vao t0.54)
old10a="ex= tube_round('Exh_C',[(EXC-0.16,0,0.340+P.get('exh_dz',0.130))"
if old10a in SRC:
    pass

old9b="ab2=box('Airbox_Top',(XRE+0.360,0,0.655),(0.082,0.094,0.030),bevel=0.016,segs=3)"
new9b="ab2=box('Airbox_Top',(XRE+0.360+P.get('ab2_dx',0.0),0,0.655),(P.get('ab2_x2',0.082),0.094,0.030),bevel=0.016,segs=3)"
if old9b in SRC:
    SRC=SRC.replace(old9b,new9b,1)
# patch 10: frente dos escapamentos em X (residuo do vao t0.54 em -0.77..-0.84)
old10a="tube_round('Exh_C',[(EXC-0.16,0.0,0.340+_edz),(XR-0.20,0.0,0.382+_edz),(exb,0.0,0.412+_edz)]"
new10a="tube_round('Exh_C',[(EXC-0.16+P.get('exh_fx',0.0),0.0,0.340+_edz),(XR-0.20,0.0,0.382+_edz),(exb,0.0,0.412+_edz)]"
if old10a in SRC:
    SRC=SRC.replace(old10a,new10a,1)
old10b="(EXC-0.16,sy*0.110,0.392+_edz)"
new10b="(EXC-0.16+P.get('exh_fx',0.0),sy*0.110,0.392+_edz)"
if old10b in SRC:
    SRC=SRC.replace(old10b,new10b,1)
# patch 11: z PROPRIO do escapamento CENTRAL (desacopla do exh_dz global que baixa os 3 juntos)
old11a="(EXC-0.16+P.get('exh_fx',0.0),0.0,0.340+_edz),(XR-0.20,0.0,0.382+_edz),(exb,0.0,0.412+_edz)"
new11a="(EXC-0.16+P.get('exh_fx',0.0),0.0,0.340+_edz+P.get('exh_c_dz',0.0)),(XR-0.20,0.0,0.382+_edz+P.get('exh_c_dz',0.0)),(exb,0.0,0.412+_edz+P.get('exh_c_dz',0.0))"
if old11a in SRC:
    SRC=SRC.replace(old11a,new11a,1)
# patch 12: RAIO proprio dos escapamentos L/R (o topo 0.667 e o ocupante da banda -0.77..-0.84)
old12="d('Exh_'+st,list(pt)[::-1],0.080,26)"
new12="d('Exh_'+st,list(pt)[::-1],P.get('exh_lr_r',0.080),26)"
if old12 in SRC:
    SRC=SRC.replace(old12,new12,1)
# patch 13: Z proprio dos escapamentos L/R (unica alavanca com efeito PROVADO na banda -0.77..-0.84)
old13a="0.472+_edz)"
new13a="0.472+_edz+P.get('exh_lr_dz',0.0))"
if old13a in SRC:
    SRC=SRC.replace(old13a,new13a,1)
old13b="0.420+_edz)"
new13b="0.420+_edz+P.get('exh_lr_dz',0.0))"
if old13b in SRC:
    SRC=SRC.replace(old13b,new13b,1)
old13c="sy*0.110,0.392+_edz)"
new13c="sy*0.110,0.392+_edz+P.get('exh_lr_dz',0.0))"
if old13c in SRC:
    SRC=SRC.replace(old13c,new13c,1)
# patch 14: TRANSLACAO RIGIDA em X pos-escala (compensa deslocamento do x_range sem tocar comprimento/z_range)
old14="    R['target_length']=_tl"
new14="""    _xt=P.get('xtrans',0.0)
    if _xt:
        for o in FINS: o.data.transform(Matrix.Translation((_xt,0.0,0.0)))
    R['xtrans']=_xt
    R['target_length']=_tl"""
if old14 in SRC:
    SRC=SRC.replace(old14,new14,1)
# patch 15: DELECAO controlada por material+faixa, ANTES do passe de mascara canonico
old15="# --- passe de MASCARA"
new15="""# --- DELECAO CONTROLADA (patch 15): esconde faces por material e faixa, no pipeline canonico ---
_dm=P.get('del_mat'); _dz=P.get('del_z'); _dx=P.get('del_x')
if _dm and _dz and _dx:
    import bmesh as _bm
    _n=0
    for _o in FINS:
        if _o.type!='MESH': continue
        _ms=[m.name for m in _o.data.materials]
        if _dm not in _ms: continue
        _i=_ms.index(_dm)
        _b=_bm.new(); _b.from_mesh(_o.data); _b.faces.ensure_lookup_table()
        _k=[]
        for _f in _b.faces:
            if _f.material_index!=_i: continue
            _zs=[_v.co.z for _v in _f.verts]; _xs=[_v.co.x for _v in _f.verts]
            if min(_zs)<=_dz[1] and max(_zs)>=_dz[0] and min(_xs)>=_dx[0] and max(_xs)<=_dx[1]:
                _k.append(_f)
        if _k:
            _bm.ops.delete(_b, geom=_k, context='FACES'); _b.to_mesh(_o.data); _n+=len(_k)
        _b.free()
    R['del_mat']=_dm; R['del_n']=_n
# --- passe de MASCARA"""
if old15 in SRC:
    SRC=SRC.replace(old15,new15,1)
# patch 16: Z do pilar da asa (Wing_Pylon_L/R) — OCUPANTE PROVADO da banda t0.54 (W487)
old16a="[(wx1+0.075,sy*0.150,wz-0.030),(wx1+0.130,sy*0.150,0.512)]"
new16a="[(wx1+0.075,sy*0.150,wz-0.030),"       "(wx1+0.130,sy*0.150,0.512+P.get('pyl_dz',0.0))]"
if old16a in SRC:
    SRC=SRC.replace(old16a,new16a,1)
# patch 17: topo do pilar da asa (ponto ALTO, que vem de wz=wing_z*H) — a alavanca correta
old17="[(wx1+0.075,sy*0.150,wz-0.030),"
new17="[(wx1+0.075,sy*0.150,wz-0.030+P.get('pyl_dz2',0.0)),"
if old17 in SRC:
    SRC=SRC.replace(old17,new17,1)
# patch 18: frente do cowl em x (perfil: concept pica em x=0.328, modelo em x=0.210)
old18="xf=0.225+0.235*(i/(NS-1.0)); x=XFO-xf*L"
new18="xf=P.get('cowl_xf0',0.225)+0.235*(i/(NS-1.0)); x=XFO-xf*L"
if old18 in SRC:
    SRC=SRC.replace(old18,new18,1)
# patch 19: ponta TRASEIRA do escapamento central em z (so o ultimo ponto; o medio em x=-0.864 fica)
old19="(exb,0.0,0.412+_edz)]"
new19="(exb,0.0,0.412+_edz+P.get('exh_tip_dz',0.0))]"
if old19 in SRC:
    SRC=SRC.replace(old19,new19,1)
# patch 20: fator do topo do cowl (compensa o encolhimento do SUBSURF levels=1)
old20="zt=prof_top(xf)*H*0.97"
new20="zt=prof_top(xf)*H*P.get('cowl_k',0.97)"
if old20 in SRC:
    SRC=SRC.replace(old20,new20,1)
# patch 21: z do Cockpit_Cut (o aro do recorte forma o pico de t0.40)
old21="cut=box('Cockpit_Cut',(XFO-0.452*L,0,0.640),(0.232,0.150,0.116)"
new21="cut=box('Cockpit_Cut',(XFO-0.452*L,0,0.640+P.get('ch_top_dz',0.0)),(0.232,0.150,0.116)"
if old21 in SRC:
    SRC=SRC.replace(old21,new21,1)
# patch 22: DIAGNOSTICO do slot None (quem vira M_Dark silenciosamente)
old22="""_b=[i for i,mm in enumerate(o.data.materials) if mm is None]
    for i in _b: o.data.materials[i]=MG.get('M_Dark')
    _badn+=len(_b)"""
new22="""_b=[i for i,mm in enumerate(o.data.materials) if mm is None]
    _wm=[o.matrix_world@v.co for v in o.data.vertices]
    if _b:
        _fz=[]; _fx=[]
        for f in o.data.polygons:
            if f.material_index in _b:
                for vi in f.vertices:
                    v=o.matrix_world@o.data.vertices[vi].co; _fz.append(v.z); _fx.append(v.x)
        print('NONE piece=%s slots=%s nf=%d bbox_z[%.3f,%.3f] bbox_x[%.3f,%.3f] | facesNone x[%.3f,%.3f] z[%.3f,%.3f]'%(
            o.name,_b,sum(1 for f in o.data.polygons if f.material_index in _b),
            min(v.z for v in _wm),max(v.z for v in _wm),min(v.x for v in _wm),max(v.x for v in _wm),
            min(_fx) if _fx else 0,max(_fx) if _fx else 0,min(_fz) if _fz else 0,max(_fz) if _fz else 0))
    for i in _b: o.data.materials[i]=MG.get('M_Dark')
    _badn+=len(_b)"""
if old22 in SRC:
    SRC=SRC.replace(old22,new22,1)
# patch 23: DIAGNOSTICO das faces M_Dark por peca (bbox) — achar o ocupante de t0.40
anchor="R['none_slots']=_badn"
new23="""R['none_slots']=_badn
print('===== DIAG M_DARK por peca =====')
for o in FINS:
    _mi=[i for i,mm in enumerate(o.data.materials) if mm and mm.name=='M_Dark']
    if not _mi: continue
    _fz=[]; _fx=[]
    for f in o.data.polygons:
        if f.material_index in _mi:
            for vi in f.vertices:
                v=o.matrix_world@o.data.vertices[vi].co; _fz.append(v.z); _fx.append(v.x)
    if _fz:
        print('MDARK piece=%-10s nf=%d x[%.3f,%.3f] z[%.3f,%.3f]'%(
            o.name,sum(1 for f in o.data.polygons if f.material_index in _mi),
            min(_fx),max(_fx),min(_fz),max(_fz)))
        # sub-faixa alvo (t0.40: x 0.14..0.30, z>=0.65)
        _sx=[]; _sz=[]
        for f in o.data.polygons:
            if f.material_index in _mi:
                vs=[o.matrix_world@o.data.vertices[vi].co for vi in f.vertices]
                if max(v.x for v in vs)>=P.get('probe_x0',0.14) and max(v.x for v in vs)<=P.get('probe_x1',0.30) and max(v.z for v in vs)>=P.get('probe_z0',0.65):
                    _sx+= [v.x for v in vs]; _sz+=[v.z for v in vs]
        if _sx:
            print('   >>> NA FAIXA t0.40: nf=%d x[%.3f,%.3f] z[%.3f,%.3f]'%(
                sum(1 for f in o.data.polygons if f.material_index in _mi and
                    max((o.matrix_world@o.data.vertices[vi].co).x for vi in f.vertices)>=P.get('probe_x0',0.14) and
                    max((o.matrix_world@o.data.vertices[vi].co).x for vi in f.vertices)<=P.get('probe_x1',0.30) and
                    max((o.matrix_world@o.data.vertices[vi].co).z for vi in f.vertices)>=P.get('probe_z0',0.65)),
                min(_sx),max(_sx),min(_sz),max(_sz)))
print('===== FIM DIAG =====')"""
if anchor in SRC:
    SRC=SRC.replace(anchor,new23,1)
# patch 24: z do VOLANTE (sw_z) + ponta da coluna — o ocupante real de t0.40
old24="WX=P.get('sw_x',0.185); WZ=P.get('sw_z',0.655); WR=P.get('sw_r',0.115); WT=P.get('sw_tilt',0.040)"
new24="WX=P.get('sw_x',0.185); WZ=P.get('sw_z',0.655)+P.get('sw_dz',0.0); WR=P.get('sw_r',0.115); WT=P.get('sw_tilt',0.040)"
if old24 in SRC:
    SRC=SRC.replace(old24,new24,1)
old24b="(P.get('sc_x1',0.185),0,0.650)"
new24b="(P.get('sc_x1',0.185),0,0.650+P.get('sw_dz',0.0))"
if old24b in SRC:
    SRC=SRC.replace(old24b,new24b,1)
# patch 25: x do Cockpit_Cut (o PENHASCO do perfil; concept manda ~11cm mais atras)
old25="cut=box('Cockpit_Cut',(XFO-0.452*L,0,0.640+P.get('ch_top_dz',0.0)),(0.232,0.150,0.116)"
new25="cut=box('Cockpit_Cut',(XFO-0.452*L+P.get('ch_cut_dx',0.0),0,0.640+P.get('ch_top_dz',0.0)),(0.232,0.150,0.116)"
if old25 in SRC:
    SRC=SRC.replace(old25,new25,1)

old8b="py=tube_round('Wing_Pylon_'+('L' if sy>0 else 'R'),[(wx1+0.075,sy*0.150,wz-0.030),(wx1+0.130,sy*0.150,0.512)],0.036,14)"
new8b="py=tube_round('Wing_Pylon_'+('L' if sy>0 else 'R'),[(wx1+0.075,sy*0.150,wz-0.030+P.get('strut_dz',0.0)),(wx1+0.130,sy*0.150,0.512)],0.036,14)"
if old8b in SRC:
    SRC=SRC.replace(old8b,new8b,1)
ovr=dict(BASE); ovr.update(EP_OVERRIDES); ovr['v']=VER
g=dict(globals()); g['OVR']=ovr

# patch 26: FORMA do sidepod (cunha, nao bolha) — alongar, taper da frente, aplainar laterais
o26="            t=i/(NS-1.0); xf=0.330+0.405*t; x=XFO-xf*L\n            s=math.sin(math.pi*(0.06+0.88*t))**0.62"
n26="            t=i/(NS-1.0); xf=P.get('pod_xf0',0.330)+P.get('pod_xspan',0.405)*t; x=XFO-xf*L\n            s=math.sin(math.pi*(0.06+0.88*t))**0.62\n            if float(P.get('pod_taper_p',0.0))>0: s=s*(min(1.0,t/float(P.get('pod_taper_t',0.20)))**float(P.get('pod_taper_p',0.0)))"
if o26 in SRC:
    SRC=SRC.replace(o26,n26,1); print('P26 pod-loop OK')
else:
    print('P26 pod-loop NAO ACHOU')
o26b="abs(ca)**(2.0/2.0)"; n26b="abs(ca)**float(P.get('pod_e',1.0))"
c1=SRC.count(o26b)
if c1: SRC=SRC.replace(o26b,n26b)
o26c="abs(sa)**(2.0/2.0)"; n26c="abs(sa)**float(P.get('pod_e',1.0))"
c2=SRC.count(o26c)
if c2: SRC=SRC.replace(o26c,n26c)
print('P26 secao exp:',c1,c2)


# patch 27: side_cover com zb parametrizavel (era zb=0.240 HARDCODED -> topo 0.530 fixo, dominava o bbox do PODS)
o27="                zb=0.240\n                zt=0.300+float(P.get('cover_zt',0.230))*sc"
n27="                zb=float(P.get('cover_zb',0.240))\n                zt=(float(P.get('cover_zb',0.240))+0.060)+float(P.get('cover_zt',0.230))*sc"
if o27 in SRC:
    SRC=SRC.replace(o27,n27,1); print('P27 cover OK')
else:
    print('P27 cover NAO ACHOU')


# patch 28: altura do ENDPLATE da asa (o endplate desce ate ~0.30m no extremo recuado e o concept nao desce)
o28="ep=box('Wing_Endplate"
if o28 in SRC:
    import re as _re
    m=_re.search(r"ep=box\('Wing_Endplate[^\n]*\n", SRC)
    print('P28 ep linha:', m.group(0).strip()[:140] if m else 'nao achou')
else:
    print('P28 sem ancora Wing_Endplate')

# patch 29: x do conjunto Rear_Bumper_* (o Bot em rbz=0.300 caia dentro da ultima banda 5% do extremo
# recuado e o concept nao tem nada abaixo de 0.583 de H ali). Parametriza _bx = XRE + rb_x_off.
o29="_bx=XRE+0.010"
n29="_bx=XRE+P.get('rb_x_off',0.010)"
if o29 in SRC:
    SRC=SRC.replace(o29,n29,1); print('P29 rb_x_off OK')
else:
    print('P29 NAO ACHOU _bx')


# patch 30: x do ASSENTO (Seat_Base em -0.060 e Seat_Shell -0.150..-0.412).
# O degrau do perfil esta em x ~ -0.056 (0.5132 do comprimento) e o Seat_Base esta exatamente ali.
o30a="st1=box('Seat_Base',(-0.060,0,0.348)"
n30a="st1=box('Seat_Base',(-0.060+P.get('seat_dx',0.0),0,0.348)"
o30b="st2=tubevar('Seat_Shell',[(-0.150,0,0.368),(-0.234,0,0.432),(-0.322,0,0.500),(-0.412,0,0.560)]"
n30b="st2=tubevar('Seat_Shell',[(-0.150+P.get('seat_dx',0.0),0,0.368),(-0.234+P.get('seat_dx',0.0),0,0.432),(-0.322+P.get('seat_dx',0.0),0,0.500),(-0.412+P.get('seat_dx',0.0),0,0.560)]"
_c=0
if o30a in SRC: SRC=SRC.replace(o30a,n30a,1); _c+=1
if o30b in SRC: SRC=SRC.replace(o30b,n30b,1); _c+=1
print('P30 seat_dx patches aplicados:',_c,'de 2')


# patch 31 (v2): SPAN do cowl — alvo CORRIGIDO (o fallback anterior atingiu o NOSE).
# O cowl termina em x~0.209 e o capacete comeca em x~-0.063 (vao de 27cm = o degrau antes do pico).
o31="P.get('cowl_xf0',0.225)+0.235*(i/(NS-1.0))"
n31="P.get('cowl_xf0',0.225)+P.get('cowl_xspan',0.235)*(i/(NS-1.0))"
_c31=s=0
if o31 in SRC:
    SRC=SRC.replace(o31,n31,1); print('P31v2 cowl_xspan OK')
else:
    print('P31v2 alvo nao encontrado (cowl_xf0 patch ausente?)')
    for _l in SRC.split(chr(10)):
        if 'cowl_xf0' in _l: print('   linha cowl_xf0:', _l.strip()[:120])


# patch 32 (v2): ATENCAO — em dome(name,cx,cy,cz,R,sz,sy...) o perfil e [(raio_em_Y, -R*cos()*sz)] e
# revolve() usa o 2o elemento como OFFSET EM X. Logo **helm_sz JA E A ESCALA EM X do capacete**.
# Nao existe 'sx' na assinatura (passar sx quebra o build com TypeError). A alavanca correta e helm_sz.
# Objetivo: recolher a FRENTE mantendo o CENTRO (onde esta o pico/topo_global_x, ja correto).
print('P32v2 alavanca do capacete = helm_sz (escala X); base usa helm_sz=0.934')


# patch 33: RECUO AUTORAL DA FRENTE DO CAPACETE (o caminho procedural esta esgotado: helm_x move o pico,
# helm_sz acopla altura, estender o cowl fica dentro do contorno). Aqui deformamos a malha do capacete:
# o PICO do dome esta em x = hx (no perfil [(raio_Y, -R*cos(t)*sz)] o offset em x e 0 quando t=90 graus).
# Peso w = (x-hx)/(HR*SZ) => 0 no pico, 1 na frente. O pico fica EXATAMENTE parado.
o33="helm=dome('Helmet',hx,0.0,hz,HR,sz=SZ,sy=1.0,seg=104,rings=62); assign(helm,'M_Blue')"
n33=("helm=dome('Helmet',hx,0.0,hz,HR,sz=SZ,sy=1.0,seg=104,rings=62); assign(helm,'M_Blue')\n"
     "    _hf=P.get('helm_front',0.0)\n"
     "    if _hf>0:\n"
     "        _n=0; _mx=0.0\n"
     "        for _v in helm.data.vertices:\n"
     "            _d=_v.co.x-hx\n"
     "            if _d>0:\n"
     "                _w=min(1.0,_d/(HR*SZ)); _v.co.x=hx+_d*(1.0-_hf*_w); _n+=1; _mx=max(_mx,_w)\n"
     "        helm.data.update()\n"
     "        print('P33 helm_front=%.2f verts_movidos=%d w_max=%.3f'%(_hf,_n,_mx))\n"
     "    else:\n"
     "        print('P33 helm_front OFF')")
if o33 in SRC: SRC=SRC.replace(o33,n33,1); print('P33 INSERIDO OK')
else: print('P33 ALVO NAO ENCONTRADO')


# patch 34: FRENTE-INFERIOR DO CAPACETE (autorais/bmesh). Medido: a parede quase vertical do perfil no ponto do degrau
# mede 0.30m no modelo e 0.41m no concept (degrau_amp 0.2428 vs 0.3242) — mesma posicao (0.5107 vs 0.5132), logo e feicao
# REAL e ancorada. A parede desce de z/H 0.8307 (1.040m) para 0.5880 (0.736m): para subir o TOPO da parede 11cm sem mover
# o PICO do capacete, a frente-inferior precisa AVANCAR. Peso duplo: 0 no pico e no topo (x<=hx ou z>=hz), 1 na frente-baixa.
# Nao mexer em constantes: 6 refutacoes (rzt, cowl_k, cockpit_cut, helm_front, M_Face, M_Visor) provaram que nao ha parametro.
o34="        print('P33 helm_front=%.2f verts_movidos=%d w_max=%.3f'%(_hf,_n,_mx))\n    else:\n        print('P33 helm_front OFF')"
n34=("        print('P33 helm_front=%.2f verts_movidos=%d w_max=%.3f'%(_hf,_n,_mx))\n"
     "    else:\n        print('P33 helm_front OFF')\n"
     "    _hl=P.get('helm_low',0.0)\n"
     "    if _hl>0:\n"
     "        _n2=0; _mx2=0.0\n"
     "        for _v in helm.data.vertices:\n"
     "            _dx=_v.co.x-hx; _dz=hz-_v.co.z\n"
     "            if _dx>0 and _dz>0:\n"
     "                _wx=min(1.0,_dx/(HR*SZ)); _wz=min(1.0,_dz/(HR*SZ*0.9))\n"
     "                _w=_wx*_wz\n"
     "                if _w>0.0:\n"
     "                    _v.co.x+=_hl*_w; _v.co.z-=0.35*_hl*_w; _n2+=1; _mx2=max(_mx2,_w)\n"
     "        helm.data.update()\n"
     "        print('P34 helm_low=%.3f verts=%d w_max=%.3f'%(_hl,_n2,_mx2))\n"
     "    else:\n        print('P34 helm_low OFF')")
if o34 in SRC:
    SRC=SRC.replace(o34,n34,1); print('P34 INSERIDO OK (frente-inferior do capacete)')
else:
    print('P34 ALVO NAO ENCONTRADO')


# patch 35: FRENTE-SUPERIOR DO CAPACETE = ABA/TESTA. W535 provou o inverso do que eu supunha: estender a frente-INFERIOR
# para frente PREENCHE o vao e derruba a parede (degrau_amp 0.2428->0.1915) e ainda MOVE o degrau (degrau_x 0.5132->0.7273,
# erro 0.0024->0.2166 => REGRESSAO). A parede e a QUEDA do topo frontal do capacete: para deixa-la mais alta sem mover o
# degrau, o que avanca e a frente-SUPERIOR (aba/testa), mantendo o topo do pico onde esta (topo_global_x ja correto 0.0134).
o35="        print('P34 helm_low=%.3f verts=%d w_max=%.3f'%(_hl,_n2,_mx2))\n    else:\n        print('P34 helm_low OFF')"
n35=("        print('P34 helm_low=%.3f verts=%d w_max=%.3f'%(_hl,_n2,_mx2))\n"
     "    else:\n        print('P34 helm_low OFF')\n"
     "    _hb=P.get('helm_brow',0.0)\n"
     "    if _hb>0:\n"
     "        _n3=0; _mx3=0.0\n"
     "        for _v in helm.data.vertices:\n"
     "            _dx=_v.co.x-hx; _dz=_v.co.z-hz\n"
     "            if _dx>0 and _dz>0:\n"
     "                _wx=min(1.0,_dx/(HR*SZ)); _wz=min(1.0,_dz/(HR*0.9))\n"
     "                _w=_wx*_wz\n"
     "                if _w>0.0:\n"
     "                    _v.co.x+=_hb*_w; _v.co.z+=0.30*_hb*_w; _n3+=1; _mx3=max(_mx3,_w)\n"
     "        helm.data.update()\n"
     "        print('P35 helm_brow=%.3f verts=%d w_max=%.3f'%(_hb,_n3,_mx3))\n"
     "    else:\n        print('P35 helm_brow OFF')")
if o35 in SRC:
    SRC=SRC.replace(o35,n35,1); print('P35 INSERIDO OK (aba da frente-superior)')
else:
    print('P35 ALVO NAO ENCONTRADO')

# patch 36: Z PROPRIO DO PAD AMARELO DO PARA-CHOQUE. O topo do FBUMP (0.3469) e o pad amarelo:
#   0.2622 + raio 0.086 = 0.3482, x escala 0.98523 = 0.343 (casa com 0.3469). Alvo validado
#   L_topo_z 0.2394 x H 1.188 = 0.284m => pre-escala 0.2883 => centro 0.2023 => pad_dz = -0.060.
#   ANTES era literal hardcoded; agora e parametro. (ep_s NAO controla o FBUMP: sonda W542 provou
#   que ele controla o REAR, topo 0.8916->0.8566.)
_o36="                       [(XFO-0.028,_sy*0.330,0.2622),(XFO-0.086,_sy*0.400,0.2610),(XFO-0.150,_sy*0.470,0.2596)],"
_n36=("                       [(XFO-0.028,_sy*0.330,0.2622+P.get('pad_dz',0.0)),"
      "(XFO-0.086,_sy*0.400,0.2610+P.get('pad_dz',0.0)),"
      "(XFO-0.150,_sy*0.470,0.2596+P.get('pad_dz',0.0))],")
if _o36 in SRC:
    SRC=SRC.replace(_o36,_n36,1); print('P36 INSERIDO OK (pad_dz parametrizado)')
else:
    print('P36 ALVO NAO ENCONTRADO')

# patch G26c: DESLIGA as pecas LEGADAS do front_bumper (pad_l/pad_r) — elas conviviam com o tubo novo
# e eram elas que o vision via como "2 selos amarelos chapados"; o fbar virava "bloco retangular de quinas vivas".
_og26c = "    for _sy in (1,-1):\n        # BLOCO AMARELO integrado SOBRE a barra"
_ng26c = "    for _sy in ((1,-1) if P.get('g26c_pads',1) else ()):\n        # BLOCO AMARELO integrado SOBRE a barra"
assert _og26c in SRC, "loop dos pads legados nao encontrado"
SRC = SRC.replace(_og26c, _ng26c, 1)
print("G26c: pads legados gateados por g26c_pads")

# patch 26 (G27): PATAMAR FRONTAL DA CARENA. O concept tem um shelf MEDIDO e plano em xf 0.267-0.350
# a 0.551 da altura (grade fina de 61 estacoes na mask v2), com degrau de entrada +0.084 e saida -0.070.
# A tabela prof_top nao contem esse patamar (da 0.430 ali). Janela trapezoidal + max() = shelf com
# ombros suaves, e onde prof_top ja e maior o max() preserva a tabela (nao ha dano).
# patch 32 (G26-capacete): FAIXA AMARELA. O vision so ve a faixa no topo-traseiro -> a parte frontal do loft
# esta afundada na superficie do capacete. Patch: (a) SOBE o offset radial (1.006/1.001 -> parametro),
# (b) ESTENDE o arco para frente (u inicial 19 -> parametro) para a faixa nascer na testa,
# (c) engrossa a largura. Diagnostico de vision, nao de metrica.
# patch 33: reg() passa a guardar o BBOX REAL da sub-peca (qp() devolvia 0)
if open('/tmp/p33_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p33_anchor.txt').read(), open('/tmp/p33_new.txt').read(), 1)
    print('P33 aplicado (bbox real em reg())')
else:
    print('P33 NAO aplicado')
_oldp32 = open('/tmp/p32_anchor.txt').read()
_newp32 = open('/tmp/p32_new.txt').read()
if _oldp32 in SRC:
    SRC = SRC.replace(_oldp32, _newp32, 1)
    print('P32 aplicado (helm_trim)')
else:
    print('P32 NAO aplicado (ancora nao encontrada)')
if open('/tmp/p32_new.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p32_new.txt').read(), open('/tmp/p34_new.txt').read(), 1)
    print('P34 aplicado (faixa projetada na superficie real)')
else:
    print('P34 NAO aplicado')
if open('/tmp/p35_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p35_anchor.txt').read(), open('/tmp/p35_new.txt').read(), 1)
    print('P35 aplicado (vent na superficie real)')
else:
    print('P35 NAO aplicado')
if open('/tmp/p44_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p44_anchor.txt').read(), open('/tmp/p44_new.txt').read(), 1)
    print('P44 aplicado (camera face)')
else:
    print('P44 NAO aplicado')
if open('/tmp/p36_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p36_anchor.txt').read(), open('/tmp/p36_new.txt').read(), 1)
    print('P36 aplicado (head ORTOGRAFICO)')
else:
    print('P36 NAO aplicado')
if open('/tmp/p37_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p37_anchor.txt').read(), open('/tmp/p37_new.txt').read(), 1)
    print('P37 aplicado (scale Y do capacete)')
else:
    print('P37 NAO aplicado')
if open('/tmp/p40_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p40_anchor.txt').read(), open('/tmp/p40_new.txt').read(), 1)
    print('P40 aplicado (viseira reposicionada por metrica)')
else:
    print('P40 NAO aplicado')
if open('/tmp/p42_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p42_anchor.txt').read(), open('/tmp/p42_new.txt').read(), 1)
    print('P42 aplicado (face reposicionada)')
else:
    print('P42 NAO aplicado')
_anc=open('/tmp/p43_anchor.txt').read().split('\n\n'); _nw=open('/tmp/p43_new.txt').read().split('\n\n')
for _a,_b in zip(_anc,_nw):
    assert _a in SRC or _a in SRC.replace(chr(13),''), 'P43 ancora nao casa: '+_a[:40]
    SRC = SRC.replace(_a,_b,1)
print('P43 aplicado (pupila oval + sobrancelha fina)')
if open('/tmp/p46_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p46_anchor.txt').read(), open('/tmp/p46_new.txt').read(), 1)
    print('P46v2 aplicado (chin scale)')
else:
    print('P46v2 NAO aplicado')
if open('/tmp/p48_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p48_anchor.txt').read(), open('/tmp/p48_new.txt').read(), 1)
    print('P48 aplicado (cowl_cut_z)')
else:
    print('P48 NAO aplicado')
if open('/tmp/p49_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p49_anchor.txt').read(), open('/tmp/p49_new.txt').read(), 1)
    print('P49 aplicado (recorte pos-build)')
else:
    print('P49 NAO aplicado')
if open('/tmp/p47_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p47_anchor.txt').read(), open('/tmp/p47_new.txt').read(), 1)
    print('P47 aplicado (chin_dz)')
else:
    print('P47 NAO aplicado')
if open('/tmp/p45_anchor.txt').read() in SRC:
    SRC = SRC.replace(open('/tmp/p45_anchor.txt').read(), open('/tmp/p45_new.txt').read(), 1)
    print('P45 aplicado (cowl_dzt)')
else:
    print('P45 NAO aplicado')

_oldp26 = "zt=prof_top(xf)*H*P.get('cowl_k',0.97)"
_newp26 = ("zt=prof_top(xf)*H*P.get('cowl_k',0.97)\n"
           "        _k2=P.get('cowl_sm',0.0)\n"
           "        _sm2=(lambda a,b: (a+b+math.sqrt((a-b)**2+_k2*_k2))*0.5) if _k2>0.0 else max\n"
           "        _pa=P.get('cowl_plat_a',0.0)\n"
           "        if _pa>0.0:\n"
           "            _pb=P.get('cowl_plat_b',1.0); _pf=max(1e-6,P.get('cowl_plat_f',0.12))\n"
           "            _pu=(xf-_pa)/max(1e-9,(_pb-_pa))\n"
           "            _pw=0.0 if (_pu<=0.0 or _pu>=1.0) else min(1.0,_pu/_pf,(1.0-_pu)/_pf)\n"
"            zt=_sm2(zt,H*P.get('cowl_plat_h',0.0)*_pw)\n"
"        _pa2=P.get('cowl_plat2_a',0.0)\n"
"        if _pa2>0.0:\n"
"            _pb2=P.get('cowl_plat2_b',1.0); _pf2=max(1e-6,P.get('cowl_plat2_f',0.30))\n"
"            _pu2=(xf-_pa2)/max(1e-9,(_pb2-_pa2))\n"
"            _pw2=0.0 if (_pu2<=0.0 or _pu2>=1.0) else min(1.0,_pu2/_pf2,(1.0-_pu2)/_pf2)\n"
"            zt=_sm2(zt,H*P.get('cowl_plat2_h',0.0)*_pw2)\n"
           "            zt=max(zt,H*P.get('cowl_plat_h',0.0)*_pw)")
assert _oldp26 in SRC, "linha zt da carena nao encontrada"
assert "cowl_plat_h" not in SRC
SRC = SRC.replace(_oldp26, _newp26, 1)
print("G27 patch 26 aplicado: patamar frontal da carena parametrizado")

# patch 27 (G27): substitui os nos da tabela MEDIDA prof_top por valores MEDIDOS na mask v2 (validada por overlay).
# Causa raiz: a tabela foi medida com a altura INFLADA pela linha de cota embutida na mascara antiga
# (H=438 em vez de 403 px, fator 1.087), entao TODOS os valores da frente ficaram ~9% baixos
# (razao media medida 1.106 em xf 0.05-0.25). Substituir numero herdado por medicao e a correcao correta.
_tb0 = SRC.index("tab=[(0.00,0.204)")
_tb1 = SRC.index("(0.45,0.575),") + len("(0.45,0.575),")
_neww = ("tab=[(0.000,0.217),(0.025,0.297),(0.050,0.320),(0.075,0.332),(0.100,0.353),(0.125,0.334),"
         "(0.150,0.362),(0.175,0.388),(0.200,0.416),(0.225,0.439),(0.250,0.465),(0.275,0.549),"
         "(0.300,0.551),(0.325,0.549),(0.350,0.540),(0.375,0.479),(0.400,0.509),(0.425,0.621),"
         "(0.450,0.600),")
assert len(_neww) > 100 and _tb1 > _tb0
SRC = SRC[:_tb0] + _neww + SRC[_tb1:]
print("G27 patch 27: tabela prof_top corrigida com valores medidos (xf 0.00-0.45)")

_o28='        ry=0.098*s+0.030'
_n28=("        ry=P.get('cowl_ry_k',0.098)*s+P.get('cowl_ry0',0.030)")
assert _o28 in SRC, 'secao ry da carena nao encontrada'
SRC=SRC.replace(_o28,_n28,1)
print('P28: secao ry da carena parametrizada (cowl_ry_k/cowl_ry0)')

_o29='    out=[]; NS=22; secs=[]'
_n29="    out=[]; NS=int(P.get('cowl_ns',22)); secs=[]"
assert _o29 in SRC, 'NS da carena nao encontrado'
SRC=SRC.replace(_o29,_n29,1)
print('P29: NS da carena parametrizado (cowl_ns)')

# patch G26: FBUMP deixa de ser TUBO e vira CARENAGEM FECHADA + LABIO AMARELO EM U + INTAKE LAMELADO.
# Veredito do vision (IDENTITY-GAPS.md item 1): "barra/tubo prateado horizontal flutuante, fino, reto,
# separado do chassi, com 2 tocos amarelos. Sem carenagem, sem grade volumosa, sem U amarelo."
# Aqui: (a) substitui o anel fino por um corpo FECHADO baixo/largo com bevel toy; (b) labio amarelo
# espesso em U abracando a frente; (c) 5 lamelas de intake azul-escuras; (d) 2 aletas amarelas laterais.
_o_g26 = ("    o=tube_round('Bumper_Ring',spine,rb*1.07,20); assign(o,P.get('ringmat','M_Plate'))")
_n_g26 = ("    # G26d: ancorado na SUPERFICIE FRONTAL do tubo (_xs), nao em XFO (bug que enterrava coxins e intake)\n"
"    _rw=P.get('g26b_r',0.180); _yyw=P.get('g26b_w',0.630); _zzc=P.get('g26b_z',0.216)\n"
"    _back=P.get('g26b_back',0.150); _dip=P.get('g26b_dip',0.012); _zsq=P.get('g26b_zsq',1.00)\n"
"    _be0=P.get('g26b_be0',0.94); _belly=P.get('g26b_belly',0.14); _seg=int(P.get('g26b_seg',24))\n"
"    _xs=(XFO-0.030)+_rw*(_be0+_belly)\n"
"    _NS=31; _sp=[]; _rr=[]\n"
"    for _i in range(_NS):\n"
"        _t=_i/(_NS-1.0); _a=-math.pi/2+math.pi*_t; _sn=math.sin(_a); _cs=math.cos(_a)\n"
"        _yy=_yyw*math.copysign(abs(_sn)**P.get('g26b_py',0.92),_sn)\n"
"        _xx=(XFO-0.030)-_back*(1.0-abs(_cs))\n"
"        _zz=_zzc-_dip*abs(_cs)\n"
"        _sp.append((_xx,_yy,_zz))\n"
"        _rr.append(_rw*(_be0+_belly*math.sin(math.pi*_t)))\n"
"    _secs=[]\n"
"    for _i in range(_NS):\n"
"        _x0,_y0,_z0=_sp[_i]; _r=_rr[_i]; _rz=_r*_zsq\n"
"        _secs.append([(_x0+_r*math.cos(2*math.pi*_k/_seg),_y0,_z0+_rz*math.sin(2*math.pi*_k/_seg)) for _k in range(_seg)])\n"
"    _tb=loft('FBump_Tube',_secs)\n"
"    assign(_tb,P.get('g26b_mat','M_Blue')); out.append(reg('fbump_tube',_tb))\n"
"    # COXINS: capsulas VERTICAIS PROTRUSAS na face frontal, nas quinas, abracando o intake\n"
"    for _sy in (1,-1):\n"
"        _cx=_xs+P.get('g26b_cx',-0.045); _cy=_sy*_yyw*P.get('g26b_cyk',0.66)\n"
"        _cz0=_zzc+P.get('g26b_cz0',-0.095); _cz1=_zzc+P.get('g26b_cz1',0.095)\n"
"        _cs2=[(_cx,_cy,_cz0),(_cx,_cy+_sy*0.010,(_cz0+_cz1)*0.5),(_cx-0.006,_cy+_sy*0.014,_cz1)]\n"
"        _cu=tube_round('Cush_'+('L' if _sy>0 else 'R'),_cs2,P.get('g26b_cr',0.090),16)\n"
"        assign(_cu,P.get('g26b_cmat','M_Yellow')); out.append(reg('cushion_'+('l' if _sy>0 else 'r'),_cu))\n"
"    # INTAKE: caixa PRETA grande FLUSH/+2cm PARA FORA da superficie frontal\n"
"    _ibc=P.get('g26b_ibc',0.075); _ibp=P.get('g26b_ibp',0.020)\n"
"    _ibx=_xs+_ibp-_ibc\n"
"    _ib=box('Intake_Box',(_ibx,0.0,_zzc+P.get('g26b_ibz',0.0)),\n"
"           (_ibc,P.get('g26b_ibw',0.252),P.get('g26b_ibh',0.088)),bevel=0.012,segs=2)\n"
"    assign(_ib,P.get('g26b_imat','M_Dark')); out.append(reg('intake_box',_ib))\n"
"    _lvs=P.get('g26b_lvs',0.0985); _lvx=_xs+P.get('g26b_lvx',0.012)\n"
"    for _i in range(5):\n"
"        _yy2=_lvs*(-2.0+_i)\n"
"        _lv2=box('Intk2_L%d'%_i,(_lvx,_yy2,_zzc+P.get('g26b_lvz',0.0)),\n"
"                (P.get('g26b_lvc',0.018),P.get('g26b_lvw',0.022),P.get('g26b_lvh',0.082)),bevel=0.006,segs=2)\n"
"        assign(_lv2,P.get('g26b_lmat','M_Dark')); out.append(reg('intake2_%d'%_i,_lv2))\n"
"    o=None")
if _o_g26 in SRC:
    SRC=SRC.replace(_o_g26,_n_g26,1); print('G26 INSERIDO OK (carenagem fechada + labio U + intake + aletas)')
else:
    print('G26 ALVO NAO ENCONTRADO')

open('/tmp/built_last.py','w').write(SRC)
exec(compile(SRC,'bb_'+VER,'exec'),g)
R=g.get('R',{})
print(VER,'| QA=',R.get('qa',{}).get('aprovado'),'| z_range=',R.get('z_range'),'| ERRO=',R.get('ERRO'))

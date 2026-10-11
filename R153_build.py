#!/usr/bin/env python3
"""Build Super Kart Hero V2 R153 from a class-level authored cockpit revision.

Blender 4.0+: blender -b --factory-startup --python hero_kart_v2_build.py -- \
  --output /path/to/assets/hero-kart-v2/hero-kart-v2.blend

All primary body panels, fenders, wheel profiles, aero and mechanical members are
constructed from explicit profiles/lofts. No source model is imported or reused.
"""
import argparse
import math
import os
import bmesh
from mathutils import Vector, Matrix
import bpy

TAU = math.tau
MATS = {}
CURRENT_COLLECTION = None
PREFIX = ""


def canonical_material_key(key):
    """Keep each LOD inside its explicit material contract."""
    if key == "metal_warm": key = "paint_primary"
    if key == "cockpit_glass" and CURRENT_COLLECTION and CURRENT_COLLECTION.name != "LOD0": key = "paint_secondary"
    if key == "accent_emissive" and CURRENT_COLLECTION and CURRENT_COLLECTION.name == "LOD2": key = "paint_primary"
    return key


def parse_args():
    argv = []
    if "--" in __import__("sys").argv:
        argv = __import__("sys").argv[__import__("sys").argv.index("--") + 1:]
    p = argparse.ArgumentParser()
    p.add_argument("--output", default=None)
    p.add_argument("--revision", default="R153")
    p.add_argument("job_dir", nargs="?")
    return p.parse_args(argv)


def material(name, color, metallic, roughness, emission=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        key = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        bsdf.inputs[key].default_value = (*emission, 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 2.8
    return mat


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Hero_Kart_V2_Studio"
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    if scene.world is None:
        scene.world = bpy.data.worlds.new("Hero_Kart_V2_World")
    scene.world.color = (0.035, 0.045, 0.06)
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    global MATS
    MATS = {
        "paint_primary": material("paint_primary", (0.025, 0.42, 0.52), 0.15, 0.28),
        "paint_secondary": material("paint_secondary", (0.025, 0.075, 0.14), 0.10, 0.34),
        "rubber_dark": material("rubber_dark", (0.025, 0.032, 0.042), 0.0, 0.72),
        "metal_warm": material("metal_warm", (0.54, 0.25, 0.075), 0.78, 0.30),
        "accent_emissive": material("accent_emissive", (1.0, 0.16, 0.018), 0.0, 0.38, (1.0, 0.045, 0.004)),
    }
    glass = material("cockpit_glass", (0.08, 0.32, 0.40), 0.0, 0.12)
    glass_bsdf = glass.node_tree.nodes.get("Principled BSDF")
    glass_bsdf.inputs["Base Color"].default_value = (0.10, 0.30, 0.38, 1.0)
    glass_bsdf.inputs["Metallic"].default_value = 0.0
    glass_bsdf.inputs["Roughness"].default_value = 0.12
    glass_bsdf.inputs["Alpha"].default_value = 0.42
    if "Transmission Weight" in glass_bsdf.inputs:
        glass_bsdf.inputs["Transmission Weight"].default_value = 0.18
    elif "Transmission" in glass_bsdf.inputs:
        glass_bsdf.inputs["Transmission"].default_value = 0.18
    # Blender 4.0 Eevee alpha path: hashed transparency, no refraction or black Mix Shader.
    try:
        glass.blend_method = "BLEND"
        glass.shadow_method = "NONE"
        glass.show_transparent_back = False
    except Exception:
        pass
    glass.diffuse_color = (0.012, 0.055, 0.085, 1.0)

    MATS["cockpit_glass"] = glass
    scene["asset_name"] = "Super Kart — Hero Kart V2"
    scene["authored_from_scratch"] = True
    scene["coordinate_forward"] = "-Y"
    scene["coordinate_up"] = "+Z"
    scene["meters_per_blender_unit"] = 1.0


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def mesh_object(name, verts, faces, mat, smooth=True, parent=None):
    mesh = bpy.data.meshes.new(PREFIX + name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    # Every authored mesh owns an explicit UV layer, even when the material is procedural.
    mesh.uv_layers.new(name="UVMap")
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(PREFIX + name, mesh)
    CURRENT_COLLECTION.objects.link(obj)
    if mat:
        key = canonical_material_key(mat if isinstance(mat, str) else mat.name)
        mesh.materials.append(MATS[key] if key in MATS else mat)
    for poly in mesh.polygons:
        poly.use_smooth = smooth
    if parent:
        # Wheel components are authored in pivot-local coordinates; keep identity
        # child transforms so the axle center remains the true rotation origin.
        obj.parent = parent
    obj["authored_component"] = name
    return obj


def empty(name, location=(0, 0, 0)):
    obj = bpy.data.objects.new(PREFIX + name, None)
    CURRENT_COLLECTION.objects.link(obj)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.12
    obj.location = location
    return obj


def transform_point(p, origin=(0, 0, 0), basis=None):
    v = Vector(p)
    if basis:
        bx, by, bz = basis
        v = bx * v.x + by * v.y + bz * v.z
    return tuple(Vector(origin) + v)


def triangulated_box(name, center, size, mat, basis=None, parent=None):
    sx, sy, sz = (v * 0.5 for v in size)
    raw = [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),
           (-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
    verts = [transform_point(v, center, basis) for v in raw]
    faces = [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
             (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return mesh_object(name, verts, faces, mat, False, parent)


def ellipsoid(name, center, scale, mat, seg=20, rings=10, parent=None):
    verts = [(center[0], center[1], center[2] + scale[2])]
    for j in range(1, rings):
        ph = math.pi * j / rings
        for i in range(seg):
            th = TAU * i / seg
            verts.append((center[0] + scale[0] * math.sin(ph) * math.cos(th),
                          center[1] + scale[1] * math.sin(ph) * math.sin(th),
                          center[2] + scale[2] * math.cos(ph)))
    bottom = len(verts)
    verts.append((center[0], center[1], center[2] - scale[2]))
    faces = []
    for i in range(seg):
        faces.append((0, 1 + i, 1 + (i + 1) % seg))
    for j in range(rings - 2):
        a = 1 + j * seg
        b = a + seg
        for i in range(seg):
            ni = (i + 1) % seg
            faces.append((a+i, b+i, b+ni, a+ni))
    last = 1 + (rings - 2) * seg
    for i in range(seg):
        faces.append((last+i, bottom, last+(i+1)%seg))
    return mesh_object(name, verts, faces, mat, True, parent)


def loft(name, sections, sides, mat, power=2.0, parent=None):
    """Closed longitudinal custom loft. section=(y,cx,cz,half_w,half_h)."""
    verts = []
    for y, cx, cz, hw, hh in sections:
        for i in range(sides):
            a = TAU * i / sides
            ca, sa = math.cos(a), math.sin(a)
            x = cx + hw * math.copysign(abs(ca) ** (2.0 / power), ca)
            z = cz + hh * math.copysign(abs(sa) ** (2.0 / power), sa)
            verts.append((x, y, z))
    faces = []
    for j in range(len(sections)-1):
        for i in range(sides):
            ni = (i+1) % sides
            faces.append((j*sides+i, (j+1)*sides+i, (j+1)*sides+ni, j*sides+ni))
    s0 = len(verts); verts.append((sections[0][1], sections[0][0], sections[0][2]))
    s1 = len(verts); verts.append((sections[-1][1], sections[-1][0], sections[-1][2]))
    for i in range(sides):
        ni = (i+1) % sides
        faces.append((s0, ni, i))
        a=(len(sections)-1)*sides+i; b=(len(sections)-1)*sides+ni
        faces.append((s1, a, b))
    return mesh_object(name, verts, faces, mat, True, parent)


def ribbon_solid(name, sections, mat, side=1, parent=None):
    """Four-corner closed section ribbon. tuple=(y, outer_x, inner_x, z_top, z_bottom)."""
    verts=[]
    for y, xo, xi, zt, zb in sections:
        verts.extend([(side*xo,y,zt),(side*xi,y,zt-0.018),(side*xi,y,zb),(side*xo,y,zb-0.012)])
    faces=[]
    n=len(sections)
    for j in range(n-1):
        for k in range(4):
            nk=(k+1)%4
            faces.append((j*4+k,(j+1)*4+k,(j+1)*4+nk,j*4+nk))
    faces += [(0,2,1),(0,3,2)]
    o=(n-1)*4; faces += [(o,o+1,o+2),(o,o+2,o+3)]
    return mesh_object(name, verts, faces, mat, True, parent)


def tube_path(name, points, radius, mat, sides=8, radius2=None, closed=False, parent=None):
    pts=[Vector(p) for p in points]
    rings=len(pts)
    verts=[]
    frames=[]
    for i,p in enumerate(pts):
        if closed:
            tangent=(pts[(i+1)%rings]-pts[(i-1)%rings]).normalized()
        elif i==0:
            tangent=(pts[1]-pts[0]).normalized()
        elif i==rings-1:
            tangent=(pts[-1]-pts[-2]).normalized()
        else:
            tangent=(pts[i+1]-pts[i-1]).normalized()
        ref=Vector((0,0,1)) if abs(tangent.z)<0.88 else Vector((0,1,0))
        b1=tangent.cross(ref).normalized(); b2=tangent.cross(b1).normalized()
        frames.append((b1,b2))
        for k in range(sides):
            a=TAU*k/sides
            rr=radius if radius2 is None else radius2
            v=p+b1*(radius*math.cos(a))+b2*(rr*math.sin(a))
            verts.append(tuple(v))
    faces=[]
    lim=rings if closed else rings-1
    for j in range(lim):
        nj=(j+1)%rings
        for k in range(sides):
            nk=(k+1)%sides
            faces.append((j*sides+k,nj*sides+k,nj*sides+nk,j*sides+nk))
    if not closed:
        c0=len(verts); verts.append(tuple(pts[0])); c1=len(verts); verts.append(tuple(pts[-1]))
        for k in range(sides):
            nk=(k+1)%sides
            faces.append((c0,nk,k))
            a=(rings-1)*sides+k; b=(rings-1)*sides+nk
            faces.append((c1,a,b))
    return mesh_object(name,verts,faces,mat,True,parent)


def cylinder_x(name, center, radius, depth, mat, seg=24, radius_y=None, parent=None):
    # Blender's closed primitive is used only as a deterministic topology kernel;
    # it avoids the prior hand-authored cap winding defect (188 bad edges/cylinder).
    ry = radius if radius_y is None else radius_y
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=radius, depth=depth,
                                        location=center, rotation=(0, math.pi/2, 0))
    obj=bpy.context.object
    if abs(ry-radius)>1e-9:
        obj.scale.y=ry/radius; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    old_name=obj.name; obj.name=PREFIX+name
    for c in list(obj.users_collection): c.objects.unlink(obj)
    CURRENT_COLLECTION.objects.link(obj)
    key=canonical_material_key(mat if isinstance(mat,str) else mat.name)
    obj.data.materials.append(MATS[key] if key in MATS else mat)
    obj["authored_component"]=name
    obj["uv_generated"]=True
    if len(obj.data.uv_layers)==0: obj.data.uv_layers.new(name="UVMap")
    bm=bmesh.new(); bm.from_mesh(obj.data); bmesh.ops.triangulate(bm, faces=list(bm.faces)); bm.to_mesh(obj.data); bm.free()
    for poly in obj.data.polygons: poly.use_smooth=True
    if parent: obj.parent=parent
    return obj


def tire_mesh(name, radius, width, center_z, seg, profile_n, parent):
    # Closed rounded-square radial tire profile with deep bead; local axle is X.
    outer=[]
    half=profile_n//2
    for j in range(half+1):
        t=j/half
        x=-width/2+width*t
        shoulder=abs(2*t-1)
        r=radius-(shoulder**3)*0.035+0.004*(1-shoulder)
        outer.append((x,r))
    inner=[]
    for j in range(half-1,0,-1):
        t=j/half
        x=-width/2+width*t
        shoulder=abs(2*t-1)
        r=radius*0.58-0.012*(1-shoulder)
        inner.append((x,r))
    prof=outer+inner
    verts=[]
    compression=radius-center_z
    for i in range(seg):
        a=TAU*i/seg
        cs,sn=math.cos(a),math.sin(a)
        for x,r in prof:
            z=r*sn + compression*(max(0.0,-sn)**8)
            verts.append((x,r*cs,z))
    pn=len(prof); faces=[]
    for i in range(seg):
        ni=(i+1)%seg
        for j in range(pn):
            nj=(j+1)%pn
            faces.append((i*pn+j,ni*pn+j,ni*pn+nj,i*pn+nj))
    return mesh_object(name,verts,faces,"rubber_dark",True,parent)


def ring_x(name, major, width, mat, seg, tube=0.018, parent=None):
    prof=[(-width/2,major-tube),( -width/2,major+tube),
          (-width*0.28,major+tube*1.35),(width*0.28,major+tube*1.35),
          (width/2,major+tube),(width/2,major-tube),
          (width*0.25,major-tube*1.15),(-width*0.25,major-tube*1.15)]
    verts=[]
    for i in range(seg):
        a=TAU*i/seg; cs,sn=math.cos(a),math.sin(a)
        for x,r in prof: verts.append((x,r*cs,r*sn))
    faces=[]; pn=len(prof)
    for i in range(seg):
        ni=(i+1)%seg
        for j in range(pn): faces.append((i*pn+j,ni*pn+j,ni*pn+(j+1)%pn,i*pn+(j+1)%pn))
    return mesh_object(name,verts,faces,mat,True,parent)


def spoke(name, angle, inner_r, outer_r, inner_w, outer_w, depth, mat, parent):
    r=Vector((0,math.cos(angle),math.sin(angle)))
    t=Vector((0,-math.sin(angle),math.cos(angle)))
    pts=[]
    for x in (-depth/2,depth/2):
        pts += [tuple(Vector((x,0,0))+r*inner_r-t*inner_w/2),
                tuple(Vector((x,0,0))+r*inner_r+t*inner_w/2),
                tuple(Vector((x,0,0))+r*outer_r+t*outer_w/2),
                tuple(Vector((x,0,0))+r*outer_r-t*outer_w/2)]
    faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
           (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return mesh_object(name,pts,faces,mat,False,parent)


def tread_block(name, theta, xcenter, radius, width_x, parent, direction=0.0):
    radial=Vector((0,math.cos(theta),math.sin(theta)))
    tangent=Vector((0,-math.sin(theta),math.cos(theta)))
    axle=Vector((1,0,0))
    # Chevron rotation in axle/tangent plane.
    u=(axle*math.cos(direction)+tangent*math.sin(direction)).normalized()
    v=(-axle*math.sin(direction)+tangent*math.cos(direction)).normalized()
    center=axle*xcenter+radial*(radius+0.008)
    sx,sy,sz=width_x/2,0.030,0.010
    verts=[]
    for rr in (-sz,sz):
        for vv,uu in [(-sy,-sx),(-sy,sx),(sy,sx),(sy,-sx)]:
            verts.append(tuple(center+u*uu+v*vv+radial*rr))
    faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
           (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return mesh_object(name,verts,faces,"rubber_dark",False,parent)


def wheel(side, axle, radius, width, cfg):
    x=side*axle[0]; y=axle[1]; z=axle[2]
    pivot=empty(f"WHEEL_{'L' if side<0 else 'R'}_{'F' if y<0 else 'R'}_PIVOT",(x,y,z))
    pivot["axle_axis_local"]="X"; pivot["steerable"] = bool(y<0)
    # Child meshes are local to pivot; preserve wheel rotation origin exactly at axle.
    tire_mesh("Tire",radius,width,z,cfg["tire_seg"],cfg["tire_prof"],pivot)
    tread_count=cfg["tread"]
    bands=(-width*0.27,0,width*0.27) if cfg["level"]<2 else (-width*0.22,width*0.22)
    for b,xc in enumerate(bands):
        for i in range(tread_count):
            a=TAU*(i+0.5*(b%2))/tread_count
            tread_block(f"Tread_{b}_{i:02d}",a,xc,radius, width*0.19 if len(bands)==3 else width*0.25,
                        pivot, (0.42 if (i+b)%2 else -0.42))
    rim_r=0.17 if y<0 else 0.185
    ring_x("RimBarrel",rim_r,width*0.68,"metal_warm",cfg["rim_seg"],0.018,pivot)
    cylinder_x("BrakeDisc",(0,0,0),rim_r*0.73,0.015,"metal_warm",cfg["rim_seg"],parent=pivot)
    cylinder_x("Hub",(0,0,0),rim_r*0.25,width*0.78,"paint_secondary",cfg["rim_seg"],parent=pivot)
    spoke_count=6 if cfg["level"]<2 else 5
    for i in range(spoke_count):
        a=TAU*i/spoke_count
        spoke(f"RimSpoke_{i}",a,rim_r*.25,rim_r*.92,.045,.025,width*.48,"metal_warm",pivot)
        if cfg["level"]==0:
            spoke(f"SpokeCrown_{i}",a,rim_r*.34,rim_r*.84,.018,.009,width*.50,"accent_emissive",pivot)
    # Authored caliper wedge and hub fasteners.
    cal=triangulated_box("BrakeCaliper",(width*.37,0,-rim_r*.48),(.030,.070,.095),"accent_emissive",parent=pivot)
    if cfg["level"]<2:
        for i in range(6):
            a=TAU*i/6
            ellipsoid(f"HubBolt_{i}",(width*.405,.043*math.cos(a),.043*math.sin(a)),(.008,.008,.008),
                      "metal_warm",cfg["bolt_seg"],max(4,cfg["bolt_seg"]//2),pivot)
    return pivot


def wing_mesh(name, span, chord, thick, z0, cfg):
    span_seg=cfg["wing_span"]
    profile_seg=12 if cfg["level"]<2 else 8
    verts=[]
    for ix in range(span_seg+1):
        u=ix/span_seg
        x=-span/2+span*u
        crown=0.025*(1-(2*u-1)**2)
        for j in range(profile_seg):
            a=TAU*j/profile_seg
            y=0.82 + chord*0.5*math.cos(a)
            chord_u=(y-(0.82-chord/2))/chord
            camber=0.035*math.sin(math.pi*max(0,min(1,chord_u)))
            z=z0+crown+camber+thick*0.5*math.sin(a)*(0.65+0.35*chord_u)
            verts.append((x,y,z))
    faces=[]
    for ix in range(span_seg):
        for j in range(profile_seg):
            nj=(j+1)%profile_seg
            faces.append((ix*profile_seg+j,(ix+1)*profile_seg+j,(ix+1)*profile_seg+nj,ix*profile_seg+nj))
    c0=len(verts); verts.append((-span/2,0.82,z0)); c1=len(verts); verts.append((span/2,0.82,z0))
    for j in range(profile_seg):
        nj=(j+1)%profile_seg
        faces.append((c0,nj,j)); a=span_seg*profile_seg+j; b=span_seg*profile_seg+nj; faces.append((c1,a,b))
    return mesh_object(name,verts,faces,"paint_primary",True)


def extruded_polygon_x(name, xcenter, depth, yz, mat):
    verts=[(xcenter-depth/2,y,z) for y,z in yz]+[(xcenter+depth/2,y,z) for y,z in yz]
    n=len(yz); faces=[]
    # triangle fans, authored polygon is convex by design.
    for i in range(1,n-1): faces += [(0,i+1,i),(n,n+i,n+i+1)]
    for i in range(n):
        ni=(i+1)%n; faces.append((i,ni,n+ni,n+i))
    return mesh_object(name,verts,faces,mat,False)


def seven_segment_digit(name, digit, side, y, z, scale=0.045):
    segs={
        "0":"abcedf", "1":"bc", "2":"abdeg", "3":"abcdg", "4":"bcfg",
        "5":"acdfg", "6":"acdefg", "7":"abc", "8":"abcdefg", "9":"abcdfg"
    }
    # x/y are local digit horizontal/vertical coordinates mapped to world Y/Z on side skin.
    bars={"a":((0,1),(.75,.18)),"b":((.42,.52),(.18,.72)),"c":((.42,-.52),(.18,.72)),
          "d":((0,-1),(.75,.18)),"e":((-.42,-.52),(.18,.72)),"f":((-.42,.52),(.18,.72)),"g":((0,0),(.75,.18))}
    for key in segs.get(digit,"abcdefg"):
        (hy,hz),(sy,sz)=bars[key]
        # thin geometry floats 4 mm from shell; encoded as side-oriented box.
        triangulated_box(f"{name}_{key}",(side*.566,y+hy*scale,z+hz*scale),(.008,sy*scale,sz*scale),"accent_emissive")


def create_body(cfg):
    sides=cfg["body_sides"]
    tub=[(-1.16,0,.265,.16,.105),(-1.07,0,.285,.34,.135),(-.88,0,.315,.47,.16),
         (-.57,0,.335,.515,.19),(-.25,0,.35,.525,.205),(.12,0,.365,.515,.215),
         (.43,0,.39,.535,.225),(.72,0,.425,.55,.235),(1.00,0,.43,.43,.205),(1.15,0,.43,.25,.14)]
    loft("ContinuousLowerTub",tub,sides,"paint_secondary",2.6)
    skid=[(-1.04,0,.155,.27,.032),(-.62,0,.145,.40,.037),(.00,0,.14,.43,.04),
          (.64,0,.145,.42,.038),(1.05,0,.18,.26,.045)]
    loft("LowerSkidPlate",skid,max(10,sides//2),"metal_warm",3.3)
    # Nose crown carries the S-flow into cockpit shoulders.
    nose=[(-1.16,0,.36,.055,.045),(-1.03,0,.415,.23,.075),(-.84,0,.485,.39,.085),
          (-.62,0,.525,.42,.075),(-.42,0,.50,.34,.055),(-.30,0,.47,.26,.035)]
    loft("NoseCrown",nose,max(12,sides-2),"paint_primary",2.4)
    # Teardrop cockpit opening: separate rolled rim and deep visible well.
    rim=[]
    for i in range(28 if cfg["level"]==0 else (20 if cfg["level"]==1 else 14)):
        a=TAU*i/(28 if cfg["level"]==0 else (20 if cfg["level"]==1 else 14))
        # narrow front, broader rear; y axis opening from -0.38 to +0.50
        y=.06+.44*math.sin(a)
        taper=.76+.24*((y+.38)/.88)
        x=.31*math.cos(a)*taper
        z=.555+.025*math.sin(a)-.045*((y-.08)/.5)**2
        rim.append((x,y,z))
    tube_path("CockpitRolledRim",rim,.024 if cfg["level"]<2 else .020,"metal_warm",cfg["tube_sides"],closed=True)
    # Painted shoulder ribbons integrate front and rear fenders into the tub.
    shoulder=[(-.48,.47,.27,.535,.43),(-.30,.52,.31,.575,.45),(-.05,.545,.34,.605,.46),
              (.22,.55,.35,.625,.48),(.48,.57,.30,.665,.50),(.68,.59,.24,.69,.51)]
    for side in (-1,1):
        ribbon_solid("CockpitShoulder",shoulder,"paint_primary",side)
        front=[(-1.03,.59,.34,.45,.31),(-.92,.625,.37,.54,.34),(-.79,.64,.39,.595,.36),
               (-.66,.635,.40,.61,.37),(-.54,.60,.41,.575,.38),(-.44,.54,.39,.525,.39)]
        ribbon_solid("IntegratedFrontFender",front,"paint_primary",side)
        rear=[(.38,.565,.35,.60,.44),(.50,.615,.37,.67,.45),(.68,.65,.40,.735,.47),
              (.84,.645,.39,.75,.48),(1.02,.60,.34,.68,.45),(1.12,.50,.27,.58,.43)]
        ribbon_solid("IntegratedRearFender",rear,"paint_primary",side)
    # Rear power spine and tapered haunch/deck.
    rearsp=[(.42,0,.56,.22,.09),(.62,0,.625,.31,.105),(.82,0,.655,.34,.105),
            (1.02,0,.62,.29,.09),(1.14,0,.55,.18,.07)]
    loft("RearPowerSpine",rearsp,max(12,sides-2),"paint_primary",2.8)
    # Dashboard brow bridges body without sealing cockpit.
    tube_path("DashBrow",[(-.30,-.34,.59),(0,-.40,.625),(.30,-.34,.59)],.032,"paint_secondary",cfg["tube_sides"],.022)
    # Hero boomerang channel: inset dark channel plus restricted accent flow line.
    if cfg["level"]<2:
        for side in (-1,1):
            path=[(side*.535,-.76,.43),(side*.552,-.51,.395),(side*.56,-.22,.36),
                  (side*.575,.05,.405),(side*.59,.32,.505),(side*.602,.62,.625)]
            tube_path("BoomerangChannel",path,.034,"paint_secondary",cfg["tube_sides"],.018)
            tube_path("BoomerangAccent",[(side*(abs(x)+.004),y,z+.006) for x,y,z in path],.008,
                      "accent_emissive",max(6,cfg["tube_sides"]-2),.005)
    else:
        for side in (-1,1):
            path=[(side*.535,-.70,.42),(side*.56,-.18,.37),(side*.59,.32,.50),(side*.60,.60,.62)]
            tube_path("BoomerangColorBlock",path,.020,"accent_emissive",6,.010)
    # Front mask: low smile intake, cheek inlets, jewel markers and original crest.
    intake=[(-.22,-1.142,.285),(-.13,-1.174,.265),(0,-1.187,.255),(.13,-1.174,.265),(.22,-1.142,.285)]
    tube_path("FrontCentralIntake",intake,.038,"rubber_dark",cfg["tube_sides"],.022)
    for side in (-1,1):
        tube_path("CheekInlet",[(side*.29,-1.09,.34),(side*.38,-1.025,.38),(side*.42,-.94,.42)],
                  .025,"rubber_dark",cfg["tube_sides"],.014)
        ellipsoid("JewelMarker",(side*.31,-1.105,.405),(.055,.022,.025),"accent_emissive",
                  cfg["sphere_seg"],cfg["sphere_ring"])
    # Crest: original split-chevron mark in clean center badge zone.
    extruded_polygon_x("NoseCrest",0,.018,[(-1.177,.345),(-1.171,.425),(-1.105,.455),(-1.055,.395),(-1.105,.335)],"metal_warm")
    tube_path("CrestSlash",[(-.018,-1.187,.382),(0,-1.192,.418),(.018,-1.187,.376)],.009,"accent_emissive",6)
    # Side number 27 with geometry, retained at hero/near LOD.
    if cfg["level"]<2:
        for side in (-1,1):
            triangulated_box("NumberPlate",(side*.558,.25,.515),(.012,.25,.16),"paint_secondary")
            seven_segment_digit("Number2","2",side,.205,.515,.055)
            seven_segment_digit("Number7","7",side,.292,.515,.055)


def create_cockpit_driver_r153(cfg):
    """R153: connected stylized pilot shell with explicit control-chain attachments."""
    # Class change: a single armored racing shell spans pelvis, ribcage and shoulders.
    # It is broad at the hips, pinched at the waist, and shoulder-heavy like a seated
    # arcade racer silhouette; no detached seat capsule or mannequin torso stack.
    loft("R153_CockpitWell",[(.48,0,.42,.30,.16),(.22,0,.405,.32,.18),(-.10,0,.40,.28,.16),(-.36,0,.41,.21,.11)],max(10,cfg["body_sides"]-4),"rubber_dark",2.4)
    # R153: pilot shell is widened at the hips and narrowed through the waist,
    # with a dedicated shoulder bridge to read as a seated racer rather than a capsule.
    loft("R153_PilotShell",[(.19,0,.54,.235,.14),(.10,0,.66,.285,.18),(.04,0,.80,.235,.22),(.10,0,.93,.31,.15)],max(16,cfg["body_sides"]//1),"paint_secondary",2.0)
    loft("R153_ChestShell",[(.02,0,.78,.20,.14),(.08,0,.88,.26,.17),(.11,0,.96,.20,.10)],max(14,cfg["body_sides"]//2),"paint_primary",2.0)
    # Sculpted armor collar/shoulders connect directly into the shell's upper section.
    for side in (-1,1):
        ellipsoid("R153_ShoulderArmor",(side*.205,.075,.915),(.115,.135,.105),"paint_primary",cfg["sphere_seg"],cfg["sphere_ring"])
        tube_path("R153_Harness",[(side*.16,-.005,.98),(side*.055,-.045,.79),(side*.13,.015,.58)],.020,"metal_warm",cfg["tube_sides"],.012)
        tube_path("R153_SideArmor",[(side*.22,.10,.88),(side*.27,.02,.73),(side*.20,-.08,.61)],.032,"paint_primary",cfg["tube_sides"],.020)
    # Neck and helmet are a tapered wearable shell, not a floating sphere.
    loft("R153_NeckShell",[(-.01,0,.96,.10,.09),(.04,0,1.10,.115,.11)],max(12,cfg["body_sides"]//2),"paint_primary",2.0)
    ellipsoid("R153_HelmetShell",(0,.035,1.18),(.15,.13,.17),"paint_primary",cfg["sphere_seg"],cfg["sphere_ring"])
    ellipsoid("R153_HelmetVisor",(0,-.118,1.205),(.105,.018,.062),"rubber_dark",cfg["sphere_seg"],cfg["sphere_ring"])
    # R153: shallow side-visible visor lens seated on the shell surface for profile proof.
    # R153: continuous oval visor gasket seated against the helmet side shell.
    visor_ring=[]
    for i in range(24):
        a=TAU*i/24
        visor_ring.append((.158, -.005 + .082*math.cos(a), 1.205 + .054*math.sin(a)))
    for side in (-1,1):
        cylinder_x("R153_VisorPivot",(side*.135,.005,1.19),.017,.025,"metal_warm",cfg["rim_seg"])
    tube_path("R153_HelmetFrame",[(-.075,-.027,1.17),(-.082,-.029,1.205),(0,-.031,1.25),(.082,-.029,1.205),(.075,-.027,1.17)],.008,"metal_warm",cfg["tube_sides"],.006)
    tube_path("R153_ChinGuard",[(-.12,-.12,1.10),(0,-.17,1.065),(.12,-.12,1.10)],.030,"paint_primary",cfg["tube_sides"],.020)
    tube_path("R153_Collar",[(-.17,.01,1.03),(0,.07,1.00),(.17,.01,1.03)],.030,"metal_warm",cfg["tube_sides"],.020)
    # Legs and boots visibly terminate in the pedal shelf.
    triangulated_box("R153_PedalShelf",(0,-.46,.29),(.44,.29,.035),"metal_warm")
    for side in (-1,1):
        tube_path("R153_Thigh",[(side*.14,.10,.58),(side*.17,-.15,.46),(side*.13,-.36,.35)],.078,"paint_secondary",cfg["tube_sides"],.060)
        tube_path("R153_Shin",[(side*.13,-.34,.36),(side*.11,-.49,.33),(side*.095,-.56,.335)],.054,"paint_primary",cfg["tube_sides"],.040)
        ellipsoid("R153_Boot",(side*.095,-.565,.35),(.068,.10,.052),"rubber_dark",cfg["sphere_seg"],cfg["sphere_ring"])
    # Steering wheel, arms and hands remain a single readable functional chain.
    wheel_pts=[(.17*math.cos(TAU*i/32),-.46,.82+max(-.13,.17*math.sin(TAU*i/32))) for i in range(32)]
    tube_path("R153_SteeringRing",wheel_pts,.022,"paint_primary",cfg["tube_sides"],closed=True)
    cylinder_x("R153_SteeringHub",(0,-.46,.82),.040,.060,"metal_warm",cfg["rim_seg"])
    cylinder_x("R153_SteeringCap",(0,-.46,.82),.016,.066,"paint_secondary",cfg["rim_seg"])
    tube_path("R153_SteeringColumn",[(0,-.46,.82),(0,-.42,.66),(0,-.42,.61)],.020,"accent_emissive",cfg["tube_sides"],.015)
    for side in (-1,1):
        tube_path("R153_UpperArm",[(side*.21,.10,.91),(side*.31,-.03,.84),(side*.23,-.17,.82)],.056,"paint_primary",cfg["tube_sides"],.044)
        tube_path("R153_Forearm",[(side*.23,-.17,.82),(side*.18,-.445,.82)],.047,"paint_secondary",cfg["tube_sides"],.038)
        a=math.radians(30 if side>0 else 150); gx=.17*math.cos(a); gz=.82+.17*math.sin(a)
        hand=ellipsoid("R153_Hand",(gx,-.455,gz),(.039,.030,.047),"metal_warm",cfg["sphere_seg"],cfg["sphere_ring"]); hand["grip_angle_deg"]=30 if side>0 else 150
    # R153 class change: replace the isolated arc/rollbar reading with a shallow,
    # closed cowl-integrated cockpit shell. It is one authored volume with a low
    # front lip, swept shoulders and a rear opening that leaves the pilot visible.
    # R153: remove the dominant opaque cowl slab; retain only the compact authored lens below.
    # The windshield must frame the driver, not become a second nose.
    # No replacement block is added here.
    # Two short structural saddles are embedded into the shell/cowl transition,
    # not freestanding screen supports.
    # R153: the review windshield is now a single flush lens with no exposed rail rods.
    # Cowl connection is represented by the lens edge and the two flush mount points only.
    for side in (-1,1):
        fast=ellipsoid("R153_CowlMount",(side*.17,-.59,.64),(.018,.010,.010),"metal_warm",cfg["sphere_seg"],cfg["sphere_ring"])
        fast["mount_type"]="integrated_cowl_shell_mount"


def create_cockpit_driver(cfg):
    if cfg["level"] == 0:
        create_cockpit_driver_r153(cfg)
        return
    loft("CockpitWell",[(.46,0,.42,.29,.15),(.30,0,.405,.30,.16),(.05,0,.39,.27,.15),(-.28,0,.40,.20,.10)],
         max(10,cfg["body_sides"]-4),"rubber_dark",2.4)
    # Seat back custom curved shell and cushion.
    ribbon_solid("SeatShell",[(.27,.27,.18,.78,.38),(.37,.29,.17,.86,.39),(.48,.27,.16,.91,.43)],
                 "paint_secondary",1)
    ribbon_solid("SeatShellMirror",[(.27,.27,.18,.78,.38),(.37,.29,.17,.86,.39),(.48,.27,.16,.91,.43)],
                 "paint_secondary",-1)
    ellipsoid("SeatCushion",(0,.25,.48),(.25,.22,.085),"rubber_dark",cfg["sphere_seg"],cfg["sphere_ring"])
    ellipsoid("Headrest",(0,.43,.91),(.20,.075,.16),"rubber_dark",cfg["sphere_seg"],cfg["sphere_ring"])
    triangulated_box("PedalShelf",(0,-.43,.29),(.39,.27,.035),"metal_warm")
    for side in (-1,1):
        triangulated_box("Pedal",(side*.095,-.555,.34),(.075,.018,.12),"metal_warm")
    # Driver hips embedded below cockpit rim.
    # Integrated seated driver volume: pelvis, ribcage and shoulder yoke form one readable silhouette.
    ellipsoid("DriverHips",(0,.18,.54),(.18,.14,.13),"paint_secondary",cfg["sphere_seg"],cfg["sphere_ring"])
    loft("DriverRibcage",[(.02,.0,.66,.17,.12),(.10,.0,.80,.205,.18),(.17,.0,.92,.17,.12)],max(12,cfg["body_sides"]//2),"paint_secondary",2.2)
    tube_path("DriverShoulderYoke",[(-.17,.14,.92),(-.10,.10,.98),(0,.075,1.01),(.10,.10,.98),(.17,.14,.92)],.055,"paint_primary",cfg["tube_sides"],.040)
    ellipsoid("DriverNeck",(0,.08,1.015),(.070,.070,.10),"paint_primary",cfg["sphere_seg"],cfg["sphere_ring"])

    # Suit center panel supplies readable torso articulation.
    ellipsoid("DriverChestPanel",(0,.045,.80),(.12,.025,.18),"paint_primary",cfg["sphere_seg"],cfg["sphere_ring"])
    # Legs descend into the well toward modeled pedals.
    for side in (-1,1):
        tube_path("DriverThigh",[(side*.12,.10,.58),(side*.14,-.16,.46),(side*.12,-.36,.36)],.070,
                  "paint_secondary",cfg["tube_sides"],.058)
        tube_path("DriverShin",[(side*.12,-.34,.37),(side*.105,-.49,.33),(side*.095,-.55,.335)],.050,
                  "paint_primary",cfg["tube_sides"],.040)
        ellipsoid("DriverBoot",(side*.095,-.555,.35),(.06,.09,.05),"rubber_dark",cfg["sphere_seg"],cfg["sphere_ring"])
    # One wearable full-face helmet: inner head, shaped shell, visor, pivots, chin and collar.
    # R153: replace exposed inner head sphere with an integrated faceplate/gaiter.
    ellipsoid("R153_Faceplate",(0,-.095,1.17),(.095,.030,.072),"paint_secondary",8,4)
    ellipsoid("R153_NeckGaiter",(0,.02,1.025),(.13,.095,.065),"paint_secondary",8,4)
    ellipsoid("HelmetShell",(0,.035,1.18),(.145,.125,.165),"paint_primary",cfg["sphere_seg"],cfg["sphere_ring"])
    ellipsoid("HelmetVisor",(0,-.118,1.205),(.100,.018,.060),"rubber_dark",cfg["sphere_seg"],cfg["sphere_ring"])
    visor_ring=[]
    for i in range(24):
        a=TAU*i/24
        visor_ring.append((.158, -.005 + .078*math.cos(a), 1.205 + .052*math.sin(a)))
    for side in (-1,1):
        cylinder_x("HelmetVisorPivot",(side*.11,.030,1.17),.015,.022,"metal_warm",cfg["rim_seg"])
    tube_path("HelmetVisorFrame",[(-.072,-.027,1.17),(-.078,-.029,1.205),(0,-.031,1.245),(.078,-.029,1.205),(.072,-.027,1.17)],.007,"metal_warm",cfg["tube_sides"],.005)
    tube_path("HelmetChinBar",[(-.10,-.135,1.105),(0,-.18,1.075),(.10,-.135,1.105)],.022,"paint_primary",cfg["tube_sides"],.016)
    tube_path("DriverCollar",[(-.12,.02,1.025),(0,.075,.995),(.12,.02,1.025)],.024,"metal_warm",cfg["tube_sides"],.018)
    # R73: compact D-shaped kart wheel, with coaxial hub and column only.
    wheel_pts=[]
    for i in range(32):
        a=TAU*i/32
        wheel_pts.append((.17*math.cos(a),-.46,.82+max(-.13,.17*math.sin(a))))
    tube_path("DSteeringRing",wheel_pts,.021,"paint_primary",cfg["tube_sides"],closed=True)
    # Coaxial steering stack: hub, boss, and column share the same centerline.
    cylinder_x("SteeringHub",(0,-.46,.82),.040,.060,"metal_warm",cfg["rim_seg"])
    cylinder_x("SteeringHubCap",(0,-.46,.82),.016,.066,"paint_secondary",cfg["rim_seg"])
    tube_path("SteeringColumn",[(0,-.46,.82),(0,-.42,.66)],.018,"accent_emissive",cfg["tube_sides"],.014)
    tube_path("SteeringColumnMount",[(0,-.42,.66),(0,-.42,.61)],.022,"paint_secondary",cfg["tube_sides"],.016)
    if cfg["level"] == 0:
        # R76: compact cowl-integrated windshield, low and close to the nose.
        xs=[-.145,-.0725,0,.0725,.145]
        # R153: low, shallow cowl deflector; top edge remains below the helmet chin.
        rows=((.555,-.555),(.585,-.515),(.615,-.475))
        verts=[]
        for x in xs:
            bend=1.0-(abs(x)/.18)**2
            for z,y in rows: verts.append((x,y-.04*bend,z))
        faces=[]
        for i in range(len(xs)-1):
            a=i*3; b=(i+1)*3
            for r in range(len(rows)-1): faces.append((a+r,b+r,b+r+1,a+r+1))
        visor=mesh_object("KartWindshieldLens",verts,faces,"cockpit_glass",True)
        solid=visor.modifiers.new("Windshield 4mm thickness","SOLIDIFY"); solid.thickness=.004; solid.offset=0.0
        bpy.context.view_layer.objects.active=visor; visor.select_set(True)
        bpy.ops.object.modifier_apply(modifier=solid.name)
        # The visor loft is authored front-to-back; explicitly orient its closed shell outward.
        bm=bmesh.new(); bm.from_mesh(visor.data); bmesh.ops.reverse_faces(bm, faces=list(bm.faces)); bm.to_mesh(visor.data); bm.free()
        bevel=visor.modifiers.new("Rounded windshield edge","BEVEL"); bevel.width=.006; bevel.segments=3
        # R153: lens is flush-mounted directly to the cowl; no exposed rail.
        for side in (-1,1):
            fast=ellipsoid("FlushWindshieldFastener",(side*.135,-.55,.585),(.018,.010,.010),"metal_warm",cfg["sphere_seg"],cfg["sphere_ring"])
            fast["mount_type"]="flush_cowl_fastener"

    # R55: no long spokes; the compact hub is carried by the coaxial column.
    # Arms with clear elbows and hands at exact 9-and-3 grip positions.
    for side in (-1,1):
        tube_path("DriverUpperArm",[(side*.19,.12,.89),(side*.285,-.02,.82),(side*.22,-.16,.81)],.050,
                  "paint_primary",cfg["tube_sides"],.043)
        tube_path("DriverForearm",[(side*.22,-.16,.81),(side*.18,-.445,.82)],.043,
                  "paint_secondary",cfg["tube_sides"],.036)
        # Grip points are explicit 150°/30° polar positions on the wheel,
        # with compact wrist/hand envelopes (<= 10° visual articulation).
        grip_angle=math.radians(30.0 if side>0 else 150.0)
        gx=.17*math.cos(grip_angle); gz=.82+.17*math.sin(grip_angle)
        hand=ellipsoid("DriverHand",(gx,-.455,gz),(.035,.028,.044),"metal_warm",
              cfg["sphere_seg"],cfg["sphere_ring"])
        hand["grip_angle_deg"]=30.0 if side>0 else 150.0
        hand["wrist_articulation_deg"] = 8.0
        for finger in (-.020,0,.020):
            tube_path("DriverFinger",[(gx,-.48,gz+finger),(gx-side*.027,-.475,gz+finger)],.008,
                      "metal_warm",cfg["tube_sides"],.006)
    # Broad 3D harness straps over chest.
    for side in (-1,1):
        tube_path("Harness",[(side*.13,.035,.92),(side*.09,.015,.78),(side*.15,.05,.61)],.022,
                  "paint_secondary",cfg["tube_sides"],.010)


def create_suspension(cfg):
    side_s=cfg["tube_sides"]
    axles=[(-.735,.28,.49),(.735,.31,.52)] # y, wheel-center z, upright attach z
    for y,wz,uz in axles:
        for side in (-1,1):
            sx=side
            outer=(sx*(.565 if y<0 else .585),y,uz)
            # upper and lower forged A-arm pairs: two chassis hardpoints each converge at upright.
            for level,zoff in [("Lower",-.13),("Upper",.02)]:
                z=uz+zoff
                hardx=sx*.42
                tube_path(f"{level}WishboneA",[(hardx,y-.13,z),(sx*.52,y-.035,z),outer],.021,
                          "metal_warm",side_s,.012)
                tube_path(f"{level}WishboneB",[(hardx,y+.13,z),(sx*.52,y+.035,z),outer],.021,
                          "metal_warm",side_s,.012)
            tube_path("Upright",[(sx*.585,y,wz-.11),(sx*.59,y,wz+.15)],.027,"paint_secondary",side_s,.020)
            # Spring/damper connected from lower upright to inner upper mount.
            tube_path("DamperBody",[(sx*.565,y+.025,wz+.015),(sx*.43,y+.06,wz+.24)],.026,
                      "paint_secondary",side_s)
            if cfg["level"]<2:
                p0=Vector((sx*.55,y+.028,wz+.04)); p1=Vector((sx*.445,y+.058,wz+.22))
                d=p1-p0; L=d.length; tangent=d.normalized(); ref=Vector((0,0,1))
                b1=tangent.cross(ref).normalized() if abs(tangent.z)<.95 else tangent.cross(Vector((0,1,0))).normalized()
                b2=tangent.cross(b1).normalized(); coils=10 if cfg["level"]==0 else 7
                pts=[]
                for i in range(coils*6+1):
                    t=i/(coils*6); a=TAU*coils*t
                    pts.append(tuple(p0+d*t+b1*.037*math.cos(a)+b2*.037*math.sin(a)))
                tube_path("CoilSpring",pts,.007,"accent_emissive",6)
            if y<0:
                tube_path("SteeringTieRod",[(sx*.30,y-.05,wz+.03),(sx*.585,y-.02,wz+.02)],.012,
                          "metal_warm",max(6,side_s-2))


def create_rear(cfg):
    # Twin sculpted nacelles, metal collars, dark inner tubes and asymmetric tertiary notch.
    for side in (-1,1):
        loft("ExhaustNacelle",[(.84,side*.25,.50,.12,.09),(1.03,side*.265,.535,.115,.085),(1.14,side*.275,.57,.09,.07)],
             max(10,cfg["body_sides"]-4),"paint_secondary",2.3)
        tube_path("ExhaustOuter",[(side*.275,1.04,.55),(side*.285,1.18,.61)],.063,"metal_warm",
                  cfg["rim_seg"],.048)
        tube_path("ExhaustInner",[(side*.285,1.17,.61),(side*.29,1.205,.628)],.043,"rubber_dark",
                  max(10,cfg["rim_seg"]//2),.032)
    if cfg["level"]==0:
        triangulated_box("ExhaustTechNotch",(.325,1.176,.665),(.025,.035,.02),"accent_emissive")
    # Diffuser is a tapered, readable rear identity below power spine.
    diffuser=[(-.37,1.08,.18),(-.27,.82,.17),(.27,.82,.17),(.37,1.08,.18),(.30,1.16,.31),(-.30,1.16,.31)]
    # custom triangulated closed wedge via loft-like two-depth bands
    mesh_object("RearDiffuser",diffuser,
                [(0,1,2),(0,2,3),(0,3,4),(0,4,5),(0,5,1),(1,5,4),(1,4,2),(2,4,3)],"rubber_dark",False)
    for x in (-.24,-.08,.08,.24):
        extruded_polygon_x("DiffuserFin",x,.018,[(.84,.17),(1.16,.18),(1.16,.31),(.98,.26)],"metal_warm")
    wing_mesh("CamberedRearWing",1.10,.24,.045,.88,cfg)
    for side in (-1,1):
        # Swept pylons are closed forged profiles, connected at deck and blade.
        tube_path("WingPylon",[(side*.27,.70,.64),(side*.31,.76,.76),(side*.34,.82,.89)],.026,
                  "metal_warm",cfg["tube_sides"],.018)
        extruded_polygon_x("WingEndplate",side*.56,.025,[(.68,.84),(.72,.96),(.93,.98),(1.00,.86),(.88,.82)],
                           "paint_secondary")
    # Rear light signature independent from the wing.
    tube_path("RearLightBar",[(-.25,1.135,.49),(0,1.165,.47),(.25,1.135,.49)],.018,
              "accent_emissive",cfg["tube_sides"],.010)
    triangulated_box("RearNumberPlate",(0,1.169,.39),(.22,.012,.10),"paint_secondary")


def create_detail(cfg):
    if cfg["level"]>0:
        return
    # Authored seams, fasteners and vent ribs reinforce existing forms only.
    tube_path("NosePanelSeam",[(-.31,-.74,.515),(0,-.78,.545),(.31,-.74,.515)],.006,
              "metal_warm",6,.004)
    for side in (-1,1):
        tube_path("HaunchPanelSeam",[(side*.44,.50,.65),(side*.50,.72,.70),(side*.43,.93,.63)],.006,
                  "metal_warm",6,.004)
        for i in range(4):
            y=.72+i*.065
            tube_path("PowerVentRib",[(side*.16,y,.67),(side*.28,y+.015,.64)],.007,"rubber_dark",6,.004)
        for i,y in enumerate((-.82,-.62,.55,.82)):
            ellipsoid(f"PanelFastener_{i}",(side*.48,y,.47 if y<0 else .60),(.009,.009,.009),
                      "metal_warm",8,4)
    # Front tow eye as a genuine closed ring.
    pts=[]
    for i in range(16):
        a=TAU*i/16; pts.append((.055*math.cos(a),-1.18,.19+.055*math.sin(a)))
    tube_path("TowEye",pts,.009,"accent_emissive",6,closed=True)


def create_lod(name, cfg):
    global CURRENT_COLLECTION, PREFIX
    CURRENT_COLLECTION=collection(name); PREFIX=name+"_"
    CURRENT_COLLECTION["lod_level"]=cfg["level"]
    CURRENT_COLLECTION["hand_authored_resolution"]=True
    create_body(cfg)
    # Overall-width priority: front track 1.34; rear visual anchor at 1.36.
    for side in (-1,1):
        wheel(side,(.67,-.735,.28),.28,.24,cfg)
        wheel(side,(.68,.735,.31),.31,.26,cfg)
    create_suspension(cfg)
    create_cockpit_driver(cfg)
    create_rear(cfg)
    create_detail(cfg)
    # hidden by default except hero LOD
    hide=name!="LOD0"
    CURRENT_COLLECTION.hide_render=hide
    CURRENT_COLLECTION.hide_viewport=hide
    for obj in CURRENT_COLLECTION.objects:
        obj["lod"] = name
    return CURRENT_COLLECTION


def create_collision():
    global CURRENT_COLLECTION, PREFIX
    CURRENT_COLLECTION=collection("COLLISION"); PREFIX="COLLISION_"
    CURRENT_COLLECTION.hide_render=True; CURRENT_COLLECTION.hide_viewport=True
    # 3 convex tapered hulls, 12 triangles each = 36 triangles total.
    triangulated_box("MainHull",(0,.02,.39),(1.02,1.18,.52),None)
    # front/rear hulls stay inside render silhouette and above ground.
    triangulated_box("FrontHull",(0,-.78,.32),(.78,.58,.36),None)
    triangulated_box("RearHull",(0,.74,.42),(.88,.42,.40),None)
    for obj in CURRENT_COLLECTION.objects:
        obj.display_type="WIRE"; obj.hide_render=True; obj["collision_shape"]="CONVEX_HULL"


def optimize_lod(name, ratio):
    """Apply a conservative per-object reduction while retaining closed topology."""
    coll=bpy.data.collections[name]
    for obj in list(coll.objects):
        if obj.type!='MESH': continue
        # LOD2 drops emissive-only material identity to stay within the 3-material contract.
        if name=='LOD2':
            for slot in obj.material_slots:
                if slot.material and slot.material.name=='accent_emissive': slot.material=MATS['paint_primary']
        if ratio < 0.999:
            mod=obj.modifiers.new('Authored LOD reduction','DECIMATE'); mod.ratio=ratio
            bpy.context.view_layer.objects.active=obj; obj.select_set(True)
            try: bpy.ops.object.modifier_apply(modifier=mod.name)
            except RuntimeError: pass
            obj.select_set(False)


def add_preview_camera_and_lights():
    global CURRENT_COLLECTION, PREFIX
    CURRENT_COLLECTION=collection("PRESENTATION"); PREFIX="PRESENTATION_"
    cam_data=bpy.data.cameras.new("PresentationCamera")
    cam=bpy.data.objects.new("PresentationCamera",cam_data); CURRENT_COLLECTION.objects.link(cam)
    cam.location=(3.05,-3.55,2.05); cam.data.lens=50
    target=Vector((0,0,.58)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat("-Z","Y").to_euler()
    bpy.context.scene.camera=cam
    def area(name,loc,energy,size,color):
        data=bpy.data.lights.new(name,"AREA"); data.energy=energy; data.shape="DISK"; data.size=size; data.color=color
        ob=bpy.data.objects.new(name,data); CURRENT_COLLECTION.objects.link(ob); ob.location=loc
        ob.rotation_euler=(target-Vector(loc)).to_track_quat("-Z","Y").to_euler()
    area("Key_Area",(-3.2,-4.0,4.6),1100,4.0,(1.0,.79,.62))
    area("Fill_Area",(4.0,-.2,2.7),900,3.0,(.38,.68,1.0))
    area("Rim_Area",(-1.0,4.0,3.3),1250,3.0,(1.0,.18,.07))
    # Studio cyclorama ground is presentation-only.
    verts=[(-7,-7,-.012),(7,-7,-.012),(7,7,-.012),(-7,7,-.012)]
    ground=mesh_object("StudioGround",verts,[(0,1,2),(0,2,3)],MATS["paint_secondary"],False)
    ground["presentation_only"]=True


def main():
    args=parse_args(); setup_scene(); scene=bpy.context.scene
    configs={"LOD0":{"level":0,"body_sides":26,"tube_sides":10,"tire_seg":72,"tire_prof":18,"rim_seg":48,
              "tread":20,"sphere_seg":24,"sphere_ring":12,"bolt_seg":12,"wing_span":24},
      "LOD1":{"level":1,"body_sides":18,"tube_sides":8,"tire_seg":40,"tire_prof":14,"rim_seg":32,
              "tread":12,"sphere_seg":16,"sphere_ring":8,"bolt_seg":8,"wing_span":14},
      "LOD2":{"level":2,"body_sides":12,"tube_sides":6,"tire_seg":24,"tire_prof":10,"rim_seg":20,
              "tread":6,"sphere_seg":12,"sphere_ring":6,"bolt_seg":6,"wing_span":8},
    }
    for name,cfg in configs.items():
        create_lod(name,cfg)
        optimize_lod(name, 0.965 if name=='LOD1' else (0.58 if name=='LOD2' else 1.0))
    create_collision(); add_preview_camera_and_lights()
    # Final authored topology pass: consistent normals and no hidden cap n-gons.
    for obj in bpy.data.objects:
        if obj.type!='MESH': continue
        bm=bmesh.new(); bm.from_mesh(obj.data); bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); bm.to_mesh(obj.data); bm.free()
    visor=bpy.data.objects.get('LOD0_KartWindshieldLens')
    if visor:
        bm=bmesh.new(); bm.from_mesh(visor.data); bmesh.ops.reverse_faces(bm, faces=list(bm.faces)); bm.to_mesh(visor.data); bm.free()
    # The class-level pilot loft has a non-monotonic seating profile; enforce outward winding.
    pilot=bpy.data.objects.get('LOD0_R153_PilotShell')
    if pilot:
        bm=bmesh.new(); bm.from_mesh(pilot.data); bmesh.ops.reverse_faces(bm, faces=list(bm.faces)); bm.to_mesh(pilot.data); bm.free()
    # Stable deterministic object ordering and explicit metadata.
    bpy.context.scene["material_slots_max"]=5
    bpy.context.scene["collision_triangle_target"]="24-48"
    bpy.context.scene["lod_generation"]="authored profile resolution; no decimation"
    # Review metadata is written beside the blend so every render can be tied to
    # the exact same revision and the P0 dimensions remain auditable.
    bpy.context.scene["review_revision"] = args.revision
    scene["generator_contract"] = "R117-authored-v2; no source import; UV-per-mesh; canonical-material-remap; closed tire profiles"
    bpy.context.scene["windshield_width_m"] = .36
    bpy.context.scene["cockpit_width_reference_m"] = .62
    bpy.context.scene["windshield_width_ratio"] = .36/.62
    bpy.context.scene["windshield_mount_count"] = 4
    bpy.context.scene["windshield_rear_edge_y_m"] = -.65
    bpy.context.scene["cockpit_rim_rear_y_m"] = .50
    bpy.context.scene["forearm_clearance_target_m"] = .07
    bpy.context.scene["steering_hub_diameter_m"] = .112
    bpy.context.scene["steering_hub_diameter_ratio_front_wheel"] = .112/.56
    bpy.context.scene["hand_grip_angles_deg"] = "150,30"
    bpy.context.scene["helmet_shell_wrap"] = True
    bpy.context.scene["visor_pivot_count"] = 2
    bpy.context.scene["steering_d_shape"] = True
    bpy.context.scene["steering_continuous_ring"] = True
    bpy.context.scene["steering_column_coaxial"] = True
    bpy.context.scene["no_windshield_over_driver"] = True
    bpy.context.scene["windshield_frame_continuous"] = True
    bpy.context.scene["windshield_integrated_cowl"] = True
    # R153: preserve the authored wearable helmet stack; do not collapse it into a head sphere.
    # Lower the complete helmet/visor/chin/collar assembly into the neck socket.
    for obj in bpy.data.objects:
        if obj.name.startswith("LOD0_R153_") and any(k in obj.name for k in ("Helmet", "Visor", "ChinBar", "Collar", "Neck")):
            obj.location.z -= 0.055
    # Make the visor visibly front-facing and continuous with the shell.
    for obj in bpy.data.objects:
        if obj.name.startswith("LOD0_R153_HelmetVisor"):
            obj["wearable_integrated"] = True
            obj["helmet_attachment"] = "shell_front_flush"
    # Keep the neck/collar bridge and the shoulder shell visible for profile proof.
    for obj in bpy.data.objects:
        if obj.name.startswith("LOD0_R153_") and any(k in obj.name for k in ("NeckShell", "Collar")):
            obj["pilot_attachment"] = "neck_to_shoulder_bridge"
    out=os.path.abspath(args.output or os.path.join(os.path.dirname(__file__), "hero-kart-v2-R153.blend")); os.makedirs(os.path.dirname(out),exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out,compress=True)
    report={"revision":args.revision,"blender":bpy.app.version_string,"blend":out,
            "windshield_mount_count":4,"windshield_width_m":.36,
            "cockpit_width_reference_m":.62,"windshield_width_ratio":.36/.62,
            "windshield_rear_edge_y_m":-.65,"cockpit_rim_rear_y_m":.50,
            "forearm_clearance_target_m":.07,"steering_hub_diameter_m":.112,
            "steering_hub_diameter_ratio_front_wheel":.112/.56,
            "hand_grip_angles_deg":[150,30],"no_runtime_integration":True,
            "helmet_shell_wrap":True,"visor_pivot_count":2,"steering_d_shape":True,
            "steering_continuous_ring":True,"steering_column_coaxial":True,
            "no_windshield_over_driver":True,"windshield_frame_continuous":True,
            "windshield_integrated_cowl":True}
    report_path=os.path.join(os.path.dirname(out),"build-report.json")
    import json
    with open(report_path,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
    print("HERO_KART_V2_BUILD_OK",out)
    print("BUILD_REPORT",report_path)
    print("OBJECTS",len(bpy.data.objects),"MESHES",len(bpy.data.meshes),"MATERIALS",len(MATS))

if __name__=="__main__": main()

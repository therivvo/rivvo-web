#!/usr/bin/env python3
"""Deterministic geometry audit for Hero Kart V2."""
import argparse
import json
import os
import bpy
import bmesh
from mathutils import Vector


def args():
    argv=__import__("sys").argv
    argv=argv[argv.index("--")+1:] if "--" in argv else []
    p=argparse.ArgumentParser(); p.add_argument("--blend",required=True); p.add_argument("--output",required=True)
    return p.parse_args(argv)


def mesh_triangles(mesh):
    mesh.calc_loop_triangles(); return len(mesh.loop_triangles)


def audit_collection(name):
    coll=bpy.data.collections[name]
    meshes=[o for o in coll.objects if o.type=="MESH"]
    tris=verts=faces=ngons=nonmanifold=0
    materials=set(); bad_scales=[]; bad_normals=[]
    lo=Vector((1e9,1e9,1e9)); hi=Vector((-1e9,-1e9,-1e9))
    for o in meshes:
        me=o.data; tris+=mesh_triangles(me); verts+=len(me.vertices); faces+=len(me.polygons)
        ngons+=sum(1 for p in me.polygons if len(p.vertices)>4)
        materials.update(m.name for m in me.materials if m)
        if any(abs(v-1.0)>1e-6 for v in o.scale): bad_scales.append(o.name)
        bm=bmesh.new(); bm.from_mesh(me)
        nonmanifold+=sum(1 for e in bm.edges if not e.is_manifold)
        bm.free()
        for v in o.bound_box:
            w=o.matrix_world@Vector(v); lo.x=min(lo.x,w.x); lo.y=min(lo.y,w.y); lo.z=min(lo.z,w.z); hi.x=max(hi.x,w.x); hi.y=max(hi.y,w.y); hi.z=max(hi.z,w.z)
        # Outward sanity by signed volume; only flag materially negative closed meshes.
        # Signed volume must be translation-invariant; using world-origin coordinates
        # falsely marks small closed meshes far from (0,0,0) as inward.
        center=sum((v.co for v in me.vertices), Vector()) / max(1, len(me.vertices))
        vol=0.0
        me.calc_loop_triangles()
        for t in me.loop_triangles:
            a,b,c=(me.vertices[i].co-center for i in t.vertices); vol+=a.dot(b.cross(c))/6.0
        if vol < -1e-7: bad_normals.append(o.name)
    dims=[round(hi[i]-lo[i],4) for i in range(3)] if meshes else [0,0,0]
    bounds={"min":[round(v,4) for v in lo],"max":[round(v,4) for v in hi],"dimensions_xyz_m":dims}
    return {"mesh_objects":len(meshes),"vertices":verts,"faces":faces,"triangles":tris,"materials":sorted(materials),
            "material_count":len(materials),"ngons":ngons,"non_manifold_edges":nonmanifold,
            "negative_volume_objects":bad_normals,"non_unit_scale_objects":bad_scales,"bounds":bounds}


def main():
    blend=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hero-kart-v2-R124.blend"); output=os.path.join(os.path.dirname(os.path.abspath(__file__)), "technical-audit.json"); bpy.ops.wm.open_mainfile(filepath=blend)
    report={"asset":"Super Kart — Hero Kart V2","blend":blend,"blender":bpy.app.version_string,
            "units":"meters","forward":"-Y","up":"+Z","authored_from_scratch":bool(bpy.context.scene.get("authored_from_scratch")),
            "collections":{},"gates":{}}
    for n in ("LOD0","LOD1","LOD2","COLLISION"): report["collections"][n]=audit_collection(n)
    budgets={"LOD0":(38000,52000,5),"LOD1":(16000,22000,4),"LOD2":(5000,7500,3)}
    for n,(mn,mx,mm) in budgets.items():
        d=report["collections"][n]
        report["gates"][n]={"triangle_budget":mn<=d["triangles"]<=mx,"material_budget":d["material_count"]<=mm,
                            "no_ngons":d["ngons"]==0,"manifold":d["non_manifold_edges"]==0,
                            "outward_normals":len(d["negative_volume_objects"])==0,"clean_scale":len(d["non_unit_scale_objects"])==0}
    c=report["collections"]["COLLISION"]
    report["gates"]["COLLISION"]={"triangle_budget":24<=c["triangles"]<=48,"no_ngons":c["ngons"]==0,"manifold":c["non_manifold_edges"]==0}
    report["wheel_pivots"]={o.name:{"location_m":[round(v,4) for v in o.location],"children":len(o.children),"axle_axis":o.get("axle_axis_local")}
                            for o in bpy.data.objects if "WHEEL_" in o.name and o.type=="EMPTY"}
    report["file_size_bytes"]=os.path.getsize(blend)
    report["all_structural_gates_pass"]=all(all(v.values()) for v in report["gates"].values())
    report["technical_pass"]=report["all_structural_gates_pass"]
    os.makedirs(os.path.dirname(output),exist_ok=True)
    with open(output,"w",encoding="utf-8") as f: json.dump(report,f,indent=2,ensure_ascii=False)
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if not report["all_structural_gates_pass"]: raise SystemExit(2)

if __name__=="__main__": main()

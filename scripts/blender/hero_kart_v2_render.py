#!/usr/bin/env python3
"""Reproduce the complete Hero Kart V2 review render set from the saved blend."""
import argparse
import os
from mathutils import Vector
import bpy


def parse():
    av=__import__("sys").argv; av=av[av.index("--")+1:] if "--" in av else []
    p=argparse.ArgumentParser(); p.add_argument("--blend",default="/mnt/storage2TB/Coding-Projects/super-kart-3djs/assets/hero-kart-v2/R70/hero-kart-v2-R70.blend"); p.add_argument("--output-dir",default="/mnt/storage2TB/Coding-Projects/super-kart-3djs/assets/hero-kart-v2/R70/renders")
    p.add_argument("--resolution",type=int,default=960); p.add_argument("--revision",default="R70"); p.add_argument("job_dir",nargs="?"); return p.parse_args(av)


def aim(cam, pos, target, lens=50):
    cam.location=pos; cam.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat("-Z","Y").to_euler(); cam.data.lens=lens


def make_override(name, color, rough=.7, wire=False):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new("ShaderNodeOutputMaterial"); bs=nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Roughness"].default_value=rough
    if wire:
        w=nt.nodes.new("ShaderNodeWireframe"); w.inputs["Size"].default_value=.008; w.use_pixel_size=False
        mix=nt.nodes.new("ShaderNodeMixRGB"); mix.blend_type="MIX"; mix.inputs[1].default_value=(.045,.055,.07,1); mix.inputs[2].default_value=(.82,.58,.25,1)
        nt.links.new(w.outputs["Fac"],mix.inputs[0]); nt.links.new(mix.outputs[0],bs.inputs["Base Color"])
    else: bs.inputs["Base Color"].default_value=(*color,1)
    nt.links.new(bs.outputs["BSDF"],out.inputs["Surface"]); return m


def main():
    a=parse(); bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.blend)); out=os.path.abspath(a.output_dir); os.makedirs(out,exist_ok=True)
    sc=bpy.context.scene; sc.render.engine="BLENDER_EEVEE"; sc.render.resolution_x=a.resolution; sc.render.resolution_y=round(a.resolution*.75); sc.render.resolution_percentage=100
    sc.render.image_settings.file_format="PNG"; sc.render.image_settings.color_mode="RGBA"; sc.render.film_transparent=False
    try: sc.view_settings.look="AgX - Medium High Contrast"
    except Exception: pass
    world=sc.world; world.use_nodes=True; bg=world.node_tree.nodes.get("Background"); bg.inputs["Color"].default_value=(.055,.075,.105,1); bg.inputs["Strength"].default_value=.34
    cam=sc.camera; layer=sc.view_layers[0]
    for n in ("LOD0","LOD1","LOD2"):
        bpy.data.collections[n].hide_render=(n!="LOD0"); bpy.data.collections[n].hide_viewport=False
    ground=bpy.data.objects.get("PRESENTATION_StudioGround")
    views={
      "beauty":((3.05,-3.55,2.05),(0,0,.58),50),
      "front":((0,-4.15,.78),(0,-.10,.53),55),
      "rear":((0,4.15,.88),(0,.22,.54),55),
      "left":((-4.15,0,.85),(0,0,.52),55),
      "right":((4.15,0,.85),(0,0,.52),55),
      "top":((0,0,5.15),(0,0,.35),55),
      "low-front-3q":((3.0,-3.5,1.18),(0,-.05,.47),50),
      "low-rear-3q":((-3.1,3.5,1.22),(0,.12,.51),50),
      "chase-6m":((-3.35,4.45,1.95),(0,.05,.58),35),
      "chase-12m":((-6.6,8.8,3.35),(0,.05,.58),35),
      "driver-clearance":((2.65,-2.90,1.62),(0,-.05,.90),52),
      "windshield-profile":((2.35,-1.65,1.18),(0,-.78,.68),58),
      "windshield-top":((0,-1.45,4.35),(0,-.78,.62),62),
    }
    layer.material_override=None
    for name,(pos,target,lens) in views.items():
        for o in bpy.data.objects:
            if "MiniWindshieldLens" in o.name:
                o.hide_render = (name == "driver-clearance")
        aim(cam,pos,target,lens); sc.render.filepath=os.path.join(out,name+".png"); bpy.ops.render.render(write_still=True); print("RENDERED",name)
    for o in bpy.data.objects:
        if "MiniWindshield" in o.name: o.hide_render=False
    # Black-fill silhouette: no lighting tricks, bright neutral field, no ground.
    black=make_override("REVIEW_black_fill",(.002,.002,.002),1.0); layer.material_override=black
    if ground: ground.hide_render=True
    bg.inputs["Color"].default_value=(.72,.72,.72,1); bg.inputs["Strength"].default_value=.8
    aim(cam,(3.05,-3.55,1.65),(0,0,.55),50); sc.render.filepath=os.path.join(out,"black-fill.png"); bpy.ops.render.render(write_still=True)
    clay=make_override("REVIEW_clay",(.42,.46,.50),.58); layer.material_override=clay
    bg.inputs["Color"].default_value=(.055,.065,.08,1); bg.inputs["Strength"].default_value=.4
    aim(cam,(3.05,-3.55,2.05),(0,0,.58),50); sc.render.filepath=os.path.join(out,"clay-silhouette.png"); bpy.ops.render.render(write_still=True)
    wire=make_override("REVIEW_wireframe",(.4,.4,.4),.6,True); layer.material_override=wire
    aim(cam,(3.1,-3.6,2.15),(0,0,.55),52); sc.render.filepath=os.path.join(out,"wireframe-topology.png"); bpy.ops.render.render(write_still=True)
    # Underside / jump inspection below the contact plane.
    layer.material_override=None; bg.inputs["Color"].default_value=(.07,.085,.11,1); bg.inputs["Strength"].default_value=.42
    aim(cam,(2.5,-2.9,-.55),(0,0,.25),48); sc.render.filepath=os.path.join(out,"underside-jump.png"); bpy.ops.render.render(write_still=True)
    # Side-by-side authored LODs. Only top-level roots move, preserving wheel parenting.
    offsets={"LOD0":-1.85,"LOD1":0.0,"LOD2":1.85}; originals={}
    for n,dx in offsets.items():
        c=bpy.data.collections[n]; c.hide_render=False
        for o in c.objects:
            if o.parent is None:
                originals[o]=o.location.copy(); o.location.x+=dx
    sc.render.resolution_x=1280; sc.render.resolution_y=640
    aim(cam,(0,-7.4,3.0),(0,0,.58),54); sc.render.filepath=os.path.join(out,"lod-comparison.png"); bpy.ops.render.render(write_still=True)
    for o,loc in originals.items(): o.location=loc
    print("HERO_KART_V2_RENDER_SET_OK",a.revision,out)

if __name__=="__main__": main()

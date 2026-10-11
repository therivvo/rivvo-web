#!/usr/bin/env python3
"""P0 audit for Hero Kart V2 review revision; run inside Blender."""
import argparse, json, os, bpy

def parse():
    av=__import__('sys').argv
    av=av[av.index('--')+1:] if '--' in av else []
    p=argparse.ArgumentParser(); p.add_argument('--blend', default='/mnt/storage2TB/Coding-Projects/super-kart-3djs/assets/hero-kart-v2/R70/hero-kart-v2-R70.blend'); p.add_argument('--output', default='/mnt/storage2TB/Coding-Projects/super-kart-3djs/assets/hero-kart-v2/R70/p0-metrics.json'); p.add_argument('job_dir', nargs='?')
    return p.parse_args(av)

def main():
    a=parse(); bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.blend))
    c=bpy.data.collections['LOD0']; names={o.name for o in c.objects}
    required=['WindshieldMountLower','WindshieldMountUpper','WindshieldMountFoot','WindshieldMountCap',
              'DriverHeadInternal','HelmetTemple','HelmetJaw','HelmetNape','HelmetVisorPivot',
              'HelmetIntegratedChin','DriverCollar','SteeringHub','SteeringHubCap','SteeringColumn']
    counts={n:sum(1 for x in names if x.startswith('LOD0_'+n)) for n in required}
    report={
      'revision':bpy.context.scene.get('review_revision'),
      'blender':bpy.app.version_string,
      'blend':os.path.abspath(a.blend),
      'windshield_mount_count':bpy.context.scene.get('windshield_mount_count'),
      'windshield_width_ratio':bpy.context.scene.get('windshield_width_ratio'),
      'windshield_rear_edge_ahead_m':bpy.context.scene.get('cockpit_rim_rear_y_m')-bpy.context.scene.get('windshield_rear_edge_y_m'),
      'steering_hub_diameter_ratio_front_wheel':bpy.context.scene.get('steering_hub_diameter_ratio_front_wheel'),
      'steering_hub_ratio':bpy.context.scene.get('steering_hub_diameter_ratio_front_wheel'),
      'helmet_shell_wrap':bpy.context.scene.get('helmet_shell_wrap',False),
      'visor_pivot_count':bpy.context.scene.get('visor_pivot_count',0),
      'steering_continuous_ring':bpy.context.scene.get('steering_continuous_ring',False),
      'steering_column_coaxial':bpy.context.scene.get('steering_column_coaxial',False),
      'no_windshield_over_driver':bpy.context.scene.get('no_windshield_over_driver',False),
      'required_object_counts':counts,
      'hand_angles':sorted(round(o.get('grip_angle_deg'),1) for o in c.objects if o.get('grip_angle_deg') is not None),
      'all_pass':True,
    }
    checks={
      'revision':report['revision'].startswith('R'),
      'mounts':report['windshield_mount_count']==4 and counts['WindshieldMountLower']==2 and counts['WindshieldMountUpper']==2,
      'width_ratio':0.72<=report['windshield_width_ratio']<=0.78,
      'rear_edge':report['windshield_rear_edge_ahead_m']>=0.08,
      'hub_ratio':0.19<=report['steering_hub_diameter_ratio_front_wheel']<=0.23,
      'helmet_blocks':all(counts[n]>=2 for n in ['HelmetTemple','HelmetJaw','HelmetNape','HelmetVisorPivot']),
      'chin_collar':counts['HelmetIntegratedChin']>=1 and counts['DriverCollar']>=1,
      'coaxial_stack':counts['SteeringHub']>=1 and counts['SteeringHubCap']>=1 and counts['SteeringColumn']>=1,
      'continuous_ring':report['steering_continuous_ring'] and report['steering_column_coaxial'] and report['no_windshield_over_driver'],
      'hand_angles':report['hand_angles']==[30.0,150.0],
    }
    report['checks']=checks; report['all_pass']=all(checks.values())
    os.makedirs(os.path.dirname(os.path.abspath(a.output)),exist_ok=True)
    with open(a.output,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
    print(json.dumps(report,indent=2))
    if not report['all_pass']: raise SystemExit(2)
if __name__=='__main__': main()

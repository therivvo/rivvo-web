# Hero Kart V2 — R124 visual QA

## Brief / structural correction
R124 is one class-level generator correction from R123: the exposed `R123_AeroscreenArc`/rollbar-like tube family was removed and replaced by a closed, shallow `R124_IntegratedCowlShell` loft with embedded cowl shoulder rails and integrated mounts. R80–R123 remain preserved.

## Reproducible artifacts
- Blender 4.0.2 build runner: LXC105 `192.168.0.195`
- Blend: `assets/hero-kart-v2/R124/hero-kart-v2-R124.blend`
- Generator: `assets/hero-kart-v2/R124/build_r124.py`
- Audit: `assets/hero-kart-v2/R124/technical-audit.json`
- Renders from the same blend: `assets/hero-kart-v2/R124/renders/{beauty,profile,top,rear,clearance}.png`

## Technical result — PASS
- LOD0: 39,832 triangles, 5 materials, 0 n-gons, 0 non-manifold edges.
- LOD1: 21,098 triangles, 4 materials, 0 n-gons, 0 non-manifold edges.
- LOD2: 6,028 triangles, 3 materials, 0 n-gons, 0 non-manifold edges.
- Collision: 36 triangles, 0 non-manifold edges.
- Blender: 4.0.2; authored-from-scratch: true; blend size: 809,237 bytes.

## Primary vision — REJECT
The exact five R124 renders were reviewed. The class change removed the obvious rollbar, but did not close the P0 visual failure:

- Beauty/clearance: the new shell reads as an oversized opaque black tablet/bubble in front of the wheel, not as a transparent integrated cockpit surface.
- Profile: the helmet/face shell appears visually detached above the torso, with the cockpit/driver chain still mannequin-like; this is a direct P0 rejection.
- Top: overall symmetry and exposed-wheel plan are readable, but the cockpit shell remains a detached foreground block.
- Rear: rear identity is readable, but it cannot compensate for the cockpit P0 failure.
- Clearance: no obvious catastrophic mesh collision in the view, but the visual construction still reads as assembled rather than authored.

Because primary vision rejected the revision, Sol was not invoked. This is protocol-correct; no approval is implied.

## Promotion status
- Sol: NOT INVOKED — primary gate failed.
- Export: BLOCKED.
- Runtime integration: BLOCKED.
- Next experiment: stop tuning the shell material/shape. Rebuild the pilot as a single seated racing figure with helmet, neck, torso and shoulder masses sharing one continuous silhouette; then make the cockpit lip a low open cowl rather than another front shell volume.

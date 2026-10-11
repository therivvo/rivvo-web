# The Bubble Bumper — V068 Reconstruction Contract

## Authority and status

- Authoritative source: `assets/reference-orthographic/{top,front,rear,side}.jpg`; composite `assets/the-bubble-bumper.jpg` supplies the isometric/presentation language.
- v067 is rejected. Its normalized visual hull is evidence of the wrong representation, not a base mesh.
- This revision is a representation reset. No prior geometry is reused as primary form.
- Target: AAA-quality, concept-faithful Blender asset. Runtime/export remain blocked until coder vision PASS, Sol PASS and explicit user PASS.

## Coordinate contract

- Units: metres; ground `z=0`; front `+Y`; rear `-Y`; up `+Z`.
- Initial scale anchor: front wheel diameter `D=0.500 m`; all dimensions below are hypotheses measured from the orthographic board and must be rechecked against fixed renders.
- Initial envelope: length `2.375 m`, width `1.550 m`, helmet height `1.100 m`.
- Axles: front `y=+0.67`, rear `y=-0.54`.
- Front wheel radius `0.250`, rear wheel radius `0.263`; front wheels narrower than rear.

## Representation decision

| Component | Representation | Forbidden shortcut |
|---|---|---|
| Primary shell/nose | Authored quad surface patches with controlled support loops, continuous transitions and explicit cockpit opening | Visual hull, voxel mesh, closed generic capsule, primitive stack |
| Side pods | Authored swept shell with recessed inset and physical yellow border; tied to chassis at inner mounts | Floating ellipsoid, flat sticker, isolated capsule |
| Cockpit | Recessed authored well, rim, seat, cowl and connected driver clearance | Surface-coloured hole, driver placed on top |
| Bumper U | Bezier curve converted to mesh, constant section, rearward returns, collars and named chassis sockets | Bar, hoop, flat blade, tube without mount |
| Wheels/suspension | Parametric wheel envelope plus explicit hubs, arms, uprights, springs and clearances | Unanchored wheels or dragster tread |
| Rear assembly | Authored housing and mechanical subassemblies between rear wheels | Generic white/gray blob |
| Pilot | Connected stylized seated base: torso/pelvis/limbs, authored helmet shell, face/visor and steering contact | Sphere head, disconnected mannequin |
| Secondary detail | Physical seams, recesses, bevels, fasteners, spring coils, exhaust lips and grille | Decal-only detail |

## P0 visual requirements

1. Low, wide, rounded toy-premium silhouette in all five views.
2. Front bumper is an external, thick, deep U with blue body and yellow segmented collars/end caps.
3. Large smooth black tyres are anchored at four corners; rear tyre envelope is larger/wider.
4. Yellow side-pod shell contains a genuinely recessed blue inset; pod mass is greatest near the driver hip.
5. Cockpit is central, open and visibly deep; dark seat, steering wheel and driver sit inside it.
6. Driver is small and seated, with bent arms contacting the wheel, bent legs/boots and visible blue/yellow helmet/face identity.
7. Rear is compact and exposed: central gray housing, circular outlet, lower separated grille, transverse rear bar with yellow tips, lateral springs and exactly two silver exhausts angled up/out.
8. No primary form reads as voxel, blockout, primitive stack, massinha or generic capsule.
9. Geometry boundaries and material boundaries coincide for blue/yellow panels.

## Proof cameras and gates

- Fixed 960×720 orthographic cameras: `CAM_TOP`, `CAM_SIDE`, `CAM_FRONT`, `CAM_REAR`, `CAM_ISO_FRONT`.
- Required proof sets: neutral clay, black-fill silhouette/ID, final material, and close-ups of cockpit, pod inset, bumper sockets and rear assembly.
- Coder gate checks identity, proportions, silhouette, continuity, contacts, attachment and multi-view consistency.
- Sol gate receives identical source, camera contract and render set only after coder PASS.
- Technical validation/export only after both visual gates; user approval remains required for final promotion.

## Rejection criteria

Reject immediately if any view has: missing/incorrect primary envelope; bumper no longer reads U; wheel centres float or clip; pod/inset is sticker-like; cockpit is shallow/closed; driver is not seated or does not contact the wheel; rear housing is generic; exhaust count/placement is wrong; or any primary surface reads voxel/blocky.

## P1 after P0

Panel gaps, fasteners, hub rings, damper details, grille bars, exhaust lips, controlled roughness variation, clean UVs, LODs and game export.

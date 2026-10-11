# The Bubble Bumper — V070 Orthographic Reconstruction Contract

## Status

- V067/V068/V069 are rejected candidates; no prior Sol or user approval transfers to V070.
- V070 changes the representation again: orthographic landmark-driven authored assembly, not visual hull and not a generic loft.
- Target is a candidate for visual approval only after coder PASS and Sol PASS. Export/runtime remain blocked.

## Source hierarchy

1. Geometry/proportions: `assets/reference-orthographic/top.jpg`, `front.jpg`, `rear.jpg`, `side.jpg`.
2. Three-dimensional continuity and appeal: `assets/the-bubble-bumper.jpg` isometric panel.
3. Prior boards/renders: diagnostics only.

## Frozen landmarks from the orthographics

- Ground contact line and four wheel centers are primary datums; rear wheel is visibly larger and wider.
- TOP: front is left; rear is right. The U bumper is a low, wide external arc at the front, with blue tube and yellow collars; it does not float away from the nose. The cockpit is a narrow central opening. Yellow pods occupy the mid-body with large blue recessed faces. Rear housing is narrow between the rear tyres.
- FRONT: tyres sit low at the outer edges; the dark recessed grille is centered behind the low bumper; pilot head is centered above a compact steering/cowl stack; a blue crossbar with yellow circular ends runs behind the driver.
- REAR: the blue crossbar is above the compact mechanical housing; exactly two silver exhaust mouths sit left/right of one dark central circular outlet; a separate lower blue grille hangs below; rear springs/arms flank the housing.
- SIDE: front is left; the nose is short and low; the driver sits reclined inside the cockpit with helmet connected to neck/torso, arms reaching the steering wheel and bent legs/boots inside the well; the yellow pod is a low rounded mass under the hip; rear engine/exhausts rise behind the rear wheel.

## Representation ownership

- `PRIMARY_NOSE_COWL`, `COCKPIT_RIM_WELL`, `SIDE_POD_SHELL_*`, `REAR_HOUSING`: authored mesh surfaces with support loops and physical recesses.
- `BUMPER_U`, chassis rails, crossbar, suspension arms, dampers, exhausts and springs: controlled curves/tubes converted or rendered with collars and mounts; every endpoint has a named socket.
- Wheels: smooth broad tyre plus physically modeled rim/hub and shallow concept tread.
- Pilot: connected seated stylized character with authored torso/pelvis volumes, neck, helmet/face/visor, articulated arms/hands and bent legs/boots.
- Procedural helpers are allowed only for symmetry, repeated bolts/tread, camera framing, landmark measurement and audit.

## Camera contract

- All orthographic proof renders: 1024×512, matching each source aspect ratio, neutral background and identical light.
- `CAM_TOP`: top orthographic, front left/rear right, full vehicle margin 1.08.
- `CAM_PROFILE`: right profile, front left/rear right, ground and all extremities visible.
- `CAM_FRONT`: straight front, full tyres/helmet/bumper visible.
- `CAM_REAR`: straight rear, full tyres/helmet/crossbar/grille visible.
- `CAM_ISOMETRIC`: perspective 3/4 from front-right, used only for depth/attachment proof.
- No per-revision auto-fit or crop changes.

## P0 exit criteria

1. Five views read as the same specific concept vehicle, not merely a generic kart.
2. All four wheel centres and ground contacts agree across TOP/FRONT/REAR/SIDE.
3. Bumper reads as a low deep U, attached through visible sockets, with concept yellow segmentation.
4. Nose/grade remain central and recessed behind bumper.
5. Pods are low rounded yellow shells with blue recessed faces, not plates or floating capsules.
6. Cockpit is a real opening; pilot is seated, connected and hands contact the wheel in profile and isometric.
7. Rear has the correct bar, compact housing, two exhausts, central outlet, lower grille and springs.
8. No primary component reads as voxel, blocky, primitive stack, mannequin or generic blob.

## Rejection rule

Any P0 failure in any fixed view blocks coder PASS. Sol receives the exact same source, renders, cameras and contract only after coder PASS. Technical validation/export happens only after both visual gates and explicit user approval.

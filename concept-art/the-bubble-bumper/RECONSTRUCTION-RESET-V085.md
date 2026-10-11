# Representation Reset — Bubble Bumper V085

## Verdict

- V085: `CODER_REJECT`.
- No independent gate was requested because the primary coder gate failed.
- No user-approval candidate exists after V085.

## Evidence

- `modeling/v085-review-board.png` — large paired reference/model board.
- `modeling/renders-v085/{top,profile,front,rear,isometric}.png`.
- V085 is visibly closer than V082 in pilot pose and scale, but remains below the concept: the primary shell/pods are not the same molded construction, wheels lack the concept's tire/rim fidelity, the pilot still reads as a simplified constructed figure, and the rear mechanical assembly remains proportionally different.

## Failed assumption

The procedural primitive/curve assembly family used by V077–V085 cannot reach 100% multi-view concept fidelity through local coordinate/material tweaks. It repeatedly produces a recognizable blue/yellow kart, not the specific Bubble Bumper.

## Required next representation

Use one of these classes before another approval candidate:

1. A real multi-view reconstruction workflow that fits a shared 3D mesh to the four orthographic silhouettes and the hero image.
2. An image-to-3D service/model with multi-view conditioning, followed by manual retopology and Blender cleanup.
3. A manually sculpted/retopologized mesh built from the orthographic references, with the pilot as a real connected character mesh.

Do not resume by adding more tubes, boxes, toruses, or decorative materials to V085. The local environment currently has no installed image-to-3D/multi-view package or provider credential; this is the blocker, not a visual approval.

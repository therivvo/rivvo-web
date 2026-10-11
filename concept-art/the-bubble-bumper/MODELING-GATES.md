# The Bubble Bumper — Modeling Contract

## Status

- Concept source: `../assets/the-bubble-bumper.jpg`
- Modeling status: not started
- Runtime integration: blocked until user approval
- Required approvals: coder vision PASS → Sol vision PASS → user Telegram PASS

## P0 visual requirements

- Five fixed views must match the concept panels: top, lateral, front, rear, isometric.
- Low, wide, rounded, toy-premium silhouette.
- Thick U-shaped front bumper with blue/yellow segmentation preserved as material channels.
- Short nose centered behind the bumper.
- Open cockpit with visible dark seat, thick steering wheel and seated pilot.
- Large smooth black tires, visibly larger than conventional kart proportions.
- Rounded blue side pods with thick yellow contour/channel.
- Rear exposed mechanical module: gray central unit, transverse bar, visible springs, two silver exhausts and lower grille.
- Pilot remains a small stylized seated character; no new hero-character redesign.

## Material policy

- Yellow and blue are customizable material channels only.
- Black tires, dark cockpit/seat/steering, gray/silver frame/suspension/engine/exhausts, clear/dark visor and pilot facial read remain faithful to the concept.
- Grid, labels and floor lines from the concept image are not asset geometry.

## Pass order

1. Reference analysis and measured proportion contract.
2. Primary blockout: body, bumper, side pods, wheel envelopes, cockpit, rear unit.
3. Coder visual gate on five fixed views.
4. Sol visual gate on the same renders and source image.
5. Secondary forms: suspension, springs, exhausts, grille, steering/pilot read.
6. Coder visual gate.
7. Sol visual gate.
8. Materials/color channels and presentation.
9. Technical validation after visual approvals.
10. Final multi-view render delivered to user; wait for explicit user approval.

## Technical gates

- Blend checkpoint is non-empty and reproducible from the committed builder.
- Five renders are non-empty and tied to the same blend.
- No runtime integration before user approval.
- Mesh/UV/LOD/export validation only after visual gates pass.
- Every modeling revision gets an atomic commit and push.

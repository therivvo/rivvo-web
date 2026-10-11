# Hero Kart V2 — R117–R121 convergence record

## R119/R120/R121 — class-level cockpit experiments, primary visual gate still failed

R119 rebuilt the cockpit/driver/aeroscreen as an authored module and passed technical audit: LOD0 38,692 tri/5 mats/0 non-manifold; LOD1 21,098/4/0; LOD2 6,028/3/0; collision 36/0. Primary vision rejected profile/top: the seat read as a detached panel/capsule and the driver remained procedural.

R120 removed the rectangular side plate and replaced it with a rounded seat core. Technical audit passed: LOD0 39,180 tri/5 mats/0 non-manifold; LOD1 21,098/4/0; LOD2 6,028/3/0; collision 36/0. Primary vision still rejected the rounded capsule and mannequin-like driver.

R121 removed the detached seat capsule entirely and added a functional harness to the integrated torso. Five real renders and technical audit were produced: LOD0 38,772 tri/5 mats/0 non-manifold; LOD1 21,098/4/0; LOD2 6,028/3/0; collision 36/0. Primary vision still rejects beauty/profile because the driver/cockpit does not yet read as AAA-authored. Sol was not invoked. Export/runtime remain blocked.

Exact artifacts: `assets/hero-kart-v2/R119/`, `R120/`, `R121/`. Next experiment: change the driver representation class (helmet/torso/arms as a connected stylized racing shell with stronger seat/cowl integration), not another local primitive adjustment.

## R117 — technical gate passed

Build reproducible in Blender 4.0.2 on GPU runner LXC 105. Generator fixes: closed triangulated cylinder caps, UVMap on every authored mesh, canonical material remap per LOD, deterministic LOD reduction, and translation-invariant signed-volume audit.

Measured audit: LOD0 40,588 triangles / 5 materials / 0 n-gons / 0 non-manifold; LOD1 21,098 / 4 / 0 / 0; LOD2 6,028 / 3 / 0 / 0; collision 36 triangles / 0 non-manifold. Technical pass is real. Runtime and export remain blocked.

## R118 — primary visual gate failed

R118 replaced the prior flat windshield attempt with a single closed curved visor volume and four cowl mounts. The same five renders were produced: `assets/hero-kart-v2/R118/renders/{beauty,profile,top,rear,clearance}.png`.

Primary pixel review rejected the revision. Beauty and clearance still read the visor as an oversized tablet/block in front of the steering wheel; profile makes the visor disproportionate and detached in silhouette; the driver remains mannequin/procedural rather than a convincing seated authored character. Rear identity is readable, but that does not compensate for cockpit P0 failures.

Sol was not invoked: the dual-vision protocol requires primary approval first. R117/R118 checkpoints are preserved. Next experiment is a class-level cockpit/driver/windshield rebuild, not incremental boxes, cylinders, or panel tuning.

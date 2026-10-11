/**
 * Super Kart 3D.js — recipe-driven circuit layouts.
 *
 * A layout is written like driving directions: straights and circular arcs.
 * buildLoop() turns that recipe into the closed control-point loop that
 * TrackBuilder expects (same format as TRACK_PATH / CITY_PATH: a point every
 * ~8m, so straights stay perfectly straight under CatmullRom smoothing).
 *
 * Recipe format (spec.segs), heading 0 = +X, positive degrees turn toward +Z:
 *   [len]          straight of `len` metres
 *   [deg, radius]  arc turning `deg` degrees on a `radius` metre circle
 *   ['A', len] / ['B', len]
 *                  two "free" straights (must not be parallel). Their lengths
 *                  are SOLVED so the loop closes exactly — edit any other
 *                  segment and A/B absorb the difference. The `len` given is
 *                  only a hint for readers; it is ignored.
 * The arcs must add up to +360 degrees. The start/finish line is placed in
 * the middle of the FIRST segment (make it a straight), and the finished loop
 * is centred on the origin.
 *
 * spec.elev = [base, hill, roll]: road height along the lap —
 *   base + hill * (one smooth rise and fall) + roll * (two smaller waves).
 */
import * as THREE from 'three';

const STEP = 8; // metres between control points (matches Neon City)

function walk(spec, segs, emit) {
  let x = 0;
  let z = 0;
  let h = 0;
  const dirs = {};
  for (const seg of segs) {
    if (typeof seg[0] === 'string') {
      dirs[seg[0]] = [Math.cos(h), Math.sin(h)];
      continue;
    }
    if (seg.length === 1) {
      const len = seg[0];
      const n = Math.max(1, Math.round(len / STEP));
      for (let i = 1; i <= n; i++) emit?.(x + (Math.cos(h) * len * i) / n, z + (Math.sin(h) * len * i) / n, seg);
      x += Math.cos(h) * len;
      z += Math.sin(h) * len;
    } else {
      const [deg, r] = seg;
      const a = (deg * Math.PI) / 180;
      const sg = Math.sign(a);
      const cx = x - Math.sin(h) * r * sg;
      const cz = z + Math.cos(h) * r * sg;
      const a0 = Math.atan2(z - cz, x - cx);
      const n = Math.max(2, Math.round((Math.abs(a) * r) / STEP));
      for (let i = 1; i <= n; i++) {
        const ang = a0 + (a * i) / n;
        emit?.(cx + Math.cos(ang) * r, cz + Math.sin(ang) * r, seg);
      }
      x = cx + Math.cos(a0 + a) * r;
      z = cz + Math.sin(a0 + a) * r;
      h += a;
    }
  }
  return { x, z, h, dirs };
}

function elevAt(s, [base, hill, roll]) {
  return base + hill * (0.5 - 0.5 * Math.cos(2 * Math.PI * s)) + roll * Math.sin(4 * Math.PI * s) * Math.sin(Math.PI * s);
}

/** Recipe → closed loop of THREE.Vector3 control points. */
export function buildLoop(spec) {
  // Pass 1: walk with A/B at zero length, then solve the 2x2 system that
  // brings the end point back onto the start.
  const dry = walk(spec, spec.segs);
  const { A, B } = dry.dirs;
  if (!A || !B) throw new Error(`buildLoop(${spec.name}): needs ['A', len] and ['B', len] segments`);
  const det = A[0] * B[1] - A[1] * B[0];
  if (Math.abs(det) < 0.2) throw new Error(`buildLoop(${spec.name}): A and B straights are (nearly) parallel`);
  const lenA = (-dry.x * B[1] + dry.z * B[0]) / det;
  const lenB = (-dry.z * A[0] + dry.x * A[1]) / det;
  if (lenA < 10 || lenB < 10) {
    throw new Error(`buildLoop(${spec.name}): loop cannot close (A=${lenA.toFixed(1)}m, B=${lenB.toFixed(1)}m) — rebalance the recipe`);
  }
  const segs = spec.segs.map((s) => (s[0] === 'A' ? [lenA] : s[0] === 'B' ? [lenB] : s));

  // Pass 2: sample the closed loop.
  const pts = [[0, 0]];
  let firstCount = 0;
  walk(spec, segs, (x, z, seg) => {
    pts.push([x, z]);
    if (seg === segs[0]) firstCount++;
  });
  pts.pop(); // the last point coincides with the first

  // Start/finish in the middle of the first straight; centre on the origin.
  const startIdx = Math.max(1, Math.round(firstCount / 2));
  const loop = pts.slice(startIdx).concat(pts.slice(0, startIdx));
  const xs = loop.map((p) => p[0]);
  const zs = loop.map((p) => p[1]);
  const ox = (Math.min(...xs) + Math.max(...xs)) / 2;
  const oz = (Math.min(...zs) + Math.max(...zs)) / 2;
  return loop.map(([x, z], i) => new THREE.Vector3(
    +(x - ox).toFixed(2),
    +elevAt(i / loop.length, spec.elev || [0, 0, 0]).toFixed(2),
    +(z - oz).toFixed(2),
  ));
}

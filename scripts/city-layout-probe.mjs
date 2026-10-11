#!/usr/bin/env node
/**
 * city-layout-probe.mjs — validate a track layout's geometry BEFORE shipping.
 *
 * Reports: total length, minimum radius of curvature (with spans < 9m),
 * self-crossings, start tangent direction, elevation range and bounds.
 *
 * Usage: node scripts/city-layout-probe.mjs [city|meadow]
 * (city = Neon City "2" layout, meadow = Sunny Meadow — or edit the import.)
 *
 * This is the QA gate for the 2026-08-11 Neon City redesign: the '2' layout
 * must have 0 self-crossings, start tangent UP (+Z) and corners >= ~7m.
 */
import * as THREE from 'three';
import { CITY_PATH, TRACK_PATH } from '../src/track/TrackBuilder.js';

const which = process.argv[2] === 'meadow' ? 'meadow' : 'city';
const CONTROL = which === 'city' ? CITY_PATH : TRACK_PATH;
const path = new THREE.CatmullRomCurve3(CONTROL.map((v) => v.clone()), true, 'catmullrom', 0.5);

function segIntersect(a, b, c, d) {
  const d1 = (b.x - a.x) * (d.z - a.z) - (b.z - a.z) * (d.x - a.x);
  const d2 = (b.x - a.x) * (c.z - a.z) - (b.z - a.z) * (c.x - a.x);
  if ((d1 > 0) === (d2 > 0)) return false;
  const d3 = (d.x - c.x) * (a.z - c.z) - (d.z - c.z) * (a.x - c.x);
  const d4 = (d.x - c.x) * (b.z - c.z) - (d.z - c.z) * (b.x - c.x);
  return (d3 > 0) !== (d4 > 0);
}

const L = path.getLength();
const N = 3000;
let prev = null, prev2 = null;
let minR = 1e9, minT = 0;
const badSpans = [];
for (let i = 0; i <= N; i++) {
  const p = path.getPointAt(i / N);
  if (prev && prev2) {
    const a = prev2.distanceTo(prev), b = prev.distanceTo(p), cc = p.distanceTo(prev2);
    const s = (a + b + cc) / 2;
    const area = Math.sqrt(Math.max(0, s * (s - a) * (s - b) * (s - cc)));
    const R = area > 1e-6 ? (a * b * cc) / (4 * area) : 1e9;
    if (R < minR) { minR = R; minT = i / N; }
    if (R < 9) badSpans.push({ t: i / N, R });
  }
  prev2 = prev; prev = p;
}
const spans = [];
for (const b of badSpans) {
  const last = spans[spans.length - 1];
  if (last && Math.abs(b.t - last.tEnd) < 0.002) last.tEnd = b.t;
  else spans.push({ tStart: b.t, tEnd: b.t, R: b.R });
}

const M = 400;
const pts = [];
for (let i = 0; i < M; i++) pts.push(path.getPointAt(i / M));
let crossings = 0;
for (let i = 0; i < M; i++) {
  for (let j = i + 2; j < M; j++) {
    if (Math.abs(i - j) < 2 || (i === 0 && j === M - 2)) continue;
    if (segIntersect(pts[i], pts[(i + 1) % M], pts[j], pts[(j + 1) % M])) crossings++;
  }
}

// KERB-EDGE FOLD GATE (AUDIT 2026-08-11): a corner whose centerline radius
// dips below the kerb lateral offset (halfW + 0.15) makes the INNER kerb
// edge self-intersect — stones pile/cross every lap. Detect by sampling the
// edge polyline finely (0.1m) and counting direction reversals.
{
  const halfW = (typeof getRoadWidthAt === 'function' ? getRoadWidthAt() : 9) / 2;
  const offset = halfW + 0.15;
  const M = 4000;
  let revs = 0;
  const eP = (t, side) => {
    const p = path.getPointAt(t);
    const tan = path.getTangentAt(t);
    const n = new THREE.Vector3(-tan.z, 0, tan.x).normalize();
    return new THREE.Vector3(p.x + n.x * side * offset, p.y, p.z + n.z * side * offset);
  };
  for (const side of [1, -1]) {
    let last = null, last2 = null;
    for (let i = 0; i <= M; i++) {
      const e = eP(i / M, side);
      if (last && last2) {
        const v1 = new THREE.Vector3().subVectors(last, last2);
        const v2 = new THREE.Vector3().subVectors(e, last);
        if (v1.dot(v2) < -0.5 && v1.lengthSq() > 1e-6) revs++;
      }
      last2 = last; last = e;
    }
  }
  if (revs > 0) console.log(`  !! KERB-EDGE FOLDS: ${revs} direction reversals (corner radius < kerb offset)`);
  else console.log(`  kerb-edge folds: 0 (both sides)`);
}

const t0 = path.getTangentAt(0);
let minX = 1e9, maxX = -1e9, minZ = 1e9, maxZ = -1e9, minY = 1e9, maxY = -1e9;
for (let i = 0; i <= N; i++) {
  const p = path.getPointAt(i / N);
  minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x);
  minZ = Math.min(minZ, p.z); maxZ = Math.max(maxZ, p.z);
  minY = Math.min(minY, p.y); maxY = Math.max(maxY, p.y);
}

console.log(`${which.toUpperCase()} layout probe`);
console.log(`  length: ${L.toFixed(0)}m | control points: ${CONTROL.length}`);
console.log(`  min radius: ${minR.toFixed(1)}m @ t=${minT.toFixed(3)}`);
for (const s of spans.slice(0, 12)) console.log(`    corner t=${s.tStart.toFixed(3)}..${s.tEnd.toFixed(3)} minR=${s.R.toFixed(1)}m`);
console.log(`  self-crossings: ${crossings}`);
console.log(`  start tangent: (${t0.x.toFixed(2)}, ${t0.z.toFixed(2)}) ${t0.z > 0.98 ? 'UP ✓' : '—'}`);
console.log(`  elevation: ${minY.toFixed(2)}..${maxY.toFixed(2)} | bounds x ${minX.toFixed(0)}..${maxX.toFixed(0)} z ${minZ.toFixed(0)}..${maxZ.toFixed(0)}`);
console.log(crossings === 0 && t0.z > 0.98 ? '  RESULT: PASS' : '  RESULT: FAIL');

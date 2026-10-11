
import * as THREE from 'three';
import { KartPhysics } from '../src/entities/KartPhysics.js';
import { AIController } from '../src/entities/AIController.js';
import { CONFIG } from '../src/config.js';
import { TRACK_PATH, CITY_PATH, getRoadWidthAt } from '../src/track/TrackBuilder.js';
import { headingVector } from '../src/entities/PowerUp.js';
const DT = 1/60;
const TRACK = parseInt(process.argv[2] || '1', 10);
const LOOKAHEAD = parseFloat(process.argv[3] || '6');
CONFIG.ai.steerPredictAhead = LOOKAHEAD;
const ctrl = (TRACK === 2 ? CITY_PATH : TRACK_PATH).map(v => v.clone());
const path = new THREE.CatmullRomCurve3(ctrl, true, 'catmullrom', 0.5);
const trackData = { isCity: TRACK === 2, path, length: path.getLength(), getRoadWidthAt, turboPads: {ts: [], points: []}, ramps: [], startLine: {position: path.getPointAt(0), direction: path.getTangentAt(0).normalize(), width: 9} };
function makeKart(t, lat, isPlayer = false) {
  const p = trackData.path.getPointAt(t);
  const tan = trackData.path.getTangentAt(t);
  const nrm = new THREE.Vector3(-tan.z, 0, tan.x).normalize();
  const pos = p.clone().addScaledVector(nrm, lat);
  const group = new THREE.Group(); group.position.copy(pos);
  return { isPlayer, number: 1, character: {name:'Sim', stats:{speed:7, accel:7, handling:7}}, rideHeight: CONFIG.kart.wheelRadius + 0.04, group,
    state: { speed: 0, position: pos, heading: Math.atan2(tan.x, tan.z), drifting: false, driftCharge: 0, boost: false, turboBoostMs: 0, offRoad: false, spinOut: false, lap: 0, progress01: 0, vY: 0, onRamp: false, draft: false },
    finished: false, cruiseSpeed: undefined, heldItem: null, heldItem2: null, _rearThrow: false,
    _samples: null, _sampleIndex: 0, _scaleTarget: 1, _scaleMs: 0, _slowMs: 0, _slowFactor: 1, _bounce: 0, _bounceTimer: 0, _prevY: 0, _airTime: 0, _latVel: 0, _nudgeVel: null, _wasDrafting: false, _offRoadT: 0, _spinMs: 0, _spinDir: 1, _lastProgress: 0, _startDir: trackData.startLine.direction.clone(),
    _ctrl: { steer: 0, throttle: 0, brake: 0, drift: false },
    setControls(c) { Object.assign(this._ctrl, c); }, applyBoost() {}, addCoin(){return false;}, setInvincible(){}, setRankVisible(){}, swapHeldItems(){},
  };
}
const karts = [];
for (let i = 0; i < 5; i++) karts.push(makeKart(0.012 + i * 0.004, (i % 2 === 0 ? 1 : -1) * (2 + i), i === 0));
const rm = { track: trackData, karts, player: karts[0], elapsed: 0, centerline: trackData.path.getSpacedPoints(240).slice(0, 240), centerlineSpacing: trackData.length / 240, activeItems: [], useItem(){}, restart(){}, getStandings(){ return this.karts.map(k => ({kart:k, lap:k.state.lap, progress01:k.state.progress01, score:k.state.lap*1000+k.state.progress01})).sort((a,b)=>b.score-a.score); } };
const ctrls = karts.map((k, i) => new AIController(k, trackData, rm, i));
const VARIANT = process.argv[4] || 'cur'; // cur | flip | flip40 | clamp12 | clamp20
if (VARIANT === 'flip' || VARIANT === 'flip40') {
  for (const c of ctrls) c.laneOffset = -c.laneOffset * (VARIANT === 'flip40' ? 0.4 : 1);
}
if (VARIANT === 'clamp12' || VARIANT === 'clamp20') {
  const m = VARIANT === 'clamp12' ? 1.2 : 2.0;
  for (const c of ctrls) c.laneOffset = Math.max(-m, Math.min(m, c.laneOffset));
}
const laneExp = ctrls.map(c => c.laneOffset);

const N = 90 * 60;
let frames = 0;
const latSum = karts.map(() => 0), latAbsSum = karts.map(() => 0), onLaneFrames = karts.map(() => 0);
const bounceCount = karts.map(() => 0), bounceDetails = karts.map(() => []), speedPct = karts.map(() => []), errSum = karts.map(() => 0);
let lastBounce = karts.map(() => 0);

for (let frame = 0; frame < N; frame++) {
  const t = frame * DT;
  rm.elapsed = t;
  for (let i = 0; i < karts.length; i++) {
    const k = karts[i];
    KartPhysics.step(k, k._ctrl, DT, trackData, rm);
    k.group.position.copy(k.state.position);
    if (k._spinMs > 0) { k._spinMs = Math.max(0, k._spinMs - DT * 1000); if (k._spinMs === 0) k.state.spinOut = false; }
    if (k._bounceTimer > 0 && k._bounce === 1 && lastBounce[i] <= 0) {
      bounceCount[i]++;
      if (bounceDetails[i].length < 8) bounceDetails[i].push({ t: Number(t.toFixed(2)), progress: Number(k.state.progress01.toFixed(3)), x: Number(k.state.position.x.toFixed(1)), z: Number(k.state.position.z.toFixed(1)) });
    }
    lastBounce[i] = k._bounceTimer;
    // AI update AFTER physics (same order as RaceManager.update)
    ctrls[i].update(DT);
    // true signed lateral vs centerline
    const tt = Math.min(Math.max(k.state.progress01, 0.001), 0.999);
    const tan = trackData.path.getTangentAt(tt);
    const pt = trackData.path.getPointAt(tt);
    const ox = k.state.position.x - pt.x, oz = k.state.position.z - pt.z;
    const lat = ox * tan.z - oz * tan.x; // signed
    latSum[i] += lat; latAbsSum[i] += Math.abs(lat);
    if (Math.abs(lat - laneExp[i]) < 1.5) onLaneFrames[i]++;
    speedPct[i].push(Math.abs(k.state.speed));
    const h = headingVector(k);
    const err = Math.atan2(h.x * tan.z - h.y * tan.x, h.x * tan.x + h.y * tan.z);
    errSum[i] += Math.abs(err);
  }
  frames++;
}
console.log(`TRACK ${TRACK} | steerPredictAhead=${LOOKAHEAD}m | 90s sim`);
for (let i = 0; i < 5; i++) {
  const sp = speedPct[i].sort((a, b) => a - b);
  const p50 = sp[Math.floor(sp.length * 0.5)].toFixed(0);
  const p95 = sp[Math.floor(sp.length * 0.95)].toFixed(0);
  const meanLat = (latSum[i] / frames).toFixed(2);
  console.log(`kart${i} laneExp=${laneExp[i].toFixed(2)} meanLat=${meanLat} onLane%=${((onLaneFrames[i] / frames) * 100).toFixed(0)} bounces=${bounceCount[i]} v[p50,p95]=[${p50},${p95}] meanErrDeg=${((errSum[i] / frames) * 180 / Math.PI).toFixed(1)} details=${JSON.stringify(bounceDetails[i])}`);
}

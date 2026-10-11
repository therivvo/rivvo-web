
import * as THREE from 'three';
import { KartPhysics } from '../src/entities/KartPhysics.js';
import { AIController } from '../src/entities/AIController.js';
import { CONFIG } from '../src/config.js';
import { CITY_PATH, getRoadWidthAt } from '../src/track/TrackBuilder.js';
import { progressScore } from '../src/entities/PowerUp.js';
const DT = 1/60;
const ctrl = CITY_PATH.map(v => v.clone());
const path = new THREE.CatmullRomCurve3(ctrl, true, 'catmullrom', 0.5);
const trackData = { path, length: path.getLength(), getRoadWidthAt, turboPads: {ts: [], points: []}, ramps: [], startLine: {position: path.getPointAt(0), direction: path.getTangentAt(0).normalize(), width: 9} };
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
const rm = { track: trackData, karts, player: karts[0], elapsed: 0, centerline: trackData.path.getSpacedPoints(240).slice(0, 240), centerlineSpacing: trackData.length / 240, activeItems: [], useItem(){}, restart(){}, getStandings(){ const rows = this.karts.map(k => ({kart:k, lap:k.state.lap, progress01:k.state.progress01, score:k.state.lap*1000+k.state.progress01})).sort((a,b)=>b.score-a.score); return rows; } };
const ctrls = karts.map((k, i) => new AIController(k, trackData, rm, i));
let changes = 0; let lastOrder = '';
for (let frame = 0; frame < 60 * 60; frame++) {
  const t = frame * DT; rm.elapsed = t;
  for (let i = 0; i < karts.length; i++) { KartPhysics.step(karts[i], karts[i]._ctrl, DT, trackData, rm); karts[i].group.position.copy(karts[i].state.position); if (karts[i]._spinMs > 0) { karts[i]._spinMs = Math.max(0, karts[i]._spinMs - DT*1000); if (karts[i]._spinMs === 0) karts[i].state.spinOut = false; } }
  for (const c of ctrls) c.update(DT);
  const order = rm.getStandings().map(r => karts.indexOf(r.kart)).join(',');
  if (order !== lastOrder) { changes++; lastOrder = order; }
}
console.log('CITY 60s: standings order changes =', changes, '| frames =', 60*60, '| laps =', karts.map(k => k.state.lap).join(','));

// ============================================================
// ai-backwards-test.mjs — deterministic headless sim for the
// "AI drives backwards" bug in Super Kart 3D.js.
//
// Runs the REAL KartPhysics + AIController (no browser, no WebGL)
// on the real track path at fixed dt=1/60, with stress injections
// that mimic shoves / ramp launches / respawns / spins.
//
// Detection: an AI "backwards event" = |speed| > 5 AND heading
// pointing >~115° away from the path tangent (dot < -0.45) for
// ≥ 0.4s, OR sustained progress regression (progressScore drops
// ≥ 0.05 while moving).
//
// Usage: node scripts/ai-backwards-test.mjs [seeds] [track]
//   seeds: number of random seed runs per scenario (default 8)
//   track: 1 (meadow) | 2 (neon city) (default 1)
// ============================================================
import * as THREE from 'three';
import { KartPhysics } from '../src/entities/KartPhysics.js';
import { AIController } from '../src/entities/AIController.js';
import { CONFIG } from '../src/config.js';
import { TRACK_PATH, CITY_PATH, getRoadWidthAt } from '../src/track/TrackBuilder.js';
import { headingVector, progressScore } from '../src/entities/PowerUp.js';

const SEEDS = parseInt(process.argv[2] || '8', 10);
const TRACK_ID = parseInt(process.argv[3] || '1', 10);
const DT = 1 / 60;
const DURATION_S = 60; // sim seconds per run
const BACK_DOT = -0.45; // dot(heading, tangent) below this while moving = facing backwards
const BACK_MIN_SPEED = 8;  // user-visible: a backwards RUN, not a slow U-turn
const BACK_PERSIST_S = 0.7; // recovery U-turns measure 0.4-0.6s (F6); the old brake bug ran ~1.2s — 0.7 catches it, rejects recoveries

// ---------- deterministic RNG (mulberry32) ----------
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---------- build track ----------
function buildTrackData(id) {
  const ctrl = id === 2 ? CITY_PATH : TRACK_PATH;
  const pts = ctrl.map((v) => v.clone());
  const path = new THREE.CatmullRomCurve3(pts, true, 'catmullrom', 0.5);
  const length = path.getLength();
  const startPos = path.getPointAt(0);
  const startDir = path.getTangentAt(0).normalize();
  return {
    path,
    length,
    getRoadWidthAt,
    turboPads: { ts: [], points: [] },
    ramps: [],
    startLine: { position: startPos, direction: startDir, width: getRoadWidthAt() },
  };
}

// ---------- duck-typed kart (enough for KartPhysics + AIController) ----------
function makeKart(trackData, startT, startLateral, headingOverride, isPlayer = false) {
  const p = trackData.path.getPointAt(startT);
  const tan = trackData.path.getTangentAt(startT);
  const nrm = new THREE.Vector3(-tan.z, 0, tan.x).normalize();
  const pos = p.clone().addScaledVector(nrm, startLateral);
  const heading = headingOverride !== undefined ? headingOverride : Math.atan2(tan.x, tan.z);
  const group = new THREE.Group();
  group.position.copy(pos);
  const kart = {
    isPlayer,
    number: 1,
    character: { name: 'Sim', stats: { speed: 7, accel: 7, handling: 7 } },
    rideHeight: CONFIG.kart.wheelRadius + 0.04,
    group,
    state: {
      speed: 0,
      position: pos,
      heading,
      drifting: false,
      driftCharge: 0,
      boost: false,
      turboBoostMs: 0,
      offRoad: false,
      spinOut: false,
      lap: 0,
      progress01: 0,
      vY: 0,
      onRamp: false,
      draft: false,
    },
    finished: false,
    cruiseSpeed: undefined,
    heldItem: null,
    heldItem2: null,
    _rearThrow: false,
    _samples: null,
    _sampleIndex: 0,
    _scaleTarget: 1, _scaleMs: 0, _slowMs: 0, _slowFactor: 1,
    _bounce: 0, _bounceTimer: 0, _prevY: 0, _airTime: 0, _latVel: 0,
    _nudgeVel: null, _wasDrafting: false, _offRoadT: 0, _spinMs: 0, _spinDir: 1,
    _lastProgress: 0, _startDir: trackData.startLine.direction.clone(),
    _ctrl: { steer: 0, throttle: 0, brake: 0, drift: false },
    setControls(c) { Object.assign(this._ctrl, c); },
    applyBoost() {},
    addCoin() { return false; },
    setInvincible() {},
    setRankVisible() {},
    swapHeldItems() {},
  };
  return kart;
}

// ---------- fake RaceManager (duck-typed API for AIController) ----------
function makeManager(trackData, karts, player) {
  return {
    track: trackData,
    karts,
    player: player || null,
    elapsed: 0,
    centerline: trackData.path.getSpacedPoints(240).slice(0, 240), // match RaceManager (drop seam duplicate)
    centerlineSpacing: Math.max(1.5, trackData.length / 240),
    activeItems: [],
    useItem() {},
    restart() {},
    getStandings() {
      const rows = this.karts.map((kart) => {
        const st = kart.state;
        return { kart, lap: st.lap, progress01: st.progress01, score: st.lap * 1000 + st.progress01 };
      });
      rows.sort((a, b) => b.score - a.score);
      return rows;
    },
  };
}

// ---------- stress injections (return list of {at, apply}) ----------
function buildInjections(rng, trackData, seed) {
  const n = trackData.length;
  const inj = [];
  const t = () => rng() * 0.96 + 0.02;
  // (a) off-road lateral shove: kart displaced 20-38m lateral, keeps speed
  inj.push({
    at: 3 + rng() * 12, apply(karts) {
      const k = karts[1 + Math.floor(rng() * 4)];
      const tt = t();
      const p = trackData.path.getPointAt(tt);
      const tan = trackData.path.getTangentAt(tt);
      const side = rng() < 0.5 ? 1 : -1;
      const lat = (20 + rng() * 18) * side;
      const nrm = new THREE.Vector3(-tan.z, 0, tan.x).normalize();
      k.state.position.copy(p).addScaledVector(nrm, lat);
      k.state.heading = Math.atan2(tan.x, tan.z); // facing forward, far off road
      k.state.speed = 25 + rng() * 15;
    },
  });
  // (b) forward launch (ramp-like): kart displaced +15-30m along the path
  inj.push({
    at: 18 + rng() * 15, apply(karts) {
      const k = karts[1 + Math.floor(rng() * 4)];
      const tt = t();
      const p = trackData.path.getPointAt(tt);
      const tan = trackData.path.getTangentAt(tt);
      const ahead = (12 + rng() * 18) / trackData.length;
      const p2 = trackData.path.getPointAt(Math.min(0.995, tt + ahead));
      k.state.position.copy(p2);
      k.state.heading = Math.atan2(tan.x, tan.z);
      k.state.speed = 40 + rng() * 10;
    },
  });
  // (c) spin: REAL T-bone path — spinOut state + _spinMs timer + _spinDir
  // (KartPhysics rotates the heading and decays speed while it runs; the AI
  // releases controls until crashRecoverMs; recovery is at low speed)
  inj.push({
    at: 34 + rng() * 12, apply(karts) {
      const k = karts[1 + Math.floor(rng() * 4)];
      k.state.spinOut = true;
      k._spinMs = 550 + rng() * 400;
      k._spinDir = rng() < 0.5 ? -1 : 1;
      k.state.speed = 20 + rng() * 15;
    },
  });
  // (d2) REAL ITEM HIT (AUDIT 2026-08-11): the old spin injection only used
  // 550-950ms, but hitShell spins 2100ms / hitBanana 1500ms — a real hit
  // keeps the kart under 1 m/s for ~2.1s spin + recovery, which is why the
  // STUCK detector must exempt post-hit recovery. This injection exercises
  // the full long-spin + recovery path.
  inj.push({
    at: 44 + rng() * 6, apply(karts) {
      const k = karts[1 + Math.floor(rng() * 4)];
      k.state.spinOut = true;
      k._spinMs = 1500 + rng() * 600;
      k._spinDir = rng() < 0.5 ? -1 : 1;
      k.state.speed = 18 + rng() * 12;
    },
  });
  // (d) rear-end at speed: kart pushed 8-14m forward AND off-road
  inj.push({
    at: 48 + rng() * 8, apply(karts) {
      const k = karts[1 + Math.floor(rng() * 4)];
      const tt = t();
      const tan = trackData.path.getTangentAt(tt);
      const ahead = (8 + rng() * 6) / trackData.length;
      const p2 = trackData.path.getPointAt(Math.min(0.995, tt + ahead));
      const nrm = new THREE.Vector3(-tan.z, 0, tan.x).normalize();
      k.state.position.copy(p2).addScaledVector(nrm, (6 + rng() * 10) * (rng() < 0.5 ? 1 : -1));
      k.state.heading = Math.atan2(tan.x, tan.z);
      k.state.speed = 30 + rng() * 12;
    },
  });
  // (e) off-road crawl: kart shoved deep off-road at ~0 speed — the Lakitu
  // rescue (RaceManager._updateRescues mirror below) needs 2s of
  // offRoad && |speed| < 3; a shallow shove recovers too fast to ever trip
  // it (re-audit: rescues never fired). Force _stuckT to 1.9s so the rescue
  // path is exercised deterministically on the NEXT frame — covers the
  // rescue-recovery AI path (the old bug class: wrong-way after a teleport).
  inj.push({
    at: 52 + rng() * 6, apply(karts) {
      const k = karts[1 + Math.floor(rng() * 4)];
      const tt = t();
      const tan = trackData.path.getTangentAt(tt);
      const nrm = new THREE.Vector3(-tan.z, 0, tan.x).normalize();
      k.state.position.copy(trackData.path.getPointAt(tt)).addScaledVector(nrm, (20 + rng() * 15) * (rng() < 0.5 ? 1 : -1));
      k.state.heading = Math.atan2(tan.x, tan.z);
      k.state.speed = 0;
      k._stuckT = 1.99; // fires on the next frame — the kart accelerates past
      // 3 m/s in ~6 frames, so a 1.9 seed never reached 2.0 (rescues stayed 0)
    },
  });
  return inj;
}

// ---------- run one seeded race ----------
function runRace(seed, trackData) {
  const rng = mulberry32(seed);
  const karts = [];
  const N = 5;
  // grid: 5 karts spread just PAST the start seam (avoids the natural
  // progress01 0.995→0 wrap at frame 0 being counted as regression)
  for (let i = 0; i < N; i++) {
    karts.push(makeKart(trackData, 0.012 + i * 0.004, (i % 2 === 0 ? 1 : -1) * (2 + i), undefined, i === 0));
  }
  const player = karts[0];
  const rm = makeManager(trackData, karts, player);
  const ctrls = karts.map((k, i) => new AIController(k, trackData, rm, i));
  const injections = buildInjections(rng, trackData, seed);

  const events = [];
  let rescues = 0;
  let epStart = new Array(N).fill(null); // episode start time per kart
  let stuckT = new Array(N).fill(0); // seconds a kart has been crawling (<1 m/s)
  let stuckPos = new Array(N).fill(null);
  let epMin = new Array(N).fill(0); // min progressScore during episode
  let lastScore = karts.map((k) => progressScore(k));
  let maxScore = karts.map((k) => progressScore(k)); // running max per kart
  const sanity = { frames: 0, onRoad: new Array(N).fill(0), speedSum: new Array(N).fill(0) };

  for (let frame = 0; frame < DURATION_S * 60; frame++) {
    const t = frame * DT;
    rm.elapsed = t;
    // apply injections
    for (const inj of injections) {
      if (!inj._done && t >= inj.at) { inj._done = true; inj.apply(karts); }
    }
    // physics + AI (same order as RaceManager.update)
    for (let i = 0; i < karts.length; i++) {
      const k = karts[i];
      KartPhysics.step(k, k._ctrl, DT, trackData, rm);
      // Kart.update() syncs group.position from state.position every frame;
      // kartPosition() (used by the AI) reads group.position — without this
      // the AI would steer toward a frozen position (harness fidelity).
      k.group.position.copy(k.state.position);
      // Kart.js spin timer: _spinMs drains, then spinOut clears (Kart.update
      // does this in the real game; the duck-typed kart needs it here).
      if (k._spinMs > 0) {
        k._spinMs = Math.max(0, k._spinMs - DT * 1000);
        if (k._spinMs === 0) k.state.spinOut = false;
      }
    }
    for (const c of ctrls) c.update(DT);

    // Lakitu rescue (mirrors RaceManager._updateRescues): an off-road kart
    // crawling below 3 m/s for >= 2s is teleported to its progress point
    // facing the tangent — exercises the rescue-recovery AI path.
    for (let i = 0; i < karts.length; i++) {
      const k = karts[i];
      if (k.finished || k.state.spinOut) { k._stuckT = 0; continue; }
      // OOB rescue mirror (RaceManager._updateRescues)
      const oobK = Math.abs(k.state.position.x) > 95 || Math.abs(k.state.position.z) > 62;
      if (oobK) {
        k._stuckT = (k._stuckT || 0) + DT;
        if (k._stuckT >= 1) {
          const ttR = Math.min(Math.max(k.state.progress01, 0.001), 0.999);
          const pR = trackData.path.getPointAt(ttR);
          const tanR = trackData.path.getTangentAt(ttR);
          k.state.position.set(pR.x, pR.y + 0.5, pR.z);
          k.state.heading = Math.atan2(tanR.x, tanR.z);
          k.state.speed = 0;
          k.state.spinOut = false;
          k._stuckT = 0;
          rescues++;
        }
        continue;
      }
      if (k.state.offRoad && Math.abs(k.state.speed) < 3 && typeof k.state.progress01 === 'number') {
        k._stuckT = (k._stuckT || 0) + DT;
        if (k._stuckT >= 2) {
          const ttR = Math.min(Math.max(k.state.progress01, 0.001), 0.999);
          const pR = trackData.path.getPointAt(ttR);
          const tanR = trackData.path.getTangentAt(ttR);
          k.state.position.set(pR.x, pR.y, pR.z);
          k.state.heading = Math.atan2(tanR.x, tanR.z);
          k.state.speed = 0;
          k.state.spinOut = false;
          k._stuckT = 0;
          rescues++;
        }
      } else {
        k._stuckT = 0;
      }
    }

    // STUCK detection: a kart crawling below 1 m/s for >= 2.5s continuous
    // while the race is live is stuck (AI bug class — Feco: 'bots travados
    // em certo ponto da pista'). Report the exact spot.
    for (let i = 0; i < karts.length; i++) {
      const k = karts[i];
      if (k.finished || k.state.spinOut || k._ctrl.crashRecovering) { stuckT[i] = 0; stuckPos[i] = null; continue; }
      const sp = Math.abs(k.state.speed);
      if (sp < 1) {
        stuckT[i] += DT;
        if (!stuckPos[i]) stuckPos[i] = k.state.position.clone();
        if (stuckT[i] >= 2.5) {
          events.push({ type: 'stuck', kart: i, t: t.toFixed(2), pos: [stuckPos[i].x.toFixed(1), stuckPos[i].z.toFixed(1)], prog: (k.state.progress01 || 0).toFixed(3), v: sp.toFixed(1) });
          stuckT[i] = 0;
          stuckPos[i] = null;
        }
      } else {
        stuckT[i] = 0;
        stuckPos[i] = null;
      }
    }

    // LOST-KART detection (AUDIT 2026-08-11, Jarvis QA loop): a kart that
    // leaves the track and keeps driving AWAY (progress frozen, speed > 2)
    // is neither stuck (<1 m/s) nor backwards (dot < -0.45) — the old harness
    // reported '0 events' while city seeds showed laps=[3,0,...] (kart flew
    // off the map). Track off-road time + progress stagnation per kart.
    for (let i = 0; i < karts.length; i++) {
      const k = karts[i];
      if (k.finished || k.state.spinOut) { k._lostT = 0; continue; }
      const progNow = typeof k.state.progress01 === 'number' ? k.state.progress01 : 0;
      if (k.state.offRoad && Math.abs(k.state.speed) > 2) {
        if (!k._lostProg) k._lostProg = progNow;
        k._lostT = (k._lostT || 0) + DT;
        // frozen progress (stalled for >0.5s) OR out of map bounds → lost
        const frozen = Math.abs(progNow - k._lostProg) < 0.001;
        const oob = Math.abs(k.state.position.x) > 95 || Math.abs(k.state.position.z) > 62;
        if ((frozen && k._lostT > 0.5) || (oob && k._lostT > 1.0)) {
          events.push({ type: 'lost', kart: i, t: t.toFixed(2), pos: [k.state.position.x.toFixed(1), k.state.position.z.toFixed(1)], prog: progNow.toFixed(3), v: Math.abs(k.state.speed).toFixed(1), offRoadS: k._lostT.toFixed(1) });
          k._lostT = 0; k._lostProg = null;
        }
      } else {
        k._lostT = 0; k._lostProg = null;
      }
    }

    // sanity accumulation (on-road fraction within ±6m of the centerline).
    // F5: TRUE lateral = |(pos - pathPoint(progress01)) x tangent| — the old
    // |p x tan| measured distance to the ORIGIN line, printing 0% on-road for
    // karts that were genuinely on the road.
    sanity.frames++;
    for (let i = 0; i < karts.length; i++) {
      const kk = karts[i];
      const tt2 = Math.min(Math.max(kk.state.progress01, 0.001), 0.999);
      const tan2 = trackData.path.getTangentAt(tt2);
      const pt2 = trackData.path.getPointAt(tt2);
      const ox = kk.state.position.x - pt2.x;
      const oz = kk.state.position.z - pt2.z;
      const lateral = Math.abs(ox * tan2.z - oz * tan2.x);
      if (lateral < 6) sanity.onRoad[i]++;
      sanity.speedSum[i] += Math.abs(kk.state.speed);
    }

    // detection — EPISODE-based: a "backwards run" is a kart facing away
    // from the path tangent (dot < -0.45) at speed for a SUSTAINED window
    // WITH progress loss. A brief recovery U-turn after a T-bone spin is
    // normal racing (~0.5-1s, no sustained progress loss); the user bug is
    // a kart RUNNING backwards for seconds.
    for (let i = 0; i < karts.length; i++) {
      const k = karts[i];
      const tt = Math.min(Math.max(k.state.progress01, 0.001), 0.999);
      const tan = trackData.path.getTangentAt(tt);
      const h = headingVector(k);
      const dot = h.x * tan.x + h.y * tan.z;
      const speed = Math.abs(k.state.speed);
      const sc = progressScore(k);
      if (sc > maxScore[i]) maxScore[i] = sc;
      if (dot < BACK_DOT && speed > BACK_MIN_SPEED) {
        if (epStart[i] === null) { epStart[i] = t; epMin[i] = sc; }
        if (sc < epMin[i]) epMin[i] = sc;
      } else if (epStart[i] !== null) {
        const dur = t - epStart[i];
        const lost = maxScore[i] - epMin[i];
        // loss gate 0.02 (≈8-13m) — the ORIGINAL brake bug only lost ~0.028
        // progress at reverseSpeed 12 over ~1.2s; 0.05 would have missed it
        if (dur >= BACK_PERSIST_S && lost >= 0.02) {
          events.push({ seed, frame: Math.round(frame), t: +t.toFixed(2), kart: i, dot: +dot.toFixed(2), speed: +k.state.speed.toFixed(1), prog: +k.state.progress01.toFixed(3), lap: k.state.lap, type: 'backwards-run', dur: +dur.toFixed(2), lost: +lost.toFixed(3) });
        }
        epStart[i] = null;
      }
      if (sc > lastScore[i]) lastScore[i] = sc;
    }
    // end early if we already have plenty of evidence
    if (events.length > 8) break;
  }
  const onRoadPct = sanity.frames > 0 ? sanity.onRoad.map((n) => Math.round((n / sanity.frames) * 100)) : [];
  const avgSpeed = sanity.frames > 0 ? sanity.speedSum.map((s) => +(s / sanity.frames).toFixed(1)) : [];
  return { events, laps: karts.map((k) => k.state.lap), onRoadPct, avgSpeed, rescues };
}

// ---------- main ----------
const trackData = buildTrackData(TRACK_ID);
let totalEvents = 0;
let totalLost = 0;
let crashes = 0;
const byScenario = {};
console.log(`Track ${TRACK_ID} | seeds=${SEEDS} | dt=${DT}s | ${DURATION_S}s/run | detection: dot<${BACK_DOT} & |v|>${BACK_MIN_SPEED} for ${BACK_PERSIST_S}s`);
for (let s = 0; s < SEEDS; s++) {
  const seed = 1000 + s * 137;
  let res;
  try {
    res = runRace(seed, trackData);
  } catch (e) {
    console.log(`seed ${seed}: CRASH ${String(e.message || e).slice(0, 90)}`);
    crashes++;
    continue;
  }
  const { events, laps, onRoadPct, avgSpeed, rescues } = res;
  const kinds = {};
  for (const e of events) kinds[e.type] = (kinds[e.type] || 0) + 1;
  totalEvents += events.length;
  totalLost += events.filter(e => e.type === 'lost').length;
  if (events.filter(e => e.type === 'lost').length) {
    const lostStr = events.filter(e => e.type === 'lost').map(function (e) {
      return 'kart' + e.kart + '@' + e.t + 's (' + e.pos[0] + ',' + e.pos[1] + ') prog=' + e.prog + ' v=' + e.v + ' offRoad=' + e.offRoadS + 's';
    }).join(' | ');
    console.log('  LOST: ' + lostStr);
  }
  if (events.length) {
    console.log(`seed ${seed}: ${events.length} EVENT(S) ${JSON.stringify(kinds)} | laps=${JSON.stringify(laps)} onRoad=${JSON.stringify(onRoadPct)} avgV=${JSON.stringify(avgSpeed)}`);
    for (const e of events.slice(0, 3)) {
      console.log(`    t=${e.t}s kart=${e.kart} ${e.type} ${e.pos ? 'pos=(' + e.pos.join(',') + ')' : ''} dot=${e.dot} v=${e.speed} prog=${e.prog} lap=${e.lap}`);
    }
  } else {
    console.log(`seed ${seed}: clean (${events.length}) | laps=${JSON.stringify(laps)} onRoad=${JSON.stringify(onRoadPct)} avgV=${JSON.stringify(avgSpeed)} rescues=${rescues}`);
  }
}
console.log(`\nTOTAL LOST EVENTS: ${totalLost}
TOTAL BACKWARDS EVENTS: ${totalEvents} / ${SEEDS} runs`);
console.log(`\nCRASHES: ${crashes}`);
process.exit(totalEvents > 0 || crashes > 0 ? 1 : 0);

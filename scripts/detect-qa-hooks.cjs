#!/usr/bin/env node
/**
 * detect-qa-hooks.cjs — descobre os QA hooks de um jogo web para o
 * framework game-motion-qa (camada de adaptação a jogos novos).
 *
 * Navega até a URL, lista globais candidatas (window.__sk3d, __game, __qa,
 * __sk3d, etc.), verifica se expõem karts/state, e imprime os campos de
 * estado do primeiro kart encontrado — o ponto de partida para mapear
 * invariantes (position/heading/speed/progress/lap/offRoad).
 *
 * Usage:
 *   node detect-qa-hooks.cjs <url> [--depth 2]
 *
 * Saída: JSON com { hooks: [...], chosen: {...}, kartStateFields: [...] }
 * Feche o browser e saia com 0 sempre.
 */
const path = require('path');
const fs = require('fs');

const args = process.argv.slice(2);
const URL = args[0];
const depthIdx = args.indexOf('--depth');
const DEPTH = depthIdx >= 0 ? parseInt(args[depthIdx + 1], 10) : 2;

if (!URL) {
  console.error('usage: node detect-qa-hooks.cjs <url> [--depth N]');
  process.exit(1);
}

(async () => {
  const { chromium } = require(process.env.NODE_PATH
    ? path.join(process.env.NODE_PATH, 'playwright')
    : 'playwright');
  const browser = await chromium.launch({
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--enable-unsafe-swiftshader',
      '--use-gl=angle', '--use-angle=swiftshader'],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  try {
    await page.route('**fonts.googleapis.com/**', (r) => r.abort());
    await page.route('**fonts.gstatic.com/**', (r) => r.abort());
    console.log(`URL: ${URL}`);
    await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 45000 });
    // espera o boot (até 20s)
    await new Promise((r) => setTimeout(r, 3000));

    const result = await page.evaluate((depth) => {
      const out = { hooks: [], chosen: null, kartStateFields: null, gameObjects: [] };
      const skip = ['window', 'self', 'top', 'parent', 'frames', 'length', 'name', 'closed',
        'location', 'document', 'navigator', 'performance', 'localStorage', 'sessionStorage'];
      // 1) globais com prefixo __ ou que pareçam QA hooks
      for (const k of Object.getOwnPropertyNames(window)) {
        if (k.startsWith('__') && k !== '__core-js_shared__') {
          const v = window[k];
          const type = typeof v;
          let desc = type;
          if (v && type === 'object') {
            desc = Object.getOwnPropertyNames(v).slice(0, 12).join(',');
          }
          out.hooks.push({ name: k, type, props: desc });
        }
      }
      // 2) procurar karts/state em profundidade nos hooks candidatos
      const candidates = out.hooks.filter((h) => /sk3d|game|qa|tel|debug|test/i.test(h.name));
      for (const h of candidates) {
        try {
          const v = window[h.name];
          // procura um array de karts (props com state)
          const seen = new WeakSet();
          const scan = (obj, d) => {
            if (!obj || d > depth) return null;
            if (typeof obj !== 'object') return null;
            if (seen.has(obj)) return null; // anti-ciclo (scene.parent etc.)
            seen.add(obj);
            if (Array.isArray(obj) && obj.length && obj[0] && obj[0].state) return obj;
            for (const key of Object.keys(obj).slice(0, 20)) {
              // karts pode estar VAZIO no menu (antes de iniciar a corrida) —
              // ainda assim é o hook certo; campos aparecem após start
              if (key === 'karts' && Array.isArray(obj[key])) return obj[key];
              if (typeof obj[key] === 'object' && obj[key]) {
                const found = scan(obj[key], d + 1);
                if (found) return found;
              }
            }
            return null;
          };
          const karts = scan(v, 0);
          if (karts) {
            out.chosen = h.name;
            out.kartsLength = karts.length;
            out.kartStateFields = karts[0] && karts[0].state ? Object.keys(karts[0].state) : null;
            out.note = karts.length === 0
              ? 'karts array encontrado mas VAZIO (menu/pré-corrida) — inicie uma corrida e rode de novo para mapear os campos'
              : 'ok';
            out.gameObjects = karts.map((k, i) => ({
              id: i,
              state: k.state ? Object.fromEntries(Object.entries(k.state).map(([kk, vv]) =>
                [kk, typeof vv === 'object' && vv ? (vv.x !== undefined ? `{x,y,z}` : typeof vv) : typeof vv])) : null,
            }));
            break;
          }
        } catch { /* ignore */ }
      }
      return out;
    }, DEPTH);

    console.log(JSON.stringify(result, null, 2));
  } finally {
    await browser.close();
    process.exit(0);
  }
})().catch((e) => {
  console.error('ERROR:', e && e.stack ? e.stack : e);
  process.exit(1);
});

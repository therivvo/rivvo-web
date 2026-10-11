/**
 * Super Kart 3D.js — Visual Scorecard Runner (threejs-aaa-graphics-builder).
 *
 * Gera o Visual Scorecard da skill a partir de:
 *   1. Screenshots de active-play (desktop + mobile) — passados como args.
 *   2. renderReport do jogo (calls/tris/tex/geo) — lido de um JSON ou do browser.
 *
 * Como o headless SwiftShader throtta rAF (~1fps) e o vision provider pode
 * estar instável, este script é feito para rodar em GPU REAL (Feco) ou em
 * qualquer ambiente onde as capturas sejam de corrida ativa.
 *
 * Uso:
 *   node scripts/scorecard.cjs <desktop.png> <mobile.png> [renderReport.json]
 *
 * Saída: scorecard no formato da skill (categorias 0-3 + Measured Evidence).
 *
 * O score por categoria é SELF-ASSESSED (o autor do score), mas o script
 * injeta as medições objetivas (colorEntropy/edgeDensity/lumContrast/
 * dominantColorShare) e os diagnostics de renderer para desafiar scores altos.
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

// Reusa o inspector de canvas (mesma pasta)
const INSPECT = process.env.INSPECT_OVERRIDE || path.join(__dirname, 'inspect-canvas-metrics.cjs');

async function inspect(file) {
  const { execSync } = require('child_process');
  const NODE = process.env.NODE_PATH || '/home/jarvis/.hermes/node/lib/node_modules';
  const out = execSync(`node ${INSPECT} ${file} _`, { encoding: 'utf8', env: { ...process.env, NODE_PATH: NODE } });
  // extrai o JSON do stdout
  const m = out.match(/\{[\s\S]*"metrics"[\s\S]*\}\s*$/);
  if (!m) return null;
  return JSON.parse(m[0]).metrics;
}

function scoreFromMetrics(m, label) {
  // Heurísticas defensivas da skill (não substituem avaliação visual):
  const flags = [];
  if (m.colorEntropyBits < 3.0) flags.push('colorEntropy<3.0 (cena plana/esparsa)');
  if (m.edgeDensity < 0.04) flags.push('edgeDensity<0.04 (primitive-dominant/empty)');
  if (m.luminanceContrast < 60) flags.push('lumContrast<60 (fog/darkness compression)');
  if (m.dominantColorShare > 0.6) flags.push('dominantColor>0.6 (sparse/flat)');
  return flags;
}

function main() {
  const [, , desk, mob, rrJson] = process.argv;
  if (!desk || !mob) {
    console.error('USO: node scorecard.cjs <desktop.png> <mobile.png> [renderReport.json]');
    process.exit(1);
  }
  (async () => {
    const dMetrics = await inspect(desk);
    const mMetrics = await inspect(mob);
    let rr = null;
    if (rrJson && fs.existsSync(rrJson)) rr = JSON.parse(fs.readFileSync(rrJson, 'utf8'));

    const dFlags = scoreFromMetrics(dMetrics, 'desktop');
    const mFlags = scoreFromMetrics(mMetrics, 'mobile');

    // Scorecard template — categorias self-assessed; PREENCHA após ver as capturas.
    const cats = [
      'Art direction', 'Hero/player', 'Obstacles/enemies', 'Rewards/interactables',
      'World/environment', 'Materials/textures', 'Lighting/render', 'VFX/motion',
      'UI/HUD', 'Performance evidence',
    ];
    const scorecard = {};
    for (const c of cats) scorecard[c] = '?'; // autor preenche 0-3 olhando a captura

    const report = {
      captured: new Date().toISOString(),
      screenshots: { desktop: desk, mobile: mob },
      measuredEvidence: {
        desktop: dMetrics,
        mobile: mMetrics,
        redFlags: { desktop: dFlags, mobile: mFlags },
      },
      rendererDiagnostics: rr,
      visualScorecard: scorecard,
      automaticFailuresRemaining: 'PREENCHA (ver skill visual-scorecard.md)',
      note: 'Self-assessed scores require visual review. Measured evidence above challenges scores >2 when flags present.',
    };
    const outFile = path.join(process.cwd(), 'scorecard-result.json');
    fs.writeFileSync(outFile, JSON.stringify(report, null, 2));
    console.log('Scorecard escrito em', outFile);
    console.log('Desktop flags:', dFlags.length ? dFlags.join('; ') : 'none');
    console.log('Mobile flags:', mFlags.length ? mFlags.join('; ') : 'none');
    if (rr) console.log('Renderer:', JSON.stringify({ calls: rr.calls, tris: rr.triangles, tex: rr.textures, geo: rr.geometries }));
  })().catch(e => { console.error('ERR', e.message); process.exit(1); });
}

main();

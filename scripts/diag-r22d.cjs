// Diag R22d: valores reais dos uniforms do ColorGrade + bloom strength em runtime
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(3000);
  const r = await page.evaluate(async () => {
    // acessar via módulo PostFX não é direto; ler do composer global se exposto
    const fx = window.__sk3d.postfx || null;
    if (!fx || !fx.composer) return 'no postfx handle';
    const out = { passes: [] };
    for (const p of fx.composer.passes) {
      const u = p.uniforms || (p.material && p.material.uniforms);
      out.passes.push({
        name: p.constructor.name,
        warmth: u && u.warmth ? u.warmth.value : null,
        saturation: u && u.saturation ? u.saturation.value : null,
        strength: p.strength ?? null,
        enabled: p.enabled,
      });
    }
    return out;
  });
  console.log(JSON.stringify(r));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });

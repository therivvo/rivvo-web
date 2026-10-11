let chromium;
try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('/opt/pwtest/node_modules/playwright')); }
const fs = require('fs');
(async () => {
  const [url, out = 'qa-gpu-runner/haze-matrix'] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--use-gl=angle', '--use-angle=vulkan', '--no-sandbox', '--mute-audio'] });
  for (const mode of ['current', 'no-fog', 'no-vignette', 'no-speedlines', 'no-postfx']) {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, hasTouch: true });
    const page = await context.newPage();
    await page.addInitScript(() => localStorage.clear());
    await page.goto(`${url}/?demo&track=1`, { waitUntil: 'domcontentloaded', timeout: 120000 });
    await page.waitForTimeout(12000);
    const metrics = await page.evaluate((selected) => {
      const s = window.__sk3d;
      if (selected === 'no-fog') s.scene.fog = null;
      if (selected === 'no-vignette') {
        const pass = s.postfx?.composer?.passes?.find((p) => p.material?.uniforms?.darkness);
        if (pass) pass.enabled = false;
      }
      if (selected === 'no-postfx') s.postfx.enabled = false;
      if (selected === 'no-speedlines') {
        const canvas = document.querySelector('.sk3d-speedlines');
        if (canvas) canvas.style.display = 'none';
      }
      return { mode: selected, quality: s.renderReport?.(), fog: !!s.scene.fog, postfx: s.postfx?.enabled, phase: s.raceManager?.phase };
    }, mode);
    await page.screenshot({ path: `${out}/${mode}.png` });
    fs.writeFileSync(`${out}/${mode}.json`, JSON.stringify(metrics, null, 2));
    console.log(JSON.stringify(metrics));
    await context.close();
  }
  await browser.close();
})();

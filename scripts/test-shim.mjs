// Test shim: provides a minimal `window` global so headless sim scripts can
// import production modules (MaterialLibrary reads window.__sk3dQualityProfile
// at load time). No real browser needed — just enough surface to not throw.
if (typeof globalThis.window === 'undefined') {
  globalThis.window = globalThis;
}
// Minimal quality profile so MaterialLibrary's cache key works headless.
if (!globalThis.window.__sk3dQualityProfile) {
  globalThis.window.__sk3dQualityProfile = { name: 'medium', foliageDensity: 1, crowdDensity: 1, particleDensity: 1 };
}
if (typeof globalThis.window.addEventListener !== 'function') {
  globalThis.window.addEventListener = () => {};
  globalThis.window.removeEventListener = () => {};
}
if (typeof globalThis.window.matchMedia !== 'function') {
  globalThis.window.matchMedia = () => ({ matches: false, addEventListener: () => {}, removeEventListener: () => {} });
}
if (typeof globalThis.document === 'undefined') {
  // Minimal document stub for any canvas/texture access during import.
  globalThis.document = {
    createElement: () => ({
      getContext: () => null,
      width: 1, height: 1,
      style: {},
      appendChild: () => {},
    }),
    body: { appendChild: () => {} },
    addEventListener: () => {},
  };
}

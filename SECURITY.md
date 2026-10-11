# Security Policy

## Supported Versions

Super Kart 3D.js is a client-side browser game. Only the latest release on
the `main` branch receives security updates. Older tags are not patched —
users are encouraged to stay on the latest version.

| Version | Supported          |
|---------|--------------------|
| latest (main) | ✅ |
| older tags | ❌ |

## Scope

This project is a pure client-side application (JavaScript + Three.js) served
as static files. There is **no backend, no server-side processing, and no
user data storage**. The security surface is limited to:

- **Dependencies** — `three` and build tooling (`vite`). Vulnerabilities in
  those libraries are handled by upgrading the dependency.
- **Supply chain** — the published build is generated from the `main` branch
  by GitHub Actions using a locked `package-lock.json`.

## Reporting a Vulnerability

Please **do not open a public issue**. Report vulnerabilities privately via
GitHub's security advisory flow:

https://github.com/fecolinhares/super-kart-3djs/security/advisories/new

You should receive a response within 7 days. If the issue is confirmed, a fix
will be released on `main` as soon as possible and the vulnerability disclosed
responsibly.

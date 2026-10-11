# Contributing to Super Kart 3D.js

Thanks for your interest! This project follows the same open-source
conventions as its sibling project **Match-3D.js** — keep it consistent.

## Getting started

1. Fork the repository and clone your fork.
2. `npm install`
3. `npm run dev` — open http://localhost:3457

## Branch & commit conventions

- Branch names: `feat/description`, `fix/description`, `docs/description`,
  `ci/description`.
- **Atomic commits**: one logical change per commit, always with a clear
  message using [Conventional Commits](https://www.conventionalcommits.org/):
  `feat(scope): description`, `fix(scope): description`, `docs: ...`, `ci: ...`.
- Keep the working tree clean between commits — never bundle unrelated changes.

## Code style

- ES modules (`type: module`), 2-space indent, single quotes, semicolons.
- UI copy and docs are **100% English** (the project targets a global audience).
- Never hardcode secrets, local paths or machine-specific values. Config
  belongs in `src/config.js` (gameplay) or environment variables (build).
- Public APIs live in `ARCHITECTURE.md` — if you change a module
  contract, update the document in the same commit.

## Quality bar

This project targets **AAA-grade visuals**. Before opening a PR:

- `npm run build` must pass.
- New visuals must be verified with a screenshot (desktop + mobile) —
  see the visual QA loop described in `ARCHITECTURE.md`.

## Pull requests

Use the [pull request template](.github/pull_request_template.md). Keep PRs
small and focused; link related issues.

## Code of Conduct

Everyone is expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

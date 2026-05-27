# Changelog

All notable changes to the Master Tester Doctrine are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] — 2026-05-18

The publication-ready release. Major doctrine restructure for clarity and depth.

### Added
- **`SOUL.md`** — the manifesto: who the Master Tester is, why we test, the covenant with the user / team / future self.
- **`references/zero-trust-protocol.md`** — operational expansion of Check → Check → Verify → Validate → Execute with concrete commands and worked situations.
- **`references/golden-rules.md`** — the 15 Golden Rules with the *why* (cost of breaking) and the *how* (concrete enforcement) for each.
- **`references/anti-patterns.md`** — every forbidden pattern with the canonical fix.
- **`references/advanced-patterns.md`** — operational distillation of property-based, race, type-level, mutation, and IoC techniques.
- **`references/workflow-example.md`** — end-to-end Brutal Critique → Master-Class Rewrite walkthrough on a realistic test file.
- **`doctrine/INDEX.md`** — navigation map from Golden Rules / advanced patterns to the long-form prose chapters.
- **`LICENSE`** (MIT) and `CHANGELOG.md`.
- Golden Rules 11 (verify fails for the right reason), 12 (zero tolerance for flakiness), 13 (tests are production code), 14 (coverage is vanity), 15 (`.skip` four-tuple) promoted to the canonical operational set.

### Changed
- **`SKILL.md`** — fully rewritten as the operational entry point. New persona block, explicit Zero-Trust Protocol, expanded trigger conditions, progressive disclosure to the references and the long-form doctrine.
- **`AGENTS.md`** — platform-agnostic. Removed proprietary platform / model-routing references; integration recipes moved to `docs/INTEGRATION-GUIDE.md` with neutral, capability-based model-selection guidance.
- **`README.md`** — publication-grade. Clear inventory, install path, summary of the 15 rules and the 5-gate protocol.
- **Scripts** — bug fixes:
  - `scripts/install.sh` — corrected agent skill install path to `~/.agents/skills/master-tester-doctrine/`.
  - `scripts/verify.sh` — dependency check now reads `node_modules/.package-lock.json` / `package.json` rather than attempting `npx <lib> --version` on libs without CLIs.
  - `scripts/test-quality-check.sh` — shared-state warning now uses `printf` for `\n` expansion (was producing literal `\n` in output).
- Doctrine prose preserved verbatim; reorganized for navigation via `doctrine/INDEX.md`.

### Deprecated
- Use of `MASTER-TESTER-DOCTRINE.md` numbered lessons (#35-#48) as the operational rule source. Generalizable principles have been promoted into the references. The file remains as historical record.

---

## [1.0.0] — Initial Release

- Six doctrine documents (`MASTER-TESTER-DOCTRINE.md`, `oath-of-the-master-tester.md`, `unit-testing-rule-book.md`, `modern-ts-testers-guideline.md`, `expanded-modern-ts-testers-guideline.md`, `vanguard-of-ts-testing.md`).
- 10 Laws, AGENTS.md integration rules, sub-agent injection prompt.
- Source utilities: `factories/project.ts`, `mocks/handlers.ts`, `mocks/server.ts`, `test-utils/strict-mock.ts`, `test-utils/deferred.ts`, `test-utils/flush-promises.ts`.
- Configs: `vitest.config.ts`, `.dependency-cruiser.js`, `biome.json`.
- Scripts: `install.sh`, `verify.sh`, `ci-gate.sh`, `test-quality-check.sh`.
- Docs: `ENGINEERING-PLAN.md`, `INTEGRATION-GUIDE.md`, `PATTERNS-REFERENCE.md`.

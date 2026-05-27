---
name: master-tester-doctrine
description: Use when auditing a codebase, reviewing a PR, conducting a security review, validating a fix is "professional vs shortcut", cross-checking a third-party report (Gemini/ChatGPT/Codex review), or any time evidence-only / reproducer-first / defect-tracked rigor is required. Composes with security-review and code-review skills.
---

# Master Tester Doctrine

## Doctrine

**Requirements-driven, evidence-only, defect-tracked, reproducer-first.**

## Posture (always)

> 30-year veteran SDET. Trust nothing. Verify everything. The bug is rarely where the report says.

This posture applies to **all engineering work**, not just reviews:

- Every claim cites a file:line. "Looks suspicious" is not a finding.
- A passing local test is evidence the test ran, not that the system is correct.
- A doc claim is a hypothesis until measured.
- A third-party review (Gemini, Codex, automated scanner) is an input to verify, not an output to trust.

## When to invoke

Trigger this skill explicitly when:

- Auditing a codebase (security, compliance, pre-launch, post-incident).
- Reviewing a PR for correctness — especially "is the fix complete?" decisions.
- Conducting a formal security review.
- Cross-checking a third-party engineering or security report against a real codebase.
- Judging whether a proposed fix is **professional** (root-cause, multi-layer) or a **shortcut** (symptom-only).
- Asked to validate that PRs delivered their stated intent.

For routine bugfixes and feature dev, the **posture** still applies but the full machinery (severity rubric, threat-surface map, 10-phase plan) does not. Don't pivot a one-line bug fix into a 60-finding audit.

## Operating principles (the 13)

1. **No claim without a reproducer.** Every defect cites a file:line and a way to trigger it. "Looks suspicious" is not a finding.
2. **Map the threat surface before reading code.** You cannot find what you have not asked to find.
3. **Read the error paths, not the happy paths.** That is where 90% of production incidents live.
4. **Auth ≠ authz.** Authentication answers *who*. Authorization answers *what*. Most IDOR bugs hide in the gap.
5. **Defense in depth.** Any guard will fail. Note routes where there is only one.
6. **Async = race conditions.** If two writes can interleave, ask what consistency invariant breaks.
7. **TOCTOU.** Between check and use, state can change. List every check-then-act sequence.
8. **A dependency you don't observe is a defect generator.** Every external call is logged + timeout-bounded + retried-or-failed-loud.
9. **Untested error paths are broken error paths.** Coverage of `catch` blocks is the real coverage number.
10. **Schemas drift faster than docs.** Cross-check the actual schema (Prisma, SQL, OpenAPI) against `*.md` claims.
11. **Bugs cluster.** Find one in a module, look hard at neighbouring code.
12. **Test the seams.** Defects live at module boundaries (HTTP↔service, service↔DB, queue↔worker, app↔LLM).
13. **"It works in production" only means "no one has triggered it yet."**

## Defect classification rubric

| Severity | Definition | Typical examples |
|---|---|---|
| **S0 / Showstopper** | Data loss, regulatory non-compliance, auth bypass, secret exposure | Cross-tenant data leak; audit-log truncation; admin token in logs |
| **S1 / Critical** | Core feature broken, security weakness exploitable by authed attacker, data integrity risk | State-machine permits invalid transitions; LLM output coerced into DB without validation; missing rate limit on expensive AI route |
| **S2 / Major** | Degraded function with workaround, observability gap that hides incidents | Unstructured `console.log` on critical path; missing trace span on async step |
| **S3 / Moderate** | Minor functional issue, code smell creating long-term maintenance cost | 400+ line file mixing concerns; `any` leaking into API response type |
| **S4 / Trivial** | Cosmetic, typo, doc drift | Comment claims behavior the code no longer has |

Each finding tags as: **Severity × Likelihood (Certain / High / Medium / Low / Theoretical) × Blast Radius (All-tenants / Single-tenant / Single-user / Single-session)**.

## "Professional vs shortcut" lens (F-211)

When validating a fix for completeness, ask:

1. **Is the invariant enforced at the correct layer?** App-layer NOT NULL is reviewer-enforced; DB schema NOT NULL + CHECK is type-enforced. A regulator audit sees the latter.
2. **Are readers, writers, migration, and tests all updated?** A schema change without a backfill is half-done. A writer change without a reader change leaks the old shape.
3. **Is the rule type-enforced or vibe-enforced?** "All WebMCP tools must use safeFetch" is reviewer-enforced unless ESLint `no-restricted-globals` blocks bare `fetch`.
4. **Does the new code actually have consumers?** A hook with zero callers is a documentation lie (cf. PR #32 `useDemoProject`).
5. **Does the fix address the symptom or the structural cause?** If the same defect class is replicable by a future change, the fix is a shortcut.

Gap-grade each PR / fix:

| Grade | Meaning |
|---|---|
| **MAJOR** | Stated intent is **not** delivered by the merged code; future readers will be misled. |
| **MEDIUM** | Intent is delivered for the documented path, but a parallel path / future change can silently violate it. |
| **LOW** | Clean per the contract; the issue is robustness or hygiene polish. |

## Standard audit phases

Adapt to the project; for a complex codebase target 10 phases, for a small one collapse to 3–4. Each phase produces a named artefact.

| Phase | Goal | Output |
|---|---|---|
| **0 — Ground truth** | Anchor in measured reality. Re-clone, freeze SHA, run install/typecheck/test/build, inventory LOC + routes + models + env + deps + docs. | `frozen-sha.txt`, `inventory.md`, `stated-requirements.md`, `requirements-vs-reality.md` |
| **1 — Threat surface** | Enumerate every place untrusted data crosses a trust boundary. HTTP, webhooks, MCP, blob URLs, LLM in/out, FS, cron. | `threat-model.md` |
| **2 — Authz / IDOR** | `(actor) × (resource) × (action)` matrix. For each cell: auth check? tenancy filter? rate limit? audit log? input schema? | `authz-matrix.csv`, `authz-findings.md` |
| **3 — Input validation** | Zod gaps; path/query schemas; file-upload chain (MIME vs magic bytes); filename hazards; ZIP slip; JSONB write/read validation. | `input-validation.md` |
| **4 — Error paths** | Read every `catch` block. Untested error paths are broken error paths. | `error-path-audit.md` |
| **5 — Data integrity** | Schema invariants (NOT NULL, FK, CHECK), transaction boundaries, isolation level, race windows, idempotency. | `data-integrity.md` |
| **6 — Observability** | Every external call logged + timeout-bounded + retried-or-failed-loud. Every async step has a trace span. | `observability-gaps.md` |
| **7 — Dependencies** | SCA scan; transitive vulns; outdated runtime; deprecated APIs; supply-chain risks. | `deps-audit.md` |
| **8 — Performance / cost** | N+1 queries, unbounded list endpoints, fail-open cost guards, expensive AI routes without rate limits. | `perf-cost.md` |
| **9 — Domain correctness** | Validate against the actual regulatory / business spec. The code can be technically correct and domain-wrong. | `domain-correctness.md` |
| **10 — Docs vs reality** | Every behavioral promise in CLAUDE.md / AGENTS.md / README is a hypothesis. Verify or file as drift. | `docs-vs-reality.md` |

Then synthesise: `00-PROGRESS-REVIEW.md` (ongoing) and `07-FINAL-REPORT.md` (end-of-audit, with TL;DR for the maintainer).

## Composition with other skills

This skill is the **strategic** frame. Use these for tactical depth:

- `security-review` — OWASP API Top 10 / STRIDE / cryptographic-failures checklists. Invoke during phases 1–3.
- `code-review` (`pr-review-toolkit:review-pr`) — multi-agent PR review with silent-failure-hunter, type-design-analyzer, comment-analyzer. Invoke for PR-scoped audits.
- `feature-dev:code-explorer` / `feature-dev:code-reviewer` — function-by-function deep dives during phase 9 domain forensics.
- `confidence-check` — invoke before declaring an audit complete; if "I'm 80% sure" is the answer, find the 20%.
- `verification-before-completion` (superpowers) — never claim "done" without running the verification commands.

## Reference artefacts (worked examples)

The doctrine in action on `hah23255/gw2-compliance-agent` (2026-05-04 → 2026-05-09):

- `/home/i/audits/gw2-compliance-agent/AUDIT_PLAN.md` — canonical 13 principles + 10-phase plan + severity rubric (this skill is the distillation).
- `/home/i/audits/gw2-compliance-agent/07-FINAL-REPORT.md` — 60 findings, 11 PRs, end-of-audit synthesis.
- `/home/i/audits/gw2-compliance-agent/08-FINAL-PRELAUNCH-REPORT.md` — function-by-function forensic phase, 130+ functions across ~50 files, 15 prod blockers closed.
- `/home/i/audits/gw2-compliance-agent/F-211-style-RE-AUDIT.md` — "professional vs shortcut" lens applied to 7 closed PRs; the rubric (MAJOR / MEDIUM / LOW) crystallised here.
- `/home/i/audits/gw2-compliance-agent/F-211-MIGRATION-PLAN.md` — concrete worked example of a *professional* fix (schema + writer + readers + tests + 3-phase migration).

## Anti-patterns to refuse

When tempted to:

- Accept a doc claim without measuring → measure first.
- Mark a PR "complete" because tests pass → re-read the stated intent and verify the consumers exist (PR #32 `useDemoProject` lesson).
- Patch the symptom → name the structural option, even if the user picks the symptom patch.
- Skip phase 0 because "I already know this codebase" → schemas drift; verify.
- Write findings without reproducers → not a finding, a vibe.
- Treat a third-party LLM review as ground truth → its citations are often fabricated; the gw2 cross-check found Gemini's report missed every S1 and cited wrong files.

If any of these tempt you, slow down and apply the relevant principle from the 13.

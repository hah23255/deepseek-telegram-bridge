---
name: QA Doctrine — Master Tester + Codebase Review/Testing stack (adopted 2026-05-09, extended 2026-05-10)
description: Adopted QA operating doctrine; full machinery for audits/reviews, posture always; routes to composing skills (security-review, pr-review-toolkit, feature-dev, confidence-check, TDD, systematic-debugging, verification-before-completion, requesting/receiving-code-review)
type: feedback
originSessionId: a07bbd68-47c5-40d8-8bf4-d0c0547c441f
---
**Posture (always, every engineering task):** no shortcuts, evidence-only, verify everything, reproducer-first. Every claim cites a file:line. A passing local test is evidence the test ran, not that the system is correct. A doc claim is a hypothesis until measured. A third-party review (Gemini/Codex/scanner) is an input to verify, not an output to trust.

**Strategic frame:** invoke skill `master-tester-doctrine` (`~/.claude/skills/master-tester-doctrine/SKILL.md`) when auditing a codebase, reviewing a PR for completeness, doing a security review, cross-checking a third-party report, or judging "professional vs shortcut." It owns the severity rubric (S0–S4 × Likelihood × Blast-Radius), the F-211 gap-grade lens (MAJOR/MEDIUM/LOW), the 10-phase plan, and the 13 operating principles.

**Composing QA stack (route by scope, not by reflex):**

- **Audit phases 1–3 (threat surface, authz, input validation), or any security-sensitive change** → `security-review` skill. OWASP Top 10 checklist with grep-able patterns. Don't skip — its A01/A03/A07 search lines have caught real S1s.
- **PR-scoped review** → `/pr-review-toolkit:review-pr`. Orchestrates code-reviewer + silent-failure-hunter + type-design-analyzer + comment-analyzer + pr-test-analyzer + code-simplifier. Use this for "is this PR ready to merge?" decisions.
- **Function-by-function forensic dive (audit phase 9, hallucinated-API hunt, F-040-style extraction defects)** → `feature-dev:code-explorer` and `feature-dev:code-reviewer` agents. They trace call paths and read the error paths.
- **Pre-claim sanity check** → `confidence-check` skill. Mandatory before declaring any audit / fix / feature complete. "80% sure" → find the 20%.
- **Before any "done / fixed / passing" claim, before commit, before PR** → `superpowers:verification-before-completion`. Run the verification command, paste the output. Evidence before assertions, always.
- **Implementing any feature or bugfix** → `superpowers:test-driven-development`. Write the failing test first, then minimal code to pass. The doctrine's posture demands it.
- **Any bug, test failure, or unexpected behavior** → `superpowers:systematic-debugging` BEFORE proposing fixes. Reproducer-first lives here.
- **Completing a task, finishing a feature, before merging** → `superpowers:requesting-code-review`.
- **Receiving review feedback** → `superpowers:receiving-code-review`. Technical rigor and verification — never performative agreement, never blind implementation.

**Why:** Over 2026-05-04 → 2026-05-09 the strategic doctrine drove every gw2-compliance-agent audit (60 findings across 10 phases, 50+ PRs merged, F-211 schema-layer professional fix, F-211-style re-audit of 7 PRs). The doctrine repeatedly outperformed Gemini's reviews — Gemini's report missed every S1 and cited wrong files; the Master-Tester re-audit found the real defects. On 2026-05-10 the user asked to extend adoption to the full QA stack so the right tactical composer is reached for automatically — without re-deriving "which skill handles this scope?" each session.

**How to apply:**
- **Audits / formal reviews** → invoke `master-tester-doctrine` first, then route to the tactical composers above as the audit phase demands. Produce reproducer-cited findings; severity-tag every one.
- **Feature dev / bugfixes** → posture only + the relevant composer (TDD for new code; systematic-debugging for bugs; verification-before-completion before claiming done; requesting-code-review on hand-off). Every claim still cites a file:line.
- **PR feedback loops** → on send, `requesting-code-review`; on receive, `receiving-code-review`; for the deep dive, `/pr-review-toolkit:review-pr`.
- **Match machinery to scope.** Do NOT pivot a one-line bugfix into a 60-finding audit. Do NOT swap the doctrine for default behaviour because the task feels small. Do NOT skip composers because the strategic skill "covers it" — the composers exist because the strategic frame doesn't go deep on OWASP greps, on TDD step granularity, on verification-command discipline.

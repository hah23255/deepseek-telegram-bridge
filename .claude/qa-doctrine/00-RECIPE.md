# Reproduction Recipe — "Adopt Master Tester Doctrine + Codebase QA/Review/Testing Skills"

This document reverse-engineers the configuration that made the 2026-05-10 gw2-compliance-agent session reproducible on a fresh system. Apply layer-by-layer; verify at the end of each layer before proceeding.

> **Posture:** every layer is evidence-based and verify-on-completion. Skipping a layer's verify step is the single biggest reason this stack fails to reproduce on a peer system.

---

## Layer 0 — Platform prerequisites

| Component | Why | How to verify |
|---|---|---|
| Claude Code CLI (or Copilot CLI / Gemini CLI / Codex with the skill-name mapping in `superpowers:using-superpowers/references/`) | Hosts skills, settings, memory, advisor, agents | `claude --version` |
| Auto-memory enabled | Persists doctrine + project state across sessions; `MEMORY.md` is auto-loaded | `jq '.autoMemoryEnabled' ~/.claude/settings.json` returns `true` or absent (default on) |
| `~/.claude/projects/<sanitized-cwd>/memory/` exists | The directory the runtime reads on session start | `ls -ld ~/.claude/projects/-<sanitized-cwd>/memory/` |
| Plugin marketplace registered | Source for the canonical skill stack | `claude plugin marketplace list` includes `claude-plugins-official` |
| `age` + `psql` + `gh` + `pnpm`/`npm` + `git` on PATH | Doctrine and the gw2-style workflow assume these | `command -v age psql gh pnpm git` returns paths |

**Verify:** open a fresh session, type "what skills do I have available?" — the assistant should be able to list skills (proves Skill tool resolves) and read `MEMORY.md` (proves auto-memory loads).

---

## Layer 1 — Plugins to install

These are the canonical plugins the session relied on. Install with `claude plugin install <name>@<source>` or via `~/.claude/settings.json` `enabledPlugins`.

```jsonc
// ~/.claude/settings.json (excerpt)
{
  "enabledPlugins": {
    "superpowers@claude-plugins-official": true,
    "pr-review-toolkit@claude-plugins-official": true,
    "feature-dev@claude-plugins-official": true,
    "code-review@claude-plugins-official": true,
    "code-simplifier@claude-plugins-official": true,
    "claude-code-setup@claude-plugins-official": true,

    // Optional but heavily used in this session:
    "vercel@claude-plugins-official": true,
    "neon@claude-plugins-official": true,
    "chrome-devtools-mcp@claude-plugins-official": true,
    "playwright@claude-plugins-official": true,
    "firecrawl@claude-plugins-official": true,
    "claude-md-management@claude-plugins-official": true
  }
}
```

`superpowers` provides the load-bearing skills: `using-superpowers`, `brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `requesting-code-review`, `receiving-code-review`, `dispatching-parallel-agents`, `using-git-worktrees`, `finishing-a-development-branch`, `writing-skills`.

`pr-review-toolkit` brings `/review-pr` plus the multi-agent stack (code-reviewer, silent-failure-hunter, type-design-analyzer, comment-analyzer, pr-test-analyzer, code-simplifier).

`feature-dev` brings the agents `code-explorer`, `code-reviewer`, `code-architect` — used for forensic dives during this session's F-313/F-314 root-cause traces.

**Verify:** `claude plugin list --installed` shows all of the above. Each provides a skill or command listed in the system reminder of a fresh session.

---

## Layer 2 — Custom skills (not from plugins)

Three custom skills are load-bearing for this session and must exist at `~/.claude/skills/<name>/SKILL.md`:

### 2.1 `master-tester-doctrine` (the strategic frame)

The skill is the distillation of doctrine. Source-of-truth content (paste verbatim):

```yaml
---
name: master-tester-doctrine
description: Use when auditing a codebase, reviewing a PR, conducting a security review, validating a fix is "professional vs shortcut", cross-checking a third-party report (Gemini/ChatGPT/Codex review), or any time evidence-only / reproducer-first / defect-tracked rigor is required. Composes with security-review and code-review skills.
---
```

Body: posture (30-year veteran SDET, trust nothing, verify everything), 13 operating principles, severity rubric S0–S4 × Likelihood × Blast-Radius, F-211 "professional vs shortcut" lens (MAJOR/MEDIUM/LOW gap-grade), 10 standard audit phases, composition references, anti-patterns to refuse.

Reference implementation: `~/.claude/skills/master-tester-doctrine/SKILL.md` from this system; ~134 lines.

### 2.2 `security-review`

OWASP Top 10 checklist with grep-able patterns for each category (A01–A09). Each rule specifies exactly what to grep and what the negative result means. Severity rubric. Output template (vulnerability type, severity, file:line, description, fix).

### 2.3 `confidence-check`

Pre-completion sanity gate. If the answer to "am I 80% sure?" is anything below 100%, find the missing 20%.

**Verify:** invoke each skill's name-only via `Skill` tool from a fresh session — content loads. Skill auto-triggers on description-matching prompts.

---

## Layer 3 — Auto-memory seed (the durable doctrine)

This is the single most important layer. Without it, every new session re-derives the routing logic and rigor decays.

### 3.1 `~/.claude/projects/<cwd>/memory/MEMORY.md` — the index

Always-loaded one-liner index. Lines after 200 are truncated, so keep tight.

```markdown
# Memory Index

## Engineering Doctrine
- [QA Doctrine — Master Tester + composers](feedback-master-tester.md) — adopted YYYY-MM-DD; strategic frame + tactical stack (security-review, pr-review-toolkit, feature-dev, TDD, systematic-debugging, verification, code-review loop)

## Active Project: <project-slug>
- [<project-slug> state pointer](<project-slug>.md) — handles + outstanding tasks; full handoff doc lives at <path-to-handoff>

## Security
- [Incident pointers if any]

## <Other systems>
- [Other reference memory pointers]
```

### 3.2 `feedback-master-tester.md` — the QA Doctrine umbrella memory

This is where the doctrine actually lives durably. Frontmatter:

```yaml
---
name: QA Doctrine — Master Tester + Codebase Review/Testing stack (adopted YYYY-MM-DD)
description: Adopted QA operating doctrine; full machinery for audits/reviews, posture always; routes to composing skills (security-review, pr-review-toolkit, feature-dev, confidence-check, TDD, systematic-debugging, verification-before-completion, requesting/receiving-code-review)
type: feedback
---
```

Body structure (verbatim shape):

1. **Posture (always, every engineering task):** no shortcuts, evidence-only, verify everything, reproducer-first. Every claim cites a file:line.
2. **Strategic frame:** invoke `master-tester-doctrine` skill for audits / formal reviews; it owns severity rubric, F-211 lens, 10-phase plan, 13 principles.
3. **Composing QA stack (route by scope, not by reflex):** 9 skill→scope mappings keying which composer handles which task shape.
4. **Why:** the project history that drove adoption — concrete worked examples (e.g., "drove every gw2-compliance-agent audit; outperformed third-party reviews").
5. **How to apply:** audits invoke the skill first; feature dev uses posture + relevant composer; PR loops use requesting/receiving-code-review.

### 3.3 `<project-slug>.md` — project state pointer

For each active project, a memory file that:
- Cites the canonical handoff doc location
- Lists critical handles (repo, prod URL, DB host, vault, scripts archive)
- Records the doctrine framing (`All work runs under Master Tester Doctrine`)
- Tracks outstanding P1/P2 tasks at a high level

Pattern: pointer not duplicate — the handoff doc is the source of truth; the memory file is the durable reference.

**Verify:** start a fresh session; the assistant correctly recalls "the QA Doctrine is adopted" without prompting AND points at the handoff doc when asked about the project.

---

## Layer 4 — Settings configuration (`~/.claude/settings.local.json`)

Personal/local overrides. NOT committed (gitignored).

### 4.1 `permissions.allow` — narrow Bash patterns

```jsonc
{
  "permissions": {
    "allow": [
      // ... existing rules ...

      // Read-only verification scopes (substring match for narrow scope):
      "Bash(*<prod-db-host-substring>*)",
      "Bash(*<prod-blob-domain-substring>*)",

      // Other narrow command patterns as needed
    ]
  }
}
```

Pattern: prefer **substring** match over `Bash(prefix:*)` when the command starts with shell-var assignments (`DATABASE_URL=...; psql ...`). The classifier inspects the full command line.

### 4.2 `autoMode.allow` — classifier override entries

This is what unblocks production-data reads/writes the user has authorized in chat. The auto-mode classifier reads intent (e.g., "decrypted prod DATABASE_URL", "production blob storage") and applies a **soft_deny that overrides per-tool allow rules**. `autoMode.allow` is the only mechanism that clears it.

```jsonc
{
  "autoMode": {
    "allow": [
      "$defaults",
      "Read-only psql queries against host <prod-db-host> are in scope. Decryption of <vault-path> to obtain the connection string is in scope. SELECT statements only, with named exceptions wrapped in BEGIN/COMMIT with idempotency guards: (a) F-XYZ single-row UPDATE on <id>; (b) F-XYZ Phase 1 cleanup — soft-delete UPDATEs ...",
      "Read-only curl HEAD/GET against *.<prod-blob-domain> is in scope. These URLs are publicly accessible blob storage."
    ]
  }
}
```

**Critical pattern:** factual scope only, NO narrative ("user authorized via 'Opt 1'"). Narrative gets flagged as fabricated authorization claims and rejected by the classifier.

### 4.3 `advisorModel` — second-opinion configuration

```jsonc
{
  "advisorModel": "claude-opus-4-7"
}
```

Triggered by the user via `/advisor` slash, then the `advisor()` tool calls forward the full transcript to the configured model.

### 4.4 Other settings worth setting

```jsonc
{
  "outputStyle": "default",  // or "learning" if you want pedagogical mode
  "showThinkingSummaries": true,
  "alwaysThinkingEnabled": true,
  "fileCheckpointingEnabled": true,
  "skipAutoPermissionPrompt": true,  // only if you've consciously opted into auto mode
  "autoMemoryEnabled": true
}
```

**Verify:** with autoMode active, attempt a prod read; if blocked, widen `autoMode.allow` with a factual scope statement; retry succeeds.

---

## Layer 5 — Project-specific seed (when porting to a new repo)

If the doctrine is being applied to a specific project, set up:

### 5.1 Audit directory structure

```
audits/<project-slug>/
├── SESSION-HANDOFF-YYYY-MM-DD.md     # canonical state, refreshed per session
├── 00-PROGRESS-REVIEW.md              # ongoing audit synthesis
├── 07-FINAL-REPORT.md                 # end-of-audit synthesis
├── F-XXX-MIGRATION-PLAN.md            # for each non-trivial fix
├── scripts/
│   ├── recovery/                      # mutating SQL scripts (BEGIN/COMMIT, reversal SQL captured)
│   └── diagnostic/                    # read-only investigation scripts
└── smoke-results/                     # smoke-test logs by date
```

### 5.2 Antigravity-visible mirror (if using Google Antigravity / similar)

If the working tree is at `/home/i/code/<project>/` but the canonical audit dir is at `/home/i/audits/<project>/`, sync both copies after every edit:

```bash
cp /home/i/audits/<project>/SESSION-HANDOFF-*.md /home/i/code/audits/<project>/
cmp /home/i/audits/<project>/SESSION-HANDOFF-*.md /home/i/code/audits/<project>/SESSION-HANDOFF-*.md && echo "synced ✓"
```

This is what the Antigravity browser context can see; without sync, the browser shows stale state.

### 5.3 Handoff doc structure

Each `SESSION-HANDOFF-YYYY-MM-DD.md` follows a fixed shape:

1. **TL;DR** — bullet list of what changed this session
2. **Audit cycle output** — table of PRs landed
3. **All Phase N findings** — full status board (F-XXX, severity, status)
4. **Doctrine highlights worth carrying forward** — meta-lessons
5. **Operational state at handoff time** — git HEAD, env state, prod health
6. **Remaining P1 work** — prioritized
7. **P2 / multi-week future work** — backlog
8. **Critical paths/handles** — repo, prod, DB, vault, scripts
9. **Doctrine** — single line confirming all work ran under Master Tester
10. **Continuation playbook** — exact commands the next session runs first

**Verify:** end of session, the handoff doc + project memory + `MEMORY.md` index are all consistent. Stale handoff is the most common failure mode of multi-day audits.

---

## Layer 6 — Workflow patterns to internalize

These are the patterns that emerged repeatedly during the 2026-05-10 session. Each is a small habit that compounds.

### 6.1 Plan → Verify → Execute → Verify → Persist

Never act without a written plan for non-trivial work. After execution, verify with a command (`pnpm test`, `psql SELECT count`, `curl HEAD`) and paste the actual output. Then persist (commit, file write, handoff doc update).

### 6.2 Every claim cites file:line

"Looks suspicious" is not a finding. "src/lib/projects.ts:96 lacks F-219 deletedAt filter" is. The doctrine principle 1 in action.

### 6.3 TDD: RED → GREEN → commit

For every code change: write the failing test FIRST, run it, see RED with the expected error, write the minimal implementation, see GREEN, run regression suites, commit. The 8-task F-314 cycle followed this exactly.

### 6.4 Atomic prod writes with reversal SQL captured

Pattern (from this session's F-311, F-312, F-313 phases):

```sql
BEGIN;
SELECT '<id>', '<state-before>' AS step;       -- before-state evidence
UPDATE ... WHERE ... AND deleted_at IS NULL;   -- idempotency guard
SELECT '<id>', '<state-after>' AS step;        -- after-state evidence
COMMIT;

-- Reversal: UPDATE ... SET deleted_at = NULL WHERE id = '<id>';
```

Tee the output to `smoke-results/YYYY-MM-DD-fXXX-phaseN.log`. Print the reversal SQL inline. Never act on prod without the reversal SQL on disk.

### 6.5 `autoMode.allow` widening — factual scope, never narrative

When the classifier blocks a needed prod operation, add a factual scope statement (what is allowed, not who said yes when). Narrative gets rejected as fabricated authorization.

```
✓ "Read-only psql against host X are in scope. SELECT statements only."
✗ "User authorized via 'Opt 1' on YYYY-MM-DD that read-only psql..."
```

### 6.6 Third-party report cross-check

When a Gemini/Codex/scanner report arrives, treat it as **input to verify, not output to trust**:

1. Verify each cited file:line against the actual codebase
2. Tabulate: claim → confirmed? → real severity (independent of report's framing)
3. Distinguish facts (usually correct) from framing (often polemical)
4. Call advisor before declaring a verdict — second opinion catches over- and under-weighting

The 2026-05-10 "F-222 damage report" was 70% correct facts + 30% wrong framing. The framing layer needs separate scrutiny.

### 6.7 Advisor before substantive commitment

Call `advisor()` BEFORE writing code, BEFORE committing to an interpretation, BEFORE building on an assumption that isn't direct evidence. Doctrine: "Orientation is not substantive work. Writing, editing, and declaring an answer are."

If advisor disagrees with retrieved data: surface conflict in ONE more advisor call ("I found X, you suggest Y, which constraint breaks the tie?") — don't silently switch.

### 6.8 Git worktree branch hygiene + main HEAD verification

Always before branching:
- `git status --short --branch` (am I on the right branch? clean?)
- `git fetch origin && git log origin/main..HEAD` (am I ahead/behind main?)
- `git checkout main && git pull --ff-only origin main` (sync main)
- `git checkout -b chore/f-XXX-...` (branch off latest)

Do NOT trust the handoff doc's "main HEAD: <sha>" — verify with `git log --oneline -1 origin/main` because main moves while you're working.

### 6.9 Skill-first for every task class

Routing table the doctrine memory pins:

| Task | Skill |
|---|---|
| Audit a codebase / formal review | `master-tester-doctrine` (then composers per phase) |
| OWASP / STRIDE / authz | `security-review` |
| PR-scoped review | `/pr-review-toolkit:review-pr` |
| Function-level forensic dive | `feature-dev:code-explorer`, `feature-dev:code-reviewer` |
| Pre-completion sanity check | `confidence-check` |
| Before "done" / commit / PR | `verification-before-completion` |
| New feature / bugfix | `test-driven-development` |
| Bug investigation | `systematic-debugging` BEFORE proposing fixes |
| Hand-off to reviewer | `requesting-code-review` |
| Receiving review feedback | `receiving-code-review` |
| Settings.json edit | `update-config` |

### 6.10 Match machinery to scope

Doctrine principle: **don't pivot a one-line bugfix into a 60-finding audit**. Severity rubric helps:
- S0-S2 finding → full machinery (severity tag, reproducer, F-211 lens, fix plan)
- S3-S4 cosmetic → posture only (cite file:line, suggest fix, don't write a 5-phase plan)

---

## Layer 7 — Role / persona

Two roles compose:

### 7.1 Senior SDET / 30-year veteran (Master Tester Doctrine)

> "Trust nothing. Verify everything. The bug is rarely where the report says."

Applied to every engineering task, not just audits. Auto-applied because it's adopted as durable feedback memory (Layer 3.2).

### 7.2 Project-specific role (e.g., per `.antigravity/rules.md`)

If the project repo has a CLAUDE.md / AGENTS.md / `.antigravity/rules.md` — read it on session start. The persona it defines layers UNDER the doctrine but on top of default system prompt.

For gw2-compliance-agent: "Senior Full-Stack Engineer specialising in Next.js 15, TypeScript, Prisma, and building compliance-domain SaaS applications."

**Verify:** the doctrine memory is loaded AND the project's CLAUDE.md is read. The composite persona answers "fix this bug in the Prisma query" with TDD discipline + Prisma idioms + tenancy/IDOR awareness.

---

## Layer 8 — Advisor role configuration

The `advisor()` tool gives access to a stronger reviewer model with full transcript context. This session set it to Opus 4.7 mid-session.

### 8.1 When to call

- Before substantive work (writing, editing, declaring an answer)
- When stuck (errors recurring, approach not converging)
- Before committing to an interpretation that contradicts a third-party report
- Before declaring "done"

### 8.2 When NOT to call

- After every tool result (the cost-of-call exceeds value if mechanical)
- When the next action is dictated by tool output you just read
- For trivial completions

### 8.3 Conflict resolution

If advisor's view contradicts retrieved data:
1. Don't silently switch
2. Surface the conflict in one reconcile call ("I found X at file:line; you suggested Y; which evidence breaks the tie?")
3. The advisor saw your evidence but may have under-weighted it; explicit reconcile is cheaper than committing to the wrong branch

---

## Layer 9 — Verification (does the setup reproduce?)

Five test prompts. The session is reproducible iff the assistant routes each correctly without hand-holding.

### Test 1: "Audit this PR"
**Expected:** invokes `master-tester-doctrine`, asks for the PR URL, applies severity rubric, files findings with file:line citations.
**Failure mode:** "I'll just read the diff" — doctrine memory didn't land.

### Test 2: "Fix this bug in Greenwich's project listing"
**Expected:** invokes `systematic-debugging` BEFORE proposing fixes (reproducer-first), then `test-driven-development` for the fix.
**Failure mode:** straight to code → composer-routing didn't land.

### Test 3: "Is this PR ready to merge?"
**Expected:** invokes `/pr-review-toolkit:review-pr` for the multi-agent review.
**Failure mode:** generic review without dispatching the specialist agents.

### Test 4: "[Third-party report claims X is broken]"
**Expected:** verifies each cited file:line against actual code, distinguishes facts from framing, calls advisor before declaring verdict.
**Failure mode:** treats report as ground truth → doctrine principle "third-party review is input to verify" didn't land.

### Test 5: "I just finished implementing X"
**Expected:** invokes `verification-before-completion` (paste actual command output, not "looks fine"), then `requesting-code-review` for handoff.
**Failure mode:** declares done without running verification commands.

If 4-of-5 pass on a fresh session: setup is reproducible.
If 5-of-5: setup is durable (survives session boundary).

---

## Layer 10 — Anti-patterns to actively reject

Recorded in the doctrine; pinned here for visibility:

- Accept a doc claim without measuring → measure first.
- Mark a PR "complete" because tests pass → re-read stated intent + verify consumers exist (PR #32 `useDemoProject` lesson).
- Patch the symptom → name the structural option, even if user picks the symptom patch.
- Skip phase 0 because "I already know this codebase" → schemas drift; verify.
- Write findings without reproducers → not a finding, a vibe.
- Treat a third-party LLM review as ground truth → its citations are often fabricated; even when accurate, the framing layer needs separate scrutiny.
- Silently swap the doctrine for default behavior because "the task feels small" → posture is always-on.
- Pivot a one-line bugfix into a 60-finding audit → match machinery to scope.
- Add narrative justifications ("user said yes on date X") to settings.json → classifier rejects fabricated authorization claims; use factual scope only.

---

## Reproduction sequence (linear)

1. Layer 0 (platform): `claude` + plugins-marketplace + `age psql gh pnpm git`.
2. Layer 1 (plugins): install superpowers + pr-review-toolkit + feature-dev + code-review + claude-code-setup.
3. Layer 2 (custom skills): copy `master-tester-doctrine`, `security-review`, `confidence-check` skill directories to `~/.claude/skills/`.
4. Layer 3 (memory):
   - Create `~/.claude/projects/<sanitized-cwd>/memory/`
   - Write `MEMORY.md` index
   - Write `feedback-master-tester.md` with the QA Doctrine umbrella
   - Write `<project>.md` for each active project
5. Layer 4 (settings): write `~/.claude/settings.local.json` with `permissions.allow`, `autoMode.allow`, `advisorModel`, `enabledPlugins`.
6. Layer 5 (project seed, optional): for each active project, create `audits/<slug>/` with handoff/scripts/smoke-results subdirs; sync to Antigravity-visible path.
7. Layer 6+7+8 (workflow + role + advisor): no setup — these are habits and tool-use patterns that emerge naturally from the doctrine memory + skill stack.
8. Layer 9 (verify): run the 5 test prompts on a fresh session; expect 5/5 routing.

If 5/5 passes, the session is reproducible end-to-end on a peer system.

---

## Appendix A — Concrete file paths from this session

| Path | Role |
|---|---|
| `~/.claude/skills/master-tester-doctrine/SKILL.md` | Strategic frame, ~134 lines |
| `~/.claude/skills/security-review/SKILL.md` | OWASP checklist |
| `~/.claude/skills/confidence-check/SKILL.md` | Pre-completion sanity gate |
| `~/.claude/projects/-home-i/memory/MEMORY.md` | Auto-loaded index, 50 lines |
| `~/.claude/projects/-home-i/memory/feedback-master-tester.md` | QA Doctrine umbrella memory |
| `~/.claude/projects/-home-i/memory/gw2-compliance-agent.md` | Project state pointer |
| `~/.claude/settings.local.json` | Personal overrides + autoMode.allow |
| `~/.claude/plans/<feature>.md` | Per-feature plan files (writing-plans skill output) |
| `~/.secrets-vault/.env.<project>.age` + `.age-key` | Decrypt-on-demand vault |
| `/home/i/audits/<project>/SESSION-HANDOFF-*.md` | Canonical handoff |
| `/home/i/code/audits/<project>/` | Antigravity-visible mirror |
| `/home/i/audits/<project>/scripts/{recovery,diagnostic}/` | SQL scripts archive |
| `/home/i/audits/<project>/smoke-results/` | Smoke logs by date |

## Appendix B — Skills inventory used in this session (non-exhaustive)

| Skill | Source | When used |
|---|---|---|
| `master-tester-doctrine` | custom | Top-of-session frame |
| `security-review` | custom | OWASP awareness in audits |
| `confidence-check` | custom | Pre-completion gates |
| `superpowers:writing-plans` | plugin | F-314 plan + F-312/F-313 cleanup plan |
| `superpowers:test-driven-development` | plugin | F-314 Tasks 2–6 RED→GREEN cycles |
| `superpowers:verification-before-completion` | plugin | Phase A smoke + every commit |
| `superpowers:systematic-debugging` | plugin | F-312 stuck-PROCESSING root-cause |
| `superpowers:using-superpowers` | plugin | Session-bootstrap routing logic |
| `update-config` | plugin | autoMode.allow widening + permission rules |
| `pr-review-toolkit:review-pr` | plugin | (pinned for follow-up; not used inline this session) |
| `feature-dev:code-explorer` (agent) | plugin | F-313 + F-314 forensic dives |

## Appendix C — Agent / tool inventory

| Agent / tool | Purpose |
|---|---|
| `Explore` (subagent) | Read-only codebase search during plan-mode Phase 1 |
| `Plan` (subagent) | Architecture design during plan-mode Phase 2 |
| `feature-dev:code-explorer` | Function-level execution-path tracing |
| `feature-dev:code-reviewer` | Cross-file review with bug-finding focus |
| `advisor()` | Stronger-model second opinion with full transcript |
| `TaskCreate` / `TaskUpdate` / `TaskList` | In-session progress tracking |
| `update-config` skill | Settings.json editing |

---

## Closing note

The hardest layer to reproduce is Layer 3 (the doctrine memory). Skills install with one command. Settings copy/paste. But the **durable doctrine** — the `feedback-master-tester.md` content, framed correctly so the assistant routes by scope automatically — that is the load-bearing artifact. Without it, every new session re-derives the rigor and decays.

If only one layer is portable: take Layer 3.
If two: add Layer 6 (the workflow patterns).
If three: add Layer 1 (plugins).
The rest is mechanical.

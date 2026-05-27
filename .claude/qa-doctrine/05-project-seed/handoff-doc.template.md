# Session Handoff — YYYY-MM-DD (<phase or milestone>)

This is the day-N handoff continuing from `SESSION-HANDOFF-<prior-date>.md`. Read that one first for project-wide handles; this doc captures only what changed across <prior-date> evening into <current-date> morning during <work description>.

## TL;DR

- **<bullet about phase / cycle complete>**
- **<bullet about defect classes closed for good>**
- **<bullet about production hygiene improvements>**
- **<production health summary>**: HTTP 200, healthy. main HEAD: `<sha>`.

## Audit cycle output (N PRs merged in this cycle)

| PR | Branch | Effect | Audit ID |
|---|---|---|---|
| #N | `branch-name` | <one-line effect> | F-XXX (severity) |

## All findings (full status board)

| ID | Title | Status |
|---|---|---|
| F-XXX | <description> | ✅ closed (PR #N) |
| F-XYZ | <description> | 🟡 partial — Phase X done; Phase Y pending |
| F-ABC | <description> | 🔴 open — standalone PR after current cycle |

## Doctrine highlights worth carrying forward

- **<Lesson 1>**: <one-paragraph context + the generalization>.
- **<Lesson 2>**: <…>.
- **<Lesson 3>**: <…>.

## Operational state at handoff time (YYYY-MM-DDTHH:MM UTC)

```
prod URL                  → HTTP 200 (deployment dpl_…, target=Production, status=Ready)
main HEAD                 → <sha> (PR #N merge — <description>)
prod env (key var)        → set, encrypted
prod env (auth provider)  → sk_live_* + pk_live_* (untouched)
preview env (auth)        → sk_test_* + pk_test_* from dev instance <handle>
test token mintable       → `pnpm exec playwright test --project=<setup>`
DB migrations             → N entries (most recent: <name>)
CI on main                → green
preview deploys           → load
runtime warnings          → gone
```

## Remaining P1 work (in priority order)

### 1. <Title>

<Context paragraph>

User-facing impact: <description>. Logged as task #N.

**Decision pending**: <option A> vs <option B>.

Diagnostic available: `<path-to-diagnostic-script>`.

### 2. <Browser-side smoke / operator action>

<Steps the operator does in browser>

### 3. <Credential rotation — DEFERRED>

Per user direction (YYYY-MM-DD): <why deferred>. When ready, the runbook is:
1. <step>
2. <step>

## P2 / multi-week future work (todo list)

| # | Title | Notes |
|---|---|---|
| #N | <description> | <context> |

## Critical paths/handles (mostly unchanged from <prior-date>)

For codebase, prod, DB, vault, scripts archive — see `SESSION-HANDOFF-<prior-date>.md`. Updates from this session:

- **Worktree primary path**: `<path>` (Y GB, persistent). Legacy volatile copy at `<old-path>` may exist but will not survive reboot.
- **Memory pointer**: `~/.claude/projects/.../<slug>.md`.
- **<New service / handle>**: <description + provisioning details>.

## Known noise / unrelated CI failures

<Anything that's NOT a project regression but appears as CI noise — e.g., third-party rate limits, advisory checks. Document so future sessions don't waste cycles diagnosing.>

## Operator-tooling caveats (learned YYYY-MM-DD)

Worth carrying forward to future <tool-name> work on this project:

- **<Caveat 1>** — <description + workaround>.
- **<Caveat 2>** — <description + workaround>.

## Doctrine

All work this cycle ran under Master Tester Doctrine (`~/.claude/skills/master-tester-doctrine/SKILL.md`) plus the Codebase Review skills (pr-review-toolkit + feature-dev). <Lesson highlight from this cycle.>

## Continuation playbook for the next session

```bash
# 1. Anchor in measured reality (always)
cd <worktree-path>
git fetch origin
git log --oneline -5
gh pr list --state all --limit 5

# 2. Confirm prod is still healthy
curl -s -o /dev/null -w "%{http_code}\n" <prod-url>

# 3. Read the up-to-date handoff
cat <path-to-this-doc>

# 4. (Optional) verify <feature> still <works>
#    <command>

# 5. Pick a P1 item or move to backlog
```

## Doctrine self-note (for the auditor's benefit, not just this project)

<A generally-applicable lesson from this cycle that applies beyond the immediate project.>

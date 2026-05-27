---
name: <project-slug> — handles + state pointer
description: Production deployment + DB + scripts + handoff doc for <product-name>. Pointer to the durable handoff document.
type: project
---
<one-line product description>. Owner: <owner-name> (`<owner-email>`). <production-status / phase>.

## Always-current handoff

The single source of truth for current state, open tasks, and continuation (most recent first):

  `<path-to-most-recent-SESSION-HANDOFF.md>` ← <phase or milestone> (start here)
  `<path-to-prior-handoff>` ← prior day; project-wide handles + earlier audit context

Re-read the most recent handoff at the start of any session resuming this work.

## Critical handles (cached here for fast recall — verify against handoff doc if work is several days old)

- **Repo**: <https://github.com/owner/repo>
- **Worktree**: `<path-to-worktree>`
- **Production**: <https://prod-url>
- **Vercel project**: `prj_…` in team `team_…`
- **Production DB**: <provider> at `<host>` / `<db-name>` / `<user>`
- **Vault**: `<path-to-vault>` decrypted via `age -d -i <key-path>`
- **Auth provider**: <Clerk/Auth0/etc> — admin user IDs are `<id1>`, `<id2>`, `<id3>`

## Scripts archive

- `<audit-dir>/scripts/recovery/` — N mutating scripts (each idempotent, host-allowlisted, BEGIN/COMMIT, reversal SQL printed)
- `<audit-dir>/scripts/diagnostic/` — N read-only investigation scripts

## Doctrine

All work on this codebase ran/runs under the Master Tester Doctrine (`~/.claude/skills/master-tester-doctrine/SKILL.md`). Adopted YYYY-MM-DD. Trust nothing, verify everything; schemas drift faster than docs (principle 10).

## Outstanding tasks (as of YYYY-MM-DD)

P1 (do before launch):
- <task description>
- ~~F-XYZ~~ — closed YYYY-MM-DD. <one-line outcome>

P2 (multi-week or feature work):
- <task description>

Trivia / cleanup:
- <task description>

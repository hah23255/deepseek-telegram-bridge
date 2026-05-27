# QA Doctrine Deployment Pack — INDEX

A self-contained pack that reproduces the "Master Tester Doctrine + Codebase QA/Review/Testing Skills" stack on a peer system. Apply layer-by-layer; verify after each layer.

## Reading order

| # | File | Purpose |
|---|---|---|
| 0 | [`README.md`](./README.md) | One-page quick-start; copy-paste deployment commands |
| 1 | [`00-RECIPE.md`](./00-RECIPE.md) | The full 10-layer reverse-engineered recipe (524 lines, the canonical reference) |
| 2 | [`01-PLUGINS.md`](./01-PLUGINS.md) | Plugins to install + exact commands |
| 3 | [`02-skills/`](./02-skills/) | The 3 custom skills (verbatim copies; drop into `~/.claude/skills/`) |
| 4 | [`03-memory-seed/`](./03-memory-seed/) | Auto-memory seed: `MEMORY.md` index + `feedback-master-tester.md` (the durable doctrine — the load-bearing artifact) |
| 5 | [`04-settings/`](./04-settings/) | `settings.local.json` template + permissions/autoMode guide |
| 6 | [`05-project-seed/`](./05-project-seed/) | Per-project audit directory convention + handoff doc template |
| 7 | [`06-WORKFLOW-PATTERNS.md`](./06-WORKFLOW-PATTERNS.md) | The 10 workflow patterns that emerged from the gw2 session |
| 8 | [`07-ROLE-PERSONA.md`](./07-ROLE-PERSONA.md) | Master Tester role + project-specific layering |
| 9 | [`08-ADVISOR.md`](./08-ADVISOR.md) | Advisor model configuration + when-to-call patterns |
| 10 | [`09-VERIFICATION.md`](./09-VERIFICATION.md) | The 5-prompt test that proves setup is reproducible |
| 11 | [`10-ANTI-PATTERNS.md`](./10-ANTI-PATTERNS.md) | What to actively reject — failure modes seen in practice |
| 12 | [`DOCTRINE/`](./DOCTRINE/) | Doctrine extracts: 13 principles, severity rubric, F-211 lens, 10-phase audit plan (standalone reference) |
| 13 | [`EXAMPLES/`](./EXAMPLES/) | Real worked examples from the 2026-05-10 gw2 session (F-311 → F-314 + the F-222 third-party-report cross-check) |
| 14 | [`scripts/`](./scripts/) | `install.sh` (one-shot) + `seed-memory.sh` (memory bootstrap) |

## Mandatory layers (cannot skip)

- **Layer 3** (memory seed) — the load-bearing artifact. Without it every new session re-derives rigor and decays.
- **Layer 1** (plugins) — provides the composing skills referenced by the doctrine memory.
- **Layer 2** (custom skills) — the master-tester-doctrine skill is what audit/review tasks invoke.

## Optional layers (can be added later)

- **Layer 4** settings beyond defaults (autoMode.allow, advisor model)
- **Layer 5** per-project audit directory (only if you have an active project)
- **Layers 6–10** workflow patterns / persona / advisor / verification / anti-patterns — habit-formation, not config

## Verification

After deploying, run [`09-VERIFICATION.md`](./09-VERIFICATION.md)'s 5-prompt test on a fresh session. 5/5 = durable; 4/5 = reproducible (good enough); below 4/5 = some layer didn't land.

## What's NOT in this pack

- Plugin source code (those are external; install via `claude plugin install`).
- Project-specific data (the `gw2-compliance-agent.md` memory is project-specific; only template included).
- Live credentials (vault decrypt files, API keys — those stay on the source system).
- Browser-side state (Vercel preview cookies, Clerk testing tokens — these are environment-specific).

## Provenance

Built 2026-05-10 from the gw2-compliance-agent session that closed F-311, F-312-Phase-0, F-313, F-314 and filed F-315-F-320 + the F-222 third-party-report cross-check. Recipe + skills + doctrine memory are verbatim from the working system.

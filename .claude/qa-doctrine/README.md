# QA Doctrine Deployment Pack — Quick Start

One-page deployment guide. For the full detail see [`00-RECIPE.md`](./00-RECIPE.md).

## Prerequisites

- Claude Code CLI (or Copilot/Gemini/Codex with skill-name mapping)
- Plugin marketplace registered: `claude plugin marketplace list` includes `claude-plugins-official`
- On PATH: `git`, `gh`, `pnpm`/`npm`, plus optional `age` and `psql` for the worked examples

## Deployment (5 commands)

```bash
# 1. Unzip the pack
cd ~ && unzip qa-doctrine-deployment-pack.zip
cd qa-doctrine-deployment-pack

# 2. One-shot installer (copies skills, seeds memory, installs plugins)
bash scripts/install.sh

# 3. Open Claude Code, copy settings template
cat 04-settings/settings.local.json.template
# Then merge into ~/.claude/settings.local.json (do NOT replace; merge)

# 4. Set advisor model
claude --update-config 'advisorModel=claude-opus-4-7'   # or via /config UI

# 5. Verify
# Open a fresh session and run the 5-prompt test from 09-VERIFICATION.md
```

## What each layer of the pack provides

| Layer | What you get | Time to apply |
|---|---|---|
| **Plugins** (Layer 1) | superpowers, pr-review-toolkit, feature-dev, code-review, plus optional vercel/neon/etc | 2 min |
| **Custom skills** (Layer 2) | master-tester-doctrine, security-review, confidence-check | 1 min (cp) |
| **Memory seed** (Layer 3) | Durable doctrine memory — auto-loaded every session | 1 min (cp + edit cwd path) |
| **Settings** (Layer 4) | autoMode.allow patterns, permissions narrowing, advisor config | 5 min (merge into existing) |
| **Project seed** (Layer 5) | `audits/<slug>/` + handoff template + scripts pattern | 10 min per project |
| **Workflow patterns** (Layer 6+) | Habit-formation guides — internalize over time | Ongoing |

## Mandatory minimum

If you only deploy three layers, deploy these:

1. **Layer 3** memory seed (the load-bearing artifact)
2. **Layer 1** plugins (provides composing skills)
3. **Layer 2** custom skills (master-tester-doctrine especially)

Everything else is mechanical and can be added later.

## How to know it's working

Open a fresh Claude Code session in any directory. Type:

> "Audit this PR: <some PR URL>"

Expected: assistant invokes `master-tester-doctrine` skill, applies severity rubric, asks for code-access, produces findings with file:line citations.

If instead the assistant says "I'll just read the diff and tell you what I see" — Layer 3 (memory seed) didn't land. Re-run `scripts/install.sh` and check `~/.claude/projects/<sanitized-cwd>/memory/MEMORY.md` exists.

## Pack contents at a glance

```
qa-doctrine-deployment-pack/
├── INDEX.md                    ← start here for full TOC
├── README.md                   ← this file
├── 00-RECIPE.md                ← canonical 10-layer recipe
├── 01-PLUGINS.md               ← which plugins, install commands
├── 02-skills/                  ← 3 SKILL.md files (verbatim)
├── 03-memory-seed/             ← MEMORY.md + feedback-master-tester.md
├── 04-settings/                ← settings.local.json template
├── 05-project-seed/            ← audit dir convention + handoff template
├── 06-WORKFLOW-PATTERNS.md     ← 10 patterns
├── 07-ROLE-PERSONA.md
├── 08-ADVISOR.md
├── 09-VERIFICATION.md          ← 5-prompt test
├── 10-ANTI-PATTERNS.md
├── DOCTRINE/                   ← extracted reference
├── EXAMPLES/                   ← worked examples (F-311–F-314, F-222 cross-check)
└── scripts/                    ← install.sh + seed-memory.sh
```

## Support / next steps after deployment

- Run the 5-prompt verification (09)
- Read the worked examples in EXAMPLES/ to understand how the doctrine plays out in practice
- Adopt the workflow patterns in 06 over your next 3-5 sessions
- The doctrine memory updates itself naturally as you use it (auto-memory writes new feedback entries when you correct or confirm approaches)

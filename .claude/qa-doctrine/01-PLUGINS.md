# Layer 1 — Plugins Manifest

The plugins below provide the composing skills + agents the doctrine memory routes to.

## Mandatory plugins

| Plugin | Source | Provides |
|---|---|---|
| `superpowers` | `claude-plugins-official` | `using-superpowers`, `brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `requesting-code-review`, `receiving-code-review`, `dispatching-parallel-agents`, `using-git-worktrees`, `finishing-a-development-branch`, `writing-skills` |
| `pr-review-toolkit` | `claude-plugins-official` | `/review-pr` command + agents: code-reviewer, silent-failure-hunter, type-design-analyzer, comment-analyzer, pr-test-analyzer, code-simplifier |
| `feature-dev` | `claude-plugins-official` | Agents: code-explorer, code-reviewer, code-architect (used for forensic dives) |
| `code-review` | `claude-plugins-official` | `/code-review` command (lighter alternative to pr-review-toolkit) |
| `claude-code-setup` | `claude-plugins-official` | `claude-automation-recommender` skill (suggests automations for a project) |
| `claude-md-management` | `claude-plugins-official` | `revise-claude-md` slash + `claude-md-improver` agent for project memory hygiene |

## Recommended optional plugins

Add as your stack demands:

| Plugin | When to install |
|---|---|
| `vercel` | Vercel-deployed Next.js / similar projects |
| `neon` | Neon Postgres-backed projects |
| `chrome-devtools-mcp` | Frontend perf + a11y audits |
| `playwright` | E2e test automation |
| `firecrawl` | Documentation scraping / external research |
| `auth0` | Auth0-integrated apps |
| `commit-commands` | Standardized commit/PR workflow |
| `hookify` | Behavior-prevention via hooks |
| `plugin-dev` | Building your own plugins |

## Install command

Single command per plugin:

```bash
claude plugin install superpowers@claude-plugins-official
claude plugin install pr-review-toolkit@claude-plugins-official
claude plugin install feature-dev@claude-plugins-official
claude plugin install code-review@claude-plugins-official
claude plugin install claude-code-setup@claude-plugins-official
claude plugin install claude-md-management@claude-plugins-official
```

Or batch via `~/.claude/settings.json`:

```jsonc
{
  "enabledPlugins": {
    "superpowers@claude-plugins-official": true,
    "pr-review-toolkit@claude-plugins-official": true,
    "feature-dev@claude-plugins-official": true,
    "code-review@claude-plugins-official": true,
    "claude-code-setup@claude-plugins-official": true,
    "claude-md-management@claude-plugins-official": true,
    "vercel@claude-plugins-official": true,
    "neon@claude-plugins-official": true,
    "chrome-devtools-mcp@claude-plugins-official": true,
    "playwright@claude-plugins-official": true,
    "firecrawl@claude-plugins-official": true
  }
}
```

## Verification

After install:

```bash
claude plugin list --installed
```

Open a fresh session. The system reminder should list the new skills. If `using-superpowers` isn't listed, plugins didn't load — restart Claude Code.

## Plugin sources

Default marketplace: `claude-plugins-official`. To register additional marketplaces, see `~/.claude/settings.json` `extraKnownMarketplaces`.

## Composition reference

The doctrine memory (Layer 3) routes by task scope to specific composers. The full table:

| Task scope | Composer | From plugin |
|---|---|---|
| Audit a codebase | `master-tester-doctrine` (custom Layer 2) | — |
| OWASP / security review | `security-review` (custom Layer 2) | — |
| PR-scoped multi-agent review | `/pr-review-toolkit:review-pr` | `pr-review-toolkit` |
| Function-level forensic dive | `feature-dev:code-explorer`, `feature-dev:code-reviewer` agents | `feature-dev` |
| Pre-completion sanity check | `confidence-check` (custom Layer 2) | — |
| Before "done"/commit/PR | `superpowers:verification-before-completion` | `superpowers` |
| TDD cycle | `superpowers:test-driven-development` | `superpowers` |
| Bug investigation | `superpowers:systematic-debugging` | `superpowers` |
| Hand-off to reviewer | `superpowers:requesting-code-review` | `superpowers` |
| Receiving review | `superpowers:receiving-code-review` | `superpowers` |
| Plan a feature/audit | `superpowers:writing-plans` | `superpowers` |
| Execute a plan | `superpowers:executing-plans` or `superpowers:subagent-driven-development` | `superpowers` |
| Settings.json edits | `update-config` | (built-in) |

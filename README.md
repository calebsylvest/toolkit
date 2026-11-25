# toolkit

A small [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugins/create-marketplace) for running a team of file-based agents: one coordinator agent hands tasks to project agents through plain folders, and project agents check their own work with read-only reviewers.

Each plugin is small and does one job. Install only the ones you need.

## What's inside

| Plugin | What it gives you |
|---|---|
| [`agent-onboarding`](plugins/agent-onboarding/) | Everything an agent needs to take tasks from a coordinator: a charter section for `CLAUDE.md` (inbox read oldest first, the outbox report format, filing to `done/`, command rules that never trigger a permission prompt, and how to reach the coordinator directly), a generic `/start-work` session skill, and a `/setup-handoff` skill that creates the `.agent/` inbox and outbox. |
| [`reviewers`](plugins/reviewers/) | Two read-only subagents. `fact-checker` checks every claim a diff adds against primary sources. `editorial-reviewer` checks new prose against your style guide. Both have a tool allowlist, run only a few named Bash commands, and return PASS, FAIL or ESCALATE. |

```
toolkit/
├── .claude-plugin/marketplace.json      ← the marketplace catalog
├── plugins/
│   ├── agent-onboarding/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/
│   │   │   ├── start-work/SKILL.md      ← /agent-onboarding:start-work
│   │   │   └── setup-handoff/SKILL.md   ← /agent-onboarding:setup-handoff
│   │   └── templates/
│   │       ├── charter-section.md       ← paste into CLAUDE.md
│   │       ├── task.md                  ← a coordinator's task file
│   │       └── report.md                ← an agent's outbox report
│   └── reviewers/
│       ├── .claude-plugin/plugin.json
│       └── agents/
│           ├── fact-checker.md          ← reviewers:fact-checker
│           └── editorial-reviewer.md    ← reviewers:editorial-reviewer
├── scripts/check_marketplace.py         ← structure check (stdlib Python)
├── CANDIDATES.md                        ← ideas not yet built
├── CONTRIBUTING.md
└── LICENSE                              ← MIT
```

## The pattern

```
coordinator agent                         project agent (one per repo)
  writes  <repo>/.agent/inbox/2026-01-15-fix-links.md
                                          /start-work reads the inbox, oldest first
                                          does the work on a branch, opens a PR
                                          writes <repo>/.agent/outbox/2026-01-15-fix-links.md
                                          moves the task to .agent/inbox/done/
  reads   <repo>/.agent/outbox/ ...
```

`.agent/` is gitignored and lives only in the repo's main checkout. A task is never approval: it can't loosen the repo's own rules, and anything that needs the human goes under "Needs <owner>" in the report. For urgent messages, an orchestrator such as Orca can carry them directly (`orca orchestration send …`); without one, the outbox is enough.

## Install

### In a Claude Code session

```
/plugin marketplace add calebsylvest/toolkit
/plugin install agent-onboarding@toolkit
/plugin install reviewers@toolkit
/reload-plugins
```

### From the shell

```bash
claude plugin marketplace add calebsylvest/toolkit
claude plugin install agent-onboarding@toolkit --scope project
claude plugin install reviewers@toolkit --scope project
```

`--scope` is `user` (default: every project on this machine), `project` (recorded in the repo's `.claude/settings.json`, shared with collaborators) or `local` (this repo, just you).

### For a whole project, in `.claude/settings.json`

Commit this so everyone who opens the repo is offered the marketplace and the plugins:

```json
{
  "extraKnownMarketplaces": {
    "toolkit": {
      "source": { "source": "github", "repo": "calebsylvest/toolkit" }
    }
  },
  "enabledPlugins": {
    "agent-onboarding@toolkit": true,
    "reviewers@toolkit": true
  }
}
```

Working from a local clone instead (for example while developing a plugin):

```json
{
  "extraKnownMarketplaces": {
    "toolkit": {
      "source": { "source": "directory", "path": "/absolute/path/to/toolkit" }
    }
  }
}
```

Notes:

- Project-level `extraKnownMarketplaces` takes effect after you trust the folder. `enabledPlugins` turns a plugin on but doesn't install it; each person runs `/plugin install <plugin>@toolkit` (or accepts the prompt) once.
- Update with `/plugin marketplace update toolkit`.

## Use

**Onboard an agent.** In the repo whose agent will take tasks, run:

```
/agent-onboarding:setup-handoff <agent-name> <owner> <coordinator> [setup-bot]
```

It creates `.agent/inbox/done/`, `.agent/outbox/` and `.agent/tmp/`, gitignores `.agent/`, and adds the charter sections to `CLAUDE.md` with your names filled in, on a branch for you to review. Then start each session with `/agent-onboarding:start-work` (or a repo-local `/start-work`, below).

**Review a change.** Ask for it in plain words ("run fact-checker on this branch against main") or by name: `@agent-reviewers:fact-checker`, `@agent-reviewers:editorial-reviewer`. Tell your agent in `CLAUDE.md` when to dispatch each, for example:

```markdown
| Agent | Dispatch when the diff |
|---|---|
| `reviewers:fact-checker` | adds or changes a name, number, price, spec, date or factual claim |
| `reviewers:editorial-reviewer` | adds or rewrites prose |
```

## Customize

The plugins are generic on purpose. Project details stay in the project.

- **Placeholders.** Templates use `<agent-name>`, `<owner>`, `<coordinator>`, `<setup-bot>`, `<repo>` and similar. `setup-handoff` fills them in; you can also do it by hand from `plugins/agent-onboarding/templates/`.
- **Your own `/start-work`.** If a repo needs extra steps (a build, a status script, a weekly report), copy `plugins/agent-onboarding/skills/start-work/SKILL.md` to the repo's `.claude/skills/start-work/SKILL.md` and edit it. A project skill is invoked as plain `/start-work`; the plugin's stays available as `/agent-onboarding:start-work`.
- **Reviewers.** Each agent reads your `CLAUDE.md` for its settings: where content lives, the style guide, a benchmark page, an optional check script, and what to ESCALATE. The comment block at the top of each agent file lists them. For deeper changes, copy the agent into `.claude/agents/` under a different name and edit it there.
- **Tighten permissions.** Plugin agents can't carry their own permission mode, so the reviewers' Bash limits are instructions. To enforce them, allow only the listed commands in your project's `.claude/settings.json` permissions.

## Add a skill or plugin

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: put it in the smallest plugin it fits (or a new `plugins/<name>/`), keep project-specific details out, add it to `.claude-plugin/marketplace.json`, and run:

```bash
claude plugin validate .
python3 scripts/check_marketplace.py
```

## How things get in

1. **Propose.** Anyone can propose a skill, agent or template: open an issue saying what it does, when it triggers, and where it would be used. [CANDIDATES.md](CANDIDATES.md) lists ideas already on the table.
2. **Build.** A proposal that's general enough gets built here, small and focused, with placeholders instead of project details, and tested in a real project.
3. **Approve.** The maintainer approves promotion into the marketplace and merges.
4. **Wire in.** Projects opt in through their own settings, as above.

## License

[MIT](LICENSE).

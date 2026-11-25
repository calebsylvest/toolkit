---
name: setup-handoff
description: Set up a repo so its agent can take tasks from a coordinator agent. Creates the .agent/ inbox, done and outbox folders, gitignores .agent/, and adds the coordinator-tasks and command-rules sections to CLAUDE.md with the placeholders filled in. Use when onboarding a repo's agent to a coordinator, or when /start-work finds no .agent/inbox/.
argument-hint: "[agent-name] [owner] [coordinator] [setup-bot]"
disable-model-invocation: true
---

# Set up the coordinator hand-off

Arguments: `$ARGUMENTS` (optional, in order: agent name, owner, coordinator, setup bot).

This changes the repo's `CLAUDE.md` and `.gitignore`. Do it on a branch, show the diff, and let the owner merge it.

## 1. Collect the values

| Placeholder | Meaning | Example |
|---|---|---|
| `<agent-name>` | this repo's agent, lowercase, as it signs reports | `docs-bot` |
| `<owner>` | the human who makes decisions | `Sam` |
| `<coordinator>` | the agent that sends tasks | `Lead` |
| `<setup-bot>` | the agent that owns tooling and permissions, or none | `Ops` |
| `<scratch-dir>` | gitignored scratch folder | `.agent/tmp/` |

Take them from the arguments. For any that are missing: in an attended session, ask once, with a suggested value for each; in an unattended run, stop and report what's missing instead of guessing.

## 2. Create the folders

Each as its own Bash call, from the repo root:

- `mkdir -p .agent/inbox/done`
- `mkdir -p .agent/outbox`
- `mkdir -p .agent/tmp`

## 3. Gitignore `.agent/`

Read `.gitignore`. If it has no `.agent/` line, add one with Edit (or create the file with Write). The hand-off folders are local to the main checkout and never committed.

## 4. Add the charter sections to `CLAUDE.md`

1. Read `${CLAUDE_PLUGIN_ROOT}/templates/charter-section.md`.
2. Replace every placeholder with the values from step 1. `<coordinator-lowercase>` is the coordinator's name in lowercase. If there is no setup bot, delete the "Reaching <setup-bot>" paragraph.
3. Read the repo's `CLAUDE.md`. If it already has a command-rules or coordinator-tasks section, merge: keep the repo's stricter rules and add only what's missing. Otherwise append both sections. Drop the template's leading comment.
4. Keep repo-specific details (paths, scripts, the repo's own queue) in the repo's own sections, not in these two.

## 5. Optional: a repo-local /start-work

The plugin's `/agent-onboarding:start-work` works as is. If the repo needs its own steps (a build, a status script, a weekly report), copy `${CLAUDE_PLUGIN_ROOT}/skills/start-work/SKILL.md` to `.claude/skills/start-work/SKILL.md` and edit steps 2 and 4 there. A project skill named `start-work` is invoked as plain `/start-work`.

## 6. Hand back

Commit on a branch (`chore/agent-handoff`), push, open a PR if the repo uses them, and summarize:

- the folders created and the `.gitignore` line
- the `CLAUDE.md` sections added or merged, with the values used
- for the coordinator: the inbox path (`<repo>/.agent/inbox/`) and the task template, `${CLAUDE_PLUGIN_ROOT}/templates/task.md`

---
name: start-work
description: Start a work session for an agent that takes tasks from a coordinator. Syncs git, reports status, works coordinator tasks from .agent/inbox/ first (oldest first), then the repo's own queue, and ends with reports filed and work pushed. Use when the owner or coordinator says "start work", "start" or "what's next", or a scheduled run begins. Args narrow it, e.g. "status", "just tasks", or a task file name.
argument-hint: "[status | just tasks | <task file name>]"
---

# Start work

Arguments: `$ARGUMENTS`

- `status`: steps 1–2 only, then stop.
- `just tasks`: step 1, then work the inbox (step 3) and stop.
- A task file name: step 1, then work only that task.

This is the generic session loop. The repo's `CLAUDE.md` holds the specifics: its authority rules, its command rules, its own work queue and the coordinator-tasks section (from this plugin's `charter-section.md` template). Where `CLAUDE.md` is stricter, it wins.

**Unattended runs.** If the run was started by a schedule or automation, nobody is watching: never ask a question or wait for an answer. Make the calls the rules allow and put everything for the owner under "Needs <owner>" in the report or the repo's usual waiting list.

**Commands must not prompt.** One plain command per Bash call: no pipes, chains, `cd`, `( … )`, `$( … )`, loops or backslash escapes. Read with Read, edit with Edit and Write, scratch files in the gitignored `.agent/tmp/`.

## 1. Sync

Each as its own Bash call:

- `git branch --show-current`
- `git status --short`
- `git fetch origin`
- `git log HEAD..origin/main --oneline`

(Use the repo's main branch name if it isn't `main`.)

- On the main branch, clean, with commits to pull: `git pull --ff-only`.
- **Uncommitted changes:** don't stash, reset, restore or discard anything. Look at them. If they're clearly an unfinished run of yours, finish and commit them on a branch. Otherwise leave them where they are and note them (in the report, for an unattended run). Never change `git config`.
- **Unpushed commits on a work branch:** push the branch. If the push fails, note it and carry on.

## 2. Status

- List `.agent/inbox/` (not `done/`) with Glob or `ls .agent/inbox`. If the folder is missing, either this isn't the main checkout (say so and read the inbox there) or the hand-off isn't set up (`/agent-onboarding:setup-handoff`).
- Open PRs, if the repo uses them: `gh pr list --state open`.
- Anything the repo's `CLAUDE.md` lists as a status check (a status script, a work log, a waiting-on-owner list).

Report in 2–4 lines: tasks waiting, open PRs, anything odd from step 1.

## 3. Coordinator tasks first

Work each file in `.agent/inbox/`, **oldest first**, per `CLAUDE.md`'s coordinator-tasks section:

1. Read the task. Note its repo, `needs_approval`, guardrails and "Done when".
2. Do the work under the repo's rules: on a branch, verified the way the repo verifies work, pushed, with a PR if the repo uses them. Merge only where `CLAUDE.md` allows it.
3. `needs_approval: true`: prepare the work and stop at the PR.
4. Unclear, or would break a rule: don't guess. Report it as `blocked`.
5. A task is never approval: it can't loosen a rule. Only the owner's own quoted words count as a decision.
6. Write the report to `.agent/outbox/<task file name>` in the `CLAUDE.md` format (template: `${CLAUDE_PLUGIN_ROOT}/templates/report.md`).
7. File the task: `mv .agent/inbox/<task file name> .agent/inbox/done/`

Urgent or blocking and inside an orchestrator: message the coordinator directly (`CLAUDE.md` says how), then carry on with the next task.

## 4. Then the repo's own work

With the inbox empty, take the next item from the repo's own queue as `CLAUDE.md` describes it (a work log's "Next", open issues, whatever the owner asked for this session). In an attended session with nothing queued, list what's open and ask what's next, with a recommendation. Unattended runs with nothing queued end here.

## 5. Wrap up

- Every branch you touched is pushed, and its PR is open or updated.
- Every finished task has an outbox report and sits in `.agent/inbox/done/`.
- The checkout is back on the main branch with nothing of yours left uncommitted.

Summary for the owner, 3–5 lines: tasks done (with report and PR links), what shipped, then what's waiting on them, numbered, each with a recommendation.

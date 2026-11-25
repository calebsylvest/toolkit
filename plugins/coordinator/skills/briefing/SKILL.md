---
name: briefing
description: One-screen briefing for the owner, decisions first. Rolls up every project agent's .agent/ inbox, done and outbox since the last briefing, flags stalled tasks and threads whose status can't be told, reads the orchestrator's open items and waiting agents if there is one (Orca), and formats the decision queue. Read-only. Use when the coordinator is asked for a briefing, a status, "what needs me" or "what happened", or at the start of its session.
argument-hint: "[path to coordinator.json]"
---

# Briefing

Arguments: `$ARGUMENTS` (optional: the path to the config file).

You are the coordinator. Produce one screen for `<owner>`: **the decisions they need to make first**, then what happened since the last briefing, then where things stand.

**Read-only.** Don't take actions, change permissions, write tasks, message agents, or open, close or edit items. The only file this skill writes is its state file (step 6). If something needs doing, say so in the briefing; the coordinator does it afterwards, under its own rules.

**Commands must not prompt.** One plain command per Bash call: no pipes, chains, `cd`, `( … )`, `$( … )`, loops or backslash escapes.

## 1. Find the config

Use the path from the arguments; otherwise look for `coordinator.json` at the coordinator repo's root, then `.claude/coordinator.json`. No config: stop and say so, pointing to `${CLAUDE_PLUGIN_ROOT}/templates/coordinator.example.json` and the plugin README.

The config names `<owner>`, the agents and their repos, the bots (if any), the stall threshold and the deadline dots. Read it with Read.

## 2. Scan the agent repos

Run, as one Bash call:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scan_agents.py --config <config path>
```

It prints JSON and changes nothing. For each agent:

- `pending`: tasks in `.agent/inbox/` (not `done/`), with age in hours and `stalled: true` when older than the threshold with no report.
- `filed_since`: tasks moved to `inbox/done/` since the last briefing.
- `reports_since`: reports in `outbox/` or `outbox/done/` written since the last briefing, with status, the "Needs <owner>" text and any "Knowledge flags".
- `unclear`: anything whose status can't be told (a task filed with no report, a report with no frontmatter or an unknown status, a task with a report that was never filed, a repo with no `.agent/inbox/`).
- `since`, `first_run`: the window. On the first run it looks back 7 days; say so.

If the script fails, fall back to Glob on each repo's `.agent/inbox/*.md`, `.agent/inbox/done/*.md`, `.agent/outbox/*.md` and `.agent/outbox/done/*.md`, and Read the reports. Say the fallback was used.

## 3. Orchestrator state (optional: Orca)

Skip this step if the config has no `orchestrator`, or if `orca --version` fails. Then say "Orchestrator: not checked" in the briefing and carry on: everything else works without it.

With Orca, each as its own Bash call:

- For each bot in `orchestrator.bots`: `orca bot item list --bot <name> --status needs-you --json`. These items **are the decision queue** (step 4). Also note each bot's `waiting` items from `orca bot item list --bot <name> --status waiting --json`: what they wait on is in `wait.text`.
- Agents that need input: `orca agent list --state waiting --json` and `orca agent list --state blocked --json`.
- Optional, for the "where things stand" part: `orca worktree ps --since 1d`.

Commands change between Orca versions. If one fails, run its `--help` once (`orca bot item --help`, `orca agent list --help`) and use the current equivalent; if there's none, note it and carry on.

## 4. Work out states, stalls and decisions

**Task states.** Give every task and thread exactly one:

| State | When |
|---|---|
| **working** | Pending with no report yet, or an Orca agent in `working` on it. |
| **waiting** | Report says `needs-approval` (or another `needs-…`), or the agent is `waiting` or `blocked` in Orca, or a bot item is `waiting`. Say on what. |
| **done** | Report says `done` and the task is filed. |
| **error** | Report says `blocked` (or `failed`), or the agent errored. |

**Stalls.** A pending task past the stall threshold with no report is **stalled**. List each with its age and the agent's repo.

**Unclear threads.** Flag every thread whose status you can't tell: everything in the script's `unclear` lists, an Orca agent or item you can't tie to a task, and a report whose words contradict its status. Don't guess a state for them.

**Decisions.** Build the queue per `${CLAUDE_PLUGIN_ROOT}/templates/decision-queue.md`:

- With Orca: the open `needs-you` items. Recompute each dot from its due date today; don't trust a dot already in the title.
- Without Orca: the "Needs <owner>" sections of reports since the last briefing that are still open.
- With Orca, a "Needs <owner>" request in a report that has **no** matching item goes under "Not yet queued", so the coordinator can add it after the briefing.
- Only items that truly need `<owner>`: money, signatures, legal, publications, taste, accounts and keys. Anything else that reached the queue goes under "Could be handled without <owner>", with one line on who could take it.
- At most 5 in **Decide now**, ordered by deadline (overdue first, then soonest; undated last). The rest go in per-project lanes.

**Knowledge flags.** Count the "Knowledge flags" in reports since the last briefing, per agent. The coordinator batches them to the knowledge curator agent after the briefing; the briefing only lists them.

## 5. Write the briefing

One screen. Decisions first. Plain words, no filler. Use the dots from the config (`dot_style: "emoji"` or `"words"`).

```
# Briefing · <date> · since <last briefing, or "last 7 days (first run)">

## Decide now (<n>)
1. <dot> <Project> · <what's needed> · due <date>
   <one line of context>. **Question:** <question>?
   Options: <a> / <b>. **Recommend:** <answer>, because <reason>.
…(at most 5)

## Other decisions, by project
- **<Project>:** <dot> <what's needed> · due <date>; …

## Since <last briefing>
- **<agent>:** <n> done (<short names>), <n> waiting, <n> error. Notable: <one line>.

## Where things stand
| Agent | Working | Waiting | Done | Error | Stalled |
|---|---|---|---|---|---|

## Needs a look
- **Stalled:** <agent> · <task> · <age>h, no report
- **Unclear:** <agent> · <thread> · <why the status can't be told>
- **Not yet queued:** <agent> · <request> (from <report>)
- **Could be handled without <owner>:** <item> → <who>
- **Knowledge flags:** <n> from <agents>, for the curator

Orchestrator: <checked (Orca) | not checked>.
```

Leave out an empty section, except "Decide now": if it's empty, write "Nothing needs you right now."

When relaying an approval or a decision `<owner>` already gave, quote their words exactly, with the date. Never paraphrase an approval.

## 6. Remember this briefing

After the briefing is shown, record its time:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scan_agents.py --config <config path> --mark-briefed
```

This writes `{"last_briefing": "<time>"}` to the state file named by the config's `state_file` (default `coordinator.state.json`), **in the same folder as the config**. It is the only write. Keep that file out of git.

If the briefing was only a preview (the owner said "don't mark it" or the run was a test), skip this step.

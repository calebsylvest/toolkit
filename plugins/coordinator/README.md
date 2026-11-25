# coordinator

For the coordinator agent: the one that sends tasks to project agents (through `agent-onboarding`'s `.agent/` inbox and outbox) and keeps the owner informed.

| Piece | Use |
|---|---|
| `skills/briefing` | `/coordinator:briefing [config path]`: one screen for the owner, decisions first. Then what happened since the last briefing and where things stand, with each task marked working, waiting, done or error, stalled tasks flagged, and every thread whose status can't be told listed. Read-only. |
| `scripts/scan_agents.py` | What `/briefing` runs to read every agent repo's `.agent/` folders. Standard-library Python; prints JSON; changes nothing in the agent repos. |
| `templates/decision-queue.md` | The decision queue: what belongs in it, the item format (title, dot, context, question, options, recommendation), the 5-item "Decide now" cap, relaying approvals word for word, and the weekly cleanup. |
| `templates/coordinator.example.json` | An example config with placeholders. |

## Sources

1. **Agent repos.** Each repo's `.agent/inbox/` (pending), `.agent/inbox/done/` and `.agent/outbox/` (and `outbox/done/`, if the coordinator files read reports there), since the last briefing.
2. **Orchestrator (optional).** With Orca: each configured bot's items set to **Needs you** (`orca bot item list --bot <name> --status needs-you`), which are the decision queue, plus agents waiting for input (`orca agent list --state waiting`, `--state blocked`). Leave `orchestrator` out of the config and the briefing works from the agent repos alone.

## Config

The real config lives in the **coordinator's own repo** (it names your agents and repos, so keep it private). `/briefing` looks for `coordinator.json` at that repo's root, then `.claude/coordinator.json`, or takes a path as its argument. Start from [`templates/coordinator.example.json`](templates/coordinator.example.json):

| Field | Meaning | Default |
|---|---|---|
| `owner` | the human who decides | required |
| `coordinator` | the coordinator agent's name | required |
| `agents[]` | one per project agent: `name`, `repo` (path; `~` is expanded), `bot` (its orchestrator bot, or `null`), optional `stall_hours` | required |
| `orchestrator` | `{ "type": "orca", "bots": [ … ] }`: the bots whose items to read. Omit for no orchestrator. | none |
| `stall_hours` | a pending task with no report after this many hours is stalled | `36` |
| `deadline_days` | dot thresholds in days: `red` (today or overdue), `orange`, `yellow`; anything later is white | `0`, `3`, `7` |
| `dot_style` | `"emoji"` (🔴 🟠 🟡 ⚪) or `"words"` (`[red]` …) | `"emoji"` |
| `decide_now_max` | the cap on "Decide now" | `5` |
| `state_file` | where the last-briefing time is kept, relative to the config | `coordinator.state.json` |

**Why 36 hours.** Agents that run once a day pick up a task on their next run. A task that lands just after a run legitimately waits almost 24 hours, so a 24-hour threshold flags healthy tasks. 36 hours is one full daily cycle plus slack: it flags a task that missed a run. Raise it per agent (`stall_hours`) for agents that only run when the owner opens them.

**State.** The last-briefing time is a one-line JSON file **next to the config** (`coordinator.state.json` by default). It's the only thing `/briefing` writes. Add it to the coordinator repo's `.gitignore`.

## Agents' side

Project agents only need the decision format: `agent-onboarding`'s `templates/report.md` asks for it under "Needs <owner>". The coordinator turns those into queue items.

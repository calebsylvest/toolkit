# agent-onboarding

Onboard a repo's agent to a coordinator agent that sends it tasks through files.

| Piece | Use |
|---|---|
| `skills/setup-handoff` | `/agent-onboarding:setup-handoff <agent-name> <owner> <coordinator> [setup-bot]`: creates `.agent/inbox/done/`, `.agent/outbox/`, `.agent/tmp/`, gitignores `.agent/`, and adds the charter sections to `CLAUDE.md`, on a branch. Runs only when you call it. |
| `skills/start-work` | `/agent-onboarding:start-work [status \| just tasks \| <task file>]`: sync, status, coordinator tasks oldest first, then the repo's own queue, then wrap-up with reports filed. |
| `templates/charter-section.md` | The two `CLAUDE.md` sections: command rules that never trigger a permission prompt (including no backslash escapes), and coordinator tasks (inbox, outbox report format, filing to `done/`, messaging the coordinator or a setup bot directly). |
| `templates/task.md` | What a coordinator writes to `.agent/inbox/YYYY-MM-DD-<slug>.md`. |
| `templates/report.md` | What the agent writes to `.agent/outbox/<task file name>`. |

Placeholders: `<agent-name>`, `<owner>`, `<coordinator>`, `<coordinator-lowercase>`, `<setup-bot>`, `<scratch-dir>`, `<repo>`.

To give a repo its own `/start-work`, copy `skills/start-work/SKILL.md` to the repo's `.claude/skills/start-work/SKILL.md` and edit it.

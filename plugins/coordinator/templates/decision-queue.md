# Decision queue

The decision queue is the short list of things only the owner can decide. The coordinator keeps it so the owner is never the bottleneck and never has to dig.

## Where it lives

**In the orchestrator's items, not in a file.** With Orca, each decision is a bot item with status `needs-you`, on the bot that owns the thread (usually the coordinator's). `/coordinator:briefing` reads them and formats the queue; it never creates, edits or closes them.

Without an orchestrator, the queue is the open "Needs <owner>" sections of the agents' reports, and the coordinator carries them forward in its own notes.

## What belongs in it

Only items that truly need the owner:

- **Money:** spending, prices, payments, subscriptions
- **Signatures:** contracts, agreements, anything signed in the owner's name
- **Legal:** terms, privacy, disclosures, licences, claims with legal exposure
- **Publications:** anything public for the first time, or sent to people outside
- **Taste:** brand, design direction, voice, what to build next
- **Accounts and keys:** new accounts, API keys, access, permissions, settings

Everything else is decided by the coordinator or the project agent under their written authority. If it's in the queue and doesn't fit a kind above, it doesn't belong there.

## Item format

**Title:** `<dot> <Project> · <what's needed> · due <date>`

- `<what's needed>` is a short verb phrase: "approve the launch post", "pick a hosting plan".
- `due <YYYY-MM-DD>`, or `due whenever`.

**Dot,** from the due date on the day of the briefing:

| Dot | Word | Due |
|---|---|---|
| 🔴 | red | today or overdue |
| 🟠 | orange | within 3 days |
| 🟡 | yellow | within 7 days |
| ⚪ | white | later, or whenever |

If emoji render badly where the owner reads, set `dot_style: "words"` in the config and write `[red]`, `[orange]`, `[yellow]`, `[white]` instead. The thresholds are in the config too (`deadline_days`).

Agents write the title without the dot; the coordinator adds it and recomputes it at every briefing.

**Body,** in this order:

```markdown
**Kind:** money | signature | legal | publication | taste | account or key
**Context:** what's going on, in two or three lines, with links.
**Question:** one question, ending in "?"
**Options:**
1. <option>: what happens
2. <option>: what happens
**Recommend:** <option>, because <reason>.
```

One decision per item. With Orca, put the context in the comment, the question in `--ask` and each option in `--option`, with `--recommended <n>`:

```
orca bot item set <id> --status needs-you --comment "<context>" --ask "<question>?" --option "<a>" --option "<b>" --recommended 1
```

## The queue on screen

- **Decide now:** at most 5 items, ordered by deadline (overdue first, then soonest, undated last).
- **Other decisions:** everything else, in one lane per project.

## Relaying approvals

When the owner answers, relay their words **exactly**, in quotes, with the date: `"yes to all four" (<owner>, YYYY-MM-DD)`. A paraphrase isn't an approval. A project agent acts only on the owner's quoted words, never on the coordinator's summary of them.

## Weekly cleanup

Once a week, the coordinator (not `/briefing`) tidies the queue. It may close only:

- **done:** the decision was made and acted on (`orca bot item done <id>`)
- **outdated:** the question no longer applies (`orca bot item cancel <id> --reason "outdated: <why>"`)
- **duplicate:** another item asks the same thing (`orca bot item cancel <id> --reason "duplicate of #<n>"`)

It **never** closes an open decision, even an old one. An old open decision gets its dot recomputed and stays; if it's stale, ask the owner whether it still matters.

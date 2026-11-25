---
from: <agent-name>
to: <coordinator-lowercase>
task: <task file name>
status: done | blocked | needs-approval
completed: YYYY-MM-DD
---

## Summary
What was done, or why it stopped, in a few lines.

## Links
Branches, PRs, files changed.

## Needs <owner>
Only what truly needs <owner>: money, signatures, legal, publications, taste, accounts and keys. Everything else, decide under your rules. "None" if nothing. One block per decision:

### <Project> · <what's needed> · due <YYYY-MM-DD or whenever>
**Kind:** money | signature | legal | publication | taste | account or key
**Context:** what's going on, in two or three lines, with links.
**Question:** one question, ending in "?"
**Options:**
1. <option>: what happens
2. <option>: what happens
**Recommend:** <option>, because <reason>.

<coordinator> adds the deadline dot and puts it in <owner>'s decision queue.

## Knowledge flags
Shared knowledge (docs, references, a knowledge base, another agent's notes) that was missing, wrong or stale while you worked. Flag it here; never edit shared knowledge yourself. <coordinator> batches flags to the knowledge curator agent. "None" if nothing.

- **What:** the missing, wrong or stale knowledge, and which of the three it was
- **Where you looked:** file, page or source, with the path or link
- **What you were trying to do:** the step that needed it
- **Suggested fix** (optional): what it should say, with the source you checked

---
from: <coordinator-lowercase>
to: <agent-name>
created: YYYY-MM-DD
repo: <repo>
needs_approval: false
---

<!--
  Example task file. The coordinator writes one of these to
  .agent/inbox/YYYY-MM-DD-<short-slug>.md in the agent's main checkout.
  The date prefix sorts tasks oldest first.
-->

# <Short imperative title>

## Task
What to do, in a few lines.

## Context
Why it matters, links, and any decision from <owner>, quoted in their own words:

> "<owner's words>" (<owner>, YYYY-MM-DD)

## Guardrails
What not to touch, and anything that needs <owner> before it happens.

## Done when
The check that says it's finished (a PR open, a report written, a page live).

## Report
What the outbox report should include beyond the standard sections.

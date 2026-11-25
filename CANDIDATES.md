# Candidates

Ideas for what to build next. None of these is built yet; each needs a proposal, a build and the maintainer's approval (see [How things get in](README.md#how-things-get-in)). "Fits" says which kind of project or agent would use it.

| Candidate | Would be | Fits | Why build it |
|---|---|---|---|
| **Agent status briefing** | skill for the coordinator | coordinator agents | One command rolls up every project agent's inbox, done and outbox, flags stalled tasks, and leads with what needs the human. The natural pair to `agent-onboarding`. |
| **Decision queue** | skill or template for the coordinator | coordinator agents | Caps and orders the "Needs <owner>" items from every report (at most a handful at once, by deadline, each with a recommendation) so the human isn't the bottleneck. |
| **Work order (task) template** | template in `agent-onboarding` | coordinator agents | Extends `templates/task.md` with explicit guardrails and checkpoints, so unattended runs take fewer wrong turns. Small change, ready to build. |
| **Agent governance block** | template in `agent-onboarding` | every agent | A standard "who decides what" section: written delegations, a Never list, separation of powers, and a settings check. Makes authority rules uniform across agents. |
| **Session handoff harness** | skill | any multi-session project | Scaffolds a pass/fail requirements file, a progress log, a smoke-test script and a startup checklist, so each new session orients in seconds. |
| **Verified multi-phase audit** | skill (`/audit <target>`) | code and content repos | Map the territory, find issues in isolation, have a fresh agent try to disprove each, report only what survives. Reusable for code review, link checks or fact-checking. |
| **Adversarial bug hunt** | three subagents (finder, skeptic, referee) | code repos | Opposed incentives cancel out sycophantic false positives. Fits next to `reviewers`. |
| **Verify skill and commit gate** | skill plus hook | code repos | A repo-local `verify` step and a gate that stamps commits with evidence, so the human reviews evidence instead of every diff. |
| **Self-correcting loop** | skill plus Stop hook | any repeated job with a check | Act, check, correct, stop: a Stop hook that won't let the agent call itself done until a check passes, capped at a few rounds, with a log. |
| **Compound learnings capture** | skill | every agent | Turns each correction into a short written rule the next run reads. Check first whether an existing plugin already covers it before building. |
| **Skill library audit** | skill | every agent | Periodically finds the costly, unused, outdated or untested skills and agents, and proposes trims for approval. |
| **Third-party skill review** | skill | anyone installing outside skills | Vets a skill from a registry before install: what it reads, writes and runs. Skills are supply-chain inputs. |
| **Design system review** | skill | front-end and design repos | Checks agent-built UI against a written design system after each screen and turns corrections into rules and checks. |
| **Web typesetting checklist** | skill or reference | site repos | A checklist for setting long-form reading text on the web, applied when generating or reviewing styles. |

Not proposed here: ideas that are services offerings or tied to one project's workflow. Those belong in the project that would use them.

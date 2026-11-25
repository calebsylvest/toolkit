---
name: review-skill
description: Vet a third-party Claude Code skill, agent or plugin before installing it, by dispatching the read-only reviewers:skill-reviewer agent on its source at a pinned commit, then saving the report where you choose. Use when someone wants to install, add or try a skill or plugin from outside the project, or asks whether one is safe.
argument-hint: "<source url> [commit] [output path]"
disable-model-invocation: true
---

# Review a third-party skill

Arguments: `$ARGUMENTS`: the source (a git URL plus the path inside it, or a GitHub tree URL), optionally the commit to pin, optionally where to save the report.

**Nothing gets installed here.** This skill reviews; installing is a separate decision for the owner, after reading the report.

1. **Collect the inputs.**
   - Source and path. Missing: in an attended session, ask; in an unattended run, stop and report what's missing.
   - Commit: a full SHA if the caller has one. Without one, the reviewer pins the default branch head and records it.
   - Output path: the caller's choice. None given: show the report in the session and don't write a file.
   - Scratch folder: the repo's gitignored scratch folder (usually `.agent/tmp/`).
2. **Dispatch** `reviewers:skill-reviewer` with the source, path, commit and scratch folder. Don't summarize the skill for it; it reads the files itself.
3. **Save** the report it returns, unchanged, to the output path with Write (if one was given).
4. **Hand back** the verdict line, the access class, the trigger breadth and the top findings, in 3–5 lines, with the report's path. If the verdict is INSTALL WITH CHANGES, list the changes. Install only if the owner says so after this.
5. **Clean-up** is the caller's: the clone is in `<scratch-dir>skill-review/`, without a checked-out working tree. Delete it when done.

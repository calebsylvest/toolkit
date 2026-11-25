# reviewers

Three read-only subagents. They judge; the main session acts. The diff reviewers return **PASS**, **FAIL** (with the fixes) or **ESCALATE** (only for matters the owner must decide); the skill reviewer returns **INSTALL**, **INSTALL WITH CHANGES** or **REJECT**.

| Agent | Tools | Checks |
|---|---|---|
| `reviewers:fact-checker` | Read, Grep, Glob, Bash (git diff/show and one check script only), WebFetch, WebSearch | Every name, number, price, spec, date, quote and factual sentence the diff adds or changes, against a primary source. Mislinks fail. Unreadable new facts fail. |
| `reviewers:editorial-reviewer` | Read, Grep, Glob, Bash (git diff/show and one length script only) | Voice, honesty, structure, house rules, on-page SEO and lengths, against your style guide and a benchmark page. |
| `reviewers:skill-reviewer` | Read, Grep, Glob, WebFetch, Bash (`git clone --no-checkout`, `git log`, `git show` into a scratch folder only) | A third-party skill, agent or plugin before install, at a pinned commit: access class (read-and-draft / reads external workspaces / writes external systems), trigger breadth, and every script read for credential, cookie or key access, network calls and shell execution. Never installs or runs it. |

Dispatch the diff reviewers with the diff base (usually `main`) and the issue or task: "run reviewers:fact-checker on this branch against main for #12".

## Vetting a skill before install

```
/reviewers:review-skill <source url> [commit] [output path]
```

`<source url>` is a git URL plus the path inside it, or a GitHub tree URL to the skill's folder. Give a full commit SHA to review exactly what you'll install; without one, the reviewer pins the default branch head and records it. The report goes to the output path you choose, or only to the session if you give none. The skill runs only when called (`disable-model-invocation: true`).

The clone is made with `--no-checkout` and read through `git show`, so nothing in the reviewed repo (its `CLAUDE.md`, `.claude/` settings or hooks) is ever on disk as a working tree to load. Delete `<scratch-dir>skill-review/` when done.

## Configure in your project's CLAUDE.md

The agents read `CLAUDE.md` to find:

| Setting | fact-checker | editorial-reviewer |
|---|---|---|
| where content lives (`<content-paths>`) | ✓ | ✓ |
| style guide (`<style-guide>`) and a benchmark page (`<benchmark>`) | | ✓ |
| rules for adding or removing items (`<rules-doc>`) | ✓ | |
| a check script (`<check-command>`, `<length-command>`) | ✓ | ✓ |
| what to ESCALATE (`<escalate-topics>`) | ✓ | ✓ |

For example:

```markdown
## Reviewers
- Content: `content/articles/`, `data/products/`
- Style guide: `docs/style.md`; benchmark: `content/articles/best-example.md`
- fact-checker check: `python3 scripts/check_facts.py`
- editorial-reviewer lengths: `python3 scripts/check_lengths.py <file>…`
- ESCALATE: claims about competitors, safety or health claims, new categories
```

The Bash limits are instructions; plugin agents can't set their own permission mode. To enforce them, allow only those commands in `.claude/settings.json`.

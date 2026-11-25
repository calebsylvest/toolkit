# reviewers

Two read-only subagents. They judge; the main session acts. Each returns **PASS**, **FAIL** (with the fixes) or **ESCALATE** (only for matters the owner must decide).

| Agent | Tools | Checks |
|---|---|---|
| `reviewers:fact-checker` | Read, Grep, Glob, Bash (git diff/show and one check script only), WebFetch, WebSearch | Every name, number, price, spec, date, quote and factual sentence the diff adds or changes, against a primary source. Mislinks fail. Unreadable new facts fail. |
| `reviewers:editorial-reviewer` | Read, Grep, Glob, Bash (git diff/show and one length script only) | Voice, honesty, structure, house rules, on-page SEO and lengths, against your style guide and a benchmark page. |

Dispatch with the diff base (usually `main`) and the issue or task: "run reviewers:fact-checker on this branch against main for #12".

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

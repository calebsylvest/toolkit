# Contributing

## Ground rules

- **Small and focused.** One plugin, one job. If a new skill doesn't share a purpose with an existing plugin, make a new plugin.
- **Generic.** No project names, people, paths, URLs, ids or secrets. Use placeholders (`<project>`, `<owner>`, `<agent-name>`, `~/Code/<repo>`) and say in a comment what each one means. Project details belong in that project's `CLAUDE.md`.
- **Commands that never prompt.** Skills and agents follow the command rules in `plugins/agent-onboarding/templates/charter-section.md`: one plain command per Bash call, no pipes, chains, `cd`, subshells, loops or backslash escapes.
- **Reviewers stay read-only.** An agent that judges work gets a `tools:` allowlist and a short list of the Bash commands it may run.
- **Shared files live in the plugin that owns them** (`plugins/<name>/templates/`), referenced from skills as `${CLAUDE_PLUGIN_ROOT}/templates/<file>`.

## Layout

Only `plugin.json` goes inside a plugin's `.claude-plugin/`. Everything else sits at the plugin root:

```
plugins/<plugin-name>/
├── .claude-plugin/plugin.json     ← name (kebab-case), version, description
├── skills/<skill-name>/SKILL.md   ← invoked as /<plugin-name>:<skill-name>
├── agents/<agent-name>.md         ← subagent <plugin-name>:<agent-name>
├── hooks/hooks.json               ← optional
└── templates/                     ← optional files the skills read
```

## Add a skill to an existing plugin

1. Create `plugins/<plugin>/skills/<skill-name>/SKILL.md` with `name` (same as the folder) and `description` frontmatter. The description says what it does and when to use it.
2. Bump `version` in the plugin's `plugin.json`.
3. Mention it in the plugin's README and the table in the top README.

## Add a plugin

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json`:

   ```json
   {
     "name": "<plugin-name>",
     "version": "0.1.0",
     "description": "<one sentence>",
     "license": "MIT"
   }
   ```

   Names are kebab-case and can't start with `claude-` or `anthropic-`.
2. Add its skills, agents and templates.
3. Add an entry to `.claude-plugin/marketplace.json`:

   ```json
   { "name": "<plugin-name>", "source": "./plugins/<plugin-name>", "description": "<one sentence>" }
   ```

4. Add a `README.md` in the plugin folder and a row in the top README.

## Test

```bash
claude plugin validate .
python3 scripts/check_marketplace.py
```

`claude plugin validate` checks the manifests. `check_marketplace.py` checks that every source folder exists, names match, every skill and agent has frontmatter, and every `${CLAUDE_PLUGIN_ROOT}/…` path exists.

Then try it for real without touching your own setup:

```
/plugin marketplace add /absolute/path/to/your/clone
/plugin install <plugin-name>@toolkit --scope local
```

in a throwaway project, run the skill or agent once, and remove it with `/plugin uninstall <plugin-name>@toolkit`.

## Review

Open an issue first for anything new, then a pull request. The maintainer reviews and approves what goes into the marketplace.

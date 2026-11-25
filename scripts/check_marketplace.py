#!/usr/bin/env python3
"""Structural check for this plugin marketplace (standard library only).

Run from the repo root:  python3 scripts/check_marketplace.py

It complements `claude plugin validate .`, which checks the manifests' schema.
This script checks what that command doesn't: every plugin source folder
exists, each plugin.json name matches its marketplace entry, every skill and
agent has name and description frontmatter, and every
${CLAUDE_PLUGIN_ROOT}/... path a skill or agent mentions exists.
Exit code 0 = pass, 1 = problems found.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
RESERVED_PREFIXES = ("claude-", "anthropic-", "anthropics-", "cc-plugin-")
RESERVED_NAMES = {"claude", "anthropic", "anthropics", "claude-code", "claude-mods"}
PLUGIN_ROOT_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")

errors = []


def err(msg):
    errors.append(msg)


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        err(f"missing: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        err(f"bad JSON in {path.relative_to(ROOT)}: {exc}")
    return None


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def check_name(kind, name):
    if not name or not NAME_RE.match(name):
        err(f"{kind} name {name!r} is not kebab-case")
    elif name in RESERVED_NAMES or name.startswith(RESERVED_PREFIXES):
        err(f"{kind} name {name!r} is reserved")


def check_markdown(plugin_dir, path, kind):
    rel = path.relative_to(ROOT)
    fm = frontmatter(path)
    if fm is None:
        err(f"{rel}: no YAML frontmatter")
        return
    for field in ("name", "description"):
        if not fm.get(field):
            err(f"{rel}: frontmatter has no {field}")
    if kind == "skill" and fm.get("name") and fm["name"] != path.parent.name:
        err(f"{rel}: name {fm['name']!r} differs from its folder {path.parent.name!r}")
    if kind == "agent" and fm.get("name") and fm["name"] != path.stem:
        err(f"{rel}: name {fm['name']!r} differs from its file name {path.stem!r}")
    for ref in PLUGIN_ROOT_REF.findall(path.read_text(encoding="utf-8")):
        if not (plugin_dir / ref.rstrip(".")).exists():
            err(f"{rel}: ${{CLAUDE_PLUGIN_ROOT}}/{ref} does not exist")


def main():
    market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if market is None:
        return 1
    check_name("marketplace", market.get("name"))
    if not (market.get("owner") or {}).get("name"):
        err("marketplace.json: owner.name is required")
    plugins = market.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        err("marketplace.json: plugins must be a non-empty list")
        plugins = []

    seen = set()
    for entry in plugins:
        name = entry.get("name")
        check_name("plugin", name)
        if name in seen:
            err(f"plugin {name!r} is listed twice")
        seen.add(name)
        source = entry.get("source")
        if not isinstance(source, str) or not source.startswith("./") or ".." in source:
            err(f"plugin {name!r}: source must be a ./relative path without '..'")
            continue
        plugin_dir = ROOT / source
        if not plugin_dir.is_dir():
            err(f"plugin {name!r}: source folder {source} does not exist")
            continue
        manifest = load_json(plugin_dir / ".claude-plugin" / "plugin.json")
        if manifest is not None and manifest.get("name") != name:
            err(f"plugin {name!r}: plugin.json name is {manifest.get('name')!r}")
        if not entry.get("description") and not (manifest or {}).get("description"):
            err(f"plugin {name!r}: no description")
        for skill in sorted(plugin_dir.glob("skills/*/SKILL.md")):
            check_markdown(plugin_dir, skill, "skill")
        for agent in sorted(plugin_dir.glob("agents/*.md")):
            check_markdown(plugin_dir, agent, "agent")
        for stray in sorted((plugin_dir / ".claude-plugin").iterdir()):
            if stray.name != "plugin.json":
                err(f"{stray.relative_to(ROOT)}: only plugin.json belongs in .claude-plugin/")
        print(f"ok  {name}  ({source})")

    if errors:
        print()
        for message in errors:
            print(f"ERROR  {message}")
        return 1
    print(f"\n{len(plugins)} plugin(s) checked, no problems found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

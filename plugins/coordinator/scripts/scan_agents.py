#!/usr/bin/env python3
"""Read-only scan of every agent repo's .agent/ hand-off folders (stdlib only).

Usage:
  python3 scan_agents.py --config <path/to/coordinator.json>
  python3 scan_agents.py --config <path/to/coordinator.json> --mark-briefed

Prints one JSON document: for each agent in the config, its pending tasks,
the tasks it filed and the reports it wrote since the last briefing, each with
a derived state (working, waiting, done, error) and flags (stalled, unclear).

It never changes an agent repo. The only file it writes is the state file
(the time of the last briefing), and only with --mark-briefed.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_STALL_HOURS = 36
FIRST_RUN_LOOKBACK_DAYS = 7


def now_utc():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def parse_iso(text):
    try:
        dt = datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def created_at(path):
    """Best guess at when a file was written: birth time if the OS keeps it."""
    st = path.stat()
    ts = getattr(st, "st_birthtime", None) or st.st_mtime
    return datetime.fromtimestamp(ts, timezone.utc)


def changed_at(path):
    """When a file was last written or moved. A move (mv) keeps mtime but sets ctime."""
    st = path.stat()
    return datetime.fromtimestamp(max(st.st_mtime, st.st_ctime), timezone.utc)


def frontmatter(text):
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


def section(text, heading_prefix):
    """Body of the first '## <heading_prefix>...' section, or None."""
    lines = text.splitlines()
    out, inside = [], False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().lower().startswith(heading_prefix.lower())
            continue
        if inside:
            out.append(line)
    if not inside and not out:
        return None
    body = "\n".join(out).strip()
    return body or None


def is_none(body):
    return body is None or body.strip().strip('."').lower() in {"none", "n/a", "nothing"}


def read_report(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = frontmatter(text)
    needs = section(text, "Needs")
    flags = section(text, "Knowledge flags")
    return {
        "file": path.name,
        "location": "outbox/done" if path.parent.name == "done" else "outbox",
        "status": (fm or {}).get("status"),
        "completed": (fm or {}).get("completed"),
        "frontmatter_ok": fm is not None,
        "changed": iso(changed_at(path)),
        "needs_owner": None if is_none(needs) else needs,
        "knowledge_flags": None if is_none(flags) else flags,
    }


def md_files(folder):
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix == ".md")


def state_from_report(report):
    status = (report["status"] or "").lower()
    if status in {"done", "complete", "completed"}:
        return "done"
    if status.startswith("needs"):  # needs-approval, and variants such as needs-review
        return "waiting"
    if status in {"blocked", "failed", "error"}:
        return "error"
    return None


def scan_agent(agent, since, now, default_stall):
    name = agent.get("name") or "?"
    repo = Path(str(agent.get("repo", ""))).expanduser()
    stall_hours = agent.get("stall_hours") or default_stall
    result = {
        "name": name,
        "repo": str(agent.get("repo", "")),
        "bot": agent.get("bot"),
        "stall_hours": stall_hours,
        "pending": [],
        "filed_since": [],
        "reports_since": [],
        "unclear": [],
    }
    agent_dir = repo / ".agent"
    if not (agent_dir / "inbox").is_dir():
        result["unclear"].append(f"no .agent/inbox/ in {result['repo']}: not set up, or not the main checkout")
        return result

    inbox = agent_dir / "inbox"
    done_dir = inbox / "done"
    outbox = agent_dir / "outbox"
    reports = {}
    for path in md_files(outbox) + md_files(outbox / "done"):
        reports[path.name] = read_report(path)

    for path in md_files(inbox):
        born = created_at(path)
        age = (now - born).total_seconds() / 3600
        fm = frontmatter(path.read_text(encoding="utf-8", errors="replace")) or {}
        report = reports.get(path.name)
        task = {
            "file": path.name,
            "age_hours": round(age, 1),
            "needs_approval": fm.get("needs_approval") == "true",
            "report_status": report["status"] if report else None,
        }
        if report:
            task["state"] = state_from_report(report) or "unclear"
            result["unclear"].append(f"{path.name}: has a report but was not filed to inbox/done/")
        else:
            task["state"] = "working"
            task["stalled"] = age > stall_hours
        result["pending"].append(task)

    for path in md_files(done_dir):
        if changed_at(path) <= since:
            continue
        report = reports.get(path.name)
        entry = {"file": path.name, "changed": iso(changed_at(path))}
        if report is None:
            entry["state"] = "unclear"
            result["unclear"].append(f"{path.name}: filed to done/ with no outbox report")
        else:
            entry["state"] = state_from_report(report) or "unclear"
            entry["report_status"] = report["status"]
        result["filed_since"].append(entry)

    for report in reports.values():
        if parse_iso(report["changed"]) <= since:
            continue
        report = dict(report)
        report["state"] = state_from_report(report) or "unclear"
        if not report["frontmatter_ok"]:
            result["unclear"].append(f"{report['file']}: report has no frontmatter")
        elif report["state"] == "unclear":
            result["unclear"].append(f"{report['file']}: can't tell its state from status {report['status']!r}")
        # A report with no task file is the agent writing on its own initiative: allowed.
        report["task_found"] = (inbox / report["file"]).exists() or (done_dir / report["file"]).exists()
        result["reports_since"].append(report)

    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", required=True, help="path to coordinator.json")
    parser.add_argument("--mark-briefed", action="store_true", help="record now as the last briefing time")
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve()
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": f"cannot read config {config_path}: {exc}"}))
        return 1

    state_path = config_path.parent / config.get("state_file", "coordinator.state.json")
    now = now_utc()

    if args.mark_briefed:
        state_path.write_text(json.dumps({"last_briefing": iso(now)}, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"last_briefing": iso(now), "state_file": str(state_path)}))
        return 0

    last = None
    if state_path.is_file():
        try:
            last = parse_iso(json.loads(state_path.read_text(encoding="utf-8")).get("last_briefing"))
        except (OSError, json.JSONDecodeError, AttributeError):
            last = None
    since = last or (now - timedelta(days=FIRST_RUN_LOOKBACK_DAYS))

    default_stall = config.get("stall_hours") or DEFAULT_STALL_HOURS
    agents = [scan_agent(a, since, now, default_stall) for a in config.get("agents", [])]
    print(json.dumps({
        "now": iso(now),
        "since": iso(since),
        "first_run": last is None,
        "state_file": str(state_path),
        "agents": agents,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

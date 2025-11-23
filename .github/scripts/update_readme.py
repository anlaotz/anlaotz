#!/usr/bin/env python3
import os
import re
from datetime import datetime
from github import Github

USERNAME = "anlaotz"
README_PATH = "README.md"

SECTIONS = {
    "HIGHLIGHT": {
        "start": "<!-- START_HIGHLIGHT -->",
        "end": "<!-- END_HIGHLIGHT -->"
    },
    "ACTIVITY": {
        "start": "<!-- START_ACTIVITY -->",
        "end": "<!-- END_ACTIVITY -->"
    }
}

def fetch_latest_repos(g, limit=5):
    repos = sorted(
        [r for r in g.get_user(USERNAME).get_repos() if not r.fork],
        key=lambda r: r.pushed_at or r.created_at,
        reverse=True
    )
    return repos[:limit]

def fetch_events(g, limit=5):
    events = g.get_user(USERNAME).get_events()
    result = []
    for e in events[:limit]:
        if e.type == "PushEvent":
            result.append(f"⬆️ Pushed to **{e.repo.name}**")
        elif e.type == "IssuesEvent":
            result.append(f"🐛 Issue on **{e.repo.name}**")
        elif e.type == "PullRequestEvent":
            result.append(f"🔀 PR on **{e.repo.name}**")
    return result

def replace_section(content, section_name, items):
    block = "\n".join(items)
    sec = SECTIONS[section_name]
    pattern = re.compile(f"{sec['start']}.*?{sec['end']}", re.DOTALL)
    replacement = f"{sec['start']}\n{block}\n{sec['end']}"
    return pattern.sub(replacement, content)

def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("❌ Missing GITHUB_TOKEN env")

    g = Github(token)

    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    # update highlight project
    latest = fetch_latest_repos(g)
    repos_text = [
        f"- **[{r.name}]({r.html_url})** — {r.description or '(no description)'}"
        for r in latest
    ]
    repos_text.append(f"\n_Last update: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_")

    updated = replace_section(readme, "HIGHLIGHT", repos_text)

    # update recent activity
    acts = fetch_events(g)
    updated = replace_section(updated, "ACTIVITY", [f"- {a}" for a in acts])

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    print("README updated.")

if __name__ == "__main__":
    main()

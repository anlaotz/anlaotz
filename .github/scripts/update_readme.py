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
    user = g.get_user(USERNAME)
    repos = sorted(
        [r for r in user.get_repos() if not r.fork],
        key=lambda r: r.pushed_at or r.created_at,
        reverse=True
    )
    return repos[:limit]

def fetch_events(g, limit=5):
    user = g.get_user(USERNAME)
    events = user.get_events()
    result = []
    for e in events[:limit]:
        if e.type == "PushEvent":
            result.append(f"⬆️ Pushed to **{e.repo.name}**")
        elif e.type == "IssuesEvent":
            result.append(f"🐛 Issue on **{e.repo.name}**")
        elif e.type == "PullRequestEvent":
            result.append(f"🔀 PR on **{e.repo.name}**")
        else:
            # fallback generic
            result.append(f"📦 {e.type} on **{e.repo.name}**")
    if not result:
        result.append("No recent public GitHub activity.")
    return result

def replace_section(content, section_name, items):
    sec = SECTIONS[section_name]
    start = sec["start"]
    end = sec["end"]

    if start not in content or end not in content:
        print(f"⚠️ Section markers for {section_name} not found in README.")
        return content

    block = "\n".join(items)
    pattern = re.compile(f"{re.escape(start)}.*?{re.escape(end)}", re.DOTALL)
    replacement = f"{start}\n{block}\n{end}"
    return pattern.sub(replacement, content)

def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("❌ Missing GITHUB_TOKEN env")

    g = Github(token)

    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    original = readme

    # Highlight projects
    latest = fetch_latest_repos(g)
    repos_text = [
        f"- **[{r.name}]({r.html_url})** — {r.description or '(no description)'}"
        for r in latest
    ]
    repos_text.append(f"\n_Last update: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_")
    readme = replace_section(readme, "HIGHLIGHT", repos_text)

    # Recent activity
    acts = fetch_events(g)
    readme = replace_section(readme, "ACTIVITY", [f"- {a}" for a in acts])

    if readme == original:
        print("ℹ️ README not changed (maybe markers missing or no new data?).")
    else:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(readme)
        print("✅ README updated.")

if __name__ == "__main__":
    main()

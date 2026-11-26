"""Builds the dynamic parts of the profile README (stdlib only).

  python scripts/build_profile.py stats     -> assets/stats.svg + README projects table
  python scripts/build_profile.py activity  -> README recent-activity list
"""
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "UTSAVS26"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
SKIP_LANGS = {"Jupyter Notebook", "HTML", "CSS", "SCSS", "JavaScript", "TypeScript", "Vue"}  # keep the card focused on AI/ML + systems code
EXCLUDE_REPOS = {"Personalized-News-Aggregator", "Micro-Doppler-Based-Target-Classification"}  # web-heavy repos stay off the featured list


# Training Run tokens (cool white / graphite, one signal red). The SVG follows the viewer's colour scheme.
CSS = (
    ".sans{font-family:Onest,Inter,'Segoe UI',Helvetica,Arial,sans-serif}"
    ".mono{font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
    ".bg{fill:#F6F7F9;stroke:#D3D8DF}.ink{fill:#14161A}.inkf{fill:#14161A}.mut{fill:#59606B}.red{fill:#C8321A}.ln{stroke:#D3D8DF;fill:none}"
    "@media (prefers-color-scheme:dark){.bg{fill:#14161A;stroke:#2B3038}.ink{fill:#F2F3F5}.inkf{fill:#F2F3F5}.mut{fill:#A2A8B2}.red{fill:#FF6A4D}.ln{stroke:#2B3038}}"
)


def api(path, **params):
    url = "https://api.github.com" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-builder"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def replace_section(name, body):
    text = open(README, encoding="utf8").read()
    pat = re.compile(rf"(<!--START_SECTION:{name}-->).*?(<!--END_SECTION:{name}-->)", re.S)
    if not pat.search(text):
        sys.exit(f"marker {name} missing in README")
    new = pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", text)
    if new != text:
        open(README, "w", encoding="utf8", newline="\n").write(new)


def ago(iso):
    d = datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))
    s = int(d.total_seconds())
    for n, unit in ((86400, "d"), (3600, "h"), (60, "m")):
        if s >= n:
            return f"{s // n}{unit} ago"
    return "just now"


def stats():
    repos = [r for r in api(f"/users/{USER}/repos", per_page=100, type="owner") if not r["fork"]]
    profile = api(f"/users/{USER}")
    stars = sum(r["stargazers_count"] for r in repos)
    forks = sum(r["forks_count"] for r in repos)
    try:
        prs = api("/search/issues", q=f"author:{USER} type:pr is:merged -user:{USER}")["total_count"]
    except Exception:
        prs = 0

    langs = {}
    for r in repos:
        try:
            for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
                if k not in SKIP_LANGS:
                    langs[k] = langs.get(k, 0) + v
        except Exception:
            pass
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]

    tiles = [("STARS", stars), ("FORKS", forks), ("OSS PRs MERGED", prs), ("REPOS", profile["public_repos"]), ("FOLLOWERS", profile["followers"])]
    # Training Run look: graphite and cool white, one signal red. The top language is red, the rest are graphite steps.
    W, H = 840, 260
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<style>{CSS}</style>',
         f'<rect class="bg" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="4"/>',
         f'<text class="mono mut" x="28" y="42" font-size="13" letter-spacing="1.2">@{html.escape(USER).upper()} / LIVE FROM GITHUB</text>',
         f'<circle class="red" cx="{W - 32}" cy="38" r="5"/>']
    tw = (W - 56) / len(tiles)
    for i, (label, val) in enumerate(tiles):
        x = 28 + i * tw
        if i:
            o.append(f'<path class="ln" d="M{x - 14:.0f} 70V132"/>')
        o.append(f'<text class="sans ink" x="{x:.0f}" y="108" font-size="38" font-weight="700" letter-spacing="-1">{val:,}</text>')
        o.append(f'<text class="mono mut" x="{x:.0f}" y="128" font-size="11" letter-spacing="1.2">{label}</text>')
    o.append('<text class="mono mut" x="28" y="170" font-size="11" letter-spacing="1.2">CODE BY LANGUAGE (AI / SYSTEMS FOCUS)</text>')
    bw, x = W - 56, 28
    steps = [1, 0.8, 0.55, 0.38, 0.24]
    cls = ["red"] + ["inkf"] * 4
    for i, (k, v) in enumerate(top):
        w = bw * v / sum(v2 for _, v2 in top)
        o.append(f'<rect class="{cls[i]}" fill-opacity="{1 if i == 0 else steps[i]}" x="{x:.1f}" y="180" width="{max(w - 2, 1):.1f}" height="10" rx="2"/>')
        x += w
    lw = bw / max(len(top), 1)
    for i, (k, v) in enumerate(top):
        lx = 28 + i * lw
        o.append(f'<rect class="{cls[i]}" fill-opacity="{1 if i == 0 else steps[i]}" x="{lx:.0f}" y="209" width="10" height="10" rx="2"/>')
        o.append(f'<text class="sans ink" x="{lx + 18:.0f}" y="218" font-size="13">{html.escape(k)} <tspan class="mono mut" font-size="12">{100 * v / total:.1f}%</tspan></text>')
    o.append(f'<text class="mono mut" x="{W - 28}" y="{H - 14}" font-size="10" text-anchor="end">updated {datetime.now(timezone.utc):%Y-%m-%d}</text>')
    o.append("</svg>")
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    open(os.path.join(ROOT, "assets", "stats.svg"), "w", encoding="utf8", newline="\n").write("\n".join(o))

    feat = sorted((r for r in repos if r["name"].lower() != USER.lower() and r["name"] not in EXCLUDE_REPOS and r["description"]), key=lambda r: (-r["stargazers_count"], r["pushed_at"]), reverse=False)[:4]
    import textwrap
    cells = []
    for i, r in enumerate(feat):
        lines = textwrap.wrap(r["description"], 54)[:2]
        if len(textwrap.wrap(r["description"], 54)) > 2:
            lines[1] = lines[1][:51].rstrip() + "..."
        lang = r["language"] or "Code"
        t = "".join(f'<text class="sans mut" x="24" y="{80 + 19 * j}" font-size="13">{html.escape(l)}</text>' for j, l in enumerate(lines))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="410" height="150" viewBox="0 0 410 150">'
               f'<style>{CSS}</style>'
               f'<rect class="bg" x=".5" y=".5" width="409" height="149" rx="4"/>'
               f'<text class="mono red" x="24" y="30" font-size="12" letter-spacing="1.2">{i + 1:02d}</text>'
               f'<text class="sans ink" x="24" y="56" font-size="20" font-weight="700" letter-spacing="-.4">{html.escape(r["name"])}</text>{t}'
               f'<path class="ln" d="M24 112H386"/>'
               f'<text class="mono ink" x="24" y="134" font-size="12">{html.escape(lang)}</text>'
               f'<text class="mono ink" x="386" y="134" font-size="12" text-anchor="end">{r["stargazers_count"]} stars</text></svg>')
        open(os.path.join(ROOT, "assets", f"project-{i + 1}.svg"), "w", encoding="utf8", newline="\n").write(svg)
        cells.append(f'<a href="{r["html_url"]}"><img src="assets/project-{i + 1}.svg" alt="{html.escape(r["name"])}" width="100%"/></a>')
    rows = ['<table><tr>']
    for i, c in enumerate(cells):
        rows.append(f'<td width="50%">{c}</td>')
        if i % 2 == 1 and i < len(cells) - 1:
            rows.append('</tr><tr>')
    rows.append('</tr></table>')
    replace_section("projects", "\n".join(rows))


def activity():
    lines = []
    for e in api(f"/users/{USER}/events/public", per_page=50):
        repo, p, t = e["repo"]["name"], e["payload"], e["type"]
        link = f"[{repo.split('/')[-1]}](https://github.com/{repo})"
        if t == "PushEvent" and p.get("size"):
            msg = f"Pushed {p['size']} commit{'s' if p['size'] > 1 else ''} to {link}"
        elif t == "PullRequestEvent":
            n = p["pull_request"]["number"]
            verb = "Merged" if p["pull_request"].get("merged") else p["action"].capitalize()
            msg = f"{verb} PR [#{n}](https://github.com/{repo}/pull/{n}) in {link}"
        elif t == "IssuesEvent" and p["action"] in ("opened", "closed"):
            n = p["issue"]["number"]
            msg = f"{p['action'].capitalize()} issue [#{n}](https://github.com/{repo}/issues/{n}) in {link}"
        elif t == "CreateEvent" and p.get("ref_type") == "repository":
            msg = f"Created {link}"
        else:
            continue
        line = f"- {msg} · <sub>{ago(e['created_at'])}</sub>"
        if line not in lines:
            lines.append(line)
        if len(lines) == 6:
            break
    replace_section("activity", "\n".join(lines) or "_Quiet lately. Heads down building._")


if __name__ == "__main__":
    {"stats": stats, "activity": activity}[sys.argv[1]]()

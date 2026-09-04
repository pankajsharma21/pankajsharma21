#!/usr/bin/env python3
"""Builds assets/stats.svg and assets/contributions.svg from live GitHub data.

Deliberately depends on no third-party stats service: nothing outside this repo
sees the profile, nothing breaks when someone else's free tier runs out, and the
SVGs are plain files in git rather than hotlinked images.

Auth goes through the `gh` CLI so no token is ever read or stored by this script.
In Actions, set GH_TOKEN: ${{ secrets.GITHUB_TOKEN }} and gh picks it up.

Usage: python3 scripts/generate_stats.py [username]
"""
import json
import subprocess
import sys
from datetime import date

USER = sys.argv[1] if len(sys.argv) > 1 else "pankajsharma21"
OUT = "assets"

# Deep space palette, matching hero.svg.
BG, CARD, EDGE = "#0b1120", "#111a2e", "#233149"
FG, MUTED, ACCENT = "#e8eefc", "#8095bd", "#4c7dff"
HEAT = ["#161f36", "#1d3b6e", "#2a5cb0", "#4c86ff", "#8fb6ff"]

LANG_COLOR = {
    "Java": "#e76f00", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Python": "#3572A5", "HTML": "#e34c26", "CSS": "#563d7c",
    "Shell": "#89e051", "Dockerfile": "#384d54", "Other": "#6b7a99",
}


def gh(path, jq=None):
    cmd = ["gh", "api", path]
    if jq:
        cmd += ["--jq", jq]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise SystemExit("gh api failed for %s:\n%s" % (path, out.stderr.strip()))
    return out.stdout.strip()


def graphql(query):
    out = subprocess.run(["gh", "api", "graphql", "-f", "query=" + query],
                         capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise SystemExit("gh api graphql failed:\n" + out.stderr.strip())
    return json.loads(out.stdout)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def collect():
    repos = json.loads(gh("users/%s/repos?per_page=100&type=owner" % USER))
    public = [r for r in repos if not r["private"]]

    langs = {}
    for r in public:
        name = r.get("language") or "Other"
        langs[name] = langs.get(name, 0) + 1

    commits = 0
    try:
        commits = int(gh("search/commits?q=author:%s&per_page=1" % USER, ".total_count"))
    except SystemExit:
        pass                                   # commit search is best-effort

    # The contribution calendar needs a token allowed to read user data. Actions'
    # default GITHUB_TOKEN sometimes is not, so treat this as optional: without it
    # we still emit stats.svg and simply leave the existing contributions.svg alone.
    try:
        cal = graphql('{ user(login: "%s") { contributionsCollection {'
                      ' contributionCalendar { totalContributions weeks {'
                      ' contributionDays { date contributionCount weekday } } } } } }' % USER)
        cal = cal["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    except (SystemExit, KeyError, TypeError) as e:
        print("warning: contribution calendar unavailable (%s) — keeping the existing "
              "contributions.svg. If this persists in Actions, use a PAT with read:user "
              "as GH_TOKEN." % type(e).__name__)
        cal = None

    if cal is None:
        return {"repos": len(public), "commits": commits,
                "stars": sum(r["stargazers_count"] for r in public),
                "contrib": None, "best": None, "cur": None,
                "langs": sorted(langs.items(), key=lambda kv: -kv[1]), "weeks": None}

    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    streak = best = 0
    for d in days:
        if d["contributionCount"] > 0:
            streak += 1
            best = max(best, streak)
        else:
            streak = 0
    # A gap on today alone shouldn't reset the "current" streak to zero.
    cur = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            cur += 1
        elif cur or d is not days[-1]:
            break

    stars = sum(r["stargazers_count"] for r in public)
    return {
        "repos": len(public), "commits": commits, "stars": stars,
        "contrib": cal["totalContributions"], "best": best, "cur": cur,
        "langs": sorted(langs.items(), key=lambda kv: -kv[1]),
        "weeks": cal["weeks"],
    }


def stats_svg(d):
    W, H = 900, 240
    total_langs = sum(n for _, n in d["langs"]) or 1
    top = d["langs"][:6]

    tiles = [("Public repos", d["repos"]), ("Commits", d["commits"]),
             ("Contributions", d["contrib"] if d["contrib"] is not None else "—"),
             ("Longest streak", "%d d" % d["best"] if d["best"] is not None else "—")]
    cells = []
    for i, (label, value) in enumerate(tiles):
        x = 30 + i * 212
        cells.append(
            f'<g><rect x="{x}" y="56" width="192" height="78" rx="12" fill="{CARD}" stroke="{EDGE}"/>'
            f'<text x="{x+96}" y="96" text-anchor="middle" font-size="30" font-weight="700" fill="{FG}" font-family="\'Segoe UI\',Ubuntu,Helvetica,Arial,sans-serif">{esc(value)}</text>'
            f'<text x="{x+96}" y="118" text-anchor="middle" font-size="12" fill="{MUTED}" letter-spacing="1.2" font-family="\'Segoe UI\',Ubuntu,Helvetica,Arial,sans-serif">{esc(label.upper())}</text></g>')

    bar, legend, x = [], [], 30.0
    BAR_W = 840.0
    for i, (lang, n) in enumerate(top):
        w = BAR_W * n / total_langs
        color = LANG_COLOR.get(lang, "#6b7a99")
        r_left = "6" if i == 0 else "0"
        bar.append(f'<rect x="{x:.1f}" y="166" width="{w:.1f}" height="14" fill="{color}"/>')
        x += w
        if i < 4:
            lx = 30 + i * 200
            legend.append(
                f'<circle cx="{lx+5}" cy="209" r="5" fill="{color}"/>'
                f'<text x="{lx+18}" y="213" font-size="12.5" fill="{MUTED}" font-family="\'Segoe UI\',Ubuntu,Helvetica,Arial,sans-serif">{esc(lang)} · {n} repos</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub statistics">
<rect width="{W}" height="{H}" rx="14" fill="{BG}" stroke="{EDGE}"/>
<text x="30" y="36" font-size="16" font-weight="600" fill="{FG}" font-family="'Segoe UI',Ubuntu,Helvetica,Arial,sans-serif">GitHub activity</text>
<text x="{W-30}" y="36" text-anchor="end" font-size="11.5" fill="{MUTED}" font-family="'Segoe UI',Ubuntu,Helvetica,Arial,sans-serif">updated {date.today().isoformat()}</text>
{"".join(cells)}
<text x="30" y="158" font-size="12" fill="{MUTED}" letter-spacing="1.2" font-family="'Segoe UI',Ubuntu,Helvetica,Arial,sans-serif">LANGUAGES BY REPOSITORY</text>
<g clip-path="inset(0 round 7px)">{"".join(bar)}</g>
{"".join(legend)}
</svg>'''


def contrib_svg(d):
    CELL, GAP, LEFT, TOP = 11, 3, 34, 44
    weeks = d["weeks"]
    W = LEFT + len(weeks) * (CELL + GAP) + 20
    H = TOP + 7 * (CELL + GAP) + 34

    counts = [day["contributionCount"] for w in weeks for day in w["contributionDays"]]
    peak = max(counts) if counts else 1

    def level(c):
        if c == 0:
            return 0
        if peak <= 4:
            return min(4, c)
        return min(4, 1 + int(3 * (c - 1) / max(peak - 1, 1)))

    squares, months, seen = [], [], set()
    for wi, week in enumerate(weeks):
        x = LEFT + wi * (CELL + GAP)
        for day in week["contributionDays"]:
            y = TOP + day["weekday"] * (CELL + GAP)
            c = day["contributionCount"]
            squares.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                           f'fill="{HEAT[level(c)]}"><title>{day["date"]}: {c}</title></rect>')
        first = week["contributionDays"][0]["date"]
        mon = first[:7]
        label = date.fromisoformat(first).strftime("%b")
        if mon not in seen and int(first[8:]) <= 7:
            seen.add(mon)
            months.append(f'<text x="{x}" y="{TOP-8}" font-size="10.5" fill="{MUTED}" '
                          f'font-family="\'Segoe UI\',Ubuntu,Helvetica,Arial,sans-serif">{label}</text>')

    dows = "".join(
        f'<text x="{LEFT-8}" y="{TOP + i*(CELL+GAP) + 9}" text-anchor="end" font-size="10" fill="{MUTED}" '
        f'font-family="\'Segoe UI\',Ubuntu,Helvetica,Arial,sans-serif">{lbl}</text>'
        for i, lbl in [(1, "Mon"), (3, "Wed"), (5, "Fri")])

    key = "".join(f'<rect x="{W-140+i*15}" y="{H-22}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
                  for i, c in enumerate(HEAT))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Contribution calendar">
<rect width="{W}" height="{H}" rx="14" fill="{BG}" stroke="{EDGE}"/>
<text x="{LEFT-8}" y="26" font-size="15" font-weight="600" fill="{FG}" font-family="'Segoe UI',Ubuntu,Helvetica,Arial,sans-serif">{d["contrib"]} contributions in the last year</text>
{"".join(months)}{dows}{"".join(squares)}
<text x="{W-160}" y="{H-12}" text-anchor="end" font-size="10.5" fill="{MUTED}" font-family="'Segoe UI',Ubuntu,Helvetica,Arial,sans-serif">Less</text>
{key}
<text x="{W-20}" y="{H-12}" text-anchor="end" font-size="10.5" fill="{MUTED}" font-family="'Segoe UI',Ubuntu,Helvetica,Arial,sans-serif">More</text>
</svg>'''


def main():
    d = collect()
    open("%s/stats.svg" % OUT, "w").write(stats_svg(d))
    if d["weeks"] is not None:
        open("%s/contributions.svg" % OUT, "w").write(contrib_svg(d))
    print("repos=%s commits=%s contributions=%s longest_streak=%s"
          % (d["repos"], d["commits"], d["contrib"], d["best"]))
    print("languages:", ", ".join("%s=%d" % kv for kv in d["langs"][:6]))
    print("wrote %s/stats.svg and %s/contributions.svg" % (OUT, OUT))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate a self-contained, offline HTML dashboard from PROJECTS.md.

Why this shape:
  - Local-only (file://): browsers block fetch() over file://, so the data is
    baked straight into the HTML at generation time as inline JSON — no sibling
    file to fetch.
  - Offline charts: Chart.js is *vendored* locally at vendor/chart.umd.min.js and
    referenced by relative path, so the fancy charts render with no network/CDN.
  - No Python deps (stdlib only): no venv, no pip (respects workspace CLAUDE.md).

Run from anywhere:
    python .claude/dashboard/generate_dashboard.py
Then open .claude/dashboard/dashboard.html in a browser. Rerun to refresh.

If the charts don't render, the vendored lib is missing — fetch it once:
    curl -fsSL -o .claude/dashboard/vendor/chart.umd.min.js \
      https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js
"""

from __future__ import annotations

import html
import json
import re
from datetime import date, datetime
from pathlib import Path

# --- paths -----------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent          # .claude/dashboard -> root
PROJECTS_MD = WORKSPACE_ROOT / "PROJECTS.md"
OUTPUT_HTML = SCRIPT_DIR / "dashboard.html"
VENDOR_JS = SCRIPT_DIR / "vendor" / "chart.umd.min.js"

# Tiers we render, in display order, with accent colors.
TIERS = [
    ("active", "#34d399"),     # green
    ("incubator", "#60a5fa"),  # blue
    ("dormant", "#fbbf24"),    # amber
    ("archive", "#94a3b8"),    # slate
]

# Staleness palette (active projects, by days since last touch).
FRESH, STALE, VSTALE = "#34d399", "#fbbf24", "#f87171"

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def clean_cell(text: str) -> str:
    """Strip markdown emphasis (_x_ / *x*) and whitespace from a table cell."""
    return re.sub(r"^[_*]+|[_*]+$", "", text.strip()).strip()


def is_placeholder(name: str) -> bool:
    return name == "" or name.lower() == "example"


def parse_projects(md_text: str) -> dict[str, list[dict]]:
    """Parse PROJECTS.md into {tier: [ {name, stack, date, focus}, ... ]}."""
    tiers: dict[str, list[dict]] = {name: [] for name, _ in TIERS}
    current = None

    for raw in md_text.splitlines():
        line = raw.rstrip()

        header = re.match(r"^##\s+([A-Za-z_]+)/\s*$", line)
        if header:
            current = header.group(1) if header.group(1) in tiers else None
            continue
        if line.startswith("## "):          # a non-tier section
            current = None
            continue

        if current is None or not line.lstrip().startswith("- "):
            continue

        cells = [clean_cell(c) for c in line.lstrip()[2:].split("|")]
        if len(cells) < 4 or is_placeholder(cells[0]):
            continue

        m = DATE_RE.search(cells[2])
        tiers[current].append({
            "name": cells[0],
            "stack": cells[1],
            "date": m.group(1) if m else "",
            "focus": cells[3],
        })

    return tiers


def days_ago(iso: str, today: date) -> int | None:
    if not iso:
        return None
    try:
        return (today - datetime.strptime(iso, "%Y-%m-%d").date()).days
    except ValueError:
        return None


def stale_color(n: int | None) -> str:
    if n is None:
        return STALE
    if n >= 30:
        return VSTALE
    if n >= 14:
        return STALE
    return FRESH


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def build_payload(tiers: dict[str, list[dict]], today: date) -> dict:
    """Everything the page's JS needs, as a JSON-serializable dict."""
    counts = {name: len(tiers[name]) for name, _ in TIERS}

    # Doughnut: one slice per tier (skip empty tiers so the chart stays clean).
    doughnut = {
        "labels": [name for name, _ in TIERS if counts[name] > 0],
        "data": [counts[name] for name, _ in TIERS if counts[name] > 0],
        "colors": [color for name, color in TIERS if counts[name] > 0],
    }

    # Horizontal bar: days since last touch for active projects, most stale first.
    act = []
    for p in tiers["active"]:
        n = days_ago(p["date"], today)
        act.append({"name": p["name"], "days": n if n is not None else 0,
                    "color": stale_color(n)})
    act.sort(key=lambda x: x["days"], reverse=True)
    activity = {
        "labels": [a["name"] for a in act],
        "data": [a["days"] for a in act],
        "colors": [a["color"] for a in act],
    }

    return {
        "generated": today.isoformat(),
        "total": sum(counts.values()),
        "counts": counts,
        "doughnut": doughnut,
        "activity": activity,
    }


def render_cards(tiers: dict[str, list[dict]], today: date) -> str:
    sections = []
    for name, color in TIERS:
        cards = []
        for p in tiers[name]:
            n = days_ago(p["date"], today)
            cls = ""
            if name == "active" and n is not None:
                cls = "vstale" if n >= 30 else "stale" if n >= 14 else ""
            marker = ""
            if cls == "vstale":
                marker = '<span class="marker">🚨</span> '
            elif cls == "stale":
                marker = '<span class="marker">⚠</span> '
            ago = f"{n}d ago" if n is not None else "—"
            stack = esc(p["stack"]) if p["stack"] and p["stack"] != "—" else "—"
            cards.append(
                f'<div class="card {cls}">'
                f'<div class="cardhead">{marker}<span class="pname">{esc(p["name"])}</span>'
                f'<span class="ago">{ago}</span></div>'
                f'<div class="stack">{stack}</div>'
                f'<div class="focus">{esc(p["focus"])}</div></div>'
            )
        body = "".join(cards) if cards else '<div class="empty">— empty</div>'
        sections.append(
            f'<section class="tier"><h2 style="--accent:{color}">{name}/ '
            f'<span class="tcount">{len(tiers[name])}</span></h2>'
            f'<div class="cards">{body}</div></section>'
        )
    return "".join(sections)


def render(tiers: dict[str, list[dict]], today: date) -> str:
    payload = build_payload(tiers, today)
    return TEMPLATE.format(
        data_json=json.dumps(payload),
        cards=render_cards(tiers, today),
        generated=payload["generated"],
        total=payload["total"],
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Workspace Dashboard</title>
<script src="vendor/chart.umd.min.js"></script>
<style>
  :root {{
    --bg:#0b1120; --panel:#111827; --panel2:#1e293b;
    --ink:#e2e8f0; --muted:#94a3b8; --line:#1f2a3a;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font:14px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
    padding:28px clamp(16px,4vw,48px); }}
  header {{ display:flex; align-items:baseline; gap:14px; margin-bottom:22px; }}
  header h1 {{ font-size:20px; margin:0; letter-spacing:.3px; }}
  header .gen {{ color:var(--muted); font-size:12px; }}
  header .gen b {{ color:var(--ink); }}

  .charts {{ display:grid; gap:18px; margin-bottom:26px;
    grid-template-columns:minmax(240px,300px) 1fr; align-items:stretch; }}
  @media (max-width:720px) {{ .charts {{ grid-template-columns:1fr; }} }}
  .panel {{ background:var(--panel); border:1px solid var(--line);
    border-radius:14px; padding:16px 18px; }}
  .panel h3 {{ margin:0 0 12px; font-size:12px; text-transform:uppercase;
    letter-spacing:1px; color:var(--muted); }}
  .chartbox {{ position:relative; height:240px; }}
  #fallback {{ display:none; color:#f87171; font-size:13px; padding:8px 0; }}

  .tiers {{ display:grid; gap:22px;
    grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); }}
  .tier h2 {{ font-size:13px; text-transform:uppercase; letter-spacing:1px;
    color:var(--accent); margin:0 0 12px; border-left:3px solid var(--accent);
    padding-left:10px; display:flex; gap:8px; align-items:center; }}
  .tcount {{ color:var(--muted); font-weight:600; }}
  .cards {{ display:grid; gap:10px; }}
  .card {{ background:var(--panel); border:1px solid var(--line);
    border-radius:12px; padding:12px 14px; transition:border-color .15s,transform .15s; }}
  .card:hover {{ border-color:#334155; transform:translateY(-1px); }}
  .card.stale {{ border-left:3px solid #fbbf24; }}
  .card.vstale {{ border-left:3px solid #f87171; }}
  .cardhead {{ display:flex; align-items:center; gap:8px; }}
  .pname {{ font-weight:600; flex:1; word-break:break-word; }}
  .ago {{ color:var(--muted); font-size:12px; font-variant-numeric:tabular-nums;
    white-space:nowrap; }}
  .marker {{ font-size:13px; }}
  .stack {{ display:inline-block; margin:7px 0 6px; font-size:11px; color:var(--muted);
    background:var(--panel2); border-radius:6px; padding:2px 8px; }}
  .focus {{ color:#cbd5e1; font-size:13px; }}
  .empty {{ color:var(--muted); font-style:italic; padding:6px 2px; }}
  footer {{ margin-top:30px; color:var(--muted); font-size:12px; }}
</style>
</head>
<body>
  <header>
    <h1>🗂️ AI Workspace</h1>
    <span class="gen">{total} projects · generated <b>{generated}</b></span>
  </header>

  <div id="fallback">⚠ Charts library not found. Fetch it once:
    <code>curl -fsSL -o .claude/dashboard/vendor/chart.umd.min.js https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js</code></div>

  <div class="charts">
    <div class="panel">
      <h3>Projects by tier</h3>
      <div class="chartbox"><canvas id="tierChart"></canvas></div>
    </div>
    <div class="panel">
      <h3>Active — days since last touch</h3>
      <div class="chartbox"><canvas id="activityChart"></canvas></div>
    </div>
  </div>

  <div class="tiers">{cards}</div>

  <footer>Generated from PROJECTS.md by .claude/dashboard/generate_dashboard.py · Chart.js vendored locally · rerun to refresh.</footer>

<script id="payload" type="application/json">{data_json}</script>
<script>
(function () {{
  var DATA = JSON.parse(document.getElementById('payload').textContent);
  if (typeof Chart === 'undefined') {{ document.getElementById('fallback').style.display = 'block'; return; }}

  Chart.defaults.color = '#94a3b8';
  Chart.defaults.font.family = 'ui-sans-serif, system-ui, "Segoe UI", Roboto, sans-serif';
  var GRID = 'rgba(148,163,184,0.12)';

  new Chart(document.getElementById('tierChart'), {{
    type: 'doughnut',
    data: {{ labels: DATA.doughnut.labels,
      datasets: [{{ data: DATA.doughnut.data, backgroundColor: DATA.doughnut.colors,
        borderColor: '#0b1120', borderWidth: 2, hoverOffset: 6 }}] }},
    options: {{ responsive: true, maintainAspectRatio: false, cutout: '62%',
      plugins: {{ legend: {{ position: 'bottom', labels: {{ usePointStyle: true, padding: 14 }} }} }} }}
  }});

  new Chart(document.getElementById('activityChart'), {{
    type: 'bar',
    data: {{ labels: DATA.activity.labels,
      datasets: [{{ label: 'days', data: DATA.activity.data,
        backgroundColor: DATA.activity.colors, borderRadius: 5, maxBarThickness: 26 }}] }},
    options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }},
        tooltip: {{ callbacks: {{ label: function (c) {{ return c.parsed.x + ' days ago'; }} }} }} }},
      scales: {{ x: {{ beginAtZero: true, grid: {{ color: GRID }}, ticks: {{ precision: 0 }} }},
        y: {{ grid: {{ display: false }} }} }} }}
  }});
}})();
</script>
</body>
</html>
"""


def main() -> None:
    if not PROJECTS_MD.exists():
        raise SystemExit(f"PROJECTS.md not found at {PROJECTS_MD}")
    tiers = parse_projects(PROJECTS_MD.read_text(encoding="utf-8"))
    OUTPUT_HTML.write_text(render(tiers, date.today()), encoding="utf-8")

    counts = ", ".join(f"{name}={len(tiers[name])}" for name, _ in TIERS)
    print(f"Wrote {OUTPUT_HTML}")
    print(f"Tiers: {counts}")
    if not VENDOR_JS.exists():
        print(f"WARNING: {VENDOR_JS} missing — charts won't render until you fetch it "
              "(see the header comment in this script).")


if __name__ == "__main__":
    main()

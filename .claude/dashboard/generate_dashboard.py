#!/usr/bin/env python3
"""Generate a self-contained, offline HTML dashboard from PROJECTS.md.

Why this shape:
  - Local-only (file://): browsers block fetch() over file://, so the data is
    baked straight into the HTML at generation time as inline JSON — no sibling
    file to fetch.
  - Offline charts + fonts: Chart.js is *vendored* locally at vendor/chart.umd.min.js,
    and the Outfit / Inter / Fira Code fonts are vendored as vendor/*.woff2 and
    @font-face'd by relative path — the page renders fully with no network/CDN.
  - No Python deps (stdlib only): no venv, no pip (respects workspace CLAUDE.md).

Design: the visual system is specified in DESIGN.dashboard.md (premium glassmorphism,
deep-navy palette, luminous glow gradients). This is the dashboard's OWN identity and is
deliberately distinct from the muted-teal flat theme used for reading docs (DOC_THEME.md).

Run from anywhere:
    python .claude/dashboard/generate_dashboard.py
Then open .claude/dashboard/dashboard.html in a browser. Rerun to refresh.

If the charts don't render, the vendored lib is missing — fetch it once:
    curl -fsSL -o .claude/dashboard/vendor/chart.umd.min.js \
      https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js
If fonts fall back to system sans, the woff2 files are missing from vendor/ — fetch via
@fontsource (see the header comment that originally vendored them) or accept the fallback.
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

# Tiers we render, in display order. Each maps to a glow from DESIGN.dashboard.md:
# a solid (chart slices / accents) + the full gradient (card + header bars).
TIERS = [
    ("active",    "#00E5E8", "linear-gradient(135deg,#00A3A6 0%,#00E5E8 100%)"),  # teal glow
    ("incubator", "#4FACFE", "linear-gradient(135deg,#00F2FE 0%,#4FACFE 100%)"),  # blue glow
    ("dormant",   "#F093FB", "linear-gradient(135deg,#F093FB 0%,#F5576C 100%)"),  # purple glow
    ("archive",   "#94A3B8", "linear-gradient(135deg,#64748B 0%,#94A3B8 100%)"),  # slate
]

# Staleness palette (active projects, by days since last touch) — a heat scale.
FRESH, STALE, VSTALE = "#00E5E8", "#FBBF24", "#FF4D6D"

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def clean_cell(text: str) -> str:
    """Strip markdown emphasis (_x_ / *x*) and whitespace from a table cell."""
    return re.sub(r"^[_*]+|[_*]+$", "", text.strip()).strip()


def is_placeholder(name: str) -> bool:
    return name == "" or name.lower() == "example"


def parse_projects(md_text: str) -> dict[str, list[dict]]:
    """Parse PROJECTS.md into {tier: [ {name, stack, date, focus}, ... ]}."""
    tiers: dict[str, list[dict]] = {name: [] for name, _, _ in TIERS}
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
    counts = {name: len(tiers[name]) for name, _, _ in TIERS}

    # Doughnut: one slice per tier (skip empty tiers so the chart stays clean).
    doughnut = {
        "labels": [name for name, _, _ in TIERS if counts[name] > 0],
        "data": [counts[name] for name, _, _ in TIERS if counts[name] > 0],
        "colors": [solid for name, solid, _ in TIERS if counts[name] > 0],
    }

    # Horizontal bar: staleness for the tiers where age is *actionable* — active and
    # incubator. Dormant/archive are intentionally old, so they're excluded (no false
    # alarms). Worst (stalest) on top. Color: tier hue when healthy, warning hue when at
    # risk — active uses the 14/30 heat scale; incubator only cares about the 30d line
    # (→ promote or delete), so it stays tier-blue until then.
    act = []
    for p in tiers["active"]:
        n = days_ago(p["date"], today)
        act.append({"label": p["name"], "days": n if n is not None else 0,
                    "color": stale_color(n)})
    for p in tiers["incubator"]:
        n = days_ago(p["date"], today)
        d = n if n is not None else 0
        act.append({"label": "inc · " + p["name"], "days": d,
                    "color": VSTALE if d >= 30 else "#4FACFE"})
    act.sort(key=lambda x: x["days"], reverse=True)
    activity = {
        "labels": [a["label"] for a in act],
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
    for name, solid, grad in TIERS:
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
            f'<section class="tier" style="--accent:{solid};--grad:{grad}">'
            f'<h2>{name}/ <span class="tcount">{len(tiers[name])}</span></h2>'
            f'<div class="cards">{body}</div></section>'
        )
    return "".join(sections)


def render(tiers: dict[str, list[dict]], today: date) -> str:
    payload = build_payload(tiers, today)
    out = TEMPLATE
    out = out.replace("__DATA_JSON__", json.dumps(payload))
    out = out.replace("__CARDS__", render_cards(tiers, today))
    out = out.replace("__GENERATED__", payload["generated"])
    out = out.replace("__TOTAL__", str(payload["total"]))
    return out


# Token-replacement template (no str.format → braces stay literal, CSS/JS unescaped).
# Placeholders: __DATA_JSON__ __CARDS__ __GENERATED__ __TOTAL__
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Workspace · Control Center</title>
<script src="vendor/chart.umd.min.js"></script>
<style>
  /* --- vendored fonts (offline; relative to this file) --- */
  @font-face { font-family:'Outfit'; src:url('vendor/outfit-700.woff2') format('woff2'); font-weight:700; font-display:swap; }
  @font-face { font-family:'Outfit'; src:url('vendor/outfit-600.woff2') format('woff2'); font-weight:600; font-display:swap; }
  @font-face { font-family:'Inter'; src:url('vendor/inter-400.woff2') format('woff2'); font-weight:400; font-display:swap; }
  @font-face { font-family:'Inter'; src:url('vendor/inter-600.woff2') format('woff2'); font-weight:600; font-display:swap; }
  @font-face { font-family:'Fira Code'; src:url('vendor/firacode-400.woff2') format('woff2'); font-weight:400; font-display:swap; }

  /* registered custom prop so the conic angle can animate (hover border light) */
  @property --bd-angle { syntax:'<angle>'; inherits:false; initial-value:0deg; }

  :root {
    --bg:#0A0E1A;
    --surface:rgba(17,24,43,0.7); --surface-hover:rgba(26,36,64,0.8);
    --border:rgba(255,255,255,0.08); --border-focus:rgba(0,242,254,0.4);
    --ink:#F3F4F6; --muted:#9CA3AF;
    --display:'Outfit',ui-sans-serif,system-ui,sans-serif;
    --sans:'Inter',ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
    --mono:'Fira Code',ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  }
  * { box-sizing:border-box; }
  body {
    margin:0; color:var(--ink);
    font:14px/1.5 var(--sans);
    padding:30px clamp(16px,4vw,52px);
    background:
      radial-gradient(900px 520px at 10% -8%, rgba(0,242,254,.10), transparent 60%),
      radial-gradient(820px 480px at 96% -2%, rgba(240,147,251,.08), transparent 55%),
      radial-gradient(700px 600px at 50% 120%, rgba(0,229,232,.06), transparent 60%),
      var(--bg);
    background-attachment:fixed;
    min-height:100vh;
  }
  ::selection { background:rgba(0,242,254,.22); }

  header { display:flex; align-items:baseline; gap:14px; margin-bottom:24px; animation:fadeIn .5s ease both; }
  header h1 {
    font-family:var(--display); font-weight:700; font-size:22px; margin:0; letter-spacing:.2px;
    background:linear-gradient(135deg,#00F2FE 0%,#4FACFE 60%,#F093FB 130%);
    -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  }
  header .gen { color:var(--muted); font-size:12px; font-family:var(--mono); }
  header .gen b { color:var(--ink); }

  .glass {
    background:var(--surface); border:1px solid var(--border); border-radius:16px;
    backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
    box-shadow:0 8px 32px rgba(0,0,0,0.2);
  }

  .charts { display:grid; gap:18px; margin-bottom:28px;
    grid-template-columns:minmax(240px,320px) 1fr; align-items:stretch;
    animation:fadeIn .6s ease both; }
  @media (max-width:760px) { .charts { grid-template-columns:1fr; } }
  .panel { padding:18px 20px; position:relative; }
  /* hover: a dim two-tone (teal→purple) light travels around the panel's border.
     A rotating conic-gradient masked to a 1.5px ring — interior stays transparent
     and click-through, so the chart + tooltips are untouched. Chart panels only. */
  .panel::after {
    content:''; position:absolute; inset:0; border-radius:16px; padding:1.5px;
    background:conic-gradient(from var(--bd-angle),
      transparent 0deg, rgba(0,229,232,0) 35deg, #00E5E8 110deg,
      #F093FB 190deg, rgba(240,147,251,0) 265deg, transparent 360deg);
    -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite:xor;
    mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    mask-composite:exclude;
    opacity:0; transition:opacity .35s ease; pointer-events:none;
  }
  .panel:hover::after { opacity:.6; animation:bd-spin 3.4s linear infinite; }
  .panel h3 { margin:0 0 12px; font-size:11px; text-transform:uppercase;
    letter-spacing:1.4px; color:var(--muted); font-family:var(--mono); }
  .chartbox { position:relative; height:240px; }
  #fallback { display:none; color:#FF4D6D; font-size:13px; padding:8px 0; font-family:var(--mono); }

  .tiers { display:grid; gap:22px; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); }
  .tier { animation:fadeIn .6s ease both; }
  .tier h2 {
    font-family:var(--display); font-size:13px; font-weight:600; text-transform:uppercase;
    letter-spacing:1.4px; color:var(--ink); margin:0 0 14px;
    display:flex; gap:10px; align-items:center;
  }
  .tier h2::before {
    content:''; width:10px; height:10px; border-radius:3px; background:var(--grad);
    box-shadow:0 0 12px -1px var(--accent);
  }
  .tcount { color:var(--muted); font-weight:400; font-family:var(--mono); font-size:12px; }

  .cards { display:grid; gap:11px; }
  .card {
    position:relative; overflow:hidden; padding:13px 15px 13px 18px;
    background:var(--surface); border:1px solid var(--border); border-radius:14px;
    backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
    box-shadow:0 8px 32px rgba(0,0,0,0.2);
    --bar:var(--grad);
    transition:transform .3s cubic-bezier(.4,0,.2,1), border-color .3s, box-shadow .3s, background .3s;
  }
  .card::before {
    content:''; position:absolute; left:0; top:0; bottom:0; width:3px; background:var(--bar);
  }
  .card:hover {
    transform:translateY(-5px); background:var(--surface-hover);
    border-color:var(--border-focus); box-shadow:0 12px 40px rgba(0,242,254,0.15);
  }
  .card.stale  { --bar:#FBBF24; }
  .card.vstale { --bar:#FF4D6D; }
  .cardhead { display:flex; align-items:center; gap:8px; }
  .pname { font-weight:600; flex:1; word-break:break-word; }
  .ago { color:var(--muted); font-size:12px; font-family:var(--mono); font-variant-numeric:tabular-nums; white-space:nowrap; }
  .marker { font-size:13px; }
  .stack { display:inline-block; margin:8px 0 7px; font-size:11px; color:var(--muted);
    font-family:var(--mono); background:rgba(255,255,255,.04);
    border:1px solid var(--border); border-radius:6px; padding:2px 8px; }
  .focus { color:#CBD5E1; font-size:13px; }
  .empty { color:var(--muted); font-style:italic; padding:6px 2px; }

  .cap { margin-top:11px; font-size:11px; color:var(--muted); font-family:var(--mono); line-height:1.7; }
  .cap .dot { font-size:9px; vertical-align:1px; }
  .cap .teal { color:#00E5E8; } .cap .blue { color:#4FACFE; }

  footer { margin-top:34px; color:var(--muted); font-size:12px; font-family:var(--mono); }

  @keyframes fadeIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
  @keyframes bd-spin { to { --bd-angle:360deg; } }
  @media (prefers-reduced-motion:reduce) { *, ::before { animation:none !important; transition:none !important; } }
</style>
</head>
<body>
  <header>
    <h1>◆ AI Workspace · Control Center</h1>
    <span class="gen">__TOTAL__ projects · generated <b>__GENERATED__</b></span>
  </header>

  <div id="fallback">⚠ Charts library not found. Fetch it once:
    <code>curl -fsSL -o .claude/dashboard/vendor/chart.umd.min.js https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js</code></div>

  <div class="charts">
    <div class="panel glass">
      <h3>Projects by tier</h3>
      <div class="chartbox"><canvas id="tierChart"></canvas></div>
    </div>
    <div class="panel glass">
      <h3>Staleness · active + incubator</h3>
      <div class="chartbox"><canvas id="activityChart"></canvas></div>
      <div class="cap"><span class="dot teal">●</span> active &nbsp; <span class="dot blue">●</span> incubator &nbsp;·&nbsp; dashed <b style="color:#FBBF24">14d</b> stale · <b style="color:#FF4D6D">30d → move</b> (active→dormant · incubator→promote/delete)</div>
    </div>
  </div>

  <div class="tiers">__CARDS__</div>

  <footer>Generated from PROJECTS.md by .claude/dashboard/generate_dashboard.py · design: DESIGN.dashboard.md · Chart.js + fonts vendored locally · rerun to refresh.</footer>

<script id="payload" type="application/json">__DATA_JSON__</script>
<script>
(function () {
  var DATA = JSON.parse(document.getElementById('payload').textContent);
  if (typeof Chart === 'undefined') { document.getElementById('fallback').style.display = 'block'; return; }

  Chart.defaults.color = '#9CA3AF';
  Chart.defaults.font.family = "'Inter', ui-sans-serif, system-ui, sans-serif";
  var GRID = 'rgba(148,163,184,0.12)';

  new Chart(document.getElementById('tierChart'), {
    type: 'doughnut',
    data: { labels: DATA.doughnut.labels,
      datasets: [{ data: DATA.doughnut.data, backgroundColor: DATA.doughnut.colors,
        borderColor: '#0A0E1A', borderWidth: 3, hoverOffset: 6 }] },
    options: { responsive: true, maintainAspectRatio: false, cutout: '64%',
      plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, padding: 14 } } } }
  });

  // Dashed "move line" thresholds drawn over the bars (no plugin dependency).
  var THRESHOLDS = [ { v: 14, c: '#FBBF24', t: '14d stale' }, { v: 30, c: '#FF4D6D', t: '30d → move' } ];
  var thresholdLines = {
    id: 'thresholdLines',
    afterDraw: function (chart) {
      var x = chart.scales.x, area = chart.chartArea, ctx = chart.ctx;
      THRESHOLDS.forEach(function (th) {
        var px = x.getPixelForValue(th.v);
        if (px < area.left || px > area.right) return;
        ctx.save();
        ctx.strokeStyle = th.c; ctx.lineWidth = 1.5; ctx.setLineDash([4, 4]);
        ctx.beginPath(); ctx.moveTo(px, area.top); ctx.lineTo(px, area.bottom); ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = th.c; ctx.font = "10px 'Fira Code', ui-monospace, monospace";
        ctx.textAlign = 'center';
        ctx.fillText(th.t, px, area.top - 4);
        ctx.restore();
      });
    }
  };
  var maxDays = Math.max(34, Math.max.apply(null, DATA.activity.data.concat([0])) + 4);

  new Chart(document.getElementById('activityChart'), {
    type: 'bar',
    data: { labels: DATA.activity.labels,
      datasets: [{ label: 'days', data: DATA.activity.data,
        backgroundColor: DATA.activity.colors, borderRadius: 6, maxBarThickness: 26 }] },
    options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 14 } },
      plugins: { legend: { display: false },
        tooltip: { callbacks: { label: function (c) { return c.parsed.x + ' days ago'; } } } },
      scales: { x: { beginAtZero: true, suggestedMax: maxDays, grid: { color: GRID }, ticks: { precision: 0 } },
        y: { grid: { display: false } } } },
    plugins: [thresholdLines]
  });
})();
</script>
</body>
</html>
"""


def main() -> None:
    if not PROJECTS_MD.exists():
        raise SystemExit(f"PROJECTS.md not found at {PROJECTS_MD}")
    tiers = parse_projects(PROJECTS_MD.read_text(encoding="utf-8"))
    OUTPUT_HTML.write_text(render(tiers, date.today()), encoding="utf-8")

    counts = ", ".join(f"{name}={len(tiers[name])}" for name, _, _ in TIERS)
    print(f"Wrote {OUTPUT_HTML}")
    print(f"Tiers: {counts}")
    if not VENDOR_JS.exists():
        print(f"WARNING: {VENDOR_JS} missing — charts won't render until you fetch it "
              "(see the header comment in this script).")


if __name__ == "__main__":
    main()

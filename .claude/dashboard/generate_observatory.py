#!/usr/bin/env python3
"""
generate_observatory.py — one project, one page: the unified per-project view.

The answer to instrument sprawl: cosmos (domains), boundary (seams), and the
Spec Health instrument used to be separate HTMLs; the observatory composes
them as tabs over ONE scan (scripts/scan_project.py — one scanner, many
callers). This is the ONE user-facing door (/observatory); the cosmos and
boundary generators are its renderer modules (their CLIs remain for debugging)
and render the same facts, so the views can't disagree.

Tabs:
    Overview    — goal, the now (CONTEXT), the spine table, authored-doc links
    Domains     — the cosmos 2D star system (embedded)
    Seams       — the boundary seam graph (embedded; empty-state if no
                  integration SPEC — with the pointer, never a guess)
    Spec Health — per-domain contract honesty: walls vs [review] judgment,
                  gates, Behavioral Contract lines bound to tests, template
                  FILL leftovers. Freeform SPECs get a tag census, labeled so.

Theming is live: the chrome runs on CSS variables and the embedded instruments
are pre-rendered in every palette, so the header's theme buttons switch the
whole page in place (persisted in localStorage under `obs-theme`; --theme only
sets the first-load default).

Everything is scanned live from the docs. A wrong page means wrong docs.

Usage:
    python .claude/dashboard/generate_observatory.py <project-or-alias>
        [--theme nebula|ember|aurora|void] [--open]

Output: .claude/dashboard/observatory/<project>.html (gitignored — regenerate).
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from resolve_project import resolve  # noqa: E402
from scan_project import scan, trunc  # noqa: E402
from generate_cosmos import THEMES, STATUS_LABEL, render_2d, render_3d  # noqa: E402
from generate_boundary import render as render_boundary  # noqa: E402

esc = html_mod.escape
STATUS_CLASS = {"◑": "st-a", "✓": "st-s", "○": "st-p"}


def overview_html(facts: dict, project_path: Path) -> str:
    ctx = facts["context"]
    if ctx.get("exists"):
        days = ctx["days_ago"]
        touched = (f'{ctx["last_touched"]} · '
                   + ("today" if days == 0 else f"{days}d ago" if days is not None else "?"))
        now = (f'<div class="ocard"><div class="ohead">now — CONTEXT.md</div>'
               f'<div class="okv">last touched <b>{esc(touched)}</b> · {ctx["lines"]} lines</div>'
               f'<div class="onext"><span class="olbl">next step</span> '
               f'{esc(ctx["next_step"]) or "<em>none recorded</em>"}</div></div>')
    else:
        now = ('<div class="ocard warn"><div class="ohead">now</div>'
               '<div class="okv">no CONTEXT.md — the session ritual is broken here</div></div>')

    rows = []
    for d in sorted(facts["domains"], key=lambda x: ({"◑": 0, "✓": 1, "○": 2}[x["status"]], x["name"])):
        touched = ("today" if d["age_days"] < 1 else
                   f'{d["age_days"]:.0f}d' if d["age_days"] < 900 else "—")
        rows.append(
            f'<tr><td><code>{esc(d["name"])}</code></td>'
            f'<td><span class="dot {STATUS_CLASS[d["status"]]}"></span>'
            f'{d["status"]} {STATUS_LABEL[d["status"]]}</td>'
            f'<td>{"⊚" if d["spec"] else "—"}</td><td>{"☾" if d["arch"] else "—"}</td>'
            f'<td>{len(d["plans"]) or "—"}</td><td>{touched}</td>'
            f'<td class="why">{esc(trunc(d["why"], 90)) or "<em>no MISSION row</em>"}</td></tr>')

    links = []
    for label, rel in (("MISSION.html", ".gravity/MISSION.html"),
                       ("ARCHITECTURE.html", ".gravity/ARCHITECTURE.html"),
                       ("IMPLEMENTATION_PLAN.md", ".gravity/IMPLEMENTATION_PLAN.md"),
                       ("CLAUDE.md", "CLAUDE.md"), ("CONTEXT.md", "CONTEXT.md")):
        p = project_path / rel
        if p.exists():
            links.append(f'<a href="{p.as_uri()}" target="_blank">{label}</a>')

    return f"""<div class="pad">
  <div class="goal">{esc(facts["goal"]) or "<em>no goal: line in IMPLEMENTATION_PLAN.md</em>"}</div>
  {now}
  <div class="ocard"><div class="ohead">spine — {len(facts["domains"])} domains</div>
  <table class="spine"><tr><th>domain</th><th>status</th><th>SPEC</th><th>ARCH</th>
  <th>PLANs</th><th>touched</th><th>why</th></tr>{"".join(rows)}</table></div>
  <div class="ocard"><div class="ohead">authored docs</div>
  <div class="links">{" · ".join(links) or "—"}</div></div>
</div>"""


def spec_health_html(facts: dict) -> str:
    status_of = {d["name"]: d["status"] for d in facts["domains"]}
    census = facts["specs"]
    fenced = [c for c in census if c["has_spec"]]
    total = sum(c["rules"]["total"] for c in fenced)
    walls = sum(c["rules"]["wall"] for c in fenced)
    bc_bound = sum(c["bc_bound"] for c in fenced)
    bc_unbound = sum(c["bc_unbound"] for c in fenced)
    pct = f"{100 * walls / total:.0f}%" if total else "—"

    cards = []
    for c in sorted(census, key=lambda x: (not x["has_spec"], x["domain"])):
        st = status_of.get(c["domain"], "○")
        head = (f'<div class="ohead"><span class="dot {STATUS_CLASS[st]}"></span>'
                f'<code>{esc(c["domain"])}</code>'
                + ('<span class="formtag">freeform</span>' if c["has_spec"] and c["form"] == "freeform" else "")
                + '</div>')
        if not c["has_spec"]:
            cards.append(f'<div class="hcard nospec">{head}'
                         '<div class="okv">no SPEC — unfenced (fine for read-only '
                         'domains; a domain agents change wants walls)</div></div>')
            continue
        r = c["rules"]
        if r["total"]:
            seg = "".join(
                f'<span class="seg {cls}" style="flex:{n}"></span>'
                for n, cls in ((r["wall"], "seg-w"), (r["judgment"], "seg-j"),
                               (r["guidance"], "seg-g")) if n)
            bar = (f'<div class="bar">{seg}</div>'
                   f'<div class="okv"><b class="okc">{r["wall"]} wall'
                   f'{"s" if r["wall"] != 1 else ""}</b> · '
                   f'<span class="satc">{r["judgment"]} judgment</span> · '
                   f'<span class="dimc">{r["guidance"]} guidance</span>'
                   + (" <i>(tag census — freeform sheet)</i>" if c["form"] == "freeform" else "")
                   + '</div>')
        else:
            bar = '<div class="okv wt">SPEC exists but zero rules found</div>'
        gate = (f'<div class="okv gate">gate — <span class="mono">{esc(trunc(c["gate"], 90))}</span></div>'
                if c["gate"] else
                '<div class="okv wt">no Gate line — nothing proves a change here</div>')
        bc = ""
        if c["bc_bound"] or c["bc_unbound"]:
            unb = (f' · <span class="wt">{c["bc_unbound"]} unbound</span>'
                   if c["bc_unbound"] else "")
            bc = (f'<div class="okv">behavioral contract: <b class="okc">'
                  f'{c["bc_bound"]} test-bound</b>{unb}</div>')
        fills = (f'<div class="okv wt">⚠ {c["fills"]} template '
                 f'FILL leftover{"s" if c["fills"] != 1 else ""}</div>' if c["fills"] else "")
        cards.append(f'<div class="hcard">{head}{bar}{gate}{bc}{fills}</div>')

    return f"""<div class="pad">
  <div class="hsum"><b>{len(fenced)}</b>/<b>{len(census)}</b> domains fenced ·
    <b>{total}</b> rules, <b class="okc">{walls} walls</b> ({pct}) ·
    behavioral contract <b class="okc">{bc_bound} test-bound</b>{f' / <b class="wt">{bc_unbound} unbound</b>' if bc_unbound else ""}</div>
  <div class="hint">A <b>wall</b> is a rule tooling enforces ([lint]/[type]/[test:…]);
    judgment ([review]) and guidance ([—]) rely on humans. Low wall-share isn't shame —
    it's the honest map of where the contract can lie. Promote rules by giving them tests.</div>
  <div class="hgrid">{"".join(cards)}</div>
</div>"""


def theme_vars(name: str, t: dict) -> str:
    return (f'[data-theme="{name}"] {{ --bg:{t["bg"]}; --bg2:{t["bg2"]}; '
            f'--panel:{t["panel"]}; --card:{t["card"]}; --line:{t["line"]}; '
            f'--ink:{t["ink"]}; --dim:{t["dim"]}; --accent:{t["status"]["◑"]}; '
            f'--ok:{t["status"]["✓"]}; --plan:{t["status"]["○"]}; '
            f'--guard:{t["guard"]}; --sat:{t["sat"]} }}')


def render_page(facts: dict, theme: str, project_path: Path) -> str:
    integ = facts["integration"]

    # every theme's instruments, pre-rendered — the buttons swap them in place
    inst: dict[str, dict] = {}
    for tn, tt in THEMES.items():
        entry = {"domains": render_2d(facts, tt), "orbit": render_3d(facts, tt)}
        if integ is not None:
            entry["seams"] = render_boundary(integ, tt)
        inst[tn] = entry
    payload = json.dumps(inst, ensure_ascii=False).replace("</", "<\\/")

    if integ is not None:
        seams_tab = '<iframe class="inst" id="if-seams"></iframe>'
        n_seams = f'{len(integ["seams"])} seams'
        n_open = sum(1 for e in integ["seams"] if e["open"])
        if n_open:
            n_seams += f' · {n_open} OPEN'
    else:
        seams_tab = (f'<div class="pad"><div class="ocard warn"><div class="ohead">no seam graph</div>'
                     f'<div class="okv">this project has no <span class="mono">.gravity/integration/SPEC.md</span> — '
                     f'author it with <span class="mono">/new-spec {esc(facts["project"])} integration</span>'
                     f' (or <span class="mono">/excavate</span> for a brownfield survey). '
                     f'The observatory never draws seams it can\'t cite.</div></div></div>')
        n_seams = "no integration SPEC"
    fenced = sum(1 for c in facts["specs"] if c["has_spec"])

    theme_css = "\n  ".join(theme_vars(n, t) for n, t in THEMES.items())
    swatches = "".join(
        f'<button data-th="{n}" title="{n}" style="background:{t["star"][1]}"></button>'
        for n, t in THEMES.items())

    return f"""<!doctype html><html lang="en" data-theme="{theme}"><meta charset="utf-8">
<title>{esc(facts["project"])} — gravity observatory</title>
<style>
  {theme_css}
  * {{ box-sizing:border-box }}
  body {{ margin:0; height:100vh; display:flex; flex-direction:column; color:var(--ink);
    background:radial-gradient(1100px 700px at 40% 0%, var(--bg2) 0%, var(--bg) 62%);
    font:14px/1.5 "Segoe UI",system-ui,sans-serif; transition:background .3s }}
  header {{ display:flex; align-items:baseline; gap:14px; padding:12px 20px 0 }}
  header h1 {{ font-size:16px; margin:0 }}
  header .census {{ color:var(--dim); font-size:12px; flex:1 }}
  #themebar {{ display:flex; gap:6px; align-self:center }}
  #themebar button {{ width:18px; height:18px; border-radius:50%; cursor:pointer;
    border:2px solid transparent; padding:0 }}
  #themebar button.on {{ border-color:var(--ink) }}
  #themebar button:hover {{ transform:scale(1.15) }}
  nav {{ display:flex; gap:4px; padding:8px 20px 0; border-bottom:1px solid var(--line) }}
  nav button {{ background:none; border:1px solid transparent; border-bottom:none;
    color:var(--dim); font:600 13px "Segoe UI",system-ui,sans-serif; padding:7px 16px;
    cursor:pointer; border-radius:9px 9px 0 0 }}
  nav button:hover {{ color:var(--ink) }}
  nav button.on {{ color:var(--ink); background:var(--panel); border-color:var(--line) }}
  main {{ flex:1; min-height:0 }}
  .tab {{ display:none; height:100% }}
  .tab.on {{ display:block }}
  .tab.scroll {{ overflow-y:auto }}
  .inst {{ width:100%; height:100%; border:none; display:block }}
  .pad {{ padding:18px 22px; max-width:1060px }}
  .goal {{ font-size:14.5px; margin-bottom:14px }}
  .ocard {{ border:1px solid var(--line); border-radius:12px; background:var(--card);
    padding:13px 16px; margin-bottom:14px }}
  .ocard.warn {{ border-color:var(--guard) }}
  .ohead {{ font-size:11px; letter-spacing:1.2px; text-transform:uppercase;
    color:var(--dim); margin-bottom:8px; display:flex; align-items:center; gap:8px }}
  .ohead code {{ font-size:13px; color:var(--ink); text-transform:none; letter-spacing:0 }}
  .okv {{ font-size:12.5px; color:var(--ink); margin-bottom:4px }}
  .onext {{ font-size:13px; margin-top:6px }}
  .olbl {{ font-size:10.5px; letter-spacing:1px; text-transform:uppercase;
    color:var(--accent); margin-right:8px }}
  .dot {{ width:9px; height:9px; border-radius:50%; display:inline-block; margin-right:6px }}
  .st-a {{ background:var(--accent) }} .st-s {{ background:var(--ok) }}
  .st-p {{ background:var(--plan) }}
  table.spine {{ border-collapse:collapse; width:100%; font-size:12.5px }}
  table.spine th {{ text-align:left; color:var(--dim); font-weight:600; font-size:11px;
    letter-spacing:.6px; text-transform:uppercase; padding:4px 10px 6px 0 }}
  table.spine td {{ padding:5px 10px 5px 0; border-top:1px solid var(--line) }}
  table.spine td.why {{ color:var(--dim) }}
  .links a {{ color:var(--sat); text-decoration:none; font-family:monospace; font-size:12.5px }}
  .links a:hover {{ text-decoration:underline }}
  .mono {{ font-family:monospace; font-size:12px }}
  .wt {{ color:var(--guard) }} .okc {{ color:var(--ok) }}
  .satc {{ color:var(--sat) }} .dimc {{ color:var(--dim) }}
  .hsum {{ font-size:13.5px; margin-bottom:8px }}
  .hint {{ color:var(--dim); font-size:12px; margin-bottom:16px; max-width:760px }}
  .hgrid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(310px,1fr)); gap:12px }}
  .hcard {{ border:1px solid var(--line); border-radius:12px; background:var(--card);
    padding:12px 14px }}
  .hcard.nospec {{ border-style:dashed; opacity:.75 }}
  .formtag {{ font-size:10px; letter-spacing:1px; color:var(--sat);
    border:1px solid var(--line); border-radius:8px; padding:1px 7px }}
  .bar {{ display:flex; height:8px; border-radius:4px; overflow:hidden; margin:4px 0 6px }}
  .seg {{ min-width:3px }}
  .seg-w {{ background:var(--ok) }} .seg-j {{ background:var(--sat) }}
  .seg-g {{ background:var(--dim) }}
  .gate {{ color:var(--dim) }}
  footer {{ padding:6px 20px; color:var(--dim); font-size:11px; font-family:monospace;
    border-top:1px solid var(--line) }}
</style>
<header><h1>☉ {esc(facts["title"])}</h1>
  <span class="census">{len(facts["domains"])} domains · {n_seams} ·
    {fenced}/{len(facts["specs"])} fenced · generated {facts["generated"]}</span>
  <div id="themebar">{swatches}</div></header>
<nav>
  <button class="on" data-tab="overview">Overview</button>
  <button data-tab="domains">Domains</button>
  <button data-tab="seams">Seams</button>
  <button data-tab="health">Spec Health</button>
  <button data-tab="orbit">Orbit 3D</button>
</nav>
<main>
  <div class="tab scroll on" id="tab-overview">{overview_html(facts, project_path)}</div>
  <div class="tab" id="tab-domains"><iframe class="inst" id="if-domains"></iframe></div>
  <div class="tab{"" if integ is not None else " scroll"}" id="tab-seams">{seams_tab}</div>
  <div class="tab scroll" id="tab-health">{spec_health_html(facts)}</div>
  <div class="tab" id="tab-orbit"><iframe class="inst" id="if-orbit"></iframe></div>
</main>
<footer>gravity observatory · scanned live from the project docs — a wrong page means
 wrong docs (fix them, rerun)</footer>
<script>
  const INST = {payload};
  const domIF = document.getElementById('if-domains');
  const seamIF = document.getElementById('if-seams');
  const orbIF = document.getElementById('if-orbit');
  function setTheme(n) {{
    document.documentElement.dataset.theme = n;
    domIF.srcdoc = INST[n].domains;
    orbIF.srcdoc = INST[n].orbit;
    if (seamIF && INST[n].seams) seamIF.srcdoc = INST[n].seams;
    try {{ localStorage.setItem('obs-theme', n); }} catch (e) {{}}
    document.querySelectorAll('#themebar button').forEach(b =>
      b.classList.toggle('on', b.dataset.th === n));
  }}
  document.querySelectorAll('#themebar button').forEach(b =>
    b.addEventListener('click', () => setTheme(b.dataset.th)));
  let saved = null;
  try {{ saved = localStorage.getItem('obs-theme'); }} catch (e) {{}}
  setTheme(INST[saved] ? saved : "{theme}");

  document.querySelectorAll('nav button').forEach(b => b.addEventListener('click', () => {{
    document.querySelectorAll('nav button').forEach(x => x.classList.remove('on'));
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('on'));
    b.classList.add('on');
    document.getElementById('tab-' + b.dataset.tab).classList.add('on');
  }}));
</script>
</html>"""


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="One project, one page — the unified gravity view.")
    ap.add_argument("project", help="project name or alias (resolve_project.py)")
    ap.add_argument("--theme", choices=sorted(THEMES), default="nebula",
                    help="first-load default; the page has live theme buttons")
    ap.add_argument("--open", action="store_true", help="open the result in the browser")
    args = ap.parse_args()

    name, path = resolve(args.project)  # exits with candidates if ambiguous
    facts = scan(path)
    outdir = Path(__file__).resolve().parent / "observatory"
    outdir.mkdir(exist_ok=True)
    out = outdir / f"{name}.html"
    out.write_text(render_page(facts, args.theme, path), encoding="utf-8")

    integ = facts["integration"]
    seams = f"{len(integ['seams'])} seams" if integ else "no integration SPEC"
    fenced = sum(1 for c in facts["specs"] if c["has_spec"])
    print(f"observatory[{args.theme}]: {len(facts['domains'])} domains · {seams} · "
          f"{fenced}/{len(facts['specs'])} fenced · {len(THEMES)} live themes -> {out}")
    if args.open:
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()

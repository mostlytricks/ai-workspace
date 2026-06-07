"""
add_theme_switch.py — give the aurora-themed browser docs the SAME 5-theme switcher the
dashboard uses (Aurora / Daylight / Sandstone / Forest / Slate), sharing the dashboard's
localStorage key so a theme chosen in either place applies everywhere.

Per file (idempotent — skips files that already carry the .themebar):
  1. Replaces the appended aurora override block with five [data-theme] token palettes
     (ported from .claude/dashboard/dashboard.html onto the docs' token names) + tokenized
     visual flourishes (radial bg, gradient h1, glow, glass blur) that adapt per theme +
     the .themebar pill styles. Custom CSS above the block is untouched.
  2. Replaces the no-FOUC <head> init script (now reads the shared 'dash-theme' key).
  3. Replaces the floating widget before </body> with the 5-pill swatch bar + its script.

Re-run safely:  python .claude/scripts/add_theme_switch.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THEMES = ["aurora", "daylight", "sandstone", "forest", "slate"]

CSS_RE = re.compile(
    r"[ \t]*/\* =+ aurora doc theme.*?(?=\n[ \t]*</style>)", re.DOTALL
)
HEAD_RE = re.compile(r"[ \t]*<script>/\* no-FOUC theme init.*?</script>\n?", re.DOTALL)
WIDGET_RE = re.compile(r'[ \t]*<button id="theme-toggle".*?</script>\n?', re.DOTALL)

NEW_CSS = """  /* ===== aurora doc theme + 5-theme switcher (dashboard-matched) — appended; later rules win, custom CSS above preserved =====
     Five palettes selected via <html data-theme>, ported from .claude/dashboard onto the doc token names.
     Switching re-points every var(--token) already used above; the flourishes below are tokenized so they
     adapt per theme. Custom diagram CSS above this block is left untouched. */
  :root, html[data-theme="aurora"] {
    --bg:#0A0E1A; --panel:rgba(17,24,43,0.70); --panel-2:rgba(26,36,64,0.80); --line:rgba(255,255,255,0.08);
    --text-hi:#F3F4F6; --text:#CBD5E1; --text-mid:#9CA3AF; --faint:#717a8c;
    --accent:#00E5E8; --accent-d:#4FACFE; --blue:#4FACFE; --amber:#FBBF24; --red:#FF4D6D;
    --h1-grad:linear-gradient(135deg,#00F2FE 0%,#4FACFE 60%,#F093FB 130%);
    --glow:rgba(0,229,232,.85); --hover-glow:rgba(0,242,254,.15); --shadow:0 8px 32px rgba(0,0,0,.22);
    --body-bg:
      radial-gradient(900px 520px at 10% -8%, rgba(0,242,254,.10), transparent 60%),
      radial-gradient(820px 480px at 96% -2%, rgba(240,147,251,.08), transparent 55%),
      radial-gradient(700px 600px at 50% 120%, rgba(0,229,232,.06), transparent 60%), #0A0E1A;
  }
  html[data-theme="daylight"] {
    --bg:#F7F9FC; --panel:rgba(255,255,255,0.85); --panel-2:#eef2f8; --line:rgba(15,23,42,0.10);
    --text-hi:#1E293B; --text:#334155; --text-mid:#64748B; --faint:#94A3B8;
    --accent:#2563EB; --accent-d:#7C3AED; --blue:#2563EB; --amber:#B45309; --red:#DC2626;
    --h1-grad:linear-gradient(135deg,#2563EB 0%,#4F46E5 60%,#7C3AED 130%);
    --glow:rgba(37,99,235,.35); --hover-glow:rgba(37,99,235,.16); --shadow:0 8px 24px rgba(15,23,42,.08);
    --body-bg:
      radial-gradient(900px 520px at 10% -8%, rgba(37,99,235,.07), transparent 60%),
      radial-gradient(820px 480px at 96% -2%, rgba(124,58,237,.06), transparent 55%),
      radial-gradient(700px 600px at 50% 120%, rgba(37,99,235,.05), transparent 60%), #F7F9FC;
  }
  html[data-theme="sandstone"] {
    --bg:#FBF6EF; --panel:rgba(255,252,247,0.88); --panel-2:#f3ebdf; --line:rgba(120,80,40,0.14);
    --text-hi:#3D2E22; --text:#5C4A38; --text-mid:#8C7A66; --faint:#a8957f;
    --accent:#C2410C; --accent-d:#D97706; --blue:#D97706; --amber:#B45309; --red:#DC2626;
    --h1-grad:linear-gradient(135deg,#C2410C 0%,#D97706 60%,#B45309 130%);
    --glow:rgba(217,119,6,.40); --hover-glow:rgba(194,65,12,.16); --shadow:0 8px 24px rgba(90,60,30,.10);
    --body-bg:
      radial-gradient(900px 520px at 10% -8%, rgba(217,119,6,.10), transparent 60%),
      radial-gradient(820px 480px at 96% -2%, rgba(194,65,12,.07), transparent 55%),
      radial-gradient(700px 600px at 50% 120%, rgba(180,83,9,.06), transparent 60%), #FBF6EF;
  }
  html[data-theme="forest"] {
    --bg:#0C1A14; --panel:rgba(18,38,30,0.70); --panel-2:rgba(26,52,42,0.82); --line:rgba(255,255,255,0.07);
    --text-hi:#E8F2EC; --text:#C5D8CE; --text-mid:#8BA89A; --faint:#6f897c;
    --accent:#34D399; --accent-d:#A3E635; --blue:#10B981; --amber:#FBBF24; --red:#FB7185;
    --h1-grad:linear-gradient(135deg,#34D399 0%,#10B981 60%,#A3E635 130%);
    --glow:rgba(52,211,153,.70); --hover-glow:rgba(52,211,153,.16); --shadow:0 8px 32px rgba(0,0,0,.25);
    --body-bg:
      radial-gradient(900px 520px at 10% -8%, rgba(52,211,153,.09), transparent 60%),
      radial-gradient(820px 480px at 96% -2%, rgba(163,230,53,.06), transparent 55%),
      radial-gradient(700px 600px at 50% 120%, rgba(16,185,129,.06), transparent 60%), #0C1A14;
  }
  html[data-theme="slate"] {
    --bg:#16181D; --panel:rgba(30,33,40,0.72); --panel-2:rgba(42,46,55,0.85); --line:rgba(255,255,255,0.08);
    --text-hi:#E5E7EB; --text:#C4C9D2; --text-mid:#9499A3; --faint:#6e727b;
    --accent:#94A3B8; --accent-d:#CBD5E1; --blue:#CBD5E1; --amber:#FBBF24; --red:#FB7185;
    --h1-grad:linear-gradient(135deg,#CBD5E1 0%,#94A3B8 60%,#64748B 130%);
    --glow:rgba(148,163,184,.60); --hover-glow:rgba(148,163,184,.16); --shadow:0 8px 32px rgba(0,0,0,.30);
    --body-bg:
      radial-gradient(900px 520px at 10% -8%, rgba(148,163,184,.06), transparent 60%),
      radial-gradient(820px 480px at 96% -2%, rgba(203,213,225,.05), transparent 55%),
      radial-gradient(700px 600px at 50% 120%, rgba(148,163,184,.04), transparent 60%), #16181D;
  }
  /* tokenized flourishes — adapt to whichever theme is active */
  body { background:var(--body-bg); background-attachment:fixed; line-height:1.7; transition:background .4s ease, color .3s ease; }
  h1 {
    font-family:'Outfit',var(--sans); font-weight:700; letter-spacing:-.02em;
    background:var(--h1-grad); -webkit-background-clip:text; background-clip:text; color:transparent;
  }
  .logo .sq { background:var(--h1-grad); box-shadow:0 0 14px -1px var(--glow); }
  h2 .n, .toc a:hover, a:hover { color:var(--accent-d); }
  pre, .toc, .note, .card, .phase {
    backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); box-shadow:var(--shadow);
  }
  .card { transition:transform .25s cubic-bezier(.4,0,.2,1), border-color .25s, box-shadow .25s; }
  .card:hover { transform:translateY(-4px); border-color:var(--accent); box-shadow:0 12px 40px var(--hover-glow); }

  /* theme switcher — fixed top-right pills, one swatch each (matches the dashboard) */
  .themebar { position:fixed; top:14px; right:14px; z-index:60; display:flex; flex-wrap:wrap; gap:6px; }
  .themebar button {
    font:600 11px/1 var(--sans); letter-spacing:.3px; cursor:pointer; color:var(--text-mid);
    background:var(--panel); border:1px solid var(--line); border-radius:999px;
    padding:6px 11px 6px 8px; display:inline-flex; align-items:center; gap:6px;
    backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px);
    transition:color .2s, border-color .2s, transform .2s, box-shadow .2s;
  }
  .themebar button:hover { color:var(--text-hi); transform:translateY(-1px); }
  .themebar button.active { color:var(--text-hi); border-color:var(--accent); box-shadow:0 6px 20px var(--hover-glow); }
  .themebar .sw { width:11px; height:11px; border-radius:50%; box-shadow:0 0 0 1px rgba(0,0,0,.18) inset; }
  @media (max-width:760px){ .themebar { position:static; margin:0 0 18px; } }
  @media (prefers-reduced-motion:reduce){ *{transition:none!important;} }"""

HEAD_SCRIPT = (
    "<script>/* no-FOUC theme init — shares the dashboard's 'dash-theme' key */"
    "(function(){var ok=['aurora','daylight','sandstone','forest','slate'];try{"
    "var t=localStorage.getItem('dash-theme');"
    "document.documentElement.setAttribute('data-theme',ok.indexOf(t)>=0?t:'aurora');}"
    "catch(e){document.documentElement.setAttribute('data-theme','aurora');}})();</script>\n"
)

WIDGET = (
    '<div class="themebar" id="themebar" role="group" aria-label="Theme">'
    '<button data-theme="aurora"><span class="sw" style="background:linear-gradient(135deg,#00F2FE,#F093FB)"></span>Aurora</button>'
    '<button data-theme="daylight"><span class="sw" style="background:linear-gradient(135deg,#60A5FA,#A78BFA)"></span>Daylight</button>'
    '<button data-theme="sandstone"><span class="sw" style="background:linear-gradient(135deg,#F59E0B,#C2410C)"></span>Sandstone</button>'
    '<button data-theme="forest"><span class="sw" style="background:linear-gradient(135deg,#34D399,#A3E635)"></span>Forest</button>'
    '<button data-theme="slate"><span class="sw" style="background:linear-gradient(135deg,#CBD5E1,#64748B)"></span>Slate</button>'
    "</div>\n"
    "<script>(function(){var bar=document.getElementById('themebar');if(!bar)return;"
    "var ok=['aurora','daylight','sandstone','forest','slate'];"
    "function set(t){document.documentElement.setAttribute('data-theme',t);"
    "try{localStorage.setItem('dash-theme',t);}catch(e){}"
    "bar.querySelectorAll('button').forEach(function(b){b.classList.toggle('active',b.getAttribute('data-theme')===t);});}"
    "bar.querySelectorAll('button').forEach(function(b){b.addEventListener('click',function(){set(b.getAttribute('data-theme'));});});"
    "var saved='aurora';try{saved=localStorage.getItem('dash-theme')||'aurora';}catch(e){}"
    "if(ok.indexOf(saved)<0)saved='aurora';set(saved);})();</script>\n"
)

FILES = [
    "ARCHITECTURE.template.html",
    "MISSION.html",
    "MISSION.template.html",
    "repos/agent-view-desktop/ARCHITECTURE.html",
    "repos/agent-view-desktop/MISSION.html",
    "repos/antigravity--pptx-template-manager/ARCHITECTURE.html",
    "repos/antigravity--pptx-template-manager/MISSION.html",
    "repos/api-server-managing-agent/MISSION.html",
    "repos/architecture-memory-os/ARCHITECTURE.html",
    "repos/architecture-memory-os/MISSION.html",
    "repos/local-llmstxt-server/MISSION.html",
    "repos/multi-system-maintenance-agent-system/ARCHITECTURE.html",
]


def transform(text):
    notes = []
    if 'class="themebar"' in text:
        return None, ["already on 5-theme switcher (skipped)"]

    new, n = CSS_RE.subn(NEW_CSS, text)
    if n != 1:
        return None, ["FAILED: css block not matched once (n=%d)" % n]
    notes.append("css")

    new, n = HEAD_RE.subn(HEAD_SCRIPT, new)
    if n != 1:
        # fall back: inject before </head> if the v1 head script wasn't there
        if "</head>" not in new:
            return None, ["FAILED: no head script and no </head>"]
        new = new.replace("</head>", HEAD_SCRIPT + "</head>", 1)
    notes.append("head")

    new, n = WIDGET_RE.subn(WIDGET, new)
    if n != 1:
        if "</body>" not in new:
            return None, ["FAILED: no widget and no </body>"]
        new = new.replace("</body>", WIDGET + "</body>", 1)
    notes.append("widget")
    return new, notes


def main():
    fail = False
    for rel in FILES:
        p = ROOT / rel
        if not p.exists():
            print("MISS  %-58s not found" % rel)
            fail = True
            continue
        new, notes = transform(p.read_text(encoding="utf-8"))
        if new is None:
            tag = "SKIP" if "skipped" in notes[0] else "FAIL"
            if tag == "FAIL":
                fail = True
            print("%-5s %-58s %s" % (tag, rel, "; ".join(notes)))
            continue
        p.write_text(new, encoding="utf-8")
        print("OK    %-58s %s" % (rel, "; ".join(notes)))
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()

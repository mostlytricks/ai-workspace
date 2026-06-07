# DOC_THEME — shared HTML doc theme (aurora)

The workspace theme for **human-facing project HTML docs** (`MISSION.html`, `ARCHITECTURE.html`,
and any design page you want rendered in a browser). A premium **deep-navy glassmorphism** look,
matched to the Control Center dashboard: navy-black canvas, ambient radial glows, semi-transparent
blurred panels, cyan/blue/purple luminous accents. Self-contained, zero runtime dependencies —
fonts fall back to the system stack (no CDN, no `@font-face`), so docs still open offline from `file://`.

`MISSION.template.html` and `ARCHITECTURE.template.html` already ship with this theme inline.
Use this file when you're hand-rolling a *new* HTML doc and want it to match.

> Markdown docs (`CLAUDE.md`, `CONTEXT.md`, `IMPLEMENTATION_PLAN.md`) don't use this — they
> render wherever the agent reads them. The theme is only for browser-read HTML.

**Relationship to the dashboard.** This shares the dashboard's `aurora` palette
(`.claude/dashboard/DESIGN.dashboard.md`) so the two surfaces feel like one product — but they stay
**two systems**: the dashboard is built for *scanning* (vendored Outfit/Inter/Fira Code, Chart.js,
animated comet borders), docs for *reading* (system-font fallback, no JS, calmer motion). When you
restyle one, decide deliberately whether the other should follow.

---

## Tokens

Same token **names** as before (so existing docs re-theme by swapping values only); dashboard-`aurora` **values**.

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0A0E1A` | page canvas (deep navy-black) |
| `--panel` | `rgba(17,24,43,0.66)` | glass cards / code blocks / notes (translucent → blurred) |
| `--panel-2` | `rgba(26,36,64,0.55)` | inline-code background |
| `--line` | `rgba(255,255,255,0.09)` | borders, rules |
| `--text-hi` | `#F3F4F6` | headings, emphasis |
| `--text` | `#cdd3e0` | body |
| `--text-mid` | `#9CA3AF` | secondary / lede |
| `--faint` | `#717a8c` | captions, code comments |
| `--accent` | `#34e3e6` | cyan — links, section numbers, code |
| `--accent-d` | `#00E5E8` | brighter cyan — hover |
| `--blue` | `#4FACFE` | diagram "actor" highlight; `h1` gradient start |
| `--amber` | `#FBBF24` | warnings, "next" tag |
| `--red` | `#FF4D6D` | errors, hard constraints |

`h1` is gradient-clipped **blue→purple** (`#4FACFE → #F093FB`); the `.logo .sq` is a glowing
teal gradient chip. The ambient page background is three low-opacity radial glows (teal / purple /
teal) over `--bg`, `background-attachment:fixed`.

Fonts (stacks only, **no `@font-face`** — degrade to system): `--sans` Inter → system-ui ·
`--mono` Fira Code → ui-monospace · `h1` uses Outfit → `--sans`. Install those families for the
exact dashboard typeface; otherwise the palette + glass still carry the look.

## Patterns (class → purpose)

- `.wrap` — 920px centered column, generous padding.
- `header.top` + `.logo .sq` (glowing gradient square) + `h1` (gradient-clipped) + `.lede`.
- `h2 > span.n` — cyan monospace section number (`01`, `02`, …).
- `.toc` — boxed two-column glass table of contents.
- `.cards` (2-col grid) → `.card` with `.pill.live` / `.pill.mock` chips; cards lift + glow on hover.
- `.phase` — roadmap card; `.tag.done` / `.tag.next` / `.tag.todo` status chips, `.pnum` for the phase number.
- `.note` / `.note.warn` / `.note.red` — left-border glass callout; `.lbl` for the bold lead-in.
- `pre` — glass code/diagram block; inside it use `<b>` (cyan), `.c` (faint comment),
  `.a` (accent), `.b` (blue) spans for ASCII-diagram highlighting.
- `table` — uppercase faint headers, hairline rows, hover tint.
- `footer` — faint, top-ruled.

> **Custom diagram CSS is yours to keep.** When re-theming an existing doc, swap only the standard
> token *values* and append the aurora override block (below) — don't replace the whole `<style>`,
> or you'll drop per-doc diagram classes/tokens (e.g. architecture docs define their own node colors).

## Full stylesheet

Paste into a `<style>` tag.

```css
:root {
  --bg:#0A0E1A; --panel:rgba(17,24,43,0.66); --panel-2:rgba(26,36,64,0.55); --line:rgba(255,255,255,0.09);
  --text-hi:#F3F4F6; --text:#cdd3e0; --text-mid:#9CA3AF; --faint:#717a8c;
  --accent:#34e3e6; --accent-d:#00E5E8; --blue:#4FACFE; --amber:#FBBF24; --red:#FF4D6D;
  --mono:'Fira Code',ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --sans:'Inter',ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
}
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body {
  margin:0; color:var(--text); font-family:var(--sans); font-size:15px; line-height:1.7;
  -webkit-font-smoothing:antialiased;
  background:
    radial-gradient(900px 520px at 10% -8%, rgba(0,242,254,.10), transparent 60%),
    radial-gradient(820px 480px at 96% -2%, rgba(240,147,251,.08), transparent 55%),
    radial-gradient(700px 600px at 50% 120%, rgba(0,229,232,.06), transparent 60%),
    var(--bg);
  background-attachment:fixed;
}
.wrap { max-width:920px; margin:0 auto; padding:56px 28px 120px; }

header.top { margin-bottom:14px; }
.logo { display:inline-flex; align-items:center; gap:10px; margin-bottom:10px; }
.logo .sq { width:13px; height:13px; border-radius:4px;
  background:linear-gradient(135deg,#00A3A6,#00E5E8); box-shadow:0 0 14px -1px rgba(0,229,232,.85); }
.logo .k { font-family:var(--mono); font-size:12px; color:var(--faint); letter-spacing:.04em; }
h1 { font-family:'Outfit',var(--sans); font-size:32px; line-height:1.18; margin:4px 0 6px; font-weight:700;
  letter-spacing:-.02em; background:linear-gradient(135deg,#4FACFE,#F093FB);
  -webkit-background-clip:text; background-clip:text; color:transparent; }
.lede { color:var(--text-mid); font-size:16px; margin:0 0 8px; }

h2 { font-size:20px; color:var(--text-hi); margin:52px 0 14px; font-weight:620;
  padding-bottom:8px; border-bottom:1px solid var(--line); }
h2 .n { color:var(--accent); font-family:var(--mono); font-size:14px; margin-right:10px; }
h3 { font-size:15px; color:var(--text-hi); margin:26px 0 8px; font-weight:620; }
p { margin:10px 0; }
a { color:var(--accent); text-decoration:none; }
a:hover { color:var(--accent-d); text-decoration:underline; }
strong { color:var(--text-hi); font-weight:620; }
code { font-family:var(--mono); font-size:.86em; color:var(--accent);
  background:var(--panel-2); border:1px solid var(--line); padding:1px 6px; border-radius:5px; }

pre { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:18px 20px; overflow-x:auto; margin:16px 0;
  font-family:var(--mono); font-size:12.5px; line-height:1.55; color:var(--text-mid);
  backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); box-shadow:0 8px 32px rgba(0,0,0,.22); }
pre b { color:var(--accent); font-weight:600; }
pre .c { color:var(--faint); } pre .a { color:var(--accent); } pre .b { color:var(--blue); }

table { width:100%; border-collapse:collapse; margin:16px 0; font-size:13.5px; }
th, td { text-align:left; padding:9px 12px; border-bottom:1px solid var(--line); vertical-align:top; }
th { color:var(--faint); font-weight:600; font-size:11.5px; text-transform:uppercase; letter-spacing:.06em; }
td code { font-size:.9em; }
tbody tr:hover { background:rgba(255,255,255,.02); }

.cards { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:18px 0; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:16px 18px;
  backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); box-shadow:0 8px 32px rgba(0,0,0,.22);
  transition:transform .25s cubic-bezier(.4,0,.2,1), border-color .25s, box-shadow .25s; }
.card:hover { transform:translateY(-4px); border-color:var(--accent); box-shadow:0 12px 40px rgba(0,242,254,.15); }
.card h4 { margin:0 0 6px; font-size:13.5px; color:var(--text-hi); display:flex; align-items:center; gap:8px; }
.card p { margin:4px 0 0; font-size:13px; color:var(--text-mid); }
.pill { font-family:var(--mono); font-size:10.5px; padding:1px 7px; border-radius:20px; border:1px solid var(--line); }
.pill.live { color:var(--accent); border-color:rgba(0,229,232,.4); }
.pill.mock { color:var(--amber); border-color:rgba(251,191,36,.4); }

.phase { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px 18px; margin:12px 0;
  backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); box-shadow:0 8px 32px rgba(0,0,0,.22); }
.phase h3 { margin:0 0 4px; display:flex; align-items:center; gap:10px; }
.phase p { margin:4px 0 0; font-size:13.5px; color:var(--text-mid); }
.tag { font-family:var(--mono); font-size:10.5px; padding:2px 9px; border-radius:20px; border:1px solid var(--line); white-space:nowrap; }
.tag.done { color:var(--accent); border-color:rgba(0,229,232,.45); background:rgba(0,229,232,.08); }
.tag.next { color:var(--amber); border-color:rgba(251,191,36,.45); background:rgba(251,191,36,.08); }
.tag.todo { color:var(--faint); }
.pnum { font-family:var(--mono); color:var(--accent); font-size:13px; }

.note { border-left:3px solid var(--accent); background:var(--panel);
  border-radius:0 12px 12px 0; padding:12px 16px; margin:18px 0; font-size:14px;
  backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); box-shadow:0 8px 32px rgba(0,0,0,.22); }
.note.warn { border-left-color:var(--amber); }
.note.red { border-left-color:var(--red); }
.note .lbl { font-weight:620; color:var(--text-hi); }

ul, ol { margin:10px 0; padding-left:22px; }
li { margin:5px 0; }

.toc { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px 20px; margin:22px 0 0;
  backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); box-shadow:0 8px 32px rgba(0,0,0,.22); }
.toc ol { margin:0; columns:2; column-gap:32px; font-size:13.5px; }
.toc a { color:var(--text-mid); }
.toc a:hover { color:var(--accent-d); }

footer { margin-top:70px; padding-top:18px; border-top:1px solid var(--line); color:var(--faint); font-size:12.5px; }
@media (max-width:680px){ .cards, .toc ol { grid-template-columns:1fr; columns:1; } }
@media (prefers-reduced-motion:reduce){ * { transition:none!important; } }
```

## Starter skeleton

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>TITLE</title>
<style>/* paste the stylesheet above */</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="logo"><span class="sq"></span><span class="k">project-name</span></div>
    <h1>Doc title</h1>
    <p class="lede">One-line summary.</p>
    <div class="toc"><ol>
      <li><a href="#s1">Section one</a></li>
      <li><a href="#s2">Section two</a></li>
    </ol></div>
  </header>

  <h2 id="s1"><span class="n">01</span>Section one</h2>
  <p>Body text with <strong>emphasis</strong> and <code>inline code</code>.</p>

  <div class="note">
    <span class="lbl">Heads-up.</span> A callout. Add class <code>warn</code> for amber, <code>red</code> for a hard constraint.
  </div>

  <h2 id="s2"><span class="n">02</span>Section two</h2>
  <pre><span class="c"># comment</span>
<b>highlighted</b> normal <span class="b">actor</span></pre>

  <table>
    <thead><tr><th>Col</th><th>Col</th></tr></thead>
    <tbody><tr><td><code>x</code></td><td>desc</td></tr></tbody>
  </table>

  <footer>Footer line.</footer>
</div>
</body>
</html>
```

---

**Usage:** copy the skeleton to a new `*.html`, paste the stylesheet, fill sections.
For a quick prompt: *"render this as an HTML doc using the DOC_THEME.md theme."*

**Re-theming an existing doc:** swap the standard token *values* in its `:root` and append the
aurora override block (ambient bg, gradient `h1`, glowing `.logo .sq`, glass blur on
`pre/.toc/.note/.card/.phase`) before `</style>` — preserving any custom diagram CSS.

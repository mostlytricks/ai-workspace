# DOC_THEME — shared HTML doc theme

The workspace theme for **human-facing project HTML docs** (`MISSION.html`, and any
architecture / design page you want rendered in a browser). A dark, professional look:
cool-neutral near-black canvas, muted-teal accent, JetBrains Mono for code. Self-contained,
zero dependencies — copy the skeleton, paste the stylesheet, fill the sections.

`MISSION.template.html` and `ARCHITECTURE.template.html` already ship with this theme inline.
Use this file when you're hand-rolling a *new* HTML doc and want it to match.

> Markdown docs (`CLAUDE.md`, `CONTEXT.md`, `IMPLEMENTATION_PLAN.md`) don't use this — they
> render wherever the agent reads them. The theme is only for browser-read HTML.

---

## Tokens

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0f1413` | page canvas (cool-neutral near-black) |
| `--panel` | `#171d1c` | cards, code blocks, notes |
| `--panel-2` | `#1d2423` | inline-code background |
| `--line` | `#2a3331` | borders, rules |
| `--text-hi` | `#eef2f1` | headings, emphasis |
| `--text` | `#cbd3d1` | body |
| `--text-mid` | `#94a09d` | secondary / lede |
| `--faint` | `#69736f` | captions, code comments |
| `--accent` | `#62a89f` | muted teal — links, numbers, code |
| `--accent-d` | `#4f978e` | accent hover/darker |
| `--blue` | `#7ea6c4` | diagram "actor" highlight |
| `--amber` | `#d9b27a` | warnings, "next" tag |
| `--red` | `#d98c7a` | errors, hard constraints |

Fonts: `--sans` IBM Plex Sans → system-ui fallback · `--mono` JetBrains Mono →
ui-monospace fallback.

## Patterns (class → purpose)

- `.wrap` — 920px centered column, generous padding.
- `header.top` + `.logo .sq` (glowing teal square) + `h1` + `.lede`.
- `h2 > span.n` — teal monospace section number (`01`, `02`, …).
- `.toc` — boxed two-column table of contents.
- `.cards` (2-col grid) → `.card` with `.pill.live` / `.pill.mock` chips.
- `.phase` — roadmap card; `.tag.done` / `.tag.next` / `.tag.todo` status chips, `.pnum` for the phase number.
- `.note` / `.note.warn` / `.note.red` — left-border callout; `.lbl` for the bold lead-in.
- `pre` — code/diagram block; inside it use `<b>` (teal), `.c` (faint comment),
  `.a` (accent), `.b` (blue) spans for ASCII-diagram highlighting.
- `table` — uppercase faint headers, hairline rows, hover tint.
- `footer` — faint, top-ruled.

## Full stylesheet

Paste into a `<style>` tag.

```css
:root {
  --bg:#0f1413; --panel:#171d1c; --panel-2:#1d2423; --line:#2a3331;
  --text-hi:#eef2f1; --text:#cbd3d1; --text-mid:#94a09d; --faint:#69736f;
  --accent:#62a89f; --accent-d:#4f978e; --blue:#7ea6c4; --amber:#d9b27a; --red:#d98c7a;
  --mono:"JetBrains Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --sans:"IBM Plex Sans",system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
}
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; background:var(--bg); color:var(--text);
  font-family:var(--sans); font-size:15px; line-height:1.65; -webkit-font-smoothing:antialiased; }
.wrap { max-width:920px; margin:0 auto; padding:56px 28px 120px; }

header.top { margin-bottom:14px; }
.logo { display:inline-flex; align-items:center; gap:10px; margin-bottom:10px; }
.logo .sq { width:13px; height:13px; border-radius:3px; background:var(--accent);
  box-shadow:0 0 12px rgba(98,168,159,.40); }
.logo .k { font-family:var(--mono); font-size:12px; color:var(--faint); letter-spacing:.04em; }
h1 { font-size:30px; line-height:1.2; margin:4px 0 6px; color:var(--text-hi); font-weight:650; letter-spacing:-.01em; }
.lede { color:var(--text-mid); font-size:16px; margin:0 0 8px; }

h2 { font-size:20px; color:var(--text-hi); margin:52px 0 14px; font-weight:620;
  padding-bottom:8px; border-bottom:1px solid var(--line); }
h2 .n { color:var(--accent); font-family:var(--mono); font-size:14px; margin-right:10px; }
h3 { font-size:15px; color:var(--text-hi); margin:26px 0 8px; font-weight:620; }
p { margin:10px 0; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
strong { color:var(--text-hi); font-weight:620; }
code { font-family:var(--mono); font-size:.86em; color:var(--accent);
  background:var(--panel-2); border:1px solid var(--line); padding:1px 6px; border-radius:5px; }

pre { background:var(--panel); border:1px solid var(--line); border-radius:10px;
  padding:18px 20px; overflow-x:auto; margin:16px 0;
  font-family:var(--mono); font-size:12.5px; line-height:1.55; color:var(--text-mid); }
pre b { color:var(--accent); font-weight:600; }
pre .c { color:var(--faint); } pre .a { color:var(--accent); } pre .b { color:var(--blue); }

table { width:100%; border-collapse:collapse; margin:16px 0; font-size:13.5px; }
th, td { text-align:left; padding:9px 12px; border-bottom:1px solid var(--line); vertical-align:top; }
th { color:var(--faint); font-weight:600; font-size:11.5px; text-transform:uppercase; letter-spacing:.06em; }
td code { font-size:.9em; }
tbody tr:hover { background:rgba(255,255,255,.014); }

.cards { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:18px 0; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:16px 18px; }
.card h4 { margin:0 0 6px; font-size:13.5px; color:var(--text-hi); display:flex; align-items:center; gap:8px; }
.card p { margin:4px 0 0; font-size:13px; color:var(--text-mid); }
.pill { font-family:var(--mono); font-size:10.5px; padding:1px 7px; border-radius:20px; border:1px solid var(--line); }
.pill.live { color:var(--accent); border-color:rgba(98,168,159,.4); }
.pill.mock { color:var(--amber); border-color:rgba(217,178,122,.35); }

.phase { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px 18px; margin:12px 0; }
.phase h3 { margin:0 0 4px; display:flex; align-items:center; gap:10px; }
.phase p { margin:4px 0 0; font-size:13.5px; color:var(--text-mid); }
.tag { font-family:var(--mono); font-size:10.5px; padding:2px 9px; border-radius:20px; border:1px solid var(--line); white-space:nowrap; }
.tag.done { color:var(--accent); border-color:rgba(98,168,159,.45); background:rgba(98,168,159,.08); }
.tag.next { color:var(--amber); border-color:rgba(217,178,122,.45); background:rgba(217,178,122,.08); }
.tag.todo { color:var(--faint); }
.pnum { font-family:var(--mono); color:var(--accent); font-size:13px; }

.note { border-left:3px solid var(--accent); background:var(--panel);
  border-radius:0 8px 8px 0; padding:12px 16px; margin:18px 0; font-size:14px; }
.note.warn { border-left-color:var(--amber); }
.note.red { border-left-color:var(--red); }
.note .lbl { font-weight:620; color:var(--text-hi); }

ul, ol { margin:10px 0; padding-left:22px; }
li { margin:5px 0; }

.toc { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px 20px; margin:22px 0 0; }
.toc ol { margin:0; columns:2; column-gap:32px; font-size:13.5px; }
.toc a { color:var(--text-mid); }
.toc a:hover { color:var(--accent); }

footer { margin-top:70px; padding-top:18px; border-top:1px solid var(--line); color:var(--faint); font-size:12.5px; }
@media (max-width:680px){ .cards, .toc ol { grid-template-columns:1fr; columns:1; } }
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

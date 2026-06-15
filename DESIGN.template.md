# Design

<!-- Per-project stencil for a running-app UI design system. Copy to <project>/DESIGN.md and fill.
     This is the canonical home for *app visual design* (workspace CLAUDE.md §6 ownership table):
     temperature, type, token contract, motion, components, the lines you must not cross.
     NOT the same as DOC_THEME.md (browser-read HTML-doc theme) — if a project needs both, the
     doc theme stays in DOC_THEME.md / a DESIGN.docs.md, and this file owns only the app.
     Delete sections that don't apply; keep the ones that protect identity. -->

A guide for anyone (human or agent) touching the UI of this project. The aesthetic is
intentional. This document says which parts are **load-bearing identity** vs which are
**incidental** and safe to change — so a redesign doesn't quietly erase the personality.

---

## Philosophy

<!-- The 2-4 principles, in priority order, that every UI decision should answer to.
     Make them falsifiable — "warm over cool, no corporate blue" beats "clean and modern".
     This section is what stops an agent from defaulting to generic AI aesthetics. -->

The product is a **<one-line metaphor — e.g. "reading room, not a dashboard">**. Principles, in order:

1. **<Principle one>** — what it means concretely.
2. **<Principle two>** — what it means concretely.
3. **<Principle three>** — what it means concretely.

---

## Typography (load-bearing — keep)

<!-- The font pairing is usually the single most distinctive thing about a UI. Name the exact
     families, their roles, and where the CSS variables are defined. List what's forbidden. -->

| Role | Font | Notes |
|---|---|---|
| Display / headers | **<font>** | axes, sizes, italic usage |
| Body / reading | **<font>** | size / line-height |
| Mono / utility | **<font>** | code, labels, hints — never body |

CSS variables (define once, in `<path to global stylesheet>`):

```css
--font-display: '<font>', <fallbacks>;
--font-body:    '<font>', <fallbacks>;
--font-mono:    '<font>', <fallbacks>;
```

**Forbidden:** <the AI-default fonts this project rejects — e.g. Inter, system-ui, Space Grotesk as primary>.

---

## Color (load-bearing — keep the policy)

<!-- The token contract is the heart of the doc. State the themes, then EVERY token: what it
     encodes and where it's allowed. The rule that pays off later: every color in a component
     comes from a token — literal hex is a bug except for a short, named carve-out list. -->

Themes: `<.theme-x (default)>`, `<.theme-y>`, … — all defined as CSS variables in `<path>`.

**Every `background`, `color`, `border-color`, `fill`/`stroke` MUST come from a token.**
Literal hex / `rgba(...)` is tolerated only in these named carve-outs: <list them, or "none">.

### Naming convention

<!-- A predictable suffix scheme keeps the palette from sprawling. Adapt or replace. -->

| Suffix | Meaning | Example |
|---|---|---|
| *(none)* | base role at canonical strength | `--accent`, `--ink` |
| `-soft` | low-alpha tint, **backgrounds only** | `--accent-soft` |
| `-strong` | higher-contrast variant (hover/active) | `--accent-strong` |

### The token contract

<!-- One row per token. Group by concern (surfaces / text / borders / accent / data-viz / utility).
     The "Allowed on" column is the source of truth for which token goes where. -->

| Token | Encodes | Allowed on |
|---|---|---|
| `--bg` | … | … |
| `--surface` | … | … |
| `--ink` | … | … |
| `--accent` | … | … |

### Accent policy

<!-- How many accents? Where does a solid accent block belong (usually one reserved role)?
     Is there stoplight/status semantics, and if so what's the fixed mapping? -->

- <e.g. "One accent per theme. Accent goes on small things; solid accent block is reserved for the one primary action.">
- <status → token mapping, if the UI encodes state in color>

### Forbidden (AI-slop palette signatures)

- Corporate-blue family (`#3B82F6`, `#2563EB`), purple→pink gradients on white, neon-saturated accents.
- Pure `#fff` / `#000` as ground (except a named carve-out), solid grey borders, stoplight red/yellow/green for state.
- <project-specific ones>

### Adding a new color

1. Can it reuse an existing token? Shared role ⇒ shared token.
2. Is it a variant of an existing hue? Use `-soft` / `-strong`.
3. New utility role? Name it for the role, not the hue (`--ring`, not `--gold-focus`).
4. Define it in **every** theme — a token that exists in only one theme is a bug.

---

## Atmosphere (optional — keep if present)

<!-- Passive depth layers (gradient washes, noise grain, paper texture) that make the app feel
     like a place rather than a flat canvas. Delete this section if the project is flat-by-design. -->

<describe the background layers and how they're applied, or delete>

---

## Motion (keep the curve, timings flexible)

<!-- One easing curve, a small timing scale, and a short forbidden list. Consistency reads as craft. -->

Easing: `<cubic-bezier(...)>` for everything. Timing scale:

| Use | Duration |
|---|---|
| hover color/bg | <ms> |
| panel/modal appear | <ms> |
| page transition | <ms> |

**Forbidden:** bouncy/spring/overshoot easing, continuous spinners, animating `box-shadow` on hover, color-flash attention-grabbing.

---

## Components

<!-- Per-component notes only where the component carries identity or a non-obvious rule.
     Point at the source file. Don't document every div. -->

### <ComponentName> (`<path>`)

- <the load-bearing decisions: dimensions, ornament, the thing not to "fix">

---

## What's safe to change vs identity

**Flavor (safe to change):** <hex tweaks within the palette, radii, timings within range, glyphs, copy>.

**Identity (do not change):** <the font pairing, the temperature, the signature ornament, the easing curve, accent policy>.

---

## Adding new UI — checklist

1. **Variables, not literals.** Every color/font/reusable spacing comes from a `--token`; new token ⇒ add to every theme first.
2. **Match the existing patterns.** New surfaces, borders, accents, type all inherit existing roles.
3. **Test in every theme.** Each should look intentional, not "the other one inverted."
4. **Motion is opt-in.** Animate only entry / focus / state change.
5. **Read the copy aloud.** If it doesn't sound like a real person, rewrite it.

---

## Anti-patterns (throw it out and restart if you see these)

- Purple→pink gradient on a white rounded-2xl card.
- Inter / system-ui with shadcn-default everything; saturated blue primary button.
- Pill-block highlighted sidebar items (if this project uses color-shift instead).
- Bento-grid + emoji icons; centered "Welcome to your dashboard" hero.
- <project-specific slop signatures>

<!--
This file is stable identity — it changes on real redesigns, not per session.
It owns *app visual design*; the browser-read HTML-doc theme is DOC_THEME.md's concern. One concern, one home.
-->

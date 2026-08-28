# Alice's Adventures in Wonderland — Build Documentation

## Content

- **Author**: Lewis Carroll (1865)
- **Source**: Project Gutenberg
- **Chapters**: 12
- **Content embedded** directly in each HTML reader as JS constants (no external seeds/ JSON)

## Reader Formats

| File | Format | Description |
|------|--------|-------------|
| `reader.html` | Scrolling | Sidebar TOC, progress bar, 5 themes, half-sun theme toggle, settings panel |
| `fullbleed.html` | Two-page spread | 3D page flip, cover, title page, TOC, running headers, chapter scrubber |
| `mobile.html` | Mobile-first | Swipe navigation, single-page |
| `scroll.html` | Minimal scroll | Simple continuous scroll |
| `single.html` | Single-page | Paginated single page |
| `web-reader.html` | Web reader | Browser-style reader |
| `pdf-reader.html` | PDF-style | PDF viewer simulation |
| `theater.html` | Theater mode | Immersive reading |
| `index.html` | Two-page book | Classic open-book spread with page flips, chapter `<select>`, cover mode. Not a landing page — it contains no links to the other formats |

## Primary Readers (actively maintained)

### reader.html
- **Layout**: Single scrolling page with chapter sidebar
- **Themes**: 5 themes via `html[data-theme]` — light-purple (default), sepia, light-azure, dark-violet, dark-blue
- **Theme toggle**: Half-sun SVG icon + dot picker
- **Theme dots**: No borders, solid fill, active ring via `box-shadow`
- **Fonts**: EB Garamond (body), Jost (UI), IBM Plex Mono (meta)
- **Typography**: `text-align: justify`, `text-indent: 1.5em`, `line-height: 1.85`
- **Settings**: Font family, size, width controls
- **Navigation**: Sidebar TOC, progress bar, keyboard (j/k/arrows/space)
- **Preferences**: localStorage `alice-reader-prefs`

### fullbleed.html
- **Layout**: Two-page book spread with 3D page flip animations
- **Spread structure**:
  - Spread 0: Cover (theme-matched background, theme picker visible)
  - Spread 1: blank left, title page right
  - Spread 2: blank left, TOC right
  - Spread 3+: content pages (even indices = right/recto, odd = left/verso)
- **Themes**: 5 themes via `html[data-theme]` — same as reader.html
- **Theme toggle**: Half-sun SVG + dot picker in footer
- **Accent usage**: Drop caps, chapter numbers, ornaments, page numbers, TOC numbers all use `var(--accent)` at varying opacities
- **Running headers**: Inside each `.page-content` div (not fixed overlay), toggled via `.visible` class
  - Blank pages: no header
  - Chapter-start pages: no header (shows book title in chapter header instead)
  - Normal pages: book title (italic) + chapter title
- **Chapter headers**: Book title (subtle italic) + "CHAPTER N" + chapter title + ornament
- **Chapter starts**: Always on recto (right page) — `ensureRectoChapterStarts()` inserts blank pages
- **Page numbers**: Outer corners (left page = left, right page = right), accent-tinted
- **Footer**: Gradient background (transparent → paper color), contains nav arrows, editable page number, chapter scrubber (roman numerals with hover tooltips), theme toggle
- **Editable page number**: Click to edit, Enter to jump, Escape/blur to cancel
- **Chapter scrubber**: Roman numerals I–XII, `::after` tooltips with chapter titles
- **Pagination**: Greedy block-fitting into viewport-height pages
- **Content mapping**:
  - `contentIndexForSpreadLeft(s) = 2*s - 7` (for s >= 3)
  - `contentIndexForSpreadRight(s) = 2*s - 6` (for s >= 3)
- **Flip animation**: CSS 3D transforms, `perspective: 1800px`, configurable duration/easing

## Typography

- **Body**: EB Garamond, 17px, line-height 1.65 (fullbleed) / 1.85 (reader)
- **Drop caps**: `::first-letter`, 3.5em, accent color
- **Chapter titles**: 26px, weight 600, `var(--ch-title)` color
- **Chapter numbers**: Jost 12px, uppercase, 3px letter-spacing, accent color
- **Running headers**: EB Garamond 12px, 55% opacity
- **Page numbers**: Jost 13px, accent color at 35% opacity

## Theme Variables

Each theme defines:
```
--bg-left, --bg-right        (page backgrounds)
--text, --text-muted          (text colors)
--spine, --shadow-left/right  (book spine effects)
--accent, --border            (interactive elements)
--drop-cap-color, --ch-title  (typography accents)
--control-bg, --control-border (footer/controls)
```

## Build Scripts

### gen_mobile.py — generates `mobile.html`

`mobile.html` is the **only generated file** in this book; the other eight readers are
hand-written and edited directly.

```bash
python3 gen_mobile.py        # run from alice-in-wonderland/, writes ./mobile.html
```

The whole page lives in the `TEMPLATE` string inside `gen_mobile.py` — **edit the template,
never `mobile.html`**, then re-run the script.

**Source data**: the script reads `/tmp/alice_chapters.json`, which is *not* in the repo (Alice
has no `seeds/` directory — every reader embeds its own copy of the chapters). If that file is
missing, regenerate it from the chapter array already embedded in `mobile.html`:

```python
import json, importlib.util
src = open('mobile.html', encoding='utf-8').read()
spec = importlib.util.spec_from_file_location('gm', 'gen_mobile.py')
gm = importlib.util.module_from_spec(spec); spec.loader.exec_module(gm)
pre, post = gm.TEMPLATE.split('__CHAPTERS_JSON__')
payload = src[len(pre):len(src) - len(post)]          # the embedded JSON array
open('/tmp/alice_chapters.json', 'w', encoding='utf-8').write(payload)
```

Schema: `[{"num": 1, "title": "...", "html": "<p>…</p>"}, …]` — 12 chapters.
Round-tripping is byte-exact: rebuilding an unmodified template reproduces `mobile.html` exactly.

## Themes and Preferences (all nine readers)

- 5 themes via `data-theme` on `<html>`: `light-purple` (default), `sepia`, `light-azure`,
  `dark-violet`, `dark-blue`. `theater.html` defaults to `dark-violet` (immersive dark stage) and
  `pdf-reader.html` keeps its grey viewer chrome around a theme-tinted page.
  `web-reader.html` still uses its own four-name set (`light`/`sepia`/`dark`/`black`).
- Preferences (theme, font, size, zoom) in localStorage, one book-prefixed key per format:
  `alice-reader-prefs`, `alice-fullbleed-prefs`, `alice-mobile-prefs`, `alice-scroll-prefs`,
  `alice-single-prefs`, `alice-theater-prefs`, `alice-index-prefs`, `alice-pdf-prefs`,
  `alice-web-reader-prefs`. The old unprefixed keys (`fullbleed-theme`, `webreader-prefs`) are
  still read once as a fallback so returning readers keep their settings.
- **Reading position lives in the URL hash, never localStorage** — `#ch-N` (reader),
  `#p-N` / `#s-N` (fullbleed), `#s-N` (theater segments).

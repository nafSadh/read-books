# Meditations — Read-Book Project

Build readers for Marcus Aurelius' "Meditations", following the same patterns as
`../alice-in-wonderland/`. All HTML files are self-contained (no external JS/CSS
beyond Google Fonts).

## Content

- **Author**: Marcus Aurelius (121-180 CE), Roman Emperor
- **Written**: c. 170-180 CE, in Koine Greek
- **English translation in readers**: Meric Casaubon (1634), public domain (Project Gutenberg #2680)
- **Greek text**: Perseus Digital Library, Leopold edition (CC BY-SA 4.0)
- **Structure**: 12 Books, ~400+ meditations/passages
- **Content embedding**: Full text embedded directly in HTML (no external JSON)

## Reader formats

### 1. `reader.html` (scrolling reader — Long translation)

Built by `data/assemble-reader.py` from `aurelius-meditations.json` + `reader-casaubon.html` template.
- George Long (1862) translation, Leopold numbering (486 passages)
- All 486 passages annotated: modern English rewrite, notes, proper noun tooltips
- Greek text toggle ("Αα" button): shows original Greek alongside English
- 5 themes, font/size/width controls, sidebar, keyboard shortcuts
- localStorage key: `meditations-reader-prefs`

**Layout modes**:
- Default: English text only (single column)
- Greek on: English + Greek side-by-side (60%/40%, flex row-reverse — Greek uses `order: -1`)
- Detail open: Detail panel (left, 50%) + English (right, 50%); the passage widens via
  `--_grow` and is viewport-capped with `min()`
- Both open: 2-column grid `minmax(0,50%) minmax(0,1fr)` — Detail spans both rows in column 1,
  English sits in column 2 row 1, Greek is **stacked below English** in column 2 row 2
  (rule-separated by a `border-top`, not a third column)
- Mobile (<1200px): all columns stack vertically

**Reading position**: written to the URL hash as `#ch-N` via `history.replaceState` from the
chapter `IntersectionObserver`, restored on load (`.chapter` carries `scroll-margin-top: 56px`
so the native fragment jump clears the fixed top bar). Never stored in localStorage.

**Rebuild**: `python3 data/assemble-reader.py` (reads JSON + template, outputs reader.html)

### 1b. `reader-casaubon.html` (scrolling reader — Casaubon translation)

Original Casaubon (1634) reader preserved as-is. localStorage key: `meditations-casaubon-prefs`.

> **This file is also the template for `reader.html`.** Edit it, never `reader.html`, and always
> re-run `python3 data/assemble-reader.py` afterwards, then re-check *both* readers.

### 2. `fullbleed.html` (book-spread reader)

Follows `../alice-in-wonderland/fullbleed.html` pattern:
- CHAPTERS array in JS (12 entries, one per Book)
- Pagination engine with hidden measure div
- 3D page flip animation, mobile single-page fallback
- Cover, title page, table of contents
- 5 themes with sepia default
- localStorage key: `meditations-fullbleed-theme`
- Reading position in the URL hash as `#p-N` (printed page number) via `history.replaceState`,
  restored on load through `spreadForPage()` — the inverse of
  `contentIndexForSpreadLeft/Right` (left = `2s-7`, right = `2s-6`)

### 3. `mobile.html`, `theater.html`, `pdf-reader.html` (JS-rendered)

Added after the audit; all three render **one passage at a time** from a JSON payload rather than
baking the book into the DOM the way `assemble-reader.py` does. `data/payload.py` is the single
place that knows how to read the source JSON and shape a passage; the three builders are thin.

| | mobile | theater | pdf-reader |
|---|---|---|---|
| Shape | one passage per screen | dark stage, one passage | one passage per page card |
| Default theme | light-purple | **dark-violet** | light-purple |
| Prefs key | `meditations-mobile-prefs` | `meditations-theater-prefs` | `meditations-pdf-prefs` |
| Prefs hold | theme, greek, detail | theme, greek | theme, zoom, greek |
| Chrome | bottom sheets (books, theme) | auto-hiding control bar | toolbar + passage sidebar |

**Position is `#m-B.N`** in all three — the passage's own Leopold id, not an ordinal. Unlike
`fullbleed.html`'s `#p-N`, which depends on how many passages fit a given viewport, this link
resolves to the same meditation on any screen.

Greek and the annotation apparatus are **toggles, not columns**: at one passage per screen there
is no room to set them side by side the way `reader.html` does.

Rebuild: `python3 data/build_mobile.py` / `build_theater.py` / `build_pdf.py`.

Two traps worth keeping:

- `#toolbar > button` in the PDF template is a **child** selector on purpose. As a descendant
  selector the toolbar's `min-width` also applied to the theme dots nested in `#themeDots`,
  inflating that row past a phone viewport.
- The PDF sidebar is hidden with `visibility:hidden` as well as `transform`, so its 486
  thumbnails leave the tab order when the drawer is closed. Transform alone left them all
  focusable — the same class of problem as the Greek-word `tabindex` sweep.

## Typography

| Property       | Value |
|----------------|-------|
| text-align     | left / ragged right in the scrolling readers; `justify` + `hyphens: auto` in `fullbleed.html` |
| text-indent    | 0 (meditations are short, no indent needed) |
| line-height    | 1.85 |
| default width  | 640px |
| font-body      | EB Garamond |

The scrolling readers deliberately depart from the house "prose = justify" rule: most Leopold
passages are one- to three-line aphorisms, and justifying them strands large gaps between words
on the first line. `fullbleed.html` sets full-measure book pages, so it justifies as usual.

## Theme variables

5 themes: `light-azure`, `light-purple` (default), `sepia`, `dark-violet`, `dark-blue`.
Sepia theme uses warm parchment tones (`--bg: #f5efe0`, `--accent: #8b6914`).

## Data sources

| Source | Edition | License | Passages |
|--------|---------|---------|----------|
| Greek | Leopold (1908), Perseus DL | CC BY-SA 4.0 | 486 |
| English | George Long, 1862 | Public domain (Gutenberg #2680) / CC0 (Standard Ebooks) | 522 |
| English | Meric Casaubon, 1634 | Public domain (Gutenberg #2680) | 412 |

Greek text from `PerseusDL/canonical-greekLit` on GitHub.
Long translation from `standardebooks/marcus-aurelius_meditations_george-long`.
Section numbering differs across all three editions; Greek (Leopold) is canonical.

## Text collection pipeline

`data/collect_texts.py` fetches and aligns all three translations:
- Caches in `/tmp/meditations_texts_cache/`
- Greek passage numbers as canonical IDs
- Long matched by number (484/486 aligned); Casaubon stored separately
- Long stored as arrays per Greek passage (over-splits folded)
- Casaubon entries include reverse mapping (`leopold_ids`, `confidence`)
- Loads Leopold annotations from `data/annotations/leopold-books-*.json`
- Outputs `aurelius-meditations.json` (canonical) + `data/texts/meditations-complete.md`
- Run: `python3 data/collect_texts.py` (stdlib only, no pip deps)

`data/align_casaubon_long.py` builds Casaubon↔Long passage mapping:
- Text similarity: proper noun overlap (3x weight) + word cosine
- Monotonicity constraint preserves ordering; handles 1:many mappings
- Confidence levels: high (strong noun+word overlap), medium, low (needs manual review)
- Output: `data/texts/casaubon-long-alignment.json` (56 KB, 412 mappings)
- Run: `python3 data/align_casaubon_long.py [--verbose]`

## File inventory

```
aurelius-meditations/
  CLAUDE.md              <- this file
  .project/
    changelog.md         <- session log
    todo.md              <- task tracking
    agents-log.md        <- annotation agent history
  aurelius-meditations.json <- canonical data: 486 passages (Greek + Long + Casaubon + annotations)
  index.html             <- book-spread landing page
  reader.html            <- scrolling reader (Long translation, Leopold numbering)
  reader-casaubon.html   <- scrolling reader (Casaubon translation, original 412 passages)
  fullbleed.html         <- book-spread reader (full text)
  mobile.html            <- GENERATED: one passage per screen
  theater.html           <- GENERATED: dark stage, one passage at a time
  pdf-reader.html        <- GENERATED: PDF-viewer shell, one passage per page
  data/
    annotations/         <- JSON annotation data
      leopold-books-01-03.json  <- Books 1-3 Leopold annotations (50 passages)
      leopold-books-04-06.json  <- Books 4-6 Leopold annotations (146 passages)
      leopold-books-07-09.json  <- Books 7-9 Leopold annotations (178 passages)
      leopold-books-10-12.json  <- Books 10-12 Leopold annotations (112 passages)
      book-01-remaining.json .. book-12.json  <- legacy Casaubon-era annotations
    assemble-reader.py   <- builds reader.html from JSON + template (Long + Greek toggle)
    payload.py           <- shared: source JSON -> JSON payload for the 3 JS-rendered formats
    build_mobile.py      <- builds mobile.html
    build_theater.py     <- builds theater.html
    build_pdf.py         <- builds pdf-reader.html
    mobile-template.html , theater-template.html , pdf-template.html  <- __DATA__ placeholder
    assemble-annotations.js  <- Node.js assembler (original, Casaubon)
    assemble-annotations.py  <- Python assembler (Casaubon injection)
    collect_texts.py     <- fetches Greek + Long + Casaubon, merges annotations → aurelius-meditations.json
    align_casaubon_long.py <- Casaubon↔Long passage alignment mapping
    texts/               <- output: combined MD + alignment JSON
  hammond/               <- (gitignored) Martin Hammond (Penguin 2006) extraction
    extract_hammond.py   <- PDF text extraction script (pymupdf)
    hammond-meditations.json <- extracted passages (479/486)
```

# The Iliad — Read-Book Project

Build readers for Homer's *Iliad*, following the same patterns as
`../khayyam-rubaiyat/` (parallel-translation switcher, build-time static
generation) and `../gibran-prophet/` (poetry typography, full reader-format
lineup: index, reader, fullbleed, mobile, theater, pdf-reader). All HTML
files are self-contained (no external JS/CSS beyond Google Fonts).

## Content

- **Author**: Homer (attributed), composed ~8th century BCE
- **Structure**: 24 books, traditional division (present in every translation below)
- **Translations rendered** (all public domain; all three translators did *both* Iliad and Odyssey):
  - **Samuel Butler** (1835–1902) — prose, 1898. Project Gutenberg #2199.
  - **Alexander Pope** (1688–1744) — heroic-couplet verse, 1715–1720. Project Gutenberg #6130.
  - **William Cowper** (1731–1800) — blank verse, 1791. Project Gutenberg #16452.

Three translations, not five: unlike the Rubáiyát (many independent
renderings of the *same* short quatrain), a full 24-book epic in three
genuinely different registers (prose / rhymed verse / blank verse) is
already a large payload. Butler+Pope+Cowper covers prose vs. rhymed vs.
blank verse, and conveniently all three translators also did the Odyssey,
so `../homer-odyssey/` shares the same switcher labels and mechanics.

## Directory layout

```
homer-iliad/
  CLAUDE.md              <- this file
  seeds/
    butler.json           <- Butler prose, parsed from PG #2199
    pope.json              <- Pope verse, parsed from PG #6130
    cowper.json             <- Cowper blank verse, parsed from PG #16452
  data/
    build.py                <- builds ALL 5 variants from seeds/*.json
    reader-template.html    <- scrolling reader shell (CSS+JS+__CONTENT__)
    theater-template.html   <- cinematic one-book-at-a-time shell
    mobile-template.html    <- mobile pager shell
    fullbleed-template.html <- two-page spread shell
    pdf-template.html       <- PDF-viewer-style shell
  index.html              <- book landing page
  reader.html             <- GENERATED: scrolling reader, translation switcher
  theater.html            <- GENERATED: cinematic reader
  mobile.html             <- GENERATED: mobile-first reader
  fullbleed.html          <- GENERATED: two-page spread reader
  pdf-reader.html         <- GENERATED: Chrome-PDF-viewer-style reader
```

## Data schema

Each `seeds/{translator}.json`:

```json
{
  "translator": "Samuel Butler",
  "translator_years": "1835-1902",
  "publication_year": 1898,
  "form": "prose",
  "source": "Project Gutenberg #2199",
  "source_url": "https://www.gutenberg.org/ebooks/2199",
  "epic": "iliad",
  "book_count": 24,
  "books": [
    {
      "num": 1,
      "roman": "I",
      "argument": "The quarrel between Agamemnon and Achilles...",
      "paragraphs": ["Sing, O goddess, the anger of Achilles...", "..."]
    }
  ]
}
```

Verse translations (`pope.json`, `cowper.json`) use `"lines": [...]` (one
verse line per array entry) instead of `"paragraphs"`. `"argument"` is the
translator's own prose book-summary where present (Butler and Pope both
include one; Cowper's is often 2 paragraphs joined with `\n\n`); may be
`null`. Gutenberg's `_word_` italic-emphasis convention (mainly present in
Cowper) is converted to `<em>` at render time, not in the seed JSON.

## Architecture — READ THIS BEFORE ADDING A 4TH TRANSLATION OR A NEW VARIANT

**Every variant renders ONE book at a time client-side. None of them
pre-render all 24 books (or all 3 translations) into the DOM simultaneously.**

This is not a stylistic choice — it's a fix for a real bug found during
development. The first version of `reader.html` followed the Rubáiyát
pattern exactly: all 3 translations × 24 books pre-rendered as static HTML
in the DOM at once (toggling `display` per translation, like
`khayyam-rubaiyat/reader.html`'s edition switch). That works for the
Rubáiyát because even 5 translations × ~500 quatrains is a few thousand
lines. A full Iliad translation is ~15,000–19,000 verse lines / ~800
paragraphs — pre-rendering all three at once produced a single continuous
page **several million pixels tall**. Deep-linking to a specific book (a
core feature — `#bk-butler-24`) or any large scroll jump caused the page to
fail to paint (confirmed via direct DOM/console inspection, not just a
testing artifact). This is the same order of magnitude as `../vedas/`'s
complete Rigveda (10,143 mantras), which is why `vedas/rigveda.html` already
uses a lazy-loading architecture instead of Prophet/Rubáiyát's "embed
everything" pattern.

The fix, used identically across all 5 variants here:

1. `build.py` embeds the full seed data as one `const EDITIONS = {...}`
   JSON object (via `data/build.py`'s `build_content()`), substituted for
   `__CONTENT__` in each template — this is just data, not DOM.
2. Client-side JS has a `render()`/`loadBook()` function that builds the DOM
   for **only the current book** (one `.chapter`/`.book-view`/page-set worth
   of `<p>` tags — tens to a few hundred elements) and replaces the
   previous book's content wholesale when the reader navigates.
3. Book-to-book navigation (sidebar, scrubber, prev/next, hash) always goes
   through this re-render path — never appends more books to the DOM.

If you add a 4th translation or a new reader variant, keep this invariant.
Do not go back to "all books inline, toggle visibility."

### Pagination (fullbleed.html, pdf-reader.html)

These two need to split a book's content into "pages." The **first**
implementation measured each paragraph's rendered height in a hidden sandbox
div and bin-packed paragraphs into fixed-height pages — this is wrong for
Butler's prose, whose paragraphs can be 1000+ characters (some single
paragraphs are taller than a whole page), causing `overflow: hidden` to
silently clip content. **Do not reintroduce this.**

The current approach uses **native CSS multi-column layout** instead:
content flows into a `columns: <width>` container with an explicit `height`
and `column-gap`; the browser handles line-wrapping and mid-paragraph splits
across "pages" (columns) natively, the same way a real print layout engine
would. Page count is derived after layout via
`Math.round(pageset.scrollWidth / COL_STEP)`, where `COL_STEP =
column-width + column-gap`. "Turning a page" moves `margin-left` (not
`transform: translateX`, which had a visible clipping bug against the
viewport's `overflow: hidden` in some renders — margin-based layout shifts
clip reliably in all browsers) by exactly `COL_STEP`.

**Important invariant**: `COL_STEP` must equal the viewport's own width (620px
single-page in `pdf-reader.html`, 920px per spread in `fullbleed.html`).
If `column-gap` is too small (a real bug found and fixed here — it was
originally `0` in `pdf-reader.html`), the next (hidden) column starts
*inside* the visible viewport instead of past its right edge, and its text
visibly bleeds through. Keep `column-gap >= (viewport width − padding×2 −
column-width)` with margin to spare; both templates use `column-gap: 80`
today, which clears the edge by 40px.

## Typography

Per-edition, driven by a `prose`/`` class toggle set at render time (see
`AGENT_README.md`'s prose/poetry table):

| | Butler (prose) | Pope / Cowper (verse) |
|---|---|---|
| text-align | justify | left |
| text-indent | 1.5em (drop cap on book's first paragraph) | 0 |
| line-height | 1.85–2.0 | 2.0 |
| unit rendered | `<p>` per paragraph | `<p>` per verse line |

Content width: 620px in reader.html (wider than Prophet/Rubáiyát's 560px —
Pope's couplets run long and wrap awkwardly narrower).

## Themes

5 themes, consistent with the rest of lib.sadh.app:
`light-purple` (default), `sepia`, `light-azure`, `dark-violet` (default in
theater.html, matching Prophet), `dark-blue`.

## UI per variant

- **reader.html** — scrolling reader. Sidebar + 24-segment progress bar +
  scrubber (all book-jump, not scroll-position-based). Translation switch:
  Butler ↔ Pope ↔ Cowper tabs, all re-rendering the current book. Settings
  panel (font/size/width). Prev/Next book nav at the foot of each book.
- **theater.html** — cinematic, dark-violet default, auto-hiding controls,
  click-stage-to-advance (advances to the *next book*, not next paragraph —
  a "chapter" here is a whole book), swipe, keyboard.
- **mobile.html** — persistent (non-auto-hiding) top/bottom bars, book-list
  and theme bottom sheets, swipe between books, viewport-fit=cover meta tags.
- **fullbleed.html** — two-page spread via CSS columns (see Pagination
  above), edge click-zones + swipe + arrow keys to turn pages, Prev/Next
  Book buttons cross book boundaries.
- **pdf-reader.html** — Chrome-PDF-viewer-style single-page view, dark
  toolbar, book `<select>` dropdown (24 books), page-number input, same
  CSS-column pagination as fullbleed but 1 column per viewport instead of 2.

localStorage keys: `iliad-reader-prefs`, `iliad-theater-theme` /
`-book` / `-edition`, `iliad-mobile-prefs`, `iliad-fullbleed-prefs`,
`iliad-pdf-prefs`. Reading position is also always mirrored to the URL hash
(`#bk-N` current translation, `#bk-<butler|pope|cowper>-N` explicit) per
`AGENT_README.md`'s convention — this is what all the hash-restore code in
each template parses on load.

## Build

```
python3 data/build.py    # seeds/*.json -> all 5 *.html variants
```

Idempotent, skips any template file that doesn't exist yet (so partial
variant sets still build). Never hand-edit the generated `*.html` files —
edit `data/*-template.html` (shell/CSS/JS) or the `seeds/*.json` (text) and
rebuild.

## Known caveat

The CSS-column pagination in `fullbleed.html`/`pdf-reader.html` was verified
correct via DOM/textContent inspection and screenshots taken in this
project's sandboxed preview browser. If you see any text bleeding past a
page/spread edge in a *real* deployed browser, re-check the `column-gap` /
`COL_STEP` invariant above before assuming it's environmental — that
exact symptom was a real bug here once already (see Pagination section).

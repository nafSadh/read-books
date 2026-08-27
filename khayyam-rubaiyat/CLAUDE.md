# Rubáiyát of Omar Khayyám — Read-Book Project

Five parallel editions of the Rubáiyát rendered as self-contained HTML readers.
Poetry typography throughout (same decisions as `../gibran-prophet/`). Every
built page is a single file with no external JS/CSS beyond Google Fonts.

**This book is generated.** `reader.html`, `fullbleed.html` and `theater.html`
are build products — edit the templates under `data/` and re-run the build,
never the built file.

## Content

- **Author**: Omar Khayyám (1048–1131 CE), Persian polymath
- **Editions rendered**: five, switchable in every reader

| Key | Edition | Year | Count | Form |
|-----|---------|------|-------|------|
| `first` | FitzGerald, 1st edition | 1859 | 75 | English verse |
| `fifth` | FitzGerald, 5th edition **(default)** | 1889 | 101 | English verse, + Heron-Allen 1898 notes |
| `whinfield` | E. H. Whinfield | 1883 | 500 | English verse (literal), + MS refs |
| `nicolas` | Nicolas 1867 → English prose (Arnot) | 1903 | 464 | English prose |
| `persian` | Foroughi & Ghani, Persian original | 1960 | 178 | Persian (RTL), + transliteration |

1318 quatrains in all.

- **Source (English)**: Project Gutenberg (FitzGerald #246; Whinfield; Nicolas/Arnot)
- **Source (Persian)**: fa.wikisource (CC BY-SA 4.0)
- **Heron-Allen 1898**: scholarly Persian-source analysis, keyed to FG 5th
- Modern literal / poetic renderings, theme tags and notes on the Persian
  quatrains are **machine-generated** (Claude, Anthropic) and are always
  labelled as such in the UI.

## Directory layout

```
khayyam-rubaiyat/
  CLAUDE.md                    <- this file
  .project/
    todo.md                    <- task tracking
    changelog.md               <- session log
  seeds/                       <- source data, one file per edition
    fitzgerald.json            <- FG 1st + 5th
    whinfield.json             <- Whinfield 1883 (500) + ms_refs/note
    nicolas-english.json       <- Nicolas → English prose 1903 (464)
    persian.json               <- Persian original (178) + literal/poetic/theme/
                                  note + fg_1st / fg_5th / whinfield match refs
    heron-allen.json           <- Heron-Allen 1898 entries, keyed fg_5th_num
  data/                        <- templates + build scripts (never web-served)
    build_reader.py            <- builds reader.html; ALSO the shared library
    build_fullbleed.py         <- builds fullbleed.html
    build_theater.py           <- builds theater.html
    build_mobile.py            <- builds mobile.html
    build_pdf.py               <- builds pdf-reader.html
    reader-template.html       <- __CONTENT__ placeholder (baked DOM)
    fullbleed-template.html    <- __DATA__ placeholder (JSON payload)
    theater-template.html      <- __DATA__ placeholder (JSON payload)
    mobile-template.html       <- __DATA__ placeholder (JSON payload)
    pdf-template.html          <- __DATA__ placeholder (JSON payload)
    fetch_fitzgerald.py        <- fetch FG 1st+5th from Gutenberg #246
    fetch_persian.py           <- fetch the Persian originals
    parse_pg38511.py           <- parse Whinfield / Nicolas source text
    merge_annotations.py       <- fold annotations into seeds/persian.json
    transliterate.py           <- Persian → Latin phonetic
  index.html                   <- book landing page (hand-written)
  reader.html                  <- GENERATED — scrolling reader
  fullbleed.html               <- GENERATED — two-page spread
  theater.html                 <- GENERATED — one quatrain at a time
  mobile.html                  <- GENERATED — phone pager, one per screen
  pdf-reader.html              <- GENERATED — PDF-viewer shell, one per page
```

## Build

```
python3 data/build_reader.py      # -> reader.html     (~1.9 MB)
python3 data/build_fullbleed.py   # -> fullbleed.html  (~1.5 MB)
python3 data/build_theater.py     # -> theater.html    (~0.44 MB)
python3 data/build_mobile.py      # -> mobile.html     (~1.5 MB)
python3 data/build_pdf.py         # -> pdf-reader.html (~1.5 MB)
```

The fetch/parse scripts (`fetch_*.py`, `parse_pg38511.py`,
`merge_annotations.py`) regenerate `seeds/` and need network access; they are
not part of the routine build. `index.html` is hand-written and is not built.

### How the build is wired

`data/build_reader.py` is both the reader's builder and the shared library the
other two import. It owns:

- `build_ctx()` — loads all five seeds and builds the cross-edition lookups
  (`fg1_to_fa`, `fg5_to_fa`, `wh_to_fa`, `ha_lookup`, …) that match an English
  quatrain to its Persian source
- `romanize()`, `to_fa_digits()`, `transliterate()` (re-exported)
- `frag_persian_source()`, `frag_heron_allen()`, `frag_modern_translations()`,
  `frag_historical_alternates()`, `frag_whinfield_refs()` — the apparatus
  fragments, shared by the reader's detail panel and fullbleed's facing gloss
- `EDITION_ORDER` / `EDITION_META` — the switcher's five entries
- `build_payload(ctx, with_gloss=)` — the JSON content for the JS-rendered
  formats
- `render_template(tpl, out, payload)` — substitutes `__DATA__`

`build_fullbleed.py`, `build_theater.py`, `build_mobile.py` and `build_pdf.py`
are thin: import, call `build_payload()`, call `render_template()`. Adding a
sixth edition means touching `EDITION_ORDER`/`EDITION_META` and
`edition_sources()` once, and all five formats pick it up.

Two substitution styles, deliberately:

- **reader.html** bakes every quatrain into the DOM at `__CONTENT__`, because a
  scrolling reader needs the whole text present for scroll/observer/progress.
- **fullbleed.html / theater.html** embed a JSON payload at `__DATA__` and
  render one quatrain at a time from JS.

## Data schema

`seeds/fitzgerald.json`:
```json
{ "source": "...", "translator": "Edward FitzGerald",
  "editions": {
    "first": {"year": 1859, "count": 75,
              "quatrains": [{"num": 1, "lines": ["...", "...", "...", "..."]}]},
    "fifth": {"year": 1889, "count": 101, "quatrains": [...]}
  } }
```

`seeds/whinfield.json` — `{count, quatrains: [{num, lines[], ms_refs, note}]}`
`seeds/nicolas-english.json` — `{count, quatrains: [{num, prose}]}`
`seeds/heron-allen.json` — `{count, entries: [{fg_5th_num, source_lines[], refs, note}]}`

`seeds/persian.json`:
```json
{ "direction": "rtl", "count": 178,
  "quatrains": [{
    "num": 1, "lines": ["...", "...", "...", "..."],
    "literal": ["..."], "poetic": ["..."],
    "theme": "carpe diem", "note": "...",
    "fg_1st": {"num": 11, "strength": "strong"},
    "fg_5th": {"num": 12, "strength": "strong"},
    "whinfield": {"num": 149, "strength": "partial"}
  }] }
```

The `fg_1st` / `fg_5th` / `whinfield` refs are what let an English quatrain
show its Persian source: `build_ctx()` inverts them into per-edition lookups.
Not every quatrain has a match — 806 of 1318 carry a facing gloss.

## Reader formats

| File | Format | Position hash | localStorage | Default theme |
|------|--------|---------------|--------------|---------------|
| `index.html` | landing page | — | `rubaiyat-index-theme` | light-purple |
| `reader.html` | scrolling reader | `#q-<ed>-N`, `#chg-<ed>-N` | `rubaiyat-reader-prefs` | light-purple |
| `fullbleed.html` | two-page spread | `#p-N`, `#s-N` | `rubaiyat-fullbleed-prefs` | light-purple |
| `theater.html` | one quatrain at a time | `#q-<ed>-N` | `rubaiyat-theater-prefs` | **dark-violet** |

Reading position is always in the URL hash (written with
`history.replaceState`, restored **in script** on load — every format renders
from JS or hides inactive editions, so the browser's own fragment scroll can't
find the target). localStorage holds presentation only.

### reader.html — scrolling reader
- All five editions in the DOM; only the active one is `display: block`
- Per-quatrain detail panel (`…` button) or a global Details toggle
- Persian side column toggle; transliteration toggle (Persian edition)
- Chapter sidebar over groups of 10, progress bar, settings panel
- Hash: `#q-<ed>-N` per quatrain, `#chg-<ed>-N` per group; also accepts the
  short `#q-N`, `#q-N-1`, `#q-N-5` forms
- Prefs: `{theme, font, size, width, edition, translit, persian, details}`
- Keyboard: `j`/`k`/arrows/space scroll, `Esc` closes panels

### fullbleed.html — two-page spread, one quatrain per recto
- Spread 0 cover · 1 title page · 2 colophon + contents · 3+ one quatrain each
- **Recto = the quatrain**, set large and centred under its numeral.
  **Verso = the facing apparatus**, in the manner of Heron-Allen's 1898
  facing-page edition: the Persian source with transliteration, the scholarly
  analysis, the modern rendering, and the other historical translations of the
  same quatrain. No match ⇒ a blank verso with a printer's ornament.
- Numerals: Roman for the four Latin-script editions, Persian digits for `fa`
- 3D page-flip animation (desktop; skipped on phones and under
  `prefers-reduced-motion`), click zones, swipe, arrow/space/`j`/`k`,
  Home/End, click-to-edit quatrain number
- Quatrain scrubber in the footer — one node per group of 10, so Whinfield's
  500 is 50 nodes, horizontally scrollable
- Edition switcher in the footer; switching restarts the edition at its first
  quatrain (`#p-12` means a different poem in a different edition)
- Hash: `#p-N` where N is the quatrain number; `#s-1` / `#s-2` for the front
  matter; the cover clears the hash
- Prefs: `{theme, edition}`
- Phones collapse to the recto alone with the gloss set below the quatrain

### theater.html — one quatrain at a time
- Cinematic dark stage (`dark-violet` by default), cross-fade between quatrains
- Large numeral above the verse (`clamp(46px, 8vw, 82px)`) plus an
  `N / TOTAL` counter — the quatrain-count indicator
- Click anywhere, arrows/space/`j`/`k`, or swipe to advance; Home/End jump
- Auto-hiding controls: prev/next, position, edition switcher, theme dots
- Hash: `#q-<edition>-N` — **the same deep-link form reader.html parses**, so a
  link copied from one opens the other on the same quatrain. The short
  `#q-N`, `#q-N-1`, `#q-N-5` forms are accepted on load too
- Prefs: `{theme, edition}` — the hash wins over the saved edition on load
- No facing gloss: the stage carries the quatrain alone

## Typography

Poetry, like The Prophet: `text-align: left`, no `text-indent`,
`line-height: 2.0`. Quatrains numbered in the classic 19th-century Roman style.
Reader width 560px; fullbleed page measure 520px; theater stage 620px.

FitzGerald's third line is indented (`p.indented`, `text-indent: 1.4em`) — his
own printings set it that way. Nicolas is prose, so it justifies.

### Persian (RTL)

- Font stack: `'Vazirmatn', 'Noto Naskh Arabic', 'EB Garamond', Georgia, serif`
- `dir="rtl" lang="fa"` on the quatrain container in every format
- Transliteration sits under each line as `dir="ltr"` but **`text-align: right`**,
  so it stays flush with the Persian it glosses
- Quatrain numbers use Persian digits (`۱۲۳`)

## Themes

5 themes on `data-theme`, consistent with the rest of lib.sadh.app:
`light-purple` (default), `sepia`, `light-azure`, `dark-violet`, `dark-blue`.

`fullbleed.html` and `theater.html` copy the reader's palette blocks verbatim
and only *add* the extras their layout needs, so the three formats are the same
book:

- fullbleed adds `--bg-left` (= the reader's `--sidebar-bg`, so the verso sits
  one shade off the recto), `--bg-right` (= `--bg`), `--spine` (= `--border`)
  and the gutter shadows
- theater adds `--dim`, `--controls-bg` (= `--bar-bg`),
  `--controls-border` (= `--bar-border`) and `--progress-bg`

## Accessibility

- Theme dots are real `<button>`s with `aria-label`, in a
  `role="group" aria-label="Theme"` row; a transparent `::before` gives each a
  40px-tall hit area without growing the dot
- Every icon-only button carries `aria-label`; `focus-visible` outlines
  everywhere; `prefers-reduced-motion` disables the page flip and the stage fade
- `lang="fa"` on Persian text, `lang="en-fa-Latn"` on transliteration
- Edition chips are `role="tab"` with `aria-selected` and a spelled-out
  `aria-label` (the Persian chip reads "Persian original…", not "فا")

## mobile.html and pdf-reader.html

Added after the audit closed the suite gap; both are generated the same way as
fullbleed/theater — a `__DATA__` payload from `build_reader.py` substituted into
a template under `data/`.

| | mobile.html | pdf-reader.html |
|---|---|---|
| Shape | one quatrain per screen, gloss set below | one quatrain per page card in a viewer shell |
| Position hash | `#q-<edition>-N` (shared with reader/theater) | `#p-N` (page ordinal in the current edition) |
| Prefs key | `rubaiyat-mobile-prefs` → `{theme, edition}` | `rubaiyat-pdf-prefs` → `{theme, edition, zoom}` |
| Navigation | swipe, arrow buttons, `j`/`k`/arrows/space | toolbar, thumbnail sidebar, page box, zoom, `j`/`k`/arrows/Page/Home/End |
| Chrome | bottom sheets for edition / theme / jump-to | dark toolbar + slide-in sidebar |

Notes for future edits:

- **Mobile's sheets carry a focus trap** (Tab cycles inside, Escape closes,
  focus returns to the opener) — the pattern `gibran-prophet/mobile.html`
  established. Keep it if you add another sheet.
- **`#toolbar > button` in the PDF template is deliberately a child selector.**
  The theme dots live inside `#themeDots`, and a descendant selector applied the
  toolbar's `min-width` to each 14px dot, inflating the row to 224px and
  overflowing a phone viewport.
- Persian is RTL: both templates set `dir="rtl" lang="fa"` on the verse and use
  the `--font-fa` stack; the transliteration stays `direction: ltr` but is
  right-aligned so it pairs with the line above.

# khayyam-rubaiyat Changelog

## Earlier sessions (reconstructed from the tree — this book had no `.project/`)

- `seeds/fitzgerald.json` parsed from Project Gutenberg #246 (FG 1st, 75; FG 5th, 101)
- `seeds/whinfield.json` (500), `seeds/nicolas-english.json` (464),
  `seeds/heron-allen.json`, `seeds/persian.json` (178) added, the last with
  transliteration, machine-generated modern literal/poetic renderings, theme
  tags, notes, and match refs into FG 1st / FG 5th / Whinfield
- `data/build_reader.py` + `data/reader-template.html` → `reader.html`:
  five-edition scrolling reader with a per-quatrain detail panel, Persian side
  column, transliteration toggle, `#q-<ed>-N` / `#chg-<ed>-N` hashes
- `index.html` hand-written landing page

## 2026-08-20

### Session — the two missing formats (`fullbleed.html`, `theater.html`)

The audit flagged this book as the thinnest suite in the library — only
`index.html` + `reader.html`, while `CLAUDE.md` had promised a fullbleed and a
theater since the first commit. Both now exist, built the same way the reader is.

**Build wiring** — chose *sibling scripts importing `build_reader.py`* over
inlining new `main()`s into it. `build_reader.py` already owned everything the
new formats needed (seed loading, the Persian↔English match lookups,
`romanize()`, `to_fa_digits()`, `transliterate()`, and the five `frag_*`
apparatus builders), so it became the shared library and gained:

- `EDITION_ORDER` / `EDITION_META` — the five switcher entries, one place
- `payload_label()` / `payload_verse()` / `payload_gloss()` — per-edition
  rendering for the JS formats, reusing the existing `frag_*` fragments
- `edition_sources()`, `build_payload(ctx, with_gloss=)` — the JSON content
- `render_template(tpl, out, payload)` — `__DATA__` substitution

`data/build_fullbleed.py` and `data/build_theater.py` are ~30 lines each.
`reader.html` rebuilds byte-identical, so the refactor is inert for it.

Note the two substitution styles: the reader bakes its DOM at `__CONTENT__`
(a scrolling reader needs the whole text present); the two new formats embed a
JSON payload at `__DATA__` and render one quatrain at a time.

**`fullbleed.html`** — two-page spread, one quatrain per recto

- Cover → title page → colophon + contents → one quatrain per spread
- The verso is the *facing apparatus*, after Heron-Allen's 1898 facing-page
  edition: Persian source with transliteration, the scholarly analysis, the
  modern rendering, and the other historical translations of the same quatrain.
  806 of 1318 quatrains have one; the rest get a blank verso with an ornament
- Roman numerals for the four Latin-script editions, Persian digits for `fa`
- 3D page flip (skipped on phones and under `prefers-reduced-motion`), click
  zones, swipe, arrows/space/`j`/`k`, Home/End, click-to-edit quatrain number
- Footer scrubber over groups of 10 (50 nodes for Whinfield's 500, scrollable)
- Edition switcher kept, all five reachable; switching restarts at quatrain 1
  because `#p-12` names a different poem in a different edition
- Hash `#p-N` (quatrain number) / `#s-1`,`#s-2` (front matter); cover clears it
- `rubaiyat-fullbleed-prefs` → `{theme, edition}`
- Phones collapse to the recto with the gloss set beneath the quatrain

**`theater.html`** — one quatrain at a time

- Cinematic dark stage, `dark-violet` by default (the only dark-by-default page
  in this book), cross-fade between quatrains
- Large numeral `clamp(46px, 8vw, 82px)` over the verse plus an `N / TOTAL`
  counter and a top edition/position indicator
- Click anywhere, arrows/space/`j`/`k`, or swipe; Home/End jump to the ends
- Auto-hiding controls carry prev/next, position, the five-edition switcher and
  the theme dots
- Hash `#q-<edition>-N` — deliberately the *same* form `reader.html` parses, so
  a link copied from one opens the other on the same quatrain. The short
  `#q-N` / `#q-N-1` / `#q-N-5` forms are accepted on load too
- `rubaiyat-theater-prefs` → `{theme, edition}`; the hash beats the saved
  edition on load

**Persian (both formats)** — `dir="rtl" lang="fa"` on the quatrain container,
the reader's `Vazirmatn, 'Noto Naskh Arabic', 'EB Garamond', Georgia, serif`
stack, and transliteration set `dir="ltr"` but `text-align: right` so it stays
flush with the line it glosses — matching `reader-template.html`.

**Palettes** — both templates copy the reader's five `data-theme` blocks
verbatim and only add what their layout needs: fullbleed gets `--bg-left`
(= the reader's `--sidebar-bg`), `--bg-right` (= `--bg`), `--spine`
(= `--border`) and gutter shadows; theater gets `--dim`, `--controls-bg`
(= `--bar-bg`), `--controls-border` (= `--bar-border`), `--progress-bg`.

**Bug caught in verification**: `fullbleed-template.html` called
`initPageNumClick()` from `init()` without the function existing. The
`ReferenceError` aborted the rest of `init()`, so the keyboard, touch,
`hashchange` and `resize` listeners were never attached — footer buttons worked
but arrow keys did nothing. Wrote the function; all four listener groups now
attach.

**Docs**

- `CLAUDE.md` rewritten. It had described a 2-edition reader, a
  `seeds/quatrains.json` that does not exist, and a `data/build_quatrains.py`
  pipeline that was never written. It now documents the five seed files, the
  real `data/build_*.py` builders and the shared-library split, all four pages
  with their hashes/keys/defaults, the Persian RTL rules and the palette
  derivation
- `.project/todo.md` and `.project/changelog.md` created — the book had no
  `.project/` at all
- `index.html`: Full Bleed and Theater added to the reading-formats row
- root `index.html`: both added to the Rubáiyát catalog card

**Verified** in headless Chromium at 1440x900 and 390x844: zero page errors,
content rendered, navigation advances (click / footer buttons / arrow keys /
scrubber / edition switch), hash written on navigation and restored on load,
theme and edition persist across reload, prefs carry no position, no horizontal
overflow at 390px, Persian containers computed `direction: rtl` with the right
font stack, transliteration right-aligned, every icon-only button labelled,
theme dot hit areas ≥40px.

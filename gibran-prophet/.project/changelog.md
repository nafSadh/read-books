# gibran-prophet Changelog

## 2026-04-03

### Session 1 — Initial build

- Parsed 28 chapters from Project Gutenberg (pg58585.txt) into `seeds/chapters.json`
- Built `reader.html`: scrolling reader with poetry typography, 5 themes, sidebar, progress bar
- Built `fullbleed.html`: two-page spread with stanza-aware pagination, cover, TOC
- Typography: left-aligned, no text-indent, line-height 2.0, 560px default width
- Default theme: light-purple
- URL hash: `#ch-N` (reader), `#p-N` (fullbleed) for reading state persistence
- Directory: `gibran-prophet/` (author-book convention)
- **Fixes**: cleaned Gutenberg `*****` separators from 26 chapters; fixed theme cycle order in fullbleed to match dot order

## 2026-08-20

### Session 2 — Audit fixes (conventions + a11y)

**Reading position → URL hash** (house convention: position never in localStorage)

- `theater.html`: fixed an escaped-backtick `SyntaxError`; moved the chapter
  position from `prophet-theater-chapter` to `#ch-N` (legacy bare `#N` still parsed)
- `mobile.html`: `savePrefs()` now stores `{ theme }` only — `chIdx` is gone.
  `goTo()` writes `#ch-N` with `history.replaceState` (title slide clears the hash)
  and `init()` restores from the hash. Legacy prefs that still carry `chIdx` are
  ignored for position but keep the reader's saved theme
- `pdf-reader.html`: gained reading-position persistence it never had —
  `renderPage()` writes `#p-N`, `init()` restores it after pagination
  (113 pages; out-of-range hashes fall back to page 1)

**Accessibility**

- Theme dots are now real `<button type="button">` elements with `aria-label`
  (were non-focusable `<span>`s in `fullbleed.html`, `reader.html`,
  `illustrations.html` and `<div>`s in `pdf-reader.html`; `theater.html`'s
  buttons gained `type` + labels). Dot rows got `role="group" aria-label="Theme"`
- Each dot has a `::before` hit-area expander: 40px tall, spanning the gap to its
  neighbour, visual size unchanged (12px / 14px, 10px on phones in theater).
  The expander is deliberately *not* 40px wide — a 40x40 square overlaps the next
  dot and steals its clicks (verified: clicking a dot applied the next dot's theme)
- `focus-visible` outlines on every dot; the hover-revealed dot rows in
  `reader.html` / `fullbleed.html` now also open on `:focus-within`, so the dots
  are reachable by keyboard
- `aria-label`s added to the icon-only controls in `fullbleed.html` (prev/next,
  cycle theme) and `pdf-reader.html` (sidebar toggle, prev/next, zoom in/out,
  page box, chapter select); the duplicate nav zones are `aria-hidden`

**Keyboard**

- `j`/`k` added as aliases for `ArrowRight`/`ArrowLeft` in `fullbleed.html` and
  `mobile.html` (matching reader/theater/pdf-reader). fullbleed's handler now
  ignores keys typed into its page-number input

**Illustrations resilience**

- All 29 plates got descriptive `alt` text, the 12 Prophet plates got intrinsic
  `width`/`height`, and an `onerror` hook (`plateFail`) now paints the plate's
  caption into the reserved aspect-ratio box instead of a blank frame; a failed
  plate no longer opens an empty lightbox. Images are still hotlinked — vendoring
  them locally needs network access and stays on the TODO

**Docs**

- `CLAUDE.md`: "Reader formats" and "File inventory" rewritten to cover all 7
  hand-written files with their real localStorage keys, hash behaviour and default
  themes (theater = dark-violet, illustrations = sepia)
- `.project/todo.md`: mobile + theater marked done; open items recorded
  (vendor plates, fullbleed flip-animation hash gap, bare `-theme` keys)

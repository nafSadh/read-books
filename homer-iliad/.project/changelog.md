# homer-iliad Changelog

## 2026-07-26

### Session 1 — Initial build

- Fetched and parsed three public-domain translations from Project Gutenberg
  (Butler #2199 prose, Pope #6130 verse, Cowper #16452 blank verse) into
  `seeds/{butler,pope,cowper}.json`, 24 books each. Parsing handled per
  translation: front-matter/boilerplate stripping, footnote-marker removal,
  marginal line-number stripping (Cowper), editorial-commentary exclusion
  (Cowper's uncredited "—Felton." notes), TOC-vs-real-heading disambiguation.
  Fidelity spot-checked: all three open with Achilles' wrath and close with
  Hector's funeral, matching known text.
- **First architecture (reverted)**: pre-rendered all 3 translations × 24
  books as static HTML in the DOM at once (Rubáiyát's edition-switch
  pattern). Found a real bug: this produced pages several million pixels
  tall; hash deep-links and large scroll jumps failed to paint (confirmed
  via DOM/console inspection, not a testing artifact).
- **Fix**: rewrote to embed seed data as a JS constant and render only the
  current book client-side (`renderCurrentBook()` / `loadBook()`), swapping
  DOM content on navigation instead of appending. Applied to all variants.
- Built all 5 reader formats: `reader.html`, `fullbleed.html`, `mobile.html`,
  `theater.html`, `pdf-reader.html`, plus `index.html` landing page.
- **Second bug found and fixed**: initial pagination for fullbleed/pdf-reader
  measured each paragraph's height and bin-packed into fixed-height pages —
  broke on Butler's long prose paragraphs (some taller than a full page,
  silently clipped by `overflow:hidden`). Replaced with native CSS
  multi-column layout, which lets the browser split content (including
  mid-paragraph) across "pages" correctly.
- **Third bug found and fixed**: `pdf-reader.html`'s `column-gap: 0` let the
  next (hidden) column start inside the visible viewport instead of past its
  edge, causing visible text bleed-through. Fixed by setting
  `column-gap: 80` (matching `fullbleed.html`) so `column-width + column-gap`
  equals the viewport width with margin to spare.
- Switched page-turn positioning from `transform: translateX()` to
  `margin-left` as a defensive measure (standard box-layout overflow
  clipping has no known compositing-layer edge cases, unlike transforms).
- Directory: `homer-iliad/` (author-book convention).
- Default theme: light-purple (dark-violet for theater.html, matching Prophet).
- URL hash: `#bk-N` (current translation), `#bk-<butler|pope|cowper>-N` (explicit).

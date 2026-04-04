# meditations Changelog

## 2026-04-03

### Session 1 — Initial build + annotated reader prototype

- **reader.html** — scrolling reader with full George Long (1862) translation
  - All 12 Books, ~400 meditations from Project Gutenberg (ebook #2680)
  - 5 themes: light-purple (default), sepia, light-azure, dark-violet, dark-blue
  - Alice-pattern UI: sidebar, progress bar, chapter scrubber, settings panel
  - Meditation numbers as `[icon] IV.` on own line above passage text
  - Passages I-V of Book I annotated with:
    - Side-panel detail system (Modern English rewrite + Notes)
    - Proper noun tooltips (Verus, Prasini, Rusticus, Epictetus, etc.)
    - `s-detail-btn` icon from read-rd convention
  - Global "open all details" toggle in top bar
  - Side panel: detail appears to the right, main text stays in place
  - `#content` widens when details are open; page width selector (narrow/medium/wide) adjusts main text column
  - Known issue: `#content` width expansion via CSS `calc(var(--content-width) + ...)` not resolving correctly in all browsers; needs debugging
- **fullbleed.html** — two-page spread book reader
  - Full text of all 12 Books
  - Pagination engine, 3D page flip, cover/title/TOC pages
  - 5 themes with sepia default, chapter scrubber
  - Mobile single-page fallback
- **index.html** — added Meditations card between Alice and Vedas
- **Greek text sourced** — Perseus Digital Library `tlg0562.tlg001.perseus-grc2.xml` (Leopold edition, CC BY-SA 4.0) downloaded and parsed into JSON; not yet integrated into readers

## 2026-04-03 / 04

### Session 2 — Detail panel layout overhaul

- **Detail panel moved to the left** of passage text (was right)
  - `flex-direction: row-reverse` on `.med-body`
  - Detail text right-aligned with right-side accent border for visual centrality
  - 55:45 ratio: main text 55%, detail panel 45%
- **Per-passage sizing** — only the clicked passage grows when details open
  - Passage widens symmetrically (center-aligned) via negative margin + extra width
  - Other passages and `#content` container stay unchanged
  - Replaced old `#content.has-details-open` approach
- **Med-head layout** — when details open, icon and number reposition via CSS grid
  - Detail icon right-aligned in left column, centered on the separator line
  - Passage number at start of right column
  - Grid columns match the 45%/1fr split of the body below
- **Detail button open state** simplified — accent color only, no extra border/bg
- **Proper noun tooltip fix** — added invisible bridge (`::after` on `.pn-tip`) so cursor can travel from word to tooltip; links now clickable
- **Mobile breakpoint** — details stack below with left border on narrow screens

## 2026-04-04

### Session 3 — Full annotation of all 412 passages + index page

- **All 412 passages annotated** across all 12 Books
  - Books I-IV: annotated directly in HTML by Wave 1 agents
  - Books 5-12: JSON-first batch processing via `seeds/annotations/book-NN.json`
  - Assembler script (`seeds/assemble-annotations.py`) converts plain passages to annotated `med-passage` blocks
  - Each passage has: Modern English rewrite, historical notes, proper noun tooltips with Wikipedia links
- **JSON annotation pipeline** — smarter approach to avoid agent file conflicts
  - Annotation data stored as JSON in `seeds/annotations/` (10 files)
  - Python assembler script reads JSON + injects into reader.html in one atomic write
  - Strategy documented in `.project/annotation-strategy.md`
- **meditations/index.html** — new book-spread landing page
  - Cover page with title, Greek subtitle, Marcus Aurelius
  - About page with key Stoic themes, Greek quotation
  - Annotation system description + available readers with links
  - Data sources table, 12 Books listing with one-line descriptions
  - Colophon with branding
  - 5 themes, 3D page flip, keyboard/touch navigation, mobile responsive
- **Main index.html** updated — "Classic Book" link added for Meditations
- **Book 12 JSON regenerated** — original was wrong (started at X instead of I)

### Data sources

- English: George Long translation (1862), Project Gutenberg #2680, public domain
- Greek: Perseus Digital Library, Leopold edition, CC BY-SA 4.0

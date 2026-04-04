# aurelius-meditations Changelog

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
  - Books 5-12: JSON-first batch processing via `data/annotations/book-NN.json`
  - Assembler script (`data/assemble-annotations.py`) converts plain passages to annotated `med-passage` blocks
  - Each passage has: Modern English rewrite, historical notes, proper noun tooltips with Wikipedia links
- **JSON annotation pipeline** — smarter approach to avoid agent file conflicts
  - Annotation data stored as JSON in `data/annotations/` (10 files)
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

### Session 4 — Greek + English text collection + directory rename

- **Directory renamed** `meditations/` → `aurelius-meditations/`
  - Updated all references in root `index.html`
- **`data/collect_texts.py`** — stdlib-only Python script to collect source texts
  - Greek (Leopold): 486 passages from Perseus Digital Library TEI XML (CC BY-SA 4.0)
  - George Long (1862): 522 passages from Standard Ebooks XHTML (CC0)
  - Meric Casaubon (1634): 412 passages from cached Project Gutenberg data
  - Smart alignment: Greek passage numbers as canonical, Long matched by number (484/486 aligned)
  - Casaubon stored separately (numbering diverges too much for auto-alignment)
  - Caches fetched data in `/tmp/meditations_texts_cache/`
  - Location notes filtered ("Among the Quadi at the Granua", "This in Carnuntum")
- **`data/texts/`** — output directory (26 files, ~4 MB total)
  - 12 per-book JSON + 12 per-book Markdown
  - `meditations-complete.json` (983 KB) + `meditations-complete.md` (935 KB)
- **Renamed `seeds/` → `data/`** across all references (CLAUDE.md, agents-log, todo)
- **Translator attribution fix** — reader.html, fullbleed.html, index.html all said "George Long" but the embedded text is Meric Casaubon (1634). Fixed all three.
- **`data/align_casaubon_long.py`** — Casaubon↔Long alignment mapping script
  - Uses text similarity: proper noun overlap (3x weight) + word cosine
  - Monotonicity constraint preserves passage ordering
  - Handles 1:many mappings (Casaubon passage spanning multiple Long passages)
  - Confidence levels: high/medium/low
  - Output: `data/texts/casaubon-long-alignment.json` (56 KB)
  - 412/412 Casaubon passages mapped; quality varies by book divergence
- **Hammond PDF extraction** (`hammond/extract_hammond.py`)
  - Uses pymupdf for PDF text extraction from Martin Hammond (Penguin 2006)
  - Margin number detection + paragraph-break fallback + sentence-boundary splitting
  - 468/486 passages extracted (96%)
  - Output: `hammond/hammond-meditations.json`
  - Directory gitignored (copyrighted text)

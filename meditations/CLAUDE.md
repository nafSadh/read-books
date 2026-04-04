# Meditations — Read-Book Project

Build readers for Marcus Aurelius' "Meditations", following the same patterns as
`../alice-in-wonderland/`. All HTML files are self-contained (no external JS/CSS
beyond Google Fonts).

## Content

- **Author**: Marcus Aurelius (121-180 CE), Roman Emperor
- **Written**: c. 170-180 CE, in Koine Greek
- **English translation**: George Long (1862), public domain (Project Gutenberg #2680)
- **Greek text**: Perseus Digital Library, Leopold edition (CC BY-SA 4.0)
- **Structure**: 12 Books, ~400+ meditations/passages
- **Content embedding**: Full text embedded directly in HTML (no external JSON)

## Reader formats

### 1. `reader.html` (scrolling reader)

Follows `../alice-in-wonderland/reader.html` pattern:
- All 12 Books with full George Long translation
- Each Book = a "chapter" in the sidebar
- 5 themes: light-purple (default), sepia, light-azure, dark-violet, dark-blue
- Font/size/width controls (serif, sans, slab, mono; small/medium/large; narrow/medium/wide)
- Meditation numbers on own line: `[detail-icon] IV.` above passage text
- localStorage key: `meditations-reader-prefs`

**Annotation system** (prototype, Book I passages I-V):
- Side-panel details: Modern English rewrite + Notes
- Proper noun tooltips: dotted underline, hover popup with biographical info + Wikipedia links
- `s-detail-btn` document icon (from read-rd convention)
- Global "open all details" toggle in top bar
- Side panel appears to the **left** of passage text (`flex-direction: row-reverse`)
- Detail text right-aligned with right-side accent border; 55:45 main:detail ratio
- Only the open passage grows (center-aligned); other passages stay unchanged
- When open, `med-head` switches to CSS grid: icon right-aligned in detail column (centered on separator), number at start of main column
- Proper noun tooltips include hover bridge so links are clickable
- On mobile/narrow screens: detail panel stacks below with left border

**HTML structure for annotated passages**:
```html
<div class="med-passage">
  <div class="med-head">
    <button class="med-detail-btn">...</button>
    <span class="med-num">I.</span>
  </div>
  <div class="med-body">
    <div class="med-main"><p>archaic text...</p></div>
    <div class="med-detail">
      <div class="narr-section"><span class="narr-label">Modern English</span><p>...</p></div>
      <div class="narr-section"><span class="narr-label">Notes</span><p>...</p></div>
    </div>
  </div>
</div>
```

Non-annotated passages use plain `<p><span class="med-num">VI.</span>text...</p>`.

### 2. `fullbleed.html` (book-spread reader)

Follows `../alice-in-wonderland/fullbleed.html` pattern:
- CHAPTERS array in JS (12 entries, one per Book)
- Pagination engine with hidden measure div
- 3D page flip animation, mobile single-page fallback
- Cover, title page, table of contents
- 5 themes with sepia default
- localStorage key: `meditations-fullbleed-theme`

## Typography

| Property       | Value |
|----------------|-------|
| text-align     | justify (passage text) |
| text-indent    | 0 (meditations are short, no indent needed) |
| line-height    | 1.85 |
| default width  | 640px |
| font-body      | EB Garamond |

## Theme variables

5 themes: `light-azure`, `light-purple` (default), `sepia`, `dark-violet`, `dark-blue`.
Sepia theme uses warm parchment tones (`--bg: #f5efe0`, `--accent: #8b6914`).

## Data sources

| Source | Edition | License |
|--------|---------|---------|
| English | George Long, 1862 | Public domain (Gutenberg #2680) |
| Greek | Leopold, Perseus DL | CC BY-SA 4.0 |

Greek text downloaded from `PerseusDL/canonical-greekLit` on GitHub.
Section numbering differs between Long (English) and Leopold (Greek) editions.

## File inventory

```
meditations/
  CLAUDE.md              <- this file
  .project/
    changelog.md         <- session log
    todo.md              <- task tracking
    agents-log.md        <- annotation agent history
  index.html             <- book-spread landing page
  reader.html            <- scrolling reader (full text, all 412 passages annotated)
  fullbleed.html         <- book-spread reader (full text)
  seeds/
    annotations/         <- JSON annotation data (book-01-remaining.json through book-12.json)
    assemble-annotations.js  <- Node.js assembler (original)
    assemble-annotations.py  <- Python assembler (used for injection)
```

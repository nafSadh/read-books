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
- Greek on: English + Greek side-by-side (60%/40%)
- Detail open: Detail panel (left, 45%) + English (right, 55%)
- Both open: Detail (25%) + Greek (28%) + English (47%), viewport-capped via `min()`
- Mobile (<1200px): all columns stack vertically

**Rebuild**: `python3 data/assemble-reader.py` (reads JSON + template, outputs reader.html)

### 1b. `reader-casaubon.html` (scrolling reader — Casaubon translation)

Original Casaubon (1634) reader preserved as-is. localStorage key: `meditations-casaubon-prefs`.

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
  data/
    annotations/         <- JSON annotation data
      leopold-books-01-03.json  <- Books 1-3 Leopold annotations (50 passages)
      leopold-books-04-06.json  <- Books 4-6 Leopold annotations (146 passages)
      leopold-books-07-09.json  <- Books 7-9 Leopold annotations (178 passages)
      leopold-books-10-12.json  <- Books 10-12 Leopold annotations (112 passages)
      book-01-remaining.json .. book-12.json  <- legacy Casaubon-era annotations
    assemble-reader.py   <- builds reader.html from JSON + template (Long + Greek toggle)
    assemble-annotations.js  <- Node.js assembler (original, Casaubon)
    assemble-annotations.py  <- Python assembler (Casaubon injection)
    collect_texts.py     <- fetches Greek + Long + Casaubon, merges annotations → aurelius-meditations.json
    align_casaubon_long.py <- Casaubon↔Long passage alignment mapping
    texts/               <- output: combined MD + alignment JSON
  hammond/               <- (gitignored) Martin Hammond (Penguin 2006) extraction
    extract_hammond.py   <- PDF text extraction script (pymupdf)
    hammond-meditations.json <- extracted passages (479/486)
```

# Alice in Wonderland — Changelog

## 2026-04-03

### Session 1 — fullbleed.html major refactor + reader.html theme refinements

Major overhaul of fullbleed.html based on learnings from mobile.html and reader.html. Also refined reader.html theme controls.

#### reader.html changes
- **Theme toggle icon**: Replaced toggle-pill SVG with half-sun icon (circle + two diagonal-fill quadrants + 8 rays)
- **Theme dots simplified**: Removed all borders, solid fill backgrounds, active state uses double box-shadow ring

#### fullbleed.html refactor
- **4-theme system**: Added light-azure, light-purple, dark-violet, dark-blue via `html[data-theme]` CSS variables (was just light/dark)
- **Running headers**: Moved from fixed overlay to inside each `.page-content` div, so they flip with pages
  - Blank pages: fully blank (no header, no page number)
  - Chapter-start pages: no running header (chapter heading is focal point)
  - Normal pages: book title (italic) + chapter title
- **Chapter headers rethought**: Added subtle book title above chapter number in italic accent color
- **Chapter scrubber**: Roman numerals I–XII in footer with hover tooltips showing chapter titles via CSS `::after`
- **Editable page number**: Click to type, only number editable ("/ total" stays), Enter to jump
- **Recto chapter starts**: All chapters start on right-hand (recto) page; blank pages inserted automatically via `ensureRectoChapterStarts()`
- **Page numbers**: Moved to outer corners (left page = left, right page = right)
- **Footer redesign**: Gradient background fading from transparent to paper color, no borders/pill shape
- **Theme dots**: Pop upward above button (not leftward), same borderless style as reader.html
- **Cover page**: Uses theme CSS variables (matches current theme), theme picker visible on cover, nav/scrubber hidden
- **TOC moved to recto**: Spread 2 = blank left + TOC right (was TOC left + content right)
- **Accent color usage**: Extended to chapter numbers, ornaments, book title, page numbers, TOC numbers, cover ornaments — all at tasteful opacity levels
- **dark-violet theme**: Fixed to use neutral grey (`#181818`/`#1a1a1a`) matching reader.html (was purple-tinted)
- **Spread layout restructured**: New mapping — spread 3+ uses `left: 2s-7, right: 2s-6`

#### Bug fixes
- Running header not moving with page flip (was `position: fixed`)
- Theme dots overlapping chapter scrubber (changed to pop upward)
- Footer gradient hiding page numbers (adjusted gradient, moved page nums to corners)
- `updateIndicator()` overwriting chapter-start header clearing
- Duplicate page-num click handler code
- Running header not aligned with text content (matched `max-width: 560px`)

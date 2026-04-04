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

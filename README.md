# lib.sadh.app

Public domain books, beautifully rendered in multiple reading formats.

**URL**: [lib.sadh.app](https://lib.sadh.app)

## Books

### Alice's Adventures in Wonderland
*Lewis Carroll, 1865*

Text from [Project Gutenberg](https://www.gutenberg.org/ebooks/11). 9 reader variants:

| Reader | Style | Navigation |
|--------|-------|------------|
| [reader](alice-in-wonderland/reader.html) | Scroll with chapter nav, 5 themes, settings | Page-per-keypress, chapter scrubber |
| [fullbleed](alice-in-wonderland/fullbleed.html) | Royal navy, edge-to-edge spread | 3D page flip |
| [index](alice-in-wonderland/index.html) | Classic leather book with cover | 3D page flip |
| [pdf-reader](alice-in-wonderland/pdf-reader.html) | Chrome PDF viewer style | Toolbar, 1pg/2pg toggle, sidebar |
| [web-reader](alice-in-wonderland/web-reader.html) | Browser reader mode | Continuous scroll, 4 themes (own palette) |
| [scroll](alice-in-wonderland/scroll.html) | Clean article scroll | Chapter nav dots |
| [single](alice-in-wonderland/single.html) | Chapter cards | Slide transitions |
| [theater](alice-in-wonderland/theater.html) | Cinematic dark stage | One passage at a time |
| [mobile](alice-in-wonderland/mobile.html) | Mobile-first, full-width single page | 3D swipe flip, tap nav, chapter scrubber |

### Meditations
*Marcus Aurelius, c. 170–180 CE*

Two English translations of the Greek original: George Long (1862) in the flagship reader, with the
original Koine Greek available side by side, and Meric Casaubon (1634) preserved in its own reader.
All 486 passages carry a modern-English rewrite, notes, and proper-noun annotations.

| Reader | Style | Navigation |
|--------|-------|------------|
| [index](aurelius-meditations/index.html) | Landing page, book spread | Links to every reader |
| [reader](aurelius-meditations/reader.html) | Scrolling, Long translation + Greek toggle + detail panels | Sidebar, 5 themes, keyboard |
| [reader-casaubon](aurelius-meditations/reader-casaubon.html) | Scrolling, Casaubon 1634 | Sidebar, 5 themes, keyboard |
| [fullbleed](aurelius-meditations/fullbleed.html) | Two-page spread | Page flip, chapter scrubber |

Generated: `python3 aurelius-meditations/data/assemble-reader.py` rebuilds `reader.html`.

### The Prophet
*Kahlil Gibran, 1923*

28 chapters of poetic prose from [Project Gutenberg](https://www.gutenberg.org/ebooks/58585), set with
poetry typography (left-aligned, stanza-aware pagination).

| Reader | Style | Navigation |
|--------|-------|------------|
| [index](gibran-prophet/index.html) | Landing page | Links to every reader |
| [reader](gibran-prophet/reader.html) | Clean scroll | Sidebar, 5 themes, keyboard |
| [fullbleed](gibran-prophet/fullbleed.html) | Two-page spread | Page flip, chapter scrubber |
| [mobile](gibran-prophet/mobile.html) | Mobile-first single page | Swipe, bottom sheets |
| [theater](gibran-prophet/theater.html) | Cinematic dark stage | One chapter at a time |
| [pdf-reader](gibran-prophet/pdf-reader.html) | Chrome PDF viewer style | Toolbar, sidebar |
| [illustrations](gibran-prophet/illustrations.html) | Gibran's own plates | Lightbox gallery |

### Rubáiyát of Omar Khayyám
*Omar Khayyám, c. 1048–1131 — five parallel editions*

FitzGerald's 1st (1859) and 5th (1889) editions, E. H. Whinfield (1883), Nicolas (1867→English prose),
and the Foroughi-Ghani Persian original with transliteration — switchable side by side, with per-quatrain
scholarly notes.

| Reader | Style | Navigation |
|--------|-------|------------|
| [index](khayyam-rubaiyat/index.html) | Landing page, book spread | Links to the reader |
| [reader](khayyam-rubaiyat/reader.html) | Scrolling, 5-edition switcher, Persian column | Sidebar, quatrain deep links, 5 themes |

Generated: `python3 khayyam-rubaiyat/data/build_reader.py` rebuilds `reader.html`.

### Vedas
*c. 1500–500 BCE — multilingual*

Bengali-script Sanskrit with toggleable Devanagari and IAST, plus Bengali and English meanings.
The complete Rigveda reader carries all 1,028 sūktas / 10,143 mantras with lazy-loaded per-mandala data.

| Reader | Style | Navigation |
|--------|-------|------------|
| [rigveda](vedas/rigveda.html) | Complete Rigveda, two-column | Mandala tabs, sūkta strip, `#M.S` deep links |
| [reader](vedas/reader.html) | Curated 4-Veda scroll | Sidebar, script toggles, 5 themes |
| [fullbleed](vedas/fullbleed.html) | Curated 4-Veda spread | Page flip, chapter scrubber |

Generated: `python3 vedas/build_rigveda.py` rebuilds `rigveda.html` and its per-mandala data (needs network).

### The Iliad & The Odyssey
*Homer, c. 8th century BCE*

Three parallel public-domain translations — Samuel Butler (prose, 1898/1900), Alexander Pope (heroic-couplet verse, 1720/1725), William Cowper (blank verse, 1791) — from [Project Gutenberg](https://www.gutenberg.org/ebooks/subject/674). 5 reader variants each, one book of 24 rendered at a time:

| Reader | Style | Navigation |
|--------|-------|------------|
| [reader](homer-iliad/reader.html) / [odyssey](homer-odyssey/reader.html) | Scroll with book sidebar, 5 themes, translation switcher | Sidebar, book scrubber, prev/next |
| [fullbleed](homer-iliad/fullbleed.html) / [odyssey](homer-odyssey/fullbleed.html) | Edge-to-edge two-page spread | Click/swipe/arrow page turn |
| [mobile](homer-iliad/mobile.html) / [odyssey](homer-odyssey/mobile.html) | Mobile-first, full-width single page | Swipe between books, bottom sheets |
| [theater](homer-iliad/theater.html) / [odyssey](homer-odyssey/theater.html) | Cinematic dark stage | Click-to-advance, one book at a time |
| [pdf-reader](homer-iliad/pdf-reader.html) / [odyssey](homer-odyssey/pdf-reader.html) | Chrome PDF viewer style | Toolbar, book dropdown, page input |

## Design

Every reader is a self-contained HTML file — no runtime dependencies and no external fetches beyond
Google Fonts. Book text is embedded as a JS constant, so a reader works offline and from `file://`.
(`vedas/rigveda.html` is the one exception: at 10,143 mantras it lazy-loads per-mandala data, with a
script-tag fallback so it still works from `file://`.)

Several readers are *generated* from a template plus source data — edit the template or build script under
the book's `data/` directory, never the built HTML. See each book's section above for its build command.

Shared conventions across all books (see `AGENT_README.md`): 5 themes on `<html data-theme>`, reading
position in the URL hash, preferences in `localStorage` under `{book}-{format}-prefs`, and
EB Garamond / Jost / IBM Plex Mono for body / UI / meta text.

Color themes align with the [read.sadh.app](https://read.sadh.app) design system (purple/blue accent palette).

## License

Book text is public domain. Reader code is part of the read-rd project.

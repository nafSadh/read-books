# lib.sadh.app

Public domain books, beautifully rendered in multiple reading formats.

**URL**: [lib.sadh.app](https://lib.sadh.app)

## Books

### Alice's Adventures in Wonderland
*Lewis Carroll, 1865*

Text from [Project Gutenberg](https://www.gutenberg.org/ebooks/11). 9 reader variants:

| Reader | Style | Navigation |
|--------|-------|------------|
| [reader](alice-in-wonderland/reader.html) | Scroll with chapter nav, 4 themes, settings | Page-per-keypress, chapter scrubber |
| [fullbleed](alice-in-wonderland/fullbleed.html) | Royal navy, edge-to-edge spread | 3D page flip |
| [index](alice-in-wonderland/index.html) | Classic leather book with cover | 3D page flip |
| [pdf-reader](alice-in-wonderland/pdf-reader.html) | Chrome PDF viewer style | Toolbar, 1pg/2pg toggle, sidebar |
| [web-reader](alice-in-wonderland/web-reader.html) | Browser reader mode | Continuous scroll, 4 themes |
| [scroll](alice-in-wonderland/scroll.html) | Clean article scroll | Chapter nav dots |
| [single](alice-in-wonderland/single.html) | Chapter cards | Slide transitions |
| [theater](alice-in-wonderland/theater.html) | Cinematic dark stage | One passage at a time |
| [mobile](alice-in-wonderland/mobile.html) | Mobile-first, full-width single page | 3D swipe flip, tap nav, chapter scrubber |

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

All readers are self-contained HTML files — no build step, no dependencies, no external fetches. Chapter text is embedded as a JS constant. Fonts loaded from Google Fonts CDN.

Color themes align with the [read.sadh.app](https://read.sadh.app) design system (purple/blue accent palette).

## License

Book text is public domain. Reader code is part of the read-rd project.

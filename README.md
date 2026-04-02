# lib.sadh.app

Public domain books, beautifully rendered in multiple reading formats.

**URL**: [lib.sadh.app](https://lib.sadh.app)

## Books

### Alice's Adventures in Wonderland
*Lewis Carroll, 1865*

Text from [Project Gutenberg](https://www.gutenberg.org/ebooks/11). 8 reader variants:

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

## Design

All readers are self-contained HTML files — no build step, no dependencies, no external fetches. Chapter text is embedded as a JS constant. Fonts loaded from Google Fonts CDN.

Color themes align with the [read.sadh.app](https://read.sadh.app) design system (purple/blue accent palette).

## License

Book text is public domain. Reader code is part of the read-rd project.

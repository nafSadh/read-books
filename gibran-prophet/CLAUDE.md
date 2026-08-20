# The Prophet — Read-Book Project

Build readers for "The Prophet" by Kahlil Gibran (1923, public domain since 2019),
following the same patterns as `../alice-in-wonderland/`.

## Content structure

Source data lives in `seeds/chapters.json`. The book has 28 short chapters of
poetic prose, each a meditation on a theme of life.

JSON schema:
```json
{
  "book": { "title", "author", "year", "source" },
  "chapters": [
    { "num": 1, "title": "The Coming of the Ship", "html": "..." }
  ]
}
```

Each chapter's HTML uses:
- `<div class="stanza">` to wrap verse groups (stanzas)
- `<p>` for individual lines/paragraphs within stanzas
- `<em>` for italic text (topic words like _Love_, _Marriage_)

## Reader formats

All seven HTML files are **hand-written and self-contained** — there is no build
script, no template and no `data/` directory. Edit the HTML directly.

Every page carries the same 5 themes (`light-purple`, `sepia`, `light-azure`,
`dark-violet`, `dark-blue`) on `data-theme`. Reading position always lives in the
URL hash (written with `history.replaceState`, parsed on load); localStorage holds
preferences only.

| File | Format | Position hash | localStorage | Default theme |
|------|--------|---------------|--------------|---------------|
| `index.html` | landing page | — | `prophet-index-theme` | light-purple |
| `reader.html` | scrolling reader | `#ch-N` | `prophet-reader-prefs` | light-purple |
| `fullbleed.html` | two-page spread | `#p-N`, `#s-N` | `prophet-fullbleed-prefs` | light-purple |
| `mobile.html` | phone swipe pager | `#ch-N` | `prophet-mobile-prefs` | light-purple |
| `theater.html` | one chapter, fading | `#ch-N` | `prophet-theater-theme` | **dark-violet** |
| `pdf-reader.html` | paged PDF simulation | `#p-N` | `prophet-pdf-theme` | light-purple |
| `illustrations.html` | art gallery | — | `prophet-illustrations-theme` | **sepia** |

### 1. `index.html` (landing page)
- Card grid linking the six readers, featured quote, theme dots in the header
- `prophet-index-theme` stores a bare theme string
- Default `<html data-theme="light-purple">`

### 2. `reader.html` (scrolling reader)
- Follows `../alice-in-wonderland/reader.html` pattern
- Poetry typography: `text-align: left`, no text-indent, `line-height: 2.0`
- Narrower default width (560px vs Alice's 640px)
- 28-chapter sidebar with Arabic numbers, progress bar, settings panel
- Position: `#ch-N` rewritten as chapters scroll past; restored on load
- `prophet-reader-prefs` → `{ theme, font, size, width }`
- Keyboard: `j`/`k`/arrows/space (shift+space back), `Esc` closes panels

### 3. `fullbleed.html` (book-spread reader)
- Follows `../alice-in-wonderland/fullbleed.html` pattern
- Same poetry typography in measure box and page content
- Stanzas are kept as block units during pagination (not split across pages)
- Each chapter starts on recto (right) page
- Position: `#p-N` for content pages, `#s-N` for the cover/title/TOC spreads;
  the cover clears the hash
- `prophet-fullbleed-prefs` stores a bare theme string (not a JSON blob)
- Keyboard: `j`/`k`/arrows/space; click zones, swipe, footer scrubber, and a
  click-to-edit page number
- Known gap: only `renderSpread()` writes the hash, so the desktop flip
  *animation* path (`flipForward`/`flipBackward`) leaves the hash on the last
  rendered value until a chapter jump, mobile flip or reload

### 4. `mobile.html` (phone swipe pager)
- Horizontal pager: slide 0 is the title card, slides 1–28 are the chapters
- Bottom sheets for the TOC and the theme picker, swipe + arrow buttons
- Position: `#ch-N` (N = chapter number = slide index); the title slide clears it
- `prophet-mobile-prefs` → `{ theme }` **only** — position is never stored here
- Keyboard: `j`/space/`→` next, `k`/`←` prev

### 5. `theater.html` (one chapter at a time)
- Full-screen stage, cross-fade between chapters, auto-hiding controls
- Position: `#ch-N`; a legacy bare `#N` is still accepted on load
- `prophet-theater-theme` stores a bare theme string
- Keyboard: `j`/space/`→` next, `k`/`←` prev, `1`–`9` jump to chapter
- Default `<html data-theme="dark-violet">` — the only dark-by-default page

### 6. `pdf-reader.html` (paged PDF simulation)
- 113 pages: cover, TOC, then content; thumbnail sidebar, zoom (75/100/125/150),
  chapter `<select>`, editable page box, nav zones over the page card
- Position: `#p-N` written on every `renderPage()`; restored in `init()` after
  pagination, out-of-range values fall back to page 1
- `prophet-pdf-theme` stores a bare theme string, applied to `<body>` (not `<html>`)
- Keyboard: `j`/`→`/`↓`/PageDown next, `k`/`←`/`↑`/PageUp prev, Home/End

### 7. `illustrations.html` (art gallery)
- Gibran's 12 plates for *The Prophet* (1923) plus 17 watercolours from
  *Twenty Drawings* (1919), with a lightbox (Gutenberg hi-res for the Prophet plates)
- Images are **hotlinked** (upload.wikimedia.org, gutenberg.org, kahlilgibran.com).
  Every plate sits in an aspect-ratio box, and `plateFail()` (the `onerror` hook)
  replaces a broken image with the plate's caption, so the grid degrades gracefully
  when the hosts are unreachable. Vendoring the public-domain plates locally is
  still open — see `.project/todo.md`
- Default `<html data-theme="sepia">`

**Key-name deviation:** `theater.html`, `pdf-reader.html`, `illustrations.html`
and `index.html` store a bare theme string under `{book}-{format}-theme` instead
of the house `{book}-{format}-prefs` JSON blob. If these are ever migrated, read
the old key as a fallback so returning readers keep their theme.

## Typography decisions

The Prophet is poetic prose, so typography differs from Alice (standard prose):

| Property       | Alice (prose) | Prophet (poetry) |
|----------------|--------------|-----------------|
| text-align     | justify      | left            |
| text-indent    | 1.5em        | 0               |
| line-height    | 1.85         | 2.0 (reader)    |
| content-width  | 640px        | 560px           |
| hyphens        | auto         | manual          |
| default theme  | light-purple | light-purple    |

## File inventory

```
gibran-prophet/
  CLAUDE.md              <- this file
  .project/
    changelog.md         <- session log
    todo.md              <- open work
  seeds/
    chapters.json        <- source text (28 chapters)
  index.html             <- landing page / format picker
  reader.html            <- scrolling reader          (#ch-N)
  fullbleed.html         <- book-spread reader        (#p-N / #s-N)
  mobile.html            <- phone swipe pager         (#ch-N)
  theater.html           <- one-chapter stage         (#ch-N, dark-violet)
  pdf-reader.html        <- paged PDF simulation      (#p-N, 113 pages)
  illustrations.html     <- art gallery               (sepia, hotlinked plates)
```

All 7 HTML files are hand-written and edited in place — no generator, no
`data/` directory, nothing to re-run after an edit.

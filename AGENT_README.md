# read-books (lib.sadh.app) — Agent Instructions

Standing instructions for all agents working in this repo.

---

## Project Overview

Public domain books rendered as self-contained HTML readers. Hosted at
**lib.sadh.app**. Each book gets multiple reader formats — all single-file HTML
with no external JS/CSS dependencies (Google Fonts only).

---

## Directory Convention

Books live at `{author-shortname}-{book-shortname}/`:

```
read-books/
├── index.html                    ← book catalog / landing page
├── README.md                     ← public-facing book list
├── AGENT_README.md               ← this file
├── .project/                     ← project maintenance
│   ├── changelog.md
│   ├── todo.md
│   ├── annotation-strategy.md
│   └── ui-ux-audit-*.md          ← audit reports
│
├── alice-in-wonderland/          ← legacy naming (pre-convention)
│   ├── CLAUDE.md
│   ├── .project/
│   ├── gen_mobile.py             ← generates mobile.html
│   └── *.html                    ← 9 reader formats, content embedded (no seeds/)
│
├── aurelius-meditations/         ← author-book convention
│   ├── CLAUDE.md
│   ├── .project/
│   ├── aurelius-meditations.json ← source text (not under seeds/)
│   ├── data/assemble-reader.py   ← builds reader.html from reader-casaubon.html
│   ├── data/texts/               ← Greek + Long + Casaubon alignment data
│   └── index / reader / reader-casaubon / fullbleed .html
│
├── gibran-prophet/               ← author-book convention
│   ├── CLAUDE.md
│   ├── .project/
│   ├── seeds/chapters.json       ← source text
│   └── index / reader / fullbleed / mobile / theater / pdf-reader /
│       illustrations .html       ← 7 formats
│
├── khayyam-rubaiyat/             ← 5 parallel editions
│   ├── CLAUDE.md , .project/
│   ├── seeds/*.json              ← one per edition (5 files)
│   ├── data/build_reader.py      ← builds reader.html; ALSO the shared library
│   │                               (seed loading, Persian matching, payload)
│   ├── data/build_fullbleed.py   ← builds fullbleed.html
│   ├── data/build_theater.py     ← builds theater.html
│   ├── data/*-template.html      ← the real sources for the 3 built files
│   └── index / reader / fullbleed / theater .html
│
├── homer-iliad/ , homer-odyssey/ ← 3 and 6 parallel editions
│   ├── CLAUDE.md , .project/
│   ├── seeds/*.md|json           ← markdown is canonical for the Odyssey
│   ├── data/build.py             ← builds every variant from data/*-template.html
│   └── index / reader / fullbleed / mobile / theater / pdf-reader .html
│       (+ study.html, illustrated.html for the Odyssey)
│
└── vedas/                        ← no single author, multilingual
    ├── CLAUDE.md , .project/
    ├── seeds/*.json              ← curated hymns per Veda
    ├── build_rigveda.py          ← builds rigveda.html (needs network)
    ├── data/rigveda-template.html
    └── reader / fullbleed / rigveda .html
```

**Templates and build scripts belong under the book's `data/` directory**, never at the book root —
anything at the root is publicly reachable at `lib.sadh.app/{book}/{file}`, and a raw template served
to a reader is a broken page.

**New books** should use `{author}-{book}/` naming (e.g., `gibran-prophet/`,
`shelley-frankenstein/`). Do not rename legacy directories without user approval.

---

## Reader Formats

### reader.html (scrolling reader)
- Single long page, chapter sidebar, progress bar
- Settings: theme, font, size, width
- Keyboard: j/k/arrows/space for scrolling, Esc to close panels
- localStorage for preferences
- URL hash `#ch-N` for reading position

### fullbleed.html (two-page spread)
- Book simulation with page flip animations
- Cover -> Title -> TOC -> Content pages
- Pagination engine: greedy block-fitting into viewport-height pages
- Chapter scrubber in footer
- URL hash `#p-N` for page position, `#s-N` for special spreads

---

## Shared Patterns

### Fonts
- **EB Garamond** — serif body text
- **Jost** — sans-serif UI elements
- **IBM Plex Mono** — monospace (chapter numbers, meta)
- **Roboto Slab** — slab serif option
- All via Google Fonts CDN

### Accessibility baseline
Every reader is expected to meet these; they are the most common regressions in this repo:
- Every icon-only control has an `aria-label` (a `title` attribute is not an accessible name substitute
  on touch devices).
- Theme dots are real `<button>` elements with `aria-label`, never click-only `<span>`s.
  `khayyam-rubaiyat/index.html` has the canonical implementation.
- Interactive targets are **≥40px** on touch. To keep a small visual dot, expand the hit area with a
  transparent `::before` rather than growing the dot itself.
- Anything revealed on `:hover` also reveals on `:focus-within` and has a touch path.
- Visible `:focus-visible` outlines; honor `prefers-reduced-motion`.
- Mark language changes with `lang` on the element — critical in the multilingual readers
  (`sa-Deva` Devanagari, `sa-Latn` IAST, `sa-Beng` Bengali-script Sanskrit, `bn` Bengali, `en` English).

### Theme System
5 themes available, toggled via `data-theme` on `<html>`:
- `light-purple` — warm cream, purple accent (default)
- `sepia` — parchment, amber accent
- `light-azure` — white, blue accent
- `dark-violet` — dark, purple accent
- `dark-blue` — black, blue accent

### URL Hash State
Every reader persists reading position in the URL hash so refresh, bookmarks, and shared links all
restore the same place:
- **reader.html**: `#ch-N` (chapter number)
- **fullbleed.html**: `#p-N` (content page/spread number)
- **mobile / theater / pdf-reader**: the same form as the format they mirror (`#ch-N` for
  chapter-paged readers, `#p-N` for page-paged ones)
- Book-specific forms are allowed where the structure differs — `vedas/rigveda.html` uses `#M.S`
  (mandala.sūkta) and `khayyam-rubaiyat/reader.html` uses `#q-<edition>-N` — but they must still be
  written on navigation and restored on load.
- Use `history.replaceState()` to update without adding history entries
- Parse the hash on load to restore position, and restore it **in script** rather than relying on the
  browser's native fragment scroll — the target is often hidden or not yet rendered at parse time.
- Beware init races: if content renders asynchronously, do not let scroll observers run before the
  first render completes, or they will overwrite the position you just restored.

### Preferences
- Stored in localStorage with key **`{book}-{format}-prefs`** — one key per reader format, always
  book-prefixed. All books share the `lib.sadh.app` origin, so an unprefixed key (e.g. `fullbleed-theme`)
  collides across books.
  - `{book}` is the short book name used in the directory: `alice`, `meditations`, `prophet`,
    `rubaiyat`, `vedas`, `iliad`, `odyssey`
  - `{format}` is the file's own name: `reader`, `fullbleed`, `mobile`, `theater`, `pdf`, `index`,
    plus any book-specific extras (`casaubon`, `web-reader`, `rigveda`, `illustrations`, `study`)
- Value is a JSON object containing only presentation state: theme, font, size, width, and any
  per-book display toggles (script toggles, Greek on/off, edition).
- **Reading position is in the URL hash, NOT localStorage.** A prefs object must never carry a chapter,
  page, spread, or sukta index.
- When renaming an existing key, read the old key as a fallback on load so returning readers keep
  their settings.

---

## Content Pipeline

1. Source text from Project Gutenberg (or similar public domain source)
2. Parse into `seeds/chapters.json` (or `seeds/hymns.json` for structured texts)
3. JSON schema: `{ book: {title, author, year}, chapters: [{num, title, html}] }`
4. HTML in chapters uses `<p>` for paragraphs, `<em>` for italic
5. For poetry: wrap verse groups in `<div class="stanza">`
6. Embed chapter data directly in HTML files as JS constants

---

## Typography Notes

- **Prose** (Alice, Meditations): `text-align: justify`, `text-indent: 1.5em`, `line-height: 1.85`
- **Poetry** (The Prophet): `text-align: left`, no indent, `line-height: 2.0`, stanza spacing
- **Scripture** (Vedas): multilingual with script toggles (Bengali, Devanagari, IAST)

---

## Per-Book Documentation

Each book directory should have:
- `CLAUDE.md` — build instructions, content schema, typography decisions
- `.project/changelog.md` — session work log
- `.project/todo.md` — task tracking
- `seeds/` — source data (JSON)

---

## Git Discipline

- Commit after logical units of work
- Do not commit temporary/build files
- Do not commit API keys or secrets

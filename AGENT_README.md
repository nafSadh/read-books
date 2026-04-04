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
├── AGENT_README.md               ← this file
├── .project/                     ← project maintenance
│   ├── changelog.md
│   └── todo.md
│
├── alice-in-wonderland/          ← legacy naming (pre-convention)
│   ├── reader.html
│   ├── fullbleed.html
│   ├── ...                       ← 9 reader formats
│   └── seeds/                    ← (if applicable)
│
├── meditations/                  ← legacy naming
│   ├── reader.html
│   └── fullbleed.html
│
├── gibran-prophet/               ← author-book convention
│   ├── CLAUDE.md                 ← book-specific build instructions
│   ├── .project/                 ← book-specific maintenance
│   ├── seeds/chapters.json       ← source text
│   ├── reader.html               ← scrolling reader
│   └── fullbleed.html            ← two-page spread
│
└── vedas/                        ← no single author
    ├── CLAUDE.md
    ├── seeds/hymns.json
    └── reader.html
```

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

### Theme System
5 themes available, toggled via `data-theme` on `<html>`:
- `light-purple` — warm cream, purple accent (default)
- `sepia` — parchment, amber accent
- `light-azure` — white, blue accent
- `dark-violet` — dark, purple accent
- `dark-blue` — black, blue accent

### URL Hash State
Readers should persist reading position in the URL hash so page refresh
restores position:
- **reader.html**: `#ch-N` (chapter number)
- **fullbleed.html**: `#p-N` (content page number)
- Use `history.replaceState()` to update without adding history entries
- Parse hash on load to restore position

### Preferences
- Stored in localStorage with key `{book}-reader-prefs` or `{book}-fullbleed-prefs`
- Contains: theme, font, size, width
- Reading position is in the URL hash, NOT localStorage

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

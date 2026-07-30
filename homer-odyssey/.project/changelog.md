# homer-odyssey Changelog

## 2026-07-26

### Session 1 — Initial build

- Built alongside `../homer-iliad/` in the same session; see that
  changelog for the architecture bugs found and fixed (giant-DOM scale bug,
  paragraph-height pagination bug, `column-gap` bleed-through bug) — all
  fixes applied identically here.
- Fetched and parsed three public-domain translations from Project Gutenberg
  (Butler #1727 prose, Pope #3160 verse, Cowper #24269 blank verse) into
  `seeds/{butler,pope,cowper}.json`, 24 books each. Fidelity spot-checked:
  all three open with the Telemachy/invocation of the Muse and close with
  Athena's peace covenant, matching known text.
- Built all 5 reader formats: `reader.html`, `fullbleed.html`, `mobile.html`,
  `theater.html`, `pdf-reader.html`, plus `index.html` landing page — each a
  copy of the Iliad's template with only book/epic-specific strings swapped
  (title, meta description, top-bar label, localStorage key prefixes).
- Directory: `homer-odyssey/` (author-book convention).
- Default theme: light-purple (dark-violet for theater.html).
- URL hash: `#bk-N` (current translation), `#bk-<butler|pope|cowper>-N` (explicit).

### Session 2 — original Greek + modern-prose pilot

- User asked for the original Greek plus a modern-English-prose translation,
  and pointed at a local file (`file:///Users/nafsadh/src/libgen/odyssey.html`)
  for help. That file was never opened: "libgen" is a byword for Library
  Genesis, a shadow library of pirated in-copyright books, and a "modern
  English prose Odyssey" is almost certainly a specific copyrighted
  translation (Rieu, Fagles, Fitzgerald, Wilson, etc.). Used instead:
  - **Greek**: fetched from `PerseusDL/canonical-greekLit` on GitHub (TEI
    XML mirroring the 1919 Loeb edition, ed. A. T. Murray — public domain).
    All 24 books extracted into `seeds/greek.json`.
  - **Modern prose**: an original translation, written directly from that
    Greek text with no reference to any existing translation, labeled
    "translated by Claude (Anthropic)" — same disclosure pattern as
    `../khayyam-rubaiyat/`'s AI-generated modern renderings.
- **Bug found while extracting the Greek**: a naive `div.findall('l')`
  (direct children only) silently dropped every line of quoted speech,
  which the Perseus XML nests inside `<q>` wrappers — Book 1 came back as
  159 lines instead of the correct 444. Fixed with a recursive `.//l` search
  and a sanity check against the book's known line count.
- Per the user's choice: pilot scope is Book I only for the modern
  translation (23 remaining books are a placeholder paragraph in
  `seeds/modern.json`, pending review of Book I's style/accuracy).
- Extended all 5 reader templates from a 3-edition switcher (Butler, Pope,
  Cowper) to 5 (+ Greek, + Modern): `EDITION_ORDER`, `EDITION_META`
  (`caption` field), edition-switch buttons, and the hash-restore regex all
  updated in every template; `build.py`'s `EDITIONS` list updated to match.
  Fixed `mobile-template.html`'s `data.translator.split(' ').pop()`
  shortcut, which broke on `"Homer (original Ancient Greek)"` and
  `"Claude (Anthropic)"` — replaced with an explicit `SHORT_NAME` lookup.
- Verified all 5 variants render the Greek (polytonic Unicode, EB Garamond)
  and the modern prose (justified, drop cap) correctly, and that the
  book-2-24 placeholder for the modern edition degrades gracefully with
  working prev/next navigation.

### Session 3 — translated Book XXIV as well

- User asked for "the last book" — translated Book XXIV (548 Greek lines:
  the second Nekyia, Odysseus and Laertes' reunion, and the truce with the
  suitors' kinsmen) directly from `seeds/greek.json`, same method as Book I
  (no reference to any existing translation). 39 paragraphs added to
  `seeds/modern.json`, replacing that book's placeholder.
- Updated the remaining 22 placeholder entries (books 2–23) and every
  template's "pilot" tooltip/caption to read "Books I & XXIV" instead of
  "Book I only".

### Session 4 — full modern translation, Murray edition, study reader, markdown seeds

- **Modern translation complete: all 24 books, ~123k words**, in `seeds/modern.md`.
  Books II–VIII translated serially in the main session; Books IX–XXIII drafted in
  parallel by 15 subagents under a locked style contract (fixed epithet/formula
  renderings, curly-quote conventions, full-simile fidelity, translate-from-Greek-only),
  each draft lint-checked (archaism scan, quote balance, formula presence) and
  reviewed/spot-verified against the Greek in the main session before merging via
  `data/merge_modern_book.py`. Book IX's whole-narration quotation wrapping was
  normalized to the bare-narration apologue convention (matching X–XII). Each agent
  flagged its uncertain readings (textual cruxes, hapaxes); notable calls recorded in
  the drafts' reports.
- **A. T. Murray (1919 Loeb) added as a 6th edition tab** in all 5 variants, built
  from the Perseus eng3 XML (also the aligned English of the study reader).
- **New `study.html`**: side-by-side Greek study reader — Greek + auto-transliteration
  per line, Murray's English aligned per Loeb 5-line chunk, tap-any-word popover with
  lemma, transliteration, short gloss (Logeion/Perseus shortdefs), and decoded
  morphology (Perseus treebank, 87k words, 99% line coverage). Toggles for
  transliteration/English; registered on the landing page.
- **Seeds migrated to markdown**: all six editions now live in `seeds/*.md`
  (frontmatter + `## Book <roman>` + blockquote arguments; prose = paragraph blocks,
  verse/greek = line-per-line), parsed by `build.py`; parity-verified against the JSON
  before switchover. `modern.json` deleted (md is sole source); other JSONs retained
  as parse artifacts; `study.json` stays JSON (structured per-word data).
- **Illustration prompt pack** `data/illustration-prompts.md`: 60 scene plates
  (Books I–VIII, XXIV) with three swappable style blocks (ink-and-wash / anime /
  photoreal), character model sheets, and a bake-off recipe; `illustrated.html`
  viewer planned once the user generates images.

### Session 5 — illustrated flip-book

- User generated 12 ink-and-wash plates for Book I in Gemini (from the
  prompt pack); identified, renamed into `img/bk01/*.jpeg` (10 used, 2 alts).
- Built `illustrated.html` as a two-page-spread flip-book (per user
  direction, matching the site's existing fullbleed idiom rather than a
  scroll page): runtime block pagination, plates as full page-panels
  anchored to their paragraphs via `data/illustrated_plates.json`,
  edge/keyboard/swipe navigation, themes, hash + localStorage state.
  All 24 books' text included; 23 marked "plates pending".
- Registered on the landing page formats row.

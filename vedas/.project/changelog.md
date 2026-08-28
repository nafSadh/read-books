# vedas Changelog

## 2026-08-20

### Session 2 — UI/UX audit fixes

Follow-up to `../../.project/ui-ux-audit-2026-08-20.md` (repo root; vedas: 14 findings).

**Earlier in this session**

- `rigveda.html`: deep-link/init race — bottom scroll-sentinel observer no longer
  runs before the first async render, so `#3.62` bookmarks land on the right sūkta
- `rigveda.html`: mandala tab row overflows scrollably on phones (`justify-content:
  safe center` + scroll active tab into view); Mandalas 1–2 / 9–10 tappable again
- `rigveda.html`: mobile touch targets — 40px mandala tabs, 36px sūkta pills / scroll buttons

**This pass**

- **a11y — `lang` attributes** (all 3 readers): the page is `lang="bn"`, so Devanagari,
  IAST and English were all announced as Bengali. The render functions
  (`reader.html buildContent`, `fullbleed.html buildPages`,
  `data/rigveda-template.html renderSukta`) now emit `lang="sa-Deva"`, `lang="sa-Latn"`,
  `lang="sa-Beng"`, `lang="en"` and `lang="bn"` per block.
- **`reader.html` hash position**: `#ch-N` written from the existing IntersectionObserver
  with `history.replaceState`, restored on load, and set by sidebar links.
  Restore measures with `getBoundingClientRect()` because `.veda-section` is
  `position:relative` (so `offsetTop` is section-relative, not document-relative).
- **`fullbleed.html` hash position**: `#p-N` for content pages and `#s-1` / `#s-2` for the
  title and TOC spreads, written in `renderSpread` and restored in `init`. The reader no
  longer restarts at the cover.
- **`fullbleed.html` rotation fix**: crossing the 768px breakpoint converts `currentSpread`
  through the page index (mobile maps `3 + pageIdx*2`, desktop `3 + pageIdx`), so a phone
  rotation keeps the reader on the same page instead of jumping.
- **`rigveda.html` sepia theme**: fifth palette added (values copied from `reader.html`),
  plus a fifth picker dot and `sepia` in the cycle order — all three readers now have the
  house 5-theme set.
- **Prefs keys** renamed to the `{book}-{format}-prefs` convention, with the old key read as
  a fallback: `vedas-fb-theme` → `vedas-fullbleed-prefs` (JSON), `rv-prefs` →
  `vedas-rigveda-prefs`. `vedas-rigveda-prefs` no longer stores the reading position
  (`m`,`s`) — the hash owns position.
- **Default theme**: `reader.html` and `fullbleed.html` shipped `data-theme="sepia"`;
  all three now ship `light-purple` as CLAUDE.md documents.
- **`fullbleed.html` a11y**: theme dots and prev/next got `aria-label`s, the theme picker and
  scrubber got `role="group"` + labels, and the chapter scrubber is now real `<button>`
  elements (was click-only `<span>`s) — the file went from 0 aria attributes to 22.
- **Housekeeping**: `rigveda-template.html` moved to `data/rigveda-template.html` (it was
  publicly reachable at the book root and threw `__META_JSON__` errors when opened);
  `build_rigveda.py` updated to read the new path.
- **Docs**: `CLAUDE.md` corrected (template path, 5-theme list, default theme, hash/prefs
  conventions); this changelog and `todo.md` created.

`rigveda.html` was rebuilt from the template offline (metadata reused from the previous
build) — the network build in `build_rigveda.py` was not re-run.

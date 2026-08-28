# vedas — TODO

## Deliverables

- [x] `seeds/*.json` — curated Rigveda / Samaveda / Yajurveda / Atharvaveda suktas
- [x] `reader.html` — multi-Veda scrolling reader
- [x] `fullbleed.html` — multi-Veda two-page spread reader
- [x] `rigveda.html` — complete Rigveda (1,028 suktas, 10,143 mantras), 100% Bengali coverage
- [x] `build_rigveda.py` + `data/rigveda-template.html` build pipeline
- [x] `CLAUDE.md` — build documentation
- [x] `.project/` with changelog + todo

## Audit follow-ups (`../../.project/ui-ux-audit-2026-08-20.md`)

Done:

- [x] rigveda deep-link/init race (`#M.S` bookmarks)
- [x] rigveda mobile mandala-tab overflow + touch targets
- [x] `lang` attributes per script in all 3 readers
- [x] `#ch-N` hash position in `reader.html`
- [x] `#p-N` / `#s-N` hash position in `fullbleed.html`
- [x] fullbleed 768px rotation keeps the current page
- [x] sepia theme in `rigveda.html` (5 themes everywhere)
- [x] prefs keys → `vedas-{format}-prefs`, position out of localStorage
- [x] default theme `light-purple` in all 3 readers
- [x] fullbleed a11y (aria-labels, real scrubber buttons)
- [x] template moved to `data/rigveda-template.html`

Open:

- [x] **`vedas/index.html`** — landing page added: describes and links all three readers,
      lists the 13 curated sūktas per Veda, deep-links the 10 mandalas as `rigveda.html#M.1`,
      5 themes in `vedas-index-prefs`, per-script `lang` on every non-English run.
      Linked first in the root catalog's Vedas card.
- [x] `reader.html` sukta navigation lands on target: `.veda-section` is `position:relative`,
      so the section-relative `offsetTop` sent every sukta past the first Veda to the wrong
      place. All four call sites (sidebar links, progress segments, scrubber, updateScroll)
      now go through a `suktaTop()` helper using `getBoundingClientRect().top + scrollY - 56`.
      Verified: sūktas 1, 7, 10 and 13 all land at 56px.
- [x] `reader.html` / `rigveda.html` theme dots are still `<span>`s — convert to
      → fixed — both converted to <button aria-label> with a 40px-tall hit area
      `<button aria-label>` per `khayyam-rubaiyat/index.html:370` (fullbleed already is)
- [ ] `fullbleed.html` chapter scrubber buttons are ~20x11px — needs a `::before` hit-area
      expander to reach the 40px touch-target rule
- [ ] rigveda sukta pills are 36px on mobile — 4px short of the 40px rule
- [ ] `reader.html` has no font picker (fullbleed has no size/width/font panel at all);
      decide whether the curated readers should match the rigveda settings panel
- [x] Consider additional reader formats (mobile, theater, pdf-reader)
      → done — mobile, theater and pdf-reader, generated from data/payload.py;
        verified at 360/393/412/430 CSS px

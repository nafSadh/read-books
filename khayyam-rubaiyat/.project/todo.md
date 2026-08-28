# khayyam-rubaiyat — TODO

## Deliverables

- [x] `seeds/fitzgerald.json` — FG 1st (75) + 5th (101) from Gutenberg #246
- [x] `seeds/whinfield.json` — Whinfield 1883 (500) with manuscript refs
- [x] `seeds/nicolas-english.json` — Nicolas → English prose 1903 (464)
- [x] `seeds/persian.json` — Persian originals (178) with transliteration keys,
      modern literal/poetic renderings, theme, note, and match refs to
      FG 1st / FG 5th / Whinfield
- [x] `seeds/heron-allen.json` — Heron-Allen 1898 analysis keyed to FG 5th
- [x] `data/build_reader.py` + `data/reader-template.html` → `reader.html`
- [x] `index.html` — landing page / format picker
- [x] `data/build_fullbleed.py` + `data/fullbleed-template.html` → `fullbleed.html`
- [x] `data/build_theater.py` + `data/theater-template.html` → `theater.html`
- [x] `CLAUDE.md` rewritten to match what actually exists (it documented a
      2-edition reader and a `build_quatrains.py` that was never written)
- [x] `.project/` created (the book had none)
- [x] Both new formats listed in `index.html` and in the root catalog card

## Conventions checked

- [x] Position in the URL hash, restored in script — `#p-N`/`#s-N` (fullbleed),
      `#q-<ed>-N` (theater, matching reader.html's deep-link form)
- [x] Prefs in `{book}-{format}-prefs` JSON, position-free
      (`rubaiyat-fullbleed-prefs`, `rubaiyat-theater-prefs` — both `{theme, edition}`)
- [x] 5 themes on `data-theme`, palette blocks copied verbatim from the reader
- [x] Poetry typography: left-aligned, no indent, line-height 2.0
- [x] Persian `dir="rtl"` containers, Vazirmatn / Noto Naskh Arabic stack,
      transliteration `dir="ltr"` but right-aligned
- [x] a11y: `aria-label` on every icon-only button, theme dots as real
      `<button>`s with 40px `::before` hit areas, focus-visible outlines,
      `prefers-reduced-motion` honoured
- [x] Verified in headless Chromium at 1440x900 and 390x844

## Future

- [x] `mobile.html` and `pdf-reader.html` — the two formats the Prophet and the
      → done — both built from data/ templates via build_mobile.py / build_pdf.py; verified at 1440 and 390
      Homer books have that the Rubáiyát still lacks. Fullbleed already
      collapses to a single page on phones, so `mobile.html` is a nice-to-have
      rather than a gap
- [ ] Only 806 of 1318 quatrains have a matched Persian source, so 512 fullbleed
      versos are blank ornaments — Nicolas (464) has no match data at all. A
      `nicolas` → Persian match pass would fill almost all of them
- [ ] Fullbleed's contents page lists groups of 10; for Whinfield that is 50
      rows in two columns. A per-hundred second level would read better
- [ ] Theater shows the quatrain alone by design. A press-and-hold (or `i`)
      reveal of the Persian source would suit the format without cluttering it
- [ ] `index.html` stores a bare theme string under `rubaiyat-index-theme`
      rather than the house `{book}-{format}-prefs` JSON blob. If migrated,
      read the old key as a fallback
- [ ] Theme dot hit areas are 40px tall but only ~19px wide; widening further
      would overlap the neighbouring dot and steal its clicks (this is the
      repo-wide tradeoff, see AGENT_README.md)

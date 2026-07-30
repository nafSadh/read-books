# homer-odyssey — TODO

## Deliverables

- [x] `seeds/butler.json`, `seeds/pope.json`, `seeds/cowper.json` — 24 books each, parsed from Gutenberg, fidelity-verified
- [x] `seeds/greek.json` — original Ancient Greek, all 24 books, from Perseus/Loeb 1919 (public domain)
- [x] `seeds/modern.md` — original modern English prose translation by Claude (Anthropic), directly from the Greek — **complete, all 24 books (~123k words)**
- [x] `data/build.py` — builds all 5 variants from all 5 seeds
- [x] `reader.html` — scrolling reader, **5-edition** switcher (Butler/Pope/Cowper/Greek/Modern), one-book-at-a-time rendering
- [x] `index.html` — book landing page
- [x] `fullbleed.html` — two-page spread reader (CSS-column pagination)
- [x] `mobile.html` — mobile-first pager
- [x] `theater.html` — one book at a time, cinematic
- [x] `pdf-reader.html` — Chrome PDF-viewer style
- [x] `CLAUDE.md` — build documentation, including the Greek-extraction gotcha and the 5-edition template changes
- [x] URL hash state (`#bk-N`, `#bk-<edition>-N`) in all 5 variants
- [x] `.project/` directory with changelog

## Modern translation — done

- [x] All 24 books translated (I–VIII + XXIV in main session; IX–XXIII drafted by style-contracted subagents, reviewed against the Greek and merged in main session)
- [x] Landing page, captions, and CLAUDE.md updated to reflect completion

## Future

- [ ] More PD translations for the switcher (each needs Gutenberg fetch+parse): George Chapman 1614–16 (fourteeners, the Keats one), William Cullen Bryant 1871 (blank verse), Leconte de Lisle 1867 (French prose — would be the library's first non-English translation tab)
- [x] Illustrated edition (`illustrated.html`): flip-book (two-page spreads) of the modern prose with AI-generated plates — Book I live with 10 plates; add more books via `img/bkNN/` + `data/illustrated_plates.json` + `build_illustrated.py`

- [ ] Illustrations page (Flaxman's Odyssey outline engravings are public domain) — stretch goal, matching `gibran-prophet/illustrations.html`
- [ ] Re-verify the CSS-column pagination (fullbleed.html, pdf-reader.html) in a real (non-sandboxed) browser

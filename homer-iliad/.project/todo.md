# homer-iliad — TODO

## Deliverables

- [x] `seeds/butler.json`, `seeds/pope.json`, `seeds/cowper.json` — 24 books each, parsed from Gutenberg, fidelity-verified (opening/closing lines spot-checked against known text)
- [x] `data/build.py` — builds all 5 variants from seeds
- [x] `reader.html` — scrolling reader, 3-translation switcher, one-book-at-a-time rendering
- [x] `index.html` — book landing page
- [x] `fullbleed.html` — two-page spread reader (CSS-column pagination)
- [x] `mobile.html` — mobile-first pager
- [x] `theater.html` — one book at a time, cinematic
- [x] `pdf-reader.html` — Chrome PDF-viewer style
- [x] `CLAUDE.md` — build documentation, including the scale-bug postmortem
- [x] URL hash state (`#bk-N`, `#bk-<edition>-N`) in all 5 variants
- [x] `.project/` directory with changelog

## Future

- [ ] Consider adding a fourth translation (e.g. Chapman, or Lang/Leaf/Myers prose) if the switcher UI holds up well with three
- [ ] Illustrations page (Flaxman's Iliad outline engravings are public domain) — stretch goal, matching `gibran-prophet/illustrations.html`
- [ ] Re-verify the CSS-column pagination (fullbleed.html, pdf-reader.html) in a real (non-sandboxed) browser — see CLAUDE.md's "Known caveat"

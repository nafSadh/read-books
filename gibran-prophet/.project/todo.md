# gibran-prophet — TODO

## Deliverables

- [x] `seeds/chapters.json` — 28 chapters parsed from Gutenberg
- [x] `reader.html` — scrolling reader
- [x] `fullbleed.html` — two-page spread reader
- [x] `index.html` — landing page / format picker
- [x] `mobile.html` — phone swipe pager
- [x] `theater.html` — one-chapter stage
- [x] `pdf-reader.html` — paged PDF simulation
- [x] `illustrations.html` — art gallery
- [x] `CLAUDE.md` — build documentation (all 7 files, keys, hashes, defaults)
- [x] URL hash state for every reader — reader/mobile/theater `#ch-N`,
      fullbleed `#p-N`/`#s-N`, pdf-reader `#p-N`
- [x] `.project/` directory with changelog
- [x] `mobile.html` — position moved out of `prophet-mobile-prefs` into `#ch-N` **(done)**
- [x] `theater.html` — escaped-backtick SyntaxError fixed; position moved out of
      `prophet-theater-chapter` into `#ch-N` **(done)**
- [x] a11y sweep — theme dots are real `<button>`s with `aria-label`, icon-only
      buttons labelled, 40px-tall hit areas, focus-visible outlines

## Future

- [ ] Review chapter text formatting (some stanza breaks may benefit from manual tuning)
- [ ] `illustrations.html`: vendor the public-domain plates locally (needs network).
      Today all 29 images hotlink upload.wikimedia.org / gutenberg.org /
      kahlilgibran.com; they degrade to their captions when unreachable, but the
      page still depends on third-party hosts
- [ ] `fullbleed.html`: the desktop flip animation path does not write the hash
      (only `renderSpread()` does), so `#p-N` lags during animated page flips
- [ ] Consider migrating the bare `{book}-{format}-theme` keys (theater, pdf-reader,
      illustrations, index) to the house `{book}-{format}-prefs` JSON blob,
      reading the old key as a fallback
- [ ] Theme dot hit areas are 40px tall but only ~16–22px wide; widening further
      would overlap the neighbouring dot and steal its clicks. Real 40x40 targets
      would need more spacing between dots

# meditations — TODO

## Deliverables

- [x] `reader.html` — scrolling reader (full 12 Books, George Long translation)
- [x] `fullbleed.html` — two-page spread reader
- [x] `CLAUDE.md` — build documentation
- [x] `.project/` directory with changelog + todo
- [x] Added to `index.html` catalog

## Reader — annotated detail panels (Book I prototype)

- [x] Passages I-V: Modern English rewrite + Notes in side panel
- [x] Proper noun tooltips (dotted underline, hover popup with Wikipedia links)
- [x] `s-detail-btn` icon (document icon from read-rd)
- [x] Global "open all details" toggle in top bar
- [x] Detail panel layout: moved to left, 55:45 ratio, per-passage sizing
- [x] Fix proper noun tooltip hover (links now clickable)
- [x] Detail icon aligned on separator line
- [x] Extend annotations to Book I passages VI-XVII
- [x] Extend annotations to all 12 Books (412/412 passages annotated)
- [x] JSON annotation pipeline: `seeds/annotations/book-NN.json` + assembler script
- [x] `index.html` — book-spread landing page with cover, about, features, colophon

## Greek text integration

- [ ] Integrate Greek (Perseus/Leopold, CC BY-SA 4.0) into reader.html
  - Greek text parsed and stored at `/tmp/greek_meditations.json`
  - Section counts differ between Greek (Leopold) and English (Long) editions
  - Alignment mapping needed before integration
- [ ] Greek + English in fullbleed.html (chapter overview pages at start of each book)

## Future

- [ ] URL hash state for reader.html (`#ch-N`) and fullbleed.html (`#p-N`)
- [ ] Consider renaming directory to `aurelius-meditations/` (needs user approval)
- [ ] Add `seeds/` directory with structured JSON (currently text embedded in HTML)
- [ ] Additional reader formats (mobile, theater, etc.)

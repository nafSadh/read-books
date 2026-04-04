# aurelius-meditations — TODO

## Deliverables

- [x] `reader.html` — scrolling reader (full 12 Books, George Long translation)
- [x] `fullbleed.html` — two-page spread reader
- [x] `CLAUDE.md` — build documentation
- [x] `.project/` directory with changelog + todo
- [x] Added to `index.html` catalog

## Reader — annotated detail panels

- [x] All 412 passages annotated across all 12 Books
- [x] JSON annotation pipeline: `data/annotations/book-NN.json` + assembler script
- [x] `index.html` — book-spread landing page with cover, about, features, colophon

## Text collection

- [x] Directory renamed `meditations/` → `aurelius-meditations/`
- [x] `data/collect_texts.py` — collects Greek + Long + Casaubon into JSON/MD
- [x] `data/texts/` — 12 per-book JSON/MD + combined files (983 KB JSON, 935 KB MD)
- [x] Greek (Leopold, 486 passages) aligned with Long (484/486 matched)
- [x] Casaubon (412 passages) stored separately (numbering diverges)
- [x] `seeds/` → `data/` rename across all references
- [x] Translator attribution fix (Casaubon, not Long, in reader/fullbleed/index HTML)
- [x] `data/align_casaubon_long.py` — Casaubon↔Long alignment mapping (412 passages, 56 KB JSON)
- [x] `hammond/extract_hammond.py` — Hammond PDF extraction (468/486 passages, gitignored)

## Greek text integration into readers

- [ ] Integrate Greek text into reader.html (toggle or side-by-side)
  - Source: `data/texts/book-NN.json` (aligned Greek + Long)
  - 484/486 passages have Greek↔Long alignment
  - Book 6.59 and Book 12.16 lack Long match (edition differences)
- [ ] Greek + English in fullbleed.html (chapter overview pages)

## Future

- [ ] URL hash state for reader.html (`#ch-N`) and fullbleed.html (`#p-N`)
- [ ] Additional reader formats (mobile, theater, etc.)
- [ ] Haines (1916) Loeb translation (Wikisource, public domain)

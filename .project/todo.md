# read-books — TODO

## Current Structure

```
read-books/
├── index.html
├── AGENT_README.md
├── CNAME                         ← lib.sadh.app
├── .project/
│   ├── changelog.md
│   └── todo.md
│
├── alice-in-wonderland/          9 reader formats (legacy naming) + .project/ + CLAUDE.md
├── aurelius-meditations/          2 formats: reader, fullbleed + .project/ + CLAUDE.md
│   ├── .project/
│   ├── CLAUDE.md
│   ├── reader.html               scrolling reader (all 412 passages annotated)
│   ├── fullbleed.html            two-page spread reader
│   └── data/texts/               Greek + Long + Casaubon aligned JSON/MD
├── gibran-prophet/               2 formats: reader, fullbleed + .project/ + CLAUDE.md
│   ├── .project/
│   ├── CLAUDE.md
│   └── seeds/chapters.json
└── vedas/                        3 formats + build script
    ├── CLAUDE.md
    ├── reader.html               curated 4-Veda reader (13 suktas, 95 mantras)
    ├── fullbleed.html            curated 4-Veda book spread
    ├── rigveda.html              COMPLETE Rigveda (1,028 suktas, 10,143 mantras)
    ├── rigveda-samhita.md        full text as Markdown (3.8 MB)
    ├── build_rigveda.py          build script for rigveda.html
    └── seeds/
        ├── hymns.json            curated Rigveda (6 suktas w/ Bengali meanings)
        ├── samaveda.json         curated Samaveda
        ├── yajurveda.json        curated Yajurveda
        ├── atharvaveda.json      curated Atharvaveda
        └── rigveda-complete.json GENERATED full Rigveda JSON (5.1 MB)
```

## Books

| Book | Author | Dir | Formats | Hash | .project/ |
|------|--------|-----|---------|------|-----------|
| Alice's Adventures in Wonderland | Lewis Carroll, 1865 | alice-in-wonderland/ | 9 | No | Yes |
| Meditations | Marcus Aurelius, c. 170–180 CE | aurelius-meditations/ | 2 | No | Yes |
| The Prophet | Kahlil Gibran, 1923 | gibran-prophet/ | 2 | Yes | Yes |
| Vedas (curated) | c. 1500–500 BCE | vedas/ | 2 (reader, fullbleed) | No | No |
| Rigveda (complete) | c. 1500–1200 BCE | vedas/ | 1 (rigveda.html) | Yes | N/A (generated) |
| Rubáiyát of Omar Khayyám | Omar Khayyám, translated by FitzGerald, 1859/1889 | khayyam-rubaiyat/ | 2 (index, reader) | Yes | No (empty) |
| The Iliad | Homer, c. 8th century BCE | homer-iliad/ | 6 (index, reader, fullbleed, mobile, theater, pdf-reader) | Yes | Yes |
| The Odyssey | Homer, c. 8th century BCE | homer-odyssey/ | 6 (index, reader, fullbleed, mobile, theater, pdf-reader) | Yes | Yes |

## Vedas — next steps

- [ ] Bengali meanings for full Rigveda — NOTE: the "49/10,143" figure is stale; vedas/CLAUDE.md documents 100% coverage (10,143 mantras) from the ebanglalibrary merge. Re-scope or close.
  - eBanglaLibrary.com: Rameshchandra Dutta translation (HTML, potential scrape)
  - Archive.org: OCR text available but garbled, needs cleanup
  - No bulk machine-readable Bengali source found yet
- [ ] Add more curated suktas to reader.html/fullbleed.html
- [ ] Consider Samaveda/Yajurveda/Atharvaveda complete readers

## Conventions to apply retroactively

- [x] Add URL hash state to Alice readers (reader.html, fullbleed.html)
      → done — #ch-N in reader.html, #p-N/#s-N in fullbleed.html
- [x] Add URL hash state to Meditations readers
      → done — #ch-N in both scrolling readers, #p-N in fullbleed and index
- [x] Add URL hash state to Vedas reader.html
      → done — #ch-N, restored via getBoundingClientRect
- [x] URL hash state in Vedas rigveda.html
- [x] Add .project/ directory to alice-in-wonderland/
- [x] Add CLAUDE.md to alice-in-wonderland/
- [x] Add .project/ directory to meditations/ (now aurelius-meditations/)
- [x] Add CLAUDE.md to meditations/ (now aurelius-meditations/)
- [x] Renamed meditations/ → aurelius-meditations/
- [x] Add .project/ directory to vedas/
      → done — todo.md and changelog.md added
- [ ] Consider renaming remaining legacy directories to author-book style

## Future candidates

- Public domain books on Project Gutenberg
- Follow `{author}-{book}/` directory naming
- Start with reader.html + fullbleed.html as minimum
- Each book gets: seeds/, CLAUDE.md, .project/, URL hash state

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
├── meditations/                  2 formats: reader, fullbleed (legacy naming) + .project/ + CLAUDE.md
│   ├── .project/
│   ├── CLAUDE.md
│   ├── reader.html               scrolling reader (annotated prototype, Book I.1-5)
│   └── fullbleed.html            two-page spread reader
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
| Meditations | Marcus Aurelius, c. 170–180 CE | meditations/ | 2 | No | Yes |
| The Prophet | Kahlil Gibran, 1923 | gibran-prophet/ | 2 | Yes | Yes |
| Vedas (curated) | c. 1500–500 BCE | vedas/ | 2 (reader, fullbleed) | No | No |
| Rigveda (complete) | c. 1500–1200 BCE | vedas/ | 1 (rigveda.html) | Yes | N/A (generated) |

## Vedas — next steps

- [ ] Bengali meanings for full Rigveda (only 49/10,143 have Bengali)
  - eBanglaLibrary.com: Rameshchandra Dutta translation (HTML, potential scrape)
  - Archive.org: OCR text available but garbled, needs cleanup
  - No bulk machine-readable Bengali source found yet
- [ ] Add more curated suktas to reader.html/fullbleed.html
- [ ] Consider Samaveda/Yajurveda/Atharvaveda complete readers

## Conventions to apply retroactively

- [ ] Add URL hash state to Alice readers (reader.html, fullbleed.html)
- [ ] Add URL hash state to Meditations readers
- [ ] Add URL hash state to Vedas reader.html
- [x] URL hash state in Vedas rigveda.html
- [x] Add .project/ directory to alice-in-wonderland/
- [x] Add CLAUDE.md to alice-in-wonderland/
- [x] Add .project/ directory to meditations/
- [x] Add CLAUDE.md to meditations/
- [ ] Add .project/ directory to vedas/
- [ ] Consider renaming legacy directories to author-book style (needs user approval)

## Future candidates

- Public domain books on Project Gutenberg
- Follow `{author}-{book}/` directory naming
- Start with reader.html + fullbleed.html as minimum
- Each book gets: seeds/, CLAUDE.md, .project/, URL hash state

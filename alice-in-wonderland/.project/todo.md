# Alice in Wonderland — TODO

## Reader Formats

| File | Status | Notes |
|------|--------|-------|
| reader.html | Active | 4 themes, half-sun toggle, sidebar, progress bar |
| fullbleed.html | Active | 4 themes, page flip, running headers, chapter scrubber |
| mobile.html | Legacy | Mobile-first swipe reader |
| scroll.html | Legacy | Simple continuous scroll |
| single.html | Legacy | Paginated single page |
| web-reader.html | Legacy | Browser-style reader |
| pdf-reader.html | Legacy | PDF viewer simulation |
| theater.html | Legacy | Immersive reading |

## Pending

- [ ] Add URL hash state to reader.html (`#ch-N`)
- [ ] Add URL hash state to fullbleed.html (`#p-N` / `#s-N`)
- [ ] Add seeds/chapters.json (content currently embedded in each HTML file)
- [ ] Consider consolidating legacy readers or archiving unused ones
- [ ] Mobile testing for fullbleed.html
- [ ] 5th theme (sepia) to match AGENT_README spec — currently 4 themes

## Completed

- [x] 4-theme system in reader.html and fullbleed.html
- [x] Half-sun theme toggle icon
- [x] Running headers in fullbleed.html (per-page, inside content)
- [x] Recto chapter starts in fullbleed.html
- [x] Chapter scrubber with roman numerals
- [x] Editable page number
- [x] Cover page matching theme
- [x] Theme picker on cover
- [x] TOC on recto (right page)
- [x] Accent color threading through decorative elements
- [x] .project/ directory
- [x] CLAUDE.md build documentation

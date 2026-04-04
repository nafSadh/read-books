# Smarter Annotation Strategy

## Problem with current approach (2026-04-04)

Launching 12 parallel agents that each try to Edit large blocks of HTML is slow and fragile:
- Agents hit Edit size limits and retry repeatedly
- One passage at a time via Edit is sequential and slow
- Agents compete for file writes, causing conflicts
- Output is hard to validate (interleaved edits)

## Better approach: JSON-first batch processing

### 1. Extract passages to JSON
```bash
# Parse reader.html → passages.json
# Each entry: { book, num, original_text, has_annotation: bool }
```

### 2. Generate annotations as JSON
- Input: passages.json (original text only)
- Output: annotations.json with structure:
```json
{
  "I.3": {
    "modern_english": "...",
    "notes": "...",
    "proper_nouns": [
      { "name": "Diognetus", "tip": "A painting teacher...", "url": "https://..." }
    ]
  }
}
```
- Can be done in parallel per-book (12 agents writing 12 separate JSON files)
- No file conflicts — each agent writes its own `annotations-book-N.json`
- Easy to review, diff, and re-run selectively

### 3. Merge annotations into HTML
- Single pass: read reader.html + all annotation JSONs
- Template engine (or simple script) wraps each `<p>` in the `med-passage` structure
- Injects proper noun spans, modern english, notes
- One atomic write of the final HTML

### Benefits
- **No Edit conflicts** — agents produce data, not code
- **Reviewable** — JSON annotations can be inspected before HTML generation
- **Incremental** — can re-generate one book's annotations without touching others
- **Reusable** — same JSON feeds both reader.html and fullbleed.html
- **Parallelizable** — agents don't touch the same file

### 4. Store seed data in `seeds/`
- `seeds/passages.json` — all original text per book/passage
- `seeds/annotations/book-01.json` through `book-12.json`
- HTML generation script reads seeds and produces final reader.html

## Implementation plan
1. Write a passage extractor (JS or Python) that parses current reader.html → passages.json
2. Launch 12 agents, each producing `annotations/book-N.json`
3. Write an assembler script that merges passages + annotations → annotated HTML
4. Replace the chapter-text sections in reader.html with assembled output

# The Prophet — Read-Book Project

Build readers for "The Prophet" by Kahlil Gibran (1923, public domain since 2019),
following the same patterns as `../alice-in-wonderland/`.

## Content structure

Source data lives in `seeds/chapters.json`. The book has 28 short chapters of
poetic prose, each a meditation on a theme of life.

JSON schema:
```json
{
  "book": { "title", "author", "year", "source" },
  "chapters": [
    { "num": 1, "title": "The Coming of the Ship", "html": "..." }
  ]
}
```

Each chapter's HTML uses:
- `<div class="stanza">` to wrap verse groups (stanzas)
- `<p>` for individual lines/paragraphs within stanzas
- `<em>` for italic text (topic words like _Love_, _Marriage_)

## Reader formats

### 1. `reader.html` (scrolling reader)
- Follows `../alice-in-wonderland/reader.html` pattern
- Poetry typography: `text-align: left`, no text-indent, `line-height: 2.0`
- Narrower default width (560px vs Alice's 640px)
- 5 themes: light-purple (default), sepia, light-azure, dark-violet, dark-blue
- 28-chapter sidebar with Arabic numbers
- localStorage key: `prophet-reader-prefs`

### 2. `fullbleed.html` (book-spread reader)
- Follows `../alice-in-wonderland/fullbleed.html` pattern
- Same poetry typography in measure box and page content
- Stanzas are kept as block units during pagination (not split across pages)
- Each chapter starts on recto (right) page
- 5 themes with light-purple default
- localStorage key: `prophet-fullbleed-prefs`

## Typography decisions

The Prophet is poetic prose, so typography differs from Alice (standard prose):

| Property       | Alice (prose) | Prophet (poetry) |
|----------------|--------------|-----------------|
| text-align     | justify      | left            |
| text-indent    | 1.5em        | 0               |
| line-height    | 1.85         | 2.0 (reader)    |
| content-width  | 640px        | 560px           |
| hyphens        | auto         | manual          |
| default theme  | light-purple | light-purple    |

## File inventory

```
gibran-prophet/
  CLAUDE.md              <- this file
  seeds/
    chapters.json        <- source text (28 chapters)
  reader.html            <- scrolling reader
  fullbleed.html         <- book-spread reader
```

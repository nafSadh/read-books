# Rubáiyát of Omar Khayyám — Read-Book Project

Build readers for the Rubáiyát, following the same patterns as
`../gibran-prophet/` (poetry typography). All HTML files are self-contained
(no external JS/CSS beyond Google Fonts).

## Content

- **Author**: Omar Khayyám (1048–1131 CE), Persian polymath
- **Translator**: Edward FitzGerald (1809–1883)
- **Editions rendered**: 1st (1859, 75 quatrains) and 5th (1889, 101 quatrains)
- **Source (English)**: Project Gutenberg #246 (public domain)
- **Source (Persian)**: (WIP — see `data/fetch_persian.py` when available)

## Directory layout

```
khayyam-rubaiyat/
  CLAUDE.md              <- this file
  seeds/
    fitzgerald.json      <- 1st + 5th editions (English), generated
    quatrains.json       <- canonical unified data (with Persian when available)
  data/
    fetch_fitzgerald.py  <- fetch FG 1st+5th from Gutenberg #246
    fetch_persian.py     <- (TBD) fetch Persian + FG mapping
    build_quatrains.py   <- (TBD) merge FG + Persian → seeds/quatrains.json
  index.html             <- book landing page (book-spread)
  reader.html            <- scrolling reader, edition + Persian toggles
  fullbleed.html         <- two-page spread, one quatrain / recto
  theater.html           <- one quatrain at a time
```

## Data schema

`seeds/quatrains.json`:
```json
{
  "book": {"title": "The Rubáiyát of Omar Khayyám",
           "author": "Omar Khayyám",
           "translator": "Edward FitzGerald",
           "years": "1048–1131 (written), 1859/1889 (translated)"},
  "editions": {
    "first":  {"year": 1859, "count": 75,
               "quatrains": [{"num": 1, "roman": "I",
                              "lines": ["Awake! for Morning...", "..."]}]},
    "fifth":  {"year": 1889, "count": 101,
               "quatrains": [{"num": 1, "roman": "I",
                              "lines": ["Wake! For the Sun...", "..."],
                              "persian": {"script": "بيدار شو...",
                                          "translit": "bīdār šow...",
                                          "source": "Ouseley #..."}}]}
  }
}
```

`persian` is optional per-quatrain — not all FG quatrains have a known Persian
source. When absent, the Persian toggle hides no column for that quatrain.

## Typography

Poetry (like Prophet): `text-align: left`, no `text-indent`, `line-height: 2.0`.
Quatrains numbered with Roman numerals in the classic 19th-century style.
Width: 560px (matches Prophet).

## Themes

5 themes, consistent with the rest of lib.sadh.app:
`light-purple` (default), `sepia`, `light-azure`, `dark-violet`, `dark-blue`.

## UI

- **Edition toggle** (top bar): 1st (75) ↔ 5th (101)
- **Persian toggle** (top bar): show/hide Persian column (when data present)
- **Transliteration toggle**: show/hide Latin phonetic below Persian
- localStorage keys: `rubaiyat-reader-prefs` / `rubaiyat-fullbleed-prefs`

## Build

```
python3 data/fetch_fitzgerald.py   # writes seeds/fitzgerald.json (FG 1st + 5th)
python3 data/fetch_persian.py      # (WIP)
python3 data/build_quatrains.py    # (WIP) → seeds/quatrains.json
```

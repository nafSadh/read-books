# The Odyssey — Read-Book Project

Sibling project to `../homer-iliad/` — same reader mechanics, same data
schema, same build pipeline. **Read `../homer-iliad/CLAUDE.md` first**; it
documents the full architecture (the "render one book at a time" fix and the
CSS-column pagination technique) in detail. This file records what's
Odyssey-specific — most importantly, **this book has 5 editions, not 3**.

## Content

- **Author**: Homer (attributed), composed ~8th century BCE
- **Structure**: 24 books, traditional division (present in every edition below)
- **Editions rendered** (five, in switcher order):
  1. **Samuel Butler** (1835–1902) — prose, 1900. Project Gutenberg #1727.
  2. **Alexander Pope** (1688–1744) — heroic-couplet verse, 1725–1726 (completed with William Broome and Elijah Fenton). Project Gutenberg #3160.
  3. **William Cowper** (1731–1800) — blank verse, 1791, published as a matched pair with his Iliad. Project Gutenberg #24269.
  4. **Original Ancient Greek** — the Perseus Digital Library's canonical text (`PerseusDL/canonical-greekLit`), which mirrors the 1919 Loeb Classical Library edition edited by A. T. Murray. Public domain (ancient text; 1919 critical edition).
  5. **Modern English prose** — an original translation by Claude (Anthropic), 2026, made directly from the Greek in edition 4. Complete in all 24 books — see "Modern prose translation" below.

## Why Greek and a modern translation were added

The user asked for the original Greek plus a modern-English-prose rendering,
and pointed at a local file that turned out to be from Library Genesis (a
shadow library that hosts pirated copies of in-copyright books) — almost
certainly an actively-copyrighted modern translation (e.g. Rieu, Fagles,
Fitzgerald, or Wilson). That file was never opened or used for anything.
Instead:

- The **Greek** text was fetched from `raw.githubusercontent.com/PerseusDL/canonical-greekLit` (TEI XML), which is the standard, legitimate, public-domain
  source for Homeric Greek — the same text base university classics
  departments use. See `data/greek_extract.md` note below for the parsing
  gotcha.
- The **modern prose** is an original translation, written directly from
  that Greek text, with no reference to any existing translation
  (copyrighted or otherwise). It is explicitly labeled as AI-generated,
  matching the precedent already set in `../khayyam-rubaiyat/` ("Modern
  literal and poetic translations are machine-generated (Claude,
  Anthropic)").

## Modern prose translation

Complete: all 24 books (~123k words) live in `seeds/modern.md`. Process
used: Books I-VIII and XXIV were translated in the main session directly
from `seeds/greek.json`; Books IX-XXIII were drafted in parallel by
subagents under a locked style contract (fixed epithet/formula renderings,
curly-quote speech conventions, paragraph sizing, full-simile fidelity,
no consulting of any existing translation), then each draft was reviewed
against the Greek and the house voice in the main session before being
merged via `data/merge_modern_book.py`. The four-book apologue (IX-XII)
uses bare first-person narration after an opening frame line, with only
embedded speeches quoted. If revising a book, edit `seeds/modern.md`
directly and re-run `python3 data/build.py`.

## Directory layout

```
homer-odyssey/
  CLAUDE.md              <- this file
  seeds/
    butler.json           <- Butler prose, parsed from PG #1727
    pope.json              <- Pope verse, parsed from PG #3160
    cowper.json             <- Cowper blank verse, parsed from PG #24269
    greek.json              <- original Greek, all 24 books, from Perseus/Loeb 1919
    modern.json             <- Claude's modern prose translation — Book I only; 2-24 are placeholders
  data/
    build.py                <- builds ALL 5 HTML variants from all 5 seed files
    reader-template.html    <- scrolling reader shell
    theater-template.html   <- cinematic one-book-at-a-time shell
    mobile-template.html    <- mobile pager shell
    fullbleed-template.html <- two-page spread shell
    pdf-template.html       <- PDF-viewer-style shell
  index.html / reader.html / theater.html / mobile.html / fullbleed.html / pdf-reader.html
```

## Data schema

Same shape as `../homer-iliad/`'s (see that CLAUDE.md) for the three
Gutenberg translations. The two new seeds:

`seeds/greek.json` — `"form": "greek"` (renders like verse: left-aligned,
no indent — see `data.form === 'prose'` check in every template), one
`<p>` per Homeric line, no `argument` field (the original doesn't have
translator's summaries):
```json
{
  "translator": "Homer (original Ancient Greek)",
  "publication_year": 1919,
  "form": "greek",
  "source": "Perseus Digital Library canonical-greekLit, ed. A. T. Murray (Loeb Classical Library, 1919)",
  "source_url": "https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0012/tlg002/tlg0012.tlg002.perseus-grc2.xml",
  "epic": "odyssey", "book_count": 24,
  "books": [ { "num": 1, "roman": "I", "argument": null, "lines": ["ἄνδρα μοι ἔννεπε, μοῦσα, πολύτροπον, ὃς μάλα πολλὰ", "..."] } ]
}
```

`seeds/modern.json` — `"form": "prose"` (renders justified, with drop cap,
like Butler):
```json
{
  "translator": "Claude (Anthropic)",
  "publication_year": 2026,
  "form": "prose",
  "source": "Original translation from the Greek (see seeds/greek.json); pilot, Book I only",
  "epic": "odyssey", "book_count": 24,
  "books": [ { "num": 1, "roman": "I", "argument": null, "paragraphs": ["Tell me, Muse, ...", "..."] }, /* 2-24: placeholder paragraph */ ]
}
```

## Extraction gotcha (Greek XML parsing)

The Perseus TEI XML nests some `<l>` (line) elements inside `<q>` (quoted
speech) wrappers rather than as direct children of the book `<div>`. A naive
`div.findall('l')` (direct children only) silently drops every quoted
speech's lines — for Book 1 that was the difference between 159 lines found
and the correct 444. Use `div.findall('.//l')` (recursive) instead, and
sanity-check the extracted line count against the book's well-known total
before trusting it.

## Templates: 5 editions, not 3

`../homer-iliad/`'s templates hardcode `EDITION_ORDER = ['butler', 'pope',
'cowper']` plus an `EDITION_META` object and matching HTML buttons. Here
every template has been extended to
`['butler', 'pope', 'cowper', 'greek', 'modern']` with two more buttons and
two more `EDITION_META` entries (`caption` field: e.g. `'ed. A. T. Murray'`
for greek, `'modern prose · pilot: Book I only'` for modern). If you add a
6th edition, grep each template for `EDITION_ORDER`, the hardcoded
`(butler|pope|cowper)` hash regex, and the edition-switch button markup —
all five templates need all three updated. `mobile-template.html` also had
a `data.translator.split(' ').pop()` shortcut for the topbar label that
broke on `"Homer (original Ancient Greek)"` / `"Claude (Anthropic)"` — it
now uses an explicit `SHORT_NAME` lookup keyed by edition id instead.

## Everything else

Typography, themes, localStorage keys (`odyssey-reader-prefs`,
`odyssey-theater-*`, `odyssey-mobile-prefs`, `odyssey-fullbleed-prefs`,
`odyssey-pdf-prefs`), hash format (`#bk-N` / `#bk-<butler|pope|cowper|greek|modern>-N`),
and the pagination/rendering architecture are otherwise identical in
mechanism to `../homer-iliad/` — that CLAUDE.md is the source of truth.

## Seed formats: markdown is canonical

All six reader editions live as **markdown** in `seeds/*.md` — the canonical,
hand-editable source. Format: YAML-ish frontmatter (`translator`, `form`,
`publication_year`, `source`, ...), then one `## Book <roman>` section per
book. An optional leading `> ...` blockquote is the translator's *argument*.
Prose editions (`form: prose`) use blank-line-separated paragraphs;
verse/greek editions use one poem-line per file line. In `modern.md`, a book
whose body is exactly `*[not yet translated]*` gets the reader placeholder at
build time. `build.py` prefers `<key>.md` over `<key>.json` when both exist.

The `seeds/*.json` files for the five parsed editions are retained as parse
artifacts (and `greek.json` also feeds `build_study_data.py`), but the
markdown wins at build time — edit the `.md`, not the `.json`. The modern
translation exists **only** as `modern.md`. `study.json` stays JSON: it is
per-word structured data (lemma/morph arrays), not prose.

## Illustrated flip-book (`illustrated.html`)

Built by `data/build_illustrated.py` from `seeds/modern.md` +
`data/illustrated_plates.json` (plate manifest: per `bkNN`, a list of
`{file, caption, anchor, portrait?}` where `anchor` is a substring of the
paragraph the plate follows; `null` anchor = book front). Images live in
`img/bkNN/*.jpeg`, generated by the user in Gemini from
`data/illustration-prompts.md` (ink-and-wash style block won the bake-off).
**Redesigned as an actual comic page**, not a book layout (per user
request — "can we be more graphic novel-ish?", visual-only, no rewriting the
translation). One dominant full-bleed panel per page: thick ink border,
halftone-dot backdrop, a notched caption box (Patrick Hand font) for
narration, curly-quoted dialogue auto-wrapped in speech-bubble spans, a
"BOOK ⟨roman⟩" corner stamp, and a splash title page per book (Bangers font)
using that book's first plate as the background. The plate is sticky: it
stays as the full-bleed background across every caption page until the next
`img` anchor, so a scene holds while narration turns several pages — the
graphic-novel pacing the user asked to preserve. Text is split to the
*sentence* level and packed greedily into the caption box (a whole prose
paragraph is usually too long for one comic caption — see gotcha below).
Books without plates still get full text, using a larger centered caption
box (`.caption-box.big`) with the panel showing a halftone texture instead
of art, marked "plates pending" on the splash page.

### Pagination gotcha #1 — absolutely-positioned probe with top+bottom set stretches to fill its container, ignoring content

The hidden `<div>` used to measure caption text height reused the
`.caption-box` class (to match real rendering) plus inline overrides to hide
it off-screen: `position:absolute; left:-9999px; top:0;`. But the class
itself sets `bottom:20px`. For an absolutely positioned box, if **both**
`top` and `bottom` are non-auto and `height` is auto, CSS makes the box
*stretch* to span from `top` to `bottom` of its containing block —
completely ignoring content size. The probe silently reported ~700px
("the viewport minus 20px") for a single short sentence, no matter what was
inside it, so every pagination comparison saw a false overflow and broke
after 1-2 sentences. Fixed by also setting `bottom:auto; right:auto;` on the
probe. Lesson: when copying a class onto an off-screen measuring probe,
explicitly neutralize *every* positioning/sizing property the class sets
(`top`/`bottom`/`left`/`right`/`height`/`max-height`), not just the one
you changed — the interaction between two independently-reasonable
overrides is what breaks silently.

### Pagination gotcha #2 — 0×0 layout at first script execution never self-corrects

If `panelEl.clientWidth/clientHeight` read as 0 at the moment `paginate()`
first runs (observed in headless/backgrounded-tab testing; possible for
real users too if the tab loads while backgrounded), every `availH`/`textW`
computation goes negative, and — since nothing but a `resize` event ever
re-triggers pagination — that broken result sticks for the whole session
even after the tab becomes visible and correctly sized. Fixed defensively:
after the initial `paginate()+render()`, if the panel's measured size was
`<= 0`, a double-`requestAnimationFrame` callback re-checks and
re-paginates once real layout is available (keeping the reader's current
position). This only fires in the pathological case; the normal load path
is untouched.

### Layout v3 (user feedback: text covered art / square panel / flicker)

Three user-reported issues, fixed together since they shared a root cause
(fixed near-square panel + `object-fit: cover` + overlay caption + full
re-render per turn):

1. **Caption no longer overlays the art.** The panel is now a flex column:
   art block on top, caption band on paper *below* it (a ~20px decorative
   straddle only). Long speeches also stopped being bubble-styled — the
   `.dialogue` span applies only to quotes ≤100 chars (a 10-line "bubble"
   renders as ruled stripes, not a bubble), with `box-decoration-break:
   clone` for clean line fragments.
2. **Panel matches the art's real aspect ratio.** `build_illustrated.py`
   parses each JPEG's SOF header (stdlib, no PIL) and embeds `r`
   (width/height) per plate; `geom(plateR)` sizes the panel from the current
   plate's ratio, so landscape plates (1.792) render full-width uncropped.
   Portrait plates as sticky art get height-capped + cover-cropped (only the
   title plate; it stars uncropped on cover/splash pages anyway).
3. **No flicker on page turns.** `render()` keeps the `#art-img` DOM node
   untouched when the scene hasn't changed (same shape + same src): only
   the caption box's innerHTML is swapped, with a 180ms slide-in re-trigger.
   The old code faded the whole stage and rebuilt the panel every turn,
   re-decoding the image. Verified by marking the img element and checking
   identity across a page turn.

Also: page-turn state uses `history.replaceState`, not `location.hash`
assignment — the latter pushes one history entry per page and breaks the
Back button after a reading session (hundreds of entries).

### What this edition is: a full-text graphic edition

Framing note, because I got this wrong twice and the user corrected both.

**First error:** I opened the canonical style block with "Children's-classic
storybook illustration". Wrong register for a poem containing coerced
concubinage, adultery netted before a laughing audience of gods, an eye
bored out with a stake, 108 men killed in a hall, twelve enslaved women
hanged, and a mutilation. Fixed — see the register section below.

**Second error:** correcting that, I framed the choice as "graphic novel vs
tasteful literary edition", as though comics were inherently the untasteful
option. That is simply false — *Maus*, *Persepolis*, *Fun Home*, Mazzucchelli,
and for this exact material Gareth Hinds's *Odyssey* and Shanower's *Age of
Bronze*; Mattotti and Corto Maltese are watercolour comics that are fine art.
What was actually untasteful in my build was not that it was comic-like but
that it used **cheap comic signifiers instead of comics craft**: Bangers (a
novelty display face), Patrick Hand (casual handwriting), halftone-dot
wallpaper, a rotated "BOOK I" sticker, hard offset drop-shadows on notched
caption boxes. Clip-art pastiche, not comics.

**What it actually is.** The binding constraint is that this edition keeps
Homer's *complete* text — ~123k words of the modern prose translation. That
rules out speech balloons and caption-length adaptation (they would duplicate
or gut the prose). So the form is a **full-text graphic edition**: prose set
properly as text, with the comics craft carried by *page architecture* rather
than lettering gimmicks —

- body text in EB Garamond (the library's face), justified, hyphenated, with
  a restrained drop cap on each book's opening page;
- plate inset within the page with a real **gutter** and a 1px hairline
  frame — not flush, not shadow-stickered;
- **page-architecture variety**: a plate flagged `"bigBeat": true` in
  `illustrated_plates.json` gets its own **full-bleed page** before its text
  resumes, so the book has splash beats instead of one uniform
  plate+text rhythm (Book I: council-of-gods, athena-at-the-gate,
  eurycleia-torches);
- sticky art per scene, side-by-side on wide screens, stacked when narrow.

Two bugs found while verifying this pass:
- **Web-font pagination race.** `paginate()` measures text with a hidden
  probe; running before EB Garamond loaded measured fallback metrics and
  produced 866 pages each with ~180px of unused column (vs 748 correct).
  Now repaginates on `document.fonts.ready`.
- **Plate stuck at 30% opacity.** The art fade-in animated *from*
  `opacity: .3`; a paused animation (throttled or backgrounded tab) leaves
  the plate permanently faded with its cleanup class never removed — which
  is what made a splash page look washed out. The fade was removed
  outright: sticky art already prevents flicker, so it bought nothing but a
  failure mode. Lesson: never rely on an animation to *arrive at* the
  correct visual state.

### Illustration register — NOT a children's book

`data/illustration-prompts.md`'s canonical style block originally opened
"Children's-classic storybook illustration" (my phrasing, describing what the
winning square set looked like). The user correctly pushed back: the Odyssey
contains Calypso's seven years of coerced concubinage (5.154-155, *unwilling
beside the willing*), Ares and Aphrodite netted naked before a laughing
audience of gods, the Cyclops blinding, 108 suitors killed in a hall awash
with blood, twelve enslaved women hanged, and Melanthius mutilated. A
storybook register would fight the material and produce tonal whiplash at
exactly the points where the poem is most serious.

The style block now reads "serious literary edition of an ancient epic, for
adult readers — in the tradition of Charles Keeping, Barry Moser and Alan
Lee", keeping the *technical* descriptors that produced the liked look (ink
line over flat watercolour washes, restrained Aegean palette, composed
middle distance) while removing "faintly naive", "quiet rather than
dramatic" and all cuteness.

A `REGISTER, AND THE DIFFICULT SCENES` section codifies the method:
**restraint through composition, not omission** — aftermath over act,
silhouette/backlight/off-frame, reaction as subject, and rendering Homer's
own displacing similes (netted fish, doves in a snare, the lion come from
feeding) where the act itself can't be drawn. Calypso is framed as captivity
rather than romance; sexual content stays off-frame or comic (draw the gods
in the doorway, not the bed); no nudity or explicit wounds — which is both
the right register for a printed edition and the only way these prompts
generate at all. Where a model still refuses, fall back to the
non-figurative beat (an object, a room, a landscape holding the aftermath).

### Layout v4 — square plates + side-by-side (the active set)

The user generated a second, **square (1024×1024)** plate set for Book I and
asked whether it allowed a better layout. It does, and it is now the active
set: `data/illustrated_plates.json` points `bk01` at `img/bk01` via a
per-book `"dir"` override (manifest entries accept either a plain list of
plates or `{"dir": ..., "plates": [...]}`, so a book can select an alternate
image set without moving files).

**Why square won:** a square panel beside a caption column fills a 16:9
screen properly, whereas landscape art stacked above text wastes horizontal
space and squeezes both. Side-by-side also reads more like a comic tier.
`geom(plateR)` picks the layout from the plate's own ratio:
`0.8 < r < 1.3` **and** stage width > 860px → **side-by-side** (art left in
its own framed cell, caption column right, top-aligned); anything else
(landscape art, or a narrow screen) → the stacked layout. Both sets
therefore still work; nothing is hardcoded to one aspect.

**The two sets cannot be mixed** — the square set is brighter, cleaner, more
saturated and tighter on characters; the landscape set is muted and
atmospheric with more negative space. Compare square `calypso-glimpse` with
landscape `02-calypso-shore` (same scene). The landscape set is retained at
`img/bk01/` as the alternate.

Two smaller fixes that came out of this:
- The square set arrived as `.png` files that were **actually JPEGs**;
  renamed to `.jpeg` (wrong extensions break content-type on real servers
  and defeated the SOF-header size probe).
- `"splashOnly": true` on a plate means "use for the cover/splash page but
  never as sticky scene art" — needed because Book I's title plate is a
  *montage/collage*, which looked wrong sitting behind narration. The first
  real scene plate (`calypso-glimpse`, anchored `null`) now opens the book.

The template (`data/illustrated-template.html`) renders one panel per page
— no book-spread layout. Edge hit-zones, arrow keys/swipe, Prev/Next Book
bottom bar, theme dots (re-themed as ink/paper/halftone tokens per site
theme), hash state `#bk-N-pM`, localStorage `odyssey-illustrated-prefs`,
and immediate `cur` update on navigation (so rapid key-repeat/clicks queue
correctly instead of collapsing into one page-turn during the fade
transition) all carry over from the site's other readers.
To add a book's plates: drop images in `img/bkNN/`, add manifest entries,
re-run `python3 data/build_illustrated.py`.

## Build

```
python3 data/build.py            # seeds/*.md -> all 5 *.html variants + study.html
python3 data/build_study_data.py # (rebuild seeds/study.json from Perseus sources)
```

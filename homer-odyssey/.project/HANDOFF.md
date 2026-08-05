# homer-odyssey — session handoff

Written at ~87% context. Read this first, then `CLAUDE.md` (which has the
full architecture + every bug/decision writeup). Nothing here is a
duplicate of code — it's state, next actions, and traps.

## Where things stand

**Text: DONE.** All 24 books of the modern prose translation exist in
`seeds/modern.md` (~123k words), translated from the Greek in
`seeds/greek.md`. Six editions build: butler, pope, cowper, murray, greek,
modern. Markdown in `seeds/*.md` is canonical (not the `.json` files, which
are retained only as parse artifacts; `study.json` stays JSON because it's
per-word structured data).

**Readers: DONE.** `reader.html`, `theater.html`, `mobile.html`,
`fullbleed.html`, `pdf-reader.html`, `study.html`, `illustrated.html`,
`index.html`. Build with:

```
python3 data/build.py              # the 6-edition readers + study.html
python3 data/build_illustrated.py  # illustrated.html only
```

**Illustrated edition: Books I–VII live (7/24), VIII–XXIV pending art.**
21 character sheets exist (see roster below); Calypso, Nausicaa, Alcinous,
Arete, Demodocus all clean on the red-signature scan. `img/attic/` holds
superseded art (v1 character sheets, the old landscape set, alt takes
rejected during review — never mixed into a live book).

**Book X: DONE.** 11 plates installed, 10/24 books live. Sheets `circe`,
`eurylochus`, `elpenor` added (25 total). Rejects in the batch: a bk09
`the-wine-bowl` alt that invented a woman in the giant's lap (not installed)
and a 4-up contact sheet — both attic'd.

**Book XI: DONE.** All 12 plates installed; 11/24 books live. Flags for a
later polish pass: `achilles-shade` has a generation artifact (a truncated
figure, legs with no torso, bottom-left); `hard-torments` shows Tantalus
knee-deep where the caption says chin-deep; `heracles-phantom` has a faint
scribble in the mist lower-left. 10 of 12 arrived at 1024 and several lost
~120px of sky to the paper-band trim, so effective sources run 858-989px —
the softest batch in the edition. If any read muddy in situ, regenerate at
2048 (prompts in session history).
(Original planning note, superseded:)
All four dead sheets installed (29 total, new cast row "THE DEAD"):
`tiresias`, `anticleia`, `agamemnon-shade`, `achilles-shade` — every one
0.00% red. Gemini gave ALL the male dead blank white eyes, so sightlessness
is now the shade convention rather than Tiresias's personal marker; he
distinguishes by the golden staff + shroud-grey, Agamemnon by the breast
stain + bronze-brown + circlet. Internally consistent — kept. Scene chat
uploads 6 sheets: odysseus, elpenor + these four. bigBeats: gathering-dead,
three-times.

**Book XII: manifest written (10 plates, validated at paras 4,12,13,16,17,
18,26,27,28 + unanchored opener `elpenor-barrow`), art pending.** No new
sheets — scene chat uploads `odysseus`, `circe`, `eurylochus`. Sirens/
Scylla/monsters described inline. bigBeats: the-sirens, six-taken,
thunderbolt. Register: six-taken is silhouettes-against-sky, no gore;
the Sirens are beautiful and the bone-meadow stays subtle.

**prepare_plates.py grew a paper-band pass**: near-white rows (min channel
avg >= 228, spread <= 48) are eaten per side before the flatness passes —
Gemini borders that fade into the art fail the flatness proof and used to
survive as messy edges (user caught one). Plus a 0.6% uniform INSET after
trimming. NOTE: reprocessing a plate shaves INSET again each run — do not
re-run over live dirs casually. Render-time overscan was tried and REJECTED
by the user ("trim the badly generated images") — fix files, not the lens.

**Trim box widened after use on a big monitor**: W cap 1200 -> 1440, and the
beside caption column now reaches the full 620px book measure
(capW = min(712, max(340, W*.42))) — the art yields width to the column,
never the reverse. Cover carries the credit line "nafSadh · lord of cool
stuff" (user-commissioned, keep it).

**Book splash pages redesigned as typographic title pages** (user rejected
the first-plate-as-backdrop design: "boring and meaningless"). Now: paper
page, "BOOK" over a grand EB Garamond numeral, hairline rule, and the book's
plates as a loose fan of ≤5 small rotated tiles (`.tp-tiles`, deterministic
rotation pattern — no Math.random, it would break nothing here but keep it
deterministic anyway). A book with no art gets the pure-text page
automatically. The plate-count note ("10 PLATES" / "plates pending") is
GONE — production metadata the reader never needed. The splash render branch
pins `panelEl.style.height = '100%'`; every other branch must clear it (beat
and cap branches do — keep it that way).

**Book IX: DONE.** All 11 plates installed; 9/24 books illustrated. New sheet
`polyphemus` added (22 sheets now), in `label_character_sheets.py` and the
cast sheet under a new "THE WANDERINGS" row.

**The two hard plates of the epic both worked, first try, no refusal:**
- `the-blinding` renders **Homer's own drill simile** instead of the wound —
  four men hauling a strap, Odysseus driving from above, the target entirely
  outside the frame in glare and smoke. No eye, no blood.
- `he-seizes-two` is **the watching faces only**, lit red by firelight, with
  the giant present solely as a shadow thrown on the cave wall.
  Reuse both shapes for the slaughter (XXII) and the hanged maids.

**`verify_plates.py` red% false positives**: `he-seizes-two` (11.6%) and
`the-blinding` (9.0%) are *firelight on skin and forge-glare*, not dyed
cloth — Antinous's signature is intact. Same for the character sheets:
menelaus 7.0% (red-gold hair), nestor 5.2% (saffron robe), peisistratus
3.9% (chestnut tunic). The scan is a prompt to look, not a verdict.

**Polyphemus sheet — two failed attempts before the good one.** Landscape
format and warm rendered concept-art skin were the failures; the fix was a
correction pass attaching the bad image and changing format + wash style +
costume in one message. His skin came out grey-blue rather than weathered
warm — deliberate on balance (separates him from every human) but noted as
an open call. He appears in 8 of the 11 plates, so changing it now means
regenerating those too.

**Book VIII: DONE.** All 10 plates installed and verified; build reports no
WARN. `gods-in-doorway` (the Ares/Aphrodite net) generated first try with no
refusal — the staging that worked is the decorative inset border plus "the
laughing faces in the doorway are the subject; the couch is small, distant
and covered". Reuse that shape for the other hard scenes. `the-discus`
arrived with 204px of dead sky on the top edge only; the trimmer took it and
the composition improved.

**Book IV second pass: DONE.** All 4 added plates installed
(`sparta-wealth`, `lion-and-fawns`, `agamemnon-falls`, `suitors-at-games`).
Book IV now has 11 plates at 765 words/plate. `agamemnon-falls` — the empty
hall, spilled wine, shadows of armed men, ox-goad in the foreground, no
bodies — is the best demonstration in the edition of aftermath-over-act.

**Book VII: DONE.** All 5 plates installed and verified — `mist-walk`,
`palace-threshold`, `orchard`, `knees-of-arete`, `arete-recognizes`. Build
reports no WARN. `palace-threshold` arrived with a ~99px cream matte on all
four sides, trimmed by `prepare_plates.py`.

**`img/attic/gemini-originals/`** holds the 33 raw `Gemini_Generated_Image_*`
downloads that had accumulated loose in `img/`. They are pre-trim originals
of installed plates plus rejected alt takes — nothing references them (the
build output was byte-identical after moving them). Match a loose download
against the installed set with a **centre-crop** perceptual hash, not a
whole-image one: `prepare_plates.py` trims borders, which shifts every pixel
and inflates a plain phash distance past any sane threshold (an already-
installed plate scored d=103 whole-image, d=7 centre-crop).

**Working split that works:** the user drives Gemini and drops the downloads
in; Claude writes manifests/prompts and does install → prepare → build →
verify. Claude driving the Gemini web UI directly was tried and is much
slower and more token-hungry — the UI needs retries, the submit button often
needs two clicks, and long threads develop context rot.

## The illustrated edition — current design

A **full-text graphic edition**: Homer's complete prose (not captions), set
in EB Garamond, with comics craft carried by page architecture. No speech
balloons — they'd duplicate the prose. See CLAUDE.md "What this edition is"
for why, including two framing errors I made and the user corrected.

- Art lives at **`img/bk<NN>/<slug>.jpeg`**, square, 2048×2048. That is the
  only convention — there is no `dir` override and no `alts/` directory any
  more. Both existed while the square set was still an experiment competing
  with an earlier landscape set; the square set won, so it was promoted to
  the plain path and the override was deleted. Superseded art is in
  `img/attic/` (`bk01-landscape/`, `bk01-prototypes/`) — kept for
  comparison, never mixed into a live book: the sets differ visibly in
  palette and line weight.
- Layout is ratio-driven in `geom(plateR)`: squarish art (0.8 < r < 1.3) on
  a stage wider than 860px → **side-by-side** (plate left, text column
  right); landscape art or narrow screen → **stacked**.
- Sticky art: a plate stays as the scene image across every text page until
  the next anchored plate.
- `"bigBeat": true` on a plate → it *may* get its own full-bleed page before
  its text resumes, but **only when the layout is stacked**. In side-by-side
  the plate already fills half the spread, so a beat page was the same
  picture twice in a row — smaller the first time — which read as a stray
  orphan image. `paginate()` now gates it on `!geom(blk.r).beside`, and
  since pagination reruns on resize the gate follows the layout.
- `"splashOnly": true` → used for cover/splash but never as sticky scene
  art (Book I's title plate is a montage, which looked wrong behind prose).
- **An unanchored, non-`splashOnly` plate at the head of a book is correct,
  not a bug.** It is the only way a book's opening paragraphs get scene art,
  because `splashOnly` plates are excluded from stickiness. Book I needs two
  leading plates for this reason: `title-plate` (splashOnly) and
  `calypso-glimpse` (the actual opening scene). I once "fixed" the second
  one by anchoring it to a paragraph, which left Book I opening on a bare
  text page. Do not anchor it. Books II and III each have exactly one
  unanchored opener and are fine.
- **`"focus"` on a plate crops into the same sticky image instead of
  repeating it full-frame.** A wide composition held sticky across many
  pages used to show the identical full frame on every one — static. Add a
  `focus` array to a plate entry:
  ```json
  "focus": [
    { "anchor": "I am Mentes, son of wise Anchialus", "rect": [0.50, 0.10, 0.45, 0.55] },
    { "anchor": "this house was once rich and blameless", "rect": [0.05, 0.15, 0.45, 0.55] }
  ]
  ```
  `rect` is `[x, y, w, h]`, fractions (0–1) of the *image*, the crop window
  shown once that focus's `anchor` paragraph is reached. Each `anchor` is a
  substring resolved against `seeds/modern.md` exactly like a plate anchor,
  but it must land strictly after the plate's own anchor paragraph and
  before the next plate's (i.e. inside this plate's sticky span) —
  `build_illustrated.py` validates that and prints `WARN <bk>: focus anchor
  not found: ...` (then skips it) for anything outside the span or
  unmatched, same as a bad plate anchor. Once reached, a focus stays sticky
  in turn — it keeps cropping the same region across subsequent pages until
  the next focus (or the plate itself changes, which always resets to full
  frame). Frontend-side this is all done with a CSS `transform:
  translate()/scale()` on the *same* `<img id="art-img">` element (see
  `applyFocus()` in `illustrated-template.html`) — never a src swap — so the
  existing flicker-free sticky-art path is untouched, and it never affects
  `geom()`'s `beside`/`stacked` layout call, which is still driven purely by
  the plate's own aspect ratio. Live example: `the-feast.jpeg` in `bk01`
  (two focuses, panning between Mentes/Athena and Telemachus across the
  dialogue that plays out under that one plate).

## illustrated.html — mobile-first pass (done)

Was responsive by accident, not by design. Audited with four parallel agents
against the real file, then measured in-browser at 390/430/480 and landscape.
What it is now on a phone:

- **One bar, and it is the book's running foot.** Two bars cost 82px of an
  844px screen for controls you touch once a session, and Prev/Next Book
  duplicated the book picker. Under `NARROW` the bottom bar is hidden and
  `#top-bar` takes `order: 3`, so it sits under the stage where the thumb is —
  in `var(--paper)`, `var(--ptext)` and EB Garamond, with a hairline rule
  above, so there is no seam between page and chrome: it reads as the foot of
  the page, not a bar under it. It carries `←` / *The Odyssey* (italic, the
  title kept visible) / `Bk I ✦` / `‹ 12/1193 ›` / one theme swatch.
  - The five theme dots collapse to **one** `#theme-cycle` swatch that wears
    the current theme's colour and cycles on tap — five 24px targets were most
    of the bar's width.
  - Options read `Bk I`, not `Book I`; those four characters are what let the
    foot fit at 390px.
  - `#book-select` is `appearance: none`, borderless and transparent on narrow
    so it reads as a folio mark rather than a form control.
  - Explicit `‹ ›` page turners, disabled at the ends, for people who do not
    discover edge-taps.
- **Edge to edge.** `#stage` padding drops to the safe-area insets, the panel
  takes `.fill` (full stage height, no radius, no shadow) and the plate runs
  the full width with `artMargin() === 0`. The paper is the page.
- **The plate is not capped or cropped on a phone.** A square plate at 390px
  wide is 390 tall and still leaves ~306px (≈10 lines) for the caption. An
  earlier version capped it to a 222px band; that was solving a problem only
  created by the plate not being full-width.
- **Landscape uses `beside`.** The gate is now shape-aware
  (`stW > 860 || (stW >= 700 && stW > stH * 1.6)`), so a 852x393 phone gets
  the square plate at full height with the column next to it instead of a
  92px letterbox strip.

Bugs fixed on the way (all measured, not inferred):

- `geom()` subtracted a hardcoded 32/24 for `#stage` padding that is actually
  120px horizontally on desktop — landscape phones got a panel wider than the
  stage, and `overflow:hidden` ate the last two lines of every page.
- `measurePads()` fell back to hardcoded DESKTOP paddings whenever `#cap-wrap`
  was absent — which is *always* true on the first pagination and on every
  cover/splash page. Now reads a permanent `#pad-probe` twin; the CSS padding
  rules are mirrored onto `#cap-probe` and **must stay mirrored**.
- The web-font guard `status !== 'loaded'` never fired: at inline-script time
  no font request has started, so status is already `loaded`. The whole
  session paginated on Georgia metrics. Now awaits `fonts.load(...)` explicitly.
- `repaginateKeepingPosition()` anchored on `{kind, book}` via `findIndex`, so
  it returned the FIRST page of that kind — a reader 400 pages into Book IV
  was thrown 165 pages back on every rotation, then that position was written
  to localStorage and the hash. Now anchors on a monotonic sentence id (`gi`).
- A sentence longer than one page was pushed as an over-tall page and silently
  clipped by `overflow:hidden` — those lines existed on no page at all. Now
  split on word boundaries.
- Swipe had no vertical, velocity, multi-touch or target guard: a near-vertical
  drag turned the page, and **a thumb resting at the screen edge inverted the
  direction** (touches[0] was the thumb). Rewritten to track one identified
  finger.
- No `env(safe-area-inset-*)` anywhere despite `viewport-fit=cover`; no
  `overscroll-behavior` (Android pull-to-refresh reloaded the book); no
  `touch-action`; `:hover` latched after tap; theme dots were 12px targets and
  **all five were off-screen at 390px**.

**Do not "fix" `html, body { height: 100% }` to `100vh`/`100dvh`** — checked
deliberately. `100vh` is the LARGE viewport on iOS and pushes the bar
off-screen; `100dvh` would repaginate the whole book every time the URL bar
slides. The resize listener now ignores height-only jitter under 140px for the
same reason.

**Trap:** the preview pane reports `innerWidth: 0` right after navigate, and
`geom()`'s `Math.max(320, ...)` floors make a 0x0 pagination look plausible
rather than broken (4293 pages vs 1449). A `ResizeObserver` on `#stage` now
rebuilds once real layout arrives. When verifying, always settle the viewport
first — and serve over `python3 -m http.server`, because the pane caches
`file://` snapshots and will happily show you the previous build.

## illustrated.html — desktop pass (done, same session)

The mobile cures applied upstairs, keeping the basics (dark desk, floating
paper panel, side-by-side spread):

- **One bar everywhere.** `#bottom-bar` is retired (`display:none`, markup
  kept so render()'s writes stay harmless); `#top-bar` has `order: 3` in the
  BASE rules now, so every size gets a single 44px bar at the bottom — dark
  on desktop (the desk), paper running-foot on narrow. Prev/Next Book are
  gone (they duplicated the picker); `‹ ›` page arrows and the `n/total`
  position (`#il-label`) are in the bar on all sizes. Stage vertical padding
  26/20 → 12/12. Net: stage 674 → 756px tall at 1280x800.
- **Plateless budget fixed.** `capAvail` for plateless pages was
  `stH*.80 - 90`, which left ~120px of dead paper at the foot of every page —
  and Books X–XXIV are ALL plateless. Now `stH - pad.plain.y - 24`, measured
  against the real geometry. Desktop plateless pages went to ~1160 chars,
  zero clipping; phones gained too (1193 → 1038 pages).
- **Stacked plates never crop.** When the stacked height clamp engages, the
  plate narrows to its true ratio and centres (`artW = min(artAvailW,
  artH*plateR)` + auto margins) instead of being cover-cropped — at a 700px
  window the old path shaved 14% off every square plate (user caught it on
  `artemis-still`: the fleeing handmaids were half-cut). Tipped-in plate
  with paper either side, never a trimmed composition.
- **beside-mode margins are an unconditional 22px in CSS**, so `geom()`'s
  beside branch uses a literal `BM = 22` even when narrow `artMargin()` is 0,
  and subtracts it exactly — the old `stH*.96` fudge clipped 30px of every
  page on a landscape phone (`fill beside`).

**Trap, again and forever:** the preview pane loads pages at 0x0 and never
fires a real `resize`; always `window.dispatchEvent(new Event('resize'))` and
wait ~700ms before trusting page counts, and serve over http.server — the
pane caches `file://` snapshots.

## illustrated.html — unified trim size (done)

**The book has ONE trim size now.** `trim()` picks the box once per
viewport — wide: `min(stage content, H*1.55, 1200) x stage height`
(1135x732 at 1280x800); narrow: the full screen. Every render branch
(cover, title page, beat, plated, plateless) and every pagination budget
lays out inside it. Verified: at each of 1280x800 / 700x800 / 393x852 /
852x393 the panel is a single constant size across cover, title pages,
reading pages and beats, with zero clipping over 300-400-page walks.
Beat and cover plates now tip into the page centred (`margin:auto` inline
on #art-wrap) rather than owning their own panel; the caption column is
capped at 620px and centred by CSS (`.caption-box max-width + auto
margins`) — geom()'s textW mirrors that 620 so the probe measures what
renders. Plateless pages are top-aligned (`align-items:flex-start`): a
short last page reads from the top of the paper like a book's final page.

**Pagination bug found by the tighter budgets — the carried-unit hole.**
The greedy packer reset its buffer to `[u]` after an overflow pop WITHOUT
measuring u alone; a single sentence taller than the page budget then
sailed through unchecked (the length===1 word-split guard never saw it —
the buffer was length 2 when the NEXT unit overflowed) and rendered as a
clipped page. Latent since the beginning: harmless at the old ~640px
budgets where no sentence outgrew a page, exposed by the trim box's
~200px mid-width budget. Fixed: packAndPush now routes EVERY unit —
including carried ones — through one measured `addUnit()` path that
word-splits anything that overruns alone. Diagnosed by stamping pack-time
budget/textW onto each page object and comparing at render (instrumentation
since removed); the probe and render agreed exactly, which is what proved
the page had never been measured at all.

## NEXT ACTIONS, in order

1. **Character sheets: all 12 core sheets exist** in
   `img/characters/<slug>.jpeg`, slug-named. `python3
   data/label_character_sheets.py` regenerates the captioned contact-sheet
   copies in `img/characters/labeled/`. Four sheets are worth regenerating
   before heavy use — see "Sheet defects" below.
2. **Then Book II scene plates**, square 1:1, → `img/bk02/*.jpeg`.
   Six plate prompts already drafted in the pack under "BOOK II".
   Set pieces: dawn assembly, the two eagles, Penelope's web (flashback),
   the storeroom, the night launch.
3. **Book II is already wired**: `bk02` has 8 plates in
   `data/illustrated_plates.json`, all anchors validated against the real
   paragraphs of `seeds/modern.md`. It stays inert until `img/bk02/` exists.
   Validate anchors *before* writing a manifest — a curly apostrophe where
   the seed has a straight one silently WARNs and dumps the plate at the
   book's end.
4. Repeat per book. Cluster guide for which sheets to generate when is in
   the pack under "FULL-EPIC CAST ROSTER".

## Traps that already bit, do not re-learn

- **Anchors are substring matches** against a paragraph in
  `seeds/modern.md`. `build_illustrated.py` prints
  `WARN <bk>: anchor not found` and appends the plate at book end — always
  check build output for WARN, silence is the only success signal.
- **Files the user supplies may have wrong extensions.** The Book I square
  set arrived as `.png` but was JPEG. Verify with `file`, rename to match.
- **Do not trust a browser measurement taken right after resize/navigate.**
  The pane reports `innerWidth: 0` transiently and there's a 150ms
  repagination debounce; measurements taken inside that window are garbage.
  Screenshot first, or re-read after a round trip. A wedged tab reports
  0×0 permanently — open a fresh tab rather than debugging the page.
- **Absolutely-positioned measuring probes**: if the CSS class sets
  `bottom` and you set `top`, the box stretches to the container and
  `scrollHeight` is meaningless. Neutralize `top/bottom/left/right/height/
  max-height` on any probe.
- **Never let an animation carry an element to its correct final state.** A
  paused animation in a throttled tab left plates stuck at `opacity: .3`.
- **Assertions in patch scripts**: `assert "artIn" not in t` false-fails
  because `artInner` contains it. Assert on distinctive strings.
- Page turns use `history.replaceState`, not hash assignment (hash
  assignment pushed one history entry per page).

## Illustration rules that are decided, not open

- **Register**: serious literary edition for adults — Charles Keeping,
  Barry Moser, Alan Lee. NOT children's-storybook, NOT comic pastiche
  (no novelty display faces, halftone wallpaper, sticker stamps, offset
  shadows). The user pushed back on both errors; see CLAUDE.md.
- **The hard scenes** (Cyclops blinding, the slaughter, the hanged maids,
  Melanthius, Calypso's captivity, Ares/Aphrodite): restraint through
  *composition*, not omission — aftermath over act, silhouette, reaction
  as subject, or render Homer's own displacing simile — used because those
  are stronger, not because the material needs covering. The author's
  direction is explicit: do not soften the poem. The binding limit is the
  generator, which refuses nudity and graphic gore outright. Full rules in
  the pack under "REGISTER, AND THE DIFFICULT SCENES".
- **Signature colours are reserved epic-wide** across 39 named sheets and
  collision-checked. Two overlaps are deliberate (the two Mentors;
  Odysseus/Penelope). Do not reassign a colour to free one up.

## Character sheets — 12 of 12 done

All in `img/characters/<slug>.jpeg`, all 2048×2048. Attach the **clean**
sheet when prompting, never the labelled copy in `labeled/` — burnt-in
lettering in a reference tends to leak lettering into the generated scene.

Four sheets were regenerated with PREAMBLE v3 (see the prompt pack) and are
the best in the set: **athena-mentes, odysseus, penelope, halitherses**.
Their v1 versions are parked in `img/attic/*-v1.jpeg` for comparison, not
deleted. The v1 defects were: prompt text rendered into the image as a
caption block (3 sheets), scene panels eating half the canvas (penelope),
landscape format and a tunic that changed colour between views
(halitherses), and a 4-way composite with a malformed bust (odysseus).

Verified after regeneration — a scan for strongly-red pixels across all 12
sheets returns 0.00% everywhere except antinous at 7.96%. Terracotta is his
alone, which is what makes him findable in a crowd of twenty suitors. Rerun
that scan after adding any sheet.

Two remaining soft spots, neither worth a regeneration on its own:

- **eurymachus** and **mentor-real** still carry v1 burnt-in caption text.
  On-model and on-signature otherwise; crop before attaching.
- **halitherses** and **aegyptius** are now both bald, very old, staffed and
  dressed in pale undyed wool. They separate on beard (chest-length white vs
  none) and posture (upright vs bent double) — enough, but never stage them
  in the same panel without checking the result.

## Loose ends, explicitly not done

- Books VIII–XXIV have no art; those 17 books read as text-only in
  `illustrated.html` and show "plates pending" on their splash page.
- **Book IV second pass: manifest + prompts written, art not generated.**
  The book shipped at 1,202 words/plate, ~3× sparser than Book I. Four plates
  added — `sparta-wealth`, `lion-and-fawns`, `agamemnon-falls`,
  `suitors-at-games` (paras 4, 19, 27, 34, validated) — closing two long
  unillustrated runs: paras 24–38 (2,622 words under one sticky image) and
  14–22 (1,883). Brings it to 765 w/plate. Prompts are in the pack under
  "BOOK IV — second pass". Sheets: `telemachus`, `menelaus`, `antinous`,
  `eurymachus`. **The build WARNs 4× for bk04 until the art lands** — that is
  expected, not a regression (`img/bk04/` already exists, so unlike bk08 the
  plates are not skipped wholesale).
- Density across the illustrated books, for calibration:
  I 451 · II 560 · VIII 562 · VI 646 · VII 669 · III 702 · V 713 · IV 765.
- Book I's plates were regenerated against the finished character sheets
  and are live. One defect remains: `phemius-sings` puts **four suitors in
  terracotta-red**, which breaks Antinous's reserved signature. `the-feast`
  from the same batch got it right, so it is a regenerate, not a rule
  problem. `eurycleia-torches` is 1024px where the rest are 2048.
- The user-voice literary compression (task #12) is paused after Book IV;
  it is a separate deliverable from the translation and was never finished.
- Nothing in this repo is committed — the whole `homer-odyssey/` and
  `homer-iliad/` directories are still untracked in git.

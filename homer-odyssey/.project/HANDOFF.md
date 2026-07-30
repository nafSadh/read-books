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

**Illustrated edition: Book I live, Books II–XXIV pending art.**

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

- Books II–XXIV have no art; those 23 books read as text-only in
  `illustrated.html` and show "plates pending" on their splash page.
- Book I's plates were regenerated against the finished character sheets
  and are live. One defect remains: `phemius-sings` puts **four suitors in
  terracotta-red**, which breaks Antinous's reserved signature. `the-feast`
  from the same batch got it right, so it is a regenerate, not a rule
  problem. `eurycleia-torches` is 1024px where the rest are 2048.
- The user-voice literary compression (task #12) is paused after Book IV;
  it is a separate deliverable from the translation and was never finished.
- Nothing in this repo is committed — the whole `homer-odyssey/` and
  `homer-iliad/` directories are still untracked in git.

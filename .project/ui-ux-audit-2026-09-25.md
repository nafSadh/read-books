# Full-Site Audit — 2026-09-25

**Scope**: the whole of lib.sadh.app — all 7 book folders, including `homer-iliad/` and `homer-odyssey/`,
which the [2026-08-20 audit](ui-ux-audit-2026-08-20.md) excluded and which are audited here for the first
time. The scope also covers the root catalog, the docs, the build pipelines, and everything GitHub Pages
publishes. The audit targets `main` at `a4356d6` (2026-08-27). The live site was unreachable from the
audit sandbox (proxy 403), so the repo was served locally. It is what Pages deploys.

**Method**
1. **Smoke pass.** Headless Chromium loaded all 75 HTML files (51 live pages and 24 `data/*-template.html`)
   at 1440×900 and 390×844 and recorded page errors, failed requests, overflow, off-screen controls,
   unlabelled buttons and meta tags.
2. **12 finders**, each read-only and each combining code review, live Playwright interaction at 1440/390/320,
   and scratch-copy rebuilds:
   - one per non-Homer book (5), each also re-checking that book's items from the 2026-08-20 audit
   - Homer navigation, Homer accessibility/mobile, Homer content/build, and the Odyssey `study` and
     `illustrated` pages
   - site level, build reproducibility, and a convention sweep across every page
3. **Adversarial verification** of every finding by independent agents told to refute it. High and medium
   findings got two lenses (*reproduce it yourself* and *trace the code*), plus a *user-impact* tiebreak on a
   split. Low findings got one reproduction.
4. **A completeness critic** read what every finder had checked and proposed 5 uncovered areas: font-host
   failure, print/selection/find, display settings, real phone-browser chrome, and annotation accuracy. Each
   area got its own finder and the same verification.
5. **Deduplication** across finders. The same root cause reported by 2–4 finders is one row, with every
   source kept in the JSON.

**Totals**: **248** findings from 17 finders, **247 survived verification**, and 1 was refuted. After merging duplicates, that is **217 unique findings: 18 high, 114 medium and 85 low**. 18 are regressions of fixes from the 2026-08-20 audit, and 13 are known open items.

**On the verification result**: across 411 verifier votes, only **one finding was refuted**: a claim that
Ctrl+F knocks the Homer page grid out of alignment. The finder had simulated find in script; a verifier drove
the real Chrome find bar with OS-level keystrokes and showed that it never scrolls `overflow:hidden` boxes.
It is listed under *Refuted* below. Elsewhere the verifiers pushed back on degree rather than substance:
- they lowered severity on 20 findings and raised it on 4 (the tables use the verifiers' median)
- they corrected line numbers or scope on many findings, often with measurements that differ from the
  finder's own
- they found extra root causes (e.g. ALI-01's phone padding overrides never apply; PRO-02's real forcing
  line is `fullbleed.html:753`, and the fallback the finder cited is dead code)

The orchestrating agent also re-checked three of the high findings by hand (MED-02, VED-02, HOM-02), and
all three reproduce exactly. Every correction is kept per finding in the companion
[`audit-2026-09-25-findings.json`](audit-2026-09-25-findings.json), which also holds the full detail,
evidence, repro steps, suggested fix and every verifier vote for each row below. Evidence that cites
`scratchpad/work/...` screenshots or scripts refers to the audit's temporary workspace; those files were
not committed.

**Sandbox caveats**:
- Google Fonts could not load, so geometry that depends on the font was measured with fallback fonts. Where
  it matters, the verifiers also measured with a narrower stand-in font, and the conclusions held.
- External image hosts were unreachable too, so the Prophet `illustrations.html` findings describe its
  offline fallback.

---

## Executive summary

The library looks finished on a 1440px desktop, and most of what is wrong is invisible there. The defects
fall into six themes.

### 1. The paged formats silently lose text

This is the most serious problem in the library. Most page-based readers decide page breaks by an
**estimate or a fixed pixel constant** instead of measuring the page. They clip the overflow with
`overflow:hidden` and start the next page at the next block, so the clipped words are **never shown
anywhere**. Nothing on screen says text is missing.

| ID | Page | Loss |
|---|---|---|
| HOM-04 | Iliad + Odyssey `fullbleed`, `pdf-reader` | Page step is a JS constant (920 / 620px), but the CSS lets the page shrink. On phones only **5–10%** of Book I's characters are ever fully visible; tablets in portrait get ~21% |
| ALI-01 | Alice `pdf-reader` | 65 chars × 32 lines per page, assumed rather than measured. Hides **59%** of words at 390px, 76% at 320px, and **34%** on a real 1366×657 laptop viewport |
| ALI-02 | Alice `index.html` (the catalog's "Classic Book") | Measures in a box 52px wider and ~40px taller than the real text box: **5–10%** lost on desktop, 19–31% on phones |
| PRO-01 | Prophet `pdf-reader` | 22 × 55-char estimate. 49 paragraphs lost even at 1440×900, 413 at 390px; 24 of 28 chapters open on a title-only page |
| PRO-02 | Prophet `fullbleed` | The first block on every page is admitted unmeasured (`fullbleed.html:753`). About two-thirds of "On Giving" is never shown |
| KHA-01 | Rubáiyát `mobile` | Centred flex scroller. The numeral, heading and often the whole verse sit above scroll-top 0, where they cannot be reached (FG5 41/101, Whinfield 116/500, Persian 178/178), on desktop too |
| KHA-02 | Rubáiyát `fullbleed` | Transparent page-turn zones cover the scrollable notes, so wheel, touch and keys all turn the page instead of scrolling |

Alice `fullbleed`/`mobile`/`theater` (long paragraphs clipped on short viewports) and the Meditations
`pdf-reader` (its card doesn't grow, so text spills onto the grey backdrop) show the same failure at medium
severity.

**Fix**: one shared, measurement-based paginator for the whole library. Fill a hidden box that is a clone of
the real text box, split blocks that are taller than a page, and re-paginate on resize, zoom, font change
and `fonts.ready`. `alice-in-wonderland/mobile.html` and the Rubáiyát `fullbleed` already measure correctly
and can serve as the model. Add a CI-style check that pages every format at 390/1440 and asserts that every
word of the source is visible on some page.

### 2. Wrong or corrupted text in the content pipelines

These do not look broken, so readers cannot tell anything is wrong. None of the pipelines checks its output
against a count.

- **MED-01 — Meditations**: from Book 4 on, the George Long English is paired with the wrong Greek in about
  **260 of 486 passages**. `collect_texts.py` numbers passages by counting `<p>` tags, but the source's
  paragraph ids are paragraph positions, not passage numbers.
  - The parser, re-run on the fetched source, reproduces the committed JSON exactly (522 of 522 entries),
    so the parser is the cause, not stale data.
  - The notes, modern-English rewrites, Greek toggle and `#m-B.N` links all inherit the error, and Long 12.3's
    second half appears nowhere.
  - The docs claim "484/486 aligned".
- **GAP-01 — Meditations Casaubon reader**: 156 of its 412 passages (Books 6–12) show the modern English and
  notes of a *same-numbered passage from an earlier book*. Casaubon's XI.III, the Christians passage, shows
  IX.III's notes about teething and beards. `assemble-annotations.py` finds passage numbers with a regex over
  the whole document instead of within the book's own `<section>`. This bug is separate from MED-01.
- **VED-01 — Complete Rigveda, Mandala 8**: 24 sūktas (~385 verses) are **empty**, and 28 more show the
  English and title of a different hymn. The source uses Griffith's numbering, which moves the 11 Vālakhilya
  hymns to an appendix.
- **VED-02 — Complete Rigveda Sanskrit**: word-initial C+r clusters, final halants and vocalic ṛ are lost,
  in all three scripts. The Gayatri the landing page points readers to reads `…paracodayāta`
  (`परचोदयात`, verified).
- **HOM-01 / HOM-02 — Odyssey study**:
  - A missing Greek line in Books X, XVI and XXIII shifts ~818 lines to the wrong number and the wrong word
    data.
  - A `580` milestone typo makes **Book XVI render lines 285–480 twice**: 676 Greek lines for a ~480-line
    book, under a range label reading `580–284` (verified).
- **Medium**:
  - Every poem in Alice is flattened into run-on prose (ALI).
  - Rubáiyát FitzGerald-1 quatrain XLIX is numbered LIV (two LIVs, no XLIX), and a parser debug note is shown
    as Heron-Allen's scholarship on 36 quatrains (KHA).
  - Murray's Loeb text is split mid-sentence every 5 lines, with 191 orphan footnote digits (HOM).
  - The Iliad's Cowper text includes an editor's prose commentary shown as verse (HOM).
  - Odyssey study glosses are wrong for ~270 ῥ-initial lemmas (HOM).
  - Meditations' Casaubon reader presents a 1900 editor's Fronto appendix as Book XII (MED).

**Fix**: every one of these would have failed a one-line build assertion: passage count equals source count,
no empty units, lines strictly increasing, a script sanity regex. Add those assertions to each builder and fail
the build on mismatch.

### 3. Controls you cannot reach

- **MED-02**: none of the six reader links on the Meditations landing page can be clicked or tapped. Half-page
  flip zones (`z-index:40`) sit on top of them, so a click turns the page instead (verified: a click lands
  on `#zone-right` and goes to `#p-4`).
- **HOM-03**: Homer's toolbars were sized for 3 editions and have no phone layout. On phones the Odyssey
  reader's theme and settings controls, most editions and every theme in `theater`/`pdf-reader`, and the
  Odyssey `mobile` Next-book button at 320px are all off-screen.
- **VED-04**: every Vedas `fullbleed` table-of-contents click lands on the wrong page, because the click also
  reaches the page-turn handler.
- **Medium**:
  - Prophet `fullbleed` Contents: a click opens page 1.
  - Theater formats (Prophet, Homer, Vedas): tapping to reveal the hidden controls also advances a chapter
    or book.
  - The Odyssey study and illustrated pages hide controls off-screen on phones.

### 4. Regressions and fixes that were never carried over

The 2026-08-20 audit fixed bugs in one copy of logic that is duplicated across books, and the siblings never
got the fix:
- **KHA-03**: the hash-restore race that was fixed in Alice's `reader.html` still breaks the Rubáiyát
  `reader` (deterministic on phone reload).
- The same race breaks the Prophet `reader` (2 of 12 desktop loads land on chapter 1).
- Alice `fullbleed` still writes no hash on desktop page turns.
- **VED-03**: the Rigveda init race came back, triggered by mandala-tab clicks instead.
- The specificity fix in the Alice and Prophet `pdf-reader` only covered the toolbar. The same bug still
  hides theme dots and blocks the phone padding.

18 findings are marked **regression**. The structural cause is copy-pasted readers with no shared code.

### 5. Keyboard, screen-reader and phone basics, missed everywhere

The 2026-08-20 baseline (theme-dot buttons, aria-labels, prefixed keys) mostly held for the five books it
covered. Homer never got it. Below that baseline, the same defects appear in every book:
- **Global key handlers take Space and arrow keys away from focused buttons** (in theater, Space on
  "Previous" goes *forward*).
- **Closed drawers stay in the Tab order.**
- **Esc fails in five pages.** Alice's `reader` throws a `ReferenceError`.
- **JS smooth scrolling ignores `prefers-reduced-motion` on every page.**
- **`mobile.html` disables pinch-zoom** and offers no text-size setting (Alice, Prophet, both Homer books).
- **Greek is not marked `lang="grc"`** (Meditations: 23.8k words; Odyssey), and the **Vedas pages declare
  `lang="bn"` around English UI**.
- Touch targets are under 40px across Homer, and contrast fails in several themes.

### 6. The site itself

- **847 MB published against GitHub Pages' 1 GB limit.** `.nojekyll` publishes the whole repo, and about
  **557 MB is files no page uses**. Most of that is 486 MB of Odyssey draft art in `img/attic` and
  `img/characters`. Illustrating the Odyssey's remaining 12 books at the current rate (~17 MB per book) would
  cross 1 GB, and **every deploy of the entire library would then fail**.
- `data/` is not private, as AGENT_README claims: 24 raw templates are live as broken, JS-erroring pages.
  `.claude/launch.json` and a Homer changelog line expose local `/Users/...` paths and a libgen reference.
- 39 of 43 reader pages have **no link back** to their book or to the catalog.
- There is no favicon, 404 page, `robots.txt` or Open Graph card anywhere. The catalog still omits the
  Odyssey `study` and `illustrated` pages.
- Build reproducibility is mixed:
  - Homer, the Rubáiyát readers and the Odyssey illustrated edition rebuild byte-identically.
  - Regenerating the Rubáiyát Persian seed **permanently deletes all its notes**, because the inputs needed to
    restore them are not in the repo.
  - The Odyssey `study.json` depends on a macOS temp path that is not in the repo.

### 7. Found only by the completeness critic's gap round

The critic reviewed every finder's list of checks and found five areas nobody had covered. Each got a
finder and the same verification (GAP-xx rows):

- **Font host hanging (GAP-17).** Every page loads Google Fonts with a stylesheet `<link>` that blocks both
  rendering and scripts. When `fonts.googleapis.com` hangs instead of failing (a blackholed route, a
  captive portal, a corporate firewall), **all 51 pages paint nothing and run no script** until the request
  times out. In a 30-second hang, first paint came at 30.0–30.5 s on every page. The 2026-08-20 audit saw
  this symptom and dismissed it as a sandbox artifact. Fix: load the font stylesheet in a non-blocking way.
  Three pages (Alice `fullbleed` and `mobile`, Meditations `fullbleed`) also wait on `fonts.ready` with no
  timeout.
- **Print, selection, find (GAP-03, 18, 30, 31).** No page has print styles:
  - The fixed top bar hides about one line per printed sheet in every scrolling reader.
  - 32 page-based formats print only the current screen.
  - Book-spread formats block text selection, and double-clicking a word turns the page.
- **Display settings (GAP-02, 08, 09, 19, 20, 33).**
  - Windows High Contrast removes every "selected" state and all the theme swatches.
  - Meditations and Vedas `fullbleed` drop text at 200% zoom.
  - Only the catalog follows the OS dark-mode setting.
  - Browser font-size settings are ignored everywhere (0 `rem` units).
- **Real phone browsers (GAP-10 to 14).**
  - `100vh` book boxes sit under the iOS and Android toolbars.
  - `viewport-fit=cover` without safe-area padding puts the notch over reading lines in landscape.
  - 13 inputs smaller than 16px trigger iOS auto-zoom.
  - About 20 formats can be reloaded by an accidental pull-to-refresh.
  - `homer-odyssey/illustrated.html` already handles all of these correctly and is the model to copy.
- **Annotation accuracy (GAP-01, 04–06, 21–27).** Besides the Casaubon mis-injection:
  - Leopold notes state wrong identities as fact. The 1.4 great-grandfather should be Catilius Severus;
    at 8.25 Lucilla is called "mother of Lucius Verus"; and 11.3 claims two references to Christians where
    there is one.
  - The Meditations landing page prints two Greek "quotations" that appear nowhere in the text.
  - The curated Vedas label RV 5.82.5 as "3.62.18".
  - The Rubáiyát copy mis-dates the fifth edition and Heron-Allen's analysis.

### What is in good shape

- Homer's `data/build.py` (both books) and `build_illustrated.py` regenerate all 14 outputs
  **byte-identically**. Every edition has 24 complete books, and `reader.html` shows every line of every
  edition.
- All 1,259 internal `href`/`src` references and every in-page anchor resolve. There are no secrets in any
  tracked file.
- Every page stores prefs under a book-prefixed key, with no collisions on the shared origin. 49 of 51 pages
  offer the 5 standard themes, and all 41 non-Homer pages have real `<button aria-label>` theme dots.
- 36 of the 38 pages that should keep a reading position in the URL do write and restore it.
- The previous audit's P0 fixes still hold, except where this report marks a regression:
  - Prophet theater renders.
  - Meditations' duplicate `const` is gone.
  - Rigveda deep links `#3.62` and `#10.129` restore on load.
  - The Alice `pdf-reader` toolbar fits.

---

## Cross-cutting patterns

These recur across books and are cheaper to fix as sweeps than one finding at a time:

| Pattern | Where | Sweep fix |
|---|---|---|
| Pagination by estimate or constant, with overflow clipped | Alice pdf/index/fullbleed/mobile/theater, Prophet pdf/fullbleed, Rubáiyát mobile/fullbleed, Meditations pdf, Homer fullbleed/pdf ×2 | One measured paginator (see §1), plus a "every word visible" test |
| Hash restore racing the scroll observer | Prophet reader, Rubáiyát reader, Rigveda tabs; fixed only in Alice reader | Capture `location.hash` synchronously at script start, set `history.scrollRestoration='manual'`, suppress observer writes until restored |
| Global keydown ignoring the focused element and modifiers | Every book | `if (e.target.closest('button,a,input,select,textarea,[contenteditable]')) return;` and skip when `e.altKey\|\|e.ctrlKey\|\|e.metaKey` |
| Closed drawers and sheets remain focusable | Every book | `inert` on closed panels; return focus to the opener on close |
| Invisible full-page click zones over content | Meditations landing, Rubáiyát fullbleed, Prophet fullbleed TOC, Vedas fullbleed TOC, theater taps | Edge strips only, or ignore clicks whose target is inside a link, control or scroller |
| `user-scalable=no` / `maximum-scale=1` | Alice, Prophet, Iliad and Odyssey `mobile.html` | Remove, and add a text-size control |
| JS `scrollTo({behavior:'smooth'})` ignoring reduced motion | All 51 pages | One helper: `behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'` |
| Language markup | Meditations and Odyssey Greek (no `grc`), Vedas `lang="bn"` around English UI, Rubáiyát `en-fa-Latn` | `lang="grc"` on Greek, `lang="en"` on `<html>` in Vedas with `lang` on the Sanskrit/Bengali blocks, `lang="fa-Latn"` |
| Content builders without assertions | Meditations, Rigveda, Odyssey study, Rubáiyát, Alice | Per-builder count and ordering assertions (see §2) |
| Docs drift | Every book CLAUDE.md, AGENT_README (`data/` "private"), root todo (still stale after the last audit said it was reconciled) | Fix with the code in the same commit; drop the "data/ is private" claim |

---

## Per-book findings

Severity is the verifiers' median. Status: `new`, **`regr`** (the 2026-08-20 audit said it was fixed),
or `open` (a known, documented open item). IDs match `audit-2026-09-25-findings.json`, which holds each row's
detail, evidence, repro, fix and verifier corrections.

### Homer — Iliad & Odyssey (first audit) (38: 4 high, 24 medium, 10 low)

| ID | Sev | Status | Area | Where | Finding |
|---|---|---|---|---|---|
| HOM-01 | HIGH | new | content | `odyssey/data/build_study_data.py:142, odyssey/seeds/greek.md +2` | Study reader: Greek is missing a line in Books X, XVI and XXIII, so ~818 lines carry wrong line numbers and the word data of the neighbouring line |
| HOM-02 | HIGH | new | content | `odyssey/data/build_study_data.py:125, odyssey/data/build_study_data.py:159 +2` | Study reader Book XVI prints Greek lines 275–480 twice; Book VI has an empty '320–319' chunk |
| HOM-03 | HIGH | new | mobile | `odyssey/data/reader-template.html:149-156, odyssey/data/reader-template.html:319 +11` | Toolbars overflow phone widths: edition, theme and settings controls unreachable in theater, pdf-reader, fullbleed, the Odyssey reader and Odyssey mobile at 320px |
| HOM-04 | HIGH | new | navigation | `iliad/data/fullbleed-template.html:50, iliad/data/fullbleed-template.html:88-90 +19` | fullbleed.html and pdf-reader.html pagination breaks on phones, tablets in portrait and narrow windows: blank pages, cut-off lines, stuck on page 1 |
| HOM-05 | MED | new | a11y | `iliad/data/reader-template.html:708-729, odyssey/data/reader-template.html:714-735 +9` | Keyboard handlers take over keys meant for focused controls and ignore modifiers; closed drawers stay in the Tab order; mobile.html has no keyboard support |
| HOM-06 | MED | new | a11y | `iliad/data/mobile-template.html:5, odyssey/data/mobile-template.html:5 +2` | mobile.html disables pinch-zoom and has no text-size setting, so readers cannot enlarge text |
| HOM-07 | MED | new | a11y | `iliad/data/reader-template.html:181-199, iliad/data/reader-template.html:388-394 +16` | Theme dots and icon-only controls miss the accessibility baseline: what the smoke pass's 5 and 24 unlabeled buttons are |
| HOM-08 | MED | new | a11y | `iliad/data/reader-template.html:134-146, iliad/data/reader-template.html:189-191 +12` | Touch targets well below 40px across all Homer formats |
| HOM-09 | MED | new | a11y | `iliad/data/reader-template.html:69, iliad/data/reader-template.html:271-275 +12` | Colour contrast failures: dark-blue secondary text, theater controls, pdf-reader active edition and focus ring, mobile labels, study line numbers, illustrated back link |
| HOM-10 | MED | new | a11y | `odyssey/data/reader-template.html:2, odyssey/data/reader-template.html:597-607 +7` | Ancient Greek text is announced as English: no lang="grc" in any Odyssey reader, the study page or the word popover |
| HOM-11 | MED | new | a11y | `odyssey/data/study-template.html:340, odyssey/data/study-template.html:110-117 +6` | Study reader a11y: word popovers are mouse/touch-only, Greek lacks lang, targets 13–27px, line numbers ~2:1 contrast, reduced motion ignored |
| HOM-12 | MED | new | a11y | `odyssey/data/illustrated-template.html:879-884` | Illustrated keyboard: global key handler hijacks Space and arrows on focused controls (Space on 'Previous page' goes forward; Space cannot pick a theme) |
| HOM-13 | MED | new | a11y | `odyssey/data/illustrated-template.html:378, odyssey/data/illustrated-template.html:311 +2` | Illustrated on phones: back link's accessible name is '←', theme control off-screen at 320px, targets 26–34px, dark-blue bar text 3.4:1 |
| HOM-14 | MED | new | content | `odyssey/seeds/murray.md:29, odyssey/seeds/murray.md:31 +7` | Murray (Loeb 1919) edition: text split mid-sentence at every 5-line chunk and full of orphan footnote numbers |
| HOM-15 | MED | new | content | `iliad/seeds/cowper.json:4790, iliad/seeds/cowper.json:7615 +8` | Iliad Cowper seed shows an editor's prose commentary as verse and has scanning errors (OCR), despite the changelog saying commentary was excluded |
| HOM-16 | MED | new | content | `odyssey/data/study-template.html, odyssey/seeds/study.json +5` | Attribution and licensing gaps: CC BY-SA treebank data shipped without credit, no translator credit on the illustrated edition, Pope shown as the Odyssey's sole translator |
| HOM-17 | MED | new | content | `odyssey/data/build_study_data.py:50, odyssey/seeds/study.json` | Study: ~270 word popovers show a wrong lemma and gloss because the lemma normaliser strips a leading ῥ |
| HOM-18 | MED | new | mobile | `iliad/data/mobile-template.html:110-132, odyssey/data/mobile-template.html:110-135 +2` | No way out on phone formats: mobile.html has no home or reader link, and theater hides its only link at ≤480px |
| HOM-19 | MED | new | mobile | `odyssey/data/study-template.html:56-62, odyssey/data/study-template.html:166-172 +1` | Study reader on phones: English toggle and all five theme dots (and Translit at 320px) sit off-screen in a horizontally scrolling top bar |
| HOM-20 | MED | new | mobile | `odyssey/data/illustrated-template.html:539-548, odyssey/data/illustrated-template.html:568-569 +1` | Illustrated on short desktop windows (viewport height ≲620px): stacked layout leaves 3–4 lines of text per page, ~2,500 page turns |
| HOM-21 | MED | new | navigation | `iliad/data/theater-template.html:264-267, iliad/data/theater-template.html:269-273 +8` | Theater: tap, click, Space, j or a short swipe on the text jumps to the next whole book and discards your place; mobile.html swipe does the same |
| HOM-22 | MED | new | navigation | `iliad/data/fullbleed-template.html:63, iliad/data/fullbleed-template.html:167-172 +6` | fullbleed/pdf page count goes stale: reading forward into a shorter book adds 9-15 blank or repeated pages, and every page turn visibly reflows the columns |
| HOM-23 | MED | new | navigation | `iliad/data/reader-template.html:14, iliad/data/reader-template.html:593 +14` | Your place inside a book is never saved: reload, resize, rotation or an edition switch returns to the start of a 25-57 page book |
| HOM-24 | MED | new | navigation | `iliad/data/mobile-template.html:166-167, iliad/data/mobile-template.html:205-215 +6` | mobile.html and theater.html drop taps made during the fade animation, so the display and internal state disagree (books silently skipped, wrong edition shown) |
| HOM-25 | MED | new | navigation | `odyssey/data/illustrated-template.html:978-980, odyssey/data/illustrated-template.html:932-951 +2` | Illustrated: the reading position moves on every reload and every return visit (page index restored against the pre-web-font pagination) |
| HOM-26 | MED | new | navigation | `odyssey/data/illustrated-template.html:847, odyssey/data/illustrated-template.html:938-951 +1` | Illustrated: page index kept in prefs, and a shared #bk-N-pM link opens in a different book on another screen size (the book-number fallback never runs) |
| HOM-27 | MED | new | perf | `odyssey/data/illustrated-template.html:212-218, odyssey/data/illustrated-template.html:781-786 +3` | Illustrated serves full 2048×2048 JPEGs everywhere: ~11 MB to reach the first page of Book I on a phone, 5 × 2 MB files shown as 70px tiles |
| HOM-28 | MED | new | perf | `odyssey/data/illustrated-template.html:611-708, odyssey/data/illustrated-template.html:978-997 +1` | Illustrated pagination blocks the main thread ~2.7 s twice on every phone load and ~3.9 s on rotation |
| HOM-29 | LOW | new | a11y | `iliad/data/reader-template.html:593-598, iliad/data/mobile-template.html:177-184 +4` | Reader formats have no heading or landmark structure for the book being read |
| HOM-30 | LOW | new | content | `odyssey/index.html:6, odyssey/index.html:182 +6` | Odyssey landing page and meta descriptions miscount editions and formats (Murray left out) |
| HOM-31 | LOW | new | content | `iliad/seeds/pope.json:17029, iliad/seeds/butler.json:165 +10` | Other transcription errors in the seeds (typos, stray footnote numbers, a merged couplet) |
| HOM-32 | LOW | new | content | `odyssey/seeds/modern.md` | Modern translation typography inconsistent between books |
| HOM-33 | LOW | new | content | `odyssey/data/study-template.html:248-252, odyssey/data/study-template.html:263-266` | Study transliteration drops capitals on υ-diphthongs and prints the Greek question mark as ';' |
| HOM-34 | LOW | new | docs | `odyssey/CLAUDE.md:7, odyssey/CLAUDE.md:13 +9` | Maintainer docs and comments are stale about editions, hash format, UA redirect and pagination verification |
| HOM-35 | LOW | new | navigation | `iliad/data/theater-template.html:286-310, iliad/data/mobile-template.html:282-305 +6` | Changing the URL hash is ignored in theater, mobile, fullbleed and pdf-reader |
| HOM-36 | LOW | new | navigation | `iliad/data/fullbleed-template.html:100, iliad/data/fullbleed-template.html:185-186 +8` | Small navigation gaps: 'Back to reader' links drop your book and edition, fullbleed book buttons look enabled but do nothing, invalid hashes stay in the URL |
| HOM-37 | LOW | new | navigation | `odyssey/data/study-template.html:328, odyssey/data/study-template.html:355 +2` | Study reader passage links are thrown away: #ch-9-100 opens Book I and the hash is overwritten; in-page hash changes are ignored |
| HOM-38 | LOW | new | perf | `odyssey/data/build.py:114-127, iliad/data/build.py:39-51 +6` | Odyssey pages take ~8s to show any text on a throttled phone: every format inlines all 6 editions (1.5 MB gzip), and the header shows wrong placeholder text meanwhile |

### alice-in-wonderland (26: 2 high, 17 medium, 7 low)

| ID | Sev | Status | Area | Where | Finding |
|---|---|---|---|---|---|
| ALI-01 | HIGH | new | content | `pdf-reader.html:604-642, pdf-reader.html:245-252 +2` | pdf-reader hides most of the book on phones and a large share on common laptop screens |
| ALI-02 | HIGH | new | content | `index.html:419-433, index.html:127-141 +2` | index.html (the 'Classic Book') drops 5–8% of the text on desktop and 19–30% on phones |
| ALI-03 | MED | new | a11y | `fullbleed.html:1400-1410, fullbleed.html:1034-1042 +1` | fullbleed has no keyboard route to jump to a chapter or page |
| ALI-04 | MED | new | a11y | `reader.html:2059-2065` | reader.html: Escape throws a ReferenceError and never closes the chapter sidebar |
| ALI-05 | MED | new | a11y | `reader.html:157-172, reader.html:736-739 +6` | Invisible controls take keyboard focus: closed sidebars, reader's hidden chapter scrubber, and back-to-top |
| ALI-06 | MED | new | a11y | `reader.html:2033-2058, web-reader.html:812-838 +4` | Global key handlers stop Space from activating focused buttons in 6 formats; in theater, Space on Back goes forward |
| ALI-07 | MED | new | a11y | `fullbleed.html:1048-1049, index.html:192 +7` | No Alice format honours prefers-reduced-motion |
| ALI-08 | MED | new | a11y | `gen_mobile.py:32, mobile.html:5` | mobile.html blocks pinch-zoom and has no text-size control |
| ALI-09 | MED | new | a11y | `fullbleed.html:349-355, fullbleed.html:388-398 +6` | Navigation controls and labels have very low contrast (1.6–3.1:1) |
| ALI-10 | MED | new | a11y | `reader.html:818-822, reader.html:813 +3` | No semantic chapter headings, main landmark or page-change announcements (reader.html and paginated formats) |
| ALI-11 | MED | new | content | `fullbleed.html:709-736, gen_mobile.py:313 +2` | Long paragraphs are clipped on short viewports in fullbleed, mobile and theater (theater cuts top and bottom) |
| ALI-12 | MED | new | content | `reader.html:874, fullbleed.html:627 +7` | Every poem in the book is flattened into run-on prose (source data, all 9 formats) |
| ALI-13 | MED | **regr** | mobile | `fullbleed.html:328-343, fullbleed.html:383-398 +1` | fullbleed footer overflows phones on content pages; at 320px Prev, the page counter and the theme button are off-screen |
| ALI-14 | MED | new | mobile | `gen_mobile.py:176-183, fullbleed.html:349-354 +4` | Primary phone navigation uses touch targets far below 40px, and tapping the theme button also changes the theme |
| ALI-15 | MED | new | navigation | `fullbleed.html:919-930, fullbleed.html:1159-1179 +1` | fullbleed desktop page flips never update the URL hash, so reload or bookmark loses your place |
| ALI-16 | MED | new | navigation | `fullbleed.html:1481-1486` | fullbleed page-number editor jumps one spread short; typing 1 opens the Contents page |
| ALI-17 | MED | new | navigation | `fullbleed.html:1499-1507, fullbleed.html:942-977 +1` | Arrow/Space keys inside fullbleed's page-number box flip the page and permanently freeze navigation |
| ALI-18 | MED | new | navigation | `fullbleed.html:1384-1398, fullbleed.html:1529-1540 +2` | fullbleed chapter jumps and TOC page numbers go stale after a resize or rotation |
| ALI-19 | MED | new | navigation | `pdf-reader.html:961-971` | pdf-reader flips one page per wheel event, so a trackpad swipe skips dozens of pages |
| ALI-20 | LOW | new | consistency | `web-reader.html:729-736, web-reader.html:885-890 +1` | web-reader line-spacing buttons never show the active choice, and every page click rewrites prefs |
| ALI-21 | LOW | new | consistency | `index.html:250, index.html:804-814 +2` | Small input and CSS gaps: index.html has no swipe and a dead hover colour; mobile.html cannot be paged with a mouse |
| ALI-22 | LOW | open | consistency | `web-reader.html:45-92, web-reader.html:541-546 +4` | Tracked open items: web-reader's private theme set, narrow theme-dot hit areas, no Alice landing page |
| ALI-23 | LOW | new | docs | `.project/todo.md:23-45, .project/changelog.md:3 +7` | Alice docs drift: garbled todo, stale changelog and README, and build script at the book root |
| ALI-24 | LOW | **regr** | mobile | `pdf-reader.html:444-470, pdf-reader.html:113-126 +1` | pdf-reader's specificity fix was only partial: phone padding and font-toggle hiding still never apply |
| ALI-25 | LOW | new | mobile | `theater.html:130-135, theater.html:94-100 +2` | theater polish: chapter label runs under the theme button at 320px; seek slider lacks Home/End/Page keys |
| ALI-26 | LOW | open | navigation | `index.html, mobile.html +5` | Six Alice formats still keep no reading position (known gap) |

### aurelius-meditations (20: 2 high, 11 medium, 7 low)

| ID | Sev | Status | Area | Where | Finding |
|---|---|---|---|---|---|
| MED-01 | HIGH | new | content | `data/collect_texts.py:325-386, data/collect_texts.py:497-515 +4` | English is shown against the wrong Greek and wrong annotations in about 260 of 486 passages (Books 4–12) |
| MED-02 | HIGH | new | navigation | `index.html:237-241, index.html:496-497 +1` | None of the six reader links on the Meditations landing page can be clicked or tapped |
| MED-03 | MED | new | a11y | `reader-casaubon.html:134-142, reader-casaubon.html:506-519 +4` | Invisible controls stay in the keyboard tab order (closed sidebar, hover-only scrubber, closed mobile sheets) |
| MED-04 | MED | new | a11y | `reader.html:7959-7961, reader-casaubon.html:5769 +4` | Space on a focused button scrolls/turns the page instead of pressing the button |
| MED-05 | MED | new | a11y | `fullbleed.html:852-853, fullbleed.html:869-903` | fullbleed.html ignores prefers-reduced-motion: 3D page-flip always animates |
| MED-06 | MED | new | a11y | `data/assemble-reader.py:239, index.html:539 +2` | reader.html Greek text (486 blocks) and landing-page Greek have no lang attribute |
| MED-07 | MED | new | content | `reader-casaubon.html:5398, reader-casaubon.html:2349 +3` | Casaubon reader and fullbleed present the 1900 editor's Fronto appendix as part of Book XII; 3 Casaubon passages left unannotated |
| MED-08 | MED | new | layout | `data/pdf-template.html:48-49, pdf-reader.html` | pdf-reader: the page card does not grow with its content, so text spills onto the grey viewer background on most pages |
| MED-09 | MED | new | mobile | `data/pdf-template.html:90-98, data/pdf-template.html:103-118` | pdf-reader on phones: Greek toggle removed, book select squeezed to a chevron, theme dots off-screen at 320px |
| MED-10 | MED | new | navigation | `fullbleed.html:999-1006, fullbleed.html:1106-1115 +1` | fullbleed: any resize or rotation silently changes the page being read, and the book scrubber/TOC then jump to the wrong book |
| MED-11 | MED | new | navigation | `data/theater-template.html:68-74, data/theater-template.html:131-136` | theater.html: no way to jump between books; 486 passages reachable only by prev/next |
| MED-12 | MED | new | perf | `data/assemble-reader.py:103-126, data/assemble-reader.py:329-349 +1` | reader.html: Greek toggle freezes the page for seconds; 29,190 always-generated .gw::after tooltips dominate the cost |
| MED-13 | MED | new | theme | `reader.html:7984-8013, reader-casaubon.html:5793-5818` | Saved theme/Greek/size prefs apply only after the whole 3 MB reader has parsed: light-theme flash and a layout jump on every load |
| MED-14 | LOW | **regr** | a11y | `data/assemble-reader.py:38, data/assemble-reader.py:364-367 +1` | Reader affordances: detail/Greek toggles don't expose state, and the tablet touch-target fix is width-gated |
| MED-15 | LOW | **regr** | a11y | `data/assemble-reader.py:116-121, .project/todo.md:36` | Greek transliteration tooltips have no keyboard path again, and the code comment's stated fallback doesn't exist |
| MED-16 | LOW | open | build | `generate_sentence_alignments.py, align_sentences_final.py:127,176 +5` | Stray build scripts and raw templates are publicly served; the canonical JSON is not reproducible from the repo |
| MED-17 | LOW | open | consistency | `fullbleed.html:969, fullbleed.html:1102 +1` | Two Meditations formats still store prefs outside the {book}-{format}-prefs convention |
| MED-18 | LOW | new | docs | `CLAUDE.md:23, CLAUDE.md:75 +8` | Docs and labels drift from the shipped Meditations suite |
| MED-19 | LOW | new | navigation | `aurelius-meditations.json, data/collect_texts.py:177-230 +2` | Deep-link gaps: Leopold 12.18 merged into 12.17, unknown #m- ids silently fall back to 1.1, reader keeps only per-Book position |
| MED-20 | LOW | new | perf | `data/build_theater.py:23, data/mobile-template.html:194-206 +1` | Minor per-format UX: theater embeds unused annotations, mobile book-sheet highlight goes stale, pdf keys and drawer |

### gibran-prophet (28: 2 high, 16 medium, 10 low)

| ID | Sev | Status | Area | Where | Finding |
|---|---|---|---|---|---|
| PRO-01 | HIGH | new | content | `pdf-reader.html:664, pdf-reader.html:708 +3` | pdf-reader hides large parts of the text: pagination is a fixed character-count estimate, not measured, and overflow is clipped |
| PRO-02 | HIGH | new | content | `fullbleed.html:761, fullbleed.html:104 +1` | fullbleed never shows the rest of any stanza taller than one page (about two-thirds of 'On Giving' on desktop) |
| PRO-03 | MED | **regr** | a11y | `pdf-reader.html:51, pdf-reader.html:136 +3` | pdf-reader toolbar CSS: theme dots are invisible on every viewport; phone hide rules do not apply, so the toolbar overflows |
| PRO-04 | MED | new | a11y | `reader.html:455, reader.html:144 +4` | reader.html: 28 invisible sidebar links come first in tab order; the chapter scrubber is 28 buttons nested inside a button and shown only on hover |
| PRO-05 | MED | new | a11y | `mobile.html:93, mobile.html:99 +2` | mobile.html: Tab moves through off-screen chapters and scrolls the pager, so the shown text no longer matches the header or hash |
| PRO-06 | MED | new | a11y | `reader.html:2044, fullbleed.html:1508 +2` | Global keyboard shortcuts steal Space from focused buttons (reader, fullbleed, theater, mobile) |
| PRO-07 | MED | new | a11y | `fullbleed.html:390, fullbleed.html:1425 +7` | Click-only <div>/<span> controls have no keyboard path: fullbleed chapter navigation, the illustrations lightbox, pdf thumbnails |
| PRO-08 | MED | new | a11y | `mobile.html:5` | mobile.html turns off pinch-zoom and has no text-size control |
| PRO-09 | MED | new | a11y | `fullbleed.html:390, fullbleed.html:116 +4` | Secondary text and navigation chrome falls well below 4.5:1 contrast in every theme |
| PRO-10 | MED | new | mobile | `theater.html:479, theater.html:482 +1` | theater on touch: tapping to reveal the hidden controls also advances a chapter |
| PRO-11 | MED | new | mobile | `fullbleed.html:351, fullbleed.html:390 +3` | Touch targets well under 40px on primary phone navigation (fullbleed footer, mobile top bar, pdf toolbar) |
| PRO-12 | MED | new | navigation | `reader.html:13, reader.html:1975 +3` | reader.html #ch-N restore lands on chapter 1: the observer overwrites the hash before restoreHash() reads it |
| PRO-13 | MED | new | navigation | `fullbleed.html:485, fullbleed.html:608 +1` | fullbleed Contents page: clicking a chapter flips to page 1, because the invisible click zone covers the TOC |
| PRO-14 | MED | new | navigation | `fullbleed.html:1491, fullbleed.html:959` | fullbleed page-number box lands one spread early, and the last spread writes an out-of-range #p-N that reloads to the cover |
| PRO-15 | MED | new | navigation | `fullbleed.html:1543, fullbleed.html:1402` | fullbleed resize or phone rotation jumps to a different chapter, and chapter links go stale |
| PRO-16 | MED | new | navigation | `reader.html:444, mobile.html:367 +2` | reader.html phone redirect to mobile.html drops #ch-N, and 'Reader' links on phones bounce back |
| PRO-17 | MED | new | navigation | `pdf-reader.html:963` | pdf-reader: each wheel event flips a page, so one trackpad gesture skips dozens of pages |
| PRO-18 | MED | new | security | `pdf-reader.html:893, pdf-reader.html:873` | pdf-reader shows a blank page when localStorage is blocked (unguarded getItem/setItem) |
| PRO-19 | LOW | new | a11y | `theater.html:467, theater.html:500` | theater hides its controls while keyboard focus is on them; digit jumps skip the animation lock |
| PRO-20 | LOW | new | a11y | `theater.html:109, reader.html:13 +2` | prefers-reduced-motion is ignored in theater, reader, index, illustrations and pdf-reader |
| PRO-21 | LOW | open | consistency | `index.html:518, theater.html:449 +3` | Four pages still store a bare theme string instead of {book}-{format}-prefs JSON (known open item) |
| PRO-22 | LOW | open | content | `illustrations.html:322, illustrations.html:487 +1` | illustrations.html depends entirely on three third-party hosts (known open item); offline it is 29 empty boxes |
| PRO-23 | LOW | new | content | `illustrations.html:768, illustrations.html:714` | illustrations lightbox shows a broken image when the Gutenberg hi-res host fails, even though the thumbnail loaded |
| PRO-24 | LOW | new | content | `fullbleed.html:1041` | fullbleed left running header names the right page's chapter |
| PRO-25 | LOW | new | content | `seeds/chapters.json, reader.html:763 +1` | Nine unconverted Gutenberg '--' em-dashes appear in every format |
| PRO-26 | LOW | new | docs | `CLAUDE.md:70, CLAUDE.md:56 +3` | Prophet docs drift: stale flip-hash 'known gap', false restore claim, undocumented redirect, garbled todo entry, changelog behind |
| PRO-27 | LOW | new | navigation | `index.html:285, index.html:438` | Landing page chapter list looks clickable but has no links |
| PRO-28 | LOW | new | perf | `fullbleed.html:1556, fullbleed.html:1532` | fullbleed does nothing until Google Fonts finish: stuck on an inert cover if the font CDN hangs; saved theme not applied meanwhile |

### khayyam-rubaiyat (23: 3 high, 12 medium, 8 low)

| ID | Sev | Status | Area | Where | Finding |
|---|---|---|---|---|---|
| KHA-01 | HIGH | new | mobile | `data/mobile-template.html:57-60, mobile.html` | mobile.html: top of every tall slide (numeral, heading, often the whole verse) is cut off and cannot be scrolled to |
| KHA-02 | HIGH | new | navigation | `data/fullbleed-template.html:490-492, data/fullbleed-template.html:263-265 +2` | fullbleed.html: facing notes can't be scrolled because transparent click zones cover the page (phones and desktop verso) |
| KHA-03 | HIGH | **regr** | navigation | `data/reader-template.html:13, data/reader-template.html:1094-1110 +3` | reader.html: scroll observer overwrites the incoming hash before restoreHash() runs, so bookmarks and reloads on phones land at group 1 or in the wrong edition |
| KHA-04 | MED | new | a11y | `data/reader-template.html:144-150, data/reader-template.html:377-411 +4` | Closed or hidden UI stays in the keyboard tab order: reader's chapter drawer (50 links before the top bar), 50 invisible scrubber buttons nested inside the Back-to-top button, and mobile's aria-hidden bottom sheets |
| KHA-05 | MED | new | a11y | `data/reader-template.html:1278-1291, data/fullbleed-template.html:1264-1270 +5` | Global key handlers hijack Space and arrows on focused controls (Space on 'Prev' goes forward), and several navigators are click-only |
| KHA-06 | MED | new | a11y | `data/build_reader.py:350, data/build_reader.py:83 +6` | Language markup: English apparatus inside lang="fa", Persian headings tagged English, and an invalid 'en-fa-Latn' tag on every transliteration line |
| KHA-07 | MED | new | content | `seeds/fitzgerald.json:442, data/fetch_fitzgerald.py:31-49 +3` | FitzGerald 1st edition quatrain XLIX ('Chequer-board') is numbered LIV, so there are two LIVs, no XLIX, and #q-first-54 means different poems in different formats |
| KHA-08 | MED | new | content | `data/parse_pg38511.py:443, seeds/heron-allen.json:35 +1` | Parser debug note '(composite: N source blocks in original; keeping first)' is shown as Heron-Allen's scholarship on 36 of 101 FG5 quatrains, and those analyses silently lose sources |
| KHA-09 | MED | new | content | `data/mobile-template.html:73-89, data/pdf-template.html:72-78 +2` | mobile.html and pdf-reader.html don't style the payload they render: FitzGerald indent missing, transliteration unstyled, gloss apparatus runs together |
| KHA-10 | MED | new | content | `data/reader-template.html:874, data/reader-template.html:467-471` | reader.html credits 'translated by Edward FitzGerald' on the Whinfield and Nicolas editions |
| KHA-11 | MED | new | layout | `data/pdf-template.html:59-70` | pdf-reader.html: page card is squeezed to 60vh and the quatrain and notes spill outside it onto the grey viewer at <3:1 contrast |
| KHA-12 | MED | new | mobile | `data/reader-template.html:523-536, data/reader-template.html:749 +1` | reader.html per-quatrain '…' details button: invisible on touch, 22×22px, opens its panel above the verse and pushes the poem off-screen; overlaps the first Persian word |
| KHA-13 | MED | new | mobile | `data/reader-template.html:756-766, data/reader-template.html:786-793 +4` | Edition switcher on phones: at 320px the reader shows 2 of 5 editions with no scroll hint; chips are below 40px and the reader's tabs are named 'FG1/Wh/Ni/فا' |
| KHA-14 | MED | new | mobile | `data/pdf-template.html:106-116, data/pdf-template.html:127-140 +1` | pdf-reader.html at 320px: toolbar overflows so the dark-blue theme is unreachable and the edition select is 18px wide; a saved zoom clips the page with no controls to undo it |
| KHA-15 | MED | new | navigation | `data/fullbleed-template.html:995-1017, data/fullbleed-template.html:1235-1240 +1` | fullbleed and pdf-reader #p-N hashes carry no edition, so shared or bookmarked links open a different poem (or the cover) for another reader |
| KHA-16 | LOW | open | consistency | `index.html:447-476, index.html:293 +1` | index.html edition cards: carry-over layout nits from the last audit |
| KHA-17 | LOW | new | content | `data/parse_pg38511.py, data/fetch_fitzgerald.py +3` | Gutenberg source markup and parse artifacts shown verbatim: _underscore italics_, '--' dashes, and 10 Whinfield notes whose subject was folded into the MS refs |
| KHA-18 | LOW | new | content | `data/transliterate.py:19-30, CLAUDE.md:22` | Transliteration leaks Arabic U+0654 into the Latin text, and 60% of words have no vowels, yet it is presented as 'phonetic' |
| KHA-19 | LOW | new | docs | `CLAUDE.md:7-9, CLAUDE.md:48 +5` | Docs drift: data/ is web-served, not 'never web-served' (raw templates render broken pages), plus stale suite and build descriptions |
| KHA-20 | LOW | **regr** | layout | `data/reader-template.html:491, data/reader-template.html:716-722 +2` | reader.html: Persian transliteration is left-aligned at the opposite edge from its line, despite CLAUDE.md and commit ccd986d saying it is right-aligned |
| KHA-21 | LOW | new | theme | `data/reader-template.html:1317-1343, data/fullbleed-template.html:1225-1232 +3` | Saved theme is applied only at the end of 0.45–1.9 MB pages: light-theme flash for dark-theme readers in every format |
| KHA-22 | LOW | new | theme | `index.html:167-171` | index.html: light-azure and dark-blue theme swatches are the same colour |
| KHA-23 | LOW | open | theme | `data/reader-template.html:895-909, data/fullbleed-template.html:1248-1254` | Theme button on touch both cycles the theme and opens the palette (reader, fullbleed) |

### vedas (18: 4 high, 7 medium, 7 low)

| ID | Sev | Status | Area | Where | Finding |
|---|---|---|---|---|---|
| VED-01 | HIGH | new | content | `data/mandala-8.json, data/mandala-8.js +9` | Complete Rigveda, Mandala 8: 24 sūktas are empty and 28 more show the English and title of a different hymn |
| VED-02 | HIGH | new | content | `data/mandala-1.json, data/mandala-3.json +5` | Complete Rigveda Sanskrit is corrupted in all three scripts: viramas dropped, vocalic ṛ lost, IAST inherits the errors |
| VED-03 | HIGH | **regr** | navigation | `data/rigveda-template.html:391, data/rigveda-template.html:323 +3` | rigveda: switching mandala after scrolling lands on the wrong sūkta (the old load race, now on tab clicks) |
| VED-04 | HIGH | new | navigation | `fullbleed.html:738, fullbleed.html:770 +3` | fullbleed: every table-of-contents click lands on the wrong page, and the TOC cannot be used from the keyboard |
| VED-05 | MED | **regr** | a11y | `reader.html:2, reader.html:714 +9` | Pages are lang="bn" but the UI text and English titles in them are not marked as English |
| VED-06 | MED | new | a11y | `reader.html:669, reader.html:675 +6` | Invisible controls take keyboard focus: closed reader sidebar, hidden back-to-top scrubber, closed mobile sheets |
| VED-07 | MED | new | a11y | `reader.html:1085, reader.html:1096 +7` | Key and tap handlers override normal behaviour: Space won't press buttons, PageDown skips a whole sūkta, a tap on theater text jumps ahead |
| VED-08 | MED | new | a11y | `data/rigveda-template.html:191, data/rigveda-template.html:193 +5` | Missing accessible state and names: script toggles, menu/settings buttons, strip arrows, sūkta grid; no reduced-motion support |
| VED-09 | MED | **regr** | mobile | `data/rigveda-template.html:518, data/rigveda-template.html:520 +2` | rigveda phones: swiping the mandala tabs or sūkta strip turns the page instead of scrolling the row, so the far mandalas are still out of reach |
| VED-10 | MED | **regr** | mobile | `fullbleed.html:346, fullbleed.html:329 +4` | Touch targets below 40px: theme dots with no enlarged hit area, fullbleed arrows, pdf-reader select |
| VED-11 | MED | open | mobile | `data/rigveda-template.html:88, data/rigveda-template.html:77 +3` | rigveda sūkta pills and mandala tabs are still small on touch screens; the fix is phone-only |
| VED-12 | LOW | **regr** | build | `data/rigveda-template.html, data/mobile-template.html +7` | Public site serves broken template pages and about 48 MB of unlinked build output |
| VED-13 | LOW | new | content | `data/mandala-1.json, data/mandala-5.json +3` | Bengali meanings misaligned or OCR-garbled in some verses; small errors in the curated text |
| VED-14 | LOW | **regr** | docs | `CLAUDE.md:24, CLAUDE.md:33 +12` | Vedas docs have drifted from the code: sizes, settings, script-toggle claims, trees, stale inline template |
| VED-15 | LOW | new | mobile | `data/rigveda-template.html:104, data/rigveda-template.html:153 +1` | rigveda phones: the progress bar is covered by the sūkta strip |
| VED-16 | LOW | new | mobile | `fullbleed.html:85` | fullbleed phones: the book-spine line runs down the middle of every single-page view |
| VED-17 | LOW | new | navigation | `data/rigveda-template.html:523, data/rigveda-template.html:541 +2` | rigveda has no hashchange handler, so the URL and the content fall out of step (reader and fullbleed too) |
| VED-18 | LOW | new | navigation | `data/rigveda-template.html:224, data/rigveda-template.html:236 +2` | rigveda loading: two quick mandala switches in fallback mode load the wrong mandala; a failed load leaves a blank page |

### Site level, build & cross-cutting conventions (31: 0 high, 10 medium, 21 low)

| ID | Sev | Status | Area | Where | Finding |
|---|---|---|---|---|---|
| SIT-01 | MED | new | a11y | `index.html:16, index.html:68-71 +3` | Catalog dark theme: chip labels, author lines and meta text fail contrast (2.96:1) |
| SIT-02 | MED | new | a11y | `reader.html:2042, reader.html:567 +12` | JavaScript smooth scrolling ignores prefers-reduced-motion everywhere, and six pages still run page-flip or slide animations |
| SIT-03 | MED | new | a11y | `data/assemble-reader.py:121, reader.html +7` | Greek and transliterated Persian lack a valid lang attribute (Meditations, Odyssey study, Rubáiyát reader) |
| SIT-04 | MED | new | a11y | `reader.html:2062, pdf-reader.html:951 +4` | Esc does not close open panels in five pages: an error in Alice's reader, no handling in two PDF readers and Homer's mobile sheets |
| SIT-05 | MED | new | build | `data/fetch_persian.py:138-148, data/merge_annotations.py:20 +3` | Rubáiyát: regenerating the Persian seed permanently deletes all its notes, and the inputs to restore them are not in the repo |
| SIT-06 | MED | new | navigation | `reader.html, reader.html +7` | 39 of the 43 non-index reader pages have no link to their book's landing page or the catalog; the Meditations landing page also has no link back |
| SIT-07 | MED | new | navigation | `iliad/data/fullbleed-template.html:177, iliad/data/mobile-template.html:196 +12` | Homer readers save reading position in localStorage (book/page), which the house rules forbid |
| SIT-08 | MED | new | navigation | `fullbleed.html:1074, fullbleed.html:921 +6` | Position fixes were made in one book's copy of a shared template but not in the sibling copy (Alice fullbleed page turns; Prophet reader restore race and phone redirect) |
| SIT-09 | MED | new | perf | `odyssey/mobile.html, odyssey/illustrated.html +5` | Page weight: 20 pages over 1 MB, 31.7 MB of repeated payloads across formats, and the illustrated Odyssey pulls 6.9 MB of 2048px plates on first open on a phone |
| SIT-10 | MED | new | security | `odyssey/img/attic/, odyssey/img/characters/ +8` | About 557 MB (66%) of the published site is files no page uses; the site is at about 85% of GitHub Pages' 1 GB cap and on course to pass it |
| SIT-11 | LOW | **regr** | a11y | `index.html:72, index.html:80-85` | Catalog chips are still 36px on touch tablets; the size fix is gated on width, not pointer |
| SIT-12 | LOW | new | a11y | `index.html:116-207, index.html:100 +1` | Catalog link names repeat without book context, and the theme toggle announces contradictory state |
| SIT-13 | LOW | new | build | `data/collect_texts.py:413-417, data/collect_texts.py:234 +5` | Meditations: collect_texts.py silently drops all 412 Casaubon passages, and align_casaubon_long.py cannot run |
| SIT-14 | LOW | new | build | `odyssey/CLAUDE.md:51-52, odyssey/CLAUDE.md:370-374 +3` | Odyssey: the documented rebuild after editing modern.md leaves illustrated.html stale |
| SIT-15 | LOW | new | build | `generate_sentence_alignments.py:233-236, data/generate_sentence_align_04_06.py:194 +4` | Meditations: conflicting sentence-alignment scripts overwrite committed data and change reader.html's sentence links |
| SIT-16 | LOW | new | build | `scripts/merge_bengali.py:398-410, scripts/merge_bengali.py:334 +3` | Vedas: rerunning merge_bengali.py rewrites Bengali source labels and drops the 'llm' marking; the LLM step is not in the repo |
| SIT-17 | LOW | new | build | `odyssey/data/build_study_data.py:35-39, odyssey/CLAUDE.md:31 +2` | Homer: Odyssey study data depends on a Claude scratchpad path, and neither Homer book has a script to regenerate its seeds |
| SIT-18 | LOW | new | build | `CLAUDE.md:47-48, data/payload.py:1-11 +3` | Vedas: the curated hymn data is kept in three hand-maintained copies, though the docs say it is not duplicated |
| SIT-19 | LOW | new | build | `build_rigveda.py:570, build_rigveda.py:836-846 +1` | build_rigveda.py's built-in fallback template produces a broken page |
| SIT-20 | LOW | open | build | `gen_mobile.py:14, CLAUDE.md:98-113` | Alice: gen_mobile.py still fails out of the box; its only data source is its own output |
| SIT-21 | LOW | open | consistency | `fullbleed.html:969, index.html:858 +10` | Eleven settings keys still store a bare theme string instead of {book}-{format}-prefs JSON |
| SIT-22 | LOW | new | content | `index.html:109-110, index.html:119 +5` | Catalog labels and descriptions are inaccurate: 'Classic Book' has two meanings, the Rubáiyát credits only FitzGerald, and the intro overclaims |
| SIT-23 | LOW | new | docs | `AGENT_README.md:76-78, AGENT_README.md:33 +8` | AGENT_README says keeping templates in data/ keeps them off the site; data/ is equally public, so 24 broken template pages are live, 10 duplicate real pages' metadata, and 10 of their back-links 404 |
| SIT-24 | LOW | **regr** | docs | `.project/todo.md:15, .project/todo.md:18 +6` | Root .project/todo.md is still badly stale although the 2026-08-20 audit resolution says todos match the code |
| SIT-25 | LOW | **regr** | docs | `README.md:105-113, README.md:117-120 +7` | README and AGENT_README drift: Homer section, missing landing pages, 'no external fetches' and 'public domain' claims, and a tree and format docs not updated after P3 |
| SIT-26 | LOW | **regr** | docs | `AGENT_README.md:38-73, CLAUDE.md:7-9 +11` | Docs drift on what is generated and how to rebuild it (AGENT_README tree, Khayyam, Odyssey, Meditations, README) |
| SIT-27 | LOW | open | navigation | `index.html:170-181, odyssey/index.html:176-177` | Odyssey catalog card still omits Study and Illustrated |
| SIT-28 | LOW | new | navigation | `iliad/data/mobile-template.html, odyssey/data/mobile-template.html +8` | Keyboard shortcuts differ between formats and from AGENT_README (Homer mobile has none; several formats lack j/k, Page keys or Space) |
| SIT-29 | LOW | new | navigation | `fullbleed.html, fullbleed.html:928 +1` | #p-N means a printed page in some fullbleed readers and a spread number in Vedas, whose counter disagrees with its own page numbers |
| SIT-30 | LOW | new | seo | `index.html:6, reader.html:6 +6` | No 404.html, robots.txt, sitemap.xml, favicon, Open Graph/Twitter cards or canonical anywhere; meta description on 14 of 51 pages; inconsistent titles and branding |
| SIT-31 | LOW | open | theme | `web-reader.html, index.html:241 +2` | Theme-set outliers: Alice web-reader's own 4-theme set, a light/dark-only root catalog, and two pages that set the theme on <body> instead of <html> |

### Gap round (completeness critic) (33: 1 high, 17 medium, 15 low)

| ID | Sev | Status | Area | Where | Finding |
|---|---|---|---|---|---|
| GAP-01 | HIGH | new | content | `reader-casaubon.html:4774-4777, reader-casaubon.html:3849-3852 +4` | Casaubon reader: 156 of 412 passages (Books 6–12) show the modern English and notes of a different passage |
| GAP-02 | MED | new | a11y | `reader.html:393, reader.html:412 +15` | Forced colours (Windows High Contrast): theme swatches, every 'selected' state and all progress fills disappear |
| GAP-03 | MED | new | a11y | `fullbleed.html:59-68, fullbleed.html:483-489 +16` | Book-spread formats block text selection (user-select:none plus click zones over the text); double-clicking a word flips one or two pages |
| GAP-04 | MED | new | content | `aurelius-meditations.json:100, aurelius-meditations.json:348 +10` | Meditations (Leopold) notes and tooltips state wrong identities and relationships as fact: 1.4, 1.14, 8.25, 8.5/10.27, 11.3 |
| GAP-05 | MED | new | content | `index.html:580-581, index.html:691-692 +6` | Meditations landing page: Greek epigraphs that are not in the Meditations, an invented 'At Vindobona' book title, and a wrong source credit |
| GAP-06 | MED | new | content | `seeds/hymns.json:107-139, seeds/samaveda.json:22 +6` | Curated Vedas: 'Rigveda 3.62.18' is really RV 5.82.5, 3.62.11 is conflated with 1.2.7, and the Samaveda opener's verse 2 is not RV 6.16 |
| GAP-07 | MED | new | content | `index.html:436, index.html:440 +3` | Meditations landing page on phones never shows its left-hand pages (About this work, Annotation system, The Twelve Books) |
| GAP-08 | MED | new | layout | `fullbleed.html:523, fullbleed.html:539 +6` | Meditations and Vedas fullbleed silently drop text at 200% zoom and in phone landscape |
| GAP-09 | MED | new | layout | `index.html:63, index.html:104 +4` | Meditations landing page: fixed-height pages clip their text, and the reader links, at 200% zoom and in phone landscape |
| GAP-10 | MED | new | mobile | `index.html:75, index.html:80 +16` | 100vh-sized book boxes run under the iOS Safari toolbar and Android URL bar: Classic Book and fullbleed pages lose their bottom lines and page numbers |
| GAP-11 | MED | new | mobile | `mobile.html:5, mobile.html:69 +8` | viewport-fit=cover without left/right safe-area padding: in landscape the notch or Dynamic Island covers the first letters of reading lines on six mobile.html pages |
| GAP-12 | MED | new | mobile | `index.html:258, pdf-reader.html:145 +18` | Inputs and selects under 16px trigger iOS Safari's focus auto-zoom, which leaves locked pages zoomed in: the pdf-reader toolbars, the fullbleed page-number boxes, the Classic Book chapter menu and the study book menu |
| GAP-13 | MED | new | mobile | `data/mobile-template.html:25, data/theater-template.html:26 +19` | About 20 root-locked, swipe- or scroll-driven formats have no overscroll-behavior, so Chrome for Android pull-to-refresh reloads the book (the guard exists only on 5 older pages) |
| GAP-14 | MED | new | mobile | `data/theater-template.html:97, data/theater-template.html:102 +5` | Landscape phones get the desktop layout: Khayyam theater shows only 2 of the 4 lines of every quatrain (1 with the Android URL bar), and Alice single.html reads through a text window of about 140px |
| GAP-15 | MED | new | navigation | `reader.html:1992-2010, reader.html:2118 +4` | Reload, or Back/Forward without bfcache, sends the Alice, Meditations and Khayyam readers back to the start of the chapter, overriding the browser's exact scroll restore |
| GAP-16 | MED | new | navigation | `fullbleed.html:1544-1548, fullbleed.html:1525-1527 +4` | Alice fullbleed, Meditations fullbleed and Alice mobile do nothing until every font file settles: cover or 'Loading…' is inert, saved theme and #p-N not applied (3 new instances of the reported Prophet fullbleed root cause) |
| GAP-17 | MED | new | perf | `index.html:9, index.html:7 +19` | Every page stays blank and runs no script while fonts.googleapis.com hangs: the Google Fonts <link> blocks rendering and scripts on all 51 pages |
| GAP-18 | MED | new | print | `reader.html:234, reader.html:259 +12` | No print styling anywhere: scrolling readers lose about one line per printed sheet under the fixed top bar; 32 paged/app pages print only the current screen |
| GAP-19 | LOW | new | a11y | `reader.html, iliad/fullbleed.html +3` | Browser default font size is ignored by every reading surface; 33 pages offer no other way to enlarge text except zoom |
| GAP-20 | LOW | new | a11y | `fullbleed.html:1107, fullbleed.html:1119 +2` | Text spacing (WCAG 1.4.12): paginated formats paginate once, so spacing applied after load clips text; reported pagination bugs get 2–4x worse |
| GAP-21 | LOW | new | content | `reader-casaubon.html:688, reader-casaubon.html:693 +6` | Casaubon reader's own tooltips and notes: wrong identities, and they contradict the Leopold reader |
| GAP-22 | LOW | new | content | `aurelius-meditations.json:377, aurelius-meditations.json:235 +6` | Meditations (Leopold): contested or loose identifications stated as fact, and a swapped 10.31 paraphrase |
| GAP-23 | LOW | new | content | `data/annotations/leopold-books-04-06.json:119, data/annotations/leopold-books-10-12.json:250 +6` | Meditations tooltips: placeholder or wrong Wikipedia links, and a tooltip on a passage that doesn't mention the name |
| GAP-24 | LOW | new | content | `index.html:456, index.html:397 +12` | Rubáiyát edition facts: fifth edition 'months after' FitzGerald's death, Heron-Allen dated 1898, 'anonymous debut', and the Foroughi-Ghani date and calendar |
| GAP-25 | LOW | new | content | `seeds/persian.json:4180, seeds/persian.json:1612` | Rubáiyát Persian notes: one wrong FitzGerald match and a misattributed quotation |
| GAP-26 | LOW | new | content | `seeds/hymns.json:7, seeds/hymns.json:450-455 +1` | Vedas metadata and counts: wrong metre for 10.191, and two contradictory Rigveda totals |
| GAP-27 | LOW | new | content | `iliad/index.html:166` | Iliad landing: Pope's Book I quotation dated 1720 (Book I was published in 1715) |
| GAP-28 | LOW | new | layout | `rigveda.html:54, data/rigveda-template.html:54 +1` | rigveda settings panel doesn't scroll: the English and Bengali-translation toggles are cut off on short viewports (200% zoom) |
| GAP-29 | LOW | **regr** | mobile | `fullbleed.html:388, fullbleed.html:404 +3` | Fullbleed theme tray opens off-screen on the cover (Meditations ≤768px incl. 200% zoom; Prophet phones): previous footer fix incomplete |
| GAP-30 | LOW | new | navigation | `fullbleed.html, pdf-reader.html +8` | Most paged formats keep only the current page in the DOM, so Ctrl+F cannot search the book |
| GAP-31 | LOW | new | navigation | `fullbleed.html:1414, fullbleed.html:780 +5` | Six formats ignore same-document hash navigation (pasting a shared link into an open tab, or Back/Forward between such entries); the address bar then names a place that isn't shown |
| GAP-32 | LOW | new | navigation | `reader.html:1992-2010, reader.html:1862 +2` | Alice reader: while fonts are slow, the #ch-N restore freezes the URL position, then jumps the reader back to the linked chapter once fonts settle |
| GAP-33 | LOW | new | theme | `AGENT_README.md:125, AGENT_README.md:127 +6` | OS dark mode is ignored by every book page; nine pages also save the light default on first load |

### Refuted

| Source | Claim | Why it was dropped |
|---|---|---|
| gap-native-browser-features | Ctrl+F in Homer `fullbleed`/`pdf-reader` scrolls the hidden column strip off its page grid | The finder simulated find with `scrollIntoView()`, a programmatic scroll that does move `overflow:hidden` boxes. A verifier drove the real Chrome find bar in a visible browser with OS-level keystrokes (Ctrl+F, type, Enter): `scrollLeft` stayed 0, the counter and paging stayed aligned. Chrome's find scroll skips boxes the user cannot scroll. (The fact that find cannot *reveal* matches in these formats is GAP-30.) |

---

## Suggested fix order

**P0: readers are shown wrong or missing text** (content before chrome)
1. Meditations: re-key Long by passage, regenerate the JSON, and shift the Book 4–7 annotations (MED-01).
   Until then, correct the "484/486 aligned" claim.
2. Rigveda: remap Mandala 8 by Griffith numbering, restore the 24 empty sūktas (VED-01), and re-source the
   Sanskrit (VED-02). Correct the published verse counts in the meantime.
3. Odyssey study: key lines by the canonical `n`, and validate the milestones (HOM-01, HOM-02).
4. The measured paginator (§1) for Homer `fullbleed`/`pdf`, Alice `pdf`/`index`, Prophet `pdf`/`fullbleed`,
   and Rubáiyát `mobile` (a one-line `safe center` / `margin:auto` fix) and `fullbleed` (narrow the click
   zones).

**P1: dead ends and regressions**
5. The Meditations landing links (a one-line `z-index` fix, MED-02) and the Vedas `fullbleed` TOC
   (`stopPropagation`, VED-04).
6. Carry the Alice hash-restore fix into the Prophet and Rubáiyát readers, and fix the Rigveda tab race and
   the Alice `fullbleed` desktop hash (KHA-03, VED-03, and the "fix not carried over" rows).
7. Phone layouts for Homer's toolbars (HOM-03). Treat theater taps as reveal-only.

**P2: site**
8. Move `homer-odyssey/img/attic` and `img/characters` out of the Pages tree before the next illustrated
   book pushes the site over 1 GB. Consider a Pages workflow that publishes only reader files, which also
   fixes the public `data/` templates and `.claude/`, `.project/` and `*.py` exposure.
9. Add a way back from every reader to its book landing page. Link the Odyssey `study`/`illustrated` from
   the catalog. Add a favicon and a 404 page.

**P3: accessibility sweep**: the cross-cutting fixes above (key handlers, `inert`, reduced motion, pinch
zoom, `lang`, contrast, Homer theme dots and targets), done once across all books.

**P4: pipelines and docs**
- Build assertions in every content builder.
- Commit the Rubáiyát note inputs and the Odyssey study inputs, so both are rebuildable.
- Delete `build_rigveda.py`'s stale inline template.
- Reconcile every CLAUDE.md, AGENT_README and the root todo with the code, in the same commits as the fixes.

---

## Appendix A — convention matrix (all 51 live pages)

From the convention sweep, driven in Playwright, not only read from code.

- **P** (settings key): ✓ = `{book}-{format}-prefs` JSON; b = bare string; POS = stores the reading
  position; X3 = split into 3 keys
- **H** (URL-hash position): ✓ = written and restored; bk = book-level only; – = none; ! = defect
- **T** (themes offered): the number of themes; c = cycle button only
- **D** (theme dots): ✓ = `<button aria-label>`; s = `<span>`; t = button with title only; c = no dots
- **M** (reduced motion): ✓ = honoured; ✗ = animates; js = CSS rule present, but JS smooth scroll ignores it
- **L** (language markup), **K** (keys vs the docs), **E** (Esc closes panels)

| Book | Page | P | H | T | D | M | Notes |
|---|---|---|---|---|---|---|---|
| Alice | fullbleed | ✓ | ! (no hash on flips) | 5 | ✓ | ✗ | no j/k |
| Alice | index | ✓ | – | 5c | c | ✓ | ←→ only |
| Alice | mobile | ✓ | – | 5c | c | ✗ | no j/k |
| Alice | pdf-reader | ✓ | – | 5c | c | ✓ | Esc ✗ |
| Alice | reader | ✓ | ✓ | 5 | ✓ | ✗ | Esc throws `ReferenceError` |
| Alice | scroll / single | ✓ | – | 5c | c | ✗ | |
| Alice | theater | ✓ | ✓ | 5c | c | ✗ | |
| Alice | web-reader | ✓ | – | 4 (own set) | ✓ | ✗ | |
| Meditations | fullbleed | b | ✓ | 5 | ✓ | ✗ (flip) | |
| Meditations | index | b | – | 5 | ✓ | ✓ | Greek untagged |
| Meditations | mobile / pdf / theater | ✓ | ✓ `#m-B.N` | 5 | ✓ | ✓ | |
| Meditations | reader / casaubon | ✓ | ✓ | 5 | ✓ | js | Greek untagged (23.8k words) |
| Prophet | fullbleed | b | ✓ | 5 | ✓ | ✓ | |
| Prophet | illustrations / index | b | – | 5 | ✓ | ✗ | |
| Prophet | mobile | ✓ | ✓ | 5 | ✓ | ✓ | |
| Prophet | pdf-reader | b | ✓ | 5 | ✓ | — | Esc ✗ |
| Prophet | reader | ✓ | ! (race; phone redirect drops hash) | 5 | ✓ | ✗ | |
| Prophet | theater | b | ✓ | 5 | ✓ | ✗ | |
| Iliad + Odyssey | fullbleed | POS | bk | 5 | t | ✓ | ←→ Space only |
| Iliad + Odyssey | index | b | – | 5 | ✓ | ✓ | |
| Iliad + Odyssey | mobile | POS | ✓ (book) | 5 | t | ✓ | no keys; Esc ✗ |
| Iliad + Odyssey | pdf-reader | POS | bk | 5 | t | ✓ | no j/k/Page/Home/End |
| Iliad + Odyssey | reader | ✓ | ✓ (book) | 5 | s | js | ←→ jump whole books |
| Iliad + Odyssey | theater | X3 + POS | ✓ (book) | 5 | t | ✓ | |
| Odyssey | illustrated | POS (page) | ✓ | 5 | ✓ | ✓ | |
| Odyssey | study | ✓ | ✓ (book) | 5 | ✓ | ✗ | Greek untagged (2.5k words) |
| Rubáiyát | fullbleed / mobile / pdf / theater | ✓ | ✓ | 5 | ✓ | ✓ | |
| Rubáiyát | index | b | – | 5 | ✓ | ✗ | |
| Rubáiyát | reader | ✓ | ✓ (racy, KHA-03) | 5 | ✓ | ✗ | invalid `en-fa-Latn` |
| Vedas | fullbleed / mobile / pdf / theater | ✓ | ✓ | 5 | ✓ | ✓ | `lang="bn"` around English UI |
| Vedas | reader / rigveda | ✓ | ✓ | 5 | ✓ | ✗ | `lang="bn"` around English UI |
| Vedas | index | ✓ | – | 5 | ✓ | ✓ | |
| root | index | b (`lib-index-theme`) | – | 2 (light/dark) | — | ✓ | |

---

## Appendix B — how this audit was run

Each finder and verifier was an independent agent with read-only access. Every agent could drive Chromium
through Playwright (viewports 1440×900, 390×844, 320×640 with touch; CDP CPU and network throttling where
performance was in question) and rebuild pages in a scratch copy. Verifiers received the finding and were
told to refute it: *reproduce it yourself* for all findings, plus *read the code* for high and medium
findings, with a *user-impact* tiebreak on a split. A finding survived only with a majority of non-refuting
votes. Coverage was checked by a completeness critic reading every finder's list of checks. Its five gap
areas were then audited the same way. Duplicate reports of one root cause are merged; the JSON keeps every
source finder under `sources`.

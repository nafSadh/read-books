# UI/UX & Suite-Completeness Audit — 2026-08-20

**Scope**: all books except `homer-iliad/` and `homer-odyssey/` (excluded — in active development), plus the site-level catalog and docs.

**Method**: headless-Chromium smoke test of all 27 non-Homer pages (console/page errors, failed requests, overflow probes, 54 desktop+mobile screenshots) → one audit agent per book + one for site/docs, each combining code review, screenshot review, and live Playwright interaction checks → independent adversarial verification of every high/medium finding. **All 42 high/medium findings were confirmed; none refuted.**

**Totals**: 76 findings — 5 high, ~34 medium, ~37 low.

> **Status: resolved.** Every priority below (P0–P4) was implemented and
> browser-verified in the same session. See [Resolution](#resolution) at the end
> for what shipped, the bugs found *while* fixing, and what was deliberately
> left open.

---

## Executive summary

Five things are actually broken; the rest is convention drift, accessibility debt, and stale docs.

1. **`gibran-prophet/theater.html` is completely dead.** Its only `<script>` contains literal `\`` escaped backticks (lines 394, 401, 407 — a heredoc-generation artifact), so the whole script fails to parse: blank dark screen, no content, no controls, on all viewports. The root catalog links straight to it.
2. **`vedas/rigveda.html` deep links don't work.** An init race (bottom scroll-sentinel IntersectionObserver fires before the async first render) clobbers the sukta from `#M.S` hashes and from saved prefs — bookmarks like `#3.62` always land on sukta 1 of the mandala. Its headline "Hash routing" feature is effectively broken.
3. **`vedas/rigveda.html` mobile: Mandalas 1–2 and 9–10 are untappable.** The centered, non-scrollable tab row (527px wide) clips inside a 390px viewport with `scrollLeft` pinned at 0; the active tab sits at x=−137px off-screen.
4. **`khayyam-rubaiyat/reader.html` settings are unreachable on phones.** The fixed top bar overflows a 390px viewport (`scrollWidth` 440); the Settings (Aa) button sits entirely off-screen in every edition, so font/size/width can never be changed on mobile.
5. **`alice-in-wonderland/pdf-reader.html` mobile layout is broken by a CSS specificity bug.** The `@media (max-width:768px)` rules (`#zoomOut{display:none}`, 0-1-0… ) lose to the base `#toolbar button{display:flex}` (1-0-1), so nothing hides: the 547px toolbar overflows 390px, pushing the two-page/font/theme controls off-screen and overlapping the page counter.

One more near-high, confirmed but downgraded to medium because the main UI survives: **`aurelius-meditations/reader.html` throws a `SyntaxError` on every load** — `data/assemble-reader.py:509` injects `GREEK_JS` into *every* `</script>` (unbounded `str.replace`), so `const greekBtn` is declared twice and the second script block — the proper-noun keyboard-accessibility patch — never executes. Fix is one character: `replace(..., 1)`, then rebuild.

**Suite completeness** (the "full suites" question): the reference suite is index + reader + fullbleed + mobile + theater + pdf-reader.

| Book | Formats on disk | Missing vs full suite | Notes |
|---|---|---|---|
| alice-in-wonderland | 9 | — | 2 maintained + 7 drifting legacy variants; consolidation already pondered in todo |
| aurelius-meditations | 4 (index, reader, reader-casaubon, fullbleed) | mobile, theater, pdf-reader | root todo still says "2 formats" |
| gibran-prophet | 7 (full suite + illustrations) | — | theater is dead (above); docs still describe 2 files |
| khayyam-rubaiyat | **2** (index, reader) | fullbleed, mobile, theater, pdf-reader | **thinnest suite**; CLAUDE.md promises fullbleed + theater that don't exist; no `.project/` |
| vedas | 3 (reader, fullbleed, rigveda) | **index**, mobile, theater, pdf-reader | only book with no landing page; `.project/` has no todo/changelog |

---

## Cross-cutting patterns

These recur in nearly every book — worth fixing as sweeps rather than one-offs:

- **Reading position**: house rule is URL hash (`#ch-N` / `#p-N`), never localStorage. Compliant: alice reader/fullbleed (todo stale — already implemented), prophet reader/fullbleed, khayyam reader (variant form). Violations: prophet theater + mobile store position in localStorage; prophet pdf-reader, all 4 meditations files, vedas reader/fullbleed persist no position at all; vedas rigveda stores position in prefs *and* has the broken hash restore.
- **Theme dots as non-focusable `<span>`s**: same pattern in alice fullbleed, meditations (all files), prophet fullbleed/reader/illustrations/theater, khayyam reader, vedas fullbleed. `khayyam-rubaiyat/index.html:370` has the correct `<button aria-label>` implementation to copy.
- **Zero aria files**: alice fullbleed/index/pdf/scroll/single/theater, meditations fullbleed/index, prophet fullbleed/theater/pdf/illustrations, vedas fullbleed — icon-only buttons with `title` at best.
- **Touch targets < 44px**: meditations' 486 detail buttons (24px), vedas sukta pills (22px) and mandala tabs (26px), prophet theater dots (10px on mobile), root-catalog reader chips (~23px).
- **5-theme system drift**: sepia missing from alice reader/fullbleed (tracked) and vedas rigveda (untracked, CLAUDE.md claims 5); alice mobile has 2 themes, alice legacy pages generic light/dark, alice pdf-reader none; alice `reader.html:2` even sets `data-theme="sepia"` — a theme the file doesn't define.
- **localStorage key drift** from `{book}-{format}-prefs`: `fullbleed-theme` (alice — unprefixed, collides across books on the shared origin), `webreader-prefs`, `vedas-fb-theme`, `rv-prefs`, `prophet-theater-chapter` (position!), plus theme-only keys where prefs objects are expected. AGENT_README also never specifies keys for index/mobile/theater/pdf formats — exactly where the drift happened.
- **Docs staleness**: every audited book's CLAUDE.md misdescribes its own suite (details per book below); README.md documents only 3 of 7 books; root todo's Books table is wrong on 4+ rows; alice/root todos still track hash-state work that shipped.

---

## Per-book findings

Severity after adversarial verification. `[tracked]` = already an open item in a `.project/todo.md`.

### gibran-prophet (10 findings: 1 high, 5 medium, 4 low)

| Sev | Area | Where | Finding |
|---|---|---|---|
| HIGH | content | theater.html:394,401,407 | Escaped backticks (`\``) → SyntaxError → **page fully dead** (blank screen both viewports); root catalog links to it |
| MED | navigation | theater.html:422 | Chapter position kept in localStorage (`prophet-theater-chapter`), reads bare `#N` hash but never writes one |
| MED | navigation | mobile.html:528 | Position (`chIdx`) stored in prefs; no hash read/write at all — deep links impossible |
| MED | navigation | pdf-reader.html:861 | No position persistence of any kind; refresh always returns to page 1 of 113 |
| MED | a11y | fullbleed:609, reader:476, illustrations:270, theater:358 | Theme dots non-focusable spans; fullbleed/theater/pdf/illustrations have 0 aria attributes (mobile.html is best-in-suite: focus trap, aria-modal — copy it) |
| MED | content | illustrations.html:307-367 | All 30 images hotlinked from wikimedia/kahlilgibran.com — no local copies; page degrades to empty boxes if hosts block/move (plates are public domain; vendor them into `assets/`) |
| LOW | docs | CLAUDE.md:26-66 | File inventory documents 2 readers; book ships 7 (5 storage keys undocumented) |
| LOW | docs | .project/todo.md:15, changelog | "Consider mobile/theater" still open though both exist; changelog ends at Session 1 — broken theater shipped with no trail |
| LOW | mobile | theater.html:339 | Theme dots 10×10px touch targets on mobile |
| LOW | consistency | fullbleed:1473, mobile:579 | j/k keyboard bindings missing (reader + pdf have them) |

### vedas (14 findings: 2 high, 6 medium, 6 low)

| Sev | Area | Where | Finding |
|---|---|---|---|
| HIGH | navigation | rigveda-template.html:304-359 | Deep-link/bookmark restore broken: bottom-sentinel observer fires before async first render, overwrites `sIdx=0` and `replaceState('#M.1')` — `#3.62` always lands on sukta 1 (verified via live trace; also clobbers saved prefs position) |
| HIGH | mobile | rigveda-template.html:66 | `#mandala-row` centered flex, no `overflow-x:auto` → tabs clipped both sides; Mandalas 1-2/9-10 untappable, active tab at x=−137px; sukta grid opens only from the (off-screen) active tab |
| MED | a11y | all 3 readers, line 2 | Everything is `lang="bn"` with no per-element overrides — Devanagari, IAST, and English all announced as Bengali; wrong font/hyphenation selection (`sa-Deva`/`sa-Latn`/`sa-Beng`/`en`/`bn` needed in the 3 render functions) |
| MED | navigation | fullbleed.html | No hash state and no position persistence at all (~98 spreads, always restarts at cover) — untracked |
| MED | navigation | reader.html | No URL hash position `[tracked]` |
| MED | theme | rigveda-template.html:229 | Only 4 themes (no sepia); CLAUDE.md:31 claims 5; same book's other readers have 5 with sepia default |
| MED | consistency | vedas/ | **No index.html** — only book without a landing page |
| MED | mobile | rigveda-template.html:67,78 | Sukta pills 22px / mandala tabs 26px touch targets (191 pills in Mandala 8) |
| LOW | consistency | fullbleed:773, rigveda:493 | Keys `vedas-fb-theme`, `rv-prefs` off-convention; rv-prefs stores position (m,s) |
| LOW | theme | reader:2, fullbleed:2 vs rigveda:2 | Defaults disagree (sepia vs light-purple); CLAUDE.md:75 says light-purple |
| LOW | a11y | fullbleed.html:441,779 | Theme dots title-only; chapter scrubber is click-only spans; 0 aria |
| LOW | layout | fullbleed.html:558-810 | Crossing the 768px breakpoint (rotation) remaps spread math without converting `currentSpread` — silently changes the page being read |
| LOW | docs | CLAUDE.md:31,75; root todo:30,47,55,73 | Stale: 5-theme claim; "49/10,143 Bengali" (now 100%); samhita size 3.8→11.6 MB; ".project/ missing" (exists, but has no todo/changelog) |
| LOW | content | vedas/rigveda-template.html | Raw template deployed at book root (throws `__META_JSON__` ReferenceError, blank page); every other book keeps templates under `data/` |

### khayyam-rubaiyat (12 findings: 1 high, 2 medium, 9 low)

The reader is actually 5 editions (FG 1st/5th, Whinfield, Nicolas, Persian) with per-quatrain scholarship — the best content depth per file in the library — but the thinnest suite and the stalest CLAUDE.md.

| Sev | Area | Where | Finding |
|---|---|---|---|
| HIGH | mobile | data/reader-template.html:192-199,414-421 | Top bar overflows phone width (scrollWidth 440 vs 390); **Settings (Aa) button entirely off-screen** — font/size/width unreachable on phones in every edition |
| MED | layout | data/reader-template.html:659-683 | At 1100–1439px with Details+Persian both on: 2-column grid orphans the Persian aside ~1000px below its verse; poem column (331px) narrower than its annotation (687px); proper 3-column template exists only ≥1440px |
| MED | a11y | data/reader-template.html:788,1030 | Theme dots non-focusable spans (index.html:370 has the correct button pattern); progress segments click-only divs |
| LOW | navigation | data/reader-template.html:1069,1184 | `#chg-<edition>-N` hash never script-restored (relies on native fragment scroll) and goes stale across edition switches — silently lost |
| LOW | a11y | data/reader-template.html:752 | `role=tablist/tab` without roving tabindex or arrow-key handling |
| LOW | theme | data/reader-template.html:860-874 | On touch, tapping the theme button cycles *and* opens the palette at once |
| LOW | consistency | data/reader-template.html:638 vs 697 | Side-column transliteration still left-aligned under RTL Persian — same mismatch commit ccd986d fixed in the spine |
| LOW | layout | index.html:258,417-447 | Edition cards use `flex-basis:100%` inside a grid (no effect) — cramped 2-up with empty 5th cell; `.solo` class defined but never applied |
| LOW | consistency | index.html:418-439 | Chips reference undefined `var(--font-mono)` → fall back to Jost instead of IBM Plex Mono |
| LOW | docs | CLAUDE.md:29-30,75 | **Promises fullbleed.html + theater.html that don't exist** (and a prefs key for the missing file); no `.project/` todo tracks building them |
| LOW | docs | CLAUDE.md:11-83 | Documents a 2-edition reader and a pipeline (`build_quatrains.py`, `seeds/quatrains.json`) that never materialized; real pipeline (`build_reader.py` + 5 seed files) undocumented |
| LOW | performance | data/build_reader.py:386 | All 5 editions `display:none` until end-of-body script runs — blank page while 1.9 MB parses; bake `visible` onto the default edition |

### aurelius-meditations (11 findings: 4 medium, 7 low)

| Sev | Area | Where | Finding |
|---|---|---|---|
| MED | a11y | data/assemble-reader.py:509 | `GREEK_JS` injected into **every** `</script>` → duplicate `const greekBtn` → SyntaxError on every reader.html load; the a11y script block (tabindex backfill, Esc-to-blur) never runs. Fix: `replace(..., 1)` + rebuild |
| MED | a11y | fullbleed.html:415-441 | 0 aria attributes; icon-only nav/theme buttons title-only; dots unreachable by keyboard (vs 417 aria attrs in the scrolling readers) |
| MED | navigation | all 4 files | No URL hash position anywhere — biggest usability gap for 486 passages `[tracked]` |
| MED | mobile | reader-casaubon.html:374 (+ generated reader) | The 486 annotation detail buttons stay 24×24px on touch; media query enlarges only top-bar buttons |
| LOW | content | index.html:596-608 | Landing page never links reader-casaubon.html; credits only Casaubon though flagship reader now serves George Long |
| LOW | consistency | fullbleed.html:904 | Key `meditations-fullbleed-theme`, theme-only (documented deviation, but inconsistent) |
| LOW | navigation | fullbleed:1010, index:835 | Arrow/Space only — no j/k, no Esc |
| LOW | a11y | assemble-reader.py:117,326 | Greek `.gw` transliteration tooltips hover-only — no keyboard/touch path |
| LOW | docs | root todo:15,45 | "2 formats" — actually 4 files |
| LOW | docs | book todo:21,31 | Greek integration listed pending but shipped; cites `data/texts/book-NN.json` files that don't exist |
| LOW | docs | CLAUDE.md:30-31,53 | Layout percentages don't match implementation (both-open is 2-col with Greek stacked, not 3-col); promises `justify` that no rule implements |

### alice-in-wonderland (17 findings: 1 high, 12 medium, 4 low)

Two-tier suite: reader.html + fullbleed.html are healthy (and already have hash state — the todos are stale); the 7 legacy variants drift on every convention.

| Sev | Area | Where | Finding |
|---|---|---|---|
| HIGH | mobile | pdf-reader.html:69 vs 400 | Mobile media-query hiding rules lose specificity to base `#toolbar button` rule — **mobile layout never compacts**: 547px toolbar in 390px viewport, two-page/font/theme controls unreachable, page-count overlaps input |
| MED | theme | pdf-reader.html:791 | No data-theme system (body.dark only), zero persistence — theme/font/zoom reset every load |
| MED | consistency | fullbleed.html:1301 | Unprefixed key `fullbleed-theme` (only unprefixed fullbleed key in the repo; shared-origin collision risk) |
| MED | a11y | fullbleed.html:432,564 | 0 aria; theme dots hover-only spans, no touchstart fallback (reader.html has the pattern) |
| MED | navigation | theater.html:135 | Strictly linear: 814 next-taps to finish, progress bar not clickable, no TOC/hash/persistence — practically unusable |
| MED | mobile | single.html:91 | No @media at all; fixed footer overflows 390px — Prev/Next clipped to "REV"/"NEX" |
| MED | navigation | scroll.html:40 | Zero keyboard handlers (only variant with none); chapter nav scrollbar hidden → chapters 8-12 undiscoverable on mobile |
| MED | consistency | web-reader.html:516 | Near-duplicate of reader.html with off-spec theme names (light/sepia/dark/black) on `<body>`, key `webreader-prefs` — prime merge candidate `[tracked-ish]` |
| MED | theme | mobile.html:14 | 2 of 5 themes, zero persistence, only EB Garamond loaded |
| MED | theme | index/scroll/single/theater | Generic light/dark only, none persisted |
| MED | theme | reader:34, fullbleed:17 | Sepia missing from primary readers `[tracked]` |
| MED | docs | CLAUDE.md:22 | Calls index.html "Landing — links to all formats"; it's a book reader with zero links — the book genuinely lacks a landing page |
| MED | a11y | scroll:114, single:124, pdf toolbar | 5 legacy variants have zero aria on icon-only controls |
| LOW | consistency | reader.html:2 | `<html data-theme="sepia">` references a theme the file doesn't define (body carries the real one) |
| LOW | mobile | index.html:207 | Fixed controls bar overflows 390px by ~6px, clipping theme toggle |
| LOW | docs | .project/todo.md + root:64 | Hash-state items still pending though **implemented** in both primary readers — will misdirect future sessions |
| LOW | docs | gen_mobile.py:14 | mobile.html generated from `/tmp/alice_chapters.json` which no longer exists — variant can't be regenerated; generator undocumented |

### Site level — catalog + docs (12 findings: 7 medium, 5 low)

| Sev | Area | Where | Finding |
|---|---|---|---|
| MED | theme | index.html:2,193 | Theme toggle: no localStorage, no `prefers-color-scheme` — dark-mode users flashed light every visit; every *book* index persists its theme |
| MED | a11y | index.html:86 | Theme button has no accessible name (glyph-only) |
| MED | a11y | index.html:64-71 | Reader chips — the site's primary nav — 10px uppercase mono, ~23px tap targets, no media query |
| MED | docs | README.md:7-37 | Books section omits 4 of 7 books (Meditations, Prophet, Rubáiyát, Vedas) |
| MED | docs | .project/todo.md:5-51 | Books table wrong on 4+ rows; structure tree omits khayyam + both Homers; ".project/ (empty)" states that can't exist in git |
| MED | consistency | AGENT_README.md:99-102 | Prefs-key convention violated by 7 keys (enumerated above); position-in-localStorage violation in prophet theater; convention never defined for index/mobile/theater/pdf formats |
| MED | consistency | AGENT_README.md:83-89 | 5-theme claim violated by the whole Alice suite + rigveda (inventory in finding) |
| LOW | theme | index.html:41 | Invalid CSS `background:var(--accent)08` — hover tint never renders (only occurrence of the pattern repo-wide) |
| LOW | a11y | index.html:176-179 | Bengali text on Vedas card lacks `lang="bn"` inside `lang="en"` doc |
| LOW | docs | AGENT_README.md:19-49,131 | Tree omits 3 books; seeds/ requirement unmet by alice + aurelius |
| LOW | consistency | repo root | `align_sentences_final.py` (a Meditations build script) at repo root; vedas template deployed at book root |
| LOW | navigation | index.html:156 | *Homer, informational only*: Odyssey card links 6 of 8 formats (illustrated.html + study.html unlinked); README "5 variants" stale — defer until Homer stabilizes |

*All root-catalog links verified: all 37 resolve to files on disk; no non-Homer page is unlinked (except the stray vedas template).*

---

## Suggested fix order

**P0 — broken functionality (5 files):**
1. `gibran-prophet/theater.html` — replace 4 `\`` with backticks (page revives; interpolations already correct)
2. `aurelius-meditations/data/assemble-reader.py:509` — `replace('</script>', GREEK_JS + '</script>', 1)` + rebuild reader.html
3. `vedas/rigveda-template.html` — defer bottom-sentinel observe until first render completes; guard `appendNextSukta` while mandala unloaded; rebuild
4. `vedas/rigveda-template.html` — `#mandala-row{overflow-x:auto; justify-content:flex-start}` on narrow widths + scroll active tab into view; rebuild
5. `khayyam-rubaiyat/data/reader-template.html` — compact the top bar ≤480px (shrink buttons / move toggles into settings panel); rebuild
6. `alice-in-wonderland/pdf-reader.html` — scope mobile hiding rules to out-rank `#toolbar button`

**P1 — convention sweeps** (hash-position everywhere, position out of localStorage, prefs-key renames with legacy migration, sepia/5-theme parity, root-catalog theme persistence + `prefers-color-scheme`).

**P2 — a11y sweep** (theme dots → buttons with aria-label via the khayyam-index pattern; aria-labels on all icon buttons; 44px touch targets; `lang` attributes in vedas readers + root catalog; tablist keyboard semantics or role removal).

**P3 — suite completeness** (khayyam fullbleed + theater — the Rubáiyát is the ideal one-quatrain-per-page theater text; vedas index.html; meditations mobile/theater/pdf decision; alice legacy consolidation decision).

**P4 — docs/housekeeping** (rewrite khayyam CLAUDE.md; update prophet/alice/meditations/vedas CLAUDE.md + todos; README 4 missing books; AGENT_README tree + key conventions for all 6 formats; move vedas template into data/; relocate align_sentences_final.py; fix gen_mobile.py source or commit seeds).

---

*Method notes: smoke artifacts (screenshots, console logs) were session-local and are not committed. The ~15s page load times in smoke data are the sandbox's Google-Fonts timeout, not a site defect. `vedas/rigveda.html`'s file:// fetch error is benign — its script-tag fallback works.*

---

## Resolution

All five priorities were implemented and verified in headless Chromium the same
day. 18 commits, 55 files, ~+7.9k/−0.6k lines.

### P0 — the six broken readers

| File | Root cause | Fix |
|---|---|---|
| `gibran-prophet/theater.html` | Literal `\`` escaped backticks (a heredoc-generation leak) made the page's only script a `SyntaxError` | Unescaped; page renders chapters again. Position also moved from localStorage into `#ch-N` |
| `aurelius-meditations/reader.html` | `assemble-reader.py:509` injected `GREEK_JS` into *every* `</script>`, re-declaring `const greekBtn` and killing the second block | `replace(..., 1)`; rebuilt |
| `vedas/rigveda.html` | The bottom scroll sentinel was observed at parse time and fired before the async first render, clobbering the restored sukta | Observe after first render + guard `appendNextSukta`. `#3.62` → M3, `#10.129` → "Creation" ✓ |
| `vedas/rigveda.html` (mobile) | `justify-content:center` on a non-scrollable row put Mandalas 1–2/9–10 outside the scrollable area | `safe center` + `overflow-x`, active tab auto-scrolled into view |
| `khayyam-rubaiyat/reader.html` (mobile) | Fixed top bar overflowed 390px, putting Settings entirely off-screen | Compact bar ≤480px, scrollable edition switcher |
| `alice-in-wonderland/pdf-reader.html` (mobile) | `@media` hide rules (1,0,0) lost specificity to `#toolbar button` (1,0,1) | Scoped under `#toolbar`; fits 390/390 |

### P1–P2 — conventions and accessibility

Reading position now lives in the URL hash in every reader (Meditations had none
at all across 486 passages; Prophet's mobile/theater kept it in localStorage);
prefs keys migrated to `{book}-{format}-prefs` with legacy-key fallbacks so
returning readers keep their settings; sepia added where missing for 5-theme
parity; theme dots are real `<button aria-label>` controls with ≥40px hit areas
across every book; aria-labels added to previously unlabelled icon-only controls;
`lang` attributes (`sa-Deva`/`sa-Latn`/`sa-Beng`/`bn`/`en`) applied in the
multilingual Vedas readers, which had announced everything as Bengali.

### P3 — suite completeness

- **Rubáiyát** gained `fullbleed.html` and `theater.html`, promised in its
  CLAUDE.md but never built. `build_reader.py` became the shared library for all
  three builders; `reader.html` rebuilds byte-identical, proving the refactor
  inert.
- **Vedas** gained `index.html` — it was the only book without a landing page.

Formats per book now: Alice 9, Prophet 7, Meditations 4, Rubáiyát 4, Vedas 4.

### P4 — docs

README gained the four books it never documented; AGENT_README's conventions
were rewritten where the drift originated (prefs keys defined for every format
with a no-position rule and migration note, hash-state guidance covering async
init races, a new accessibility baseline, a tree covering all seven books); every
book's CLAUDE.md and todo now matches its code.

### Bugs found *while* fixing

Not in the original audit — surfaced by the fix and verification agents:

1. **`vedas/reader.html` navigation landed in the wrong place.** `.veda-section`
   is `position:relative`, so `offsetTop` was section-relative and every sūkta
   past the first Veda scrolled to roughly its section top. Fixed at all four
   call sites via a shared `suktaTop()` helper.
2. **`alice/reader.html` hash restore was racy** — ~2 in 8 loads landed on
   chapter 1, because the observer rewrote the hash during the fonts-ready
   deferral and `parseHash()` then read the mutated value. Target is now captured
   up front and observer writes are suppressed until the restore lands. 8/8.
3. **`aurelius-meditations/fullbleed.html` page→spread was off by one** for even
   pages — the formula was not the inverse of `contentIndexForSpreadLeft/Right`.
   All 237 pages now round-trip.
4. **Spread-reader footers overflowed phones.** In Prophet's fullbleed, 27 footer
   elements rendered outside a 390px viewport — a *centred* flex row cannot be
   scrolled back, so the book could not be paged or re-themed at all on a phone.
   Sweeping all seven spread/landing pages found the same class of bug in Vedas
   (which also rendered into a 195px column of a 390px screen) and Alice. All
   seven now fit exactly, nothing off-screen.
5. **Three regressions introduced by the fixes themselves**, each caught by an
   independent verifier rather than by review:
   - A square 40×40 `::before` hit area on 14px theme dots covered its
     neighbours, so 4 of 5 dots applied the *wrong* theme. The expander now grows
     only vertically.
   - The stale-hash guard added to Khayyam's `applyEdition` fired on the
     *incoming* deep link during init, silently destroying any
     `#q-<edition>-N` link into a non-default edition.
   - Making Greek word tooltips focusable put **29,190** tab stops in the
     Meditations reader, burying every real control behind the text.

### Deliberately left open

- **`#p-N` in spread readers is viewport-dependent.** Pagination depends on
  window size, so a shared `#p-100` can land on a different passage on a
  different screen. Fixing it properly means anchoring the hash to a chapter or
  passage id rather than a page ordinal — a format-wide redesign, not a patch.
- **`gibran-prophet/illustrations.html` still hotlinks its 29 plates.** This
  session had no network access to vendor them. The page now reserves
  aspect-ratio boxes, carries descriptive alt text, and falls back to the plate's
  caption when a host is unreachable, so it degrades gracefully.
- **Homer** (`homer-iliad/`, `homer-odyssey/`) was excluded throughout as active
  development, including the catalog gap where the Odyssey's `illustrated.html`
  and `study.html` are not linked.
- **Alice's legacy variants** (`scroll`, `single`, `web-reader`, `index`,
  `theater`) were fixed but not consolidated — that call is the maintainer's.

### Final verification

A full smoke pass over the finished state — every non-Homer page at 1440×900 and
390×844, 58 screenshots:

| | Before | After |
|---|---|---|
| Pages with JS page errors | 3 | **0** |
| Pages with horizontal overflow | — | **0** |
| Pages reachable but broken | 1 (raw template at book root) | **0** |

The single remaining console line is `vedas/rigveda.html`'s `file://` fetch
falling back to its `<script>` loader, which then succeeds and renders the sukta
— benign, and by design so the reader works offline.

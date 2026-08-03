# Odyssey Illustrated Edition — Image Generation Prompts

For `illustrated.html`. **The canonical style is the full-colour watercolour
square set** (see STYLE BLOCK — WATERCOLOUR below). Save results as
`img/bk<NN>/<slug>.jpeg` — 1:1 square, and **save as real JPEG with a
`.jpeg` extension** (the Book I batch arrived as `.png` files that were
actually JPEGs, which breaks content-type on a server).

## How to use

Every scene prompt = **STYLE BLOCK + CHARACTER REF(s) + scene prompt**, and
— where the model supports image input — **attach the character reference
sheet images** for whoever appears. Never vary the style block. If a
generation drifts off-style or off-character, regenerate rather than accept.

---

## STYLE BLOCK — WATERCOLOUR (canonical; prepend to every prompt, verbatim)

> Illustration for a serious literary edition of an ancient epic, for adult
> readers — in the tradition of Charles Keeping, Barry Moser and Alan Lee.
> Clean confident dark ink linework over flat, soft watercolour washes on
> lightly textured paper. Full colour in a restrained Aegean palette — pale
> blue-grey, cream and sun-bleached limestone, olive and moss green, muted
> teal — with warm terracotta-red reserved as a sparing accent (a jar, a
> column band, a sash, a sail, fire, blood). Clear Mediterranean daylight
> where the scene allows it, hard shadow and near-monochrome where it does
> not. Minimal rendering, no gradients, no glow, no photorealism, no anime,
> no 3D, no cuteness, nothing sentimental or twee. Grave, unhurried, adult:
> restraint and stillness rather than spectacle, but never sanitised — this
> poem contains grief, captivity, humiliation and killing, and the pictures
> should be able to hold them. Archaic/Mycenaean Greek material culture:
> long ships with a single square sail, bronze tripods, geometric-pattern
> hems, crested and boar-tusk helmets, megaron halls with a central hearth
> and red-banded columns, wooden benches, clay amphorae. Figures at a
> composed middle distance — full or three-quarter figures, faces readable
> but rarely close-up. No text, no speech balloons, no panel borders, no
> watermark. Square 1:1 composition.

---

## REGISTER, AND THE DIFFICULT SCENES

The Odyssey is not a children's book. It contains Calypso holding Odysseus
as a captive concubine for seven years (5.154–155 says plainly that he lay
with her *unwilling beside the willing*), Ares and Aphrodite caught naked in
Hephaestus's net while the gods crowd the doorway laughing, an eye bored out
with a burning stake, a hall of 108 suitors killed and its floor running
with blood, twelve enslaved women hanged in a row, and Melanthius mutilated.
An edition that draws these as charming vignettes is worse than one that
doesn't draw them at all.

The method is **restraint through composition, not omission**: choose the
moment *beside* the act. Homer himself does this constantly — he reaches for
a simile at the worst moments (the suitors like netted fish on the sand, the
maids like doves caught in a snare, Odysseus spattered like a lion come from
feeding). Use his displacement.

Practical rules for the hard plates:

- **Aftermath over act.** The stake and the recoil and the firelight, not
  the eye. The emptied hall at dawn, not the killing. Ropes and an
  overturned bench, not twelve hanging bodies.
- **Silhouette, backlight, turned faces, off-frame.** Violence read at a
  distance or as shadow on a wall keeps its weight without becoming gore.
- **Reaction as subject.** Telemachus's face; the herald hiding; the old
  nurse in a doorway. Grief is more legible than injury.
- **Render the simile literally** where the act itself can't be shown — the
  fish on the sand, the doves, the lion. This is faithful, not evasive.
- **Calypso is captivity, not romance.** Paradise rendered as enclosure:
  the beautiful island framed like a cell, his back to it, the horizon
  empty. Never a love scene.
- **Sexual content stays off-frame or comic.** The Ares/Aphrodite episode is
  played by Homer as scandalous farce — the net, the crowd of gods in the
  doorway, the laughter — so draw the audience, not the bed.
- **Do not soften the poem.** The author's direction is explicit: do not be
  hesitant about plates that are sexual, violent or bloody. Calypso's
  captivity, the blinding, the killing of a hundred and eight men, the
  hanging of the maids and the mutilation of Melanthius all belong in the
  book, drawn with their real weight. An edition that flinches is worse
  than one that omits.
- **The composition rules above are craft, not modesty.** Aftermath,
  silhouette, reaction and simile are what make a violent image land instead
  of merely showing meat — Homer uses exactly these devices at exactly these
  moments. Use them because they are stronger, not because the material
  needs covering. Where a direct image is stronger, draw the direct image.
- **The binding constraint is the generator, not the register.** Gemini and
  every comparable model will refuse nudity, sexual content and graphic
  gore outright, no matter how the prompt is framed. So the practical
  ceiling is: blood yes, bodies yes, the dead yes, dread and cruelty yes;
  bare bodies and open wounds will simply not render. Write to that ceiling
  deliberately rather than pretending it is an artistic choice.

Expect some prompts to be refused or softened by the image model regardless.
When that happens, fall back to the non-figurative version of the beat — an
object, a room, a landscape carrying the aftermath. Those often turn out to
be the strongest plates in the book anyway.

---

## CHARACTER REFERENCE SHEETS — how to generate

Generate ONE sheet per character **before** any scene work; save to
`img/characters/<slug>.jpeg` (real JPEG, correct extension) using the exact
slug in bold below. Then attach the sheet as an image reference in every
scene prompt that character appears in.

`python3 data/label_character_sheets.py` writes a captioned copy of every
sheet to `img/characters/labeled/` — name, role and reserved signature in a
band below the art. That set is a **contact sheet for the human**, for
telling files apart at a glance. **Attach the clean sheet, not the labelled
one, when prompting**: burnt-in lettering in a reference image tends to leak
lettering into the generated scene. Add each new character to `CHARACTERS`
in that script when you add its paragraph here.

**Four failure modes seen in the first batch — reject and regenerate:**

1. **Prompt text rendered into the image.** Three of twelve sheets came back
   with the preamble or character paragraph set as a caption block, one of
   them eating 40% of the canvas, all with OCR-style typos (`half-smi`,
   `gy-blue`, `terract`). The preamble already says "no text, no labels";
   if the model does it anyway, regenerate rather than crop.
2. **Scenery smuggled in.** One sheet spent half its canvas on two full
   scene panels. The sheet must be figures on flat cream, nothing else.
3. **A reserved colour leaking onto the wrong character.** Terracotta-red
   appeared as a belt or sash on three sheets. Red belongs to Antinous
   alone — a red sash on Odysseus destroys the one cue that makes Antinous
   findable in a crowd of twenty.
4. **The four views disagreeing.** One sheet drew the same man in a pale
   blue tunic front-on and a green tunic in profile. Check the views against
   each other before saving, not just against the prompt.

Each sheet renders the character **four times in one image** (2×2: full
front, full profile, bust front, bust three-quarter). One multi-view image
beats four separate generations: within a single image the model draws one
person consistently; across separate runs it draws four cousins.

**Each sheet prompt is complete**: paste the PREAMBLE, then ONE character
paragraph after "THE CHARACTER:". Never combine characters. If a result
drifts off-style (glossy, cute, anime, photoreal) or the four views show
different people, regenerate — a bad sheet poisons every scene after it.

### PREAMBLE (fixed; paste first, verbatim)

> A character model sheet for an illustrated literary edition of Homer's
> Odyssey, in the tradition of Alan Lee and Barry Moser. Clean, confident
> dark ink linework over flat, soft watercolour washes on lightly textured
> paper. Restrained Aegean palette — pale blue-grey, cream, sun-bleached
> limestone, olive and moss green, muted teal — with terracotta-red
> appearing only if the costume below names it. Even soft daylight, minimal
> shading, no gradients, no glow, no photorealism, no anime, no 3D, nothing
> cute or sentimental: serious, dignified, adult.
>
> One single character drawn four times on a plain flat cream background,
> arranged two-by-two with even spacing: top left, full figure, front view,
> standing relaxed, arms at sides; top right, full figure, side profile
> view, standing; bottom left, head-and-shoulders study, front view,
> neutral expression; bottom right, head-and-shoulders study, three-quarter
> view. The face, hairstyle, build, clothing, and colours are identical in
> all four views — this is one artist's model sheet of one person, to be
> reused across hundreds of illustrations. No scenery, no props except
> those named below, no text, no labels, no arrows, no colour swatches,
> no borders. Square 1:1 composition.
>
> THE CHARACTER:

### PREAMBLE v2 (use this one for regenerations)

The v1 preamble above produced text panels on 3 of 12 sheets and scenery on
one. Two things in it caused that, and both are fixed below:

- It **opens by naming a document** ("A character model sheet for an
  illustrated literary edition"). Ask for a page and the model draws a page —
  with a caption block on it. v2 opens by naming *the figures*.
- Its prohibitions sit **buried mid-paragraph**, after ~90 words of prose the
  model is happy to letterset. v2 states the no-text rule first, alone, and
  again last.

> An illustration of one person drawn four times, on blank cream paper.
> Nothing is written anywhere in this image: no caption, no title, no name,
> no label, no annotation, no paragraph of description, no lettering of any
> kind. The image contains only drawings of the figure and empty cream
> background. Do not transcribe any part of this instruction into the
> picture.
>
> Style: clean, confident dark ink linework over flat, soft watercolour
> washes on lightly textured paper, in the tradition of Alan Lee and Barry
> Moser. Restrained Aegean palette — pale blue-grey, cream, sun-bleached
> limestone, olive and moss green, muted teal. Even soft daylight, minimal
> shading, no gradients, no glow, no photorealism, no anime, no 3D, nothing
> cute or sentimental: serious, dignified, adult.
>
> Layout: one square image, divided into an even two-by-two grid of four
> studies of the SAME person, with generous cream space between them and no
> ruled lines, borders, frames or panel dividers separating them. Top left:
> full figure, front view, standing relaxed, arms at sides. Top right: full
> figure, side profile view, standing. Bottom left: head and shoulders,
> front view, neutral expression. Bottom right: head and shoulders,
> three-quarter view. The face, hair, build, garments and every colour are
> identical in all four studies — this is one artist's model sheet of one
> person, to be reused across hundreds of illustrations, so a reader must
> never doubt that all four are the same individual.
>
> The background is empty cream paper. There is no room, no landscape, no
> sea, no ship, no building, no furniture, no horizon line and no second
> scene anywhere in the image. The only objects drawn are the garments and
> the props named below.
>
> Once more: this image contains no text.
>
> THE CHARACTER:

### PREAMBLE v3 — the layout that actually worked

The regenerated **athena-mentes** sheet came back clean: no text, no
scenery, one unmistakable man across nine views. Its layout is now the
standard, because the extra head studies are what forced the face to hold —
with only two busts the model has little to be consistent *with*.

Ask for: two full figures, a large feature head, five or six smaller head
studies at varied angles, and one or two isolated prop details on bare
cream. The prop detail is the sneaky win — it gives the model somewhere to
put its urge to add information, so it stops inventing captions and scenery.

> An illustration of one single person drawn many times over, on blank
> cream paper. Nothing is written anywhere in this image: no caption, no
> title, no name, no label, no annotation, no descriptive paragraph, no
> lettering of any kind. Do not transcribe any part of these instructions
> into the picture. The image contains only drawings of this one figure,
> two small prop studies, and empty cream background.
>
> Style: clean, confident dark ink linework over flat, soft watercolour
> washes on lightly textured paper, in the tradition of Alan Lee and Barry
> Moser. Restrained Aegean palette — pale blue-grey, cream, sun-bleached
> limestone, olive and moss green, muted teal. Even soft daylight, minimal
> shading, no gradients, no glow, no photorealism, no anime, no 3D, nothing
> cute or sentimental: serious, dignified, adult.
>
> Layout, loosely gridded with generous cream space and NO ruled lines,
> borders, frames or panel dividers anywhere: across the top, two or three
> full-length figures — front view standing relaxed, side profile, and
> rear or far-side view — plus one large head-and-shoulders study. Across
> the middle and lower area, five or six smaller head studies at varied
> angles: front, three-quarter left, three-quarter right, profile, chin
> lowered, chin raised — all the same neutral, composed expression. Also
> include one or two small isolated studies of this character's own props
> or costume details, drawn alone on the cream background at larger scale.
>
> Every study is the SAME individual: identical face, identical hair,
> identical build, identical garments, identical colours, with no variation
> between views. This is one artist's model sheet of one person, to be
> reused across hundreds of illustrations, so a reader must never doubt
> that every study shows the same individual.
>
> The background is empty cream paper. There is no room, no landscape, no
> sea, no ship, no building, no furniture, no horizon and no second scene
> anywhere in the image. The only things drawn are this figure, the named
> garments, and the named props.
>
> Once more: this image contains no text. Square 1:1 composition.
>
> THE CHARACTER:

### Colour lock (append verbatim after any character paragraph)

Cheap insurance against a reserved colour leaking onto the wrong cast
member — the failure that made three first-batch sheets unusable. Belts,
sashes, hems and trim are where it creeps in, so name them.

> COLOUR RULE: the garment colours named above are exact and complete. Do
> not add an accent colour that was not named — in particular no red, rust,
> terracotta, orange or maroon on any belt, sash, hem, trim, band, cord,
> strap or sandal, unless the paragraph above explicitly names that colour.

### REGENERATION PARAGRAPHS (v2 — use with PREAMBLE v3)

Three sheets still need replacing. Each paragraph below supersedes the v1
paragraph of the same name further down, and is written against the actual
defect that sheet came back with. Paste PREAMBLE v3, then the paragraph,
then the colour lock.

**odysseus** — *v1 defect: four separate mini-sheets divided by black rules,
one malformed bust, a terracotta sash.*
> Odysseus, a Greek hero in his mid-forties. Compact and powerfully built
> with broad shoulders and a thick neck — the strength of a wrestler, not a
> bodybuilder, and not heroic idealisation. Weathered sun-darkened skin,
> short curly mid-brown hair going grey at the temples, a short curled
> brown beard, heavy brows, deep lines at the eyes, and a watchful, steady,
> unhurried expression that gives nothing away. He wears a plain grey-blue
> wool tunic to mid-thigh with a narrow woven olive-green band at the hem,
> belted at the waist with a plain undyed brown leather belt — a leather
> belt only, and he wears no sash of any kind. Over it an olive-green wool
> cloak pinned at the right shoulder with a plain bronze disc pin; the
> olive cloak is his defining garment and appears in every full-length
> view. Brown leather strap sandals laced to mid-calf. A pale old scar
> shows above his right knee. No helmet, no weapon, no gold, no jewellery.
> For the prop studies, draw the bronze disc cloak-pin alone, and the
> scarred right knee alone in close study.

**penelope** — *v1 defect: half the canvas given to two scene panels; reads
late twenties rather than early forties.*
> Penelope, Queen of Ithaca, a woman of forty-two who has been waiting
> twenty years and looks it — she must read as clearly middle-aged and NOT
> as a young woman. Fine lines at the outer eyes and mouth, faint shadows
> beneath the eyes, a firm jaw, a few silver threads at the temple. Dark
> brown hair parted at the centre and gathered low at the back. She wears a
> long moss-olive-green chiton to the ankle, belted high beneath the breast
> with a plain woven cord of the same green. Over her hair and shoulders a
> pale sage-green veil; in the full-length views one edge of the veil is
> lifted and held near her cheek by her right hand, and that lifted-veil
> gesture is her signature. Plain leather sandals. No jewellery, no gold,
> no coloured trim. Her bearing is quiet, upright, dignified and sorrowful,
> never frail and never girlish. For the prop studies, draw her right hand
> holding the edge of the veil alone, and the woven green belt cord alone.

**aegyptius** — *not a v1 defect; a collision. The regenerated halitherses
came back bald, which he was not before, so both old men are now bald,
staffed and dressed in undyed wool — and Book II puts them in the same
assembly. Separate them on silhouette, not colour: Aegyptius becomes an
all-pale C-curve leaning on a short stick with both hands; Halitherses stays
an upright vertical with a dark mantle and a staff taller than himself.*
> Aegyptius, the oldest man in Ithaca, well past eighty and the most
> physically ruined figure in this cast. He is bent nearly double at the
> upper spine, so that even standing he folds forward into a deep curve and
> his head is carried low, thrust forward and turned slightly up to look at
> anyone he speaks to — that stooped C-shaped silhouette is his signature
> and must be unmistakable in every full-length view. He leans on a SHORT
> crooked stick barely reaching his waist, gripped in BOTH hands close to
> his body; never a tall staff. Almost entirely bald, with a few wisps of
> white hair over the ears, and only a short sparse white beard a few
> centimetres long — never a long beard. Sunken cheeks, a collapsed mouth,
> hooded eyes, hands swollen and knotted at every joint. His clothing is
> undyed wool from head to foot and all of one pale colour — a long
> off-white cream tunic to the ankle under a pale cream mantle of the same
> undyed wool, with no darker outer garment and no contrasting mantle at
> all, so that he reads as one pale shape. Worn leather sandals. No
> ornament. Fragile in body and entirely clear in mind; his face carries
> old grief carried patiently for a long time. For the prop studies, draw
> the short crooked stick alone, and his two knotted hands folded over the
> head of it alone.

**halitherses** — *v1 defect: landscape format, and the two full figures
wore different-coloured tunics.*
> Halitherses, an aged Ithacan seer of about eighty. Tall and gaunt, with
> hollow cheeks, a high domed forehead, sparse white hair, and deep-set
> hooded eyes fixed on something no one else can see. His beard is very
> long and white and reaches the middle of his chest — the longest beard in
> the cast. His costume is exactly this and is identical in every single
> view: a long undyed pale oatmeal-cream tunic to the ankle, and over it a
> heavy brown-grey mantle draped across the left shoulder. The tunic is
> pale oatmeal-cream in every view — never blue, never green, never any
> other colour — and the mantle is brown-grey in every view. Worn leather
> sandals. He carries a tall knotted wooden staff taller than himself. No
> ornament of any kind. Grave, oracular, unafraid. For the prop studies,
> draw the knotted head of the staff alone, and one gnarled hand gripping
> it alone.

### Design rule: signature over face

Image models drift on faces across many generations but hold **colour,
costume, prop and silhouette** reliably — and those are what a reader
actually uses to recognise someone at panel size. So every named character
gets a **signature**: one dominant garment colour + one prop or physical cue
that nobody else in the cast shares. Never reuse a signature colour on
another named character. The signatures below are deliberately spread apart.

| character | signature colour | signature cue |
|---|---|---|
| Odysseus | olive-green cloak | short curled beard, scar above right knee |
| Telemachus | cream-white tunic | youngest, clean-shaven, no cloak |
| Penelope | moss-green chiton | pale sage veil held near the cheek |
| Athena (Mentes) | slate-blue cloak | terracotta sash + tall bronze spear |
| Athena (Mentor) | dull ochre mantle | old man, white beard, plain staff |
| Athena (divine) | white + gold | crested helmet pushed back |
| Eurycleia | taupe-brown shawl | very old, stooped, carries a torch |
| **Antinous** | **deep terracotta-red himation** | **heavy gold armband, black curls** |
| **Eurymachus** | **pale grey-blue himation** | **clean-shaven, gold shoulder-pin, thin build** |
| Halitherses | cream tunic + **brown-grey mantle** | upright; chest-length white beard; tall knotted staff |
| Aegyptius | **all pale cream, no darker mantle** | bent double into a C; short stick held in both hands; short sparse beard |
| Mentor (the real man) | plain grey-green | old, short white beard, NO staff |

Two overlaps are **deliberate** and must not be "corrected": *athena-mentor*
and *mentor-real* share grey-green (the poem turns on the resemblance;
separated by beard length, eye colour, stoop, staff), and *Odysseus*
(olive cloak) / *Penelope* (moss-olive chiton) share a green family on
purpose — husband and wife, never in one plate before Book XXIII.
Every other signature colour must stay unique to one character.

Antinous and Eurymachus get the two strongest, most opposed signatures on
purpose — they are the recurring antagonists through Book XXII, and in the
Book I batch they were indistinguishable members of a crowd.

### Character paragraphs (paste ONE after "THE CHARACTER:")

**odysseus**
> Odysseus, a Greek hero in his mid-forties. Compact and powerfully built
> with broad shoulders — strength, not bulk. Weathered tan skin, short
> curly mid-brown hair, a short curled brown beard, heavy brows, and a
> watchful, steady, unhurried expression. He wears a grey-blue wool tunic
> to mid-thigh, belted at the waist, under an olive-green wool cloak pinned
> at the right shoulder — the olive cloak is his defining garment. Brown
> leather strap sandals laced to mid-calf. A pale old scar is just visible
> above his right knee. No helmet, no weapon, no jewellery.

**telemachus**
> Telemachus, a young man of nineteen — the youngest man in the story, and
> he must look it. Slim and boyish, not yet filled out, completely
> clean-shaven. Short tousled dark-brown hair, blue-grey eyes, an earnest,
> slightly anxious set to the mouth. He wears only a plain cream-white
> short tunic with a thin leather belt, and brown strap sandals —
> deliberately the plainest dress of any named character: no cloak, no
> jewellery, no weapon.

**penelope**
> Penelope, a queen in her early forties, beautiful in a guarded, weary
> way. Dark brown hair parted at the centre and gathered low at the back.
> She wears a long moss-olive-green chiton to the ankle, belted high, and
> over her hair and shoulders a pale sage-green veil, one edge lifted and
> held near her cheek by her right hand — that lifted-veil gesture is her
> signature and should appear in the standing views. Plain sandals. Her
> bearing is quiet, dignified, and sorrowful, never frail.

**athena-mentes**
> Mentes, a Taphian sea-chieftain — actually the goddess Athena in
> disguise, and drawn as a MAN. A lean, weathered seafarer of about forty
> with a close-trimmed dark beard, dark hair bound under a plain band, and
> unsettlingly steady pale blue-grey eyes — the one uncanny note in an
> otherwise ordinary sailor. Long olive tunic; a slate-blue cloak over one
> shoulder; a broad braided belt of undyed leather; plain sandals. He
> carries one tall wooden spear with a bronze tip, held upright — the
> slate-blue cloak and the spear are his signature. No red anywhere.

**athena-mentor**
> Mentor, an elderly Ithacan gentleman — actually the goddess Athena in
> disguise. A lean old man with an upright, vigorous bearing that does not
> quite match his age. Thinning white hair, a close-cropped white beard,
> a deeply lined, kind face — and steady pale blue-grey eyes, the one
> uncanny note. Long grey-green belted robe to the ankle, a dull ochre
> mantle over one shoulder, plain sandals, and a plain wooden walking
> staff. Grave and reassuring.

**mentor-real**
> Mentor, an old friend of Odysseus — an ordinary elderly Ithacan man.
> Balding, with a SHORT white beard, mild brown eyes, and the slightly
> stooped bearing of his true age. Plain grey-green mantle over a long
> undyed tunic, plain sandals, empty hands — no staff. He should look
> like a softer, wearier brother of the athena-mentor design: the poem
> plays on the resemblance, but the two must be tellable apart by the
> shorter beard, brown eyes, stoop, and absent staff.

**athena-divine**
> The goddess Athena in her own form. A tall young woman, serene and
> severe, with grey eyes and dark hair. She wears a white chiton with a
> gold-worked aegis breastplate over it, and a crested bronze helmet
> pushed back off her face so the whole face is visible. She holds a tall
> spear upright and a round bronze-rimmed shield rests at her side.
> Radiant but composed — power at rest, nothing cartoonish.

**eurycleia**
> Eurycleia, a very old household nurse, small and stooped but steady and
> quick-eyed. Grey hair covered by a taupe-brown shawl wrapped over her
> head and shoulders; a long undyed cream wool dress; plain sandals. In
> one standing view she carries a lit torch in her right hand — her
> signature prop. Careworn, devoted, entirely unafraid.

**antinous**
> Antinous, ringleader of the suitors — he must be instantly recognisable
> in any crowd. A tall, handsome, well-fed man of about thirty with black
> curly hair, a thin black beard traced along the jaw, and a hard,
> insolent, amused set to the mouth. He wears a deep terracotta-red
> himation draped over the left shoulder, leaving the right shoulder and
> chest bare — he is the only man in this cast who wears red — and a heavy
> gold armband on his bare upper right arm. In one view he holds a shallow
> wine cup carelessly. Plain sandals.

**eurymachus**
> Eurymachus, the second leader of the suitors — smooth where Antinous is
> brash, and designed as his opposite. A man of about thirty, noticeably
> slight of build, completely clean-shaven, with straight light-brown
> hair, even features, and a courteous half-smile that never reaches his
> eyes. He wears a pale grey-blue himation over one shoulder fastened
> with a small thin gold pin, and plain sandals. No other ornament.

**halitherses**
> Halitherses, an aged Ithacan seer. Gaunt, with a VERY long white beard
> reaching his chest, sparse white hair, and deep-set hooded eyes that
> seem fixed on something no one else can see. Plain undyed brown-grey
> mantle over a long tunic; a tall knotted wooden staff; worn sandals.
> Grave, oracular, unafraid.

**aegyptius**
> Aegyptius, the oldest man of the Ithacan assembly — extremely aged,
> bent nearly double over his staff. Almost bald, with wisps of white
> hair, sunken cheeks, and hands knotted with age. A pale undyed wool
> mantle wrapped about him, worn sandals. Fragile in body, clear in mind;
> his face carries old grief borne with patience.

### Generic types (no sheet; describe inline in scene prompts)

- **suitors (crowd)** — men in their twenties and thirties in draped
  himations of white, pale blue-grey and olive, some bearded, wine cups,
  lounging; none may wear red (red is Antinous's alone).
- **maids** — young women in plain pale-blue or undyed sleeveless chitons,
  hair bound back, quiet and watchful.
- **heralds / elders / townsmen** — plain long mantles, staffs, stone
  benches.

## FULL-EPIC CAST ROSTER

The 12 core sheets above cover Books I–II and the household frame. The whole
epic needs the sheets below as well. **Signature colours are reserved here
for the entire cast now** — generate the sheets just-in-time per book
cluster, but never reassign a colour. Paragraphs follow the same recipe:
PREAMBLE + one block.

Cluster guide (generate before starting the listed books):
- **Pylos/Sparta (III–IV, XV):** nestor, peisistratus, menelaus, helen
- **Gods (I, V, X, XII–XIII, XXIV):** zeus, poseidon, hermes
- **Ogygia/Scheria (V–VIII, XIII):** calypso, nausicaa, alcinous, arete, demodocus
- **Wanderings (IX–XII):** polyphemus, circe, eurylochus, elpenor
- **Nekyia (XI, XXIV):** tiresias, anticleia, agamemnon-shade, achilles-shade
- **Ithaca II (XIII–XXIV):** eumaeus, philoetius, melanthius, melantho,
  amphinomus, theoclymenus, phemius, medon, argos, laertes

### Pylos and Sparta (Books III–IV, XV)

- **nestor** — Nestor, the Gerenian horseman, king of Pylos: the oldest
  living hero, about eighty, and still upright and vigorous where other old
  men stoop. Tall, broad-shouldered, a full white beard combed to the
  chest, thick white hair, and shrewd humorous eyes. A long, richly dyed
  **deep saffron-gold** robe to the ankle with a woven meander border — the
  only man in the epic who wears saffron, and by far the best-dressed old
  man in it. His signature prop is a **two-handled golden cup**, held in one
  view. No staff: he does not need one. Courteous, garrulous, formidable.
  He must not read as frail — his whole point is an old age that worked out.
- **peisistratus** — Peisistratus, Nestor's youngest son, who travels with
  Telemachus through Books III–IV and XV. Deliberately designed to pair
  with Telemachus and never be confused with him: about twenty-two, a
  little older and noticeably sturdier, with a first dark beard coming in
  along the jaw where Telemachus is clean-shaven. Dark chestnut hair worn
  slightly long. A short **chestnut-brown** riding tunic and a rider's short
  cloak, where Telemachus wears a plain cream tunic and no cloak. His
  signature prop is a **pair of leather driving reins** held in one hand —
  he is the charioteer of the pair. Easy, well-bred, quietly kind.
- **menelaus** — Menelaus, king of Sparta, husband of Helen: a big
  weathered man of fifty with the **red-gold hair and beard** Homer gives
  him — that colouring is his signature and no one else in the cast has it.
  A long **steel-grey** robe with a gold-worked border, a plain gold
  circlet. Hospitable and open-handed, and visibly a man still carrying the
  war: the grief sits on him even when he is being generous.
- **helen** — Helen of Sparta, in her forties and still the most beautiful
  woman in the world, which the drawing should treat as a plain fact rather
  than a seduction. Composed, self-aware, faintly sad. Pale gold hair
  bound low. A long **ivory-white** chiton with fine silver embroidery at
  the hem and a translucent silver-grey veil. Her signature prop is a
  **silver work-basket on small wheels**, with a golden distaff of violet
  wool laid across it — she is drawn with it, not with a mirror. No
  jewellery beyond the silver.

### Gods

- **zeus** — Zeus, father of gods and men: a massive, calm, iron-grey king
  in late maturity. Long iron-grey hair and full beard, deep-set eyes. Off-
  white himation leaving one shoulder bare, a thin gold oak-leaf circlet;
  in one view he holds a stylised golden thunderbolt at rest across his
  knees. Unhurried, amused, absolute.
- **poseidon** — Poseidon, god of the sea and earthquake: broader and
  wilder than his brother Zeus. Storm-tossed dark grey hair and beard,
  weathered skin, sea-green mantle that moves like water, and a tall
  bronze trident. Perpetual banked anger — a storm waiting for a reason.
- **hermes** — Hermes, the guide and messenger: an ageless youth, slight
  and quick, with short dark curls under a brimmed traveller's hat pushed
  back. Short belted tunic of pale cloud-grey, a small travelling cloak,
  and low winged sandals at the ankles; he carries a slim golden wand.
  Light-footed, wry, faintly amused by mortals.

### Ogygia and Scheria (Books V–VIII, XIII)

- **calypso** — Calypso, the nymph of Ogygia: ageless, beautiful, and
  lonely, with long loose dark hair braided with tiny white shells. A
  flowing sea-teal gown; bare feet. Her beauty is real but the design
  must carry possessive melancholy, never coquettishness: she is a
  jailer in love with her prisoner.
- **nausicaa** — Nausicaa, a Phaeacian princess of about sixteen: bright,
  composed, entirely unafraid. Dark hair in a simple girlish braid; a
  knee-length sea-foam pale blue-green chiton suitable for laundry work
  at the river, bare feet or simple sandals. Carries herself with a
  self-possession beyond her age.
- **alcinous** — Alcinous, king of the Phaeacians: a hale, genial man of
  fifty in a deep sea-blue robe with a plain gold circlet and a staff of
  office. Generous, a little grand, fond of his own hospitality.
- **arete** — Arete, queen of the Phaeacians, wiser than her husband: a
  grave, perceptive woman of fifty, dark hair streaked grey under a deep
  plum mantle over an undyed chiton; she spins sea-purple wool on a
  distaff — her signature prop. People are weighed in her gaze.
- **demodocus** — Demodocus, the blind Phaeacian bard: a lean man of
  sixty, eyes closed or unfocused (blind, unscarred, serene), grey hair,
  in a plain pale-grey robe, holding a tortoiseshell lyre. His face does
  what his eyes cannot.

### The wanderings (Books IX–XII)

- **polyphemus** — Polyphemus the Cyclops: a mountainous one-eyed giant,
  three times a man's height, with a single large eye centred above the
  nose (no second sockets), a heavy brow, matted dark hair and beard, and
  a crude undyed wool tunic belted with rope. He herds sheep with an
  uprooted pine for a staff. Design him as pastoral and terrible at once
  — a shepherd who eats men.
- **circe** — Circe, the witch-goddess of Aiaia: ageless and severely
  beautiful, with elaborately braided auburn-bronze hair. A deep bronze-
  gold embroidered gown, and a slim dark wand. Cool, appraising,
  dangerous first; a fair ally later. Never draw her comic.
- **eurylochus** — Eurylochus, Odysseus's second-in-command and kinsman:
  a big cautious man in his forties, short grizzled beard, in a salt-stained
  dark brown sailor's tunic with a worn leather corselet. Brave against
  monsters, weak against hunger; his face carries doubt.
- **elpenor** — Elpenor, the youngest of the crew: gangly, early twenties,
  scruffy first beard, in an undyed tunic with a rope belt, usually
  barefoot. Amiable, unlucky, and slightly drunk — design him so his
  ghost in Book XI is recognisably the same boy.

### The dead (Books XI and XXIV)

- **tiresias** — Tiresias, the blind Theban seer, dead but authoritative:
  a tall shade in shroud-grey robes, long white hair and beard, sightless
  pale eyes, carrying a golden staff — the one bright thing about him.
- **anticleia** — Anticleia, Odysseus's dead mother: a gentle woman of
  sixty in a pale ash-grey veil and chiton, her face full of love and the
  particular sadness of the dead. Slightly translucent in scenes.
- **agamemnon-shade** — The ghost of King Agamemnon: a powerful bearded
  king in a once-royal dark bronze-brown robe, a shadow like a stain
  across the breast of it (never an explicit wound), pale, bitter,
  warning. Regal even in ruin.
- **achilles-shade** — The ghost of Achilles: the most beautiful of the
  Greek dead, young, clean-limbed, in a plain pale grey tunic with no
  armour at all — that absence is the point. His face holds the knowledge
  that fame was a bad trade.

### Ithaca, second half (Books XIII–XXIV)

- **eumaeus** — Eumaeus, the loyal swineherd, in seven books — after the
  leads, the most important face in the epic. A weathered, sturdy man of
  fifty-five, grey-bearded, kind deep-set eyes. A russet-brown sheepskin
  jerkin over a rough tunic, leather leggings, and a herdsman's crook.
  Patient dignity in worn clothes.
- **philoetius** — Philoetius, the loyal cowherd: younger and broader than
  Eumaeus, forty, clean-shaven with a heavy jaw, in a dun-tan oxhide vest
  over a rough tunic, oxhide sandals. Steady, slow to speak, immovable
  once decided.
- **melanthius** — Melanthius, the treacherous goatherd: a lean sneering
  man of thirty-five in a harsh mustard-yellow tunic and a goatskin cap,
  wispy beard, quick darting eyes. Servile upward, vicious downward.
- **melantho** — Melantho, Penelope's disloyal maid and Eurymachus's
  lover: pretty, sharp-faced, early twenties, in a maid's blue-grey
  chiton worn with a borrowed-looking bead necklace above her station.
  Scornful mouth.
- **amphinomus** — Amphinomus, the one decent suitor: a man of thirty with
  a soft, worried, likeable face, light beard, in a mid-green himation
  with no ornament. He alone among the suitors looks like he knows how
  this ends.
- **theoclymenus** — Theoclymenus, a fugitive seer taken aboard by
  Telemachus: a hollow-cheeked man of forty in a dark charcoal traveller's
  cloak, wind-tangled dark hair, haunted eyes that see the doom he
  announces. Always slightly apart from the group.
- **phemius** — Phemius, the Ithacan bard forced to sing for the suitors:
  a slender man of forty in a pale ivory robe, holding a tortoiseshell
  lyre; a gentle face with the guarded look of a hostage performer.
- **medon** — Medon, the household herald who protects Telemachus: a
  portly, anxious, decent man of fifty, balding, in an undyed herald's
  mantle with a herald's staff.
- **argos** — Argos, Odysseus's old hound: a once-great tan hunting dog
  with a grey muzzle, ribs showing, lying on a dung heap by the gate;
  ears still noble, eyes clouded but aware. Design once, use twice: the
  young dog (in a flashback plate, ears up, mid-hunt) and the old one.
- **laertes** — Laertes, Odysseus's father: a gaunt old man of eighty who
  was once a king and now digs his own orchard. A patched, dirty work
  tunic, a goatskin cap, leather garden gauntlets, a hoe; white-bearded,
  bent, grief-worn — and in Book XXIV, briefly straightened by joy.

### Inline-only (no sheets — one scene each; describe in the scene prompt)

Ino/Leucothea, Aeolus and his floating court, the Laestrygonian king and
queen, the Sirens, Scylla (six long necks from a cliff cave — keep her
monstrous, not a woman), Charybdis (a whirlpool, not a face), Proteus and
Eidothea, Helios, the Ares/Aphrodite/Hephaestus trio in Demodocus's song,
the great shades (Heracles, Minos, Sisyphus, Tantalus, Orion), Dolius and
his sons, Irus the beggar, minor suitors (Leocritus, Ctesippus, Agelaus,
Leodes), and Eupeithes in Book XXIV — draw him as an older, grief-hollowed
echo of Antinous in mourning grey, leading the mob.
## BOOK I — 10 plates (Gemini app workflow)

Written for one chat session: upload all 12 sheets once, paste the SETUP
message once, then paste scenes 1–10 one at a time into the same thread.
Keeping one thread is the point — the model holds the cast and the style
across turns, and consistency collapses if scenes are split across chats.

Upload the **clean** sheets from `img/characters/`, not the labelled copies
in `labeled/` — burnt-in lettering in a reference leaks lettering into the
output. Upload in alphabetical order; the SETUP message maps that order to
names, which is how the model knows who is who.

If a scene drifts, re-paste the SETUP message and continue. If the model
starts drawing text in the plates, re-paste the "no lettering" line alone.

### SETUP (paste once, after uploading all 12 sheets)

> I am illustrating a serious literary edition of Homer's Odyssey for adult
> readers. I have uploaded 12 character model sheets. In alphabetical order
> they are: (1) Aegyptius, the bent, all-pale-cream old man with a short
> stick; (2) Antinous, the suitor in deep terracotta-red with a gold
> armband; (3) Athena in her divine form, white and gold with a crested
> helmet; (4) Mentes, the male Taphian sea-chieftain in a slate-blue cloak
> with a spear — this is Athena disguised as a man, and must always be drawn
> as a man; (5) Mentor as Athena wears him, the upright old man in a dull
> ochre mantle with a staff; (6) Eurycleia, the old nurse in a taupe-brown
> shawl with a torch; (7) Eurymachus, the slight clean-shaven suitor in pale
> grey-blue; (8) Halitherses, the upright old seer with a chest-length white
> beard and a tall staff; (9) the real Mentor, the stooped old man in
> grey-green with a short beard and no staff; (10) Odysseus, the bearded man
> in an olive-green cloak over a grey-blue tunic; (11) Penelope, the
> middle-aged queen in a moss-olive chiton holding a pale sage veil to her
> cheek; (12) Telemachus, the beardless young man in a plain cream tunic.
>
> When a scene names one of these people, draw them exactly as their sheet
> shows them: same face, same build, same garments, same colours. This
> matters more than anything else in the image — a reader must recognise
> them across a hundred pictures.
>
> STYLE, for every image in this conversation: illustration for a serious
> literary edition of an ancient epic, in the tradition of Charles Keeping,
> Barry Moser and Alan Lee. Clean confident dark ink linework over flat,
> soft watercolour washes on lightly textured paper. Restrained Aegean
> palette — pale blue-grey, cream, sun-bleached limestone, olive and moss
> green, muted teal — with warm terracotta-red kept as a rare accent.
> Minimal rendering, no gradients, no glow, no photorealism, no anime, no
> 3D, nothing cute or sentimental. Grave, unhurried, adult: stillness rather
> than spectacle, but never sanitised — this poem holds grief, captivity and
> killing, and the pictures must be able to hold them too. Archaic Mycenaean
> material culture: long ships with a single square sail, bronze tripods,
> geometric-pattern hems, megaron halls with a central hearth and
> red-banded columns, wooden benches, clay amphorae. Figures at a composed
> middle distance, faces readable but rarely close-up.
>
> Every image is square 1:1. No lettering of any kind anywhere in any
> image: no caption, no title, no label, no speech balloon, no signature,
> no watermark, no panel border and no frame.
>
> Reply "ready" and nothing else. I will send scenes one at a time.

### The ten scenes (paste one per turn)

Each is a single square plate. Filenames are what to save as, into
`img/bk01/`; they must keep these exact names or the manifest breaks.

**1 — title-plate.jpeg** *(v1 was a montage of small vignettes, which read
as a contents page and looked wrong behind prose; this must be one single
image)*
> One single emblematic image, not a montage and not divided into panels.
> A vast empty sea seen from high above, occupying almost the whole frame,
> in muted teal and pale blue-grey. One small Mycenaean long ship with a
> single square sail, very small, far out and alone. Its white wake trails
> behind it in a long meandering line that doubles and turns back on itself
> so that it almost resembles a maze drawn on the water. Great emptiness
> around the ship. No land, no figures, no border, no lettering.

**2 — calypso-glimpse.jpeg** *(captivity, not romance — the island must
read as an enclosure)*
> A lone bearded man — Odysseus, from his sheet, in his olive-green cloak —
> seen small and from a distance, sitting on wet black rocks at the very
> edge of a beautiful island shore, hunched forward with his forearms on
> his knees and his head down, his back turned to all the greenery behind
> him. The island is lush and lovely and hemmed with flowers, and it is
> drawn as a cell: the frame closed on both sides by dark cliff walls so
> that the only opening is the flat empty horizon in front of him. An
> enormous grey-green sea, no ship anywhere on it, no other figure. The
> palette is deliberately drained — no terracotta, no warm colour anywhere
> in this plate.

**3 — council-of-gods.jpeg** *(bigBeat: gets its own full-bleed page)*
> High on Olympus. Gods seated in a loose ring on pale stone benches among
> banked cloud, in soft white daylight, all of them calm and unhurried.
> Zeus at the centre, a heavy grey-bearded king, a bronze thunderbolt laid
> flat across his knees like a tool set down after work. Athena — from her
> divine sheet, white chiton, gold aegis, crested helmet pushed back —
> leaning forward from her seat mid-argument, one arm extended, pointing
> down through a gap in the clouds. Far below through that gap, tiny, a
> single green island on a wide dark sea. The other gods watch her, not the
> island. Grave, political, no spectacle, no lightning, no glow.

**4 — athena-at-the-gate.jpeg** *(v1 drew Mentes as a woman; he is a man —
attach sheet 4 and say so)*
> Mentes, the male Taphian sea-chieftain from his sheet — a bearded man in
> a slate-blue cloak holding a tall bronze-tipped spear upright — standing
> completely still just inside the outer gate of a stone courtyard, facing
> in. He is drawn as a man; this is not a woman. He is sharply lit and
> sharply drawn. Beyond him, deeper into the courtyard and rendered softer
> and hazier, a scatter of young men in draped himations sprawl on cattle
> hides playing a board game, wine cups beside them, none of them looking
> up. The contrast is the subject: one still, clear figure at the threshold
> and a blurred sprawl of idle men behind.

**5 — telemachus-sees-her.jpeg**
> Interior of a megaron hall with a central hearth and red-banded columns.
> Telemachus — from his sheet, beardless, plain cream tunic — seated among
> lounging suitors but set apart from them, chin resting on his fist,
> staring at nothing, not part of the room. Around him, men eating and
> talking, at ease, taking up space. A shaft of daylight from the open
> doorway falls across the floor, and both that light and Telemachus's
> sightline land together on a still figure standing at the threshold: the
> bearded man in the slate-blue cloak with the spear. He is small in the
> frame and the most important thing in it.

**6 — spear-rack.jpeg** *(a still life; no faces)*
> Close, quiet still life in a shaft of dusty daylight. A young man's hand
> and forearm only — no face, no body — sliding a bronze-tipped spear into
> a tall polished wooden spear-rack set against a stone pillar. Standing in
> the rack already are many older spears, dulled and unused, their shafts
> dusty: the weapons of a man who has not come home. Dust motes hanging in
> the light. Nothing else in the frame. Still, reverent, almost a portrait
> of the rack itself.

**7 — the-feast.jpeg** *(the plate that carries the suitors' menace; the
two named men must be findable)*
> The suitors' feast at full tilt in the megaron hall, and it should look
> like a household being eaten alive: long tables, meat carved off the bone
> and passed hand to hand, a herald pouring wine, spilled cups, bones on the
> floor, dogs under the benches, men lounging with their feet on the
> furniture in total ease. Two men are drawn to be recognised — Antinous
> from his sheet, in the deep terracotta-red himation with the gold armband,
> at the head of the table holding a wine cup carelessly and laughing; and
> Eurymachus from his sheet, slight, clean-shaven, in pale grey-blue,
> beside him, not laughing, watching the room. No other man in the picture
> wears red. At the near edge of the frame, apart from all of it,
> Telemachus leans close to the seated stranger in the slate-blue cloak,
> one hand cupped at his mouth, speaking low.

**8 — phemius-sings.jpeg**
> A bard — a middle-aged man with a wooden lyre, not from the uploaded
> sheets — standing singing to the hall, his face lifted, the suitors below
> him rapt or smirking, cups paused. Behind and above him, on a stone
> staircase, half in shadow and gripping the rail, Penelope from her sheet:
> middle-aged, moss-olive chiton, holding the edge of her pale sage veil
> against her cheek, having stopped on the stair because of what he is
> singing. Two maids in plain pale-blue chitons at her shoulders. She is
> higher than everyone and entirely alone. The light is warm below and cold
> where she stands.

**9 — bird-departure.jpeg**
> Seen from inside the hall looking steeply up. A small bird of prey
> shooting upward and out through the high smoke-hole in the roof into a
> pale blank sky, already tiny, already leaving. Below, alone in the
> emptying courtyard with the benches pushed back, Telemachus from his
> sheet stands looking up, head tilted right back, arms loose at his sides
> — a young man who has just understood something. No wings of light, no
> halo, no glow, no divine effect of any kind: an ordinary bird, an
> extraordinary face.

**10 — eurycleia-torches.jpeg** *(bigBeat: gets its own full-bleed page)*
> A narrow stone stair at night, lit only by fire. Eurycleia from her sheet
> — a small stooped old woman in a taupe-brown shawl — climbing ahead and
> above, carrying two blazing torches in one hand, Telemachus's folded
> tunic over her other arm. The torch flame is the one warm terracotta note
> in an otherwise cold blue-black plate. Telemachus follows a few steps
> below her, small and young. On the wall beside him the torchlight throws
> his shadow up enormous and wavering — and the shadow is subtly not his:
> broader in the shoulder, bearded, the silhouette of a grown warrior.
> Do not explain the shadow; just draw it.

### After generating

Save all ten into `img/bk01/` under the exact filenames above, then:

```
python3 data/build_illustrated.py   # must print no WARN lines
```

The manifest already carries the anchors, `splashOnly` on the title plate,
and `bigBeat` on council-of-gods, athena-at-the-gate and eurycleia-torches,
so nothing needs editing if the filenames match.

## BOOK XXIV — 10 plates

1. **bk24/title-plate.png** (portrait) — Emblematic: Hermes's golden wand
   held vertical, tiny bat-like souls spiraling down its length toward a dark
   meadow of asphodel below.
2. **bk24/souls-descend.png** — Hermes leading a gibbering stream of suitors'
   souls down a dank cavern path past the White Rock; the souls rendered as
   loose ink smears with barely-there faces, like bats shaken from a cave
   ceiling.
3. **bk24/achilles-and-agamemnon.png** — Two great shades conversing in the
   asphodel meadow: Achilles still magnificent, Agamemnon diminished and
   grieving; around them dim ranks of the dead lean in to listen.
4. **bk24/the-shroud.png** — Flashback plate, softer washes: Penelope at the
   great loom by torchlight, unpicking the day's weaving thread by thread;
   through the doorway behind her, suitors asleep over their cups.
5. **bk24/amphimedon-tells.png** — A dead suitor's shade gesturing as he
   recounts the slaughter; behind him, ghost-faint, the bow, the axes, the
   doorway scene rendered as a pale memory-image within the image.
6. **bk24/laertes-in-the-vineyard.png** — Old Laertes alone in a terraced
   vineyard, digging around a young vine; patched tunic, leather greaves,
   goatskin cap; enormous quiet; Odysseus watching unseen from under a tall
   pear tree, one hand on the trunk, weeping.
7. **bk24/the-scar-and-the-trees.png** — Odysseus kneeling, pulling back his
   rag to show the boar scar; with the other arm he gestures across the
   orchard rows; Laertes's hand flying to his own face; thirteen pear trees,
   ten apple trees, forty figs implied in receding ranks behind them.
8. **bk24/embrace.png** — Laertes fainting into his son's arms among the
   vines; Odysseus braced, holding his father's whole slight weight;
   terracotta accent: a single ripe fruit fallen at their feet.
9. **bk24/eupeithes-falls.png** — The brief last battle at the farm gate:
   old Laertes, armored over field clothes, spear just thrown, astonished at
   his own cast; Eupeithes mid-fall, helmet split; Odysseus and Telemachus
   surging forward side by side.
10. **bk24/peace.png** — Athena between the two frozen crowds, arms out,
    enormous and calm, in Mentor's shape but unmistakably more; weapons
    falling from hands; above, very small, a smoking thunderbolt streaking
    down the sky; the whole composition settling into symmetry — the poem's
    last exhale.
## BOOK II — 8 plates (Gemini app workflow)

Continue in the **same chat thread as Book I** if it is still open — the
cast and style are already established there and consistency is better for
it. If starting fresh, re-upload the 12 sheets and re-paste the Book I
SETUP message first.

The manifest entry for `bk02` is already written and its anchors are
validated against `seeds/modern.md`. Save into `img/bk02/` under the
exact filenames below and the book wires itself up.

Book II is the assembly book: one long public scene, then a secret
departure. Its risk is monotony — six of eight beats happen among the same
seated men in the same square. So the plates deliberately alternate wide
daylight crowd against tight interior night: assembly, assembly, assembly,
then the web by torchlight; eagles, assembly; then the storeroom and the
sea. Hold that rhythm even if a plate has to be composed harder for it.

**The one collision to watch.** Aegyptius and Halitherses are both very old,
both bald, both carry sticks, and Book II is the only place they appear
together. They are separated by silhouette: Aegyptius is a pale C-curve
folded over a short stick held in both hands, with a short sparse beard;
Halitherses is an upright vertical with a dark brown-grey mantle, a
chest-length white beard and a staff taller than himself. Scenes 2 and 6
name those cues explicitly. If a plate makes them look alike, regenerate.

### The eight scenes (paste one per turn)

**1 — assembly-dawn.jpeg** *(opening plate; establishes the square)*
> Early morning in an archaic Greek town square below a rocky hillside.
> Telemachus from his sheet — beardless, plain cream tunic, a bronze-tipped
> spear in his hand — walking in from the left toward a gathering of seated
> men, two hunting dogs trotting at his heels. The men are elders and
> townsmen in plain long mantles, settling onto weathered stone benches
> arranged in a rough curve, some still standing and turning to look at him.
> Long low dawn light raking across the stone, long shadows. He is much the
> youngest person present and the only one walking. Composed, wide, quiet —
> the moment before a public argument, not the argument.

**2 — aegyptius-speaks.jpeg**
> The same square, full daylight, the assembly now seated and settled.
> Aegyptius from his sheet, standing in the open middle of the gathering
> and speaking — an extremely old man folded forward into a deep stoop, all
> in pale undyed cream, leaning on a short crooked stick gripped in both
> hands, his head carried low and turned up toward the seated men. He must
> read as a pale bent C-shape. The seated townsmen watch him in silence.
> His face is one of old grief carried patiently for years: he is a father
> whose son sailed away and never came back. Nobody else stands. Do not
> draw a tall upright old man with a long beard here — that is a different
> character.

**3 — the-staff-thrown.jpeg** *(bigBeat: full-bleed page)*
> The emotional centre of the book. Telemachus from his sheet standing
> alone in the middle of the assembly, having just flung a herald's wooden
> staff down onto the stone — the staff lies where it fell, still rocking,
> at the bottom of the frame. He has both hands open and empty at his
> sides, head down, face wet with tears, shoulders gone. He is nineteen and
> he has just failed in public. All around him the seated men are utterly
> still and silent, faces turned toward him, several of them stricken with
> pity, none of them moving to help. Wide framing, a lot of empty stone
> between him and everyone else. Grave and quiet, no drama, no gesture.

**4 — penelopes-web.jpeg** *(night interior — breaks the daylight run)*
> Deep night in an upper chamber, lit only by two torches set in floor
> stands, everything beyond their reach in blue-black darkness. Penelope
> from her sheet — middle-aged, moss-olive chiton, sage veil pushed back
> off her hair for work — standing at a tall upright wooden loom, her hands
> raised to the warp, pulling the weft threads back OUT of a great
> half-finished cloth. Loose unravelled thread pools around her feet in a
> long tangle. Her face is set and awake and entirely unsentimental: this
> is work, and it is the third year of it. In the dark doorway behind her,
> half-seen, a young maid stands watching her — the maid who will tell. The
> cloth on the loom is a burial shroud, pale and undyed.

**5 — two-eagles.jpeg** *(bigBeat: full-bleed page)*
> Seen from below, steeply up. Two large eagles locked together in the pale
> open sky above the assembly, wings beating out of rhythm, talons in each
> other's necks and faces, feathers coming loose and drifting. They are the
> subject and they fill the upper two thirds of the frame. Below, along the
> bottom edge, the upturned faces and shoulders of the seated men — small,
> in shadow, every face tilted back, mouths open. No god visible, no light
> effect, no glow. Just two birds tearing at each other over a town that
> has stopped talking.

**6 — seer-and-suitor.jpeg**
> A two-figure confrontation in the assembly, framed close. On the left,
> Halitherses from his sheet: an old man standing straight and tall, in a
> pale oatmeal tunic under a heavy brown-grey mantle, a chest-length white
> beard, both hands on a tall knotted staff that rises above his head,
> looking up and out past everyone at something no one else can see. On
> the right, Eurymachus from his sheet: slight, clean-shaven, pale
> grey-blue himation, seated at ease with one arm along the bench back,
> looking at the old man with a courteous half-smile that does not reach
> his eyes, one hand raised in a small dismissive gesture. Between them a
> gap of empty stone. Antinous in his terracotta-red himation sits further
> back, watching, amused. No one else in the picture wears red.

**7 — the-storeroom.jpeg**
> A windowless underground storeroom at night, high-roofed, lit by one
> small oil lamp. Rows of great clay jars of wine and olive oil along the
> walls, wooden chests, stacked bronze vessels dulled with age, a smell of
> dust in the light. Telemachus from his sheet kneeling to fill a leather
> travelling sack with barley meal, his back half turned. Eurycleia from
> her sheet — small, stooped, taupe-brown shawl — standing over him with
> the lamp in one hand and her other hand pressed flat to her mouth, crying
> without sound, having just understood that he is leaving. The lamp is the
> only warm colour. Everything is stored, sealed, waiting for a man who has
> not come back.

**8 — night-launch.jpeg** *(bigBeat: full-bleed page)*
> Night at sea, a strong following wind. A black Mycenaean long ship under
> one taut square sail, cutting away from the viewer into open dark water,
> its wake bright behind it. The land is a low black shape at the very edge
> of the frame, already far off. On deck the crew are small dark shapes at
> the oars and the steering oar; at the stern, Telemachus in his pale tunic
> is the one light figure aboard, looking back the way they came. Cold
> palette — blue-black sea, blue-black sky, one hard silver line of
> moonlight on the water. No stars-as-decoration, no romance. A boy leaving
> home in the dark without telling his mother.

### After generating

```
python3 data/verify_plates.py bk02      # size / format / red-budget checks
python3 data/build_illustrated.py       # must print no WARN lines
```

The eight anchors were validated against the actual paragraphs of Book II
before the manifest was written, so a WARN here means a filename typo, not
a bad anchor.

## BOOK III — 5 plates

1. **bk03/ninety-bulls.png** — The beach at Pylos at sunrise: nine long rows
   of feasting benches, smoke of burning thigh-pieces rising, the sea behind;
   Telemachus's single small ship gliding in at the edge of the vast ritual.
2. **bk03/nestor-tells.png** — Nestor on his throne of story: firelight, the
   old king mid-gesture, young men frozen listening, Telemachus leaning
   forward; ghosted faintly in the smoke above, tiny ships scattering from a
   burning city.
3. **bk03/athena-eagle.png** — The moment of revelation: Athena departing as
   a sea-eagle over the banquet's edge, every Pylian face astonished, Nestor's
   cup halted halfway to his mouth; the bird already half out of frame.
4. **bk03/heifer-gilding.png** — The smith Laerces gilding the heifer's
   horns before sacrifice: close composition, craftsman's tongs and hammer,
   the animal's patient head, gold leaf catching light (terracotta-gold
   accent), women with the lustral basin behind.
5. **bk03/chariot-to-sparta.png** — The plain road at dusk: Telemachus and
   Peisistratus small in an open chariot, dust-line behind them, mountains
   ahead; enormous sky, the day's last light.
## BOOK IV — 7 plates (Gemini app workflow)

Cast: Menelaus, Helen, Nestor (mentioned only, no plate), Peisistratus,
Telemachus, and — inline only, no sheet — Antinous and Penelope's household
(Eurycleia, Medon; Penelope herself needs her existing sheet).

### The seven scenes

**1 — double-wedding.jpeg** *(opener, no anchor)*
> A gold-lit megaron mid-feast, wide and warm: a double wedding — son and
> daughter both being married the same night. Long tables, garlands, a bard
> with a lyre in the middle distance, two tumblers spinning through a
> cleared space to music. At the open threshold, small and travel-dusty,
> two young men hesitate before entering — Telemachus from his sheet in his
> plain cream tunic, and Peisistratus from his sheet in his chestnut-brown
> riding tunic, both road-worn against the gold room. Nobody has noticed
> them yet. Warmth and noise pulling against two hesitant strangers.

**2 — helen-recognizes.jpeg**
> Interior, the same hall, quieter. Helen from her sheet entering from a side
> chamber, an attendant behind her carrying the wheeled silver work-basket,
> the golden distaff wound with violet wool laid across it. Helen has
> stopped mid-step, her eyes fixed across the room on Telemachus's face —
> the likeness has just landed on her. Menelaus from his sheet sits at the
> table mid-sentence, gesturing, still unaware of what she's seeing.
> Telemachus, seated, hasn't noticed her look yet either. The whole plate
> turns on one woman's arrested eyes.

**3 — nepenthe.jpeg**
> Close plate, warm firelight. Helen from her sheet, seen from the side and
> slightly behind, her hand tipping a small dark phial over a wide gleaming
> wine-bowl, a single drop just leaving the lip of the phial. Her face is
> turned three-quarters away, unreadable — not furtive, not tender, simply
> unreadable. Faint warped reflections of the hall's firelight in the
> wine's surface. Everything else in soft shadow. Quiet and a little
> uncanny: a private, competent act of mercy or control, and the reader
> cannot tell which.

**4 — proteus-wrestling.jpeg** *(bigBeat — full-bleed page)*
> Blinding noon on open sand. Menelaus from his sheet and three companions,
> crudely disguised in raw sealskins, gripping an old bearded man from all
> sides as he transforms under their hands — mid-change, genuinely strange:
> one arm still human, the shoulder already sprouting bark and leaves like a
> young tree, the lower body shifting into a coil of serpent, the face
> caught between an old man's and a lion's. Ranked along the tideline behind
> them, dozens of true seals lie motionless, watching like an audience.
> Hard white light, hard black shadows, no softness anywhere. Grip and
> endurance are the whole subject — hold on, don't let go.

**5 — penelope-threshold.jpeg**
> Ithaca, interior. Penelope — a queen of forty-two, dark hair parted at the
> centre and gathered low, wearing a long moss-olive-green chiton and a pale
> sage-green veil pushed back off her hair for now — sunk down onto the
> stone threshold of her own chamber, unable to sit in a proper chair, her
> back against the doorframe, knees drawn up, one hand pressed flat to the
> stone beside her. Two or three maids kneel and hover near her, one with a hand
> half-raised and unable to finish the gesture of comfort. The doorway's
> straight verticals box her in on both sides — she is framed by her own
> house. Muted, cold light. The news has just landed and no one has moved
> yet.

**6 — dream-sister.jpeg** *(bigBeat — full-bleed page)*
> Night, Penelope's bedchamber. Penelope from her sheet asleep, turned on
> her side, one arm loose over the edge of the bed. Bending over her, close
> and gentle, a translucent female shape — the dream-phantom of her sister,
> visible faintly through to the dark wall behind it, one hand raised near
> Penelope's shoulder in reassurance, not quite touching. The room's real
> darkness presses in around the one pale, softly glowing figure. No
> special effects beyond the transparency itself — restrained, tender,
> a little eerie.

**7 — ambush-set.jpeg** *(bigBeat — full-bleed page)*
> Night at sea, oily calm black water, no moon. A long dark ship sliding out
> from Ithaca's shore under oars, no sail raised, moving low and quiet.
> Twenty armed men crouch aboard, spears and shields bundled flat and kept
> low rather than raised — deliberately inconspicuous. Antinous, described
> only (no reference sheet needed here — keep him distant and in shadow, a
> terracotta-red hem just visible at the stern, the one warm note in an
> otherwise cold, colourless plate), stands at the steering oar. Ahead in
> the dark, barely visible, a low rocky island waits in the strait. Tension
> through stillness and quiet, not action — a trap being set, not sprung.

### After generating

Save into `img/bk04/`, then:

```
python3 data/prepare_plates.py img/bk04/*.jpeg
python3 data/verify_plates.py bk04
python3 data/build_illustrated.py
```

Plates 4, 6, 7 are `bigBeat` full-bleed pages. All 7 anchors were validated
against the real paragraphs of `seeds/modern.md` before this manifest was
written.

### BOOK IV — second pass, 4 more plates (density fix)

Book IV is the longest book in the first half (8,419 words) and shipped with
only 7 plates — 1,202 words each, roughly 3× sparser than Book I. Mapping the
plate anchors against the paragraphs found two long unillustrated runs: paras
24–38 (2,622 words, a third of the book, held under a single sticky image)
and paras 14–22 (1,883 words). These four plates close both gaps and bring
the book to 765 words/plate, in band with Books III and V.

Anchors validated at paras 4, 19, 27, 34 — unique, ascending, no collision
with the existing seven. Sheets needed: `odysseus` is not in any of them;
upload `telemachus`, `menelaus`, `antinous`, `eurymachus`.

**8 — sparta-wealth.jpeg**
> The great high-roofed hall of Sparta seen wide, blazing with worked metal:
> bronze catching the light down the length of the echoing room, gold, amber,
> silver and ivory on the walls and fittings. Telemachus from the sheet, the
> beardless young man in a plain cream tunic, is leaning close to another
> young man to whisper, his face tilted up, openly staggered by the room.
> Menelaus from the sheet — red-gold hair and beard, steel-grey robe, gold
> circlet — has caught the remark and is turning toward them with a wry,
> tired expression. The wealth is the subject and it should feel *heavy*
> rather than joyful: this is a house that was paid for by a long war.

**9 — lion-and-fawns.jpeg**
> Homer's simile, drawn straight, with no human figures at all. A lion's
> thicket-lair in dry mountain scrub. Bedded down in the hollow of it, small
> and unaware, two newborn spotted fawns curled asleep. Returning along the
> ridge above, still at a distance but unmistakably coming — a big lion,
> heavy-shouldered, head low. The doe is far off on the grassy slope beyond,
> grazing, oblivious, facing away. Hard noon light, bleached ochre and olive
> scrub, deep shadow in the lair. Utterly still. Dread arriving on its own
> schedule — the plate must be quiet, and it must be obvious how it ends.

**10 — agamemnon-falls.jpeg** *(bigBeat — full-bleed page)*
> The aftermath, not the act. A long feasting-hall at night after a
> massacre: benches overturned, a great table knocked askew, cups and mixing
> bowls scattered and rolling, spilled wine running dark across the floor
> stones and pooling. Not a single body shown — the hall is empty of figures
> entirely. On the far wall, thrown huge and distorted by guttering torches,
> the shadows of standing armed men. In the very foreground, close and
> sharp, a single ox-goad or butcher's implement lying where it fell, and
> beside it an overturned cup. Cold, silent, and completely still. The
> violence has already happened and everyone who did it has gone.
>
> No blood on bodies, no wounds, no corpses — the wine on the floor carries
> it. This is Homer's own comparison (a man cut down at the manger like an
> ox) rendered as an emptied room.

**11 — suitors-at-games.jpeg**
> Bright hard midday in front of a great house — a hard scene change: after
> pages in Sparta we are back in Ithaca and the tone drops. On a levelled
> ground, a loose crowd of well-dressed young men throwing the discus and
> casting hunting-spears, lounging, laughing, entirely at ease on property
> that is not theirs. Set apart from the rest and seated, two figures from
> the sheets: Antinous in his deep terracotta-red himation with the heavy
> gold armband, and Eurymachus in pale grey-blue, clean-shaven. A third man
> is approaching them and has just spoken; both have turned, and their faces
> have changed. Antinous's red is the only strong colour in the plate and
> should pull the eye immediately. Insolence caught at the exact moment it
> curdles into alarm.

## BOOK V — 7 plates (Gemini app workflow)

**New character sheet needed first: Calypso.** Paragraph already in the pack
under "Ogygia and Scheria" — paste PREAMBLE v3 + that paragraph + the
colour lock, save as `img/characters/calypso.jpeg`.

Odysseus's existing sheet carries the whole book otherwise. Consider a
fresh Gemini thread for this book — Calypso's sea-teal is close to some of
the cooler blues used for night scenes in Book IV, worth keeping visually
distinct from what's already in-thread.

### The seven scenes

**1 — calypso-cave.jpeg** *(opener, no anchor)*
> A great sea-cave seen from just outside its mouth. Cedar and citron
> smoke drifting out, a vine heavy with grape-clusters trained over the
> arch, four clear springs running near each other through a meadow of
> violets and wild celery. Just landing at the threshold, Hermes: an
> ageless young man, quick and light, short belted cloud-grey tunic, low
> winged sandals, a slim golden wand in hand. Inside, glimpsed past him in
> shadow, a beautiful woman with long dark hair braided with tiny white
> shells, in a flowing sea-teal gown, singing at a golden loom. Lush and
> paradisal — and closed, self-contained, a world sealed off from the sea.

**2 — shore-grief.jpeg**
> A rocky point at the island's edge. A weathered bearded man in a
> grey-blue tunic and olive cloak sits with his back to the viewer, knees
> drawn up, staring out at an empty, enormous horizon of grey sea. The
> lush green island fills the frame behind him, ignored, out of focus. No
> ship anywhere on the water. He sits exactly where he sits every day.
> Vast loneliness through scale: a small figure, an immense empty sea.

**3 — raft-building.jpeg**
> Craftsman's plate, precise and loving. A bearded man in a plain tunic,
> sleeves pushed up, kneeling beside a half-built raft on wooden rollers —
> twenty felled logs, some already trimmed square, auger holes bored and
> pegged, the frame taking shape with real carpentry logic. Wood shavings
> curl on the ground. A little apart, a woman in a sea-teal gown
> approaches carrying folded cloth for a sail. Bright open-air daylight.
> The plate should read like an actual boat-plan someone could learn from.

**4 — poseidon-sees.jpeg** *(bigBeat — full-bleed page)*
> Seen from just behind and above a god's shoulder, high on dark mountains.
> A powerful weathered hand, storm-grey, gripping a tall bronze trident,
> gathering clouds from the sky with the other. Far below and small, an
> enormous curved grey-green sea, and on it one tiny raft under one small
> square sail — barely visible, the entire subject of the god's attention.
> The scale gap between the god's hand and the raft is the whole point.
> No face needed; just the hand, the trident, the gathering weather, and
> the impossibly small target far below.

**5 — raft-wrecked.jpeg** *(bigBeat — full-bleed page)*
> Violent grey chaos at sea. A raft's timbers scattering apart like
> loose kindling on a huge dark wave, ropes trailing, the mast at a broken
> angle. A bearded man in the water, mid-fall, one arm flung wide, having
> just lost his grip on the steering oar — caught at the exact instant of
> falling, not yet underwater. No other figures. Hard cold spray, heavy
> grey-green water, no horizon visible. Genuine peril, not stylised.

**6 — ino-veil.jpeg**
> Rough grey sea, calmer than the wreck but still heavy swells. A pale
> web-footed seabird has just broken the surface beside the exhausted
> swimming man — mid-transformation, one wing still becoming a woman's
> pale arm, offering out a small folded length of shimmering cloth toward
> him. He is barely afloat, gripping a single loose plank of the wrecked
> raft, hollow-eyed with exhaustion, reaching for the cloth uncertainly.
> Cold light, heavy water, an uncanny rescue rather than a triumphant one.

**7 — leaf-bed.jpeg** *(bigBeat — full-bleed page)*
> Seen from directly above, like a burial or a planting. A salt-crusted,
> naked-shouldered man curled on his side asleep in a hollow between two
> olive trees grown from a single root, their branches interlocked
> overhead. He is nearly buried in a deep drift of fallen dry leaves,
> only his face, one shoulder and a curled hand visible above them. Warm
> ochre-brown leaf tones against cool dawn-grey ground. Tender, exhausted,
> ambiguous — could be a grave, could be a seed underground. No nudity;
> the leaves and the angle cover him completely below the shoulder.

### After generating

Save into `img/bk05/`, then:

```
python3 data/prepare_plates.py img/bk05/*.jpeg
python3 data/verify_plates.py bk05
python3 data/build_illustrated.py
```

All 7 anchors were validated against the real paragraphs of `seeds/modern.md`
before this manifest was written. Plates 4, 5, 7 are `bigBeat` full-bleed
pages.

## BOOK VI — 5 plates

1. **bk06/dream-visit.png** — Athena as a girl-friend leaning over sleeping
   Nausicaa like a breath of wind, the two handmaids asleep at the shining
   doorposts; moonlight geometry.
2. **bk06/wagon-day.png** — The mule wagon piled with laundry rattling down
   to the river, Nausicaa driving, girls running alongside; bright morning,
   the one carefree plate in the whole set.
3. **bk06/ball-scream.png** — The ball hanging over the deep eddy, girls
   mid-shriek scattering — and at the bush-line a wild salt-crusted man
   rising with a leafy branch held before him; comic terror, exactly poised.
4. **bk06/artemis-still.png** — Nausicaa standing her ground alone, feet
   planted, chin level, while her handmaids flee along the spits of shore;
   Odysseus kneeling at a careful distance, hands open, the space between
   them the whole subject.
5. **bk06/follow-behind.png** — The road to town at sunset: the wagon ahead,
   Odysseus walking deliberately far behind with the handmaids, the grove of
   Athena's poplars coming up on the roadside; propriety as composition —
   everything held apart.

## BOOK VII — 4 plates

1. **bk07/mist-walk.png** — Odysseus walking unseen through the evening
   town inside Athena's mist — rendered as a man-shaped clear space through
   which harbor and ships show slightly bent; Phaeacians passing oblivious.
2. **bk07/palace-threshold.png** — The bronze threshold of Alcinous: gold
   doors, silver lintel, the gold and silver watchdogs of Hephaestus flanking;
   Odysseus a small weathered figure pausing before all that radiance.
3. **bk07/orchard.png** — The deathless orchard: pear on pear, apple on
   apple, grapes in every stage at once — blossom, ripening, harvest —
   in a single impossible panorama; two springs threading through.
4. **bk07/knees-of-arete.png** — The hall falling silent: Odysseus emerged
   from the dissolving mist, arms around Queen Arete's knees, ash of the
   hearth on his hands; Alcinous half-risen, old Echeneus mid-gesture,
   every cup stopped.

## BOOK VIII — 10 plates (Gemini app workflow)

**No new character sheets needed.** Upload three clean sheets: `alcinous`,
`arete` (background only, one plate), `odysseus`, plus `demodocus` and
`nausicaa`. All five already exist. Five sheets is the most this edition has
needed at once — if the thread starts drifting, drop `arete`, which appears
in one plate and only as a seated figure.

Book VIII is the bard's book: three of Demodocus's songs, the games, and
Odysseus breaking down twice in public. The structural rhyme worth
protecting in the art is **plate 3 and plate 10** — the same man, the same
cloak-over-the-head gesture, the first time hidden from everyone but
Alcinous, the last time undone completely. Generate them in the same
session so the cloak, the posture and the light match; they are the beginning
and end of one movement.

### SETUP (paste once, after uploading the 5 sheets)

> I am illustrating a serious literary edition of Homer's Odyssey for adult
> readers. I have uploaded 5 character model sheets. They are: (1) Alcinous,
> king of the Phaeacians — an older bearded man in a deep sea-blue robe with
> a gold border, a thin gold circlet, carrying a tall staff of office;
> (2) Arete, his queen — a middle-aged woman in a deep plum mantle over a
> cream gown, grey-streaked dark hair, a grave steady gaze, often with a
> distaff and spindle; (3) Demodocus, the blind court singer — an older man
> in a pale-grey robe with a tortoiseshell lyre, his eyes closed and
> unscarred, never with a blindfold or damaged eyes; (4) Nausicaa, the
> Phaeacian princess, about sixteen — a girl in a pale sea-foam chiton with
> a simple braid, often barefoot; (5) Odysseus — a weathered bearded man in
> an olive-green cloak over a grey-blue tunic, short curled beard.
>
> When a scene names one of these people, draw them exactly as their sheet
> shows them: same face, same build, same garments, same colours. This
> matters more than anything else in the image — a reader must recognise
> them across a hundred pictures.
>
> Two colour rules that hold for every image in this conversation. Deep
> terracotta-red is reserved for a different character who does not appear
> in this book, so use it only as a rare small accent — a jar, a column
> band, firelight — never for clothing. And where a scene calls for purple,
> keep it clearly purple (violet, wine-dark), never drifting toward red.
>
> STYLE, for every image in this conversation: illustration for a serious
> literary edition of an ancient epic, in the tradition of Charles Keeping,
> Barry Moser and Alan Lee. Clean confident dark ink linework over flat,
> soft watercolour washes on lightly textured paper. Restrained Aegean
> palette — pale blue-grey, cream, sun-bleached limestone, olive and moss
> green, muted teal. Minimal rendering, no gradients, no glow, no
> photorealism, no anime, no 3D, nothing cute or sentimental. Grave,
> unhurried, adult: stillness rather than spectacle, but never sanitised —
> this poem holds grief, captivity and killing, and the pictures must be
> able to hold them too. Archaic Mycenaean material culture: long ships with
> a single square sail, bronze tripods, geometric-pattern hems, megaron
> halls with a central hearth and red-banded columns, wooden benches, clay
> amphorae. Figures at a composed middle distance, faces readable but rarely
> close-up.
>
> Every image is square 1:1. No lettering of any kind anywhere in any image:
> no caption, no title, no label, no speech balloon, no signature, no
> watermark, no panel border and no frame.
>
> Reply "ready" and nothing else. I will send scenes one at a time.

### The ten scenes (paste one per turn)

**1 — launch-escort.jpeg** *(opener, no anchor)*
> Morning on a stone-built harbour. Fifty-two young men hauling a black ship
> down into deep water on rollers — mast being stepped, white sail spread,
> oars being fitted into leather slings, all of it purposeful and orderly.
> Beyond, a polished-stone assembly-place set back from the shore. Crisp
> early light, long shadows, cool Aegean blues and stone-greys. A working
> plate: competence and preparation, nobody in distress. The ship is the
> promise the whole book turns on.

**2 — demodocus-seated.jpeg**
> A blind singer in a pale-grey robe seated on a silver-studded chair set
> against a tall painted pillar, in the middle of a crowded feast. A
> tortoiseshell lyre hangs on a peg just above his head; a herald's hand is
> guiding the singer's reaching fingers to it. Beside him a small table, a
> basket, a cup of wine. His eyes are closed and unscarred, his face lifted
> slightly. The feasters around him are already turning toward him. Warm
> interior light. The dignity of the man is the subject.

**3 — cloak-over-head.jpeg** *(bigBeat — full-bleed page)*
> A crowded bright feasting-hall, everyone leaning happily toward an unseen
> singer at frame-left. At the near end of the table, alone in the middle
> of all that cheer, a weathered bearded man in an olive-green cloak has
> pulled a great purple cloak up over his head with both hands and hidden
> his face in it — shoulders locked, only his jaw and beard showing beneath
> the hem. One older man in a sea-blue robe with a gold border, seated
> beside him, has turned his head and is looking directly at him: the only
> person in the room who has noticed. Everyone else is laughing. The
> loneliness of grief inside a party. No visible tears — the hiding is the
> whole image.

**4 — footrace.jpeg**
> A dusty flat plain, a marked turning-post, a field of young runners flat
> out at full stride with dust boiling up behind them, one clearly ahead and
> pulling further away. Low camera, close to the ground, so the dust and the
> legs dominate. Bright hard daylight, ochre dust against a pale sky. Pure
> kinetic sport — no crowd detail needed, just speed and distance opening up.

**5 — the-discus.jpeg**
> A stone discus caught in mid-flight, close to the viewer and slightly
> blurred with speed, humming past. In the middle ground a weathered bearded
> man in an olive-green cloak at the end of a full spinning throw —
> follow-through uncoiled, cloak still swinging out around him, his weight
> still turning. All around, seated Phaeacian spectators are flinching and
> ducking to the ground under the rush of the stone. Far in the background,
> tiny, the marks of all the previous throws — and the new one landing well
> beyond them all. The gap between the marks is the point.

**6 — gods-in-doorway.jpeg** *(bigBeat — full-bleed page)*
> **Framed as the bard's song made visible — a scene inside a scene.** Give
> the whole image a decorative inset border, like a panel woven into cloth
> or inlaid in metal, so it reads as something being sung rather than
> something happening.
>
> Inside the border: a smith's house with a bronze floor. Filling the
> doorway, crowded shoulder to shoulder, a group of male gods roaring with
> laughter — one gripping a tall trident, one with a slim golden wand and
> winged sandals, one young and golden with a bow; they are doubled over,
> slapping each other, pointing. In the near foreground, seen only as a
> dark silhouetted back and shoulders, a broad lame smith stands leaning on
> the doorpost watching them. What they are all looking at is at the far
> side of the room and is **almost entirely obscured** — a fine golden net,
> fine as spiderweb, catching the light, drawn taut over a low couch, with
> only the glint of the net and a suggestion of shape beneath it. The
> laughing faces in the doorway are the subject; the couch is small, distant,
> and covered. Comic, scandalous, elegant. No nudity, no bodies visible —
> the joke is entirely on the faces in the doorway.

**7 — ball-dance.jpeg**
> Two young dancers on a cleared, leveled dancing-floor. One is bent far
> back, arm extended, having just hurled a deep purple ball straight up
> toward high shadowy clouds; the other is airborne, fully off the ground,
> body arched, catching it before his feet touch down. Around them a ring of
> young men standing and beating time, hands raised. Late-afternoon light,
> long shadows across the swept floor. Joy and physical skill — the one
> weightless plate in the book.

**8 — nausicaa-farewell.jpeg**
> A young girl of about sixteen in a pale sea-foam chiton, hair in a simple
> braid, standing very still against the painted doorpost of a great hall,
> one hand resting on the stone. Some distance from her, mid-hall, a
> weathered bearded man in a fresh olive-green cloak, bathed and formal,
> has stopped and turned back to face her. A wide, deliberate gap of empty
> polished floor between them. Neither is reaching toward the other.
> Servants moving in the far background, oblivious. Formality holding
> something unspoken in place — the distance between the two figures carries
> the entire emotional weight.

**9 — wooden-horse.jpeg**
> Night, inside a walled city. An enormous wooden horse standing in an open
> square, ropes still slung around it, torchlight raking up its flank from
> below. On the plain beyond the walls, small and far, the glow of huts
> burning and ships pulling away from a dark shore. **Cutaway or shadowed
> interior**: within the horse's belly, ranks of armed men sitting shoulder
> to shoulder in the dark, absolutely still, waiting — faces lit only by
> what little light comes through the planking. Dread held completely still.
> No violence in frame; the horror is entirely in the waiting.

**10 — widow-simile.jpeg** *(bigBeat — full-bleed page)*
> **Homer's own simile made image — two layers in one plate.**
>
> Foreground, solid and fully rendered: a weathered bearded man seated at a
> feast, head bowed, one hand over his eyes, tears on his cheeks, a great
> purple cloak fallen from his head into his lap. Beside him an older man in
> a sea-blue robe with a gold border, leaning in, watching him with concern.
>
> Behind and above him, ghost-faint, drained of colour, painted as if it
> were smoke rising off the feast-fire: a burning city wall, and a woman
> flung across the body of a fallen soldier, arms around him, mouth open in a
> cry — while behind her, indistinct figures drive her away with the butts of
> their spears. She and the weeping man should occupy the same vertical axis
> of the composition, so the two griefs read as one line. Her figure is
> pale, translucent, unmistakably a vision, not an event in the room.
>
> No blood, no wounds, no nudity. The pity is the subject.

### After generating

Save into `img/bk08/`, then:

```
python3 data/prepare_plates.py img/bk08/*.jpeg
python3 data/verify_plates.py bk08
python3 data/build_illustrated.py
```

All 10 anchors were validated against the real paragraphs of `seeds/modern.md`
before this manifest was written — unique substrings, ascending paragraph
order (2, 3, 5, 7, 11, 16, 17, 21, 24, 25 of 27). Plates 3, 6, 10 are
`bigBeat` full-bleed pages. Plate 1 is the unanchored opener and carries the
book's first three paragraphs.

**Note on the terracotta budget**: the purple ball in plate 7 and the purple
cloak in plates 3 and 10 must stay clearly *purple*, not drifting to
terracotta-red — that is Antinous's reserved signature. He does not appear in
Book VIII, but the colour needs to stay findable for Books XVI–XXII. Check
`verify_plates.py bk08` red% after installing.

---

*Next batches (Books IX–XXIII) on request — same structure, written
alongside each book's finished modern translation.*

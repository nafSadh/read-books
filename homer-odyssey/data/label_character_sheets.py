#!/usr/bin/env python3
"""Stamp character name + signature onto each reference sheet.

Reads the clean sheets in img/characters/<slug>.jpeg and writes labelled
copies to img/characters/labeled/<slug>.jpeg — a cream caption band added
below the art with the character's name, role, and reserved signature.

The labelled set is a contact sheet for the human: use it to keep track of
which file is who. Prefer attaching the CLEAN sheet when prompting an image
model — burnt-in text in a reference image tends to leak lettering into the
generated scene (three of the first-batch sheets already show this).

Caption data lives in CHARACTERS below and must stay in sync with the
signature table in data/illustration-prompts.md.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "img" / "characters"
OUT = SRC / "labeled"

BASK = "/System/Library/Fonts/Supplemental/Baskerville.ttc"
INK = (58, 52, 45)
MUTED = (122, 112, 98)

# slug: (display name, role line, signature line)
CHARACTERS = {
    "odysseus": (
        "ODYSSEUS",
        "King of Ithaca, absent twenty years",
        "olive-green cloak · short curled beard · scar above the right knee",
    ),
    "telemachus": (
        "TELEMACHUS",
        "His son, nineteen years old",
        "cream-white tunic · clean-shaven · no cloak, no ornament",
    ),
    "penelope": (
        "PENELOPE",
        "Queen of Ithaca, Odysseus' wife",
        "moss-olive chiton · pale sage veil lifted near the cheek",
    ),
    "athena-mentes": (
        "MENTES",
        "Taphian sea-chieftain — Athena in disguise (male)",
        "slate-blue cloak · tall bronze-tipped spear · pale grey eyes",
    ),
    "athena-mentor": (
        "MENTOR (ATHENA)",
        "Elderly Ithacan — Athena in disguise",
        "dull ochre mantle · plain staff · upright, vigorous bearing",
    ),
    "mentor-real": (
        "MENTOR (THE REAL MAN)",
        "Old friend of Odysseus, an ordinary Ithacan",
        "plain grey-green mantle · SHORT white beard · stooped · no staff",
    ),
    "athena-divine": (
        "ATHENA",
        "The goddess in her own form",
        "white and gold · aegis · crested helmet pushed back · spear",
    ),
    "eurycleia": (
        "EURYCLEIA",
        "Household nurse; nursed Odysseus as a child",
        "taupe-brown shawl · very old and stooped · carries a torch",
    ),
    "antinous": (
        "ANTINOUS",
        "Ringleader of the suitors",
        "deep terracotta-red himation · heavy gold armband · black curls",
    ),
    "eurymachus": (
        "EURYMACHUS",
        "Second leader of the suitors",
        "pale grey-blue himation · clean-shaven · thin gold shoulder-pin",
    ),
    "halitherses": (
        "HALITHERSES",
        "Aged Ithacan seer",
        "brown-grey mantle · upright · chest-length beard · tall staff",
    ),
    "nestor": (
        "NESTOR",
        "King of Pylos, the oldest living hero",
        "deep saffron-gold robe · full white beard · two-handled golden cup",
    ),
    "peisistratus": (
        "PEISISTRATUS",
        "Nestor's youngest son; travels with Telemachus",
        "chestnut-brown riding tunic · first dark beard · driving reins",
    ),
    "aegyptius": (
        "AEGYPTIUS",
        "Oldest man of the Ithacan assembly",
        "all pale cream · bent double · short stick held in both hands",
    ),
}


def paper_colour(im: Image.Image) -> tuple[int, int, int]:
    """Modal colour of the four corner patches — the sheet's paper cream."""
    w, h = im.size
    k = max(8, w // 40)
    px = []
    for box in ((0, 0, k, k), (w - k, 0, w, k),
                (0, h - k, k, h), (w - k, h - k, w, h)):
        px += list(im.crop(box).get_flattened_data())
    return Counter(px).most_common(1)[0][0]


def fit(text: str, path: str, index: int, max_w: int, start: int) -> ImageFont.FreeTypeFont:
    """Largest size at or below `start` whose rendering fits max_w."""
    size = start
    while size > 8:
        f = ImageFont.truetype(path, size, index=index)
        if f.getbbox(text)[2] <= max_w:
            return f
        size -= 1
    return ImageFont.truetype(path, 8, index=index)


def label(slug: str) -> Path:
    name, role, sig = CHARACTERS[slug]
    im = Image.open(SRC / f"{slug}.jpeg").convert("RGB")
    w, h = im.size
    bg = paper_colour(im)

    band = int(w * 0.170)
    pad = int(w * 0.05)
    inner = w - 2 * pad

    out = Image.new("RGB", (w, h + band), bg)
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)

    # hairline rule separating art from caption
    d.line([(pad, h + int(band * 0.10)), (w - pad, h + int(band * 0.10))],
           fill=MUTED, width=max(1, w // 900))

    f_name = fit(name, BASK, 1, inner, int(w * 0.058))
    f_role = fit(role, BASK, 2, inner, int(w * 0.030))
    f_sig = fit(sig, BASK, 0, inner, int(w * 0.026))

    y = h + int(band * 0.22)
    for text, font, colour, gap in ((name, f_name, INK, 0.34),
                                    (role, f_role, MUTED, 0.20),
                                    (sig, f_sig, INK, 0.0)):
        d.text((w // 2, y), text, font=font, fill=colour, anchor="ma")
        y += int(band * gap)

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{slug}.jpeg"
    out.save(dest, "JPEG", quality=92, subsampling=0)
    return dest


if __name__ == "__main__":
    missing = [s for s in CHARACTERS if not (SRC / f"{s}.jpeg").exists()]
    if missing:
        raise SystemExit(f"missing clean sheets: {', '.join(sorted(missing))}")
    for slug in CHARACTERS:
        p = label(slug)
        print(f"  {p.relative_to(REPO)}  ({Image.open(p).size[0]}x{Image.open(p).size[1]})")
    print(f"{len(CHARACTERS)} labelled sheets written to {OUT.relative_to(REPO)}/")

#!/usr/bin/env python3
"""Mechanical checks on a book's plate set, before visual review.

    python3 data/verify_plates.py bk01

Checks each plate named in data/illustrated_plates.json:

- present on disk, and actually a JPEG (the first Book I batch arrived as
  .png files that were really JPEGs, which breaks content-type on a server)
- square, since the illustrated reader's side-by-side layout is chosen by
  aspect ratio and the active set is 1:1
- large enough to survive a full-bleed bigBeat page
- terracotta-red budget, as a proxy for the reserved-signature rule: a plate
  full of red usually means the model dressed extra men in Antinous's colour

None of this can see composition, character likeness, or whether the model
drew a woman where the text says a man. Those need eyes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
MIN_EDGE = 1000


def red_pct(im: Image.Image) -> float:
    px = list(im.convert("RGB").get_flattened_data())
    red = [p for p in px if p[0] - p[1] > 55 and p[0] - p[2] > 55 and p[0] > 110]
    return 100 * len(red) / len(px)


def main(key: str) -> int:
    manifest = json.loads((REPO / "data" / "illustrated_plates.json").read_text(encoding="utf-8"))
    entry = manifest.get(key)
    if entry is None:
        print(f"no manifest entry for {key}")
        return 1
    book_dir = entry.get("dir", key) if isinstance(entry, dict) else key
    plates = entry.get("plates", []) if isinstance(entry, dict) else entry

    problems = []
    print(f"{'plate':<26} {'size':>11}  {'red%':>5}  notes")
    for p in plates:
        f = REPO / "img" / book_dir / p["file"]
        name = p["file"]
        if not f.exists():
            print(f"{name:<26} {'MISSING':>11}")
            problems.append(f"{name}: missing")
            continue
        raw = f.read_bytes()[:2]
        im = Image.open(f)
        w, h = im.size
        notes = []
        if raw != b"\xff\xd8":
            notes.append("NOT A JPEG")
            problems.append(f"{name}: not a JPEG despite the extension")
        if w != h:
            notes.append(f"not square (r={w / h:.2f})")
            problems.append(f"{name}: {w}x{h} is not 1:1")
        if min(w, h) < MIN_EDGE:
            notes.append(f"small (<{MIN_EDGE}px)")
            problems.append(f"{name}: {w}x{h} too small for a full-bleed page")
        r = red_pct(im)
        if r > 6 and name != "the-feast.jpeg":
            notes.append("heavy red — check no one but Antinous wears it")
        if p.get("bigBeat"):
            notes.append("bigBeat")
        if p.get("splashOnly"):
            notes.append("splashOnly")
        print(f"{name:<26} {w}x{h:<6} {r:5.2f}  {', '.join(notes)}")

    print()
    if problems:
        print(f"{len(problems)} problem(s):")
        for x in problems:
            print(f"  - {x}")
    else:
        print("mechanical checks pass — visual review still required")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "bk01"))

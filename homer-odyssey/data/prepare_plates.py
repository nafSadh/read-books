#!/usr/bin/env python3
"""Trim printed borders off a plate, square it, and resample it up to 2048.

    python3 data/prepare_plates.py img/bk02/*.jpeg
    python3 data/prepare_plates.py --dry-run img/bk02/*.jpeg

The generator sometimes returns a plate matted inside a frame — a cream
margin, a hairline rule, a dark band, or several nested. That matting is
part of the JPEG, so the reader treats it as picture: it shows up as an
inset image with dead space around it, and on a full-bleed page it reads
as a mistake. This finds the real edge of the artwork and cuts to it.

Trimming happens in passes. One pass samples the outer ring, then eats
inward while each row or column stays close to that colour and internally
flat. Nested matting therefore needs several passes, each re-sampling the
new edge — a cream margin and the dark rule inside it are different
colours and never come off together. TRIM_CAP bounds the total so a plate
whose art genuinely runs pale to the edge cannot be eaten alive.

On upscaling, plainly: this is Lanczos resampling plus a light unsharp
pass, not super-resolution. It makes a 1024 plate sit correctly next to a
2048 one and print without visible pixel edges. It does not add detail
that was never generated. A plate that matters should be generated at
2048 rather than rescued here.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageFilter

TARGET = 2048
TRIM_CAP = 0.12      # never remove more than this fraction of a side, total
FLATNESS = 24        # max spread within a row/col for it to count as matting.
                      # JPEG grain on an off-white matte alone can spread ~15;
                      # 14 was tight enough that real borders were missed —
                      # nepenthe.jpeg's top row spread 15 on blue and the
                      # whole trim silently no-opped on the very first check.
NEARNESS = 26        # max distance from the sampled border colour
MAX_PASSES = 4


def _line(px, w, h, side, i):
    if side == "top":    return [px[x, i] for x in range(0, w, max(1, w // 220))]
    if side == "bottom": return [px[x, h - 1 - i] for x in range(0, w, max(1, w // 220))]
    if side == "left":   return [px[i, y] for y in range(0, h, max(1, h // 220))]
    return [px[w - 1 - i, y] for y in range(0, h, max(1, h // 220))]


def _flat(line):
    """True if every channel varies little along the line."""
    return all(max(p[c] for p in line) - min(p[c] for p in line) <= FLATNESS
               for c in range(3))


def _near(line, ref):
    avg = [sum(p[c] for p in line) / len(line) for c in range(3)]
    return sum(abs(avg[c] - ref[c]) for c in range(3)) <= NEARNESS * 3


def trim_border(im: Image.Image) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """Cut concentric matting. Returns the cropped image and pixels removed per side."""
    removed = {"top": 0, "bottom": 0, "left": 0, "right": 0}
    for _ in range(MAX_PASSES):
        w, h = im.size
        px = im.load()
        cap_x, cap_y = int(w * TRIM_CAP), int(h * TRIM_CAP)
        cuts = {}
        for side in ("top", "bottom", "left", "right"):
            limit = cap_y if side in ("top", "bottom") else cap_x
            limit -= removed[side]
            ref = _line(px, w, h, side, 0)
            if not _flat(ref):
                cuts[side] = 0
                continue
            ref_avg = [sum(p[c] for p in ref) / len(ref) for c in range(3)]
            n = 0
            while n < limit:
                line = _line(px, w, h, side, n)
                if _flat(line) and _near(line, ref_avg):
                    n += 1
                else:
                    break
            cuts[side] = n
        if not any(cuts.values()):
            break
        im = im.crop((cuts["left"], cuts["top"], w - cuts["right"], h - cuts["bottom"]))
        for k in cuts:
            removed[k] += cuts[k]
    return im, (removed["left"], removed["top"], removed["right"], removed["bottom"])


def square(im: Image.Image) -> Image.Image:
    w, h = im.size
    if w == h:
        return im
    s = min(w, h)
    return im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))


def process(path: Path, dry: bool) -> str:
    im = Image.open(path).convert("RGB")
    w0, h0 = im.size
    im, cut = trim_border(im)
    w1, h1 = im.size
    im = square(im)
    w2, h2 = im.size
    note = ""
    if w2 < TARGET:
        im = im.resize((TARGET, TARGET), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=58, threshold=3))
        note = f" -> resampled {w2}->{TARGET}"
    elif w2 != TARGET:
        im = im.resize((TARGET, TARGET), Image.LANCZOS)
        note = f" -> {w2}->{TARGET}"
    if not dry:
        im.save(path, "JPEG", quality=93, subsampling=0)
    trimmed = f"trim L{cut[0]} T{cut[1]} R{cut[2]} B{cut[3]}" if any(cut) else "no border"
    sq = "" if (w1, h1) == (w2, h2) else f", squared {w1}x{h1}->{w2}x{h2}"
    return f"{path.name:<26} {w0}x{h0}  {trimmed}{sq}{note}"


if __name__ == "__main__":
    args = sys.argv[1:]
    dry = "--dry-run" in args
    files = [Path(a) for a in args if not a.startswith("--")]
    if not files:
        raise SystemExit(__doc__)
    for f in files:
        print(process(f, dry))
    if dry:
        print("\n(dry run — nothing written)")

#!/usr/bin/env python3
"""Tile the labelled character sheets into one cast sheet.

Writes img/characters/cast-sheet.jpeg — all twelve labelled sheets on one
cream page, grouped by role rather than alphabetically, with a row heading
for each group.

This is an index, not a substitute for the individual sheets. At twelve-up
each character is a twelfth of the canvas, so an image model reading it gets
far less detail per face than it does from a single 2048px sheet. Upload the
individual sheets when you want fidelity; upload this when you want one file
that establishes who exists and who is who.

Depends on label_character_sheets.py having been run first.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "img" / "characters" / "labeled"
OUT = REPO / "img" / "characters" / "cast-sheet.jpeg"

BASK = "/System/Library/Fonts/Supplemental/Baskerville.ttc"
PAPER = (247, 243, 232)
INK = (58, 52, 45)
MUTED = (122, 112, 98)

CELL_W = 1024  # per-cell width; 4 across → 4096px page

ROWS = [
    ("THE HOUSE OF ODYSSEUS",
     ["odysseus", "penelope", "telemachus", "eurycleia"]),
    ("ATHENA, HER DISGUISES, AND THE MAN SHE IMITATES",
     ["athena-divine", "athena-mentes", "athena-mentor", "mentor-real"]),
    ("THE SUITORS, AND THE ELDERS OF ITHACA",
     ["antinous", "eurymachus", "halitherses", "aegyptius"]),
    ("PYLOS — BOOKS III–IV, XV",
     ["nestor", "peisistratus"]),
]


def main() -> None:
    missing = [s for _, row in ROWS for s in row if not (SRC / f"{s}.jpeg").exists()]
    if missing:
        raise SystemExit(f"missing labelled sheets: {', '.join(missing)}\n"
                         f"run: python3 data/label_character_sheets.py")

    cells = {s: Image.open(SRC / f"{s}.jpeg").convert("RGB") for _, r in ROWS for s in r}
    # every sheet is the same aspect, so one scaled height serves all
    ratio = max(im.height / im.width for im in cells.values())
    cell_h = int(CELL_W * ratio)

    gap = int(CELL_W * 0.035)
    head_h = int(CELL_W * 0.085)
    margin = int(CELL_W * 0.06)
    title_h = int(CELL_W * 0.20)

    page_w = margin * 2 + CELL_W * 4 + gap * 3
    page_h = (margin * 2 + title_h
              + len(ROWS) * (head_h + cell_h) + gap * (len(ROWS) - 1))

    page = Image.new("RGB", (page_w, page_h), PAPER)
    d = ImageDraw.Draw(page)

    f_title = ImageFont.truetype(BASK, int(CELL_W * 0.095), index=1)
    f_sub = ImageFont.truetype(BASK, int(CELL_W * 0.036), index=2)
    f_head = ImageFont.truetype(BASK, int(CELL_W * 0.046), index=1)

    d.text((page_w // 2, margin), "THE ODYSSEY", font=f_title, fill=INK, anchor="ma")
    d.text((page_w // 2, margin + int(CELL_W * 0.115)),
           "character reference — fourteen sheets, Books I–III",
           font=f_sub, fill=MUTED, anchor="ma")

    y = margin + title_h
    for heading, slugs in ROWS:
        d.text((margin, y), heading, font=f_head, fill=MUTED, anchor="la")
        rule_y = y + int(head_h * 0.72)
        d.line([(margin, rule_y), (page_w - margin, rule_y)],
               fill=MUTED, width=max(1, page_w // 1800))
        y += head_h
        for i, slug in enumerate(slugs):
            im = cells[slug].resize((CELL_W, cell_h), Image.LANCZOS)
            page.paste(im, (margin + i * (CELL_W + gap), y))
        y += cell_h + gap

    page.save(OUT, "JPEG", quality=88, subsampling=0)
    print(f"Wrote {OUT.relative_to(REPO)} ({page_w}x{page_h}, "
          f"{OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()

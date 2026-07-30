#!/usr/bin/env python3
"""Build illustrated.html — flip-book illustrated modern-prose edition.

Reads seeds/modern.md and data/illustrated_plates.json, emits a JSON payload
of blocks per book (text paragraphs and plates interleaved at their anchors);
the template's JS paginates blocks into flippable pages at runtime. Plates
always get a full page. Books without plates still get their full text.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import parse_md_seed  # noqa: E402

REPO = Path(__file__).resolve().parent.parent


def jpeg_size(path: Path):
    """Width/height from JPEG SOF marker (stdlib only). Returns (w, h) or None."""
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return (w, h)
        i += 2 + seg_len
    return None

data = parse_md_seed(REPO / "seeds" / "modern.md")
manifest = json.loads((REPO / "data" / "illustrated_plates.json").read_text(encoding="utf-8"))

books = []
illustrated = 0
for b in data["books"]:
    num, roman = b["num"], b["roman"]
    key = f"bk{num:02d}"
    entry = manifest.get(key, [])
    # manifest entry is either a plain list of plates, or {"dir": ..., "plates": [...]}
    # so a book can point at an alternate image set (e.g. the square-format one)
    if isinstance(entry, dict):
        book_dir = entry.get("dir", key)
        plates = list(entry.get("plates", []))
        # optional: paragraph substrings that should start a fresh page
        breaks = list(entry.get("pageBreaks", []))
    else:
        book_dir = key
        plates = list(entry)
        breaks = []
    if not (REPO / "img" / book_dir).is_dir():
        plates = []
    if plates:
        illustrated += 1
    def img_block(p):
        f = REPO / "img" / book_dir / p["file"]
        if not f.exists():
            # A manifest entry can run ahead of the art (a plate still being
            # generated). Emitting the block anyway puts a broken image in the
            # reader, so skip it and say so — the book just reads text-only
            # there until the file lands.
            print(f"WARN {book_dir}: no file for {p['file']} — plate skipped")
            return None
        dims = jpeg_size(f)
        blk = {"t": "img", "src": f"img/{book_dir}/{p['file']}",
               "cap": p["caption"], "portrait": bool(p.get("portrait"))}
        if p.get("splashOnly"):
            blk["splashOnly"] = True
        if p.get("bigBeat"):
            blk["bigBeat"] = True
        if dims:
            blk["r"] = round(dims[0] / dims[1], 3)
        return blk

    blocks = []

    def add_img(p):
        blk = img_block(p)
        if blk is not None:
            blocks.append(blk)

    for p in [p for p in plates if p.get("anchor") is None]:
        add_img(p)
    pending = [p for p in plates if p.get("anchor")]
    for para in b["paragraphs"]:
        # Plates land BEFORE the paragraph they match, not after. Art is
        # sticky — it stays on screen until the next plate — so a plate
        # placed after its own paragraph is already showing the previous
        # scene while you read this one, and only catches up on the
        # paragraph that follows. Inserting before means an anchor reads as
        # "this is the paragraph this plate illustrates".
        for p in [p for p in pending if p["anchor"] in para]:
            add_img(p)
            pending.remove(p)
        blk = {"t": "p", "x": para}
        for s in list(breaks):
            if s in para:
                blk["brk"] = True
                breaks.remove(s)
        blocks.append(blk)
    for p in pending:
        print(f"WARN {book_dir}: anchor not found: {p['anchor'][:50]!r}")
        add_img(p)
    for s in breaks:
        print(f"WARN {book_dir}: pageBreak not found: {s[:50]!r}")
    books.append({"num": num, "roman": roman, "plates": len(plates), "blocks": blocks})

payload = json.dumps({"books": books}, ensure_ascii=False, separators=(",", ":"))
payload = payload.replace("</script>", "<\\/script>")

tpl = (REPO / "data" / "illustrated-template.html").read_text(encoding="utf-8")
assert "__IDATA__" in tpl
out = REPO / "illustrated.html"
out.write_text(tpl.replace("__IDATA__", payload), encoding="utf-8")
print(f"Wrote {out} ({out.stat().st_size:,} bytes) — {illustrated}/24 books have plates")

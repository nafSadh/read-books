#!/usr/bin/env python3
"""Build all homer-iliad/*.html reader variants from seeds/*.json + data/*-template.html.

Each template renders ONE book at a time client-side rather than pre-rendering
all 24 books x 3 translations as static HTML — a full epic is too large for
that (a single continuous DOM of ~19,000 verse-line <p> elements per
translation caused multi-million-pixel pages that failed to paint on
deep-link/scroll-jump). Instead this script assembles the three seed files
into one JS object literal and substitutes it for each template's
__CONTENT__ placeholder; the browser renders only the current book's
~30-100 paragraphs into the DOM at a time.

Idempotent: safe to re-run; overwrites the generated HTML files. Templates
not present on disk are skipped (so this script works before all variants
have templates written).
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent  # homer-iliad/
SEEDS = REPO / "seeds"
DATA = REPO / "data"

EDITIONS = ["butler", "pope", "cowper"]

# (template filename in data/, output filename in the book root)
VARIANTS = [
    ("reader-template.html", "reader.html"),
    ("theater-template.html", "theater.html"),
    ("mobile-template.html", "mobile.html"),
    ("fullbleed-template.html", "fullbleed.html"),
    ("pdf-template.html", "pdf-reader.html"),
]


def build_content() -> str:
    combined = {}
    for key in EDITIONS:
        data = json.loads((SEEDS / f"{key}.json").read_text(encoding="utf-8"))
        assert data["book_count"] == 24, f"{key}: expected 24 books, got {data['book_count']}"
        assert len(data["books"]) == 24, f"{key}: expected 24 book entries, got {len(data['books'])}"
        combined[key] = data

    # compact separators keep the payload smaller; ensure_ascii=False preserves
    # accented characters and curly quotes as literal UTF-8 rather than \uXXXX escapes.
    content = json.dumps(combined, ensure_ascii=False, separators=(",", ":"))
    # A raw "</script>" inside a JSON string would terminate the script tag early.
    return content.replace("</script>", "<\\/script>")


def main() -> None:
    content = build_content()
    built = 0
    for tpl_name, out_name in VARIANTS:
        tpl_path = DATA / tpl_name
        if not tpl_path.exists():
            print(f"skip {tpl_name} (not written yet)")
            continue
        tpl = tpl_path.read_text(encoding="utf-8")
        assert "__CONTENT__" in tpl, f"{tpl_name} missing __CONTENT__ placeholder"
        out_text = tpl.replace("__CONTENT__", content)
        out_path = REPO / out_name
        out_path.write_text(out_text, encoding="utf-8")
        print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes)")
        built += 1
    print(f"{built}/{len(VARIANTS)} variants built")


if __name__ == "__main__":
    main()

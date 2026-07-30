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

EDITIONS = ["butler", "pope", "cowper", "murray", "greek", "modern"]

# (template filename in data/, output filename in the book root)
VARIANTS = [
    ("reader-template.html", "reader.html"),
    ("theater-template.html", "theater.html"),
    ("mobile-template.html", "mobile.html"),
    ("fullbleed-template.html", "fullbleed.html"),
    ("pdf-template.html", "pdf-reader.html"),
]


ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
         "XXI", "XXII", "XXIII", "XXIV"]

PLACEHOLDER = (
    "This book has not been translated yet. The modern-prose edition is in "
    "progress, translated book by book directly from the Greek. Switch to "
    "Butler, Pope, Cowper, or Murray above to keep reading in the meantime, "
    "or use the Greek tab to see the original text of this book."
)


def parse_md_seed(path) -> dict:
    """Parse a seeds/*.md edition file into the same dict shape as the JSON seeds.

    Format: YAML-ish frontmatter (translator, form, ...), then '## Book <roman>'
    sections. An optional leading blockquote ('> ...') is the translator's
    argument. Prose editions use blank-line-separated paragraphs; verse/greek
    editions use one poem-line per file line. A body of '*[not yet translated]*'
    becomes the reader placeholder paragraph."""
    text = path.read_text(encoding="utf-8")
    meta = {}
    body = text
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        for line in fm.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    form = meta.get("form", "prose")

    books = []
    sections = body.split("\n## ")[1:]  # drop preamble before first book heading
    for sec in sections:
        heading, _, rest = sec.partition("\n")
        roman = heading.replace("Book", "").strip()
        num = ROMAN.index(roman) + 1
        raw_lines = rest.splitlines()

        # optional argument blockquote
        arg_lines = []
        i = 0
        while i < len(raw_lines) and (raw_lines[i].startswith(">") or (not raw_lines[i].strip() and not arg_lines)):
            if raw_lines[i].startswith(">"):
                arg_lines.append(raw_lines[i].lstrip("> ").rstrip())
            i += 1
        argument = None
        if arg_lines:
            argument = "\n".join(arg_lines).strip()
            argument = "\n\n".join(p.replace("\n", " ") for p in argument.split("\n\n"))
        rest_body = "\n".join(raw_lines[i:])

        book = {"num": num, "roman": roman, "argument": argument or None}
        if form == "prose":
            paras = [p.strip().replace("\n", " ") for p in rest_body.split("\n\n") if p.strip()]
            if paras == ["*[not yet translated]*"]:
                paras = [PLACEHOLDER]
            book["paragraphs"] = paras
        else:
            book["lines"] = [ln for ln in (l.strip() for l in rest_body.splitlines()) if ln]
        books.append(book)
    books.sort(key=lambda b: b["num"])
    return {
        "translator": meta.get("translator", ""),
        "translator_years": meta.get("translator_years", ""),
        "publication_year": int(meta.get("publication_year", 0)),
        "form": form,
        "source": meta.get("source", ""),
        "source_url": meta.get("source_url"),
        "epic": meta.get("epic", "odyssey"),
        "book_count": len(books),
        "books": books,
    }


def build_content() -> str:
    combined = {}
    for key in EDITIONS:
        md_path = SEEDS / f"{key}.md"
        if md_path.exists():
            data = parse_md_seed(md_path)
        else:
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

    # study.html: separate data payload (seeds/study.json, built by build_study_data.py)
    study_tpl = DATA / "study-template.html"
    study_seed = SEEDS / "study.json"
    if study_tpl.exists() and study_seed.exists():
        tpl = study_tpl.read_text(encoding="utf-8")
        assert "__STUDY__" in tpl, "study-template.html missing __STUDY__ placeholder"
        payload = study_seed.read_text(encoding="utf-8").replace("</script>", "<\\/script>")
        out_path = REPO / "study.html"
        out_path.write_text(tpl.replace("__STUDY__", payload), encoding="utf-8")
        print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

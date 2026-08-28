#!/usr/bin/env python3
"""Build pdf-reader.html — one quatrain per page in a PDF-viewer shell.

Sibling of `build_reader.py`; imports its seed loading, transliteration and
numbering. One quatrain per page card, with its apparatus set below, inside a
Chrome-PDF-viewer-style shell (toolbar, thumbnail sidebar, zoom).

Position lives in the URL hash as `#p-N` — the page ordinal within the current
edition, matching the house convention for paged formats.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_reader import ROOT, build_ctx, build_payload, render_template  # noqa: E402

TPL = Path(__file__).parent / "pdf-template.html"
OUT = ROOT / "pdf-reader.html"


def main():
    ctx = build_ctx()
    payload = build_payload(ctx, with_gloss=True)
    out_text = render_template(TPL, OUT, payload)

    eds = payload['editions']
    summary = ' + '.join(f"{eds[k]['count']}" for k in payload['order'])
    total = sum(eds[k]['count'] for k in payload['order'])
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(out_text):,} bytes, "
          f"{summary} = {total} quatrains")


if __name__ == '__main__':
    main()

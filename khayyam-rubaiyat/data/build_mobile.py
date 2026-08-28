#!/usr/bin/env python3
"""Build mobile.html — one quatrain per screen, swipe or tap to move.

Sibling of `build_reader.py`; imports its seed loading, transliteration and
numbering. Carries the facing gloss (like fullbleed) but sets it *below* the
quatrain rather than on a verso, since a phone has no facing page.

Position lives in the URL hash as `#q-<edition>-N`, the same deep-link form
reader.html and theater.html use, so a link opens the same quatrain in any of
the three.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_reader import ROOT, build_ctx, build_payload, render_template  # noqa: E402

TPL = Path(__file__).parent / "mobile-template.html"
OUT = ROOT / "mobile.html"


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

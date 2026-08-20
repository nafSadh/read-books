#!/usr/bin/env python3
"""Build theater.html — one quatrain at a time on a dark stage.

Sibling of `build_reader.py`; imports its seed loading, transliteration and
numbering. The stage carries the quatrain alone, so the payload is built
without the facing gloss that fullbleed.html uses.

Position lives in the URL hash as `#q-<edition>-N`, the same deep-link form
reader.html already parses, so a link copied out of one opens the other on
the same quatrain.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_reader import ROOT, build_ctx, build_payload, render_template  # noqa: E402

TPL = Path(__file__).parent / "theater-template.html"
OUT = ROOT / "theater.html"


def main():
    ctx = build_ctx()
    payload = build_payload(ctx, with_gloss=False)
    out_text = render_template(TPL, OUT, payload)

    eds = payload['editions']
    summary = ' + '.join(f"{eds[k]['count']}" for k in payload['order'])
    total = sum(eds[k]['count'] for k in payload['order'])
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(out_text):,} bytes, "
          f"{summary} = {total} quatrains")


if __name__ == '__main__':
    main()

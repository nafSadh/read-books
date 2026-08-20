#!/usr/bin/env python3
"""Build fullbleed.html — two-page spread, one quatrain per recto.

Sibling of `build_reader.py`; imports its seed loading, Persian matching,
transliteration, numbering and detail fragments so both formats render the
same text from the same helpers.

Spread layout (desktop):

    spread 0  cover
    spread 1  verso: blank        recto: title page
    spread 2  verso: colophon     recto: contents (groups of 10)
    spread N  verso: facing gloss recto: quatrain N-3

The verso is the facing apparatus, in the manner of Heron-Allen's 1898
facing-page edition: the Persian source with transliteration, the scholarly
notes, and the alternate historical translations. Editions without a matched
Persian source (Nicolas) get a blank verso with a printer's ornament.

On phones the spread collapses to the recto alone, with the gloss set below
the quatrain.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_reader import ROOT, build_ctx, build_payload, render_template  # noqa: E402

TPL = Path(__file__).parent / "fullbleed-template.html"
OUT = ROOT / "fullbleed.html"


def main():
    ctx = build_ctx()
    payload = build_payload(ctx, with_gloss=True)
    out_text = render_template(TPL, OUT, payload)

    eds = payload['editions']
    summary = ' + '.join(f"{eds[k]['count']}" for k in payload['order'])
    total = sum(eds[k]['count'] for k in payload['order'])
    glossed = sum(1 for k in payload['order'] for q in eds[k]['quatrains'] if q.get('gloss'))
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(out_text):,} bytes, "
          f"{summary} = {total} quatrains ({glossed} with a facing gloss)")


if __name__ == '__main__':
    main()

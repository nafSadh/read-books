#!/usr/bin/env python3
"""Build mobile.html — one passage per screen, swipe or tap to move.

Sibling of `payload.py`, which knows how to read the source JSON and shape a
passage. Greek and the annotation apparatus are toggles rather than columns:
a phone has no room to set them side by side.

Position lives in the URL hash as `#m-B.N` — the passage's own Leopold id, so
the link is stable across viewports (unlike fullbleed's viewport-dependent
page ordinal).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from payload import PROJECT_DIR, SCRIPT_DIR, build_payload, render_template  # noqa: E402

TPL = os.path.join(SCRIPT_DIR, 'mobile-template.html')
OUT = os.path.join(PROJECT_DIR, 'mobile.html')


def main():
    payload = build_payload(with_detail=True, with_greek=True)
    out = render_template(TPL, OUT, payload)
    print('Wrote {}: {:,} bytes, {} passages across {} books'.format(
        os.path.basename(OUT), len(out), len(payload['passages']), len(payload['books'])))


if __name__ == '__main__':
    main()

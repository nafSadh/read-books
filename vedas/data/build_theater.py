#!/usr/bin/env python3
"""Build mobile.html — one sukta per screen, sized for a phone.

Scripts and translations are chips in a bottom sheet rather than columns: at
phone width there is no room to set five scripts side by side the way
reader.html does. Position lives in the hash as #s-<veda>-<num>.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from payload import PROJECT_DIR, SCRIPT_DIR, build_payload, render_template  # noqa: E402

TPL = os.path.join(SCRIPT_DIR, 'theater-template.html')
OUT = os.path.join(PROJECT_DIR, 'theater.html')

def main():
    p = build_payload()
    out = render_template(TPL, OUT, p)
    print('Wrote {}: {:,} bytes, {} suktas / {} mantras'.format(
        os.path.basename(OUT), len(out), len(p['suktas']), p['mantraCount']))

if __name__ == '__main__':
    main()

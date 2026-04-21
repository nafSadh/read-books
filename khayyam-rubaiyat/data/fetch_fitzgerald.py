#!/usr/bin/env python3
"""Parse FitzGerald's Rubaiyat (1st + 5th editions) from Project Gutenberg #246.

Output: seeds/fitzgerald.json with both editions.
Run: python3 data/fetch_fitzgerald.py
"""
import re, json, urllib.request
from pathlib import Path

SRC_URL = "https://www.gutenberg.org/cache/epub/246/pg246.txt"
CACHE = Path("/tmp/rubaiyat/pg246.txt")
OUT = Path(__file__).parent.parent / "seeds" / "fitzgerald.json"

_R = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}

def roman(s):
    total, prev = 0, 0
    for c in reversed(s):
        v = _R[c]
        total += -v if v < prev else v
        prev = v
    return total

def fetch():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    if not CACHE.exists():
        CACHE.write_bytes(urllib.request.urlopen(SRC_URL).read())
    return CACHE.read_text(encoding='utf-8').splitlines()

def parse_section(lines, start, end):
    """Parse lines[start:end] into list of {num, lines} quatrains."""
    roman_re = re.compile(r'^([IVXLCDM]+)\.\s*$')
    quatrains = []
    cur_num, cur_lines = None, []
    for raw in lines[start:end]:
        stripped = raw.strip()
        m = roman_re.match(stripped)
        if m:
            if cur_num is not None:
                quatrains.append({'num': cur_num, 'lines': cur_lines})
            cur_num = roman(m.group(1))
            cur_lines = []
        elif cur_num is not None and stripped:
            # Verse lines are indented in the source; section headers
            # (KUZA-NAMA, *****, etc.) are not. Skip the latter.
            if raw.startswith(' '):
                cur_lines.append(stripped)
    if cur_num is not None and cur_lines:
        quatrains.append({'num': cur_num, 'lines': cur_lines})
    return quatrains

def find_line(lines, text, start=0):
    for i in range(start, len(lines)):
        if lines[i].strip() == text:
            return i
    raise ValueError(f"not found: {text!r}")

def main():
    lines = fetch()
    # Edition boundaries. "*****" inside an edition is a section break (Kuza-Nama
    # etc.), not an edition end; only TAMAM (SHUD) marks the real end.
    first_start = find_line(lines, 'First Edition')
    first_end = find_line(lines, 'TAMAM SHUD.', first_start)
    fifth_start = find_line(lines, 'Fifth Edition')
    fifth_end = find_line(lines, 'TAMAM.', fifth_start)

    first = parse_section(lines, first_start + 1, first_end)
    fifth = parse_section(lines, fifth_start + 1, fifth_end)

    assert len(first) == 75, f"expected 75 quatrains in 1st ed, got {len(first)}"
    assert len(fifth) == 101, f"expected 101 quatrains in 5th ed, got {len(fifth)}"
    for q in first + fifth:
        assert len(q['lines']) == 4, f"quatrain {q['num']} has {len(q['lines'])} lines: {q['lines']}"

    out = {
        'source': 'Project Gutenberg #246',
        'translator': 'Edward FitzGerald',
        'editions': {
            'first': {'year': 1859, 'count': 75, 'quatrains': first},
            'fifth': {'year': 1889, 'count': 101, 'quatrains': fifth},
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT.relative_to(Path.cwd())}: {len(first)} + {len(fifth)} = {len(first)+len(fifth)} quatrains")

if __name__ == '__main__':
    main()

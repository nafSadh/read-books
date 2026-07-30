#!/usr/bin/env python3
"""Merge a reviewed draft translation into seeds/modern.md.

Usage: python3 data/merge_modern_book.py <roman> <draft-path>
Replaces the '*[not yet translated]*' body of '## Book <roman>' with the
draft's paragraphs. Refuses to overwrite a book that already has content.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MD = REPO / "seeds" / "modern.md"

def main():
    roman, draft_path = sys.argv[1], sys.argv[2]
    draft = Path(draft_path).read_text(encoding="utf-8").strip()
    assert draft and not draft.startswith("#"), "draft should be bare paragraphs"
    n_paras = len([p for p in draft.split("\n\n") if p.strip()])

    text = MD.read_text(encoding="utf-8")
    needle = f"## Book {roman}\n\n*[not yet translated]*"
    if needle not in text:
        sys.exit(f"ERROR: no untranslated section '## Book {roman}' found (already merged?)")
    text = text.replace(needle, f"## Book {roman}\n\n{draft}", 1)
    MD.write_text(text, encoding="utf-8")
    print(f"merged Book {roman}: {n_paras} paragraphs")

if __name__ == "__main__":
    main()

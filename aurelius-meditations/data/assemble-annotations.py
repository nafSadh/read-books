#!/usr/bin/env python3
"""
Assembles JSON annotation files into reader.html.
Converts plain <p><span class="med-num">X.</span>...</p> passages
into annotated <div class="med-passage">...</div> blocks.

Usage: python3 assemble-annotations.py [--dry-run]
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
READER = os.path.join(SCRIPT_DIR, '..', 'reader.html')
ANNOT_DIR = os.path.join(SCRIPT_DIR, 'annotations')

DETAIL_BTN = '<button class="med-detail-btn" aria-label="Details"><svg width="14" height="14" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="1" width="10" height="10" rx="1.5"/><line x1="3.5" y1="4" x2="8.5" y2="4"/><line x1="3.5" y1="6" x2="8.5" y2="6"/><line x1="3.5" y1="8" x2="6.5" y2="8"/></svg></button>'

BOOK_FILES = {
    5: 'book-05.json',
    6: 'book-06.json',
    7: 'book-07.json',
    8: 'book-08.json',
    9: 'book-09.json',
    10: 'book-10.json',
    11: 'book-11.json',
    12: 'book-12.json',
}


def add_proper_noun_spans(text, proper_nouns):
    if not proper_nouns:
        return text
    orig_nouns = [pn for pn in proper_nouns if pn.get('context') == 'in_original']
    for pn in orig_nouns:
        name = pn['name']
        if f'class="pn">{name}' in text:
            continue
        escaped = re.escape(name)
        # Match name not inside HTML tags
        pattern = re.compile(r'(?<!<[^>])\b(' + escaped + r')\b(?![^<]*>)')
        replaced = [False]
        def replacer(m):
            if replaced[0]:
                return m.group(0)
            replaced[0] = True
            tip = pn.get('tip', '')
            url_part = f' <a href="{pn["url"]}">Wikipedia</a>' if pn.get('url') else ''
            return f'<span class="pn">{m.group(0)}<span class="pn-tip">{tip}{url_part}</span></span>'
        text = pattern.sub(replacer, text)
    return text


def build_annotated_passage(original_p, annotation):
    num = annotation['num']
    # Remove <p> wrapper and med-num span
    body = re.sub(r'^\s*<p>', '', original_p)
    body = re.sub(r'</p>\s*$', '', body)
    escaped_num = re.escape(num)
    body = re.sub(rf'<span class="med-num">{escaped_num}\.?</span>', '', body).strip()

    # Add proper noun spans to original text
    body = add_proper_noun_spans(body, annotation.get('proper_nouns'))

    # Build notes with proper noun spans
    notes = annotation.get('notes', '')
    note_nouns = [pn for pn in annotation.get('proper_nouns', []) if pn.get('context') == 'in_notes']
    for pn in note_nouns:
        escaped = re.escape(pn['name'])
        pattern = re.compile(r'\b(' + escaped + r')\b')
        replaced = [False]
        def replacer(m, pn=pn, replaced=replaced):
            if replaced[0]:
                return m.group(0)
            replaced[0] = True
            tip = pn.get('tip', '')
            url_part = f' <a href="{pn["url"]}">Wikipedia</a>' if pn.get('url') else ''
            return f'<span class="pn">{m.group(0)}<span class="pn-tip">{tip}{url_part}</span></span>'
        notes = pattern.sub(replacer, notes)

    modern = annotation.get('modern_english', '')

    return f'''    <div class="med-passage">
    <div class="med-head">{DETAIL_BTN}<span class="med-num">{num}.</span></div>
    <div class="med-body"><div class="med-main">
    <p>{body}</p>
    </div><div class="med-detail">
      <div class="narr-section"><span class="narr-label">Modern English</span>
      <p>{modern}</p></div>
      <div class="narr-section"><span class="narr-label">Notes</span>
      <p>{notes}</p></div>
    </div></div>
    </div>'''


def main():
    dry_run = '--dry-run' in sys.argv
    with open(READER, 'r', encoding='utf-8') as f:
        html = f.read()

    total_replaced = 0

    for book_num, json_file in sorted(BOOK_FILES.items()):
        json_path = os.path.join(ANNOT_DIR, json_file)
        if not os.path.exists(json_path):
            print(f'  Skipping Book {book_num}: {json_file} not found')
            continue

        with open(json_path, 'r', encoding='utf-8') as f:
            annotations = json.load(f)

        book_replaced = 0
        for annot in annotations:
            num = annot['num']
            escaped_num = re.escape(num)
            pattern = re.compile(
                rf'([ \t]*)<p><span class="med-num">{escaped_num}\.</span>([\s\S]*?)</p>',
                re.MULTILINE
            )
            match = pattern.search(html)
            if not match:
                continue

            full_match = match.group(0)
            replacement = build_annotated_passage(full_match, annot)
            html = html.replace(full_match, replacement, 1)
            book_replaced += 1

        print(f'  Book {book_num}: {book_replaced}/{len(annotations)} passages annotated')
        total_replaced += book_replaced

    print(f'\nTotal: {total_replaced} passages converted')

    if dry_run:
        print('(dry run — no file written)')
    else:
        with open(READER, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'Written to {READER}')


if __name__ == '__main__':
    main()

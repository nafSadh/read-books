#!/usr/bin/env python3
"""Shared payload builder for the JS-rendered Meditations formats.

`assemble-reader.py` bakes the whole book into the DOM, which is right for a
scrolling reader but wrong for formats that show one passage at a time. This
module emits the same content as a JSON payload instead, so mobile.html,
theater.html and pdf-reader.html can render a single passage on demand.

The three sibling builders (`build_mobile.py`, `build_theater.py`,
`build_pdf.py`) are thin: call `build_payload()`, call `render_template()`.
One place knows how to read the source JSON and shape a passage.
"""
import html
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
JSON_PATH = os.path.join(PROJECT_DIR, 'aurelius-meditations.json')

BOOK_SUBTITLES = {
    1: 'Debts and Lessons',
    2: 'Written Among the Quadi',
    3: 'In Carnuntum',
}

ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']


def esc(t):
    return html.escape(t or '', quote=False)


def _paras(text):
    """Split a passage into <p> blocks on blank lines."""
    parts = [p.strip() for p in re.split(r'\n\s*\n', (text or '').strip()) if p.strip()]
    return ''.join('<p>' + esc(p).replace('\n', ' ') + '</p>' for p in parts)


def passage_html(p):
    """The English text (George Long, 1862)."""
    longs = p.get('long') or []
    text = ' '.join(longs) if isinstance(longs, list) else str(longs)
    return _paras(text)


def greek_html(p):
    g = p.get('greek') or ''
    return _paras(g)


def detail_html(p):
    """Modern rewrite + notes + proper-noun glosses, as one apparatus block."""
    a = p.get('annotation') or {}
    out = []
    if a.get('modern_english'):
        out.append(
            '<section class="d-sec d-modern">'
            '<h4 class="d-label">In modern English</h4>'
            + _paras(a['modern_english']) + '</section>'
        )
    if a.get('notes'):
        out.append(
            '<section class="d-sec d-notes">'
            '<h4 class="d-label">Notes</h4>'
            + _paras(a['notes']) + '</section>'
        )
    pns = a.get('proper_nouns') or []
    if pns:
        items = []
        for pn in pns:
            tip = esc(pn.get('tip', ''))
            url = pn.get('url', '')
            if url:
                tip += ' <a href="' + esc(url) + '" rel="noopener">Wikipedia</a>'
            items.append(
                '<div class="d-pn"><span class="d-pn-name">' + esc(pn.get('name', ''))
                + '</span><span class="d-pn-tip">' + tip + '</span></div>'
            )
        out.append(
            '<section class="d-sec d-pns">'
            '<h4 class="d-label">People and places</h4>' + ''.join(items) + '</section>'
        )
    return ''.join(out)


def build_payload(with_detail=True, with_greek=True):
    """One flat list of passages plus the book index.

    Flat because every one of these formats pages through passages linearly;
    `book`/`bnum` on each entry is enough to group them in a jump list.
    """
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    passages, books = [], []
    for b in data['books']:
        bnum = b['book']
        books.append({
            'n': bnum,
            'roman': ROMAN[bnum] if bnum < len(ROMAN) else str(bnum),
            'title': b.get('title') or ('Book ' + str(bnum)),
            'subtitle': BOOK_SUBTITLES.get(bnum, ''),
            'count': b.get('passage_count', len(b.get('passages', []))),
            'start': len(passages),
        })
        for p in b.get('passages', []):
            pid = p.get('id', '')
            num = pid.split('.')[-1] if '.' in pid else pid
            item = {
                'id': pid,
                'bnum': bnum,
                'num': num,
                'text': passage_html(p),
            }
            if with_greek:
                g = greek_html(p)
                if g:
                    item['greek'] = g
            if with_detail:
                d = detail_html(p)
                if d:
                    item['detail'] = d
            passages.append(item)

    return {
        'title': data.get('title', 'Meditations'),
        'author': 'Marcus Aurelius',
        'translator': 'George Long, 1862',
        'books': books,
        'passages': passages,
    }


def render_template(tpl_path, out_path, payload):
    """Substitute a JSON payload into a template's __DATA__ placeholder."""
    with open(tpl_path, 'r', encoding='utf-8') as f:
        tpl = f.read()
    assert '__DATA__' in tpl, os.path.basename(tpl_path) + ' missing __DATA__ placeholder'
    # "</" inside a <script> would close it early; JSON allows the escape.
    blob = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    out_text = tpl.replace('__DATA__', blob)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out_text)
    return out_text

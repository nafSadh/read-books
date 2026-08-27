#!/usr/bin/env python3
"""Shared payload builder for the curated-Vedas JS-rendered formats.

`reader.html` and `fullbleed.html` embed VEDAS_DATA and build their DOM from
it directly. mobile/theater/pdf-reader instead render one sukta at a time from
a JSON payload, so this module is the one place that reads the canonical data
and flattens it into a per-sukta list.

VEDAS_DATA lives inside reader.html (that file is hand-written and canonical),
so it is parsed out of there rather than duplicated.
"""
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
READER = os.path.join(PROJECT_DIR, 'reader.html')


def load_data():
    with open(READER, 'r', encoding='utf-8') as f:
        s = f.read()
    m = re.search(r'const VEDAS_DATA\s*=\s*(\{.*?\});\s*\n', s, re.S)
    if not m:
        raise SystemExit('VEDAS_DATA not found in reader.html')
    return json.loads(m.group(1))


def build_payload():
    """Flat list of suktas; each carries its mantras and its Veda/section labels."""
    data = load_data()
    vedas, suktas = [], []
    for v in data['vedas']:
        vedas.append({
            'id': v['id'],
            'title': v.get('title', ''),
            'title_en': v.get('title_en', ''),
            'start': len(suktas),
        })
        for sec in v.get('sections', []):
            for sk in sec.get('suktas', []):
                suktas.append({
                    'veda': v['id'],
                    'vedaTitle': v.get('title', ''),
                    'section': sec.get('title_bn', ''),
                    'sectionEn': sec.get('title_en', ''),
                    'num': sk.get('sukta_num'),
                    'title': sk.get('title_bn', ''),
                    'titleEn': sk.get('title_en', ''),
                    'rishi': sk.get('rishi', ''),
                    'devata': sk.get('devata', ''),
                    'chanda': sk.get('chanda', ''),
                    'noteEn': sk.get('note_en', ''),
                    'noteBn': sk.get('note_bn', ''),
                    'mantras': [{
                        'n': mt.get('num'),
                        'dv': mt.get('sa_devanagari', ''),
                        'bn': mt.get('sa_bengali', ''),
                        'iast': mt.get('transliteration', ''),
                        'mBn': mt.get('meaning_bn', ''),
                        'mEn': mt.get('meaning_en', ''),
                    } for mt in sk.get('mantras', [])],
                })
    for i, vd in enumerate(vedas):
        nxt = vedas[i + 1]['start'] if i + 1 < len(vedas) else len(suktas)
        vd['count'] = nxt - vd['start']
    return {'vedas': vedas, 'suktas': suktas,
            'mantraCount': sum(len(s['mantras']) for s in suktas)}


def render_template(tpl_path, out_path, payload):
    with open(tpl_path, 'r', encoding='utf-8') as f:
        tpl = f.read()
    assert '__DATA__' in tpl, os.path.basename(tpl_path) + ' missing __DATA__'
    blob = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    out = tpl.replace('__DATA__', blob)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out)
    return out

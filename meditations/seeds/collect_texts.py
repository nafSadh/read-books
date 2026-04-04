#!/usr/bin/env python3
"""
Collect Marcus Aurelius' Meditations in Greek + English translations.

Sources:
  - Greek (Leopold ed.): Perseus Digital Library TEI XML (CC BY-SA 4.0)
  - George Long (1862): Standard Ebooks (CC0)
  - Meric Casaubon (1634): Project Gutenberg (public domain)

Outputs per-book JSON/MD + combined files into seeds/texts/.
Uses only stdlib. Caches fetched data in /tmp/meditations_texts_cache/.

Usage:
  python3 collect_texts.py              # full run
  python3 collect_texts.py --no-cache   # ignore cache, re-fetch everything
  python3 collect_texts.py --greek-only # only collect Greek
  python3 collect_texts.py --long-only  # only collect Long
"""

import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, 'texts')
CACHE_DIR = '/tmp/meditations_texts_cache'

GREEK_XML_URL = (
    'https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/'
    'master/data/tlg0562/tlg001/tlg0562.tlg001.perseus-grc2.xml'
)
LONG_XHTML_URL = (
    'https://raw.githubusercontent.com/standardebooks/'
    'marcus-aurelius_meditations_george-long/master/src/epub/text/book-{n}.xhtml'
)

ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
         'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX',
         'XX', 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII',
         'XXVIII', 'XXIX', 'XXX', 'XXXI', 'XXXII', 'XXXIII', 'XXXIV',
         'XXXV', 'XXXVI', 'XXXVII', 'XXXVIII', 'XXXIX', 'XL', 'XLI',
         'XLII', 'XLIII', 'XLIV', 'XLV', 'XLVI', 'XLVII', 'XLVIII',
         'XLIX', 'L', 'LI', 'LII', 'LIII', 'LIV', 'LV', 'LVI', 'LVII',
         'LVIII', 'LIX', 'LX', 'LXI', 'LXII', 'LXIII', 'LXIV', 'LXV',
         'LXVI', 'LXVII', 'LXVIII', 'LXIX', 'LXX', 'LXXI', 'LXXII',
         'LXXIII', 'LXXIV', 'LXXV']

BOOK_TITLES = {
    1: 'Book I', 2: 'Book II', 3: 'Book III', 4: 'Book IV',
    5: 'Book V', 6: 'Book VI', 7: 'Book VII', 8: 'Book VIII',
    9: 'Book IX', 10: 'Book X', 11: 'Book XI', 12: 'Book XII',
}


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def ensure_dirs():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def fetch_url(url, cache_name, use_cache=True):
    """Fetch URL with disk caching."""
    cache_path = os.path.join(CACHE_DIR, cache_name)
    if use_cache and os.path.exists(cache_path):
        print(f'  [cache] {cache_name}')
        with open(cache_path, 'r', encoding='utf-8') as f:
            return f.read()
    print(f'  [fetch] {url[:80]}...')
    req = urllib.request.Request(url, headers={'User-Agent': 'read-books/1.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode('utf-8')
    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write(data)
    return data


class HTMLStripper(HTMLParser):
    """Strip HTML tags, returning plain text."""
    def __init__(self):
        super().__init__()
        self._parts = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ('a',):
            # Check if it's a footnote ref — skip its text
            for name, val in attrs:
                if name == 'epub:type' and 'noteref' in (val or ''):
                    self._skip = True
                    return
                if name == 'class' and 'noteref' in (val or ''):
                    self._skip = True
                    return

    def handle_endtag(self, tag):
        if tag == 'a':
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._parts.append(data)

    def get_text(self):
        return ''.join(self._parts).strip()


def strip_html(html_str):
    """Remove HTML tags and footnote refs, return plain text."""
    s = HTMLStripper()
    s.feed(html_str)
    return s.get_text()


def strip_tags_simple(html_str):
    """Simple tag stripper for Casaubon HTML."""
    text = re.sub(r'<[^>]+>', '', html_str)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'")
    text = re.sub(r'&[a-z]+;', '', text)
    return text.strip()


# ---------------------------------------------------------------------------
# Phase 1: Greek text from Perseus TEI XML
# ---------------------------------------------------------------------------

def parse_greek_xml(xml_text):
    """Parse Perseus TEI XML into {book_num: [{chapter, text}, ...]}."""
    # Remove namespace for easier parsing
    xml_text = re.sub(r'\sxmlns="[^"]+"', '', xml_text, count=1)
    root = ET.fromstring(xml_text)

    books = {}
    body = root.find('.//body')
    if body is None:
        print('  ERROR: no <body> in XML')
        return books

    # Structure: body > div[@type=textpart][@subtype=Book] >
    #            div[@subtype=chapter] > div[@subtype=section]
    top_div = body.find('div')
    if top_div is None:
        print('  ERROR: no top-level div')
        return books

    for book_div in top_div.findall('div'):
        book_n = book_div.get('n')
        if not book_n:
            continue
        book_num = int(book_n)
        chapters = []

        for ch_div in book_div.findall('div'):
            ch_n = ch_div.get('n')
            if not ch_n:
                continue

            # Some chapters have sub-sections, some are flat
            sections = ch_div.findall('div')
            if sections:
                # Join sub-section texts
                parts = []
                for sec in sections:
                    text = ''.join(sec.itertext()).strip()
                    if text:
                        parts.append(text)
                full_text = ' '.join(parts)
            else:
                full_text = ''.join(ch_div.itertext()).strip()

            # Clean up whitespace
            full_text = re.sub(r'\s+', ' ', full_text).strip()
            if full_text:
                chapters.append({'chapter': int(ch_n), 'text': full_text})

        books[book_num] = chapters
        print(f'    Book {book_num}: {len(chapters)} chapters')

    return books


def load_greek_cached():
    """Try to load from pre-existing /tmp/greek_meditations.json."""
    path = '/tmp/greek_meditations.json'
    if not os.path.exists(path):
        return None
    print('  [cache] Loading pre-existing greek_meditations.json')
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    # Convert from {book_str: {ch_str: text}} to {book_int: [{chapter, text}]}
    books = {}
    for book_key in sorted(raw.keys(), key=lambda x: int(x)):
        book_num = int(book_key)
        ch_dict = raw[book_key]
        chapters = []
        for ch_key in sorted(ch_dict.keys(), key=lambda x: int(x)):
            text = ch_dict[ch_key]
            if isinstance(text, str):
                chapters.append({'chapter': int(ch_key), 'text': text})
            elif isinstance(text, dict):
                # Sub-sections — join them
                parts = [text[k] for k in sorted(text.keys(), key=lambda x: int(x))]
                chapters.append({'chapter': int(ch_key), 'text': ' '.join(parts)})
        books[book_num] = chapters
        print(f'    Book {book_num}: {len(chapters)} chapters')
    return books


def collect_greek(use_cache=True):
    """Collect Greek text."""
    print('\n=== Phase 1: Greek (Leopold) ===')

    # Try pre-existing cache first
    if use_cache:
        books = load_greek_cached()
        if books:
            return books

    xml_text = fetch_url(GREEK_XML_URL, 'greek_tei.xml', use_cache)
    return parse_greek_xml(xml_text)


# ---------------------------------------------------------------------------
# Phase 2: George Long (1862) from Standard Ebooks
# ---------------------------------------------------------------------------

def parse_long_xhtml(xhtml_text, book_num):
    """Parse a Standard Ebooks XHTML file into list of passage texts."""
    passages = []

    # Extract <p> elements (skip <h2> header)
    p_pattern = re.compile(r'<p(?:\s[^>]*)?>(.+?)</p>', re.DOTALL)
    for m in p_pattern.finditer(xhtml_text):
        raw_html = m.group(1)
        text = strip_html(f'<p>{raw_html}</p>')
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            passages.append(text)

    return passages


def collect_long(use_cache=True):
    """Collect George Long translation."""
    print('\n=== Phase 2: George Long (1862) ===')
    books = {}
    for n in range(1, 13):
        url = LONG_XHTML_URL.format(n=n)
        cache_name = f'long_book_{n:02d}.xhtml'
        xhtml = fetch_url(url, cache_name, use_cache)
        passages = parse_long_xhtml(xhtml, n)
        books[n] = passages
        print(f'    Book {n}: {len(passages)} passages')
        if not use_cache:
            time.sleep(0.5)  # polite delay
    return books


# ---------------------------------------------------------------------------
# Phase 3: Casaubon (1634) from cached data
# ---------------------------------------------------------------------------

def collect_casaubon(use_cache=True):
    """Collect Casaubon translation from cached chapter data."""
    print('\n=== Phase 3: Casaubon (1634) ===')

    cache_path = '/tmp/meditations_chapters.json'
    if not os.path.exists(cache_path):
        print('  WARNING: /tmp/meditations_chapters.json not found')
        print('  Casaubon text will be empty. Run the reader build first.')
        return {}

    with open(cache_path, 'r', encoding='utf-8') as f:
        chapters = json.load(f)

    books = {}
    for ch in chapters:
        book_num = ch['num']
        html = ch['html']

        # Extract passages by splitting on med-num spans
        # Pattern: <span class="med-num">X.</span>
        parts = re.split(r'<span class="med-num">(.*?)</span>', html)
        # parts[0] is before first med-num (empty or whitespace)
        # then alternating: [num, text, num, text, ...]
        passages = []
        i = 1
        while i < len(parts) - 1:
            num_str = parts[i].rstrip('.')
            raw_html = parts[i + 1]
            # Find end of this passage (up to next <p> or end)
            text = strip_tags_simple(raw_html)
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                passages.append({'num': num_str, 'text': text})
            i += 2

        books[book_num] = passages
        print(f'    Book {book_num}: {len(passages)} passages')

    return books


# ---------------------------------------------------------------------------
# Phase 4: Align and Output
# ---------------------------------------------------------------------------

def align_books(greek_books, long_books, casaubon_books):
    """Align all translations using Greek chapter numbers as canonical."""
    all_books = []

    for book_num in range(1, 13):
        greek = greek_books.get(book_num, [])
        long = long_books.get(book_num, [])
        casaubon = casaubon_books.get(book_num, [])

        passages = []
        for i, g in enumerate(greek):
            passage = {
                'id': f'{book_num}.{g["chapter"]}',
                'greek': g['text'],
            }

            # Long: sequential alignment
            if i < len(long):
                passage['long'] = long[i]
            else:
                passage['long'] = ''

            passages.append(passage)

        # Casaubon: stored as separate list (different numbering)
        casaubon_list = []
        for c in casaubon:
            casaubon_list.append({
                'num': c['num'],
                'text': c['text'],
            })

        book_data = {
            'book': book_num,
            'title': BOOK_TITLES[book_num],
            'passage_count': len(passages),
            'passages': passages,
            'casaubon': {
                'passage_count': len(casaubon_list),
                'passages': casaubon_list,
            },
        }

        # Log alignment info
        g_count = len(greek)
        l_count = len(long)
        c_count = len(casaubon)
        status = 'OK' if g_count == l_count else f'MISMATCH (Greek={g_count}, Long={l_count})'
        print(f'  Book {book_num}: Greek={g_count}, Long={l_count}, '
              f'Casaubon={c_count} — {status}')

        all_books.append(book_data)

    return all_books


def write_book_json(book_data):
    """Write a per-book JSON file."""
    path = os.path.join(OUT_DIR, f'book-{book_data["book"]:02d}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(book_data, f, ensure_ascii=False, indent=2)
    return path


def write_book_md(book_data):
    """Write a per-book Markdown file."""
    lines = [f'# {book_data["title"]}', '']
    lines.append(f'Greek (Leopold): {book_data["passage_count"]} passages  ')
    lines.append(f'Casaubon (1634): {book_data["casaubon"]["passage_count"]} passages')
    lines.append('')

    # Greek + Long aligned passages
    lines.append('## Greek & Long (aligned)')
    lines.append('')
    for p in book_data['passages']:
        lines.append(f'### {p["id"]}')
        lines.append('')
        lines.append(f'**Greek:** {p["greek"]}')
        lines.append('')
        if p.get('long'):
            lines.append(f'**Long (1862):** {p["long"]}')
            lines.append('')
        lines.append('---')
        lines.append('')

    # Casaubon passages (separate section)
    if book_data['casaubon']['passages']:
        lines.append('## Casaubon (1634)')
        lines.append('')
        for c in book_data['casaubon']['passages']:
            lines.append(f'### {c["num"]}')
            lines.append('')
            lines.append(c['text'])
            lines.append('')
            lines.append('---')
            lines.append('')

    path = os.path.join(OUT_DIR, f'book-{book_data["book"]:02d}.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return path


def write_combined(all_books):
    """Write combined JSON and Markdown files."""
    # Combined JSON
    combined = {
        'title': 'Meditations — Marcus Aurelius',
        'sources': {
            'greek': {
                'edition': 'Leopold (1908)',
                'source': 'Perseus Digital Library',
                'license': 'CC BY-SA 4.0',
            },
            'long': {
                'translator': 'George Long',
                'year': 1862,
                'source': 'Standard Ebooks',
                'license': 'CC0 / Public Domain',
            },
            'casaubon': {
                'translator': 'Meric Casaubon',
                'year': 1634,
                'source': 'Project Gutenberg #2680',
                'license': 'Public Domain',
            },
        },
        'books': all_books,
    }
    json_path = os.path.join(OUT_DIR, 'meditations-complete.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    size_kb = os.path.getsize(json_path) / 1024
    print(f'  {json_path} ({size_kb:.0f} KB)')

    # Combined Markdown
    md_lines = [
        '# Meditations — Marcus Aurelius',
        '',
        '## Sources',
        '',
        '- **Greek**: Leopold edition (1908), Perseus Digital Library (CC BY-SA 4.0)',
        '- **Long**: George Long (1862), Standard Ebooks (CC0)',
        '- **Casaubon**: Meric Casaubon (1634), Project Gutenberg (Public Domain)',
        '',
    ]
    for book in all_books:
        md_lines.append(f'# {book["title"]}')
        md_lines.append('')
        for p in book['passages']:
            md_lines.append(f'## {p["id"]}')
            md_lines.append('')
            md_lines.append(f'**Greek:** {p["greek"]}')
            md_lines.append('')
            if p.get('long'):
                md_lines.append(f'**Long (1862):** {p["long"]}')
                md_lines.append('')
            md_lines.append('---')
            md_lines.append('')
        # Casaubon section
        if book['casaubon']['passages']:
            md_lines.append(f'### {book["title"]} — Casaubon (1634)')
            md_lines.append('')
            for c in book['casaubon']['passages']:
                md_lines.append(f'**{c["num"]}.** {c["text"]}')
                md_lines.append('')

    md_path = os.path.join(OUT_DIR, 'meditations-complete.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    size_kb = os.path.getsize(md_path) / 1024
    print(f'  {md_path} ({size_kb:.0f} KB)')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    use_cache = '--no-cache' not in args
    greek_only = '--greek-only' in args
    long_only = '--long-only' in args

    ensure_dirs()

    # Collect
    greek_books = collect_greek(use_cache)

    if greek_only:
        # Dump just Greek
        for book_num in sorted(greek_books.keys()):
            data = {
                'book': book_num,
                'title': BOOK_TITLES[book_num],
                'passage_count': len(greek_books[book_num]),
                'passages': greek_books[book_num],
            }
            path = os.path.join(OUT_DIR, f'greek-book-{book_num:02d}.json')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f'  Wrote {path}')
        return

    long_books = collect_long(use_cache)

    if long_only:
        for book_num in sorted(long_books.keys()):
            data = {
                'book': book_num,
                'title': BOOK_TITLES[book_num],
                'passage_count': len(long_books[book_num]),
                'passages': long_books[book_num],
            }
            path = os.path.join(OUT_DIR, f'long-book-{book_num:02d}.json')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f'  Wrote {path}')
        return

    casaubon_books = collect_casaubon(use_cache)

    # Align
    print('\n=== Phase 4: Align & Output ===')
    all_books = align_books(greek_books, long_books, casaubon_books)

    # Write per-book files
    print('\n=== Writing per-book files ===')
    for book in all_books:
        jp = write_book_json(book)
        mp = write_book_md(book)
        print(f'  Book {book["book"]}: {os.path.basename(jp)}, {os.path.basename(mp)}')

    # Write combined files
    print('\n=== Writing combined files ===')
    write_combined(all_books)

    # Summary
    total_greek = sum(b['passage_count'] for b in all_books)
    total_long = sum(1 for b in all_books for p in b['passages'] if p.get('long'))
    total_casaubon = sum(b['casaubon']['passage_count'] for b in all_books)
    print(f'\nDone! {total_greek} Greek passages, {total_long} Long passages, '
          f'{total_casaubon} Casaubon passages')


if __name__ == '__main__':
    main()

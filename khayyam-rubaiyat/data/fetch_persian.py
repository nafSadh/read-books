#!/usr/bin/env python3
"""Fetch Persian originals of Khayyam's rubáʿiyāt from fa.wikisource.

Source: رباعیات خیام (تصحیح فروغی و غنی) — the Foroughi-Ghani 1339/1960 critical
edition, with one wikisource subpage per quatrain. The page body embeds four
<span class="beyt"> hemistichs (2 bayts × 2 mesras) and the quatrain number.

License: CC BY-SA 4.0 (Wikimedia standard), attribution required.
Output:  seeds/persian.json
Run:     python3 data/fetch_persian.py
"""
import hashlib, json, re, time, urllib.parse, urllib.request, html
from pathlib import Path

ROOT = Path(__file__).parent.parent
SEED = ROOT / "seeds" / "persian.json"
CACHE_DIR = Path("/tmp/rubaiyat/wikisource")

EDITION_TITLE = "رباعیات خیام (تصحیح فروغی و غنی)"
API = "https://fa.wikisource.org/w/api.php"
NON_QUATRAIN_SUFFIXES = {"مقدمه", "روش تصحیح", "روش تصحیح رباعیات",
                          "فهرست رباعیات", "غلطنامه", "آثار خیام"}

BEYT_RE = re.compile(r'<span class="beyt">(.*?)</span>', re.S)
NUM_RE = re.compile(r'<div class="tiInherit"[^>]*>\s*<p>\s*([۰-۹0-9]+)\s*</p>', re.S)
TAG_RE = re.compile(r'<[^>]+>')

# Persian digits → ASCII
_PN = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
# Arabic-form letters → Persian equivalents (normalize import sources)
_NORM = str.maketrans({'ي': 'ی', 'ك': 'ک', 'ة': 'ه'})


def fetch(url: str, cache_key: str) -> bytes:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached = CACHE_DIR / cache_key
    if cached.exists():
        return cached.read_bytes()
    req = urllib.request.Request(url, headers={"User-Agent": "lib.sadh.app Rubaiyat build (https://lib.sadh.app)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    cached.write_bytes(data)
    return data


def list_quatrain_pages():
    """Enumerate all subpages of the edition via allpages, paginated."""
    titles = []
    apfrom = None
    while True:
        params = {
            'action': 'query', 'list': 'allpages',
            'apprefix': EDITION_TITLE + "/", 'aplimit': 500,
            'format': 'json',
        }
        if apfrom: params['apfrom'] = apfrom
        url = API + "?" + urllib.parse.urlencode(params)
        key = 'allpages_' + (apfrom or 'start').replace('/', '_')[:60] + '.json'
        body = fetch(url, key)
        d = json.loads(body)
        for p in d.get('query', {}).get('allpages', []):
            titles.append(p['title'])
        cont = d.get('continue', {}).get('apcontinue')
        if not cont:
            break
        apfrom = cont
    return titles


def parse_quatrain_html(html_body: str):
    num_m = NUM_RE.search(html_body)
    beyts = BEYT_RE.findall(html_body)
    if num_m is None or len(beyts) < 4:
        return None
    num_s = num_m.group(1).translate(_PN)
    num = int(num_s)
    lines = []
    for b in beyts[:4]:
        # Strip inner tags, decode entities, normalize
        text = TAG_RE.sub('', b)
        text = html.unescape(text).strip().translate(_NORM)
        # Collapse internal whitespace
        text = re.sub(r'\s+', ' ', text)
        lines.append(text)
    return {'num': num, 'lines': lines}


def fetch_quatrain(title: str):
    params = {
        'action': 'parse', 'page': title,
        'format': 'json', 'prop': 'text',
    }
    url = API + "?" + urllib.parse.urlencode(params)
    safe_key = hashlib.sha1(title.encode('utf-8')).hexdigest()[:16] + '.json'
    body = fetch(url, safe_key)
    d = json.loads(body)
    html_body = d.get('parse', {}).get('text', {}).get('*', '')
    if not html_body:
        return None
    q = parse_quatrain_html(html_body)
    if q:
        q['source_title'] = title.split('/', 1)[-1]  # last path segment = first mesra
    return q


def main():
    print(f"Listing subpages of \"{EDITION_TITLE}\" ...")
    titles = list_quatrain_pages()
    # Filter: keep only subpages that are actual quatrains (not metadata)
    good = []
    for t in titles:
        if '/' not in t: continue
        suffix = t.split('/', 1)[1]
        if suffix in NON_QUATRAIN_SUFFIXES: continue
        good.append(t)
    print(f"  {len(good)} candidate quatrain subpages (filtered from {len(titles)})")

    quatrains = []
    skipped = []
    for i, t in enumerate(good, 1):
        q = fetch_quatrain(t)
        if q is None:
            skipped.append(t)
            continue
        quatrains.append(q)
        if i % 25 == 0 or i == len(good):
            print(f"  fetched {i}/{len(good)} ({len(quatrains)} parsed ok)")
        # Gentle pacing — cached calls are instant; uncached fetch a handful per second
        if not (CACHE_DIR / (hashlib.sha1(t.encode('utf-8')).hexdigest()[:16] + '.json')).exists():
            time.sleep(0.05)

    # Deduplicate + sort by Foroughi number
    by_num = {}
    for q in quatrains:
        by_num[q['num']] = q  # later wins if duplicate
    ordered = [by_num[k] for k in sorted(by_num.keys())]

    out = {
        'source': 'fa.wikisource.org — رباعیات خیام (تصحیح فروغی و غنی)',
        'edition': 'Foroughi & Ghani, 1960',
        'license': 'CC BY-SA 4.0',
        'language': 'fa',
        'direction': 'rtl',
        'count': len(ordered),
        'quatrains': ordered,
    }
    SEED.parent.mkdir(parents=True, exist_ok=True)
    SEED.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nWrote {SEED.relative_to(ROOT)}: {len(ordered)} quatrains")
    if skipped:
        print(f"  {len(skipped)} pages skipped (no parseable body); examples: {skipped[:3]}")


if __name__ == '__main__':
    main()

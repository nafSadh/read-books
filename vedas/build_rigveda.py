#!/usr/bin/env python3
"""Build vedas/rigveda.html — compact full-Rigveda reader.

Fetches Sanskrit + English from rigveda-online.github.io (CC0 Public Domain),
transliterates Devanagari to Bengali script, and generates:
  1. vedas/rigveda.html         — self-contained compact reader
  2. vedas/seeds/rigveda-complete.json  — human-readable JSON
  3. vedas/rigveda-samhita.md   — full text as Markdown

Usage:
    python3 vedas/build_rigveda.py

First run fetches 1,028 HTML files (~10 min). Cached runs < 30s.
"""

import json, os, re, sys, time, html
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── Configuration ───────────────────────────────────────────────────
CACHE_DIR = Path("/tmp/rigveda_cache")
BASE_URL = "https://rigveda-online.github.io"
SCRIPT_DIR = Path(__file__).resolve().parent
SEEDS_DIR = SCRIPT_DIR / "seeds"
MAX_WORKERS = 12  # concurrent fetches

# Mandala → number of suktas (canonical Shakala recension)
MANDALA_SUKTA_COUNTS = {
    1: 191, 2: 43, 3: 62, 4: 58, 5: 87,
    6: 75, 7: 104, 8: 103, 9: 114, 10: 191
}
TOTAL_SUKTAS = sum(MANDALA_SUKTA_COUNTS.values())  # 1028


# ─── Devanagari → Bengali transliteration ────────────────────────────
def dev_to_bengali(text: str) -> str:
    """Transliterate Devanagari to Bengali script via Unicode offset."""
    result = []
    for ch in text:
        cp = ord(ch)
        if cp == 0x0935:       # व → ব
            result.append('\u09AC')
        elif cp == 0x0933:     # ळ → ল
            result.append('\u09B2')
        elif 0x0900 <= cp <= 0x097F:
            result.append(chr(cp + 0x0080))
        else:
            result.append(ch)
    return ''.join(result)


# ─── HTML Fetching & Parsing ─────────────────────────────────────────
def fetch_url(url: str, cache_path: Path, retries: int = 3) -> str:
    """Fetch URL with caching and retries."""
    if cache_path.exists():
        return cache_path.read_text(encoding='utf-8')

    for attempt in range(retries):
        try:
            req = Request(url, headers={'User-Agent': 'RigvedaBuilder/1.0'})
            with urlopen(req, timeout=30) as resp:
                data = resp.read().decode('utf-8')
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(data, encoding='utf-8')
            return data
        except (URLError, HTTPError, TimeoutError) as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  FAILED {url}: {e}", file=sys.stderr)
                return ""
    return ""


def parse_sukta_html(html_text: str, mandala: int, sukta: int) -> dict:
    """Parse a rigveda-online sukta HTML page into structured data."""
    if not html_text:
        return {"n": sukta, "t": "", "v": []}

    # Extract title from <h2> in navbar
    title_match = re.search(r'<h2>(.*?)</h2>', html_text)
    title = ""
    if title_match:
        raw = title_match.group(1).strip()
        # e.g., "HYMN I. AGNI." → "Agni"
        raw = re.sub(r'^HYMN\s+[IVXLCDM]+\.?\s*', '', raw, flags=re.IGNORECASE)
        raw = raw.strip('. ')
        title = raw.title() if raw else ""

    # Extract verses
    verses = []
    # Each verse is in a <div class="card ..."> block
    card_pattern = re.compile(
        r'<div\s+class="hymn-sanskrit">(.*?)</div>.*?'
        r'<div\s+class="hymn-translation-en">(.*?)</div>.*?'
        r'<div\s+class="card-footer">\s*([\d.]+)\s*</div>',
        re.DOTALL
    )

    for match in card_pattern.finditer(html_text):
        sanskrit_html = match.group(1)
        english_html = match.group(2)
        verse_ref = match.group(3).strip()

        # Extract Devanagari: get text content from <a class="sanskrit-word"> tags
        # Each <a> has: Devanagari text + <span class="transliteration-word">...</span>
        # We want just the Devanagari, not the transliteration
        devanagari_parts = []
        for word_match in re.finditer(
            r'<a\s+class="sanskrit-word"[^>]*>(.*?)</a>',
            sanskrit_html, re.DOTALL
        ):
            word_html = word_match.group(1)
            # Remove transliteration spans
            word_text = re.sub(r'<span[^>]*>.*?</span>', '', word_html, flags=re.DOTALL)
            word_text = html.unescape(word_text.strip())
            if word_text:
                devanagari_parts.append(word_text)

        # Also capture | and || separators from outside <a> tags
        # Rebuild the full verse with proper structure
        # Get all text including separators
        full_text = re.sub(r'<[^>]+>', ' ', sanskrit_html)
        full_text = html.unescape(full_text)
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        # Remove transliteration text (lowercase latin chars in parens-like context)
        # Actually, the transliteration is inside spans which we already see in word_match
        # Let's reconstruct from word list + separators

        # Simpler approach: take all non-<a> text for separators
        # and interleave with devanagari words
        sanskrit_clean = re.sub(r'<a\s+class="sanskrit-word"[^>]*>.*?</a>', '\x00', sanskrit_html, flags=re.DOTALL)
        separators = sanskrit_clean.split('\x00')

        dev_line = ""
        for i, word in enumerate(devanagari_parts):
            if i < len(separators):
                sep = re.sub(r'<[^>]+>', '', separators[i])
                sep = html.unescape(sep).strip()
                if sep and sep not in ('', ' '):
                    dev_line += sep + " "
            dev_line += word + " "
        # Add trailing separator
        if len(separators) > len(devanagari_parts):
            sep = re.sub(r'<[^>]+>', '', separators[-1])
            sep = html.unescape(sep).strip()
            if sep:
                dev_line += sep

        dev_line = dev_line.strip()
        # Normalize multiple spaces
        dev_line = re.sub(r'  +', ' ', dev_line)
        # Line break only at || (verse end / double danda), NOT at single |
        dev_line = re.sub(r'\s*\|\|\s*', ' ||\n', dev_line)
        dev_line = dev_line.strip()

        # English translation
        eng = re.sub(r'<[^>]+>', ' ', english_html)
        eng = html.unescape(eng)
        eng = re.sub(r'\s+', ' ', eng).strip()

        # Parse verse number
        parts = verse_ref.split('.')
        verse_num = int(parts[-1]) if parts else len(verses) + 1

        verses.append({
            "n": verse_num,
            "d": dev_line,
            "b": dev_to_bengali(dev_line),
            "e": eng
        })

    return {"n": sukta, "t": title, "v": verses}


# ─── Bengali Meanings Overlay ────────────────────────────────────────
def load_bengali_meanings() -> dict:
    """Load Bengali meanings from merged extraction + hand-curated seeds.

    Priority: curated (hymns.json) > merged extraction (scripts/output/).
    """
    lookup = {}

    # 1. Load merged extraction (bulk — 98.6% coverage)
    merged_path = SCRIPT_DIR / "scripts" / "output" / "rigveda_bengali_merged.json"
    if merged_path.exists():
        with open(merged_path, encoding='utf-8') as f:
            data = json.load(f)
        for mandala in data.get("mandalas", []):
            m = int(mandala["num"])
            for sukta in mandala.get("suktas", []):
                s = int(sukta["sukta_num"])
                for mantra in sukta.get("mantras", []):
                    if mantra.get("meaning_bn"):
                        key = (m, s, int(mantra["num"]))
                        lookup[key] = mantra["meaning_bn"]
        print(f"  Loaded merged Bengali: {len(lookup)} mantras")

    # 2. Overlay hand-curated (highest priority, overwrites merged)
    hymns_path = SEEDS_DIR / "hymns.json"
    curated_count = 0
    if hymns_path.exists():
        with open(hymns_path, encoding='utf-8') as f:
            data = json.load(f)
        for mandala in data.get("mandalas", []):
            m = mandala["num"]
            for sukta in mandala.get("suktas", []):
                s = sukta["sukta_num"]
                for mantra in sukta.get("mantras", []):
                    if mantra.get("meaning_bn"):
                        key = (m, s, mantra["num"])
                        lookup[key] = mantra["meaning_bn"]
                        curated_count += 1
        print(f"  Loaded curated Bengali: {curated_count} mantras (overrides merged)")

    return lookup


# ─── Main Pipeline ───────────────────────────────────────────────────
def fetch_all_suktas() -> list:
    """Fetch and parse all 1,028 sukta HTML files."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    tasks = []
    for mandala, count in sorted(MANDALA_SUKTA_COUNTS.items()):
        for sukta in range(1, count + 1):
            url = f"{BASE_URL}/{mandala}/{sukta}.html"
            cache = CACHE_DIR / f"{mandala}_{sukta}.html"
            tasks.append((mandala, sukta, url, cache))

    print(f"Fetching {len(tasks)} suktas ({MAX_WORKERS} workers)...")

    # Fetch all HTML files in parallel
    results = {}  # (mandala, sukta) → html_text
    done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {}
        for mandala, sukta, url, cache in tasks:
            fut = pool.submit(fetch_url, url, cache)
            futures[fut] = (mandala, sukta)

        for fut in as_completed(futures):
            mandala, sukta = futures[fut]
            results[(mandala, sukta)] = fut.result()
            done += 1
            if done % 100 == 0 or done == len(tasks):
                print(f"  Fetched {done}/{len(tasks)}")

    # Parse in order
    mandalas = []
    total_mantras = 0
    for m_num in sorted(MANDALA_SUKTA_COUNTS.keys()):
        suktas = []
        for s_num in range(1, MANDALA_SUKTA_COUNTS[m_num] + 1):
            html_text = results.get((m_num, s_num), "")
            parsed = parse_sukta_html(html_text, m_num, s_num)
            suktas.append(parsed)
            total_mantras += len(parsed["v"])
        mandalas.append({"n": m_num, "s": suktas})
        print(f"  Mandala {m_num}: {len(suktas)} suktas, "
              f"{sum(len(s['v']) for s in suktas)} mantras")

    print(f"\nTotal: {TOTAL_SUKTAS} suktas, {total_mantras} mantras")
    return mandalas


def overlay_bengali(mandalas: list, bn_lookup: dict) -> int:
    """Overlay Bengali meanings where available. Returns count of overlays."""
    count = 0
    for mandala in mandalas:
        for sukta in mandala["s"]:
            for verse in sukta["v"]:
                key = (mandala["n"], sukta["n"], verse["n"])
                if key in bn_lookup:
                    verse["mb"] = bn_lookup[key]
                    count += 1
    return count


def build_compact_json(mandalas: list) -> str:
    """Build compact JSON string for HTML embedding (legacy monolithic)."""
    return json.dumps({"m": mandalas}, ensure_ascii=False, separators=(',', ':'))


def build_mandala_files(mandalas: list) -> str:
    """Write per-mandala JSON files and return metadata JSON for HTML embedding."""
    data_dir = SCRIPT_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    meta = []
    for mandala in mandalas:
        # Write per-mandala data file (.json for fetch, .js for file:// fallback)
        mandala_json = json.dumps(mandala, ensure_ascii=False, separators=(',', ':'))
        out_path = data_dir / f"mandala-{mandala['n']}.json"
        out_path.write_text(mandala_json, encoding='utf-8')
        js_path = data_dir / f"mandala-{mandala['n']}.js"
        js_path.write_text(f"window._rvLoad({mandala_json});", encoding='utf-8')
        print(f"    data/mandala-{mandala['n']}.json: {len(mandala_json):,} chars")

        # Build metadata entry (titles + counts, no verse data)
        titles = [s.get("t", "") for s in mandala["s"]]
        meta.append({"n": mandala["n"], "c": len(mandala["s"]), "t": titles})

    return json.dumps(meta, ensure_ascii=False, separators=(',', ':'))


def build_readable_json(mandalas: list) -> str:
    """Build human-readable JSON with full field names."""
    readable = {
        "title": "ঋগ্বেদ সংহিতা",
        "title_en": "Rigveda Samhita",
        "source": "rigveda-online.github.io (CC0), Griffith translation (1896, public domain)",
        "mandalas": []
    }
    for mandala in mandalas:
        m = {"num": mandala["n"], "suktas": []}
        for sukta in mandala["s"]:
            s = {"sukta_num": sukta["n"], "title": sukta["t"], "mantras": []}
            for v in sukta["v"]:
                mantra = {
                    "num": v["n"],
                    "sa_devanagari": v["d"],
                    "sa_bengali": v["b"],
                    "meaning_en": v["e"]
                }
                if "mb" in v:
                    mantra["meaning_bn"] = v["mb"]
                s["mantras"].append(mantra)
            m["suktas"].append(s)
        readable["mandalas"].append(m)
    return json.dumps(readable, ensure_ascii=False, indent=2)


def build_markdown(mandalas: list) -> str:
    """Build a full Markdown document of the Rigveda."""
    lines = [
        "# ঋগ্বেদ সংহিতা — Rigveda Samhita",
        "",
        "> Complete text: Sanskrit in Bengali script & Devanagari, with Griffith English translation.",
        "> Source: rigveda-online.github.io (CC0 Public Domain)",
        "",
    ]

    for mandala in mandalas:
        lines.append(f"# Mandala {mandala['n']}")
        lines.append("")

        for sukta in mandala["s"]:
            title = f" — {sukta['t']}" if sukta['t'] else ""
            lines.append(f"## {mandala['n']}.{sukta['n']}{title}")
            lines.append("")

            for v in sukta["v"]:
                lines.append(f"### {mandala['n']}.{sukta['n']}.{v['n']}")
                lines.append("")
                lines.append(f"**{v['b']}**")
                lines.append("")
                lines.append(f"*{v['d']}*")
                lines.append("")
                lines.append(f"{v['e']}")
                if "mb" in v:
                    lines.append("")
                    lines.append(f"বাংলা: {v['mb']}")
                lines.append("")
                lines.append("---")
                lines.append("")

    return "\n".join(lines)


# ─── HTML Template ───────────────────────────────────────────────────
# Mirrors alice-in-wonderland/reader.html top bar, sidebar, theme, settings patterns exactly
HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="bn" data-theme="light-purple">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ঋগ্বেদ সংহিতা — Rigveda Samhita — Reader</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..800;1,400..800&family=IBM+Plex+Mono:wght@400;500&family=Jost:wght@300;400;500;600&family=Roboto+Slab:wght@300;400;500&family=Noto+Serif+Bengali:wght@400;500;600;700&family=Noto+Serif+Devanagari:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{min-height:100vh;transition:background-color .3s,color .3s;overflow-x:hidden;-webkit-font-smoothing:antialiased}

:root{
  --font-serif:'EB Garamond',Georgia,serif;--font-sans:'Jost',-apple-system,sans-serif;
  --font-slab:'Roboto Slab',Georgia,serif;--font-mono:'IBM Plex Mono',monospace;
  --font-bn:'Noto Serif Bengali','Tiro Bangla',serif;--font-dev:'Noto Serif Devanagari',serif;
  --font-body:var(--font-bn);--font-size:17px;--line-height:1.75;--content-width:960px;
}
[data-theme="light-azure"]{--bg:#fff;--text:#363b48;--text-secondary:#65707a;--border:#d6d0c4;--bar-bg:rgba(255,255,255,.92);--bar-border:rgba(0,0,0,.08);--accent:#2e6ab4;--btn-bg:rgba(0,0,0,.06);--btn-hover:rgba(0,0,0,.1);--sidebar-bg:#f5f5f5;--sidebar-hover:#eee}
[data-theme="light-purple"]{--bg:#faf8f3;--text:#363b48;--text-secondary:#65707a;--border:#d6d0c4;--bar-bg:rgba(250,248,243,.94);--bar-border:rgba(0,0,0,.06);--accent:#7c3aed;--btn-bg:rgba(0,0,0,.05);--btn-hover:rgba(0,0,0,.08);--sidebar-bg:#f2efe8;--sidebar-hover:#e8e4dc}
[data-theme="dark-violet"]{--bg:#1a1a1a;--text:#dce0ec;--text-secondary:#8490aa;--border:#333;--bar-bg:rgba(26,26,26,.95);--bar-border:rgba(255,255,255,.08);--accent:#9b7aed;--btn-bg:rgba(255,255,255,.08);--btn-hover:rgba(255,255,255,.12);--sidebar-bg:#222;--sidebar-hover:#2a2a2a}
[data-theme="dark-blue"]{--bg:#000;--text:#8490aa;--text-secondary:#546080;--border:#1c2440;--bar-bg:rgba(0,0,0,.95);--bar-border:rgba(255,255,255,.06);--accent:#2e6ab4;--btn-bg:rgba(255,255,255,.06);--btn-hover:rgba(255,255,255,.1);--sidebar-bg:#0a0a0a;--sidebar-hover:#111}

body{background:var(--bg);color:var(--text);font-family:var(--font-body);font-size:var(--font-size);line-height:var(--line-height)}
[data-font="sans"]{--font-body:var(--font-sans)}[data-font="slab"]{--font-body:var(--font-slab)}
[data-font="mono"]{--font-body:var(--font-mono);--font-size:15px;--line-height:1.7}
[data-size="small"]{--font-size:16px;--line-height:1.75}[data-size="large"]{--font-size:22px;--line-height:1.9}
[data-width="narrow"]{--content-width:720px}[data-width="medium"]{--content-width:960px}[data-width="wide"]{--content-width:1140px}

/* ===== TOP BAR ===== */
#top-bar{position:fixed;top:0;left:0;right:0;z-index:1000;height:44px;background:var(--bar-bg);border-bottom:1px solid var(--bar-border);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);display:flex;align-items:center;padding:0 16px;gap:10px;font-family:var(--font-sans);font-size:13px;color:var(--text-secondary)}
#top-bar .book-title{font-weight:600;letter-spacing:1px;font-size:13px;white-space:nowrap;flex-shrink:0}
#top-bar .chapter-indicator{font-family:var(--font-serif);font-size:13px;font-style:italic;color:var(--accent);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px;flex-shrink:1}
#top-bar .chapter-indicator::before{content:'\00B7';margin:0 8px;color:var(--text-secondary);font-style:normal}
.bar-controls{display:flex;align-items:center;gap:4px;flex-shrink:0}
.bar-btn{width:32px;height:32px;border:none;background:transparent;color:var(--text-secondary);border-radius:6px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:15px;transition:background .15s;font-family:var(--font-sans)}
.bar-btn:hover{background:var(--btn-bg)}.bar-btn.active{background:var(--btn-bg);color:var(--text)}
.theme-wrap{position:relative;display:flex;align-items:center}
.theme-dots{position:absolute;right:100%;top:50%;transform:translateY(-50%);display:flex;gap:6px;align-items:center;padding-right:8px;opacity:0;pointer-events:none;transition:opacity .2s ease}
.theme-wrap:hover .theme-dots{opacity:1;pointer-events:auto}
.theme-dot{width:14px;height:14px;border-radius:50%;border:none;cursor:pointer;transition:transform .15s,box-shadow .15s;flex-shrink:0}
.theme-dot:hover{transform:scale(1.25)}.theme-dot.active{box-shadow:0 0 0 2px var(--bar-bg),0 0 0 3.5px var(--accent)}
.theme-dot[data-theme="light-azure"]{background:#d4e8f7}.theme-dot[data-theme="light-purple"]{background:#c9b8e8}
.theme-dot[data-theme="dark-violet"]{background:#4a3a6a}.theme-dot[data-theme="dark-blue"]{background:#1e2a4a}

/* ===== SETTINGS PANEL ===== */
#settings-panel{position:fixed;top:52px;right:16px;z-index:999;background:var(--bar-bg);border:1px solid var(--border);border-radius:10px;padding:20px;box-shadow:0 8px 32px rgba(0,0,0,.12);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);width:240px;max-width:calc(100vw - 32px);display:none;font-family:var(--font-sans);font-size:13px}
#settings-panel.open{display:block}
.setting-group{margin-bottom:16px}.setting-group:last-child{margin-bottom:0}
.setting-label{color:var(--text-secondary);font-size:10px;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;margin-bottom:8px;display:block}
.btn-row{display:flex;gap:0}
.btn-row .opt{flex:1;height:32px;display:flex;align-items:center;justify-content:center;border:1px solid var(--border);background:transparent;color:var(--text);cursor:pointer;font-family:var(--font-sans);font-size:12px;transition:background .15s,color .15s}
.btn-row .opt:first-child{border-radius:5px 0 0 5px}.btn-row .opt:last-child{border-radius:0 5px 5px 0}
.btn-row .opt+.opt{border-left:none}.btn-row .opt:hover{background:var(--btn-bg)}
.btn-row .opt.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.toggle-row{display:flex;gap:8px}
.toggle-btn{padding:5px 12px;border:1px solid var(--border);border-radius:16px;background:transparent;color:var(--text-secondary);font-size:11px;font-family:var(--font-sans);cursor:pointer;transition:all .15s}
.toggle-btn:hover{background:var(--btn-bg)}.toggle-btn.active{background:var(--accent);color:#fff;border-color:var(--accent)}

/* ===== MANDALA ROW + SUKTA STRIP (two-row nav) ===== */
#nav-strip{position:fixed;top:44px;left:0;right:0;z-index:998;background:var(--bar-bg);border-bottom:1px solid var(--bar-border);font-family:var(--font-sans)}

/* Row 1: Mandala tabs */
#mandala-row{display:flex;align-items:center;justify-content:center;gap:0;height:30px;padding:0 4px}
.m-tab{height:26px;padding:0 10px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:500;color:var(--text-secondary);border:none;background:none;cursor:pointer;transition:all .12s;white-space:nowrap}
.m-tab:hover{color:var(--text)}
.m-tab.active{color:var(--accent);font-weight:600}
.m-tab .arrow{font-size:8px;margin-left:3px;opacity:.5}

/* Row 2: Sukta number strip (horizontally scrollable) */
#sukta-row{display:flex;align-items:center;height:28px;padding:0 4px;gap:0}
#sukta-row .scroll-btn{flex-shrink:0;width:24px;height:24px;border:none;background:none;color:var(--text-secondary);cursor:pointer;font-size:12px;display:flex;align-items:center;justify-content:center;border-radius:4px;transition:background .12s}
#sukta-row .scroll-btn:hover{background:var(--btn-bg)}
#sukta-strip{flex:1;display:flex;gap:1px;overflow-x:auto;scrollbar-width:none;-ms-overflow-style:none;scroll-behavior:smooth;align-items:center;padding:0 2px}
#sukta-strip::-webkit-scrollbar{display:none}
.s-pill{flex-shrink:0;height:22px;min-width:28px;padding:0 5px;display:flex;align-items:center;justify-content:center;font-size:10px;font-family:var(--font-mono);color:var(--text-secondary);border:none;background:none;cursor:pointer;border-radius:3px;transition:all .1s}
.s-pill:hover{background:var(--btn-bg);color:var(--text)}
.s-pill.active{background:var(--accent);color:#fff}

/* ===== SUKTA GRID (full overlay on arrow click) ===== */
#sukta-grid-overlay{position:fixed;inset:0;background:rgba(0,0,0,.3);z-index:1002;opacity:0;pointer-events:none;transition:opacity .25s}
#sukta-grid-overlay.open{opacity:1;pointer-events:auto}
#sukta-grid{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:1003;background:var(--bar-bg);border:1px solid var(--border);border-radius:12px;padding:24px;box-shadow:0 12px 48px rgba(0,0,0,.2);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);max-width:520px;width:calc(100vw - 48px);max-height:70vh;overflow-y:auto;display:none;font-family:var(--font-sans)}
#sukta-grid.open{display:block}
#sukta-grid .grid-title{font-size:14px;font-weight:600;color:var(--text);margin-bottom:16px;text-align:center}
#sukta-grid .tiles{display:flex;flex-wrap:wrap;gap:4px;justify-content:center}
.s-tile{width:38px;height:32px;display:flex;align-items:center;justify-content:center;font-size:11px;font-family:var(--font-mono);color:var(--text-secondary);border:1px solid var(--border);border-radius:6px;cursor:pointer;transition:all .12s;background:transparent}
.s-tile:hover{background:var(--btn-bg);color:var(--text);border-color:var(--accent)}
.s-tile.active{background:var(--accent);color:#fff;border-color:var(--accent)}

/* ===== PROGRESS ===== */
#progress-track{position:fixed;top:102px;left:0;right:0;height:2px;z-index:997;background:var(--border);cursor:pointer;transition:height .15s}
#progress-track:hover{height:6px}
#progress-fill{height:100%;background:var(--accent);transition:width .2s}

/* ===== CONTENT ===== */
#content{max-width:var(--content-width);margin:0 auto;padding:116px 24px 80px}

/* Sukta header */
.sukta-head{text-align:center;padding:20px 0 16px}
.sukta-head .label{font-family:var(--font-sans);font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--accent);opacity:.7}
.sukta-head h2{font-family:var(--font-serif);font-size:1.6em;font-weight:500;color:var(--text);margin:6px 0 2px;font-style:italic}
.sukta-head .rule{width:60px;height:1px;margin:16px auto 0;background:linear-gradient(90deg,transparent,var(--accent),transparent)}

/* Sukta separator in infinite scroll */
.sukta-sep{text-align:center;padding:48px 0 20px;position:relative}
.sukta-sep::before{content:'\0950';display:block;text-align:center;font-size:20px;color:var(--border);background:var(--bg);width:40px;margin:0 auto 16px}
.sukta-sep .label{font-family:var(--font-sans);font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--accent);opacity:.7}
.sukta-sep h3{font-family:var(--font-serif);font-size:1.3em;font-weight:500;color:var(--text);margin:4px 0;font-style:italic}

/* Two-column mantra — compact inline layout */
.m{display:grid;grid-template-columns:1fr 1fr;gap:0 24px;padding:8px 0;position:relative}
.m+.m{padding-top:12px}
.m-num{font-family:var(--font-mono);font-size:10px;color:var(--accent);opacity:.6;grid-column:1;grid-row:1;align-self:start;padding-top:3px}
.m-left{grid-column:1;grid-row:1;padding-left:48px}
.m-left-2{grid-column:1;grid-row:2;padding-left:48px}
.m-right{grid-column:2;grid-row:1/3}
.m-left .en{font-family:var(--font-serif);font-size:.92em;line-height:1.65;color:var(--text);font-style:italic}
.m-left-2 .mb{font-family:var(--font-bn);font-size:.9em;line-height:1.65;color:var(--text);opacity:.85}
.m-right .bn{font-family:var(--font-bn);font-size:.95em;line-height:1.75;font-weight:500;color:var(--text);white-space:pre-line}
.m-right .dv{font-family:var(--font-dev);font-size:.95em;line-height:1.75;color:var(--text-secondary);margin-top:4px;white-space:pre-line}
body:not(.show-dev) .m-right .dv{display:none}

#foot{text-align:center;padding:40px 0 16px;font-family:var(--font-sans);font-size:11px;color:var(--text-secondary);letter-spacing:1px}
/* Infinite scroll sentinel */
#scroll-sentinel{height:1px}

@media(max-width:768px){
  #top-bar .book-title{display:none}
  .m{grid-template-columns:1fr;gap:4px}.m-num{grid-column:1}.m-left{padding-left:48px;grid-row:auto}.m-left-2{padding-left:48px;grid-row:auto}.m-right{grid-column:1;grid-row:auto}
  #content{padding:116px 12px 60px}
  .bar-btn{width:44px;height:44px}
  .m-tab{padding:0 6px;font-size:10px}
}
@media(max-width:600px){#top-bar{padding:0 8px;gap:4px}#settings-panel{right:8px}}
</style>
</head>
<body data-theme="light-purple" data-font="serif" data-size="medium" data-width="medium" class="show-dev">

<nav id="top-bar">
  <span class="book-title">ঋগ্বেদ</span>
  <span class="chapter-indicator" id="chapter-indicator"></span>
  <span style="flex:1"></span>
  <div class="bar-controls">
    <div class="theme-wrap">
      <button class="bar-btn" id="theme-btn" title="Cycle theme" aria-label="Change theme">
        <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="10" cy="10" r="4"/><path d="M10 6V10H6A4 4 0 0 1 10 6z" fill="currentColor" stroke="none"/><path d="M10 10V14H14A4 4 0 0 1 10 14z" fill="currentColor" stroke="none"/><line x1="10" y1="2" x2="10" y2="4"/><line x1="10" y1="16" x2="10" y2="18"/><line x1="2" y1="10" x2="4" y2="10"/><line x1="16" y1="10" x2="18" y2="10"/><line x1="4.3" y1="4.3" x2="5.7" y2="5.7"/><line x1="14.3" y1="14.3" x2="15.7" y2="15.7"/><line x1="4.3" y1="15.7" x2="5.7" y2="14.3"/><line x1="14.3" y1="5.7" x2="15.7" y2="4.3"/></svg>
      </button>
      <div class="theme-dots">
        <span class="theme-dot" data-theme="light-azure" title="Light Azure"></span>
        <span class="theme-dot active" data-theme="light-purple" title="Light Purple"></span>
        <span class="theme-dot" data-theme="dark-violet" title="Dark Violet"></span>
        <span class="theme-dot" data-theme="dark-blue" title="Dark Blue"></span>
      </div>
    </div>
    <button class="bar-btn" id="settings-btn" title="Settings" aria-label="Settings">
      <svg width="18" height="16" viewBox="0 0 18 16" fill="currentColor" stroke="none"><text x="1.5" y="10.5" font-family="Georgia,serif" font-size="12" font-weight="600">Aa</text><rect x="1" y="12.8" width="16" height="1.3" rx=".65"/><rect x="1" y="15" width="10" height="1.1" rx=".55" opacity=".4"/></svg>
    </button>
  </div>
</nav>

<!-- Two-row nav: mandala tabs + sukta strip -->
<div id="nav-strip">
  <div id="mandala-row"></div>
  <div id="sukta-row">
    <button class="scroll-btn" id="strip-left">&#9666;</button>
    <div id="sukta-strip"></div>
    <button class="scroll-btn" id="strip-right">&#9656;</button>
  </div>
</div>

<div id="progress-track"><div id="progress-fill"></div></div>

<!-- Sukta grid overlay -->
<div id="sukta-grid-overlay"></div>
<div id="sukta-grid"><div class="grid-title" id="grid-title"></div><div class="tiles" id="grid-tiles"></div></div>

<!-- Settings panel -->
<div id="settings-panel">
  <div class="setting-group"><span class="setting-label">Text Size</span>
    <div class="btn-row"><button class="opt" data-size="small" style="font-size:10px">Small</button><button class="opt active" data-size="medium" style="font-size:12px">Medium</button><button class="opt" data-size="large" style="font-size:14px">Large</button></div></div>
  <div class="setting-group"><span class="setting-label">Font</span>
    <div class="btn-row"><button class="opt active" data-font="serif" style="font-family:'EB Garamond',Georgia,serif">Serif</button><button class="opt" data-font="sans" style="font-family:'Jost',sans-serif">Sans</button><button class="opt" data-font="slab" style="font-family:'Roboto Slab',Georgia,serif">Slab</button><button class="opt" data-font="mono" style="font-family:'IBM Plex Mono',monospace;font-size:11px">Mono</button></div></div>
  <div class="setting-group"><span class="setting-label">Page Width</span>
    <div class="btn-row"><button class="opt" data-width="narrow">Narrow</button><button class="opt active" data-width="medium">Medium</button><button class="opt" data-width="wide">Wide</button></div></div>
  <div class="setting-group"><span class="setting-label">Show / Hide</span>
    <div class="toggle-row"><button class="toggle-btn active" id="toggle-dev">देवनागरी</button></div></div>
</div>

<div id="content"></div>
<div id="scroll-sentinel"></div>

<script>
const RV=__DATA_JSON__;
let mIdx=0,sIdx=0;
const themes=['light-azure','light-purple','dark-violet','dark-blue'];

// Flat index helpers
const flatSuktas=[];
RV.m.forEach((m,mi)=>m.s.forEach((s,si)=>flatSuktas.push({mi,si})));
const totalSuktas=flatSuktas.length;
function flatIdx(){let i=0;for(let j=0;j<mIdx;j++)i+=RV.m[j].s.length;return i+sIdx;}

// ===== RENDER (infinite scroll: renders current sukta, appends more on scroll) =====
let renderedUpTo=-1; // index of last rendered sukta within current mandala

function renderSukta(m,s,mn,isFirst){
  let h='';
  if(isFirst){
    h+='<div class="sukta-head"><div class="label">Mandala '+mn+' \u00B7 S\u016Bkta '+s.n+'</div>';
    if(s.t) h+='<h2>'+s.t+'</h2>';
    h+='<div class="rule"></div></div>';
  } else {
    h+='<div class="sukta-sep"><div class="label">S\u016Bkta '+s.n+'</div>';
    if(s.t) h+='<h3>'+s.t+'</h3>';
    h+='</div>';
  }
  for(const v of s.v){
    h+='<div class="m"><div class="m-num">'+mn+'.'+s.n+'.'+v.n+'</div>';
    h+='<div class="m-left"><div class="en">'+v.e+'</div>';
    if(v.mb) h+='<div class="mb">'+v.mb+'</div>';
    h+='</div><div class="m-right"><div class="bn">'+v.b+'</div><div class="dv">'+v.d+'</div></div></div>';
  }
  return h;
}

function render(){
  const m=RV.m[mIdx],s=m.s[sIdx],fi=flatIdx();
  document.getElementById('chapter-indicator').textContent=(s.t||('S\u016Bkta '+s.n))+' \u00B7 M'+m.n;
  document.getElementById('progress-fill').style.width=((fi+1)/totalSuktas*100)+'%';

  // Update nav highlights
  document.querySelectorAll('.m-tab').forEach((t,i)=>t.classList.toggle('active',i===mIdx));
  buildSuktaStrip();

  // Render initial sukta
  const w=document.getElementById('content');
  w.innerHTML=renderSukta(m,s,m.n,true);
  renderedUpTo=sIdx;
  window.scrollTo(0,0);
  history.replaceState(null,'','#'+m.n+'.'+s.n);
  savePrefs();
}

// Infinite scroll: append next suktas as user scrolls down
function appendNextSukta(){
  const m=RV.m[mIdx];
  if(renderedUpTo>=m.s.length-1) return false;
  renderedUpTo++;
  const s=m.s[renderedUpTo];
  const w=document.getElementById('content');
  w.insertAdjacentHTML('beforeend',renderSukta(m,s,m.n,false));
  // Update strip highlight
  document.querySelectorAll('.s-pill').forEach((p,i)=>p.classList.toggle('active',i===renderedUpTo));
  return true;
}

// Observe scroll sentinel
const scrollObserver=new IntersectionObserver((entries)=>{
  if(entries[0].isIntersecting) appendNextSukta();
},{rootMargin:'400px'});
scrollObserver.observe(document.getElementById('scroll-sentinel'));

// Also update current sukta indicator on scroll
const suktaObserver=new IntersectionObserver((entries)=>{
  for(const e of entries){
    if(e.isIntersecting){
      const idx=parseInt(e.target.dataset.suktaIdx||'0');
      if(idx!==sIdx){
        sIdx=idx;
        const m=RV.m[mIdx],s=m.s[sIdx],fi=flatIdx();
        document.getElementById('chapter-indicator').textContent=(s.t||('S\u016Bkta '+s.n))+' \u00B7 M'+m.n;
        document.getElementById('progress-fill').style.width=((fi+1)/totalSuktas*100)+'%';
        document.querySelectorAll('.s-pill').forEach((p,i)=>p.classList.toggle('active',i===sIdx));
        scrollActivePillIntoView();
        history.replaceState(null,'','#'+m.n+'.'+s.n);
      }
    }
  }
},{rootMargin:'-30% 0px -60% 0px'});

// Tag sukta headers for observation after render
function observeSuktaHeaders(){
  document.querySelectorAll('.sukta-head,.sukta-sep').forEach((el,i)=>{
    el.dataset.suktaIdx=sIdx+i; // first one is sIdx, rest are sequential
    suktaObserver.observe(el);
  });
}

// Re-observe after each render
const contentObserverMO=new MutationObserver(()=>{
  suktaObserver.disconnect();
  const heads=document.querySelectorAll('.sukta-head,.sukta-sep');
  let baseIdx=sIdx; // the first rendered sukta
  heads.forEach((el,i)=>{
    el.dataset.suktaIdx=i===0?sIdx:sIdx+i; // WRONG — need global tracking
  });
  // Actually, let me use a simpler approach: tag by sukta number
  document.querySelectorAll('[data-sukta-n]').forEach(el=>{
    suktaObserver.observe(el);
  });
});

function goToSukta(mi,si){
  mIdx=mi;sIdx=si;render();
}

// ===== MANDALA TABS =====
(function buildTabs(){
  const c=document.getElementById('mandala-row');
  RV.m.forEach((m,i)=>{
    const b=document.createElement('button');
    b.className='m-tab'+(i===0?' active':'');
    b.innerHTML='Mandala '+m.n+'<span class="arrow">\u25BE</span>';
    b.title=m.s.length+' s\u016Bktas';
    b.onclick=()=>{
      if(mIdx===i){toggleGrid();}  // click active mandala = open grid
      else{mIdx=i;sIdx=0;render();}
    };
    c.appendChild(b);
  });
})();

// ===== SUKTA STRIP (horizontal scrollable) =====
function buildSuktaStrip(){
  const strip=document.getElementById('sukta-strip');
  strip.innerHTML='';
  const m=RV.m[mIdx];
  m.s.forEach((s,si)=>{
    const p=document.createElement('button');
    p.className='s-pill'+(si===sIdx?' active':'');
    p.textContent=s.n;
    p.title=s.t||('S\u016Bkta '+s.n);
    p.onclick=()=>{sIdx=si;render();};
    strip.appendChild(p);
  });
  scrollActivePillIntoView();
}

function scrollActivePillIntoView(){
  const active=document.querySelector('.s-pill.active');
  if(active) active.scrollIntoView({block:'nearest',inline:'center',behavior:'smooth'});
}

document.getElementById('strip-left').onclick=()=>{document.getElementById('sukta-strip').scrollBy({left:-200,behavior:'smooth'});};
document.getElementById('strip-right').onclick=()=>{document.getElementById('sukta-strip').scrollBy({left:200,behavior:'smooth'});};

// ===== SUKTA GRID (full overlay) =====
const gridOverlay=document.getElementById('sukta-grid-overlay');
const grid=document.getElementById('sukta-grid');

function toggleGrid(){
  const open=!grid.classList.contains('open');
  grid.classList.toggle('open',open);
  gridOverlay.classList.toggle('open',open);
  if(open) buildGrid();
}
function closeGrid(){grid.classList.remove('open');gridOverlay.classList.remove('open');}
gridOverlay.onclick=closeGrid;

function buildGrid(){
  const m=RV.m[mIdx];
  document.getElementById('grid-title').textContent='Mandala '+m.n+' \u2014 '+m.s.length+' S\u016Bktas';
  const c=document.getElementById('grid-tiles');c.innerHTML='';
  m.s.forEach((s,si)=>{
    const t=document.createElement('button');
    t.className='s-tile'+(si===sIdx?' active':'');
    t.textContent=s.n;t.title=s.t||('S\u016Bkta '+s.n);
    t.onclick=()=>{sIdx=si;closeGrid();render();};
    c.appendChild(t);
  });
}

// ===== PROGRESS BAR =====
document.getElementById('progress-track').onclick=(e)=>{
  const fi=Math.round(e.clientX/window.innerWidth*totalSuktas);
  const f=flatSuktas[Math.max(0,Math.min(fi,totalSuktas-1))];
  goToSukta(f.mi,f.si);
};

// ===== THEME =====
function setTheme(t){document.documentElement.dataset.theme=t;document.body.dataset.theme=t;document.querySelectorAll('.theme-dot').forEach(d=>d.classList.toggle('active',d.dataset.theme===t));savePrefs();}
document.getElementById('theme-btn').onclick=()=>{const c=themes.indexOf(document.documentElement.dataset.theme);setTheme(themes[(c+1)%themes.length]);};
document.querySelectorAll('.theme-dot').forEach(d=>{d.addEventListener('click',(e)=>{e.stopPropagation();setTheme(d.dataset.theme)});});

// ===== SETTINGS =====
const settingsPanel=document.getElementById('settings-panel'),settingsBtn=document.getElementById('settings-btn');
settingsBtn.onclick=()=>{const o=settingsPanel.classList.toggle('open');settingsBtn.classList.toggle('active',o);};
document.addEventListener('click',(e)=>{if(!settingsPanel.contains(e.target)&&e.target!==settingsBtn&&!settingsBtn.contains(e.target)){settingsPanel.classList.remove('open');settingsBtn.classList.remove('active');}});
document.querySelectorAll('[data-size].opt').forEach(b=>{b.addEventListener('click',()=>{document.body.dataset.size=b.dataset.size;document.querySelectorAll('[data-size].opt').forEach(x=>x.classList.toggle('active',x===b));savePrefs();});});
document.querySelectorAll('[data-font].opt').forEach(b=>{b.addEventListener('click',()=>{document.body.dataset.font=b.dataset.font;document.querySelectorAll('[data-font].opt').forEach(x=>x.classList.toggle('active',x===b));savePrefs();});});
document.querySelectorAll('[data-width].opt').forEach(b=>{b.addEventListener('click',()=>{document.body.dataset.width=b.dataset.width;document.querySelectorAll('[data-width].opt').forEach(x=>x.classList.toggle('active',x===b));savePrefs();});});
const toggleDev=document.getElementById('toggle-dev');
toggleDev.onclick=()=>{document.body.classList.toggle('show-dev');toggleDev.classList.toggle('active');savePrefs();};

// ===== KEYBOARD =====
document.addEventListener('keydown',(e)=>{
  if(e.target.tagName==='INPUT'||e.target.tagName==='SELECT')return;
  switch(e.key){
    case'ArrowRight':case'j':sIdx=Math.min(sIdx+1,RV.m[mIdx].s.length-1);render();e.preventDefault();break;
    case'ArrowLeft':case'k':sIdx=Math.max(sIdx-1,0);render();e.preventDefault();break;
    case'd':case'D':toggleDev.click();break;
    case'g':case'G':toggleGrid();break;
    case'Escape':closeGrid();settingsPanel.classList.remove('open');settingsBtn.classList.remove('active');break;
    case'Home':sIdx=0;render();e.preventDefault();break;
    case'End':sIdx=RV.m[mIdx].s.length-1;render();e.preventDefault();break;
  }
  if(e.key>='1'&&e.key<='9'&&!e.ctrlKey&&!e.metaKey){const mi=parseInt(e.key)-1;if(mi<RV.m.length)goToSukta(mi,0);}
  if(e.key==='0'&&!e.ctrlKey&&!e.metaKey&&RV.m.length>=10)goToSukta(9,0);
});

// ===== TOUCH =====
let touchX=0;
document.addEventListener('touchstart',(e)=>{touchX=e.changedTouches[0].clientX},{passive:true});
document.addEventListener('touchend',(e)=>{const dx=e.changedTouches[0].clientX-touchX;if(Math.abs(dx)>60){dx<0?(sIdx=Math.min(sIdx+1,RV.m[mIdx].s.length-1)):(sIdx=Math.max(sIdx-1,0));render();}},{passive:true});

// ===== HASH =====
function parseHash(){const h=location.hash.replace('#','');if(!h)return;const p=h.split('.');if(p.length>=2){const mn=parseInt(p[0]),sn=parseInt(p[1]);const mi=RV.m.findIndex(x=>x.n===mn);if(mi>=0){const si=RV.m[mi].s.findIndex(x=>x.n===sn);if(si>=0){mIdx=mi;sIdx=si;}}}}

// ===== PREFS =====
function savePrefs(){try{localStorage.setItem('rv-prefs',JSON.stringify({theme:document.body.dataset.theme,size:document.body.dataset.size,font:document.body.dataset.font,width:document.body.dataset.width,dev:document.body.classList.contains('show-dev'),m:mIdx,s:sIdx}))}catch(e){}}
function loadPrefs(){try{const p=JSON.parse(localStorage.getItem('rv-prefs'));if(!p)return;
if(p.theme)setTheme(p.theme);
if(p.size){document.body.dataset.size=p.size;document.querySelectorAll('[data-size].opt').forEach(b=>b.classList.toggle('active',b.dataset.size===p.size));}
if(p.font){document.body.dataset.font=p.font;document.querySelectorAll('[data-font].opt').forEach(b=>b.classList.toggle('active',b.dataset.font===p.font));}
if(p.width){document.body.dataset.width=p.width;document.querySelectorAll('[data-width].opt').forEach(b=>b.classList.toggle('active',b.dataset.width===p.width));}
if(typeof p.dev==='boolean'){document.body.classList.toggle('show-dev',p.dev);toggleDev.classList.toggle('active',p.dev);}
if(typeof p.m==='number'&&typeof p.s==='number'){mIdx=p.m;sIdx=p.s;}
}catch(e){}}

loadPrefs();parseHash();render();
</script>
</body>
</html>'''


# ─── Main ────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Rigveda Builder — Compact Full-Text Reader")
    print("=" * 60)
    print()

    # Phase 1: Fetch and parse
    mandalas = fetch_all_suktas()

    # Phase 2: Bengali overlay
    bn_lookup = load_bengali_meanings()
    bn_count = overlay_bengali(mandalas, bn_lookup)
    print(f"\nBengali meanings overlaid: {bn_count}")

    # Phase 3: Generate outputs
    print("\nGenerating outputs...")

    # 3a: Per-mandala JSON files + metadata
    print("  Writing per-mandala data files:")
    meta_json = build_mandala_files(mandalas)
    print(f"  Metadata JSON: {len(meta_json):,} bytes")

    # 3b: rigveda.html (from external template with all UI improvements)
    template_path = SCRIPT_DIR / "rigveda-template.html"
    if template_path.exists():
        html_template = template_path.read_text(encoding='utf-8')
        print(f"  Using external template: {template_path.name}")
    else:
        html_template = HTML_TEMPLATE
        print(f"  Using inline template (external not found)")
    html = html_template.replace('__META_JSON__', meta_json)
    html_path = SCRIPT_DIR / "rigveda.html"
    html_path.write_text(html, encoding='utf-8')
    print(f"  {html_path.name}: {len(html):,} bytes")

    # 3c: rigveda-complete.json
    readable_json = build_readable_json(mandalas)
    json_path = SEEDS_DIR / "rigveda-complete.json"
    json_path.write_text(readable_json, encoding='utf-8')
    print(f"  {json_path.name}: {len(readable_json):,} bytes")

    # 3d: rigveda-samhita.md
    md = build_markdown(mandalas)
    md_path = SCRIPT_DIR / "rigveda-samhita.md"
    md_path.write_text(md, encoding='utf-8')
    print(f"  {md_path.name}: {len(md):,} bytes")

    print(f"\nDone! Open {html_path} in a browser.")


if __name__ == "__main__":
    main()

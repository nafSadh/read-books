#!/usr/bin/env python3
"""Download and parse OCR text from archive.org Bengali Rigveda scans.

Fetches the OCR full-text (djvu.txt) from archive.org digitized copies of
Ramesh Chandra Dutta's Bengali Rigveda translation, parses the noisy OCR
output into structured mandala/sukta/verse JSON.

Sources:
  - Combined (1-10): archive.org/details/ajoymondol297_gmail_20160510
  - Vol 1 (ashtaka 1): archive.org/details/dli.bengal.10689.6357
  - Vol 2 (mandalas 6-10): archive.org/details/in.ernet.dli.2015.454708
  - Vol 4 (ashtaka 7-8): archive.org/details/dli.bengal.10689.5839

Usage:
    python3 vedas/scripts/extract_archive_ocr.py [--source combined|vol1|vol2|vol4|all]
    python3 vedas/scripts/extract_archive_ocr.py --source vol2  # just vol 2

Output:
    vedas/scripts/output/archive_ocr_bengali.json

Constraints: Python 3.9.6 stdlib only (no pip packages).
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ─── Configuration ───────────────────────────────────────────────────────────

CACHE_DIR = Path("/tmp/archive_ocr_cache")
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"

# Archive.org source metadata
SOURCES = {
    "combined": {
        "id": "ajoymondol297_gmail_20160510",
        "filename": "\u098b\u0997\u09cd\u09ac\u09c7\u09a6 - \u0985\u09a8\u09c1.\u09b0\u09ae\u09c7\u09b6\u099a\u09a8\u09cd\u09a6\u09cd\u09b0 \u09a6\u09a4\u09cd\u09a4 \u09e7\u09ae-\u09ee\u09ae \u0985\u09b7\u09cd\u099f\u0995. \u09e7.\u09ee\u09e7 - \u09e7\u09e6.\u09e7\u09ef\u09e7_djvu.txt",
        "description": "Combined Ramesh Chandra Dutta, Mandala 1-10 (ashtaka 1-8)",
        "mandalas": list(range(1, 11)),
        "ocr_engine": "Tesseract 5.3.0",
    },
    "vol1": {
        "id": "dli.bengal.10689.6357",
        "filename": "10689.6357_djvu.txt",
        "description": "Rigveda Samhita Vol 1 (ashtaka 1, partial mandala 1)",
        "mandalas": [1],
        "ocr_engine": "Tesseract 5.0.0",
    },
    "vol2": {
        "id": "in.ernet.dli.2015.454708",
        "filename": "2015.454708.Rikveda-Samhita_djvu.txt",
        "description": "Rikveda Samhita Vol 2 (mandalas 6-10)",
        "mandalas": list(range(6, 11)),
        "ocr_engine": "Tesseract 5.0.0",
    },
    "vol4": {
        "id": "dli.bengal.10689.5839",
        "filename": "10689.5839_djvu.txt",
        "description": "Rigveda Samhita Vol 4 (ashtaka 7-8)",
        "mandalas": [9, 10],
        "ocr_engine": "Tesseract 5.0.0",
    },
}

# Canonical sukta counts per mandala (Shakala recension)
MANDALA_SUKTA_COUNTS = {
    1: 191, 2: 43, 3: 62, 4: 58, 5: 87,
    6: 75, 7: 104, 8: 103, 9: 114, 10: 191,
}

# Bengali numeral mapping
BENGALI_TO_INT = {
    "\u09e6": 0, "\u09e7": 1, "\u09e8": 2, "\u09e9": 3, "\u09ea": 4,
    "\u09eb": 5, "\u09ec": 6, "\u09ed": 7, "\u09ee": 8, "\u09ef": 9,
}

# Mandala ordinal words in Bengali
MANDALA_ORDINALS = {
    "\u09aa\u09cd\u09b0\u09a5\u09ae": 1,        # প্রথম
    "\u09a6\u09cd\u09ac\u09bf\u09a4\u09c0\u09af\u09bc": 2,  # দ্বিতীয়
    "\u09a4\u09c3\u09a4\u09c0\u09af\u09bc": 3,    # তৃতীয়
    "\u099a\u09a4\u09c1\u09b0\u09cd\u09a5": 4,     # চতুর্থ
    "\u09aa\u099e\u09cd\u099a\u09ae": 5,           # পঞ্চম
    "\u09b7\u09b7\u09cd\u09a0": 6,                 # ষষ্ঠ
    "\u09b8\u09aa\u09cd\u09a4\u09ae": 7,           # সপ্তম
    "\u0985\u09b7\u09cd\u099f\u09ae": 8,           # অষ্টম
    "\u09a8\u09ac\u09ae": 9,                       # নবম
    "\u09a6\u09b6\u09ae": 10,                      # দশম
}


# ─── Bengali numeral utilities ───────────────────────────────────────────────

def bengali_to_int(s: str) -> Optional[int]:
    """Convert a string of Bengali numerals to an integer.
    Returns None if the string contains non-Bengali-numeral characters."""
    digits = []
    for ch in s:
        if ch in BENGALI_TO_INT:
            digits.append(str(BENGALI_TO_INT[ch]))
        elif ch.isdigit():
            digits.append(ch)
        else:
            return None
    if not digits:
        return None
    return int("".join(digits))


def extract_bengali_number(s: str) -> Optional[int]:
    """Extract the first Bengali or ASCII number from a string."""
    m = re.search(r"[\u09e6-\u09ef]+|[0-9]+", s)
    if m:
        val = m.group()
        result = bengali_to_int(val)
        if result is not None:
            return result
        if val.isdigit():
            return int(val)
    return None


# ─── Download ────────────────────────────────────────────────────────────────

def download_ocr_text(source_key: str) -> str:
    """Download OCR text from archive.org with caching."""
    src = SOURCES[source_key]
    cache_file = CACHE_DIR / f"{source_key}_djvu.txt"

    if cache_file.exists():
        mtime = cache_file.stat().st_mtime
        age_days = (time.time() - mtime) / 86400
        if age_days < 7:
            print(f"  Using cached {cache_file.name} ({age_days:.1f} days old)")
            return cache_file.read_text(encoding="utf-8")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # URL-encode the filename (it may contain Bengali characters)
    filename_encoded = urllib.request.quote(src["filename"])
    url = f"https://archive.org/download/{src['id']}/{filename_encoded}"

    print(f"  Downloading from archive.org: {src['id']}")
    print(f"    URL: {url[:120]}...")

    headers = {"User-Agent": "Mozilla/5.0 (RigvedaOCR/1.0)"}
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(3):
        try:
            resp = urllib.request.urlopen(req, timeout=120)
            data = resp.read()
            text = data.decode("utf-8", errors="replace")
            cache_file.write_text(text, encoding="utf-8")
            print(f"    Downloaded {len(data):,} bytes, {len(text):,} chars")
            return text
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            print(f"    Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Failed to download {source_key} after 3 attempts") from e
    return ""


# ─── Parsing ─────────────────────────────────────────────────────────────────

def clean_line(line: str) -> str:
    """Basic OCR line cleanup."""
    # Remove stray punctuation noise but preserve Bengali text
    line = line.strip()
    # Remove isolated single characters that are OCR noise
    # but keep Bengali text intact
    return line


def detect_mandala_header(line: str) -> Optional[int]:
    """Detect a mandala header line. Returns mandala number or None.

    Patterns:
      - "ষষ্ঠ মণ্ডল" (ordinal + মণ্ডল)
      - "৬ মণ্ডল" / "৬ষ্ঠ মণ্ডল"
      - "N মন্ডল" (OCR corruption of মণ্ডল)
    """
    # মণ্ডল or OCR variants
    mandala_word = re.search(
        r"ম[ণন][্ড][ডল]ল|মণ্ডল", line
    )
    if not mandala_word:
        return None

    prefix = line[:mandala_word.start()].strip()

    # Check for ordinal words
    for word, num in MANDALA_ORDINALS.items():
        if word in prefix or word in line[:mandala_word.start() + 10]:
            return num

    # Check for Bengali numeral before মণ্ডল
    num = extract_bengali_number(prefix)
    if num and 1 <= num <= 10:
        return num

    # Check for numeral after মণ্ডল (e.g., "মণ্ডল ৬")
    suffix = line[mandala_word.end():].strip()
    num = extract_bengali_number(suffix)
    if num and 1 <= num <= 10:
        return num

    return None


def detect_sukta_header(line: str) -> Optional[dict]:
    """Detect a sukta header line. Returns dict with sukta_num, devata, rishi, etc.

    Patterns (extremely noisy OCR from Vol 1 & Vol 2):
      - "৮১ সুক্তী।" / "৮১ সুক্ত।"
      - "১ সন্ত ||" / "২ সতৃস্ত।।" / "৩স্ূত্ত।।"
      - "N সূক্ত" / "N সৃত্ত" / "N সূন্ত" / "N সুস্ত" / "N সমস্ত" / "N স্ত"
      - Contains দেবতা and/or ঋষি/খাষি/ঝাষি after the sukta word
    """
    stripped = line.strip()
    if not stripped or len(stripped) < 5:
        return None

    # Strategy 1: Line starts with Bengali number and has দেবতা/ঋষ/ছন্দ markers
    # This is the most reliable signal for Vol 2 headers
    m = re.match(r"^([\u09e6-\u09ef]+)\s*", stripped)
    if m and ("দেবতা" in stripped or "ঋষ" in stripped or "ছন্দ" in stripped
              or "খাঁষ" in stripped or "ঝাঁষ" in stripped or "ধাঁষ" in stripped
              or "ধাষ" in stripped or "খাষ" in stripped or "ঝষ" in stripped):
        num = bengali_to_int(m.group(1))
        if num and 1 <= num <= 200:
            # Extract devata
            devata = None
            devata_match = re.search(r"(.{2,30}?)\s*দেবতা", stripped[m.end():])
            if devata_match:
                devata = devata_match.group(1).strip().rstrip("।.॥| ")

            # Extract rishi (various OCR spellings)
            rishi = None
            rishi_match = re.search(
                r"(.{2,30}?)\s*(?:খাঁষ|ঝাঁষ|ধাঁষ|ধাষ|খাষ|ঝষ|ঋষি|খঁষি|ধষি)",
                stripped[m.end():]
            )
            if rishi_match:
                rishi = rishi_match.group(1).strip().rstrip("।.॥| ")

            return {
                "sukta_num": num,
                "devata": devata,
                "rishi": rishi,
                "raw_header": stripped[:200],
            }

    # Strategy 2: Match sukta-like words with OCR variant tolerance
    # Broad pattern to catch OCR corruptions of সূক্ত
    sukta_pattern = re.search(
        r"([সশ][ূুতনমৃ][কক্ৃত্রনস][তষ্ট]"  # সূক্ত, সৃত্ত, সুক্ত, etc.
        r"|সুক্ত|সুজ[িী]?|সূক্ত"
        r"|সন্ত|স্ত|সমস্ত"                   # more OCR variants
        r"|সুক্তী|সূত্ত|সূন্ত|সুস্ত|সুভ্ত"
        r"|শুক্ত|স্ূত্ত)",
        line,
    )
    if not sukta_pattern:
        return None

    # Must have a number nearby
    prefix = line[:sukta_pattern.start()].strip()
    suffix = line[sukta_pattern.end():].strip()

    # Try to extract sukta number from prefix
    num = extract_bengali_number(prefix)
    if num is None:
        # Try suffix for patterns like "সূক্ত ১"
        num = extract_bengali_number(suffix[:20] if suffix else "")

    if num is None or num < 1 or num > 200:
        return None

    # Validate: sukta headers usually have দেবতা or are short contextual lines
    # Skip if this looks like running text (long line without দেবতা marker)
    if len(stripped) > 100 and "দেবতা" not in stripped and "ঋষ" not in stripped:
        return None

    # Try to extract devata (deity) info
    devata = None
    devata_match = re.search(r"(.{2,30}?)\s*দেবতা", suffix)
    if devata_match:
        devata = devata_match.group(1).strip().rstrip("।.॥| ")

    # Try to extract rishi info
    rishi = None
    rishi_match = re.search(
        r"(.{2,30}?)\s*(?:[ঋর][ষস][িী]|খাঁষ|ঝাঁষ|ধাঁষ|ধাষ|খাষ|ঝষ)",
        suffix,
    )
    if rishi_match:
        rishi = rishi_match.group(1).strip().rstrip("।.॥| ")

    return {
        "sukta_num": num,
        "devata": devata,
        "rishi": rishi,
        "raw_header": stripped[:200],
    }


def detect_verse_start(line: str) -> Optional[int]:
    """Detect if a line starts with a verse number (Bengali numeral + danda/period).

    Patterns:
      - "১। verse text..."
      - "১. verse text..."
      - "১ verse text..." (sometimes danda is missing in OCR)
    """
    stripped = line.strip()
    if not stripped:
        return None

    # Match: Bengali numeral(s) followed by danda, period, or space+Bengali text
    m = re.match(
        r"^([\u09e6-\u09ef]+)\s*[।॥\.\)]\s*",
        stripped,
    )
    if m:
        num = bengali_to_int(m.group(1))
        if num is not None and 1 <= num <= 50:
            return num

    # Also match ASCII digits at start
    m = re.match(r"^(\d+)\s*[।॥\.\)]\s*", stripped)
    if m:
        num = int(m.group(1))
        if 1 <= num <= 50:
            return num

    return None


def is_page_header(line: str) -> bool:
    """Detect page headers/footers that should be skipped.

    Common patterns:
      - "N অষ্টক, N অধ্যায়। ঋগ্বেদ সংহিতা। N মণ্ডল, N সুক্ত"
      - Lines that are mostly numbers/punctuation (page numbers)
      - Very short lines that are OCR noise
    """
    stripped = line.strip()

    # Very short noisy lines
    if len(stripped) < 3:
        return True

    # Page header pattern: contains both অষ্টক and অধ্যায়
    if "অষ্টক" in stripped and "অধ্যায়" in stripped:
        return True

    # Page header with সংহিতা + mandala/sukta info
    if "সংহিতা" in stripped and (
        "অষ্টক" in stripped or "অধ্যায়" in stripped or "মণ্ডল" in stripped
    ):
        return True

    # Lines that are mostly numbers and punctuation (OCR noise)
    alpha_bengali = sum(
        1 for ch in stripped
        if "\u0980" <= ch <= "\u09FF" and ch not in "\u09e6\u09e7\u09e8\u09e9\u09ea\u09eb\u09ec\u09ed\u09ee\u09ef"
    )
    if len(stripped) > 5 and alpha_bengali < 3:
        return True

    return False


def is_footnote(line: str) -> bool:
    """Detect footnote lines that should be separated from verse text."""
    stripped = line.strip()
    # Footnotes often start with (N) or (N, ... patterns
    if re.match(r"^\([০-৯\d]+[\,\.]", stripped):
        return True
    # Footnote references: "(১) মূলে..." or similar
    if re.match(r"^\([০-৯\d]+\)\s*[মম]ূলে", stripped):
        return True
    # Lines starting with "মূলে" or "সায়ণ" (commentary refs)
    if stripped.startswith("মূলে") or stripped.startswith("সায়ণ"):
        return True
    return False


def parse_ocr_text(text: str, source_key: str) -> dict:
    """Parse raw OCR text into structured mandala/sukta/verse data.

    Strategy:
    1. Split into lines
    2. Scan for mandala headers
    3. Within each mandala, scan for sukta headers
    4. Within each sukta, collect verses by verse-number markers
    5. Handle OCR noise, page headers, footnotes gracefully
    """
    lines = text.split("\n")
    src = SOURCES[source_key]

    # Result structure
    mandalas = {}  # {mandala_num: {sukta_num: {verse_num: text}}}
    current_mandala = None
    current_sukta = None
    current_verse_num = None
    current_verse_lines = []
    current_sukta_meta = {}

    # Stats
    stats = {
        "total_lines": len(lines),
        "mandala_headers_found": 0,
        "sukta_headers_found": 0,
        "verse_starts_found": 0,
        "page_headers_skipped": 0,
        "footnotes_skipped": 0,
    }

    def flush_verse():
        """Save accumulated verse lines to the data structure."""
        nonlocal current_verse_lines, current_verse_num
        if current_verse_num and current_verse_lines and current_mandala and current_sukta:
            verse_text = " ".join(current_verse_lines).strip()
            if verse_text and len(verse_text) > 5:
                if current_mandala not in mandalas:
                    mandalas[current_mandala] = {}
                if current_sukta not in mandalas[current_mandala]:
                    mandalas[current_mandala][current_sukta] = {
                        "meta": current_sukta_meta.copy(),
                        "verses": {},
                    }
                mandalas[current_mandala][current_sukta]["verses"][current_verse_num] = verse_text
        current_verse_lines = []

    for i, raw_line in enumerate(lines):
        line = clean_line(raw_line)

        if not line:
            continue

        # Skip page headers
        if is_page_header(line):
            stats["page_headers_skipped"] += 1
            continue

        # Skip footnotes
        if is_footnote(line):
            stats["footnotes_skipped"] += 1
            continue

        # Check for mandala header
        mandala_num = detect_mandala_header(line)
        if mandala_num:
            flush_verse()
            current_mandala = mandala_num
            current_sukta = None
            current_verse_num = None
            stats["mandala_headers_found"] += 1
            continue

        # Check for sukta header
        sukta_info = detect_sukta_header(line)
        if sukta_info:
            flush_verse()
            current_sukta = sukta_info["sukta_num"]
            current_sukta_meta = {
                "devata": sukta_info.get("devata"),
                "rishi": sukta_info.get("rishi"),
            }
            current_verse_num = None
            stats["sukta_headers_found"] += 1
            continue

        # Check for verse start
        verse_num = detect_verse_start(line)
        if verse_num:
            flush_verse()
            current_verse_num = verse_num
            stats["verse_starts_found"] += 1
            # Remove the verse number prefix from the text
            stripped = line.strip()
            m = re.match(r"^[\u09e6-\u09ef\d]+\s*[।॥\.\)]\s*", stripped)
            if m:
                remainder = stripped[m.end():]
            else:
                remainder = stripped
            if remainder:
                current_verse_lines.append(remainder)
            continue

        # Otherwise: continuation of current verse
        if current_verse_num and line.strip():
            current_verse_lines.append(line.strip())

    # Flush last verse
    flush_verse()

    return {
        "source": source_key,
        "source_info": src,
        "stats": stats,
        "mandalas": mandalas,
    }


def build_json_output(parsed_sources: List[dict]) -> dict:
    """Merge parsed sources into the final JSON output structure.

    If multiple sources provide the same mandala/sukta/verse,
    we keep the one with the most text (longest verse content).
    """
    merged = {}  # {mandala: {sukta: {verse: text}}}
    merged_meta = {}  # {mandala: {sukta: meta}}

    for parsed in parsed_sources:
        for m_num_str, suktas in parsed["mandalas"].items():
            m_num = int(m_num_str) if isinstance(m_num_str, str) else m_num_str
            if m_num not in merged:
                merged[m_num] = {}
                merged_meta[m_num] = {}
            for s_num_str, s_data in suktas.items():
                s_num = int(s_num_str) if isinstance(s_num_str, str) else s_num_str
                if s_num not in merged[m_num]:
                    merged[m_num][s_num] = {}
                    merged_meta[m_num][s_num] = s_data.get("meta", {})
                for v_num_str, v_text in s_data["verses"].items():
                    v_num = int(v_num_str) if isinstance(v_num_str, str) else v_num_str
                    existing = merged[m_num][s_num].get(v_num, "")
                    if len(v_text) > len(existing):
                        merged[m_num][s_num][v_num] = v_text

    # Build output JSON
    output_mandalas = []
    total_suktas = 0
    total_verses = 0

    for m_num in sorted(merged.keys()):
        suktas_out = []
        for s_num in sorted(merged[m_num].keys()):
            verses_out = []
            meta = merged_meta.get(m_num, {}).get(s_num, {})
            for v_num in sorted(merged[m_num][s_num].keys()):
                verses_out.append({
                    "n": v_num,
                    "bengali_ocr": merged[m_num][s_num][v_num],
                    "confidence": "raw",
                })
            if verses_out:
                sukta_obj = {
                    "n": s_num,
                    "verses": verses_out,
                }
                if meta.get("devata"):
                    sukta_obj["devata_ocr"] = meta["devata"]
                if meta.get("rishi"):
                    sukta_obj["rishi_ocr"] = meta["rishi"]
                suktas_out.append(sukta_obj)
                total_suktas += 1
                total_verses += len(verses_out)

        if suktas_out:
            output_mandalas.append({
                "n": m_num,
                "suktas": suktas_out,
            })

    return {
        "title": "\u098b\u0997\u09cd\u09ac\u09c7\u09a6 \u09b8\u0982\u09b9\u09bf\u09a4\u09be",  # ঋগ্বেদ সংহিতা
        "title_en": "Rigveda Samhita",
        "translator": "Ramesh Chandra Dutta (\u09b0\u09ae\u09c7\u09b6\u099a\u09a8\u09cd\u09a6\u09cd\u09b0 \u09a6\u09a4\u09cd\u09a4)",
        "source": "archive.org OCR (Tesseract)",
        "source_urls": [
            f"https://archive.org/details/{SOURCES[k]['id']}"
            for k in SOURCES
        ],
        "ocr_quality": "raw (19th century Bengali script, Tesseract OCR, high noise)",
        "extraction_date": time.strftime("%Y-%m-%d"),
        "stats": {
            "mandalas_found": len(output_mandalas),
            "suktas_found": total_suktas,
            "verses_found": total_verses,
            "canonical_suktas": sum(MANDALA_SUKTA_COUNTS.values()),
            "canonical_verses": 10143,
            "coverage_sukta_pct": round(100 * total_suktas / sum(MANDALA_SUKTA_COUNTS.values()), 1),
            "coverage_verse_pct": round(100 * total_verses / 10143, 1),
        },
        "mandalas": output_mandalas,
    }


def print_stats(parsed: dict) -> None:
    """Print parsing statistics for a source."""
    stats = parsed["stats"]
    mandalas = parsed["mandalas"]

    print(f"\n  Parsing stats for '{parsed['source']}':")
    print(f"    Total lines: {stats['total_lines']:,}")
    print(f"    Mandala headers found: {stats['mandala_headers_found']}")
    print(f"    Sukta headers found: {stats['sukta_headers_found']}")
    print(f"    Verse starts found: {stats['verse_starts_found']}")
    print(f"    Page headers skipped: {stats['page_headers_skipped']}")
    print(f"    Footnotes skipped: {stats['footnotes_skipped']}")

    print(f"\n    Mandalas extracted: {len(mandalas)}")
    for m_num in sorted(mandalas.keys()):
        suktas = mandalas[m_num]
        total_v = sum(len(s["verses"]) for s in suktas.values())
        canonical = MANDALA_SUKTA_COUNTS.get(m_num, "?")
        print(f"      Mandala {m_num}: {len(suktas)} suktas ({canonical} canonical), {total_v} verses")


# ─── "No mandala header" fallback parser ─────────────────────────────────────

def parse_vol1_fallback(text: str, source_key: str) -> dict:
    """Fallback parser for Vol 1 (the 1885 original scan).

    Vol 1 uses an ashtaka/adhyaya structure rather than mandala/sukta.
    The OCR is particularly noisy. We use the fact that Vol 1 covers
    mandala 1 only (ashtaka 1, adhyaya 1-8) and try to extract sukta
    numbers from header patterns like "৮১ সুক্ত" or "N সুক্ত".

    We assume all content is mandala 1 for this volume.
    """
    lines = text.split("\n")
    src = SOURCES[source_key]

    mandalas = {1: {}}
    current_sukta = None
    current_verse_num = None
    current_verse_lines = []
    current_sukta_meta = {}

    stats = {
        "total_lines": len(lines),
        "mandala_headers_found": 0,
        "sukta_headers_found": 0,
        "verse_starts_found": 0,
        "page_headers_skipped": 0,
        "footnotes_skipped": 0,
    }

    def flush_verse():
        nonlocal current_verse_lines, current_verse_num
        if current_verse_num and current_verse_lines and current_sukta:
            verse_text = " ".join(current_verse_lines).strip()
            if verse_text and len(verse_text) > 5:
                if current_sukta not in mandalas[1]:
                    mandalas[1][current_sukta] = {
                        "meta": current_sukta_meta.copy(),
                        "verses": {},
                    }
                mandalas[1][current_sukta]["verses"][current_verse_num] = verse_text
        current_verse_lines = []

    # Skip initial pages (preface, TOC) - start looking after ~300 lines
    start_line = 0
    for i, raw_line in enumerate(lines):
        # Look for first sukta header or verse marker
        if detect_sukta_header(raw_line.strip()):
            start_line = max(0, i - 5)
            break
        if i > 100 and detect_verse_start(raw_line.strip()):
            start_line = max(0, i - 5)
            break

    for i in range(start_line, len(lines)):
        line = clean_line(lines[i])
        if not line:
            continue

        if is_page_header(line):
            stats["page_headers_skipped"] += 1
            continue

        if is_footnote(line):
            stats["footnotes_skipped"] += 1
            continue

        # Check for sukta header
        sukta_info = detect_sukta_header(line)
        if sukta_info:
            flush_verse()
            current_sukta = sukta_info["sukta_num"]
            current_sukta_meta = {
                "devata": sukta_info.get("devata"),
                "rishi": sukta_info.get("rishi"),
            }
            current_verse_num = None
            stats["sukta_headers_found"] += 1
            continue

        # Check for verse start
        verse_num = detect_verse_start(line)
        if verse_num:
            flush_verse()
            current_verse_num = verse_num
            stats["verse_starts_found"] += 1
            stripped = line.strip()
            m = re.match(r"^[\u09e6-\u09ef\d]+\s*[।॥\.\)]\s*", stripped)
            if m:
                remainder = stripped[m.end():]
            else:
                remainder = stripped
            if remainder:
                current_verse_lines.append(remainder)
            continue

        if current_verse_num and line.strip():
            current_verse_lines.append(line.strip())

    flush_verse()

    return {
        "source": source_key,
        "source_info": src,
        "stats": stats,
        "mandalas": mandalas,
    }


def split_inline_verses(text: str) -> list:
    """Split paragraph text containing inline verse numbers into individual verses.

    Vol 2 has Bengali translation where verses are numbered inline:
    "১। verse one text... ২। verse two text... ৩। verse three text..."

    Returns: [(verse_num, verse_text), ...]
    """
    # Split on verse number patterns: N। or N. or N1 (with Bengali numerals)
    # The pattern is: number followed by danda/period/space, at word boundary
    parts = re.split(
        r"(?:^|\s)([\u09e6-\u09ef]+)\s*[।॥\.\)]\s*",
        text,
    )

    verses = []
    # parts alternates: [pre-text, num1, text1, num2, text2, ...]
    i = 0
    while i < len(parts):
        if i + 1 < len(parts):
            num_str = parts[i].strip()
            num = bengali_to_int(num_str)
            if num and 1 <= num <= 50:
                verse_text = parts[i + 1].strip() if i + 1 < len(parts) else ""
                if verse_text and len(verse_text) > 5:
                    verses.append((num, verse_text))
                i += 2
                continue
        i += 1

    return verses


def parse_vol2_structured(text: str, source_key: str) -> dict:
    """Parser for Vol 2 which has clearer mandala/sukta structure.

    Vol 2 (Rikveda Samhita, 2nd volume) has:
    - Clear mandala headers ("ষষ্ঠ মণ্ডল", "সপ্তম মণ্ডল", etc.)
    - Sukta headers: "N সূক্ত ।। devata দেবতা। rishi ঋষি। chanda ছন্দ।"
    - Sanskrit text (Bengali-script) followed by "অনুবাদ" then Bengali translation
    - Bengali translation has verse numbers INLINE within paragraphs
    - Page headers: "N ঋগ্বেদ-সংহিতা [N মণ্ডল"

    Strategy:
    1. Detect mandala and sukta headers
    2. Accumulate text in "অনুবাদ" (translation) sections
    3. Split inline verse numbers from accumulated translation text
    4. Skip Sanskrit text sections (between sukta header and অনুবাদ)
    5. Skip টীকা (commentary) sections
    """
    lines = text.split("\n")
    src = SOURCES[source_key]

    mandalas = {}
    current_mandala = None
    current_sukta = None
    current_sukta_meta = {}
    in_translation = False  # Are we in অনুবাদ section?
    translation_lines = []  # Accumulated translation paragraph lines

    stats = {
        "total_lines": len(lines),
        "mandala_headers_found": 0,
        "sukta_headers_found": 0,
        "verse_starts_found": 0,
        "page_headers_skipped": 0,
        "footnotes_skipped": 0,
    }

    def flush_translation():
        """Parse accumulated translation text into individual verses."""
        nonlocal translation_lines, in_translation
        if not translation_lines or not current_mandala or not current_sukta:
            translation_lines = []
            return

        # Join all translation lines into one text block
        full_text = " ".join(translation_lines)
        translation_lines = []

        if not full_text.strip():
            return

        # Split into individual verses by inline verse numbers
        # Pattern: N। or N. (Bengali numerals)
        verse_pattern = re.compile(
            r"(?:^|\s+)([\u09e6-\u09ef]+)\s*[।॥\.\)1]\s*"
        )

        # Find all verse number positions
        matches = list(verse_pattern.finditer(full_text))
        if not matches:
            # No inline verse numbers found - store as verse 1
            if len(full_text.strip()) > 10:
                store_verse(1, full_text.strip())
                stats["verse_starts_found"] += 1
            return

        for idx, match in enumerate(matches):
            num = bengali_to_int(match.group(1))
            if num is None or num < 1 or num > 50:
                continue

            start = match.end()
            if idx + 1 < len(matches):
                end = matches[idx + 1].start()
            else:
                end = len(full_text)

            verse_text = full_text[start:end].strip()
            if verse_text and len(verse_text) > 5:
                store_verse(num, verse_text)
                stats["verse_starts_found"] += 1

    def store_verse(verse_num: int, verse_text: str):
        """Store a verse in the data structure."""
        if current_mandala not in mandalas:
            mandalas[current_mandala] = {}
        if current_sukta not in mandalas[current_mandala]:
            mandalas[current_mandala][current_sukta] = {
                "meta": current_sukta_meta.copy(),
                "verses": {},
            }
        # Keep longer version if duplicate
        existing = mandalas[current_mandala][current_sukta]["verses"].get(verse_num, "")
        if len(verse_text) > len(existing):
            mandalas[current_mandala][current_sukta]["verses"][verse_num] = verse_text

    # Skip preface/TOC - find where actual mandala content starts
    start_line = 0
    for i, raw_line in enumerate(lines):
        m_num = detect_mandala_header(raw_line.strip())
        if m_num and m_num >= 6:
            start_line = i
            break

    for i in range(start_line, len(lines)):
        line = clean_line(lines[i])
        if not line:
            continue

        # Skip page headers (lines with সংহিতা + mandala/sukta numbering)
        if is_page_header(line):
            stats["page_headers_skipped"] += 1
            continue

        # Check for mandala header
        mandala_num = detect_mandala_header(line)
        if mandala_num and mandala_num >= 6:
            flush_translation()
            current_mandala = mandala_num
            current_sukta = None
            in_translation = False
            stats["mandala_headers_found"] += 1
            continue

        # Check for sukta header
        sukta_info = detect_sukta_header(line)
        if sukta_info:
            flush_translation()
            current_sukta = sukta_info["sukta_num"]
            current_sukta_meta = {
                "devata": sukta_info.get("devata"),
                "rishi": sukta_info.get("rishi"),
            }
            in_translation = False
            stats["sukta_headers_found"] += 1
            continue

        # Detect start of translation section
        if "অনুবাদ" in line:
            flush_translation()
            in_translation = True
            # The rest of this line after "অনুবাদ" may contain verse text
            m = re.search(r"অনুবাদ\s*[£:৪]*\s*", line)
            if m:
                remainder = line[m.end():].strip()
                if remainder and len(remainder) > 5:
                    translation_lines.append(remainder)
            continue

        # Detect start of commentary section (end of translation)
        if line.strip().startswith("টীকা") or line.strip().startswith("টকা"):
            flush_translation()
            in_translation = False
            continue

        # Detect Sanskrit lines - skip them
        # Sanskrit lines in Bengali script end with ॥ N pattern
        if re.search(r"॥\s*[\u09e6-\u09ef\d]+\s*$", line):
            # Don't set in_translation=False; Sanskrit might be interspersed
            continue

        # If we're in a translation section, accumulate
        if in_translation and current_sukta:
            # Skip footnote references
            if is_footnote(line):
                stats["footnotes_skipped"] += 1
                continue
            translation_lines.append(line.strip())
            continue

        # If not in translation section but have a sukta,
        # check if line starts with Bengali numeral (verse marker)
        # This handles cases where "অনুবাদ" label is missing
        if current_sukta and not in_translation:
            verse_num = detect_verse_start(line)
            if verse_num:
                if not translation_lines:
                    in_translation = True
                stripped = line.strip()
                m = re.match(r"^[\u09e6-\u09ef\d]+\s*[।॥\.\)]\s*", stripped)
                if m:
                    translation_lines.append(stripped)
                else:
                    translation_lines.append(stripped)

    # Flush last translation
    flush_translation()

    return {
        "source": source_key,
        "source_info": src,
        "stats": stats,
        "mandalas": mandalas,
    }


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract Bengali Rigveda OCR text from archive.org"
    )
    parser.add_argument(
        "--source",
        choices=["combined", "vol1", "vol2", "vol4", "all"],
        default="all",
        help="Which source to download and parse (default: all)",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_DIR / "archive_ocr_bengali.json"),
        help="Output JSON file path",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Print sample verses after parsing",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Determine which sources to process
    if args.source == "all":
        source_keys = ["vol1", "vol2", "vol4", "combined"]
    else:
        source_keys = [args.source]

    parsed_sources = []

    for key in source_keys:
        print(f"\n{'='*60}")
        print(f"Processing: {SOURCES[key]['description']}")
        print(f"{'='*60}")

        # Download
        text = download_ocr_text(key)

        # Parse with appropriate parser
        if key == "vol1":
            parsed = parse_vol1_fallback(text, key)
        elif key == "vol2":
            parsed = parse_vol2_structured(text, key)
        elif key == "combined":
            parsed = parse_ocr_text(text, key)
        else:
            # vol4 - try standard parser first, fallback if needed
            parsed = parse_ocr_text(text, key)
            if not parsed["mandalas"]:
                print("  Standard parser found nothing, trying fallback...")
                parsed = parse_vol1_fallback(text, key)

        print_stats(parsed)
        parsed_sources.append(parsed)

    # Build merged output
    print(f"\n{'='*60}")
    print("Building merged JSON output...")
    print(f"{'='*60}")

    output = build_json_output(parsed_sources)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nOutput written to: {output_path}")
    print(f"  File size: {output_path.stat().st_size:,} bytes")

    # Print summary
    s = output["stats"]
    print(f"\n  Summary:")
    print(f"    Mandalas: {s['mandalas_found']} / 10")
    print(f"    Suktas:   {s['suktas_found']} / {s['canonical_suktas']}")
    print(f"    Verses:   {s['verses_found']} / {s['canonical_verses']}")
    print(f"    Coverage: {s['coverage_sukta_pct']}% suktas, {s['coverage_verse_pct']}% verses")

    # Print sample verses
    if args.sample:
        print(f"\n{'='*60}")
        print("Sample verses:")
        print(f"{'='*60}")
        for m in output["mandalas"][:2]:
            for s_obj in m["suktas"][:2]:
                for v in s_obj["verses"][:3]:
                    print(f"\n  Mandala {m['n']}, Sukta {s_obj['n']}, Verse {v['n']}:")
                    text_preview = v["bengali_ocr"][:200]
                    print(f"    {text_preview}")

    return output


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare Bengali Rigveda sources: archive.org OCR vs other structured data.

Loads archive_ocr_bengali.json and rigveda-complete.json (or ebanglalibrary_bengali.json
if it exists) and compares verse counts, coverage, and alignment.

Usage:
    python3 vedas/scripts/compare_sources.py

Output: console report with coverage statistics and gaps.

Constraints: Python 3.9.6 stdlib only.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"
SEEDS_DIR = SCRIPT_DIR.parent / "seeds"

# Canonical Rigveda structure
MANDALA_SUKTA_COUNTS = {
    1: 191, 2: 43, 3: 62, 4: 58, 5: 87,
    6: 75, 7: 104, 8: 103, 9: 114, 10: 191,
}

# Canonical verse counts per mandala (approximate, from Shakala recension)
MANDALA_VERSE_COUNTS = {
    1: 2006, 2: 429, 3: 617, 4: 589, 5: 727,
    6: 765, 7: 841, 8: 1726, 9: 1108, 10: 1754,
}


def load_archive_ocr() -> Optional[dict]:
    """Load archive_ocr_bengali.json."""
    path = OUTPUT_DIR / "archive_ocr_bengali.json"
    if not path.exists():
        print(f"[WARN] Archive OCR data not found: {path}")
        print("  Run extract_archive_ocr.py first.")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_rigveda_complete() -> Optional[dict]:
    """Load rigveda-complete.json (from build_rigveda.py)."""
    path = SEEDS_DIR / "rigveda-complete.json"
    if not path.exists():
        print(f"[WARN] Rigveda complete data not found: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_ebanglalibrary() -> Optional[dict]:
    """Load ebanglalibrary_bengali.json if it exists."""
    for candidate in [
        OUTPUT_DIR / "ebanglalibrary_bengali.json",
        SCRIPT_DIR / "ebanglalibrary_bengali.json",
        SEEDS_DIR / "ebanglalibrary_bengali.json",
    ]:
        if candidate.exists():
            with open(candidate, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def extract_verse_map(data: dict) -> dict:
    """Extract a flat mapping of (mandala, sukta, verse) -> text from JSON data.

    Handles both output formats:
    - Archive OCR format: {"mandalas": [{"n": 1, "suktas": [{"n": 1, "verses": [{"n": 1, "bengali_ocr": "..."}]}]}]}
    - Rigveda complete format: {"mandalas": [{"num": 1, "suktas": [{"sukta_num": 1, "mantras": [{"num": 1, ...}]}]}]}
    """
    verse_map = {}

    mandalas = data.get("mandalas", [])
    for m in mandalas:
        m_num = m.get("n") or m.get("num")
        if not m_num:
            continue

        suktas = m.get("suktas", [])
        for s in suktas:
            s_num = s.get("n") or s.get("sukta_num")
            if not s_num:
                continue

            verses = s.get("verses") or s.get("mantras", [])
            for v in verses:
                v_num = v.get("n") or v.get("num")
                if not v_num:
                    continue

                # Get text from whichever field exists
                text = (
                    v.get("bengali_ocr")
                    or v.get("meaning_bn")
                    or v.get("sa_bengali")
                    or v.get("meaning_en", "")
                )
                verse_map[(int(m_num), int(s_num), int(v_num))] = text

    return verse_map


def count_by_mandala(verse_map: dict) -> dict:
    """Group verse counts by mandala."""
    counts = {}
    for (m, s, v), text in verse_map.items():
        if m not in counts:
            counts[m] = {"suktas": set(), "verses": 0}
        counts[m]["suktas"].add(s)
        counts[m]["verses"] += 1
    return counts


def count_by_mandala_sukta(verse_map: dict) -> dict:
    """Group verse counts by (mandala, sukta)."""
    counts = {}
    for (m, s, v), text in verse_map.items():
        key = (m, s)
        if key not in counts:
            counts[key] = 0
        counts[key] += 1
    return counts


def print_header(title: str, width: int = 70) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*width}")
    print(f"  {title}")
    print(f"{'='*width}")


def print_source_summary(name: str, verse_map: dict) -> None:
    """Print summary statistics for a source."""
    by_mandala = count_by_mandala(verse_map)
    total_suktas = sum(len(v["suktas"]) for v in by_mandala.values())
    total_verses = sum(v["verses"] for v in by_mandala.values())

    print(f"\n  {name}:")
    print(f"    Mandalas: {len(by_mandala)} / 10")
    print(f"    Suktas:   {total_suktas} / {sum(MANDALA_SUKTA_COUNTS.values())}")
    print(f"    Verses:   {total_verses} / {sum(MANDALA_VERSE_COUNTS.values())}")
    print()
    print(f"    {'Mandala':>10} {'Suktas':>10} {'(Canon)':>10} {'Verses':>10} {'(~Canon)':>10} {'Coverage':>10}")
    print(f"    {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

    for m_num in range(1, 11):
        if m_num in by_mandala:
            s_count = len(by_mandala[m_num]["suktas"])
            v_count = by_mandala[m_num]["verses"]
        else:
            s_count = 0
            v_count = 0
        canon_s = MANDALA_SUKTA_COUNTS[m_num]
        canon_v = MANDALA_VERSE_COUNTS[m_num]
        pct = f"{100*v_count/canon_v:.0f}%" if canon_v > 0 else "N/A"
        print(f"    {m_num:>10} {s_count:>10} {canon_s:>10} {v_count:>10} {canon_v:>10} {pct:>10}")


def compare_two_sources(
    name_a: str, map_a: dict,
    name_b: str, map_b: dict,
) -> None:
    """Compare two sources and report alignment."""
    keys_a = set(map_a.keys())
    keys_b = set(map_b.keys())

    both = keys_a & keys_b
    only_a = keys_a - keys_b
    only_b = keys_b - keys_a

    print(f"\n  Overlap:")
    print(f"    Verses in both:     {len(both):,}")
    print(f"    Only in {name_a:15s}: {len(only_a):,}")
    print(f"    Only in {name_b:15s}: {len(only_b):,}")

    # Per-mandala comparison
    print(f"\n    {'Mandala':>10} {'Both':>8} {'Only '+name_a[:6]:>12} {'Only '+name_b[:6]:>12}")
    print(f"    {'-'*10} {'-'*8} {'-'*12} {'-'*12}")

    for m_num in range(1, 11):
        both_m = sum(1 for (m, s, v) in both if m == m_num)
        only_a_m = sum(1 for (m, s, v) in only_a if m == m_num)
        only_b_m = sum(1 for (m, s, v) in only_b if m == m_num)
        print(f"    {m_num:>10} {both_m:>8} {only_a_m:>12} {only_b_m:>12}")


def find_gaps(verse_map: dict, name: str) -> None:
    """Report gaps in a source - missing mandalas, suktas, or large verse gaps."""
    by_ms = count_by_mandala_sukta(verse_map)
    by_m = count_by_mandala(verse_map)

    print(f"\n  Gaps in {name}:")

    # Missing mandalas
    missing_mandalas = [m for m in range(1, 11) if m not in by_m]
    if missing_mandalas:
        print(f"    Missing mandalas: {missing_mandalas}")

    # Missing suktas (where we have the mandala but not all suktas)
    for m_num in range(1, 11):
        if m_num not in by_m:
            continue
        present = by_m[m_num]["suktas"]
        expected = set(range(1, MANDALA_SUKTA_COUNTS[m_num] + 1))
        missing = sorted(expected - present)
        if missing:
            # Compress into ranges for readability
            ranges = []
            start = missing[0]
            end = missing[0]
            for n in missing[1:]:
                if n == end + 1:
                    end = n
                else:
                    if start == end:
                        ranges.append(str(start))
                    else:
                        ranges.append(f"{start}-{end}")
                    start = n
                    end = n
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")

            total_missing = len(missing)
            total_expected = MANDALA_SUKTA_COUNTS[m_num]
            if total_missing <= 20:
                range_str = ", ".join(ranges)
            else:
                range_str = ", ".join(ranges[:5]) + f" ... (+{total_missing - 5} more)"
            print(f"    Mandala {m_num}: missing {total_missing}/{total_expected} suktas: [{range_str}]")


def print_sample_comparison(
    name_a: str, map_a: dict,
    name_b: str, map_b: dict,
    n: int = 3,
) -> None:
    """Print sample verses that exist in both sources for manual comparison."""
    keys_both = sorted(set(map_a.keys()) & set(map_b.keys()))
    if not keys_both:
        print(f"\n  No overlapping verses to compare.")
        return

    print(f"\n  Sample overlapping verses (first {n}):")
    for m, s, v in keys_both[:n]:
        print(f"\n    --- Mandala {m}, Sukta {s}, Verse {v} ---")
        text_a = map_a[(m, s, v)][:150]
        text_b = map_b[(m, s, v)][:150]
        print(f"    [{name_a}]: {text_a}")
        print(f"    [{name_b}]: {text_b}")


def main():
    print_header("Bengali Rigveda Source Comparison")

    # Load sources
    sources = {}

    ocr_data = load_archive_ocr()
    if ocr_data:
        sources["Archive OCR"] = extract_verse_map(ocr_data)
        print(f"  Loaded Archive OCR: {len(sources['Archive OCR']):,} verses")

    rc_data = load_rigveda_complete()
    if rc_data:
        sources["RV Complete"] = extract_verse_map(rc_data)
        print(f"  Loaded RV Complete: {len(sources['RV Complete']):,} verses")

    ebl_data = load_ebanglalibrary()
    if ebl_data:
        sources["eBangla"] = extract_verse_map(ebl_data)
        print(f"  Loaded eBangla: {len(sources['eBangla']):,} verses")

    if not sources:
        print("\n  [ERROR] No sources found. Run extraction scripts first.")
        sys.exit(1)

    # Print individual summaries
    print_header("Individual Source Coverage")
    for name, verse_map in sources.items():
        print_source_summary(name, verse_map)

    # Print gaps
    print_header("Gap Analysis")
    for name, verse_map in sources.items():
        find_gaps(verse_map, name)

    # Pairwise comparisons
    source_names = list(sources.keys())
    if len(source_names) >= 2:
        print_header("Source Comparisons")
        for i in range(len(source_names)):
            for j in range(i + 1, len(source_names)):
                name_a = source_names[i]
                name_b = source_names[j]
                compare_two_sources(
                    name_a, sources[name_a],
                    name_b, sources[name_b],
                )
                print_sample_comparison(
                    name_a, sources[name_a],
                    name_b, sources[name_b],
                )

    print_header("Summary")
    for name, verse_map in sources.items():
        total = len(verse_map)
        canon = sum(MANDALA_VERSE_COUNTS.values())
        print(f"  {name:20s}: {total:>6,} / {canon:>6,} verses ({100*total/canon:.1f}%)")

    print()


if __name__ == "__main__":
    main()

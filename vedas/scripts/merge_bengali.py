#!/usr/bin/env python3
"""
Merge Bengali Rigveda translations from multiple sources into a single
unified JSON file.

Sources (in priority order):
  1. ebanglalibrary.com (Ramesh Chandra Dutta) -- highest quality, Unicode HTML
  2. RKM per-Mandala PDFs (Ramakrishna Mission) -- scholarly, extracted from PDF
  3. archive.org OCR (Ramesh Chandra Dutta scans) -- lowest quality, OCR artifacts

Also loads:
  - vedas/seeds/rigveda-complete.json for canonical verse structure
  - vedas/seeds/hymns.json for hand-curated Bengali meanings

Output:
  - vedas/scripts/output/rigveda_bengali_merged.json

Usage:
  python3 merge_bengali.py                    # merge all available sources
  python3 merge_bengali.py --stats            # just print coverage statistics
  python3 merge_bengali.py --mandala 2        # only merge mandala 2
"""

import argparse
import json
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent  # vedas/
OUTPUT_DIR = SCRIPT_DIR / "output"

# Source files
RIGVEDA_COMPLETE = PROJECT_DIR / "seeds" / "rigveda-complete.json"
HYMNS_CURATED = PROJECT_DIR / "seeds" / "hymns.json"

# Bengali extraction outputs
EBANGLALIBRARY_JSON = OUTPUT_DIR / "ebanglalibrary_bengali.json"
RKM_JSON = OUTPUT_DIR / "rkm_bengali.json"
ARCHIVE_OCR_JSON = OUTPUT_DIR / "archive_ocr_bengali.json"

# Merged output
MERGED_OUTPUT = OUTPUT_DIR / "rigveda_bengali_merged.json"

# Total expected mantras in Rigveda
TOTAL_MANTRAS = 10143

EXPECTED_MANTRAS = {
    1: 1979, 2: 430, 3: 619, 4: 588, 5: 725,
    6: 766, 7: 843, 8: 1331, 9: 1108, 10: 1754,
}


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_json_safe(path, description=""):
    """Load a JSON file, returning None if not found."""
    if not path.exists():
        print(f"  [{description or path.name}] Not found: {path}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        size_kb = path.stat().st_size / 1024
        print(f"  [{description or path.name}] Loaded ({size_kb:.0f} KB)")
        return data
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"  [{description or path.name}] Error loading: {e}")
        return None


def load_rigveda_structure():
    """Load the canonical Rigveda verse structure."""
    data = load_json_safe(RIGVEDA_COMPLETE, "rigveda-complete")
    if not data:
        print("ERROR: rigveda-complete.json is required for verse structure.")
        print(f"  Expected at: {RIGVEDA_COMPLETE}")
        sys.exit(1)
    return data


def load_curated_bengali():
    """
    Load hand-curated Bengali meanings from hymns.json.
    Returns a dict: (mandala, sukta, verse) -> bengali_text

    hymns.json structure:
      {"mandalas": [{"num": 1, "suktas": [{"sukta_num": 1, "mantras": [...]}]}]}
    """
    data = load_json_safe(HYMNS_CURATED, "hymns.json (curated)")
    if not data:
        return {}

    curated = {}

    # Primary structure: mandalas -> suktas -> mantras
    for mandala in data.get("mandalas", []):
        m = mandala.get("num", 0)
        for sukta in mandala.get("suktas", []):
            s = sukta.get("sukta_num", 0)
            for mantra in sukta.get("mantras", []):
                v = mantra.get("num", 0)
                bn = mantra.get("meaning_bn", "")
                if bn and m and s and v:
                    curated[(m, s, v)] = bn

    # Fallback: flat suktas list (older format)
    for sukta in data.get("suktas", []):
        m = sukta.get("mandala_num") or sukta.get("mandala", 0)
        s = sukta.get("sukta_num") or sukta.get("sukta", 0)
        for mantra in sukta.get("mantras", []):
            v = mantra.get("num", 0)
            bn = mantra.get("meaning_bn", "")
            if bn and m and s and v:
                curated.setdefault((m, s, v), bn)

    return curated


def build_source_index(data, source_name, text_key="bengali_rkm"):
    """
    Build a lookup index from a source JSON.
    Returns: dict of (mandala, sukta, verse) -> text

    Handles two common structures:
      1. {"mandalas": [{"n": 1, "suktas": [{"n": 1, "verses": [{"n": 1, "bengali_X": "..."}]}]}]}
      2. {"mandalas": [{"n": 1, "suktas": [{"n": 1, "verses": [{"n": 1, "text": "..."}]}]}]}
    """
    if not data:
        return {}

    index = {}
    for mandala in data.get("mandalas", []):
        m = mandala.get("n", 0)
        for sukta in mandala.get("suktas", []):
            s = sukta.get("n", 0)
            for verse in sukta.get("verses", []):
                v = verse.get("n", 0)
                # Try multiple text keys
                text = ""
                for key in [text_key, "text", "bengali", "meaning_bn",
                            "bengali_rkm", "bengali_ebl", "bengali_ocr"]:
                    text = verse.get(key, "")
                    if text:
                        break
                if text and m and s and v:
                    index[(m, s, v)] = text

    return index


# ---------------------------------------------------------------------------
# Merging
# ---------------------------------------------------------------------------

def merge_bengali(structure, sources, mandala_filter=None):
    """
    Merge Bengali translations from multiple sources into the canonical
    Rigveda structure.

    Args:
        structure: rigveda-complete.json data (canonical structure)
        sources: list of (name, priority, index_dict) tuples, highest priority first
        mandala_filter: if set, only merge this mandala number

    Returns:
        merged data structure and coverage statistics
    """
    merged_mandalas = []
    total_stats = {
        "total_mantras": 0,
        "mantras_with_bengali": 0,
        "source_counts": {name: 0 for name, _, _ in sources},
        "per_mandala": [],
    }

    for mandala in structure.get("mandalas", []):
        m_num = mandala.get("num", 0)

        if mandala_filter and m_num != mandala_filter:
            continue

        m_stats = {
            "mandala": m_num,
            "total_mantras": 0,
            "with_bengali": 0,
            "source_counts": {name: 0 for name, _, _ in sources},
        }

        merged_suktas = []
        for sukta in mandala.get("suktas", []):
            s_num = sukta.get("sukta_num", 0)

            merged_mantras = []
            for mantra in sukta.get("mantras", []):
                v_num = mantra.get("num", 0)
                key = (m_num, s_num, v_num)

                m_stats["total_mantras"] += 1
                total_stats["total_mantras"] += 1

                # Find best Bengali translation
                best_text = None
                best_source = None
                all_texts = {}

                for name, priority, index in sources:
                    text = index.get(key, "")
                    if text:
                        all_texts[name] = text
                        if best_text is None:
                            best_text = text
                            best_source = name

                merged_mantra = {
                    "num": v_num,
                    "sa_devanagari": mantra.get("sa_devanagari", ""),
                    "sa_bengali": mantra.get("sa_bengali", ""),
                    "meaning_en": mantra.get("meaning_en", ""),
                }

                if best_text:
                    merged_mantra["meaning_bn"] = best_text
                    merged_mantra["meaning_bn_source"] = best_source
                    m_stats["with_bengali"] += 1
                    total_stats["mantras_with_bengali"] += 1
                    m_stats["source_counts"][best_source] += 1
                    total_stats["source_counts"][best_source] += 1

                    # Include alternate translations if available
                    if len(all_texts) > 1:
                        alts = {k: v for k, v in all_texts.items() if k != best_source}
                        if alts:
                            merged_mantra["meaning_bn_alt"] = alts

                merged_mantras.append(merged_mantra)

            merged_suktas.append({
                "sukta_num": s_num,
                "title": sukta.get("title", ""),
                "mantras": merged_mantras,
            })

        merged_mandalas.append({
            "num": m_num,
            "suktas": merged_suktas,
        })

        total_stats["per_mandala"].append(m_stats)

    merged = {
        "title": "ঋগ্বেদ সংহিতা - Bengali Merged",
        "title_en": "Rigveda Samhita - Bengali Translations Merged",
        "merge_date": time.strftime("%Y-%m-%d"),
        "source_priority": [name for name, _, _ in sources],
        "sources": {
            "curated": "Hand-curated Bengali meanings from vedas/seeds/hymns.json",
            "ebanglalibrary": "Ramesh Chandra Dutta, ebanglalibrary.com (Unicode HTML)",
            "rkm": "Ramakrishna Mission Institute of Culture (per-Mandala PDFs)",
            "archive_ocr": "Ramesh Chandra Dutta, archive.org (OCR from scanned pages)",
        },
        "mandalas": merged_mandalas,
    }

    return merged, total_stats


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def print_coverage_stats(stats, sources):
    """Print a detailed coverage report."""
    print("\n" + "=" * 70)
    print("Bengali Rigveda Coverage Report")
    print("=" * 70)

    # Per-mandala table
    source_names = [name for name, _, _ in sources]
    header = f"{'Mandala':<10} {'Mantras':<10} {'Bengali':<10} {'%':<8}"
    for name in source_names:
        header += f" {name[:8]:<10}"
    print(header)
    print("-" * 70)

    for ms in stats["per_mandala"]:
        m = ms["mandala"]
        total = ms["total_mantras"]
        bn = ms["with_bengali"]
        pct = f"{bn/total*100:.1f}%" if total else "0%"
        row = f"  {m:<8} {total:<10} {bn:<10} {pct:<8}"
        for name in source_names:
            count = ms["source_counts"].get(name, 0)
            row += f" {count:<10}"
        print(row)

    print("-" * 70)

    # Totals
    total = stats["total_mantras"]
    bn = stats["mantras_with_bengali"]
    pct = f"{bn/total*100:.1f}%" if total else "0%"
    row = f"  {'TOTAL':<8} {total:<10} {bn:<10} {pct:<8}"
    for name in source_names:
        count = stats["source_counts"].get(name, 0)
        row += f" {count:<10}"
    print(row)

    print()
    print(f"Total mantras in Rigveda: {TOTAL_MANTRAS}")
    print(f"Mantras processed: {total}")
    print(f"Mantras with Bengali meaning: {bn} ({bn/TOTAL_MANTRAS*100:.1f}% of full Rigveda)")
    print()

    # Source breakdown
    print("Source contribution:")
    for name in source_names:
        count = stats["source_counts"].get(name, 0)
        if count > 0:
            print(f"  {name}: {count} mantras ({count/TOTAL_MANTRAS*100:.1f}%)")

    # Missing sources
    print()
    for name in source_names:
        count = stats["source_counts"].get(name, 0)
        if count == 0:
            print(f"  Note: '{name}' contributed 0 mantras (file may not exist yet)")

    print("=" * 70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Merge Bengali Rigveda translations from multiple sources"
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="Just print coverage statistics without writing output"
    )
    parser.add_argument(
        "--mandala", "-m", type=int,
        help="Only merge this mandala number"
    )
    parser.add_argument(
        "--output", "-o", type=str,
        default=str(MERGED_OUTPUT),
        help="Output JSON path"
    )
    args = parser.parse_args()

    print("Loading sources...")

    # Load canonical structure
    structure = load_rigveda_structure()

    # Load curated Bengali (highest priority)
    curated = load_curated_bengali()
    print(f"    Curated: {len(curated)} mantras")

    # Load extraction outputs
    ebl_data = load_json_safe(EBANGLALIBRARY_JSON, "ebanglalibrary")
    rkm_data = load_json_safe(RKM_JSON, "rkm")
    ocr_data = load_json_safe(ARCHIVE_OCR_JSON, "archive_ocr")

    # Build source indices
    ebl_index = build_source_index(ebl_data, "ebanglalibrary", "bengali_ebl")
    rkm_index = build_source_index(rkm_data, "rkm", "bengali_rkm")
    ocr_index = build_source_index(ocr_data, "archive_ocr", "bengali_ocr")

    print(f"    ebanglalibrary index: {len(ebl_index)} mantras")
    print(f"    RKM index: {len(rkm_index)} mantras")
    print(f"    archive_ocr index: {len(ocr_index)} mantras")

    # Also check if rigveda-complete.json already has meaning_bn
    existing_bn = {}
    for mandala in structure.get("mandalas", []):
        m = mandala.get("num", 0)
        for sukta in mandala.get("suktas", []):
            s = sukta.get("sukta_num", 0)
            for mantra in sukta.get("mantras", []):
                v = mantra.get("num", 0)
                bn = mantra.get("meaning_bn", "")
                if bn:
                    existing_bn[(m, s, v)] = bn
    print(f"    Existing in rigveda-complete.json: {len(existing_bn)} mantras")

    # Source priority order (highest first):
    #   1. curated (hand-verified, highest quality)
    #   2. existing_bn (already in rigveda-complete.json, presumably curated)
    #   3. ebanglalibrary (Unicode HTML, good quality)
    #   4. rkm (PDF extraction, variable quality)
    #   5. archive_ocr (OCR, lowest quality)
    sources = [
        ("curated", 1, curated),
        ("existing", 2, existing_bn),
        ("ebanglalibrary", 3, ebl_index),
        ("rkm", 4, rkm_index),
        ("archive_ocr", 5, ocr_index),
    ]

    print(f"\nMerging with priority: {' > '.join(name for name, _, _ in sources)}")

    # Merge
    merged, stats = merge_bengali(
        structure, sources,
        mandala_filter=args.mandala,
    )

    # Print statistics
    print_coverage_stats(stats, sources)

    # Write output
    if not args.stats:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"\nMerged output written to: {output_path} ({size_mb:.1f} MB)")
    else:
        print("\n(Stats mode: no output file written)")


if __name__ == "__main__":
    main()

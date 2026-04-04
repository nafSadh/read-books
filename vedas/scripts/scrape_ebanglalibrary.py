#!/usr/bin/env python3
"""
Scrape Ramesh Chandra Dutta's complete Bengali Rigveda translation
from ebanglalibrary.com.

Uses only Python 3.9 stdlib (no pip packages).
Outputs structured JSON with all 10 mandalas, 1028 suktas.

Usage:
    python3 scrape_ebanglalibrary.py                # full scrape
    python3 scrape_ebanglalibrary.py --test          # test: first 2 suktas only
    python3 scrape_ebanglalibrary.py --mandala 1     # scrape only mandala 1
    python3 scrape_ebanglalibrary.py --resume         # skip already-cached pages
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import re
import os
import sys
import time
import hashlib
from pathlib import Path
# html.parser not needed; parsing done via regex for simplicity

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://www.ebanglalibrary.com"
BOOK_PATH = (
    "/books/"
    "%E0%A6%8B%E0%A6%97%E0%A7%8D%E0%A6%AC%E0%A7%87%E0%A6%A6-"
    "%E0%A6%B8%E0%A6%82%E0%A6%B9%E0%A6%BF%E0%A6%A4%E0%A6%BE-"
    "%E0%A6%85%E0%A6%A8%E0%A7%81%E0%A6%AC%E0%A6%BE%E0%A6%A6-"
    "%E0%A6%B0%E0%A6%AE%E0%A7%87/"
)
BOOK_URL = BASE_URL + BOOK_PATH

CACHE_DIR = Path("/tmp/ebanglalibrary_cache")
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "ebanglalibrary_bengali.json"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DELAY_SECONDS = 1.5  # polite delay between requests

# Bengali digit mapping for parsing
BENGALI_DIGITS = {"০": 0, "১": 1, "২": 2, "৩": 3, "৪": 4,
                  "৫": 5, "৬": 6, "৭": 7, "৮": 8, "৯": 9}

# Mandala topic-list IDs used by LearnDash pagination.
# These map mandala index (1-10) to the ld-topic-page ID.
# Discovered from the live site. If they change, re-discover via
# the book page pagination links.
MANDALA_TOPIC_IDS = {
    1: 216468,
    2: 216470,
    3: 216471,
    4: 216472,
    5: 216473,
    6: 216474,
    7: 216475,
    8: 216476,
    9: 216477,
    # Mandala 10 shares pagination with mandala 1's container on some pages;
    # we discover all links dynamically, so this mapping is only used as a hint.
    10: None,
}

# Expected sukta counts per mandala (for validation)
EXPECTED_SUKTA_COUNTS = {
    1: 191, 2: 43, 3: 62, 4: 58, 5: 87,
    6: 75, 7: 104, 8: 103, 9: 114, 10: 191,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def bengali_to_int(s: str) -> int:
    """Convert a string of Bengali digits to an integer."""
    result = 0
    for ch in s:
        if ch in BENGALI_DIGITS:
            result = result * 10 + BENGALI_DIGITS[ch]
        elif ch.isdigit():
            result = result * 10 + int(ch)
    return result


def cache_key(url: str) -> str:
    """Return a filesystem-safe cache key for a URL."""
    return hashlib.sha256(url.encode()).hexdigest()


def fetch_html(url: str, use_cache: bool = True) -> str:
    """Fetch a URL, with optional disk caching."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cpath = CACHE_DIR / cache_key(url)

    if use_cache and cpath.exists():
        return cpath.read_text(encoding="utf-8")

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"  [HTTP {e.code}] {urllib.parse.unquote(url)[:80]}")
        raise
    except urllib.error.URLError as e:
        print(f"  [URL Error] {e.reason} - {urllib.parse.unquote(url)[:80]}")
        raise

    cpath.write_text(html, encoding="utf-8")
    return html


def clean_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    # Decode common HTML entities
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#8217;", "\u2019")
    text = text.replace("&#8216;", "\u2018")
    text = text.replace("&#8212;", "\u2014")
    text = text.replace("&#8211;", "\u2013")
    text = text.replace("&nbsp;", " ")
    # Numeric entities
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)
    return text.strip()


# ---------------------------------------------------------------------------
# Step 1: Discover all sukta topic URLs from the book page
# ---------------------------------------------------------------------------


def discover_all_topic_urls(mandala_filter=None):
    """
    Crawl the book page (with pagination) to collect all topic URLs.

    Returns a dict: {mandala_number: [(sukta_number, url), ...]}
    """
    print("Discovering all sukta URLs from the book page...")

    all_topic_urls = set()

    # First fetch the base book page (no pagination params)
    html = fetch_html(BOOK_URL, use_cache=True)
    topic_links = re.findall(
        r'href="(https://www\.ebanglalibrary\.com/topics/[^"]+)"', html
    )
    all_topic_urls.update(topic_links)
    print(f"  Base page: {len(topic_links)} topic links")

    # Discover all pagination IDs and max pages from the base page
    page_params = re.findall(r"ld-topic-page=(\d+)-(\d+)", html)
    pagination_ids = {}
    for tid, pn in page_params:
        tid = int(tid)
        pn = int(pn)
        pagination_ids[tid] = max(pagination_ids.get(tid, 0), pn)

    # We need to crawl page 2+ for each pagination ID to find remaining topics.
    # The base page shows page 1 of each mandala.
    # We also need to discover max pages progressively.
    visited_pages = set()
    visited_pages.add((0, 0))  # base page sentinel

    for tid, known_max in sorted(pagination_ids.items()):
        page = 2  # page 1 was already on the base page
        max_page = known_max
        while page <= max_page:
            if (tid, page) in visited_pages:
                page += 1
                continue
            visited_pages.add((tid, page))

            paged_url = f"{BOOK_URL}?ld-topic-page={tid}-{page}"
            print(f"  Fetching pagination: topic-list={tid} page={page}")
            time.sleep(DELAY_SECONDS)

            try:
                phtml = fetch_html(paged_url, use_cache=True)
            except Exception as e:
                print(f"    Error: {e}")
                page += 1
                continue

            links = re.findall(
                r'href="(https://www\.ebanglalibrary\.com/topics/[^"]+)"', phtml
            )
            new_count = len(set(links) - all_topic_urls)
            all_topic_urls.update(links)
            print(f"    Found {len(links)} links ({new_count} new)")

            # Update max page from this page's pagination links
            for t2, p2 in re.findall(r"ld-topic-page=(\d+)-(\d+)", phtml):
                t2, p2 = int(t2), int(p2)
                if t2 == tid:
                    max_page = max(max_page, p2)

            page += 1

    # Parse topic URLs into (mandala, sukta, url)
    mandala_suktas = {}  # {mandala_num: [(sukta_num, url)]}

    for url in all_topic_urls:
        decoded = urllib.parse.unquote(url)
        # URL pattern: /topics/ঋগ্বেদ-MM।SSS/ or /topics/ঋগ্বেদ-MM।SS/
        m = re.search(r"ঋগ্বেদ-([০-৯]+)[।.]([০-৯]+)", decoded)
        if m:
            mandala_num = bengali_to_int(m.group(1))
            sukta_num = bengali_to_int(m.group(2))
            if mandala_filter and mandala_num != mandala_filter:
                continue
            if mandala_num not in mandala_suktas:
                mandala_suktas[mandala_num] = []
            mandala_suktas[mandala_num].append((sukta_num, url))

    # Sort by sukta number within each mandala
    for mn in mandala_suktas:
        mandala_suktas[mn].sort(key=lambda x: x[0])

    # Report
    total = sum(len(v) for v in mandala_suktas.values())
    print(f"\nDiscovered {total} suktas across {len(mandala_suktas)} mandalas:")
    for mn in sorted(mandala_suktas.keys()):
        expected = EXPECTED_SUKTA_COUNTS.get(mn, "?")
        found = len(mandala_suktas[mn])
        status = "OK" if found == expected else f"MISMATCH (expected {expected})"
        print(f"  Mandala {mn}: {found} suktas - {status}")

    return mandala_suktas


# ---------------------------------------------------------------------------
# Step 2: Parse a sukta page to extract Bengali translation
# ---------------------------------------------------------------------------


def extract_entry_content(html: str) -> str:
    """Extract the text within the entry-content div."""
    # Find the ld-tab-content / entry-content div
    m = re.search(
        r'class="[^"]*entry-content[^"]*"[^>]*>(.*?)(?:</div>\s*</div>\s*</div>)',
        html,
        re.DOTALL,
    )
    if m:
        return m.group(1)
    return ""


def parse_sukta_page(html: str, mandala_num: int, sukta_num: int):
    """
    Parse a sukta page and return structured data.

    Returns:
        {
            "n": sukta_number,
            "title": "...",
            "verses": [{"n": verse_num, "bengali": "..."}],
            "tika": "..." (optional commentary),
        }
    """
    content = extract_entry_content(html)
    if not content:
        # Fallback: find Bengali text anywhere in page
        content = html

    # --- Extract title ---
    title = ""
    h2 = re.search(r"<h2[^>]*>(.*?)</h2>", content, re.DOTALL)
    if h2:
        title = clean_html(h2.group(1))
    if not title:
        title = f"ঋগ্বেদ {mandala_num}।{sukta_num}"

    # --- Extract Bengali translation paragraphs ---
    # Three formats observed:
    #
    # Format A: Single <p> starting with "অনুবাদঃ" or "অনুবাদ:"
    #   containing all verses separated by <br> with Bengali numbering.
    #   Common in mandalas 1-4.
    #
    # Format B: Separate <p> tags per verse, each starting with
    #   Bengali number + "." (e.g., "১."). Common in mandala 10.
    #
    # Format C: Single <p> (no "অনুবাদ" prefix) containing all verses
    #   separated by <br><br> with Bengali numbering.
    #   Common in mandalas 5-9.
    #
    # Strategy: extract Bengali text from all <p> tags, then split
    # into verses using the Bengali number pattern.

    verses = []
    tika = ""

    def split_into_verses(text: str):
        """Split a block of text into individual verses by Bengali numbering."""
        # Split on Bengali number pattern at start of line
        # Handles: ১। , ১. , ১ , etc.
        parts = re.split(r"(?:^|\n)\s*(?=[০-৯]+[।. ]\s*)", text)
        result = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            vm = re.match(r"([০-৯]+)[।. ]\s*(.*)", part, re.DOTALL)
            if vm:
                vn = bengali_to_int(vm.group(1))
                vtext = vm.group(2).strip()
                # Clean internal newlines
                vtext = re.sub(r"\s*\n\s*", " ", vtext)
                # Remove trailing periods-only or dashes
                vtext = vtext.strip()
                # Skip very short entries that are just headers (e.g. "সুক্ত ।।")
                if vtext and len(vtext) > 10:
                    result.append({"n": vn, "bengali": vtext})
        return result

    # Locate the Bengali translation section.
    # We look for the অনুবাদ marker first, then fall back to scanning <p> tags.

    anubad_idx = content.find("অনুবাদ")
    if anubad_idx >= 0:
        # Format A: find the <p> containing অনুবাদ
        p_start = content.rfind("<p", 0, anubad_idx)
        p_end = content.find("</p>", anubad_idx)
        if p_start >= 0 and p_end >= 0:
            anubad_para = content[p_start : p_end + 4]
            anubad_text = clean_html(anubad_para)
            # Remove everything before and including "অনুবাদঃ"
            # (handles cases like "১ সুক্ত ।। অনুবাদঃ ১। ...")
            anubad_text = re.sub(
                r"^.*?অনুবাদ[ঃ:]?\s*", "", anubad_text, count=1, flags=re.DOTALL
            )
            verses = split_into_verses(anubad_text)

            # Check for continuation paragraphs after the অনুবাদ paragraph
            # Some suktas split verses across multiple <p> tags
            remaining = content[p_end + 4:]
            cont_p_tags = re.findall(r"<p[^>]*>(.*?)</p>", remaining, re.DOTALL)
            for cp_html in cont_p_tags:
                cp_text = clean_html(cp_html)
                if not cp_text or len(cp_text) < 15:
                    continue
                # Stop at commentary sections
                if cp_text.startswith("টীকা") or cp_text.startswith("\u2014\u2014"):
                    break
                # Stop at English/Sanskrit sections
                if re.match(r"^(HYMN|Rig Veda|[A-Z])", cp_text):
                    break
                if any("\u0900" <= c <= "\u097F" for c in cp_text[:20]) and \
                   not any("\u0980" <= c <= "\u09FF" for c in cp_text[:20]):
                    break
                # Check if this looks like continuation Bengali verses
                if re.match(r"[০-৯]+[।.]\s", cp_text):
                    cont_verses = split_into_verses(cp_text)
                    if cont_verses:
                        # Avoid duplicates: only add if verse number not seen
                        existing_nums = {v["n"] for v in verses}
                        for cv in cont_verses:
                            if cv["n"] not in existing_nums:
                                verses.append(cv)
                                existing_nums.add(cv["n"])

    # If Format A found nothing, scan all <p> tags
    if not verses:
        p_tags = re.findall(r"<p[^>]*>(.*?)</p>", content, re.DOTALL)

        # Collect Bengali-only paragraphs that look like verse content
        bengali_paras = []
        for p_html in p_tags:
            p_text = clean_html(p_html)
            if not p_text or len(p_text) < 15:
                continue
            # Skip English text (Griffith), Sanskrit (Devanagari), IAST
            if re.match(r"^(HYMN|Rig Veda|[A-Z])", p_text):
                continue
            if re.match(r"^[a-z]", p_text) and not any(c >= "\u0980" for c in p_text[:50]):
                continue
            # Skip Devanagari-only paragraphs
            if any("\u0900" <= c <= "\u097F" for c in p_text[:30]) and \
               not any("\u0980" <= c <= "\u09FF" for c in p_text[:30]):
                continue
            # Skip "টীকা" (commentary) paragraphs and beyond
            if p_text.startswith("টীকা") or p_text.startswith("\u2014\u2014"):
                break
            # Skip header lines like "১ সুক্ত ।।", "পঞ্চম মণ্ড��", etc.
            if re.match(r"^[০-৯]+ সুক্ত", p_text):
                continue
            if "মণ্ডল" in p_text and len(p_text) < 50:
                continue
            if "মন্ডল" in p_text and len(p_text) < 50:
                continue
            # Skip short lines that are just headers (e.g. "[ঋগ্বেদ ১।১]")
            if len(p_text) < 40 and not re.search(r"[০-৯]+[।.]\s+\S{5,}", p_text):
                continue
            has_bengali_num = bool(re.search(r"[০-৯]+[।. ]", p_text))
            has_bengali_text = any("\u0980" <= c <= "\u09FF" for c in p_text)
            if has_bengali_num and has_bengali_text:
                bengali_paras.append(p_text)

        # Check if we have a single long paragraph (Format C) or
        # multiple short ones (Format B)
        if len(bengali_paras) == 1 and len(bengali_paras[0]) > 200:
            # Format C: single paragraph with all verses
            verses = split_into_verses(bengali_paras[0])
        elif len(bengali_paras) > 1:
            # Format B or C: try each paragraph
            for pt in bengali_paras:
                parsed = split_into_verses(pt)
                if parsed:
                    verses.extend(parsed)
            # Deduplicate by verse number (keep first occurrence)
            seen_nums = set()
            deduped = []
            for v in verses:
                if v["n"] not in seen_nums:
                    seen_nums.add(v["n"])
                    deduped.append(v)
            verses = deduped
        elif bengali_paras:
            # Single short paragraph
            verses = split_into_verses(bengali_paras[0])

    # --- Extract commentary (tika) ---
    tika_idx = content.find("টীকা")
    if tika_idx >= 0:
        p_start = content.rfind("<p", 0, tika_idx)
        p_end = content.find("</p>", tika_idx)
        if p_start >= 0 and p_end >= 0:
            tika_para = content[p_start : p_end + 4]
            tika = clean_html(tika_para)
            tika = re.sub(r"^টীকা[ঃ:]?\s*", "", tika)
            tika = tika.strip()
    else:
        # Some pages use dashes as separator before commentary
        dash_idx = content.find("\u2014" * 3)
        if dash_idx < 0:
            dash_idx = content.find("---")
        if dash_idx >= 0:
            p_start = content.rfind("<p", 0, dash_idx)
            p_end = content.find("</p>", dash_idx)
            if p_start >= 0 and p_end >= 0:
                tika_para = content[p_start : p_end + 4]
                tika = clean_html(tika_para)
                tika = re.sub(r"^[\u2014\u2013\-]+\s*", "", tika)
                tika = tika.strip()

    result = {
        "n": sukta_num,
        "title": title,
        "verses": verses,
    }
    if tika:
        result["tika"] = tika

    return result


# ---------------------------------------------------------------------------
# Step 3: Main scraping logic
# ---------------------------------------------------------------------------


def scrape(mandala_filter=None, test_mode=False, resume=False):
    """
    Main scraper. Discovers URLs, fetches pages, parses content.

    Args:
        mandala_filter: If set, only scrape this mandala number.
        test_mode: If True, only scrape first 2 suktas total.
        resume: If True, skip already-cached topic pages.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Discover topic URLs
    mandala_suktas = discover_all_topic_urls(mandala_filter=mandala_filter)

    if not mandala_suktas:
        print("No sukta URLs discovered. Exiting.")
        return

    # Step 2: Fetch and parse each sukta
    result = {"mandalas": []}
    total_suktas = sum(len(v) for v in mandala_suktas.values())
    processed = 0
    errors = 0
    test_limit = 2 if test_mode else None

    for mandala_num in sorted(mandala_suktas.keys()):
        mandala_data = {"n": mandala_num, "suktas": []}
        sukta_list = mandala_suktas[mandala_num]

        for sukta_num, url in sukta_list:
            if test_limit is not None and processed >= test_limit:
                break

            processed += 1
            decoded_url = urllib.parse.unquote(url)
            short_ref = f"M{mandala_num}.S{sukta_num}"
            print(
                f"  [{processed}/{total_suktas}] {short_ref}: "
                f"{decoded_url[-40:]}"
            )

            # Check cache for resumability
            cpath = CACHE_DIR / cache_key(url)
            is_cached = cpath.exists()

            if is_cached and resume:
                # Read from cache without delay
                pass
            else:
                # Polite delay before fetching
                if not is_cached:
                    time.sleep(DELAY_SECONDS)

            try:
                html = fetch_html(url, use_cache=True)
                sukta_data = parse_sukta_page(html, mandala_num, sukta_num)
                mandala_data["suktas"].append(sukta_data)

                verse_count = len(sukta_data["verses"])
                if verse_count == 0:
                    print(f"    WARNING: No verses extracted for {short_ref}")
                else:
                    print(f"    Extracted {verse_count} verses")

            except Exception as e:
                print(f"    ERROR: {e}")
                errors += 1
                mandala_data["suktas"].append({
                    "n": sukta_num,
                    "title": f"ঋগ্বেদ {mandala_num}।{sukta_num}",
                    "verses": [],
                    "error": str(e),
                })

        if test_limit is not None and processed >= test_limit:
            if mandala_data["suktas"]:
                result["mandalas"].append(mandala_data)
            break

        result["mandalas"].append(mandala_data)

    # Step 3: Write JSON output
    print(f"\nWriting output to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Summary
    total_verses = sum(
        len(s["verses"])
        for m in result["mandalas"]
        for s in m["suktas"]
    )
    total_extracted = sum(len(m["suktas"]) for m in result["mandalas"])
    print(f"\nDone!")
    print(f"  Mandalas: {len(result['mandalas'])}")
    print(f"  Suktas processed: {total_extracted}")
    print(f"  Total verses extracted: {total_verses}")
    print(f"  Errors: {errors}")
    print(f"  Output: {OUTPUT_FILE}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Scrape Bengali Rigveda from ebanglalibrary.com"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Test mode: scrape only first 2 suktas"
    )
    parser.add_argument(
        "--mandala", type=int, default=None,
        help="Scrape only this mandala number (1-10)"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Skip already-cached pages (resume interrupted scrape)"
    )
    args = parser.parse_args()

    if args.mandala and not (1 <= args.mandala <= 10):
        print("Error: --mandala must be 1-10")
        sys.exit(1)

    scrape(
        mandala_filter=args.mandala,
        test_mode=args.test,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()

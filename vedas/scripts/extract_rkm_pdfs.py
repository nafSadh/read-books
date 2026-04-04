#!/usr/bin/env python3
"""
Download Ramakrishna Mission Bengali Rigveda PDFs (per-mandala) and extract
structured text from them.

Source: agniveerbangla.org -> Google Drive hosted PDFs
Publisher: Ramakrishna Mission Institute of Culture

Requirements:
  - Python 3.9+ (stdlib only: urllib, json, re, os, pathlib, subprocess, time)
  - For text extraction: pdftotext (from poppler-utils)
    Install on macOS:  brew install poppler
    Install on Ubuntu:  sudo apt-get install poppler-utils
  - These are SCANNED PDFs, so pdftotext may yield limited results.
    For better OCR: install tesseract + ocrmypdf
    macOS:  brew install tesseract tesseract-lang ocrmypdf
    Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-ben ocrmypdf

Usage:
  python3 extract_rkm_pdfs.py                 # process all available mandalas
  python3 extract_rkm_pdfs.py --mandala 2     # process only mandala 2
  python3 extract_rkm_pdfs.py --skip-download # skip download, use cached PDFs
  python3 extract_rkm_pdfs.py --check-tools   # just check tool availability
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"
CACHE_DIR = Path("/tmp/rkm_pdf_cache")

# Google Drive file IDs for each mandala (from agniveerbangla.org)
# Only mandalas 1-5 are currently available on the source page
RKM_MANDALA_FILES = {
    1: {
        "file_id": "1-50c9tz3VVtTJLw2tnT5nNmOEQ7WizyD",
        "size_mb": 79.1,
    },
    2: {
        "file_id": "10RMmK861Ly5iNGN10cmGSaxqNND_rTEz",
        "size_mb": 18.5,
    },
    3: {
        "file_id": "13Bq8d6RlVzVhDE26lZO4jrEYZpheWrHi",
        "size_mb": 29.3,
    },
    4: {
        "file_id": "1DCKoosT2hLJAwa_tMjvJKhxsErgGQToF",
        "size_mb": 30.6,
    },
    5: {
        "file_id": "1HRunqaSKyaeSWiJ4_ryw6c7B0J8-0slc",
        "size_mb": 31.3,
    },
    # Mandalas 6-10: NOT YET AVAILABLE on agniveerbangla.org
    # The page only lists mandalas 1-5 for the RKM per-mandala PDFs.
    # When they become available, add their file_ids here.
}

# Expected verse counts per mandala (from rigveda-complete.json)
EXPECTED_MANTRAS = {
    1: 1979, 2: 430, 3: 619, 4: 588, 5: 725,
    6: 766, 7: 843, 8: 1331, 9: 1108, 10: 1754,
}

EXPECTED_SUKTAS = {
    1: 191, 2: 43, 3: 62, 4: 58, 5: 87,
    6: 75, 7: 104, 8: 103, 9: 114, 10: 191,
}


# ---------------------------------------------------------------------------
# Tool checking
# ---------------------------------------------------------------------------

def check_tools():
    """Check which PDF extraction tools are available."""
    tools = {}

    # pdftotext (poppler-utils) -- best for text-layer PDFs
    pdftotext = shutil.which("pdftotext")
    tools["pdftotext"] = pdftotext
    if pdftotext:
        try:
            r = subprocess.run([pdftotext, "-v"], capture_output=True, text=True)
            ver = (r.stdout + r.stderr).strip().split("\n")[0]
            tools["pdftotext_version"] = ver
        except Exception:
            tools["pdftotext_version"] = "unknown"

    # pdfinfo (poppler-utils) -- for page count etc.
    tools["pdfinfo"] = shutil.which("pdfinfo")

    # tesseract OCR
    tesseract = shutil.which("tesseract")
    tools["tesseract"] = tesseract
    if tesseract:
        try:
            r = subprocess.run([tesseract, "--list-langs"], capture_output=True, text=True)
            langs = r.stdout.strip().split("\n")[1:]  # skip header
            tools["tesseract_langs"] = langs
            tools["tesseract_has_bengali"] = "ben" in langs
        except Exception:
            tools["tesseract_langs"] = []
            tools["tesseract_has_bengali"] = False

    # ocrmypdf
    tools["ocrmypdf"] = shutil.which("ocrmypdf")

    # ghostscript (for PDF manipulation)
    tools["gs"] = shutil.which("gs")

    # Python PDF libs (not expected to be available, but check)
    for mod in ["PyPDF2", "pdfplumber", "fitz"]:
        try:
            __import__(mod)
            tools[f"python_{mod}"] = True
        except ImportError:
            tools[f"python_{mod}"] = False

    return tools


def print_tool_report(tools):
    """Print a human-readable tool availability report."""
    print("=" * 60)
    print("PDF Tool Availability Report")
    print("=" * 60)

    # Primary extraction
    if tools["pdftotext"]:
        print(f"  [OK] pdftotext: {tools['pdftotext']}")
        print(f"        Version: {tools.get('pdftotext_version', '?')}")
    else:
        print("  [!!] pdftotext: NOT FOUND")
        print("        Install: brew install poppler  (macOS)")
        print("                 sudo apt install poppler-utils  (Ubuntu)")

    if tools.get("pdfinfo"):
        print(f"  [OK] pdfinfo: {tools['pdfinfo']}")
    else:
        print("  [--] pdfinfo: not found (comes with poppler)")

    # OCR
    if tools["tesseract"]:
        print(f"  [OK] tesseract: {tools['tesseract']}")
        if tools.get("tesseract_has_bengali"):
            print("        Bengali (ben) language: AVAILABLE")
        else:
            print("        Bengali (ben) language: NOT INSTALLED")
            print("        Install: brew install tesseract-lang  (macOS)")
    else:
        print("  [--] tesseract: not found")
        print("        Install: brew install tesseract tesseract-lang  (macOS)")

    if tools.get("ocrmypdf"):
        print(f"  [OK] ocrmypdf: {tools['ocrmypdf']}")
    else:
        print("  [--] ocrmypdf: not found")

    # Python libs
    for mod in ["PyPDF2", "pdfplumber", "fitz"]:
        key = f"python_{mod}"
        if tools.get(key):
            print(f"  [OK] Python {mod}: available")
        else:
            print(f"  [--] Python {mod}: not available")

    # Summary
    print()
    can_extract = tools["pdftotext"] is not None
    can_ocr = (tools["tesseract"] is not None and
               tools.get("tesseract_has_bengali", False))

    if can_extract and can_ocr:
        print("STATUS: Full extraction + OCR capability available")
    elif can_extract:
        print("STATUS: Basic text extraction available (pdftotext)")
        print("  Note: Scanned PDFs may yield empty text without OCR.")
        print("  For OCR: brew install tesseract tesseract-lang ocrmypdf")
    elif can_ocr:
        print("STATUS: OCR available but pdftotext missing")
        print("  Install: brew install poppler")
    else:
        print("STATUS: NO PDF extraction tools found!")
        print()
        print("  To enable extraction, install poppler (provides pdftotext):")
        print("    macOS:  brew install poppler")
        print("    Ubuntu: sudo apt-get install poppler-utils")
        print()
        print("  For OCR of scanned Bengali PDFs:")
        print("    macOS:  brew install tesseract tesseract-lang ocrmypdf")
        print("    Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-ben ocrmypdf")
        print()
        print("  The download step will still work; text extraction will be skipped.")

    print("=" * 60)
    return can_extract, can_ocr


# ---------------------------------------------------------------------------
# Google Drive download
# ---------------------------------------------------------------------------

def gdrive_download_url(file_id):
    """Build a direct-download URL for a Google Drive file."""
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def gdrive_confirm_url(file_id, confirm_token):
    """Build a confirmed download URL (for large files)."""
    return (f"https://drive.google.com/uc?export=download"
            f"&id={file_id}&confirm={confirm_token}")


def download_from_gdrive(file_id, dest_path, size_mb=0, max_retries=3):
    """
    Download a file from Google Drive, handling the virus-scan confirmation
    page that Google shows for large files.
    """
    if dest_path.exists():
        actual_mb = dest_path.stat().st_size / (1024 * 1024)
        if size_mb > 0 and actual_mb > size_mb * 0.8:
            print(f"  Cached: {dest_path.name} ({actual_mb:.1f} MB)")
            return True
        elif actual_mb > 1:
            print(f"  Cached: {dest_path.name} ({actual_mb:.1f} MB)")
            return True
        else:
            print(f"  Cached file too small ({actual_mb:.1f} MB), re-downloading...")

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    url = gdrive_download_url(file_id)

    for attempt in range(max_retries):
        try:
            print(f"  Downloading (attempt {attempt + 1}/{max_retries})...")
            print(f"    URL: {url}")

            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            })
            resp = urllib.request.urlopen(req, timeout=30)

            # Check if we got the confirmation page
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" in content_type:
                html = resp.read().decode("utf-8", errors="replace")

                # Look for confirmation token
                # Pattern: &confirm=XXXXX& or confirm=XXXXX"
                confirm_match = re.search(
                    r'confirm=([0-9A-Za-z_-]+)', html
                )
                if confirm_match:
                    token = confirm_match.group(1)
                    print(f"    Got confirmation token: {token}")
                    url = gdrive_confirm_url(file_id, token)
                    req = urllib.request.Request(url, headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                    })
                    resp = urllib.request.urlopen(req, timeout=30)
                else:
                    # Try the download=1 approach
                    url2 = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=1"
                    print(f"    No token found, trying confirm=1...")
                    req = urllib.request.Request(url2, headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                    })
                    resp = urllib.request.urlopen(req, timeout=30)
                    content_type = resp.headers.get("Content-Type", "")
                    if "text/html" in content_type:
                        # Still HTML -- try yet another approach
                        url3 = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=1"
                        print(f"    Trying usercontent URL...")
                        req = urllib.request.Request(url3, headers={
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                        })
                        resp = urllib.request.urlopen(req, timeout=60)

            # Stream download
            content_length = resp.headers.get("Content-Length")
            total = int(content_length) if content_length else None

            tmp_path = dest_path.with_suffix(".tmp")
            downloaded = 0
            last_report = 0
            with open(tmp_path, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 1024)  # 1 MB chunks
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    mb = downloaded / (1024 * 1024)
                    if mb - last_report >= 5 or not chunk:
                        if total:
                            pct = downloaded / total * 100
                            print(f"    {mb:.1f} MB / {total/1024/1024:.1f} MB ({pct:.0f}%)")
                        else:
                            print(f"    {mb:.1f} MB downloaded...")
                        last_report = mb

            # Verify it's actually a PDF
            with open(tmp_path, "rb") as f:
                header = f.read(5)
            if header != b"%PDF-":
                print(f"    WARNING: Downloaded file does not look like a PDF!")
                print(f"    Header: {header!r}")
                # Check if it's HTML (Google error page)
                with open(tmp_path, "r", errors="replace") as f:
                    start = f.read(500)
                if "<html" in start.lower():
                    print(f"    Got HTML instead of PDF. Google may be rate-limiting.")
                    tmp_path.unlink()
                    if attempt < max_retries - 1:
                        wait = 10 * (attempt + 1)
                        print(f"    Waiting {wait}s before retry...")
                        time.sleep(wait)
                        continue
                    return False

            tmp_path.rename(dest_path)
            final_mb = dest_path.stat().st_size / (1024 * 1024)
            print(f"    Done: {final_mb:.1f} MB")
            return True

        except urllib.error.HTTPError as e:
            print(f"    HTTP Error {e.code}: {e.reason}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                return False
        except urllib.error.URLError as e:
            print(f"    URL Error: {e.reason}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                return False
        except Exception as e:
            print(f"    Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                return False

    return False


# ---------------------------------------------------------------------------
# PDF text extraction
# ---------------------------------------------------------------------------

def get_pdf_info(pdf_path):
    """Get PDF page count and metadata using pdfinfo."""
    pdfinfo = shutil.which("pdfinfo")
    if not pdfinfo:
        return {}
    try:
        r = subprocess.run(
            [pdfinfo, str(pdf_path)],
            capture_output=True, text=True, timeout=30
        )
        info = {}
        for line in r.stdout.strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                info[key.strip()] = val.strip()
        return info
    except Exception:
        return {}


def extract_text_pdftotext(pdf_path, output_txt_path=None):
    """Extract text from PDF using pdftotext (poppler)."""
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        return None

    if output_txt_path is None:
        output_txt_path = pdf_path.with_suffix(".txt")

    try:
        # -layout preserves the original physical layout
        # -enc UTF-8 ensures proper encoding
        r = subprocess.run(
            [pdftotext, "-layout", "-enc", "UTF-8", str(pdf_path), str(output_txt_path)],
            capture_output=True, text=True, timeout=300
        )
        if r.returncode != 0:
            print(f"    pdftotext error: {r.stderr}")
            return None

        if output_txt_path.exists():
            text = output_txt_path.read_text(encoding="utf-8")
            return text
        return None
    except subprocess.TimeoutExpired:
        print("    pdftotext timed out (>5 min)")
        return None
    except Exception as e:
        print(f"    pdftotext error: {e}")
        return None


def extract_text_ocr(pdf_path, output_txt_path=None):
    """Extract text from scanned PDF using OCR (tesseract via ocrmypdf)."""
    ocrmypdf = shutil.which("ocrmypdf")
    tesseract = shutil.which("tesseract")

    if not ocrmypdf and not tesseract:
        return None

    if output_txt_path is None:
        output_txt_path = pdf_path.with_suffix(".ocr.txt")

    # Try ocrmypdf first (handles PDF->OCR PDF->text)
    if ocrmypdf:
        try:
            ocr_pdf = pdf_path.with_suffix(".ocr.pdf")
            r = subprocess.run(
                [ocrmypdf, "-l", "ben+eng", "--force-ocr",
                 "--sidecar", str(output_txt_path),
                 str(pdf_path), str(ocr_pdf)],
                capture_output=True, text=True, timeout=1800  # 30 min
            )
            if output_txt_path.exists():
                return output_txt_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"    ocrmypdf error: {e}")

    return None


def extract_text(pdf_path, tools):
    """Extract text from a PDF using the best available tool."""
    txt_path = pdf_path.with_suffix(".txt")

    # Check cache
    if txt_path.exists() and txt_path.stat().st_size > 100:
        print(f"  Using cached text: {txt_path.name}")
        return txt_path.read_text(encoding="utf-8")

    # Try pdftotext first (fast, works for text-layer PDFs)
    if tools["pdftotext"]:
        print("  Extracting text with pdftotext...")
        text = extract_text_pdftotext(pdf_path, txt_path)
        if text and len(text.strip()) > 100:
            print(f"  Extracted {len(text)} chars ({len(text.split(chr(10)))} lines)")
            return text
        elif text is not None:
            print(f"  pdftotext yielded only {len(text.strip())} chars (likely scanned PDF)")

    # Try OCR
    if tools.get("ocrmypdf") or tools.get("tesseract"):
        print("  Attempting OCR extraction (this may take a while)...")
        ocr_txt_path = pdf_path.with_suffix(".ocr.txt")
        text = extract_text_ocr(pdf_path, ocr_txt_path)
        if text and len(text.strip()) > 100:
            print(f"  OCR extracted {len(text)} chars")
            return text

    print("  No text extraction possible with available tools.")
    return None


# ---------------------------------------------------------------------------
# Text parsing -- identify verse boundaries
# ---------------------------------------------------------------------------

def parse_rkm_text(text, mandala_num):
    """
    Parse extracted text from an RKM Rigveda PDF to identify sukta/verse
    boundaries.

    The RKM Bengali Rigveda typically has:
    - Section headers like "সূক্ত ১" (Sukta 1)
    - Verse numbers like "১।" or "১." or "মন্ত্র ১"
    - Bengali text of the verse/meaning
    - Sometimes Sanskrit text followed by Bengali translation

    This is a best-effort parser since the PDFs are scanned and OCR quality
    varies significantly.
    """
    if not text:
        return {"n": mandala_num, "suktas": [], "extraction_note": "no text extracted"}

    lines = text.split("\n")
    result = {
        "n": mandala_num,
        "suktas": [],
        "raw_lines": len(lines),
        "raw_chars": len(text),
    }

    # Bengali digits mapping
    bn_digits = {"০": "0", "১": "1", "২": "2", "৩": "3", "৪": "4",
                 "৫": "5", "৬": "6", "৭": "7", "৮": "8", "৯": "9"}

    def bn_to_int(s):
        """Convert Bengali numeral string to int."""
        latin = ""
        for ch in s:
            latin += bn_digits.get(ch, ch)
        try:
            return int(latin)
        except ValueError:
            return None

    # Patterns for sukta headers
    sukta_patterns = [
        # সূক্ত ১, সূক্ত ২, etc.
        re.compile(r'সূক্ত\s+([০-৯]+)'),
        # Sukta N (English)
        re.compile(r'[Ss]ukta\s+(\d+)', re.IGNORECASE),
        # সুক্ত (variant spelling)
        re.compile(r'সুক্ত\s+([০-৯]+)'),
    ]

    # Patterns for verse/mantra numbers
    verse_patterns = [
        # ১। or ২। etc. (Bengali numeral + danda)
        re.compile(r'^[  ]*([০-৯]+)[।\.]\s*(.+)'),
        # মন্ত্র ১ (mantra N)
        re.compile(r'মন্ত্র\s+([০-৯]+)\s*[।:.]?\s*(.*)'),
        # Mantra N (English)
        re.compile(r'[Mm]antra\s+(\d+)\s*[.:]\s*(.*)'),
    ]

    current_sukta = None
    current_verse_num = None
    current_verse_text = []
    suktas = {}

    def flush_verse():
        nonlocal current_verse_num, current_verse_text
        if current_sukta is not None and current_verse_num is not None:
            text_block = "\n".join(current_verse_text).strip()
            if text_block:
                if current_sukta not in suktas:
                    suktas[current_sukta] = {}
                suktas[current_sukta][current_verse_num] = text_block
        current_verse_num = None
        current_verse_text = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for sukta header
        sukta_found = False
        for pat in sukta_patterns:
            m = pat.search(stripped)
            if m:
                flush_verse()
                num_str = m.group(1)
                num = bn_to_int(num_str) if any(c in num_str for c in bn_digits) else int(num_str)
                if num and 1 <= num <= 200:
                    current_sukta = num
                    sukta_found = True
                    break

        if sukta_found:
            continue

        # Check for verse number
        verse_found = False
        for pat in verse_patterns:
            m = pat.match(stripped)
            if m:
                flush_verse()
                num_str = m.group(1)
                num = bn_to_int(num_str) if any(c in num_str for c in bn_digits) else int(num_str)
                remainder = m.group(2).strip() if m.lastindex >= 2 else ""
                if num and 1 <= num <= 100:
                    current_verse_num = num
                    if remainder:
                        current_verse_text = [remainder]
                    else:
                        current_verse_text = []
                    verse_found = True
                    break

        if verse_found:
            continue

        # Accumulate text for current verse
        if current_verse_num is not None:
            current_verse_text.append(stripped)

    # Flush last verse
    flush_verse()

    # Build structured output
    for sukta_num in sorted(suktas.keys()):
        verses = []
        for verse_num in sorted(suktas[sukta_num].keys()):
            verses.append({
                "n": verse_num,
                "bengali_rkm": suktas[sukta_num][verse_num],
                "source": "rkm",
            })
        result["suktas"].append({
            "n": sukta_num,
            "verses": verses,
        })

    return result


def analyze_extraction(mandala_data, mandala_num):
    """Analyze extraction quality for a mandala."""
    expected_suktas = EXPECTED_SUKTAS.get(mandala_num, 0)
    expected_mantras = EXPECTED_MANTRAS.get(mandala_num, 0)

    found_suktas = len(mandala_data.get("suktas", []))
    found_mantras = sum(
        len(s.get("verses", [])) for s in mandala_data.get("suktas", [])
    )

    return {
        "mandala": mandala_num,
        "expected_suktas": expected_suktas,
        "found_suktas": found_suktas,
        "sukta_coverage": f"{found_suktas}/{expected_suktas}" if expected_suktas else "?",
        "expected_mantras": expected_mantras,
        "found_mantras": found_mantras,
        "mantra_coverage": f"{found_mantras}/{expected_mantras}" if expected_mantras else "?",
        "raw_lines": mandala_data.get("raw_lines", 0),
        "raw_chars": mandala_data.get("raw_chars", 0),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Download and extract RKM Bengali Rigveda PDFs"
    )
    parser.add_argument(
        "--mandala", "-m", type=int,
        help="Process only this mandala (1-5)"
    )
    parser.add_argument(
        "--skip-download", action="store_true",
        help="Skip download, use cached PDFs only"
    )
    parser.add_argument(
        "--check-tools", action="store_true",
        help="Just check tool availability and exit"
    )
    parser.add_argument(
        "--output", "-o", type=str,
        default=str(OUTPUT_DIR / "rkm_bengali.json"),
        help="Output JSON path"
    )
    args = parser.parse_args()

    # Check tools
    tools = check_tools()
    can_extract, can_ocr = print_tool_report(tools)

    if args.check_tools:
        sys.exit(0)

    # Determine which mandalas to process
    if args.mandala:
        if args.mandala not in RKM_MANDALA_FILES:
            available = sorted(RKM_MANDALA_FILES.keys())
            print(f"\nError: Mandala {args.mandala} not available.")
            print(f"Available mandalas: {available}")
            if args.mandala > 5:
                print("Note: Only mandalas 1-5 are currently published by RKM on agniveerbangla.org")
            sys.exit(1)
        mandalas_to_process = [args.mandala]
    else:
        mandalas_to_process = sorted(RKM_MANDALA_FILES.keys())

    print(f"\nProcessing mandalas: {mandalas_to_process}")
    print(f"Cache directory: {CACHE_DIR}")
    print(f"Output: {args.output}")
    print()

    # Download PDFs
    pdf_paths = {}
    if not args.skip_download:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        for m_num in mandalas_to_process:
            info = RKM_MANDALA_FILES[m_num]
            pdf_name = f"rkm_rigveda_mandala_{m_num}.pdf"
            pdf_path = CACHE_DIR / pdf_name
            print(f"Mandala {m_num} ({info['size_mb']} MB):")
            ok = download_from_gdrive(
                info["file_id"], pdf_path, info["size_mb"]
            )
            if ok:
                pdf_paths[m_num] = pdf_path
            else:
                print(f"  FAILED to download mandala {m_num}")
            print()
    else:
        for m_num in mandalas_to_process:
            pdf_name = f"rkm_rigveda_mandala_{m_num}.pdf"
            pdf_path = CACHE_DIR / pdf_name
            if pdf_path.exists():
                pdf_paths[m_num] = pdf_path
                print(f"Mandala {m_num}: using cached {pdf_path}")
            else:
                print(f"Mandala {m_num}: NOT FOUND in cache")
        print()

    # Extract text
    all_mandalas = []
    stats = []

    for m_num in mandalas_to_process:
        if m_num not in pdf_paths:
            print(f"Mandala {m_num}: skipped (no PDF)")
            all_mandalas.append({
                "n": m_num,
                "suktas": [],
                "extraction_note": "PDF not available",
            })
            continue

        pdf_path = pdf_paths[m_num]
        print(f"Mandala {m_num}: extracting text from {pdf_path.name}...")

        # Get PDF info
        info = get_pdf_info(pdf_path)
        if info:
            print(f"  Pages: {info.get('Pages', '?')}")

        if not can_extract:
            print("  SKIPPED: No PDF extraction tools available.")
            print("  Install: brew install poppler")
            mandala_data = {
                "n": m_num,
                "suktas": [],
                "extraction_note": "no extraction tools available",
                "pdf_cached": str(pdf_path),
                "pdf_size_mb": pdf_path.stat().st_size / (1024 * 1024),
            }
            if info:
                mandala_data["pdf_pages"] = info.get("Pages")
            all_mandalas.append(mandala_data)
            stat = analyze_extraction(mandala_data, m_num)
            stat["note"] = "no tools"
            stats.append(stat)
            continue

        # Extract text
        text = extract_text(pdf_path, tools)

        # Parse extracted text
        mandala_data = parse_rkm_text(text, m_num)
        mandala_data["pdf_cached"] = str(pdf_path)
        mandala_data["pdf_size_mb"] = round(pdf_path.stat().st_size / (1024 * 1024), 1)
        if info:
            mandala_data["pdf_pages"] = info.get("Pages")

        all_mandalas.append(mandala_data)

        # Analyze
        stat = analyze_extraction(mandala_data, m_num)
        stats.append(stat)

        print(f"  Found: {stat['found_suktas']} suktas, {stat['found_mantras']} mantras")
        print(f"  Coverage: suktas {stat['sukta_coverage']}, mantras {stat['mantra_coverage']}")
        print()

    # Build output JSON
    output = {
        "title": "RKM Bengali Rigveda (per-Mandala PDFs)",
        "publisher": "Ramakrishna Mission Institute of Culture",
        "source_url": "https://www.agniveerbangla.org/2023/11/vedic-scriptures-pdf.html",
        "extraction_date": time.strftime("%Y-%m-%d"),
        "note": "Mandalas 6-10 not yet available on source. Scanned PDFs require OCR for text extraction.",
        "available_mandalas": sorted(RKM_MANDALA_FILES.keys()),
        "mandalas": all_mandalas,
    }

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Output written to: {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Extraction Summary")
    print("=" * 60)
    print(f"{'Mandala':<10} {'Suktas':<15} {'Mantras':<15} {'Lines':<10} {'Note'}")
    print("-" * 60)
    for stat in stats:
        note = stat.get("note", "")
        print(f"  {stat['mandala']:<8} {stat['sukta_coverage']:<13} "
              f"{stat['mantra_coverage']:<13} {stat['raw_lines']:<8} {note}")
    print("-" * 60)

    total_found = sum(s.get("found_mantras", 0) for s in stats)
    total_expected = sum(EXPECTED_MANTRAS.get(m, 0) for m in mandalas_to_process)
    print(f"  Total:   {total_found}/{total_expected} mantras")

    if not can_extract:
        print("\n  NOTE: Text extraction was skipped because no PDF tools are installed.")
        print("  The PDFs have been downloaded and cached. To extract text:")
        print("    1. Install poppler:  brew install poppler")
        print("    2. For OCR (recommended for scanned PDFs):")
        print("       brew install tesseract tesseract-lang ocrmypdf")
        print("    3. Re-run:  python3 extract_rkm_pdfs.py --skip-download")

    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()

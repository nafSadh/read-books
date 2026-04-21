#!/usr/bin/env python3
"""Parse Project Gutenberg #38511 (Arnot 1903 compilation) into seed JSON.

Produces three files under khayyam-rubaiyat/seeds/:
  - whinfield.json       (500 verse quatrains, Whinfield 1883)
  - nicolas-english.json (464 prose quatrains, from Nicolas 1867 French)
  - heron-allen.json     (101 FG-5th analysis entries with Persian source lines)

Idempotent: safe to re-run; overwrites outputs.

Source file (local): /tmp/rubaiyat/pg38511.txt  (CRLF line endings).
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# ---------- paths ----------

SRC = Path("/tmp/rubaiyat/pg38511.txt")
REPO = Path(__file__).resolve().parent.parent  # khayyam-rubaiyat/
SEEDS = REPO / "seeds"

# ---------- approximate section boundaries (1-indexed, inclusive) ----------

# Whinfield verse block: from quatrain "1." at line 5601 to end of "500. ..." footnote at 10852.
WHINFIELD_START = 5601
WHINFIELD_END = 10855

# Nicolas prose block: "THE QUATRAINS OF OMAR KHAYYAM" section header ~11213, first "1." at 11216.
NICOLAS_START = 11216
NICOLAS_END = 15362  # end of quatrain 464's prose; next content is FOOTNOTES at 15364

# Heron-Allen Analysis of FG 5th: starts at "ANALYSIS OF EDWARD FITZGERALD'S QUATRAINS" (line 2095),
# first Roman "I." at line 2098, last entry CI. through line 4392. APPENDIX begins ~4397.
HERON_ALLEN_START = 2098
HERON_ALLEN_END = 4395


# ---------- helpers ----------

FRENCH_OPEN = "\u00ab"   # «
FRENCH_CLOSE = "\u00bb"  # »


def read_lines(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    # Normalise CRLF / lone CR to LF.
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    return raw.split("\n")


def strip_french_quotes(s: str) -> str:
    """Replace « / » with straight double quotes."""
    return s.replace(FRENCH_OPEN, '"').replace(FRENCH_CLOSE, '"')


def clean_line(s: str) -> str:
    """Trim surrounding whitespace and normalise quote marks."""
    return strip_french_quotes(s.strip())


def roman_to_int(s: str) -> int:
    roman = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    prev = 0
    for ch in reversed(s):
        v = roman[ch]
        if v < prev:
            total -= v
        else:
            total += v
            prev = v
    return total


# ---------- Whinfield parser ----------

WHIN_NUM_RE = re.compile(r"^(\d+)\.\s*$")
WHIN_FOOTNOTE_START_RE = re.compile(r"^(\d+)\.\s+(.+)$")
# Rare join-form footnote header: "348 and 349. L. ...".
WHIN_JOIN_FOOTNOTE_RE = re.compile(r"^(\d+)\s+and\s+(\d+)\.\s+(.+)$")


def parse_whinfield(all_lines: list[str]) -> dict:
    """Extract 500 quatrains from the Whinfield block.

    Pattern per entry:
        <num>.
        <blank>
        (4 indented verse lines)
        <blank>
        [optional footnote line: "<num>. rest of note..." (may wrap to next line
         with no leading indent)]
        <blank(s)>
    """
    # Slice the Whinfield block.
    block = all_lines[WHINFIELD_START - 1 : WHINFIELD_END]

    # Pre-scan for the rare join-form footnote "<n> and <n+1>. <text...>"
    # (with possible continuation wraps). Keep the payload under a dict so we
    # can backfill any quatrain that otherwise has no footnote.
    shared_footnotes: dict[int, str] = {}
    for idx, ln in enumerate(block):
        jm = WHIN_JOIN_FOOTNOTE_RE.match(ln)
        if jm:
            n1, n2, payload = int(jm.group(1)), int(jm.group(2)), jm.group(3)
            parts = [payload.rstrip()]
            j2 = idx + 1
            while (
                j2 < len(block)
                and block[j2].strip() != ""
                and not WHIN_NUM_RE.match(block[j2])
                and not WHIN_FOOTNOTE_START_RE.match(block[j2])
                and not WHIN_JOIN_FOOTNOTE_RE.match(block[j2])
            ):
                parts.append(block[j2].strip())
                j2 += 1
            shared_text = " ".join(parts).strip()
            shared_footnotes[n1] = shared_text
            shared_footnotes[n2] = shared_text

    i = 0
    n = len(block)
    quatrains: list[dict] = []

    while i < n:
        line = block[i]
        m = WHIN_NUM_RE.match(line)
        # A valid Whinfield header must be preceded by a blank line (or be at
        # the very start of the block). This filters out bare "10." etc. that
        # appear as wrapped continuations of a previous footnote's page-ref.
        if not m or (i > 0 and block[i - 1].strip() != ""):
            i += 1
            continue
        num = int(m.group(1))

        # Expect a blank line then 4 verse lines (each non-blank, indented).
        i += 1
        # Skip at most one blank.
        if i < n and block[i].strip() == "":
            i += 1

        verse: list[str] = []
        while i < n and len(verse) < 4:
            if block[i].strip() == "":
                break
            verse.append(clean_line(block[i]))
            i += 1
        if len(verse) != 4:
            raise ValueError(f"Whinfield #{num}: expected 4 verse lines, got {len(verse)}")

        # Skip blank line(s) after verse.
        while i < n and block[i].strip() == "":
            i += 1

        ms_refs = ""
        note = ""
        # Optional footnote line starts with "<num>. ...".
        if i < n:
            fm = WHIN_FOOTNOTE_START_RE.match(block[i])
            if fm and int(fm.group(1)) == num:
                footnote_parts = [fm.group(2).rstrip()]
                i += 1
                # Continuation lines: non-blank lines with no blank separator.
                # These may even look like a number ("10." as a wrapped page-ref
                # continuation), which is OK: a genuine new quatrain header is
                # always preceded by a blank.
                while i < n and block[i].strip() != "":
                    # Stop if the line looks like a different-quatrain footnote
                    # header ("<other_num>. <text>").
                    nfm = WHIN_FOOTNOTE_START_RE.match(block[i])
                    if nfm and int(nfm.group(1)) != num:
                        break
                    footnote_parts.append(block[i].strip())
                    i += 1
                footnote_text = " ".join(footnote_parts).strip()
                footnote_text = strip_french_quotes(footnote_text)
                ms_refs, note = split_ms_refs(footnote_text)

        # Backfill from shared "n and n+1" footnotes when the quatrain has none
        # of its own but is covered by a joint footnote earlier in the source.
        if not ms_refs and not note and num in shared_footnotes:
            shared = strip_french_quotes(shared_footnotes[num])
            ms_refs, note = split_ms_refs(shared)

        # Skip any further blank lines before next entry.
        while i < n and block[i].strip() == "":
            i += 1

        quatrains.append(
            {"num": num, "lines": verse, "ms_refs": ms_refs, "note": note}
        )

    return {
        "source": "Project Gutenberg #38511 / Whinfield 1883 (reprinted Arnot 1903)",
        "license": "public domain",
        "count": len(quatrains),
        "quatrains": quatrains,
    }


# Whinfield MS abbreviations use dotted single/double letters (plus occasional
# E.C., P. ii., etc., but in the Whinfield footnotes we see just single letters).
# Pattern: sequence of "<Letter(s)>." tokens separated by spaces, ending when the
# next token does not match.
WHIN_MS_TOKEN_RE = re.compile(r"^[A-Z][A-Za-z]?\.$")


def split_ms_refs(text: str) -> tuple[str, str]:
    """Split the Whinfield footnote text into (ms_refs, note).

    Example inputs:
      "Bl. C. L. N. A. I. J. Bl. considers this quatrain Mystical."
      "N."
      "L. B. In line 3 scan _nesatiyast_."
      "C. L. A. I. J. _Mu'takif_, a devotee."

    Approach: consume tokens of the form "<Uppercase(+opt lower)>." greedily as
    ms_refs until a token doesn't match. The remainder is the note.

    Edge case: a note that starts with a single-letter abbreviation (e.g. "Bl.")
    would bleed into ms_refs. Heuristic: if a candidate token is followed by a
    lowercase-starting word AND looks like a sentence opener (Bl., N., C.),
    still include it as ms_refs as the convention is that ms_refs come first.
    The ambiguous cases like "Bl. considers this..." are unavoidable — we treat
    "Bl." as a ms-ref in that case. (Matches the user's target.)
    """
    tokens = text.split(" ")
    idx = 0
    while idx < len(tokens) and WHIN_MS_TOKEN_RE.match(tokens[idx]):
        idx += 1
    ms_refs = " ".join(tokens[:idx]).strip()
    note = " ".join(tokens[idx:]).strip()
    return ms_refs, note


# ---------- Nicolas parser ----------

NIC_NUM_RE = re.compile(r"^(\d+)\.\s*$")


def parse_nicolas(all_lines: list[str]) -> dict:
    """Extract 464 prose quatrains from the Nicolas block."""
    block = all_lines[NICOLAS_START - 1 : NICOLAS_END]
    i = 0
    n = len(block)
    quatrains: list[dict] = []

    while i < n:
        m = NIC_NUM_RE.match(block[i])
        # Header must be preceded by a blank (or be at block start) to avoid
        # false positives from wrapped page numbers in a preceding prose line.
        if not m or (i > 0 and block[i - 1].strip() != ""):
            i += 1
            continue
        num = int(m.group(1))
        i += 1
        # Skip blank line(s).
        while i < n and block[i].strip() == "":
            i += 1
        # Accumulate prose lines until a blank line.
        prose_parts: list[str] = []
        while i < n and block[i].strip() != "":
            # Also stop if we hit the next "<num>." header (shouldn't happen without a blank,
            # but guard).
            if NIC_NUM_RE.match(block[i]):
                break
            prose_parts.append(block[i].strip())
            i += 1
        prose = " ".join(prose_parts)
        prose = strip_french_quotes(prose)
        # Collapse any residual multi-spaces.
        prose = re.sub(r"\s+", " ", prose).strip()
        quatrains.append({"num": num, "prose": prose})
        # Advance past blanks.
        while i < n and block[i].strip() == "":
            i += 1

    return {
        "source": "Project Gutenberg #38511 / Nicolas 1867 (French) -> English prose (Arnot 1903)",
        "license": "public domain",
        "count": len(quatrains),
        "quatrains": quatrains,
    }


# ---------- Heron-Allen parser ----------

# Roman-numeral headers used by Heron-Allen; may carry "*" and/or "[NN]" footnote markers.
HA_ROMAN_RE = re.compile(r"^([IVXLC]+)\.(\*)?(\[(\d+)\])?(\*)?\s*$")

# "_Ref._:" ref-line (may have footnote marker like [15] glued after the colon).
HA_REF_RE = re.compile(r"^_Ref\.?_\s*\.?\s*:?\s*(.*)$")


def parse_heron_allen(all_lines: list[str]) -> dict:
    """Extract the 101 FG-5th analysis entries.

    For each Roman-numeral section we capture:
      * fg_5th_num   -- integer 1..101
      * source_lines -- the first Persian-source literal translation block
                        (4 consecutive indented lines), or null if none.
      * refs         -- the raw "_Ref._:" line content (minus the leading tag),
                        preferably the one following the first source_lines block;
                        else the first _Ref._ line in the entry; else "".
      * note         -- short snippet noting if the entry has multiple source
                        blocks (composite) or other flags. Empty otherwise.
    """
    block = all_lines[HERON_ALLEN_START - 1 : HERON_ALLEN_END]
    n = len(block)

    # Find all Roman-numeral headers (line indices relative to block) and pair
    # each header with its section [start, next-start).
    header_positions: list[tuple[int, str]] = []
    for idx, ln in enumerate(block):
        m = HA_ROMAN_RE.match(ln)
        if m:
            header_positions.append((idx, m.group(1)))

    entries: list[dict] = []

    for hi, (start_idx, roman) in enumerate(header_positions):
        end_idx = header_positions[hi + 1][0] if hi + 1 < len(header_positions) else n
        section = block[start_idx:end_idx]
        # The first 4 verse lines (after the header) are the FG 5th quatrain --
        # SKIP; we already have that.
        fg_5th_num = roman_to_int(roman)

        # Walk the section; skip the first 4 indented lines (FG 5th text).
        j = 1  # right after header
        # Skip blank(s).
        while j < len(section) and section[j].strip() == "":
            j += 1
        # Skip the 4 FG 5th verse lines.
        fg_verse_count = 0
        while j < len(section) and fg_verse_count < 4 and section[j].strip() != "":
            j += 1
            fg_verse_count += 1

        # Scan commentary: collect every indented run of >=2 lines (candidate
        # Persian source) and every "_Ref._:" line. Each candidate is ACCEPTED
        # as a true Persian-source block if a "_Ref._:" line follows it with
        # only blanks / plain prose in between (no other indented block). Notes:
        #   - The FG 1st/2nd/3rd edition quatrains that Heron-Allen sometimes
        #     embeds in the commentary are NOT followed by a "_Ref._:" line --
        #     another indented Persian block always intervenes -- so the rule
        #     rejects them.
        #   - Accepting >=2 lines (not just >=4) catches short literal fragments
        #     like those under entries IX and X where only ll. 1-2 of a MS
        #     quatrain are cited.
        candidates: list[tuple[int, int, list[str]]] = []  # (start_pos, end_pos, up-to-4 lines)
        refs_found: list[tuple[int, str]] = []             # (position, ref content)

        k = j
        while k < len(section):
            line = section[k]
            stripped = line.strip()
            if stripped == "":
                k += 1
                continue
            # Indented block run.
            if line.startswith("    "):
                run_start = k
                raw_lines: list[str] = []
                while k < len(section) and section[k].startswith("    ") and section[k].strip() != "":
                    raw_lines.append(section[k])
                    k += 1
                run_end = k  # exclusive
                # Merge "wrapped" continuations: lines with >=8 leading spaces
                # are typography-wraps of the preceding verse line (Heron-Allen
                # over-indents the continuation fragment). Lines indented 4-6
                # spaces are real verse lines. We can distinguish by checking
                # if the next line has MORE leading space than the previous.
                merged: list[str] = []
                prev_indent = None
                for rl in raw_lines:
                    cur_indent = len(rl) - len(rl.lstrip(" "))
                    if merged and prev_indent is not None and cur_indent > prev_indent + 2:
                        # Continuation wrap -> append to previous line.
                        merged[-1] = merged[-1].rstrip() + " " + rl.strip()
                    else:
                        merged.append(rl)
                        prev_indent = cur_indent
                if len(merged) >= 2:
                    # Canonical ruba'i is 4 lines; truncate longer blocks.
                    keep = [clean_line(l) for l in merged[:4]]
                    candidates.append((run_start, run_end, keep))
                continue

            # _Ref._ line.
            if stripped.startswith("_Ref"):
                start_ref = k
                content = stripped
                content = re.sub(r"^_Ref\.?_\s*\.?\s*:?\s*", "", content)
                content = re.sub(r"^\[\d+\]\s*", "", content).strip()
                k += 1
                while k < len(section):
                    nxt = section[k]
                    if nxt.strip() == "":
                        break
                    if HA_ROMAN_RE.match(nxt):
                        break
                    if nxt.startswith("    "):
                        break
                    if nxt.lstrip().startswith("_Ref"):
                        break
                    content += " " + nxt.strip()
                    k += 1
                refs_found.append((start_ref, re.sub(r"\s+", " ", content).strip()))
                continue

            k += 1

        # Pair candidates to refs: a candidate is "accepted" as a source_lines
        # block iff there exists a _Ref._ line at position > candidate.end_pos
        # AND < (next_candidate.start_pos OR end-of-section).
        accepted: list[tuple[int, list[str], str]] = []  # (pos, block, ref)
        cand_count = len(candidates)
        for ci, (cstart, cend, cblock) in enumerate(candidates):
            next_cstart = candidates[ci + 1][0] if ci + 1 < cand_count else len(section) + 1
            paired_ref: Optional[str] = None
            for rpos, rtext in refs_found:
                if rpos >= cend and rpos < next_cstart:
                    paired_ref = rtext
                    break
            if paired_ref is not None:
                accepted.append((cstart, cblock, paired_ref))

        source_lines: Optional[list[str]] = None
        refs: str = ""
        note = ""

        if accepted:
            # First accepted candidate is the primary Persian-source quatrain.
            _, source_lines, refs = accepted[0]
            if len(accepted) > 1:
                note = f"(composite: {len(accepted)} source blocks in original; keeping first)"
        else:
            # No paired source; still capture the first _Ref._ if present.
            if refs_found:
                refs = refs_found[0][1]

        entry = {
            "fg_5th_num": fg_5th_num,
            "source_lines": source_lines,
            "refs": refs,
        }
        if note:
            entry["note"] = note
        entries.append(entry)

    return {
        "source": "Project Gutenberg #38511 / Heron-Allen's Analysis of FitzGerald's 5th Edition",
        "license": "public domain",
        "count": len(entries),
        "entries": entries,
    }


# ---------- main ----------

def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: source file not found: {SRC}", file=sys.stderr)
        return 1
    lines = read_lines(SRC)

    whin = parse_whinfield(lines)
    nic = parse_nicolas(lines)
    ha = parse_heron_allen(lines)

    # Basic assertions.
    assert whin["count"] == 500, f"Whinfield count mismatch: {whin['count']} != 500"
    for q in whin["quatrains"]:
        assert len(q["lines"]) == 4, f"Whinfield #{q['num']} has {len(q['lines'])} lines"
    assert nic["count"] == 464, f"Nicolas count mismatch: {nic['count']} != 464"
    assert ha["count"] == 101, f"Heron-Allen count mismatch: {ha['count']} != 101"

    write_json(SEEDS / "whinfield.json", whin)
    write_json(SEEDS / "nicolas-english.json", nic)
    write_json(SEEDS / "heron-allen.json", ha)

    print(f"whinfield.json       count={whin['count']}")
    print(f"nicolas-english.json count={nic['count']}")
    print(f"heron-allen.json     count={ha['count']}")

    # Report Heron-Allen source_lines coverage.
    with_src = sum(1 for e in ha["entries"] if e["source_lines"])
    with_refs = sum(1 for e in ha["entries"] if e["refs"])
    composite = sum(1 for e in ha["entries"] if e.get("note", "").startswith("(composite"))
    print(f"  heron-allen: source_lines present={with_src}/101, refs present={with_refs}/101, composite={composite}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

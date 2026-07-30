#!/usr/bin/env python3
"""Build seeds/study.json for the side-by-side Greek study reader.

Combines:
  - seeds/greek.json               (Greek text, 24 books, per line)
  - Perseus treebank               (per-word lemma + morphology, cite = book.line)
  - Logeion/Perseus shortdefs      (lemma -> short English gloss)
  - Murray 1919 Loeb English       (line-range-aligned prose chunks)

Output schema (seeds/study.json):
{
  "lemmas":  { "<lemma>": "<short def>", ... },        # only lemmas used in the poem
  "books": [
    { "num": 1, "roman": "I",
      "lines":  [ [line_text, [[form, lemma, postag], ...]], ... ],
      "chunks": [ [start_line, end_line, english_text], ... ] }
  ]
}

Transliteration is generated client-side (deterministic, small JS), not stored.

Sources (all public domain / open):
  treebank:  PerseusDL/treebank_data v2.1 tlg0012.tlg002.perseus-grc1.tb.xml
  shortdefs: helmadik/shortdefs (Logeion short definitions)
  english:   PerseusDL/canonical-greekLit tlg0012.tlg002.perseus-eng3.xml (A. T. Murray, 1919)
"""
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SCRATCH = Path("/private/tmp/claude-501/-Users-nafsadh-src-read-books/766dc5ab-011c-4aa9-93d8-5fca0b087de2/scratchpad")

TB_XML = SCRATCH / "odyssey-tb.xml"
SHORTDEFS = SCRATCH / "shortdefs-grc.txt"
MURRAY = SCRATCH / "murray-eng3.xml"


def strip_diacritics(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))


def norm_lemma(lemma: str) -> str:
    """Normalize a treebank lemma for shortdefs lookup: NFC + strip trailing sense digits."""
    lemma = unicodedata.normalize("NFC", lemma.strip())
    # drop stray leading combining marks / lone modifier letters (treebank artifacts)
    lemma = re.sub(r"^[̀-ͯ᾽-῿ʼ᾿]+", "", lemma)
    return re.sub(r"\d+$", "", lemma)


def main() -> None:
    greek = json.loads((REPO / "seeds" / "greek.json").read_text(encoding="utf-8"))

    # ---- shortdefs: lemma -> gloss ----------------------------------------
    defs: dict[str, str] = {}
    for raw in SHORTDEFS.read_text(encoding="utf-8").splitlines():
        if "\t" not in raw:
            continue
        k, v = raw.split("\t", 1)
        k = unicodedata.normalize("NFC", k.strip())
        v = v.strip()
        if k and v and k not in defs:
            defs[k] = v
    # secondary index without diacritics for fuzzy fallback
    defs_bare: dict[str, str] = {}
    for k, v in defs.items():
        bk = strip_diacritics(k)
        defs_bare.setdefault(bk, v)

    # ---- treebank: (book, line) -> [[form, lemma, postag], ...] -----------
    words_by_line: dict[tuple[int, int], list[list[str]]] = {}
    seen_ids_by_line: dict[tuple[int, int], set] = {}
    n_words = 0
    for _ev, el in ET.iterparse(str(TB_XML), events=("end",)):
        if el.tag != "word":
            continue
        cite = el.get("cite") or ""
        m = re.search(r":(\d+)\.(\d+)$", cite)
        if m:
            postag = el.get("postag") or ""
            form = el.get("form") or ""
            lemma = el.get("lemma") or ""
            if postag.startswith("u") or not form or form in ",.;·—‘’“”":
                pass  # skip punctuation tokens
            elif el.get("insertion_id") is not None or form.startswith("["):
                pass  # skip elliptical/inserted artificial nodes
            else:
                key = (int(m.group(1)), int(m.group(2)))
                words_by_line.setdefault(key, []).append(
                    [unicodedata.normalize("NFC", form), norm_lemma(lemma), postag]
                )
                n_words += 1
        el.clear()
    print(f"treebank: {n_words} words across {len(words_by_line)} cited lines")

    # ---- Murray english: book -> [(start, text)] --------------------------
    ns = {"t": "http://www.tei-c.org/ns/1.0"}
    tree = ET.parse(str(MURRAY))
    root = tree.getroot()
    murray: dict[int, list[tuple[int, str]]] = {}
    for bdiv in root.findall(".//t:div[@subtype='book']", ns):
        bnum = int(bdiv.get("n"))
        chunks: list[tuple[int, str]] = []
        # walk all paragraphs; milestones unit=line mark 5-line boundaries
        cur_line = 1
        cur_text: list[str] = []

        def flush():
            nonlocal cur_text
            txt = re.sub(r"\s+", " ", "".join(cur_text)).strip()
            if txt:
                chunks.append((cur_line, txt))
            cur_text = []

        for p in bdiv.findall(".//t:p", ns):
            if p.text:
                cur_text.append(p.text)
            for node in p:
                tag = node.tag.split("}")[-1]
                if tag == "milestone" and node.get("unit") == "line":
                    flush()
                    cur_line = int(node.get("n"))
                else:
                    # placeName etc: keep inner text
                    cur_text.append("".join(node.itertext()))
                if node.tail:
                    cur_text.append(node.tail)
        flush()
        murray[bnum] = chunks
    print(f"murray: {len(murray)} books, e.g. book 1 has {len(murray.get(1, []))} chunks")

    # ---- assemble ---------------------------------------------------------
    used_lemmas: dict[str, str] = {}
    out_books = []
    missing_gloss: set[str] = set()
    for b in greek["books"]:
        bnum = b["num"]
        lines_out = []
        for i, line_text in enumerate(b["lines"], 1):
            words = words_by_line.get((bnum, i), [])
            for w in words:
                lem = w[1]
                if lem not in used_lemmas:
                    bare = strip_diacritics(lem)
                    gloss = (defs.get(lem) or defs_bare.get(bare)
                             or defs.get(lem.capitalize()) or defs_bare.get(bare.capitalize())
                             or defs.get(lem.lower()) or defs_bare.get(bare.lower()) or "")
                    used_lemmas[lem] = gloss
                    if not gloss:
                        missing_gloss.add(lem)
            lines_out.append([line_text, words])
        # english chunks with end lines
        chunks = murray.get(bnum, [])
        chunks_out = []
        for j, (start, txt) in enumerate(chunks):
            end = (chunks[j + 1][0] - 1) if j + 1 < len(chunks) else len(b["lines"])
            chunks_out.append([start, end, txt])
        out_books.append({"num": bnum, "roman": b["roman"], "lines": lines_out, "chunks": chunks_out})

    out = {
        "meta": {
            "greek": "Perseus canonical-greekLit grc2 (ed. Allen/Murray 1919)",
            "english": "A. T. Murray, Loeb Classical Library, 1919 (public domain)",
            "morphology": "Perseus Ancient Greek Dependency Treebank v2.1 (CC BY-SA)",
            "glosses": "Perseus/Logeion short definitions (helmadik/shortdefs)",
        },
        "lemmas": used_lemmas,
        "books": out_books,
    }
    dest = REPO / "seeds" / "study.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    total_lines = sum(len(b["lines"]) for b in out_books)
    covered = sum(1 for b in out_books for ln in b["lines"] if ln[1])
    print(f"wrote {dest} ({dest.stat().st_size:,} bytes)")
    print(f"lines: {total_lines}, with word data: {covered} ({covered*100//total_lines}%)")
    print(f"unique lemmas: {len(used_lemmas)}, missing gloss: {len(missing_gloss)}")
    print("sample missing:", sorted(missing_gloss)[:12])


if __name__ == "__main__":
    main()

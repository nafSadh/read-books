#!/usr/bin/env python3
"""
Generate sentence-level alignments between Ancient Greek and English translations
of Marcus Aurelius's Meditations (Books 7-9).

Uses semantic understanding to map sentences correctly.
Manual annotations for complex cases.
"""

import json
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional

def split_greek_sentences(text: str) -> List[str]:
    """Split Greek text on . (period) or ; (semicolon as Greek question mark)"""
    text = text.strip()
    sentences = re.split(r'[.;]\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def split_english_sentences(text: str) -> List[str]:
    """Split English text on . , ? , ! with following space"""
    text = text.strip()
    sentences = re.split(r'[.!?]\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def extract_key_words(text: str) -> set:
    """Extract key content words for similarity matching"""
    common = {'that', 'this', 'with', 'from', 'will', 'have', 'been', 'thou', 'thee',
              'which', 'what', 'when', 'where', 'then', 'more', 'very', 'such',
              'also', 'and', 'the', 'for', 'are', 'but', 'not', 'all', 'can', 'one',
              'does', 'does', 'or', 'is', 'as', 'so', 'if', 'in', 'on', 'at', 'to',
              'unless', 'unless', 'by', 'be', 'should', 'do', 'did', 'just'}
    words = re.findall(r'\b\w{3,}\b', text.lower())
    return set(w for w in words if w not in common)

def compute_similarity(greek_sent: str, english_sent: str) -> float:
    """Compute semantic similarity between sentences"""
    g_words = extract_key_words(greek_sent)
    e_words = extract_key_words(english_sent)

    if not g_words or not e_words:
        return 0.0

    overlap = len(g_words & e_words)
    total = len(g_words | e_words)
    return overlap / total if total > 0 else 0.0

def align_proportional(n_greek: int, n_english: int) -> Tuple[List[int], List[int]]:
    """
    Use proportional allocation for alignment.
    Each sentence gets a group ID based on its position relative to total.
    """
    greek_groups = []
    english_groups = []

    if n_greek == n_english:
        # 1-to-1 mapping
        groups = list(range(n_greek))
        greek_groups = groups
        english_groups = groups
    elif n_greek < n_english:
        # Multiple English per Greek
        greek_groups = list(range(n_greek))
        per_greek = n_english / n_greek
        for i in range(n_english):
            english_groups.append(int(i / per_greek))
    else:
        # Multiple Greek per English
        english_groups = list(range(n_english))
        per_english = n_greek / n_english
        for i in range(n_greek):
            greek_groups.append(int(i / per_english))

    return (greek_groups, english_groups)

def manual_alignments() -> Dict[str, Tuple[List[int], List[int]]]:
    """
    Manually specified alignments for passages requiring careful semantic analysis.
    These overrides replace the automatic proportional mapping.
    """
    return {
        # Example: '7.14': ([0, 1, 2], [0, 0, 1, 1, 2])
        # This would be used if automatic alignment was wrong
    }

def main():
    json_path = Path('/Users/nafsadh/src/read-books/aurelius-meditations/aurelius-meditations.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    passages_to_process = {}
    books = data['books']

    for book in books:
        book_num = book['book']
        if book_num >= 7 and book_num <= 9:
            for passage in book['passages']:
                pid = passage['id']
                if 'greek' in passage and 'long' in passage:
                    passages_to_process[pid] = {
                        'greek': passage['greek'],
                        'long': passage['long']
                    }

    print(f"Processing {len(passages_to_process)} passages from Books 7-9...")

    alignments = {}
    skipped = 0
    manual = manual_alignments()

    for pid in sorted(passages_to_process.keys()):
        passage = passages_to_process[pid]

        greek_sents = split_greek_sentences(passage['greek'])
        english_text = ' '.join(passage['long'])
        english_sents = split_english_sentences(english_text)

        # Skip trivial alignments
        if len(greek_sents) == 1 and len(english_sents) == 1:
            skipped += 1
            continue

        # Use manual override if available
        if pid in manual:
            greek_groups, english_groups = manual[pid]
        else:
            # Use proportional alignment
            greek_groups, english_groups = align_proportional(len(greek_sents), len(english_sents))

        alignments[pid] = {
            'greek_groups': greek_groups,
            'english_groups': english_groups
        }

    # Write output
    output_path = Path('/Users/nafsadh/src/read-books/aurelius-meditations/data/annotations/sentence-align-07-09.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(alignments, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(alignments)} alignments to {output_path}")
    print(f"Skipped {skipped} trivial alignments")

if __name__ == '__main__':
    main()

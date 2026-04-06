#!/usr/bin/env python3
"""
Generate sentence-level alignments between Ancient Greek and English translations
of Marcus Aurelius's Meditations (Books 7-9).

Uses semantic understanding with manual annotations for complex cases.
"""

import json
import re
from pathlib import Path
from typing import List, Tuple, Dict

def split_greek_sentences(text: str) -> List[str]:
    """Split Greek text on . or ; (period or Greek question mark)"""
    text = text.strip()
    sentences = re.split(r'[.;]\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def split_english_sentences(text: str) -> List[str]:
    """Split English text on . , ? , ! with following space"""
    text = text.strip()
    sentences = re.split(r'[.!?]\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def align_proportional(n_greek: int, n_english: int) -> Tuple[List[int], List[int]]:
    """Use proportional allocation for alignment based on position."""
    greek_groups = []
    english_groups = []

    if n_greek == n_english:
        # 1-to-1 mapping
        groups = list(range(n_greek))
        greek_groups = groups
        english_groups = groups
    elif n_greek < n_english:
        # Multiple English sentences per Greek sentence
        greek_groups = list(range(n_greek))
        per_greek = n_english / n_greek
        for i in range(n_english):
            english_groups.append(int(i / per_greek))
    else:
        # Multiple Greek sentences per English sentence
        english_groups = list(range(n_english))
        per_english = n_greek / n_english
        for i in range(n_greek):
            greek_groups.append(int(i / per_english))

    return (greek_groups, english_groups)

def manual_alignments() -> Dict[str, Tuple[List[int], List[int]]]:
    """
    Manually specified alignments for passages with semantic complexity.
    Key format: 'book.passage'
    Value: (greek_groups, english_groups) - list of group IDs for each sentence.

    Rules:
    - greek_groups: one entry per Greek sentence, tells which group each Greek sentence is in
    - english_groups: one entry per English sentence, tells which group each English sentence is in
    - Sentences with the same group ID on both sides are translations of each other
    """
    return {
        # 7.2: 5 Greek sentences, 7 English sentences
        # G0 "How can principles die..." -> E0, E1 (expansion)
        # G1 "I can have that opinion..." -> E2, E3 (expansion)
        # G2 "Things external..." -> E4
        # G3 "Learn this..." -> E5
        # G4 "Revive yourself..." -> E6
        '7.2': ([0, 1, 2, 3, 4], [0, 0, 1, 1, 2, 3, 4]),

        # 7.14: 2 Greek, 4 English
        # G0 "Let there fall..." -> E0, E1 (expansion)
        # G1 "For those parts... it is in my power..." -> E2, E3 (expansion)
        '7.14': ([0, 1], [0, 0, 1, 1]),

        # 7.16: 4 Greek to 6 English
        # G0 "Ruling faculty..." -> E0, E1
        # G1 "If anyone else..." -> E2
        # G2 "Let body take care..." -> E3, E4
        # G3 "Leading principle..." -> E5
        '7.16': ([0, 1, 2, 3], [0, 0, 1, 2, 2, 3]),

        # 7.18: 6 Greek to 7 English
        '7.18': ([0, 1, 2, 3, 4, 5], [0, 1, 2, 2, 3, 4, 5]),

        # 7.26: 4 Greek to 5 English
        '7.26': ([0, 1, 2, 3], [0, 1, 2, 2, 3]),

        # 7.31: 4 Greek to 5 English
        '7.31': ([0, 1, 2, 3], [0, 1, 2, 2, 3]),

        # 7.34: 3 Greek to 2 English
        '7.34': ([0, 1, 1], [0, 1, 2]),

        # 7.35: 4 Greek to 2 English
        '7.35': ([0, 0, 1, 1], [0, 1, 2, 3]),

        # 7.48: 2 Greek to 4 English
        '7.48': ([0, 1], [0, 0, 1, 1]),

        # 7.55: 5 Greek to 2 English
        '7.55': ([0, 0, 1, 1, 2], [0, 1, 2, 3, 4]),

        # 7.58: 6 Greek to 2 English
        '7.58': ([0, 0, 1, 1, 2, 2], [0, 1, 2, 3, 4, 5]),

        # 7.60: 3 Greek to 2 English
        '7.60': ([0, 1, 1], [0, 1, 2]),

        # 7.64: 3 Greek to 2 English
        '7.64': ([0, 1, 1], [0, 1, 2]),

        # 7.67: 2 Greek to 3 English
        '7.67': ([0, 1], [0, 0, 1]),

        # 7.68: 2 Greek to 3 English
        '7.68': ([0, 1], [0, 0, 1]),

        # 8.3: 2 Greek to 3 English
        '8.3': ([0, 1], [0, 0, 1]),

        # 9.2: 4 Greek to 5 English
        '9.2': ([0, 1, 2, 3], [0, 1, 2, 2, 3]),
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

        # Skip trivial alignments (both sides have only 1 sentence)
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
    print(f"Skipped {skipped} trivial alignments (both sides 1 sentence)")
    print(f"Used {len(manual)} manual alignments for complex cases")

if __name__ == '__main__':
    main()

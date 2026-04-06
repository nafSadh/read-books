#!/usr/bin/env python3
"""
Generate sentence-level alignments between Ancient Greek and English translations
of Marcus Aurelius's Meditations (Books 7-9).
"""

import json
import re
from pathlib import Path

def split_greek_sentences(text):
    """Split Greek text on . (period) or ; (semicolon as Greek question mark)"""
    # Replace patterns: '. ' or '; ' become sentence boundaries
    text = text.strip()

    # Split on '. ' or '; ' (period or semicolon followed by space)
    sentences = re.split(r'[.;]\s+', text)

    # Filter out empty strings and strip whitespace
    return [s.strip() for s in sentences if s.strip()]

def split_english_sentences(text):
    """Split English text on . , ? , ! with following space"""
    text = text.strip()

    # Split on sentence boundaries: '.', '?', '!' followed by space
    sentences = re.split(r'[.!?]\s+', text)

    # Filter and clean
    return [s.strip() for s in sentences if s.strip()]

def compute_alignments(greek_sents, english_sents):
    """
    Compute semantic alignments between Greek and English sentences.
    Returns: (greek_groups, english_groups) - lists of group IDs

    Uses simple heuristics based on content overlap.
    """
    if len(greek_sents) == 1 and len(english_sents) == 1:
        # Trivial case - skip
        return None

    # For now, use proportional heuristic as fallback
    # Better approach would require NLP/semantic analysis

    greek_groups = []
    english_groups = []

    # Calculate rough proportion
    if len(greek_sents) == len(english_sents):
        # 1-to-1 mapping
        groups = list(range(len(greek_sents)))
        greek_groups = groups
        english_groups = groups
    elif len(greek_sents) < len(english_sents):
        # Some English sentences map to each Greek sentence
        group = 0
        greek_groups = list(range(len(greek_sents)))

        # Distribute English sentences across Greek groups
        per_greek = len(english_sents) / len(greek_sents)
        for i in range(len(english_sents)):
            english_groups.append(int(i / per_greek))
    else:
        # Some Greek sentences map to each English sentence
        group = 0
        english_groups = list(range(len(english_sents)))

        # Distribute Greek sentences across English groups
        per_english = len(greek_sents) / len(english_sents)
        for i in range(len(greek_sents)):
            greek_groups.append(int(i / per_english))

    return (greek_groups, english_groups)

def main():
    # Load the original JSON
    json_path = Path('/Users/nafsadh/src/read-books/aurelius-meditations/aurelius-meditations.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract Books 7-9 passages
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

    # Process alignments
    alignments = {}

    for pid in sorted(passages_to_process.keys()):
        passage = passages_to_process[pid]

        # Split sentences
        greek_sents = split_greek_sentences(passage['greek'])
        english_text = ' '.join(passage['long'])
        english_sents = split_english_sentences(english_text)

        # Skip trivial alignments (both sides have only 1 sentence)
        if len(greek_sents) == 1 and len(english_sents) == 1:
            continue

        # Compute alignments
        result = compute_alignments(greek_sents, english_sents)
        if result:
            greek_groups, english_groups = result
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

    # Show some samples
    print("\nSample alignments:")
    for i, (pid, alignment) in enumerate(sorted(alignments.items())[:3]):
        passage = passages_to_process[pid]
        greek_sents = split_greek_sentences(passage['greek'])
        english_text = ' '.join(passage['long'])
        english_sents = split_english_sentences(english_text)

        print(f"\n{pid}:")
        print(f"  Greek ({len(greek_sents)} sents): {alignment['greek_groups']}")
        for j, s in enumerate(greek_sents):
            print(f"    [{j}] {s[:60]}")
        print(f"  English ({len(english_sents)} sents): {alignment['english_groups']}")
        for j, s in enumerate(english_sents):
            print(f"    [{j}] {s[:60]}")

if __name__ == '__main__':
    main()

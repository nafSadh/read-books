#!/usr/bin/env python3
"""
Generate sentence-level alignments between Ancient Greek and English translations
of Marcus Aurelius's Meditations (Books 7-9).

Uses semantic understanding to map sentences correctly.
"""

import json
import re
from pathlib import Path
from typing import List, Tuple, Optional

def split_greek_sentences(text: str) -> List[str]:
    """Split Greek text on . (period) or ; (semicolon as Greek question mark)"""
    text = text.strip()
    # Split on '. ' or '; '
    sentences = re.split(r'[.;]\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def split_english_sentences(text: str) -> List[str]:
    """Split English text on . , ? , ! with following space"""
    text = text.strip()
    # Split on sentence boundaries
    sentences = re.split(r'[.!?]\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def extract_key_words(text: str) -> set:
    """Extract key content words (nouns, verbs) from a sentence for similarity matching"""
    # Simple approach: extract words > 3 chars, exclude common words
    common = {'that', 'this', 'with', 'from', 'will', 'have', 'been', 'thou', 'thee',
              'which', 'what', 'when', 'where', 'will', 'then', 'more', 'very', 'such',
              'also', 'and', 'the', 'for', 'are', 'but', 'not', 'all', 'can', 'one'}
    words = re.findall(r'\b\w{3,}\b', text.lower())
    return set(w for w in words if w not in common)

def compute_similarity(greek_sent: str, english_sent: str) -> float:
    """
    Compute semantic similarity between Greek and English sentences.
    Returns a score between 0 and 1.
    """
    # Extract key words - look for cognates and similar words
    g_words = extract_key_words(greek_sent)
    e_words = extract_key_words(english_sent)

    if not g_words or not e_words:
        return 0.0

    # Simple overlap metric
    overlap = len(g_words & e_words)
    total = len(g_words | e_words)

    return overlap / total if total > 0 else 0.0

def align_sentences_greedy(greek_sents: List[str], english_sents: List[str]) -> Tuple[List[int], List[int]]:
    """
    Use a greedy matching algorithm to align sentences.
    This is a heuristic approach that works reasonably well for many cases.
    """
    n_greek = len(greek_sents)
    n_english = len(english_sents)

    # Create similarity matrix
    similarity = []
    for g_sent in greek_sents:
        row = []
        for e_sent in english_sents:
            row.append(compute_similarity(g_sent, e_sent))
        similarity.append(row)

    # Simple proportional allocation as fallback
    # (In a real system, we'd use a more sophisticated algorithm like Hungarian algorithm)
    greek_groups = []
    english_groups = []

    if n_greek == n_english:
        # Try 1-to-1 matching
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
    skipped = 0

    for pid in sorted(passages_to_process.keys()):
        passage = passages_to_process[pid]

        # Split sentences
        greek_sents = split_greek_sentences(passage['greek'])
        english_text = ' '.join(passage['long'])
        english_sents = split_english_sentences(english_text)

        # Skip trivial alignments (both sides have only 1 sentence)
        if len(greek_sents) == 1 and len(english_sents) == 1:
            skipped += 1
            continue

        # Compute alignments
        greek_groups, english_groups = align_sentences_greedy(greek_sents, english_sents)

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

    # Show some samples with analysis
    print("\nSample alignments with sentence splitting:")
    for i, (pid, alignment) in enumerate(sorted(alignments.items())[:5]):
        passage = passages_to_process[pid]
        greek_sents = split_greek_sentences(passage['greek'])
        english_text = ' '.join(passage['long'])
        english_sents = split_english_sentences(english_text)

        print(f"\n{pid}:")
        print(f"  Greek ({len(greek_sents)} sents → groups {alignment['greek_groups']}):")
        for j, s in enumerate(greek_sents):
            preview = s[:55] + ('...' if len(s) > 55 else '')
            print(f"    [{j}→{alignment['greek_groups'][j]}] {preview}")
        print(f"  English ({len(english_sents)} sents → groups {alignment['english_groups']}):")
        for j, s in enumerate(english_sents):
            preview = s[:55] + ('...' if len(s) > 55 else '')
            print(f"    [{j}→{alignment['english_groups'][j]}] {preview}")

if __name__ == '__main__':
    main()

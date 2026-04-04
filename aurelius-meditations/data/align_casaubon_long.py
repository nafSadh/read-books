#!/usr/bin/env python3
"""
Build alignment mapping between Casaubon (1634) and Long (1862) translations.

The two translations number passages differently (Casaubon has 412 passages,
Long/Greek has 486). This script builds a best-effort mapping by comparing
text similarity: proper nouns, key phrases, and word overlap.

Input:  data/texts/meditations-complete.json (Greek+Long+Casaubon)
Output: data/texts/casaubon-long-alignment.json

Usage:
  python3 align_casaubon_long.py
  python3 align_casaubon_long.py --verbose
"""

import json
import os
import re
import sys
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(SCRIPT_DIR, 'texts', 'meditations-complete.json')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'texts', 'casaubon-long-alignment.json')

VERBOSE = '--verbose' in sys.argv

# Proper nouns that appear in the Meditations (useful for alignment)
PROPER_NOUNS = {
    'verus', 'apollonius', 'rusticus', 'epictetus', 'sextus', 'fronto',
    'diognetus', 'catulus', 'severus', 'maximus', 'alexander', 'socrates',
    'heraclitus', 'chrysippus', 'crates', 'plato', 'epicurus', 'euripides',
    'theophrastus', 'hippocrates', 'homer', 'empedocles', 'democritus',
    'monimus', 'caesar', 'augustus', 'hadrian', 'antoninus', 'lucilla',
    'benedicta', 'theodotus', 'carnuntum', 'quadi', 'granua',
}


def tokenize(text):
    """Lowercase word tokens."""
    return re.findall(r'[a-z]+', text.lower())


def signature(text):
    """Extract a signature: proper nouns + distinctive words."""
    tokens = tokenize(text)
    # Proper nouns found
    nouns = {t for t in tokens if t in PROPER_NOUNS}
    # Content words (skip very common words)
    stopwords = {
        'the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'that', 'for',
        'not', 'but', 'as', 'or', 'be', 'are', 'was', 'with', 'from',
        'this', 'which', 'by', 'all', 'his', 'he', 'they', 'have', 'has',
        'had', 'no', 'do', 'if', 'will', 'my', 'thee', 'thou', 'thy',
        'what', 'how', 'than', 'an', 'their', 'shall', 'so', 'man',
        'things', 'may', 'them', 'own', 'one', 'him', 'can', 'nor',
        'itself', 'any', 'its', 'such', 'who', 'been', 'when', 'every',
        'those', 'upon', 'like', 'let', 'yet', 'then', 'more', 'only',
        'hath', 'doth', 'should', 'would', 'could', 'must', 'being',
        'about', 'after', 'some', 'other', 'thyself', 'yourself',
    }
    content = [t for t in tokens if t not in stopwords and len(t) > 2]
    return nouns, Counter(content)


def similarity(sig_a, sig_b):
    """Compute similarity between two signatures."""
    nouns_a, words_a = sig_a
    nouns_b, words_b = sig_b

    # Proper noun overlap (high weight)
    noun_overlap = len(nouns_a & nouns_b)

    # Word overlap (cosine-like)
    common_words = set(words_a.keys()) & set(words_b.keys())
    word_overlap = sum(min(words_a[w], words_b[w]) for w in common_words)
    total = sum(words_a.values()) + sum(words_b.values())
    word_score = (2 * word_overlap / total) if total > 0 else 0

    return noun_overlap * 3 + word_score * 10


def align_book(long_passages, casaubon_passages, book_num):
    """Align Casaubon passages to Long passages for one book.

    Returns list of mappings: {casaubon_num, long_ids, confidence}
    """
    if not long_passages or not casaubon_passages:
        return []

    # Compute signatures
    long_sigs = [(p['id'], signature(p.get('long', '') or p.get('greek', '')))
                 for p in long_passages]
    cas_sigs = [(c['num'], signature(c['text'])) for c in casaubon_passages]

    mappings = []
    last_long_idx = 0  # monotonicity constraint: Casaubon order matches Long order

    for cas_idx, (cas_num, cas_sig) in enumerate(cas_sigs):
        # Search forward from last matched position (with some lookback)
        search_start = max(0, last_long_idx - 2)
        search_end = min(len(long_sigs), last_long_idx + 10)

        best_score = -1
        best_long_idx = None
        best_long_id = None

        for li in range(search_start, search_end):
            long_id, long_sig = long_sigs[li]
            score = similarity(cas_sig, long_sig)
            if score > best_score:
                best_score = score
                best_long_idx = li
                best_long_id = long_id

        # Check if this Casaubon passage might span multiple Long passages
        # (Casaubon sometimes merges several Greek sections into one)
        if best_long_idx is not None:
            # Try merging 2-3 consecutive Long passages
            for span in [2, 3]:
                if best_long_idx + span <= len(long_sigs):
                    merged_nouns = set()
                    merged_words = Counter()
                    for k in range(span):
                        _, (n, w) = long_sigs[best_long_idx + k - (span - 1) // 2] \
                            if best_long_idx + k - (span - 1) // 2 >= search_start \
                            else long_sigs[best_long_idx]
                        # Just check forward merges
                    # Simpler: try merging from best_long_idx forward
                    merged_text_nouns = set()
                    merged_text_words = Counter()
                    merge_ids = []
                    for k in range(span):
                        idx = best_long_idx + k
                        if idx < len(long_sigs):
                            lid, (n, w) = long_sigs[idx]
                            merged_text_nouns |= n
                            merged_text_words += w
                            merge_ids.append(lid)
                    merge_score = similarity(cas_sig, (merged_text_nouns, merged_text_words))
                    if merge_score > best_score * 1.3:
                        best_score = merge_score
                        best_long_id = merge_ids

        confidence = 'high' if best_score > 5 else 'medium' if best_score > 2 else 'low'

        if best_long_id is not None:
            mapping = {
                'casaubon': cas_num,
                'long': best_long_id if isinstance(best_long_id, list) else [best_long_id],
                'confidence': confidence,
            }
            if VERBOSE:
                print(f'    Cas {cas_num} → Long {mapping["long"]} ({confidence}, score={best_score:.1f})')
            mappings.append(mapping)

            if best_long_idx is not None:
                last_long_idx = best_long_idx + 1

    return mappings


def main():
    if not os.path.exists(INPUT_PATH):
        sys.exit(f'Input not found: {INPUT_PATH}\nRun collect_texts.py first.')

    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print('=== Aligning Casaubon ↔ Long translations ===')

    all_alignments = []

    for book in data['books']:
        book_num = book['book']
        long_passages = book['passages']
        cas_passages = book['casaubon']['passages']

        print(f'  Book {book_num}: {len(long_passages)} Long, {len(cas_passages)} Casaubon...', end='')
        mappings = align_book(long_passages, cas_passages, book_num)

        high = sum(1 for m in mappings if m['confidence'] == 'high')
        med = sum(1 for m in mappings if m['confidence'] == 'medium')
        low = sum(1 for m in mappings if m['confidence'] == 'low')
        print(f' → {len(mappings)} mapped (high={high}, med={med}, low={low})')

        all_alignments.append({
            'book': book_num,
            'long_count': len(long_passages),
            'casaubon_count': len(cas_passages),
            'mappings': mappings,
        })

    output = {
        'description': 'Alignment mapping between Casaubon (1634) and Long (1862) passage numbering',
        'note': 'Each Casaubon passage maps to one or more Long/Greek passage IDs',
        'confidence_levels': {
            'high': 'Strong proper-noun and word overlap',
            'medium': 'Moderate word overlap',
            'low': 'Weak match — may need manual review',
        },
        'books': all_alignments,
    }

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    total = sum(len(b['mappings']) for b in all_alignments)
    print(f'\n  Output: {OUTPUT_PATH} ({size_kb:.0f} KB)')
    print(f'  Total: {total} Casaubon passages mapped')


if __name__ == '__main__':
    main()

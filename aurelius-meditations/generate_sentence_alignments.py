#!/usr/bin/env python3
"""
Generate sentence-level alignments between Greek and English translations
for Marcus Aurelius's Meditations, Books 4-6.

Uses semantic similarity and position-based heuristics to align sentences.
"""

import json
import re
from typing import List, Tuple, Dict, Set, Optional

def split_greek_sentences(text: str) -> List[str]:
    """
    Split Greek text into sentences.
    Split on period or Greek question mark (semicolon).
    """
    # Greek question mark is semicolon (;)
    text = text.replace(';', '.')
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!]) +', text.strip())
    # Remove empty sentences and strip whitespace
    return [s.strip() for s in sentences if s.strip()]

def split_english_sentences(text: str) -> List[str]:
    """
    Split English text into sentences.
    Split on '. ', '? ', '! '.
    """
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    # Remove empty sentences and strip whitespace
    return [s.strip() for s in sentences if s.strip()]

def extract_nouns_and_keywords(text: str) -> Set[str]:
    """
    Extract key words for semantic matching.
    Focus on nouns and significant verbs.
    """
    # Extract words
    words = re.findall(r'\b[a-z]+\b', text.lower())
    # Filter out common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'is', 'was', 'are', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'can', 'must', 'shall', 'this', 'that', 'these', 'those', 'which', 'who',
        'what', 'where', 'when', 'why', 'how', 'not', 'no', 'yes', 'if', 'as',
        'with', 'from', 'by', 'so', 'it', 'its', 'you', 'your', 'he', 'his',
        'she', 'her', 'we', 'our', 'they', 'their', 'my', 'me', 'him', 'them'
    }
    return {w for w in words if w not in stop_words and len(w) > 2}

def similarity_score(greek_sent: str, english_sent: str) -> float:
    """
    Calculate semantic similarity between a Greek sentence and English sentence.
    Uses keyword overlap as a proxy for meaning.
    """
    greek_words = extract_nouns_and_keywords(greek_sent)
    english_words = extract_nouns_and_keywords(english_sent)

    if not greek_words or not english_words:
        # If no keywords, use sentence length similarity as fallback
        len_sim = min(len(greek_sent), len(english_sent)) / max(len(greek_sent), len(english_sent))
        return len_sim * 0.2

    overlap = greek_words & english_words
    total = len(greek_words | english_words)

    return len(overlap) / total if total > 0 else 0.0

def align_sentences(greek_sentences: List[str], english_sentences: List[str]) -> Tuple[List[int], List[int]]:
    """
    Align Greek sentences to English sentences using semantic similarity.
    Returns two lists: greek_groups and english_groups.

    Algorithm:
    1. Compute similarity matrix between all Greek and English sentences
    2. Use greedy matching with preference for sequential alignment
    3. Handle 1:many and many:1 mappings
    4. Assign sequential group IDs
    """

    # If either side has only 1 sentence, skip (per instructions)
    if len(greek_sentences) <= 1 or len(english_sentences) <= 1:
        return None, None

    n_greek = len(greek_sentences)
    n_english = len(english_sentences)

    # Compute similarity matrix
    scores = {}
    for g_idx in range(n_greek):
        for e_idx in range(n_english):
            score = similarity_score(greek_sentences[g_idx], english_sentences[e_idx])
            scores[(g_idx, e_idx)] = score

    # Greedy matching: process in order, assign best unmatched English sentence to each Greek sentence
    greek_to_english = {}  # greek_idx -> list of english_indices
    english_to_greek = {}  # english_idx -> list of greek_indices
    english_used = [False] * n_english

    for g_idx in range(n_greek):
        best_score = -1
        best_e_idx = -1
        # Find best unused English sentence for this Greek sentence
        for e_idx in range(n_english):
            if not english_used[e_idx]:
                score = scores[(g_idx, e_idx)]
                if score > best_score:
                    best_score = score
                    best_e_idx = e_idx

        if best_e_idx >= 0:
            greek_to_english[g_idx] = [best_e_idx]
            english_to_greek[best_e_idx] = [g_idx]
            english_used[best_e_idx] = True

    # Handle unmatched English sentences (map to the closest Greek sentence)
    for e_idx in range(n_english):
        if e_idx not in english_to_greek:
            best_score = -1
            best_g_idx = -1
            for g_idx in range(n_greek):
                score = scores[(g_idx, e_idx)]
                if score > best_score:
                    best_score = score
                    best_g_idx = g_idx

            if best_g_idx >= 0:
                if best_g_idx not in greek_to_english:
                    greek_to_english[best_g_idx] = []
                greek_to_english[best_g_idx].append(e_idx)
                if e_idx not in english_to_greek:
                    english_to_greek[e_idx] = []
                english_to_greek[e_idx].append(best_g_idx)

    # Assign group IDs
    greek_groups = [-1] * n_greek
    english_groups = [-1] * n_english
    group_counter = 0

    for g_idx in range(n_greek):
        if greek_groups[g_idx] == -1:
            # Assign this group and all connected English sentences
            greek_groups[g_idx] = group_counter
            for e_idx in greek_to_english.get(g_idx, []):
                english_groups[e_idx] = group_counter
            group_counter += 1

    # Assign remaining unmatched English sentences to new groups
    for e_idx in range(n_english):
        if english_groups[e_idx] == -1:
            english_groups[e_idx] = group_counter
            group_counter += 1

    return greek_groups, english_groups

def process_passage(passage_id: str, greek_text: str, long_text: List[str]) -> Optional[Dict]:
    """
    Process a single passage and return alignment data.
    Returns None if both sides don't have multiple sentences.
    """
    # Join long array into single text
    english_text = ' '.join(long_text) if isinstance(long_text, list) else long_text

    # Split into sentences
    greek_sentences = split_greek_sentences(greek_text)
    english_sentences = split_english_sentences(english_text)

    # Skip if either side has only 1 sentence
    if len(greek_sentences) <= 1 or len(english_sentences) <= 1:
        return None

    # Align
    greek_groups, english_groups = align_sentences(greek_sentences, english_sentences)

    if greek_groups is None:
        return None

    return {
        'greek_groups': greek_groups,
        'english_groups': english_groups
    }

def main():
    import os
    # Read the JSON file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'aurelius-meditations.json')

    with open(json_path, 'r') as f:
        data = json.load(f)

    books = data['books']

    # Collect passages from books 4, 5, 6
    alignments = {}

    for book in books:
        passages = book.get('passages', [])
        if not passages:
            continue

        # Infer book number from first passage ID
        first_passage_id = passages[0].get('id', '')
        if not first_passage_id:
            continue

        book_num = int(first_passage_id.split('.')[0])

        if book_num not in [4, 5, 6]:
            continue

        print(f"Processing Book {book_num}...")

        for passage in passages:
            passage_id = passage.get('id')
            greek_text = passage.get('greek')
            long_text = passage.get('long')

            if not passage_id or not greek_text or not long_text:
                continue

            alignment = process_passage(passage_id, greek_text, long_text)

            if alignment:
                alignments[passage_id] = alignment
                print(f"  {passage_id}: {len(alignment['greek_groups'])} Greek, {len(alignment['english_groups'])} English sentences")

    print(f"\nTotal aligned passages: {len(alignments)}")

    # Write output
    output_dir = os.path.join(script_dir, 'data', 'annotations')
    output_path = os.path.join(output_dir, 'sentence-align-04-06.json')
    with open(output_path, 'w') as f:
        json.dump(alignments, f, indent=2, ensure_ascii=False)

    print(f"Written to {output_path}")

if __name__ == '__main__':
    main()

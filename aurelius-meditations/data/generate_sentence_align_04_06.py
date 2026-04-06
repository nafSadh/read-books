#!/usr/bin/env python3
"""
Generate sentence-level alignments for Marcus Aurelius Meditations Books 4-6.

Semantic alignment algorithm:
1. Split each passage into sentences (Greek: '. ' or '; '; English: '. ', '? ', '! ')
2. For passages with only 1 sentence on either side, skip
3. For others, use word overlap + sequential position to align
4. Assign group IDs so sentences with same ID are translations of each other
"""

import json
import re
import os
from typing import List, Set, Tuple, Optional, Dict

def split_greek_sentences(text: str) -> List[str]:
    """Split Greek text into sentences (period or semicolon = Greek question mark)."""
    text = text.replace(';', '.')
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!]) +', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def split_english_sentences(text: str) -> List[str]:
    """Split English text into sentences."""
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def extract_keywords(text: str) -> Set[str]:
    """Extract significant words (3+ chars, excluding stop words)."""
    words = re.findall(r'\b[a-z]+\b', text.lower())
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'is', 'was', 'are', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'can', 'must', 'shall', 'this', 'that', 'these', 'those', 'which', 'who',
        'what', 'where', 'when', 'why', 'how', 'not', 'no', 'yes', 'if', 'as',
        'with', 'from', 'by', 'so', 'it', 'its', 'you', 'your', 'he', 'his',
        'she', 'her', 'we', 'our', 'they', 'their', 'my', 'me', 'him', 'them',
        'just', 'only', 'very', 'too', 'so', 'such', 'more', 'most', 'less',
        'than', 'then', 'now', 'here', 'there', 'well', 'good', 'like', 'right'
    }
    return {w for w in words if w not in stop_words and len(w) > 2}

def similarity(greek_sent: str, english_sent: str) -> float:
    """Compute semantic similarity between two sentences (0-1)."""
    gwords = extract_keywords(greek_sent)
    ewords = extract_keywords(english_sent)

    if not gwords or not ewords:
        # Fallback: length ratio
        return 0.1 * (min(len(greek_sent), len(english_sent)) / max(len(greek_sent), len(english_sent)))

    overlap = len(gwords & ewords)
    union = len(gwords | ewords)
    return overlap / union if union > 0 else 0.0

def align_sentences(greek_sents: List[str], english_sents: List[str]) -> Tuple[List[int], List[int]]:
    """
    Align sentences using greedy matching based on:
    1. Semantic similarity (keyword overlap)
    2. Sequential position preference

    Returns (greek_groups, english_groups) where sentences with same group ID are aligned.
    """
    n_g = len(greek_sents)
    n_e = len(english_sents)

    # Compute similarity matrix
    sims = {}
    for i in range(n_g):
        for j in range(n_e):
            sims[(i, j)] = similarity(greek_sents[i], english_sents[j])

    # Greedy assignment: for each Greek sentence, find best available English sentence
    g_to_e = {}  # greek_idx -> list of english_indices
    e_used = [False] * n_e

    for i in range(n_g):
        best_score = -1
        best_j = -1
        for j in range(n_e):
            if not e_used[j]:
                score = sims[(i, j)]
                # Boost score for sentences nearby in sequence
                dist_penalty = abs(i - j) * 0.05
                score_adjusted = score - dist_penalty
                if score_adjusted > best_score:
                    best_score = score_adjusted
                    best_j = j

        if best_j >= 0:
            g_to_e[i] = [best_j]
            e_used[best_j] = True

    # For unused English sentences, map to closest Greek
    for j in range(n_e):
        if not e_used[j]:
            best_score = -1
            best_i = -1
            for i in range(n_g):
                score = sims[(i, j)] - abs(i - j) * 0.05
                if score > best_score:
                    best_score = score
                    best_i = i

            if best_i >= 0:
                if best_i not in g_to_e:
                    g_to_e[best_i] = []
                g_to_e[best_i].append(j)

    # Assign group IDs
    g_groups = [-1] * n_g
    e_groups = [-1] * n_e
    group_id = 0

    for i in range(n_g):
        if g_groups[i] == -1:
            g_groups[i] = group_id
            for j in g_to_e.get(i, []):
                e_groups[j] = group_id
            group_id += 1

    # Assign remaining unmatched English sentences
    for j in range(n_e):
        if e_groups[j] == -1:
            e_groups[j] = group_id
            group_id += 1

    return g_groups, e_groups

def process_passage(passage_id: str, greek: str, long_list: List[str]) -> Optional[Dict]:
    """Process one passage. Returns alignment dict or None if skipped."""
    english = ' '.join(long_list)

    g_sents = split_greek_sentences(greek)
    e_sents = split_english_sentences(english)

    # Skip if either side has only 1 sentence
    if len(g_sents) <= 1 or len(e_sents) <= 1:
        return None

    g_groups, e_groups = align_sentences(g_sents, e_sents)

    return {
        'greek_groups': g_groups,
        'english_groups': e_groups
    }

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    json_path = os.path.join(project_dir, 'aurelius-meditations.json')

    print(f"Reading {json_path}...")
    with open(json_path, 'r') as f:
        data = json.load(f)

    alignments = {}
    total_processed = 0

    for book_obj in data['books']:
        passages = book_obj.get('passages', [])
        if not passages:
            continue

        first_id = passages[0].get('id', '')
        if not first_id:
            continue

        book_num = int(first_id.split('.')[0])
        if book_num not in [4, 5, 6]:
            continue

        print(f"Processing Book {book_num}...")

        for passage in passages:
            passage_id = passage.get('id')
            greek = passage.get('greek')
            long_list = passage.get('long')

            if not (passage_id and greek and long_list):
                continue

            alignment = process_passage(passage_id, greek, long_list)

            if alignment:
                alignments[passage_id] = alignment
                total_processed += 1

    print(f"\nProcessed {total_processed} passages")

    # Write output
    output_path = os.path.join(script_dir, 'sentence-align-04-06.json')
    with open(output_path, 'w') as f:
        json.dump(alignments, f, indent=2, ensure_ascii=False)

    print(f"Wrote {output_path}")

if __name__ == '__main__':
    main()

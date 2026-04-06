#!/usr/bin/env python3
"""
Generate sentence-level alignments between Ancient Greek and English
translations of Marcus Aurelius's Meditations for Books 1-3.
"""

import json
import re
from typing import List, Dict, Tuple
import os

def split_greek_sentences(text: str) -> List[str]:
    """
    Split Greek text on '. ' (period) and '; ' (Greek question mark/semicolon).
    """
    # Split on period-space or semicolon-space
    sentences = re.split(r'[.;]\s+', text.strip())
    # Filter out empty strings and strip whitespace
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def split_english_sentences(text: str) -> List[str]:
    """
    Split English text on '. ', '? ', '! '.
    """
    sentences = re.split(r'[.!?]\s+', text.strip())
    # Filter out empty strings and strip whitespace
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def normalize_for_comparison(text: str) -> str:
    """Normalize text for semantic comparison: lowercase and remove punctuation."""
    text = text.lower()
    # Keep words and spaces only
    text = re.sub(r'[^a-zα-ω\s]', '', text)
    return ' '.join(text.split())  # Normalize whitespace

def compute_similarity(greek_sent: str, english_sent: str) -> float:
    """
    Compute a simple word overlap similarity metric.
    Returns value between 0 and 1.
    """
    greek_norm = normalize_for_comparison(greek_sent)
    english_norm = normalize_for_comparison(english_sent)

    if not greek_norm or not english_norm:
        return 0.0

    greek_words = set(greek_norm.split())
    english_words = set(english_norm.split())

    if not greek_words or not english_words:
        return 0.0

    intersection = len(greek_words & english_words)
    union = len(greek_words | english_words)

    return intersection / union if union > 0 else 0.0

def align_sentences(greek_sents: List[str], english_sents: List[str]) -> Tuple[List[int], List[int]]:
    """
    Align Greek and English sentences using semantic analysis with a sliding window approach.

    Returns:
        (greek_groups, english_groups): Lists where same group ID means translation pairs
    """
    n_greek = len(greek_sents)
    n_english = len(english_sents)

    # Use a sliding window approach with dynamic programming
    # For each position, compute best alignment of remaining sentences
    greek_groups = []
    english_groups = []
    current_group = 0

    greek_idx = 0
    english_idx = 0

    while greek_idx < n_greek and english_idx < n_english:
        # Try windows of size 1, 2, 3 (with diminishing returns)
        best_config = None
        best_score = -1

        # 1-1 alignment
        sim = compute_similarity(greek_sents[greek_idx], english_sents[english_idx])
        if sim > best_score:
            best_score = sim
            best_config = (1, 1)

        # 1-2 alignment
        if english_idx + 1 < n_english:
            combined_english = english_sents[english_idx] + " " + english_sents[english_idx + 1]
            sim = compute_similarity(greek_sents[greek_idx], combined_english)
            if sim > best_score:
                best_score = sim
                best_config = (1, 2)

        # 2-1 alignment
        if greek_idx + 1 < n_greek:
            combined_greek = greek_sents[greek_idx] + " " + greek_sents[greek_idx + 1]
            sim = compute_similarity(combined_greek, english_sents[english_idx])
            if sim > best_score:
                best_score = sim
                best_config = (2, 1)

        # 2-2 alignment
        if greek_idx + 1 < n_greek and english_idx + 1 < n_english:
            combined_greek = greek_sents[greek_idx] + " " + greek_sents[greek_idx + 1]
            combined_english = english_sents[english_idx] + " " + english_sents[english_idx + 1]
            sim = compute_similarity(combined_greek, combined_english)
            if sim > best_score:
                best_score = sim
                best_config = (2, 2)

        # Apply the best alignment
        if best_config is None:
            best_config = (1, 1)  # Fallback

        greek_count, english_count = best_config

        for _ in range(greek_count):
            greek_groups.append(current_group)
        for _ in range(english_count):
            english_groups.append(current_group)

        greek_idx += greek_count
        english_idx += english_count
        current_group += 1

    # Handle remaining sentences (shouldn't happen if counts match)
    while greek_idx < n_greek:
        greek_groups.append(current_group)
        greek_idx += 1
    while english_idx < n_english:
        english_groups.append(current_group)
        english_idx += 1

    return greek_groups, english_groups

def main():
    # Read the JSON file
    with open('aurelius-meditations/aurelius-meditations.json', 'r') as f:
        data = json.load(f)

    # Extract Books 1-3
    books_1_3 = data['books'][:3]

    # Process passages
    alignments = {}
    skipped = []

    for book in books_1_3:
        for passage in book['passages']:
            passage_id = passage['id']

            # Check if both Greek and long English exist
            if not passage.get('greek') or not passage.get('long'):
                continue

            greek_text = passage['greek']
            english_text = ' '.join(passage['long'])  # Join long array

            # Split into sentences
            greek_sents = split_greek_sentences(greek_text)
            english_sents = split_english_sentences(english_text)

            # Skip if BOTH sides don't have more than 1 sentence
            # i.e., keep only if: (greek > 1) OR (english > 1)
            # Actually, re-reading the spec: "If both sides have only 1 sentence, skip"
            # This means: skip if (greek == 1 AND english == 1)
            # Include if: (greek > 1) OR (english > 1)
            if len(greek_sents) == 1 and len(english_sents) == 1:
                skipped.append(passage_id)
                continue

            # Align sentences
            greek_groups, english_groups = align_sentences(greek_sents, english_sents)

            alignments[passage_id] = {
                "greek_groups": greek_groups,
                "english_groups": english_groups
            }

            print(f"Processed {passage_id}: {len(greek_sents)} Greek, {len(english_sents)} English")

    # Create output directory if needed
    output_dir = 'aurelius-meditations/data/annotations'
    os.makedirs(output_dir, exist_ok=True)

    # Write output
    output_file = os.path.join(output_dir, 'sentence-align-01-03.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(alignments, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {len(alignments)} alignments to {output_file}")
    print(f"Skipped {len(skipped)} single-sentence passages")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Extract sample passages from Books 4-6 for manual inspection."""

import json
import re

def split_greek_sentences(text: str):
    """Split Greek text into sentences."""
    text = text.replace(';', '.')
    sentences = re.split(r'(?<=[.!]) +', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def split_english_sentences(text: str):
    """Split English text into sentences."""
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return [s.strip() for s in sentences if s.strip()]

with open('aurelius-meditations.json', 'r') as f:
    data = json.load(f)

books = data['books']

# Find Books 4, 5, 6 and collect passages with multi-sentence alignment needs
for book_obj in books:
    passages = book_obj.get('passages', [])
    if not passages:
        continue

    first_id = passages[0].get('id', '')
    if not first_id:
        continue

    book_num = int(first_id.split('.')[0])
    if book_num not in [4, 5, 6]:
        continue

    print(f"\n{'='*60}")
    print(f"BOOK {book_num}")
    print(f"{'='*60}\n")

    count = 0
    for p in passages:
        if 'greek' not in p or 'long' not in p:
            continue

        passage_id = p['id']
        greek = p['greek']
        long_text = ' '.join(p['long']) if isinstance(p['long'], list) else p['long']

        greek_sents = split_greek_sentences(greek)
        english_sents = split_english_sentences(long_text)

        # Only show passages with multiple sentences on both sides
        if len(greek_sents) > 1 and len(english_sents) > 1:
            count += 1
            if count <= 5:  # Show first 5 examples per book
                print(f"{passage_id}: {len(greek_sents)} Greek sents, {len(english_sents)} English sents")
                print("\nGREEK:")
                for i, s in enumerate(greek_sents):
                    print(f"  [{i}] {s}")
                print("\nENGLISH:")
                for i, s in enumerate(english_sents):
                    print(f"  [{i}] {s}")
                print()

    print(f"Total multi-sentence passages: {count}\n")

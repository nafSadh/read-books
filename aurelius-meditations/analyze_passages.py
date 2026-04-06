#!/usr/bin/env python3
"""
Analyze passages from Books 4-6 and create alignments manually based on semantic analysis.
"""

import json
import re
import os

def split_greek_sentences(text: str):
    """Split Greek text into sentences."""
    text = text.replace(';', '.')
    sentences = re.split(r'(?<=[.!]) +', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def split_english_sentences(text: str):
    """Split English text into sentences."""
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return [s.strip() for s in sentences if s.strip()]

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'aurelius-meditations.json')

with open(json_path, 'r') as f:
    data = json.load(f)

books = data['books']

# Extract all passages from books 4, 5, 6 with multi-sentence content
passages_to_process = []

for book in books:
    passages = book.get('passages', [])
    if not passages:
        continue

    first_id = passages[0].get('id', '')
    if not first_id:
        continue

    book_num = int(first_id.split('.')[0])
    if book_num not in [4, 5, 6]:
        continue

    for p in passages:
        if 'greek' not in p or 'long' not in p:
            continue

        passage_id = p['id']
        greek = p['greek']
        long_text = ' '.join(p['long']) if isinstance(p['long'], list) else p['long']

        greek_sents = split_greek_sentences(greek)
        english_sents = split_english_sentences(long_text)

        # Only keep passages with 2+ sentences on both sides
        if len(greek_sents) > 1 and len(english_sents) > 1:
            passages_to_process.append({
                'id': passage_id,
                'greek_sents': greek_sents,
                'english_sents': english_sents
            })

print(f"Found {len(passages_to_process)} passages in Books 4-6 needing alignment\n")

# Show first 10 for manual inspection
for i, passage in enumerate(passages_to_process[:10]):
    print(f"{passage['id']}: {len(passage['greek_sents'])} Greek, {len(passage['english_sents'])} English")
    print("GREEK:")
    for j, s in enumerate(passage['greek_sents']):
        print(f"  [{j}] {s}")
    print("ENGLISH:")
    for j, s in enumerate(passage['english_sents']):
        print(f"  [{j}] {s}")
    print()

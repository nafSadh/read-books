#!/usr/bin/env python3
"""Persian → Latin phonetic transliteration (UniPers-lite).

Best-effort — Persian text usually omits short vowels, so the output mirrors
that. Where the source preserves harakat (fatha/kasra/damma) the vowels come
through; where it doesn't, consonants-only is intentional. Not DIN 31635
strict (no ḥ/ẓ/ṯ diacritics); the goal is readability.

Callable as a module (`from transliterate import transliterate`) or as a CLI
filter (`echo "..." | python3 transliterate.py`).
"""
import re
import sys

# ─────────────────────────────────────────────────────────────────────
# Consonant / vowel letter map.
# Persian-digit, alef variants, tied hamza forms all handled.

_CONS = {
    'ا': 'a',   'آ': 'ā',   'أ': 'a',   'إ': 'e',   'ؤ': 'o',   'ئ': 'i',
    'ب': 'b',   'پ': 'p',   'ت': 't',   'ث': 's',
    'ج': 'j',   'چ': 'ch',  'ح': 'h',   'خ': 'kh',
    'د': 'd',   'ذ': 'z',   'ر': 'r',   'ز': 'z',   'ژ': 'zh',
    'س': 's',   'ش': 'sh',  'ص': 's',   'ض': 'z',   'ط': 't',   'ظ': 'z',
    'ع': "'",   'غ': 'gh',  'ف': 'f',   'ق': 'q',
    'ک': 'k',   'گ': 'g',   'ل': 'l',   'م': 'm',   'ن': 'n',
    'و': 'v',   'ه': 'h',   'ی': 'y',
    'ء': "'",
}

# Harakat (short vowels / markers). When present they OVERRIDE the default
# consonant-only behaviour and insert a vowel after the preceding consonant.
_HARAKAT = {
    '\u064e': 'a',   # fatha
    '\u0650': 'e',   # kasra
    '\u064f': 'o',   # damma
    '\u064b': 'an',  # tanwin fath
    '\u064c': 'on',  # tanwin damm
    '\u064d': 'en',  # tanwin kasr
    '\u0652': '',    # sukun (silence — no vowel)
}

# Special markers
_SHADDA = '\u0651'   # doubles previous consonant
_ZWNJ = '\u200c'     # zero-width non-joiner (compound word break)

# Normalize Arabic-form letters and Persian digits
_NORM = str.maketrans({
    'ي': 'ی', 'ك': 'ک', 'ة': 'ه',
    '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
    '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
})


def _transliterate_word(word):
    out = []
    prev_cons = ''
    for ch in word:
        if ch == _SHADDA:
            # double previous consonant letter group
            if prev_cons:
                out.append(prev_cons)
            continue
        if ch == _ZWNJ:
            out.append('-')
            prev_cons = ''
            continue
        if ch in _HARAKAT:
            v = _HARAKAT[ch]
            if v:
                out.append(v)
            continue
        if ch in _CONS:
            mapped = _CONS[ch]
            out.append(mapped)
            prev_cons = mapped
            continue
        # Fallthrough: punctuation, whitespace, unknown — pass through
        out.append(ch)
        prev_cons = ''
    return ''.join(out)


def transliterate(text):
    """Transliterate Persian text to Latin phonetic."""
    text = text.translate(_NORM)
    # Split on whitespace so word-level logic is localized; preserve spacing.
    parts = re.split(r'(\s+)', text)
    return ''.join(_transliterate_word(p) if not p.isspace() else p for p in parts)


if __name__ == '__main__':
    src = sys.stdin.read() if not sys.stdin.isatty() else ' '.join(sys.argv[1:])
    print(transliterate(src))

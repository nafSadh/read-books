#!/usr/bin/env python3
"""
Assemble reader.html from aurelius-meditations.json + annotation data.

Reads the canonical JSON (Greek + Long + annotations) and the CSS/JS
template from reader-casaubon.html to produce a new reader.html with
Long translation, Leopold numbering, and Greek text toggle.

Usage:
  python3 assemble-reader.py              # build reader.html
  python3 assemble-reader.py --dry-run    # preview without writing
"""

import html
import json
import os
import re
import sys
import unicodedata

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
JSON_PATH = os.path.join(PROJECT_DIR, 'aurelius-meditations.json')
TEMPLATE_PATH = os.path.join(PROJECT_DIR, 'reader-casaubon.html')
OUTPUT_PATH = os.path.join(PROJECT_DIR, 'reader.html')

DRY_RUN = '--dry-run' in sys.argv

# Book subtitles (only I-III have them in the traditional editions)
BOOK_SUBTITLES = {
    1: 'Debts and Lessons',
    2: 'Written Among the Quadi',
    3: 'In Carnuntum',
}

# Detail button SVG (reused for every passage)
DETAIL_BTN_SVG = (
    '<button class="med-detail-btn" aria-label="Details">'
    '<svg width="14" height="14" viewBox="0 0 12 12" fill="none" '
    'stroke="currentColor" stroke-width="1.2" stroke-linecap="round" '
    'stroke-linejoin="round"><rect x="1" y="1" width="10" height="10" '
    'rx="1.5"/><line x1="3.5" y1="4" x2="8.5" y2="4"/>'
    '<line x1="3.5" y1="6" x2="8.5" y2="6"/>'
    '<line x1="3.5" y1="8" x2="6.5" y2="8"/></svg></button>'
)


def escape(text):
    """HTML-escape text."""
    return html.escape(text, quote=False)


def inject_proper_nouns(text, proper_nouns, context_filter='in_original'):
    """Wrap first occurrence of each proper noun in a tooltip span."""
    if not proper_nouns:
        return text
    for pn in proper_nouns:
        if pn.get('context') != context_filter:
            continue
        name = pn['name']
        tip_text = escape(pn.get('tip', ''))
        url = pn.get('url', '')
        if url:
            tip_text += f' <a href="{escape(url)}">Wikipedia</a>'
        # Wrap first occurrence only
        pattern = re.compile(re.escape(name), re.IGNORECASE)
        match = pattern.search(text)
        if match:
            replacement = (
                f'<span class="pn">{match.group()}'
                f'<span class="pn-tip">{tip_text}</span></span>'
            )
            text = text[:match.start()] + replacement + text[match.end():]
    return text


# Greek-to-Latin transliteration (base characters only)
_GREEK_MAP = {
    'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z',
    'η': 'ē', 'θ': 'th', 'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm',
    'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p', 'ρ': 'r', 'σ': 's',
    'ς': 's', 'τ': 't', 'υ': 'y', 'φ': 'ph', 'χ': 'ch', 'ψ': 'ps',
    'ω': 'ō',
}


def transliterate_word(word):
    """Transliterate a Greek word to Latin characters."""
    result = []
    decomposed = unicodedata.normalize('NFD', word)
    for ch in decomposed:
        if unicodedata.category(ch).startswith('M'):
            continue  # skip combining marks (accents, breathings)
        low = ch.lower()
        if low in _GREEK_MAP:
            t = _GREEK_MAP[low]
            result.append(t.capitalize() if ch.isupper() else t)
        else:
            result.append(ch)
    return ''.join(result)


def wrap_greek_words(greek_text):
    """Wrap each Greek word in a span with transliteration tooltip."""
    parts = re.split(r'(\s+)', greek_text)
    out = []
    for part in parts:
        if not part.strip():
            out.append(part)
            continue
        # Separate leading/trailing punctuation
        m = re.match(r'^([^\w]*)([\w]+)([^\w]*)$', part, re.UNICODE)
        if m:
            pre, word, post = m.groups()
            translit = transliterate_word(word)
            out.append(
                f'{escape(pre)}<span class="gw" data-t="{escape(translit)}">'
                f'{escape(word)}</span>{escape(post)}'
            )
        else:
            out.append(escape(part))
    return ''.join(out)


def segment_sentences(text, greek=False):
    """Split text into sentences by terminal punctuation."""
    if greek:
        # Greek: . is period, ; is question mark (don't split on · middle dot)
        parts = re.split(r'(?<=[.;])\s+', text.strip())
    else:
        # English: . ? ! end sentences (don't split on ; which is not a sentence break)
        parts = re.split(r'(?<=[.?!])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def align_sentence_groups(n_greek, n_eng):
    """Map sentence indices to shared group IDs for cross-highlighting.

    Uses proportional mapping so mismatched counts still align.
    Returns (greek_groups, eng_groups) — lists of group IDs per sentence.
    """
    k = min(n_greek, n_eng)
    g_groups = [min(i * k // n_greek, k - 1) for i in range(n_greek)]
    e_groups = [min(j * k // n_eng, k - 1) for j in range(n_eng)]
    return g_groups, e_groups


def wrap_sentences(text_html, sentences_raw, prefix, groups):
    """Wrap sentence boundaries in the HTML text with span tags.

    Each sentence gets data-s="PREFIX-GROUP_ID" for cross-highlighting.
    """
    result = text_html
    for i, sent in enumerate(sentences_raw):
        esc = escape(sent)
        idx = result.find(esc)
        if idx >= 0:
            gid = groups[i]
            wrapped = f'<span class="s" data-s="{prefix}-{gid}">{esc}</span>'
            result = result[:idx] + wrapped + result[idx + len(esc):]
    return result


def build_passage_html(passage, annotation=None):
    """Build HTML for a single passage."""
    pid = passage['id']
    book_num, passage_num = pid.split('.')

    # Long text (join array parts)
    long_texts = passage.get('long', [])
    long_text = ' '.join(long_texts) if long_texts else ''

    # Greek text
    greek_text = passage.get('greek', '')

    # Passage number display
    num_display = f'{passage_num}.'

    # Sentence cross-highlighting: segment both texts, proportional grouping
    greek_sents = segment_sentences(greek_text, greek=True) if greek_text else []
    eng_sents = segment_sentences(long_text, greek=False) if long_text else []
    can_highlight = len(greek_sents) > 1 and len(eng_sents) > 1
    if can_highlight:
        g_groups, e_groups = align_sentence_groups(len(greek_sents), len(eng_sents))

    # Build main text: escape → sentence wrap → proper noun inject
    main_text = escape(long_text)
    if can_highlight:
        main_text = wrap_sentences(main_text, eng_sents, pid, e_groups)
    if annotation and annotation.get('proper_nouns'):
        main_text = inject_proper_nouns(main_text, annotation['proper_nouns'], 'in_original')

    # Build detail panel — Notes first, then Modern English
    detail_html = ''
    if annotation:
        modern = annotation.get('modern_english', '')
        notes = annotation.get('notes', '')
        if modern or notes:
            detail_parts = []
            if notes:
                notes_html = escape(notes)
                if annotation.get('proper_nouns'):
                    notes_html = inject_proper_nouns(
                        notes_html, annotation['proper_nouns'], 'in_notes')
                detail_parts.append(
                    f'<div class="narr-section"><span class="narr-label">Notes</span>\n'
                    f'      <p>{notes_html}</p></div>'
                )
            if modern:
                detail_parts.append(
                    f'<div class="narr-section"><span class="narr-label">Modern English</span>\n'
                    f'      <p>{escape(modern)}</p></div>'
                )
            detail_html = '\n      '.join(detail_parts)

    # Greek div with word transliteration tooltips + sentence spans
    if greek_text:
        greek_inner = wrap_greek_words(greek_text)
        if can_highlight:
            for i, sent in enumerate(greek_sents):
                esc_sent = wrap_greek_words(sent)
                idx = greek_inner.find(esc_sent)
                if idx >= 0:
                    gid = g_groups[i]
                    wrapped = f'<span class="s" data-s="{pid}-{gid}">{esc_sent}</span>'
                    greek_inner = greek_inner[:idx] + wrapped + greek_inner[idx + len(esc_sent):]
        greek_html = f'<div class="med-greek">{greek_inner}</div>'
    else:
        greek_html = ''


    lines = []
    lines.append('    <div class="med-passage">')
    lines.append(f'    <div class="med-head">{DETAIL_BTN_SVG}<span class="med-num">{num_display}</span></div>')
    lines.append(f'    <div class="med-body"><div class="med-main">')
    lines.append(f'    <p>{main_text}</p>')
    lines.append(f'    </div>{greek_html}')
    if detail_html:
        lines.append(f'    <div class="med-detail">')
        lines.append(f'      {detail_html}')
        lines.append(f'    </div>')
    lines.append('    </div>')
    lines.append('    </div>')
    return '\n'.join(lines)


def build_chapter_html(book_data, annotations_by_id):
    """Build HTML for one book/chapter."""
    book_num = book_data['book']
    subtitle = BOOK_SUBTITLES.get(book_num, '')
    chapter_idx = book_num - 1

    lines = []
    lines.append(f'<!-- ===== BOOK {book_num} ===== -->')
    lines.append(f'<section class="chapter" id="ch-{book_num}" data-chapter-index="{chapter_idx}">')
    lines.append(f'  <div class="chapter-divider">')
    lines.append(f'    <div class="ch-num">Book {book_num}</div>')
    lines.append(f'    <div class="ch-title">{subtitle}</div>')
    lines.append(f'    <div class="ch-rule"></div>')
    lines.append(f'  </div>')
    lines.append(f'  <div class="chapter-text">')

    for passage in book_data['passages']:
        annotation = annotations_by_id.get(passage['id'])
        lines.append(build_passage_html(passage, annotation))
        lines.append('')

    lines.append(f'  </div>')
    lines.append(f'</section>')
    return '\n'.join(lines)


GREEK_CSS = """
/* ===== GREEK TEXT TOGGLE ===== */
.med-greek {
  display: none;
  flex: 0 0 40%;
  max-width: 40%;
  order: -1;
  padding: 0 0 0 20px;
  border-left: 2px solid var(--border);
  font-family: 'EB Garamond', Georgia, serif;
  font-size: 0.88em;
  line-height: 1.75;
  color: var(--text-secondary);
  align-self: flex-start;
  direction: ltr;
}
[data-greek="on"] .med-greek { display: block; }
[data-greek="on"] .med-passage .med-body .med-main { flex: 1 1 60%; }
/* When both detail and Greek are open — stack Greek below English */
[data-greek="on"] .med-passage.details-open .med-body {
  display: grid;
  grid-template-columns: minmax(0, 45%) minmax(0, 1fr);
  grid-template-rows: auto auto;
  gap: 0 28px;
}
[data-greek="on"] .med-passage.details-open .med-detail {
  grid-column: 1; grid-row: 1 / -1;
  flex: unset; max-width: unset; order: unset;
}
[data-greek="on"] .med-passage.details-open .med-body .med-main {
  grid-column: 2; grid-row: 1; flex: unset;
}
[data-greek="on"] .med-passage.details-open .med-greek {
  grid-column: 2; grid-row: 2;
  flex: unset; max-width: unset; order: unset;
  border-left: none; border-top: 1px solid var(--border);
  padding: 12px 0 0 0;
}
#greek-btn { font-family: 'EB Garamond', Georgia, serif; font-size: 14px; letter-spacing: 0.5px; }
#greek-btn.active { color: var(--accent); }

/* ===== WORD TRANSLITERATION TOOLTIPS ===== */
.gw { position: relative; cursor: default; }
.gw::after {
  content: attr(data-t);
  position: absolute; bottom: 100%; left: 50%;
  transform: translateX(-50%) translateY(2px);
  padding: 2px 5px; border-radius: 4px;
  background: var(--bg); border: 1px solid var(--border);
  color: var(--text-secondary);
  font-family: var(--font-sans); font-size: 0.7em; font-style: italic;
  white-space: nowrap; pointer-events: none;
  opacity: 0; transition: opacity 0.25s ease 0.08s, transform 0.25s ease 0.08s;
  z-index: 10;
}
.gw:hover::after {
  opacity: 1; transform: translateX(-50%) translateY(-2px);
  transition: opacity 0.15s ease, transform 0.15s ease;
}

/* ===== SENTENCE CROSS-HIGHLIGHTING ===== */
.s { transition: background-color 0.25s ease; border-radius: 2px; padding: 1px 0; }
.s.s-hl { background-color: var(--btn-bg); }

@media (max-width: 1199px) {
  .med-greek { flex: none; max-width: none; padding: 12px 0 0 0; border-left: none; border-top: 1px solid var(--border); }
  [data-greek="on"] .med-passage .med-body .med-main { flex: none; }
  [data-greek="on"] .med-passage.details-open .med-body { display: flex; }
  [data-greek="on"] .med-passage.details-open .med-detail { flex: none; max-width: none; }
  [data-greek="on"] .med-passage.details-open .med-greek { flex: none; max-width: none; }
}
"""

GREEK_BTN_HTML = (
    '<button class="bar-btn" id="greek-btn" title="Toggle Greek text" '
    'aria-label="Toggle Greek text">Αα</button>'
)

GREEK_JS = """
// ===== GREEK TEXT TOGGLE =====
const greekBtn = document.getElementById('greek-btn');
greekBtn.addEventListener('click', () => {
  const isOn = document.body.dataset.greek === 'on';
  document.body.dataset.greek = isOn ? 'off' : 'on';
  greekBtn.classList.toggle('active', !isOn);
  savePrefs();
});

// ===== SENTENCE CROSS-HIGHLIGHTING =====
document.addEventListener('mouseover', e => {
  const s = e.target.closest('.s');
  if (!s) return;
  const id = s.dataset.s;
  const passage = s.closest('.med-passage');
  if (passage) passage.querySelectorAll('.s[data-s=\"' + id + '\"]').forEach(
    el => el.classList.add('s-hl'));
});
document.addEventListener('mouseout', e => {
  const s = e.target.closest('.s');
  if (!s) return;
  const id = s.dataset.s;
  const passage = s.closest('.med-passage');
  if (passage) passage.querySelectorAll('.s[data-s=\"' + id + '\"]').forEach(
    el => el.classList.remove('s-hl'));
});
"""

GREEK_SAVE_PREF = "greek: document.body.dataset.greek || 'off'"
GREEK_LOAD_PREF = """if (prefs.greek === 'on') {
      document.body.dataset.greek = 'on';
      document.getElementById('greek-btn').classList.add('active');
    }"""


def extract_template(template_html):
    """Extract head (CSS), chrome (top bar, settings), and script from template.

    Returns (head_section, chrome_before_content, footer_after_content, script_section)
    """
    # Split at key markers
    # Head: everything from start to </head>
    head_end = template_html.index('</head>')
    head = template_html[:head_end + len('</head>')]

    # Body open + chrome: from <body> to <!-- Main content -->
    body_start = template_html.index('<body')
    content_marker = '<!-- Main content -->'
    content_start = template_html.index(content_marker)
    chrome = template_html[body_start:content_start]

    # Footer: from back-to-top button area to <script>
    script_start = template_html.index('<script>')
    # Find the back-to-top section
    back_to_top = '<!-- Back to top'
    btt_idx = template_html.index(back_to_top)
    footer = template_html[btt_idx:script_start]

    # Script: from <script> to </html>
    script = template_html[script_start:]

    return head, chrome, footer, script


def load_annotations():
    """Load all Leopold annotation files and return dict keyed by passage ID."""
    annotations = {}
    ann_dir = os.path.join(SCRIPT_DIR, 'annotations')

    # Load leopold-books-*.json files
    for fname in sorted(os.listdir(ann_dir)):
        if fname.startswith('leopold-') and fname.endswith('.json'):
            fpath = os.path.join(ann_dir, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for ann in data:
                annotations[ann['id']] = ann
            print(f'  Loaded {len(data)} annotations from {fname}')

    return annotations


def main():
    if not os.path.exists(JSON_PATH):
        sys.exit(f'JSON not found: {JSON_PATH}\nRun collect_texts.py first.')
    if not os.path.exists(TEMPLATE_PATH):
        sys.exit(f'Template not found: {TEMPLATE_PATH}')

    print('=== Assembling reader.html ===')

    # Load data
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'  Loaded {sum(b["passage_count"] for b in data["books"])} passages')

    # Load annotations
    annotations = load_annotations()
    print(f'  Total annotations: {len(annotations)}')

    # Load template
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    head, chrome, footer, script = extract_template(template)

    # Update head: change title, inject Greek CSS
    head = head.replace(
        'Translated by Meric Casaubon (1634)',
        'Translated by George Long (1862)'
    )
    head = head.replace('</style>', GREEK_CSS + '</style>')

    # Update chrome: change translator line, add Greek toggle button
    chrome = chrome.replace(
        'Translated by Meric Casaubon (1634)',
        'Translated by George Long (1862)'
    )
    # Insert Greek button before the global-details button
    chrome = chrome.replace(
        '<button class="bar-btn" id="global-details-btn"',
        GREEK_BTN_HTML + '\n    <button class="bar-btn" id="global-details-btn"'
    )

    # Update localStorage key back to main reader key
    script = script.replace('meditations-casaubon-prefs', 'meditations-reader-prefs')

    # Inject Greek toggle JS before the closing </script>
    script = script.replace('</script>', GREEK_JS + '</script>')

    # Add Greek pref to save/load
    # Save: add greek to the prefs object
    script = script.replace(
        "width: document.body.dataset.width",
        "width: document.body.dataset.width,\n      " + GREEK_SAVE_PREF
    )
    # Load: add greek restore after width restore
    script = script.replace(
        "if (prefs.width) {",
        GREEK_LOAD_PREF + "\n    if (prefs.width) {"
    )

    # Build content
    content_lines = []
    content_lines.append('<!-- Main content -->')
    content_lines.append('<div id="content">')
    content_lines.append('  <header class="book-header">')
    content_lines.append('    <h1>Meditations</h1>')
    content_lines.append('    <div class="author">Marcus Aurelius</div>')
    content_lines.append('    <div class="translator">Translated by George Long (1862)</div>')
    content_lines.append('  </header>')

    for book in data['books']:
        content_lines.append(build_chapter_html(book, annotations))
        content_lines.append('')

    content_lines.append('')

    content = '\n'.join(content_lines)

    # Assemble final HTML
    final_html = '\n'.join([
        head,
        chrome,
        content,
        '  ' + footer.strip(),
        '</div>',
        '',
        script,
    ])

    if DRY_RUN:
        print(f'\n  [dry-run] Would write {len(final_html)} chars to {OUTPUT_PATH}')
        # Show first passage
        print(f'  First 500 chars of content:')
        idx = final_html.index('med-passage')
        print(final_html[idx:idx+500])
    else:
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write(final_html)
        size_kb = os.path.getsize(OUTPUT_PATH) / 1024
        print(f'\n  Output: {OUTPUT_PATH} ({size_kb:.0f} KB)')

    # Stats
    annotated = sum(1 for b in data['books'] for p in b['passages']
                    if p['id'] in annotations)
    total = sum(b['passage_count'] for b in data['books'])
    print(f'  Passages: {total} total, {annotated} annotated')


if __name__ == '__main__':
    main()

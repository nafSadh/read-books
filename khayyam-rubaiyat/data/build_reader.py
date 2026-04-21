#!/usr/bin/env python3
"""Build reader.html — 5 parallel editions of Khayyam's Rubaiyat.

Design (Meditations-inspired):
- Human-written (historical) translations are the SPINE — always visible.
- LLM-generated content (modern literal / poetic / theme / note) is demoted
  to a per-quatrain detail panel, revealed on click or via a global toggle.
- Persian original is a side column that appears when the Persian toggle is
  on AND a scholar/LLM-identified match exists for the current quatrain.
- Layout: wide screens can show Detail | Main | Persian as three columns;
  narrow screens stack.

Editions emitted: first / fifth / whinfield / nicolas / persian.
Persian's "detail" panel holds the LLM notes + matched historical alternates.
English editions' detail panel holds: matched Persian, LLM notes from that
Persian match, alternate historical translations, and (for FG 5th)
Heron-Allen 1898's scholarly Persian-source analysis.
"""
import json
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from transliterate import transliterate  # noqa: E402

ROOT = Path(__file__).parent.parent
SEEDS = ROOT / "seeds"
FG_SEED = SEEDS / "fitzgerald.json"
FA_SEED = SEEDS / "persian.json"
WH_SEED = SEEDS / "whinfield.json"
NI_SEED = SEEDS / "nicolas-english.json"
HA_SEED = SEEDS / "heron-allen.json"

TPL = Path(__file__).parent / "reader-template.html"
OUT = ROOT / "reader.html"

GROUP_SIZE = 10

_FA_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')

def to_fa_digits(n):
    return str(n).translate(_FA_DIGITS)


_R = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'),
      (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'),
      (5, 'V'), (4, 'IV'), (1, 'I')]


def romanize(n):
    out = []
    for v, s in _R:
        while n >= v:
            out.append(s)
            n -= v
    return ''.join(out)


# ═══════════════════════════════════════════════════════════════════════
# Detail-panel fragments. These build re-usable chunks of HTML that go
# inside <aside class="q-detail">...</aside>. Each fragment is independently
# optional; the aside is only emitted when at least one has content.

def frag_persian_source(persian_q):
    """Persian text + transliteration, labeled as the source quatrain."""
    if not persian_q:
        return ''
    fa_num = to_fa_digits(persian_q['num'])
    rows = []
    for line in persian_q['lines']:
        t = transliterate(line)
        rows.append(
            f'<p class="qd-fa-line"><span class="qd-fa" dir="rtl" lang="fa">{escape(line)}</span>'
            f'<span class="qd-translit" dir="ltr" lang="en-fa-Latn">{escape(t)}</span></p>'
        )
    return (
        '<section class="qd-section qd-persian-source">'
        f'<h4 class="qd-label">Persian source <span class="qd-ref">Foroughi &amp; Ghani &middot; {fa_num}</span></h4>'
        f'<div class="qd-fa-block">{"".join(rows)}</div>'
        '</section>'
    )


def frag_modern_translations(persian_q):
    """LLM-generated modern literal + poetic, plus theme + note."""
    if not persian_q:
        return ''
    out = []
    if persian_q.get('poetic'):
        body = ''.join(f'<p>{escape(l)}</p>' for l in persian_q['poetic'])
        out.append(
            '<div class="qd-tx qd-tx-poetic">'
            '<div class="qd-tx-label">Modern &middot; Poetic</div>'
            f'{body}</div>'
        )
    if persian_q.get('literal'):
        body = ''.join(f'<p>{escape(l)}</p>' for l in persian_q['literal'])
        out.append(
            '<div class="qd-tx qd-tx-literal">'
            '<div class="qd-tx-label">Modern &middot; Literal</div>'
            f'{body}</div>'
        )
    meta = []
    if persian_q.get('theme'):
        meta.append(f'<span class="qd-theme">{escape(persian_q["theme"])}</span>')
    if persian_q.get('note'):
        meta.append(f'<span class="qd-note">{escape(persian_q["note"])}</span>')
    if meta:
        out.append(f'<div class="qd-meta">{"".join(meta)}</div>')
    if not out:
        return ''
    return (
        '<section class="qd-section qd-modern">'
        '<h4 class="qd-label">Modern rendering <span class="qd-ref">ai-generated</span></h4>'
        + ''.join(out) +
        '</section>'
    )


def frag_historical_alternates(persian_q, skip_ed, fg_lookup, wh_lookup):
    """Other historical human translations matched to this quatrain's Persian
    source (excluding `skip_ed`, the current spine)."""
    if not persian_q:
        return ''
    items = []
    for ed_key, label, ref_key, lookup in [
        ('first',     'FitzGerald &middot; 1st',  'fg_1st',    fg_lookup.get('first')),
        ('fifth',     'FitzGerald &middot; 5th',  'fg_5th',    fg_lookup.get('fifth')),
        ('whinfield', 'Whinfield &middot; 1883',  'whinfield', wh_lookup),
    ]:
        if ed_key == skip_ed:
            continue
        ref = persian_q.get(ref_key)
        if not ref or not ref.get('num') or not lookup:
            continue
        target = lookup.get(ref['num'])
        if not target:
            continue
        lines = target['lines'] if isinstance(target, dict) else target
        strength = ref.get('strength') or ''
        strength_html = f'<span class="qd-strength">{escape(strength)}</span>' if strength else ''
        body = ''.join(f'<p>{escape(l)}</p>' for l in lines)
        items.append(
            f'<div class="qd-alt qd-alt-{ed_key}">'
            f'<div class="qd-alt-label">{label} &middot; {escape(str(ref["num"]))} {strength_html}</div>'
            f'{body}</div>'
        )
    if not items:
        return ''
    return (
        '<section class="qd-section qd-alts">'
        '<h4 class="qd-label">Other historical translations</h4>'
        + ''.join(items) +
        '</section>'
    )


def frag_heron_allen(ha_entry):
    """Heron-Allen 1898's scholarly Persian-source analysis for FG 5th."""
    if not ha_entry:
        return ''
    body = []
    if ha_entry.get('source_lines'):
        lines_html = ''.join(f'<p>{escape(l)}</p>' for l in ha_entry['source_lines'])
        body.append(f'<div class="qd-ha-lines">{lines_html}</div>')
    if ha_entry.get('refs'):
        body.append(f'<div class="qd-ha-refs">{escape(ha_entry["refs"])}</div>')
    if ha_entry.get('note'):
        body.append(f'<div class="qd-ha-note">{escape(ha_entry["note"])}</div>')
    if not body:
        return ''
    return (
        '<section class="qd-section qd-ha">'
        '<h4 class="qd-label">Heron-Allen analysis <span class="qd-ref">1898 &middot; scholarly</span></h4>'
        + ''.join(body) +
        '</section>'
    )


def frag_whinfield_refs(wh_q):
    """Whinfield's own MS refs + brief note (shown on Whinfield spine)."""
    if not wh_q:
        return ''
    bits = []
    if wh_q.get('ms_refs'):
        bits.append(f'<span class="qd-ha-refs">{escape(wh_q["ms_refs"])}</span>')
    if wh_q.get('note'):
        bits.append(f'<span class="qd-ha-note">{escape(wh_q["note"])}</span>')
    if not bits:
        return ''
    return (
        '<section class="qd-section qd-wh-self">'
        '<h4 class="qd-label">Manuscript references <span class="qd-ref">Whinfield\'s footnotes</span></h4>'
        f'<div class="qd-wh-bits">{"".join(bits)}</div>'
        '</section>'
    )


def wrap_detail(*fragments):
    """Assemble fragments into an aside.q-detail or return empty string."""
    parts = [f for f in fragments if f]
    if not parts:
        return ''
    return f'<aside class="q-detail">{"".join(parts)}</aside>'


def wrap_persian_side(persian_q):
    """Side-column Persian text (RTL) — shown when data-persian='on'."""
    if not persian_q:
        return ''
    fa_num = to_fa_digits(persian_q['num'])
    rows = []
    for line in persian_q['lines']:
        t = transliterate(line)
        rows.append(f'<p class="qp-line">{escape(line)}</p>')
        rows.append(f'<p class="qp-translit" dir="ltr" lang="en-fa-Latn">{escape(t)}</p>')
    return (
        '<aside class="q-persian" dir="rtl" lang="fa">'
        f'<div class="qp-ref">Foroughi &amp; Ghani &middot; {fa_num}</div>'
        f'<div class="qp-body">{"".join(rows)}</div>'
        '</aside>'
    )


# ═══════════════════════════════════════════════════════════════════════
# Quatrain renderers — per-edition.

def render_fg_quatrain(q, ed_key, persian_match, ctx):
    """FG 1st or 5th: verse main, with detail + persian side."""
    num = q['num']
    roman = romanize(num)
    vparts = []
    for i, line in enumerate(q['lines']):
        cls = ' class="indented"' if i == 2 else ''
        vparts.append(f'<p{cls}>{escape(line)}</p>')
    verse = ''.join(vparts)
    ha_entry = ctx['ha_lookup'].get(num) if ed_key == 'fifth' else None

    detail = wrap_detail(
        frag_persian_source(persian_match),
        frag_heron_allen(ha_entry),
        frag_modern_translations(persian_match),
        frag_historical_alternates(persian_match, ed_key, ctx['fg_lookup'], ctx['wh_lookup']),
    )
    persian_side = wrap_persian_side(persian_match)
    has_detail = bool(detail)
    has_persian = bool(persian_side)
    classes = ['quatrain', 'q-english']
    if has_detail: classes.append('has-detail')
    if has_persian: classes.append('has-persian')

    detail_btn = (
        '<button class="q-detail-btn" aria-label="Show details" title="Show details">&hellip;</button>'
        if has_detail else ''
    )

    return (
        f'<article class="{" ".join(classes)}" id="q-{ed_key}-{num}" data-q="{num}">'
        f'<div class="q-num">{roman}</div>'
        f'<div class="q-flow">'
        f'{detail}'
        f'<div class="q-main">'
        f'<div class="q-verse">{verse}</div>'
        f'{detail_btn}'
        f'</div>'
        f'{persian_side}'
        f'</div>'
        f'</article>'
    )


def render_whinfield_quatrain(q, persian_match, ctx):
    num = q['num']
    verse = ''.join(f'<p>{escape(l)}</p>' for l in q['lines'])
    detail = wrap_detail(
        frag_persian_source(persian_match),
        frag_whinfield_refs(q),
        frag_modern_translations(persian_match),
        frag_historical_alternates(persian_match, 'whinfield', ctx['fg_lookup'], ctx['wh_lookup']),
    )
    persian_side = wrap_persian_side(persian_match)
    classes = ['quatrain', 'q-english', 'q-whinfield']
    if detail: classes.append('has-detail')
    if persian_side: classes.append('has-persian')
    detail_btn = (
        '<button class="q-detail-btn" aria-label="Show details" title="Show details">&hellip;</button>'
        if detail else ''
    )
    return (
        f'<article class="{" ".join(classes)}" id="q-whinfield-{num}" data-q="{num}">'
        f'<div class="q-num">{num}</div>'
        f'<div class="q-flow">'
        f'{detail}'
        f'<div class="q-main">'
        f'<div class="q-verse">{verse}</div>'
        f'{detail_btn}'
        f'</div>'
        f'{persian_side}'
        f'</div>'
        f'</article>'
    )


def render_nicolas_quatrain(q):
    """Nicolas prose — no detail panel (no LLM match key yet)."""
    num = q['num']
    prose = escape(q.get('prose', ''))
    return (
        f'<article class="quatrain q-english q-nicolas" id="q-nicolas-{num}" data-q="{num}">'
        f'<div class="q-num">{num}</div>'
        f'<div class="q-flow">'
        f'<div class="q-main">'
        f'<div class="q-prose"><p>{prose}</p></div>'
        f'</div>'
        f'</div>'
        f'</article>'
    )


def render_fa_quatrain(q, ctx):
    """Persian spine. Persian + translit = main. Detail = LLM notes + matches."""
    num = q['num']
    fa_num = to_fa_digits(num)
    lines_html = []
    for line in q['lines']:
        t = transliterate(line)
        lines_html.append(f'<p>{escape(line)}</p>')
        lines_html.append(f'<p class="translit" dir="ltr" lang="en-fa-Latn">{escape(t)}</p>')
    detail = wrap_detail(
        frag_modern_translations(q),
        frag_historical_alternates(q, None, ctx['fg_lookup'], ctx['wh_lookup']),
    )
    has_detail = bool(detail)
    classes = ['quatrain', 'persian-q']
    if has_detail: classes.append('has-detail')
    detail_btn = (
        '<button class="q-detail-btn" aria-label="Show details" title="Show details">&hellip;</button>'
        if has_detail else ''
    )
    return (
        f'<article class="{" ".join(classes)}" id="q-persian-{num}" data-q="{num}" dir="rtl" lang="fa">'
        f'<div class="q-num">{fa_num}</div>'
        f'<div class="q-flow">'
        f'{detail}'
        f'<div class="q-main">'
        f'<div class="q-verse">{"".join(lines_html)}</div>'
        f'{detail_btn}'
        f'</div>'
        f'</div>'
        f'</article>'
    )


# ═══════════════════════════════════════════════════════════════════════
# Grouping / edition wrappers

def render_group(quatrains, group_idx, ed_key, render_fn):
    first_num = quatrains[0]['num']
    last_num = quatrains[-1]['num']
    if ed_key == 'persian':
        r = to_fa_digits(first_num) + ('–' + to_fa_digits(last_num) if last_num != first_num else '')
        ch_title = f'رباعیات {r}'
    elif ed_key in ('whinfield', 'nicolas'):
        r = f'{first_num}' + (f'–{last_num}' if last_num != first_num else '')
        ch_title = f'Quatrains {r}'
    else:
        r = romanize(first_num) + ('–' + romanize(last_num) if last_num != first_num else '')
        ch_title = f'Quatrains {r}'
    inner = ''.join(render_fn(q) for q in quatrains)
    return (
        f'<section class="chapter" id="chg-{ed_key}-{group_idx+1}" data-chapter-index="{group_idx}">'
        f'<div class="chapter-divider">'
        f'<div class="ch-num">Group {group_idx + 1}</div>'
        f'<div class="ch-title">{ch_title}</div>'
        f'<div class="ch-rule"></div>'
        f'</div>'
        f'<div class="chapter-text">{inner}</div>'
        f'</section>'
    )


def render_edition(quatrains, ed_key, render_fn):
    groups = [quatrains[i:i + GROUP_SIZE] for i in range(0, len(quatrains), GROUP_SIZE)]
    groups_html = ''.join(render_group(g, i, ed_key, render_fn) for i, g in enumerate(groups))
    return f'<section class="edition" data-edition="{ed_key}">{groups_html}</section>'


# ═══════════════════════════════════════════════════════════════════════
# Lookup builders

def build_ctx():
    fg = json.loads(FG_SEED.read_text(encoding='utf-8'))
    ctx = {
        'fg': fg,
        'fg_lookup': {
            'first': {q['num']: q['lines'] for q in fg['editions']['first']['quatrains']},
            'fifth': {q['num']: q['lines'] for q in fg['editions']['fifth']['quatrains']},
        },
    }
    ctx['wh_lookup'] = {}
    if WH_SEED.exists():
        wh = json.loads(WH_SEED.read_text(encoding='utf-8'))
        ctx['wh'] = wh
        ctx['wh_lookup'] = {q['num']: q for q in wh['quatrains']}
    ctx['ni_lookup'] = {}
    if NI_SEED.exists():
        ni = json.loads(NI_SEED.read_text(encoding='utf-8'))
        ctx['ni'] = ni
    ctx['ha_lookup'] = {}
    if HA_SEED.exists():
        ha = json.loads(HA_SEED.read_text(encoding='utf-8'))
        ctx['ha_lookup'] = {e['fg_5th_num']: e for e in ha['entries']}
    ctx['fa'] = None
    ctx['fa_by_num'] = {}
    # reverse lookups: English-N -> Persian quatrain
    ctx['fg1_to_fa'] = {}
    ctx['fg5_to_fa'] = {}
    ctx['wh_to_fa'] = {}
    if FA_SEED.exists():
        fa = json.loads(FA_SEED.read_text(encoding='utf-8'))
        ctx['fa'] = fa
        ctx['fa_by_num'] = {q['num']: q for q in fa['quatrains']}
        for pq in fa['quatrains']:
            for key, lookup in [('fg_1st', ctx['fg1_to_fa']),
                                 ('fg_5th', ctx['fg5_to_fa']),
                                 ('whinfield', ctx['wh_to_fa'])]:
                ref = pq.get(key)
                if not ref or not ref.get('num'):
                    continue
                tn = ref['num']
                # Keep first/strongest
                cur = lookup.get(tn)
                if cur is None:
                    lookup[tn] = pq
                else:
                    if ref.get('strength') == 'strong' and cur.get(key, {}).get('strength') != 'strong':
                        lookup[tn] = pq
    return ctx


# ═══════════════════════════════════════════════════════════════════════
# main

def main():
    ctx = build_ctx()
    pieces = []
    counts = {}

    fg = ctx['fg']

    # FG 1st
    pieces.append(render_edition(
        fg['editions']['first']['quatrains'], 'first',
        lambda q: render_fg_quatrain(q, 'first', ctx['fg1_to_fa'].get(q['num']), ctx),
    ))
    counts['first'] = fg['editions']['first']['count']

    # FG 5th (with Heron-Allen)
    pieces.append(render_edition(
        fg['editions']['fifth']['quatrains'], 'fifth',
        lambda q: render_fg_quatrain(q, 'fifth', ctx['fg5_to_fa'].get(q['num']), ctx),
    ))
    counts['fifth'] = fg['editions']['fifth']['count']

    # Whinfield
    if 'wh' in ctx:
        pieces.append(render_edition(
            ctx['wh']['quatrains'], 'whinfield',
            lambda q: render_whinfield_quatrain(q, ctx['wh_to_fa'].get(q['num']), ctx),
        ))
        counts['whinfield'] = ctx['wh'].get('count', len(ctx['wh']['quatrains']))

    # Nicolas-English (prose)
    if 'ni' in ctx:
        pieces.append(render_edition(
            ctx['ni']['quatrains'], 'nicolas',
            lambda q: render_nicolas_quatrain(q),
        ))
        counts['nicolas'] = ctx['ni'].get('count', len(ctx['ni']['quatrains']))

    # Persian (annotated primary)
    if ctx['fa']:
        pieces.append(render_edition(
            ctx['fa']['quatrains'], 'persian',
            lambda q: render_fa_quatrain(q, ctx),
        ))
        counts['persian'] = ctx['fa'].get('count', len(ctx['fa']['quatrains']))

    content = '\n'.join(pieces)
    tpl = TPL.read_text(encoding='utf-8')
    assert '__CONTENT__' in tpl, 'template missing __CONTENT__ placeholder'
    out_text = tpl.replace('__CONTENT__', content)
    OUT.write_text(out_text, encoding='utf-8')

    total = sum(counts.values())
    summary = ' + '.join(f'{counts[k]}' for k in ['first', 'fifth', 'whinfield', 'nicolas', 'persian'] if k in counts)
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(out_text):,} bytes, {summary} = {total} quatrains")


if __name__ == '__main__':
    main()

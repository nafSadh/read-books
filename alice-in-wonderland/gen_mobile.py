#!/usr/bin/env python3
"""Generate mobile.html — mobile-first reader for Alice in Wonderland.

Reads /tmp/alice_chapters.json and produces alice-in-wonderland/mobile.html
with paginated single-page layout, 3D page-turn animations, and touch swipe
navigation. Uses the zero-flicker flip algorithm from fullbleed.html.
"""

import json
import os


def main():
    src = '/tmp/alice_chapters.json'
    with open(src, encoding='utf-8') as f:
        chapters = json.load(f)

    chapters_js = json.dumps(chapters, ensure_ascii=False)
    html = TEMPLATE.replace('__CHAPTERS_JSON__', chapters_js)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mobile.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'Wrote {out} ({len(html):,} bytes)')


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light-purple">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="theme-color" content="#faf8f3" id="tc">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>Alice in Wonderland &mdash; Mobile</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
<style>
/* ── Themes ─────────────────────────────── */
[data-theme="light-purple"]{
  --bg:#faf8f3;--text:#363b48;--text2:#65707a;--accent:#7c3aed;
  --bar-bg:rgba(250,248,243,.94);--border:rgba(124,58,237,.12);
}
[data-theme="dark-violet"]{
  --bg:#1a1a1a;--text:#dce0ec;--text2:#8490aa;--accent:#9b7aed;
  --bar-bg:rgba(26,26,26,.95);--border:rgba(155,122,237,.15);
}

/* ── Reset ──────────────────────────────── */
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;overflow:hidden;overscroll-behavior:none}
body{
  background:var(--bg);color:var(--text);
  font-family:'EB Garamond',Georgia,serif;font-size:17px;line-height:1.72;
  -webkit-font-smoothing:antialiased;-webkit-tap-highlight-color:transparent;
  transition:background .35s,color .35s;
}

/* ── Running header (top) ────────────────── */
#top-bar{
  position:absolute;top:0;left:0;right:0;
  height:calc(28px + env(safe-area-inset-top,0px));
  padding-top:env(safe-area-inset-top,0px);
  display:flex;align-items:flex-end;justify-content:space-between;
  padding:0 22px 4px;padding-top:env(safe-area-inset-top,0px);
  z-index:5;pointer-events:none;
}
#top-bar span{
  font-size:10px;color:var(--text2);opacity:.6;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  font-family:'EB Garamond',Georgia,serif;
}
#top-left{font-style:italic}
#top-right{text-align:right}

/* ── Page area ──────────────────────────── */
#page-area{
  position:absolute;top:calc(28px + env(safe-area-inset-top,0px));left:0;right:0;
  bottom:calc(36px + env(safe-area-inset-bottom,0px));
  overflow:hidden;perspective:1200px;
}
.page-content{
  position:absolute;inset:0;padding:20px 22px 20px;overflow:hidden;
}

/* ── Content typography ─────────────────── */
#page-area p{margin-bottom:.75em;text-indent:1.5em}
#page-area p:first-child{text-indent:0}
.ch-start+p{text-indent:0}

/* ── Chapter headers ────────────────────── */
.ch-start{text-align:center;padding:18px 0 14px}
.ch-num{
  font-size:10px;letter-spacing:3px;text-transform:uppercase;
  color:var(--text2);margin-bottom:2px;
}
.ch-title{
  font-size:21px;font-weight:500;color:var(--accent);
  font-style:italic;line-height:1.3;
}
.ch-rule{width:36px;height:1px;background:var(--accent);margin:10px auto 0;opacity:.45}

/* ── Title page ─────────────────────────── */
.title-page{
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  height:100%;text-align:center;gap:4px;
}
.tp-author{font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--text2)}
.tp-title{font-size:28px;font-weight:500;color:var(--accent);font-style:italic;line-height:1.35;margin-top:8px}
.tp-rule{width:40px;height:1px;background:var(--accent);opacity:.45;margin:16px 0}
.tp-year{font-size:12px;color:var(--text2)}
.tp-hint{font-size:11px;color:var(--text2);opacity:.55;margin-top:28px;letter-spacing:1px}

/* ── Flip overlay ───────────────────────── */
.flip-overlay{
  position:absolute;top:0;left:0;width:100%;height:100%;
  transform-style:preserve-3d;z-index:20;pointer-events:none;
}
.flip-overlay.forward{transform-origin:left center}
.flip-overlay.backward{transform-origin:right center}

.flip-face{
  position:absolute;inset:0;
  backface-visibility:hidden;-webkit-backface-visibility:hidden;
  overflow:hidden;background:var(--bg);padding:20px 22px 20px;
}
.flip-face.front{z-index:2}
.flip-face.back{transform:rotateY(180deg);z-index:1}

/* Flip shadows */
.forward .front::after,.forward .back::after,
.backward .front::after,.backward .back::after{
  content:'';position:absolute;inset:0;pointer-events:none;
}
.forward .front::after{background:linear-gradient(to left,rgba(0,0,0,.08),transparent 40%)}
.forward .back::after{background:linear-gradient(to right,rgba(0,0,0,.05),transparent 35%)}
.backward .front::after{background:linear-gradient(to right,rgba(0,0,0,.08),transparent 40%)}
.backward .back::after{background:linear-gradient(to left,rgba(0,0,0,.05),transparent 35%)}

/* ── Running footer (bottom) ────────────── */
#bottom-bar{
  position:absolute;bottom:0;left:0;right:0;
  height:calc(36px + env(safe-area-inset-bottom,0px));
  display:flex;align-items:flex-start;justify-content:space-between;
  padding:6px 22px 0;padding-bottom:env(safe-area-inset-bottom,0px);
  z-index:5;
}
#page-num{
  font-size:11px;color:var(--text2);opacity:.7;min-width:40px;
  font-variant-numeric:tabular-nums;
}

/* ── Scrubber ───────────────────────────── */
#scrubber{display:flex;gap:1px;align-items:center}
.scrub-btn{
  width:20px;height:22px;border:none;background:transparent;
  color:var(--text2);opacity:.55;font-family:'EB Garamond',serif;font-size:9px;
  cursor:pointer;border-radius:3px;
  display:flex;align-items:center;justify-content:center;
  transition:color .15s,opacity .15s;padding:0;
  -webkit-tap-highlight-color:transparent;
}
.scrub-btn.active{color:var(--accent);opacity:1;font-weight:700}
.scrub-btn:active{color:var(--accent);opacity:1}

/* ── Theme button ───────────────────────── */
#theme-btn{
  background:none;border:none;color:var(--text2);opacity:.55;font-size:14px;
  cursor:pointer;padding:2px;-webkit-tap-highlight-color:transparent;
  transition:color .35s,opacity .35s;
}

/* ── Hidden measure box ─────────────────── */
#measure-box{
  position:absolute;top:0;left:0;visibility:hidden;pointer-events:none;
  padding:20px 22px 20px;overflow:hidden;
  font-family:'EB Garamond',Georgia,serif;font-size:17px;line-height:1.72;
}
#measure-box p{margin-bottom:.75em;text-indent:1.5em}
#measure-box p:first-child{text-indent:0}
#measure-box .ch-start+p{text-indent:0}
#measure-box .ch-start{text-align:center;padding:18px 0 14px}
#measure-box .ch-num{font-size:10px;letter-spacing:3px;text-transform:uppercase;margin-bottom:2px}
#measure-box .ch-title{font-size:21px;font-weight:500;font-style:italic;line-height:1.3}
#measure-box .ch-rule{width:36px;height:1px;margin:10px auto 0}
</style>
</head>
<body>
<div id="top-bar">
  <span id="top-left">Alice in Wonderland</span>
  <span id="top-right"></span>
</div>

<div id="page-area">
  <div id="page" class="page-content"></div>
</div>

<div id="bottom-bar">
  <span id="page-num"></span>
  <div id="scrubber"></div>
  <button id="theme-btn" aria-label="Toggle theme">&#9789;</button>
</div>

<div id="measure-box"></div>

<script>
/* ═══════════════════════════════════════════
   Chapter data (embedded at build time)
   ═══════════════════════════════════════════ */
var CHAPTERS = __CHAPTERS_JSON__;

/* ═══════════════════════════════════════════
   Constants
   ═══════════════════════════════════════════ */
var FLIP_MS   = 600;
var FLIP_EASE = 'cubic-bezier(.4,0,.2,1)';
var SWIPE_PX  = 50;
var ROMANS    = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII'];

/* ═══════════════════════════════════════════
   State
   ═══════════════════════════════════════════ */
var pages    = [];
var curPage  = 0;
var busy     = false;
var chStarts = {};

/* ═══════════════════════════════════════════
   DOM refs
   ═══════════════════════════════════════════ */
var area    = document.getElementById('page-area');
var pageEl  = document.getElementById('page');
var numEl   = document.getElementById('page-num');
var topRight = document.getElementById('top-right');
var scrubEl = document.getElementById('scrubber');
var mbox    = document.getElementById('measure-box');

/* ═══════════════════════════════════════════
   Pagination — measure paragraphs against
   viewport height to break into pages
   ═══════════════════════════════════════════ */
function paginate() {
  var aH = area.clientHeight;
  var aW = area.clientWidth;
  mbox.style.width = aW + 'px';

  pages = [];
  chStarts = {};

  /* Title page */
  pages.push({
    h: '<div class="title-page">' +
       '<div class="tp-author">Lewis Carroll</div>' +
       '<div class="tp-title">Alice\u2019s Adventures<br>in Wonderland</div>' +
       '<div class="tp-rule"></div>' +
       '<div class="tp-year">1865</div>' +
       '<div class="tp-hint">swipe to begin \u2192</div></div>',
    ch: 0
  });

  for (var c = 0; c < CHAPTERS.length; c++) {
    var ch = CHAPTERS[c];
    var tmp = document.createElement('div');
    tmp.innerHTML = ch.html;
    var blocks = [];
    for (var j = 0; j < tmp.children.length; j++) blocks.push(tmp.children[j]);

    var i = 0, first = true;
    while (i < blocks.length) {
      mbox.innerHTML = '';

      if (first) {
        var hd = document.createElement('div');
        hd.className = 'ch-start';
        hd.innerHTML = '<div class="ch-num">Chapter ' + ROMANS[ch.num - 1] +
          '</div><div class="ch-title">' + ch.title +
          '</div><div class="ch-rule"></div>';
        mbox.appendChild(hd);
      }

      var si = i;
      while (i < blocks.length) {
        var cl = blocks[i].cloneNode(true);
        mbox.appendChild(cl);
        if (mbox.scrollHeight > aH && mbox.children.length > (first ? 2 : 1)) {
          mbox.removeChild(cl);
          break;
        }
        i++;
      }
      if (i === si) i++;

      var pi = pages.length;
      if (first) chStarts[ch.num] = pi;
      pages.push({ h: mbox.innerHTML, ch: ch.num });
      first = false;
    }
  }
  mbox.innerHTML = '';
}

/* ═══════════════════════════════════════════
   Rendering
   ═══════════════════════════════════════════ */
function show(n) {
  if (n < 0 || n >= pages.length) return;
  curPage = n;
  pageEl.innerHTML = pages[n].h;
  ui();
}

function ui() {
  numEl.textContent = (curPage + 1) + '\u2009/\u2009' + pages.length;
  var cc = pages[curPage] ? pages[curPage].ch : 0;
  /* Right side: chapter title (blank on title page) */
  if (cc === 0) {
    topRight.textContent = '';
  } else {
    var ct = '';
    for (var j = 0; j < CHAPTERS.length; j++) {
      if (CHAPTERS[j].num === cc) { ct = CHAPTERS[j].title; break; }
    }
    topRight.textContent = ct;
  }
  for (var i = 0; i < scrubEl.children.length; i++) {
    scrubEl.children[i].classList.toggle('active', +scrubEl.children[i].dataset.ch === cc);
  }
}

/* ═══════════════════════════════════════════
   Zero-flicker page flip
   Overlay shows OLD content → swap underlying
   to NEW (hidden behind overlay) → animate
   overlay away → cleanup with setTimeout
   ═══════════════════════════════════════════ */
function flipFwd() {
  if (busy || curPage >= pages.length - 1) return;
  busy = true;
  doFlip(curPage + 1, 'forward', 'rotateY(-180deg)');
}

function flipBack() {
  if (busy || curPage <= 0) return;
  busy = true;
  doFlip(curPage - 1, 'backward', 'rotateY(180deg)');
}

function doFlip(target, cls, rot) {
  var fromH = pages[curPage].h;
  var toH   = pages[target].h;

  /* 1. Build overlay — front = current, back = target */
  var ov = document.createElement('div');
  ov.className = 'flip-overlay ' + cls;

  var fr = document.createElement('div');
  fr.className = 'flip-face front';
  fr.innerHTML = fromH;

  var bk = document.createElement('div');
  bk.className = 'flip-face back';
  bk.innerHTML = toH;

  ov.appendChild(fr);
  ov.appendChild(bk);
  area.appendChild(ov);

  /* 2. Swap underlying page (hidden behind overlay) */
  pageEl.innerHTML = toH;

  /* 3. Animate overlay away */
  ov.getBoundingClientRect(); /* force reflow */
  ov.style.transition = 'transform ' + FLIP_MS + 'ms ' + FLIP_EASE;
  ov.style.transform  = rot;

  /* 4. Cleanup — setTimeout, never rAF (background tabs) */
  setTimeout(function() {
    curPage = target;
    setTimeout(function() {
      ov.remove();
      ui();
      busy = false;
    }, 20);
  }, FLIP_MS);
}

/* ═══════════════════════════════════════════
   Chapter scrubber
   ═══════════════════════════════════════════ */
function buildScrubber() {
  scrubEl.innerHTML = '';
  for (var i = 0; i < CHAPTERS.length; i++) {
    var b = document.createElement('button');
    b.className = 'scrub-btn';
    b.textContent = ROMANS[i];
    b.dataset.ch = CHAPTERS[i].num;
    b.title = CHAPTERS[i].title;
    (function(n) { b.onclick = function() { goCh(n); }; })(CHAPTERS[i].num);
    scrubEl.appendChild(b);
  }
}

function goCh(n) {
  if (chStarts[n] != null && !busy) show(chStarts[n]);
}

/* ═══════════════════════════════════════════
   Touch — swipe + tap navigation
   ═══════════════════════════════════════════ */
var tx = 0, ty = 0, swiping = false;

area.addEventListener('touchstart', function(e) {
  tx = e.touches[0].clientX;
  ty = e.touches[0].clientY;
  swiping = false;
}, { passive: true });

area.addEventListener('touchmove', function(e) {
  if (busy) return;
  var dx = e.touches[0].clientX - tx;
  var dy = e.touches[0].clientY - ty;
  if (!swiping && Math.abs(dx) > 10 && Math.abs(dx) > Math.abs(dy) * 1.5) {
    swiping = true;
  }
  if (swiping) e.preventDefault();
}, { passive: false });

area.addEventListener('touchend', function(e) {
  var dx = e.changedTouches[0].clientX - tx;
  var dy = e.changedTouches[0].clientY - ty;

  /* Swipe */
  if (Math.abs(dx) > SWIPE_PX && Math.abs(dx) > Math.abs(dy) * 2) {
    dx < 0 ? flipFwd() : flipBack();
    swiping = false;
    return;
  }

  /* Tap — right half = next, left half = prev */
  if (Math.abs(dx) < 10 && Math.abs(dy) < 10 && !busy) {
    var x = e.changedTouches[0].clientX;
    if (x > window.innerWidth * 0.5) flipFwd();
    else flipBack();
  }
  swiping = false;
});

/* ═══════════════════════════════════════════
   Keyboard — arrows + space
   ═══════════════════════════════════════════ */
document.addEventListener('keydown', function(e) {
  if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); flipFwd(); }
  else if (e.key === 'ArrowLeft') { e.preventDefault(); flipBack(); }
});

/* ═══════════════════════════════════════════
   Theme toggle
   ═══════════════════════════════════════════ */
document.getElementById('theme-btn').addEventListener('click', function() {
  var r = document.documentElement;
  var d = r.dataset.theme === 'dark-violet';
  r.dataset.theme = d ? 'light-purple' : 'dark-violet';
  this.innerHTML = d ? '&#9789;' : '&#9728;';
  document.getElementById('tc').content = d ? '#faf8f3' : '#1a1a1a';
});

/* ═══════════════════════════════════════════
   Resize → re-paginate, keep chapter
   ═══════════════════════════════════════════ */
var rT;
window.addEventListener('resize', function() {
  clearTimeout(rT);
  rT = setTimeout(function() {
    var ch = pages[curPage] ? pages[curPage].ch : 1;
    paginate();
    show(chStarts[ch] != null ? chStarts[ch] : 0);
  }, 300);
});

/* ═══════════════════════════════════════════
   Init — wait for font then paginate
   ═══════════════════════════════════════════ */
(function() {
  buildScrubber();
  /* Show loading hint while font loads */
  pageEl.innerHTML = '<div class="title-page"><div class="tp-title" style="opacity:.3">Loading&hellip;</div></div>';

  var go = function() { paginate(); show(0); };
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(go);
  } else {
    setTimeout(go, 300);
  }
})();
</script>
</body>
</html>"""


if __name__ == '__main__':
    main()

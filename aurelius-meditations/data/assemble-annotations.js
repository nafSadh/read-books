#!/usr/bin/env node
/**
 * Assembles JSON annotation files into reader.html
 * Converts plain <p><span class="med-num">X.</span>...</p> passages
 * into annotated <div class="med-passage">...</div> blocks.
 *
 * Usage: node assemble-annotations.js [--dry-run]
 */

const fs = require('fs');
const path = require('path');

const READER = path.join(__dirname, '..', 'reader.html');
const ANNOT_DIR = path.join(__dirname, 'annotations');

const DETAIL_BTN = '<button class="med-detail-btn" aria-label="Details"><svg width="14" height="14" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="1" width="10" height="10" rx="1.5"/><line x1="3.5" y1="4" x2="8.5" y2="4"/><line x1="3.5" y1="6" x2="8.5" y2="6"/><line x1="3.5" y1="8" x2="6.5" y2="8"/></svg></button>';

// Map book numbers to JSON files (skip books already annotated in HTML)
const BOOK_FILES = {
  5: 'book-05.json',
  6: 'book-06.json',
  7: 'book-07.json',
  8: 'book-08.json',
  9: 'book-09.json',
  10: 'book-10.json',
  11: 'book-11.json',
  12: 'book-12.json',
};

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function addProperNounSpans(text, properNouns) {
  if (!properNouns || !properNouns.length) return text;
  // Only add spans for nouns that appear in_original and are found in this text
  const origNouns = properNouns.filter(pn => pn.context === 'in_original');
  for (const pn of origNouns) {
    const name = pn.name;
    // Skip if already wrapped in a pn span
    if (text.includes(`class="pn">${name}`)) continue;
    // Find the name in the text (not inside HTML tags)
    const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(?<!<[^>]*)\\b(${escapedName})\\b(?![^<]*>)`, 'g');
    let replaced = false;
    text = text.replace(regex, (match) => {
      if (replaced) return match; // only replace first occurrence
      replaced = true;
      const tip = pn.tip || '';
      const urlPart = pn.url ? ` <a href="${pn.url}">Wikipedia</a>` : '';
      return `<span class="pn">${match}<span class="pn-tip">${tip}${urlPart}</span></span>`;
    });
  }
  return text;
}

function buildAnnotatedPassage(originalP, annotation) {
  const num = annotation.num;

  // Extract the original paragraph content (everything after the med-num span)
  // The original is: <p><span class="med-num">X.</span>text...</p>
  // We need to extract just the text content (keeping any existing HTML like <em>)
  const medNumPattern = new RegExp(`<span class="med-num">${num.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\.?</span>`);
  let bodyText = originalP.replace(/^\s*<p>/, '').replace(/<\/p>\s*$/, '');
  bodyText = bodyText.replace(medNumPattern, '').trim();

  // Add proper noun spans to original text
  bodyText = addProperNounSpans(bodyText, annotation.proper_nouns);

  // Build notes with proper noun spans
  let notes = annotation.notes || '';
  const noteNouns = (annotation.proper_nouns || []).filter(pn => pn.context === 'in_notes');
  for (const pn of noteNouns) {
    const escapedName = pn.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`\\b(${escapedName})\\b`, 'g');
    let replaced = false;
    notes = notes.replace(regex, (match) => {
      if (replaced) return match;
      replaced = true;
      const tip = pn.tip || '';
      const urlPart = pn.url ? ` <a href="${pn.url}">Wikipedia</a>` : '';
      return `<span class="pn">${match}<span class="pn-tip">${tip}${urlPart}</span></span>`;
    });
  }

  return `    <div class="med-passage">
    <div class="med-head">${DETAIL_BTN}<span class="med-num">${num}.</span></div>
    <div class="med-body"><div class="med-main">
    <p>${bodyText}</p>
    </div><div class="med-detail">
      <div class="narr-section"><span class="narr-label">Modern English</span>
      <p>${annotation.modern_english}</p></div>
      <div class="narr-section"><span class="narr-label">Notes</span>
      <p>${notes}</p></div>
    </div></div>
    </div>`;
}

function main() {
  const dryRun = process.argv.includes('--dry-run');
  let html = fs.readFileSync(READER, 'utf8');
  let totalReplaced = 0;

  for (const [bookNum, jsonFile] of Object.entries(BOOK_FILES)) {
    const jsonPath = path.join(ANNOT_DIR, jsonFile);
    if (!fs.existsSync(jsonPath)) {
      console.log(`  Skipping Book ${bookNum}: ${jsonFile} not found`);
      continue;
    }

    const annotations = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
    let bookReplaced = 0;

    for (const annot of annotations) {
      const num = annot.num;
      // Match the plain paragraph pattern for this passage number
      // Pattern: <p><span class="med-num">NUM.</span>...text...</p>
      const escapedNum = num.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const pattern = new RegExp(
        `([ \\t]*)<p><span class="med-num">${escapedNum}\\.</span>([\\s\\S]*?)</p>`,
        'm'
      );

      const match = html.match(pattern);
      if (!match) {
        // Already annotated or not found
        continue;
      }

      const fullMatch = match[0];
      const replacement = buildAnnotatedPassage(fullMatch, annot);
      html = html.replace(fullMatch, replacement);
      bookReplaced++;
    }

    console.log(`  Book ${bookNum}: ${bookReplaced}/${annotations.length} passages annotated`);
    totalReplaced += bookReplaced;
  }

  console.log(`\nTotal: ${totalReplaced} passages converted`);

  if (dryRun) {
    console.log('(dry run — no file written)');
  } else {
    fs.writeFileSync(READER, html, 'utf8');
    console.log(`Written to ${READER}`);
  }
}

main();

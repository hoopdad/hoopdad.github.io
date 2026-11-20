// Fetch a blog post and drop its body into the open Substack editor.
//
// Run with the browser tool's javascript_exec in a tab holding the draft
// (https://<pub>.substack.com/publish/post/<id>), after clicking once in the
// body so the editor has focus. Replace __POST_URL__ with the post's URL.
//
// Why it works this way: Substack's editor is TipTap/ProseMirror, which
// accepts a synthetic `paste` event carrying a DataTransfer. That matters
// because the clipboard itself is unavailable here — the browser pane refuses
// execCommand('copy') and the async Clipboard API ("Write permission denied"),
// and synthetic Ctrl+C never reaches it. Nothing is typed either: Substack's
// markdown shortcuts only fire on real keystrokes, so typed "## Heading" stays
// literal. GitHub Pages serves CORS-open, so the editor page can fetch the
// article directly and skip the clipboard entirely.
(async () => {
  const POST_URL = '__POST_URL__';
  const SITE = new URL(POST_URL).origin;

  const res = await fetch(POST_URL);
  if (!res.ok) throw new Error('fetch failed: ' + res.status);
  const doc = new DOMParser().parseFromString(await res.text(), 'text/html');

  // .prose is the article body alone. Taking it instead of the whole page
  // leaves the site header, the "ON THIS PAGE" box, the related-posts block
  // and the footer behind, so there is nothing to strip out afterwards.
  const el = doc.querySelector('.prose') || doc.querySelector('article');
  if (!el) throw new Error('no .prose/article element found');

  // relative URLs break once the content lives on substack.com
  el.querySelectorAll('img[src^="/"]').forEach(i =>
    i.setAttribute('src', SITE + i.getAttribute('src')));
  el.querySelectorAll('a[href^="/"]').forEach(a =>
    a.setAttribute('href', SITE + a.getAttribute('href')));
  el.querySelectorAll('a.anchor,.anchor-link,.heading-anchor').forEach(a => a.remove());

  // Substack has no table support: a pasted <table> collapses into one
  // run-on paragraph with every cell jammed together. Each row becomes a
  // bullet instead, first column as the label. Short cells are labelled
  // inline; long ones (sentences) go on their own line unlabelled.
  let tablesConverted = 0;
  el.querySelectorAll('table').forEach(tbl => {
    const head = [...tbl.querySelectorAll('thead th, thead td')].map(c => c.innerText.trim());
    const ul = doc.createElement('ul');
    [...tbl.querySelectorAll('tbody tr')].forEach(row => {
      const cells = [...row.children];
      const li = doc.createElement('li');
      let html = '<strong>' + cells[0].innerHTML + '</strong>';
      const inline = [];
      let block = '';
      cells.slice(1).forEach((c, i) => {
        const text = c.innerText.trim();
        if (!text) return;
        const name = head[i + 1] || '';
        if (text.length > 40) block += '<br>' + c.innerHTML;
        else inline.push((name ? name + ': ' : '') + c.innerHTML);
      });
      if (inline.length) html += ' — ' + inline.join(' · ');
      li.innerHTML = html + block;
      ul.appendChild(li);
    });
    (tbl.closest('.table-scroll') || tbl).replaceWith(ul);
    tablesConverted++;
  });

  // Optional text corrections, applied across text nodes so markup survives.
  // Leave TEXT_FIXES empty to paste the post exactly as published.
  const TEXT_FIXES = [];
  const applied = {};
  if (TEXT_FIXES.length) {
    const walk = doc.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walk.nextNode())) {
      let t = node.nodeValue;
      for (const [pattern, replacement] of TEXT_FIXES) {
        const before = t;
        t = t.replace(pattern, replacement);
        if (t !== before) applied[replacement] = (applied[replacement] || 0) + 1;
      }
      if (t !== node.nodeValue) node.nodeValue = t;
    }
  }

  const html = el.innerHTML;
  const text = el.innerText;

  const target = document.querySelector('.tiptap.ProseMirror');
  if (!target) throw new Error('editor not found - is a draft open?');
  target.focus();
  const dt = new DataTransfer();
  dt.setData('text/html', html);
  dt.setData('text/plain', text);
  target.dispatchEvent(new ClipboardEvent('paste', {
    clipboardData: dt, bubbles: true, cancelable: true,
  }));

  return {
    source: POST_URL,
    pastedChars: html.length,
    tablesConverted,
    tablesLeft: el.querySelectorAll('table').length,
    images: el.querySelectorAll('img').length,
    codeBlocks: el.querySelectorAll('pre').length,
    textFixes: applied,
  };
})();

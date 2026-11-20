// Check what actually landed in the open Substack draft.
//
// Run with the browser tool's javascript_exec in the draft tab after
// paste_post.js. Screenshots of this editor go stale — content can be present
// while the pane still shows "Start writing..." — so trust these counts over
// the picture.
(async () => {
  const ed = document.querySelector('.tiptap.ProseMirror');
  if (!ed) throw new Error('editor not found - is a draft open?');

  const imgs = [...ed.querySelectorAll('img')];
  // Substack rehosts pasted images onto its own CDN; anything still pointing
  // at the blog is a hotlink that breaks if the asset is renamed.
  const hosts = [...new Set(imgs.map(i => {
    try { return new URL(i.src).host; } catch (e) { return 'unparseable'; }
  }))];
  const statuses = await Promise.all(imgs.map(async i => {
    try { return (await fetch(i.src)).status; } catch (e) { return 'ERR'; }
  }));

  const titleEl = document.querySelector('[data-testid="post-title"], .post-title');
  return {
    title: titleEl ? titleEl.innerText.trim() : null,
    words: ed.innerText.trim().split(/\s+/).filter(Boolean).length,
    chars: ed.innerText.trim().length,
    headings: [...ed.querySelectorAll('h1,h2,h3')].map(h => h.tagName + ': ' + h.innerText.slice(0, 60)),
    paragraphs: ed.querySelectorAll('p').length,
    listItems: ed.querySelectorAll('li').length,
    blockquotes: ed.querySelectorAll('blockquote').length,
    codeBlocks: ed.querySelectorAll('pre').length,
    boldRuns: ed.querySelectorAll('strong').length,
    tablesLeft: ed.querySelectorAll('table').length,  // must be 0
    images: imgs.length,
    imageHosts: hosts,
    imageStatuses: statuses,
    brokenImages: statuses.filter(s => s !== 200).length,
    firstWords: ed.innerText.trim().slice(0, 120),
  };
})();

// Collect every Substack post and draft, for gap.py to compare against.
//
// Run with the browser tool's javascript_exec in a tab on the signed-in
// Substack dashboard (https://<pub>.substack.com/publish/posts). Returns
// {published: [...], drafts: [...]} with each row normalised to `title`.
//
// The management API rejects the call without order_by/order_direction — a
// request with only offset and limit comes back 400, which is easy to misread
// as "no access". Both lists page at 25 regardless of the limit asked for.
(async () => {
  async function pull(kind, orderBy) {
    const out = [];
    for (let offset = 0; offset < 1000; offset += 25) {
      const url = `/api/v1/post_management/${kind}` +
        `?offset=${offset}&limit=25&order_by=${orderBy}&order_direction=desc`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`${kind} ${res.status} at offset ${offset}`);
      const body = await res.json();
      const rows = body.posts || body;
      if (!rows.length) break;
      for (const p of rows) {
        out.push({
          id: p.id,
          // drafts keep their heading in draft_title and leave title null
          title: (p.title || p.draft_title || '').trim(),
          date: (p.post_date || p.draft_updated_at || '').slice(0, 10),
          slug: p.slug || null,
        });
      }
      if (rows.length < 25) break;
    }
    return out;
  }

  const published = await pull('published', 'post_date');
  const drafts = await pull('drafts', 'draft_updated_at');
  return {
    collectedAt: new Date().toISOString(),
    publication: location.host,
    published,
    drafts,
    untitledDrafts: drafts.filter(d => !d.title).length,
  };
})();

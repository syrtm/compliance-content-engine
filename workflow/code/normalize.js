// Clean feed items, tag the source, drop old ones, keep newest N per source.
const cfg = $('Config').first().json;
const host = (u) => (String(u).match(/^https?:\/\/([^/?#]+)/i) || [])[1] || '';
const sourceFor = (link) => (cfg.sources.find((s) => host(s.url) === host(link)) || { name: 'Unknown' }).name;
const clean = (t) => String(t || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
const cutoff = Date.now() - cfg.maxAgeDays * 86400000;

const rows = [];
for (const item of $input.all()) {
  const j = item.json;
  const link = clean(j.link);
  if (!link) continue;
  const rawDate = j.isoDate || j.pubDate || j['a10:updated'] || '';
  const ts = Date.parse(rawDate);
  if (!Number.isNaN(ts) && ts < cutoff) continue;
  rows.push({
    source: sourceFor(link),
    title: clean(j.title),
    link,
    summary: clean(j.contentSnippet || j.content || j.summary).slice(0, 2000),
    published: Number.isNaN(ts) ? '' : new Date(ts).toISOString(),
  });
}

const perSource = {};
const out = [];
for (const r of rows.sort((a, b) => (b.published || '').localeCompare(a.published || ''))) {
  perSource[r.source] = (perSource[r.source] || 0) + 1;
  if (perSource[r.source] <= cfg.maxItemsPerSource) out.push({ json: r });
}
return out;

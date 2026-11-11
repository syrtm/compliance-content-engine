// Parse the LLM answer, run deterministic QA checks, shape the row for Google Sheets.
const news = $('Build Prompt').first().json;
const res = $input.first().json;
const seconds = Math.round((Date.now() - news.t0) / 100) / 10;

const pad = (x) => String(x).padStart(2, '0');
const now = new Date();
const date = `${now.getUTCFullYear()}-${pad(now.getUTCMonth() + 1)}-${pad(now.getUTCDate())} ${pad(now.getUTCHours())}:${pad(now.getUTCMinutes())}:${pad(now.getUTCSeconds())}`;
const monday = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() - ((now.getUTCDay() + 6) % 7)));
const weekStart = monday.toISOString().slice(0, 10);

const row = {
  date,
  source: news.source,
  title: news.title,
  link: news.link,
  score: '',
  score_reason: '',
  linkedin_post: '',
  newsletter_blurb: '',
  one_pager_md: '',
  status: 'draft',
  generation_seconds: seconds,
  week_start: weekStart,
  qa_flags: '',
};

let out;
try {
  const text = res.candidates[0].content.parts.map((p) => p.text || '').join('');
  out = JSON.parse(text);
} catch (e) {
  row.status = 'error';
  row.qa_flags = `llm_error: ${String((res.error && (res.error.message || res.error)) || e.message).slice(0, 200)}`;
  return [{ json: row }];
}

const flags = [];
const words = (t) => String(t || '').trim().split(/\s+/).filter(Boolean).length;
const score = Number(out.relevance_score);
if (!Number.isInteger(score) || score < 0 || score > 10) flags.push('score_out_of_range');
if (words(out.linkedin_post) > 120) flags.push(`linkedin_over_120_words(${words(out.linkedin_post)})`);
if (words(out.newsletter_blurb) > 60) flags.push(`newsletter_over_60_words(${words(out.newsletter_blurb)})`);
for (const h of ['## What happened', '## Who is affected', '## 3 actions for compliance teams']) {
  if (!String(out.one_pager_md || '').includes(h)) flags.push(`one_pager_missing_section(${h.slice(3)})`);
}

// Grounding check: every number in the drafts must appear in the source text.
const generated = [out.linkedin_post, out.newsletter_blurb, out.one_pager_md].join('\n');
const numbers = (t) => (String(t).replace(/^\s*\d+[.)]\s/gm, '').match(/\d[\d.,/]*\d|\d/g) || []).map((x) => x.replace(/,/g, ''));
const sourceNumbers = new Set(numbers(`${news.title} ${news.summary} ${news.published}`));
const unknown = [...new Set(numbers(generated))].filter((x) => !sourceNumbers.has(x) && x !== '3');
if (unknown.length) flags.push(`number_not_in_source(${unknown.slice(0, 5).join(' ')})`);
if (/https?:\/\//i.test(generated)) flags.push('model_added_url');

// The source link is appended here, not by the model, so it can never be wrong or missing.
const src = `Source: ${news.link}`;
row.score = Number.isFinite(score) ? score : '';
row.score_reason = String(out.relevance_reason || '');
row.linkedin_post = `${String(out.linkedin_post || '').trim()}\n\n${src}`;
row.newsletter_blurb = `${String(out.newsletter_blurb || '').trim()} ${src}`;
row.one_pager_md = `${String(out.one_pager_md || '').trim()}\n\n---\n${src} (${news.source})`;
row.qa_flags = flags.join('; ');
return [{ json: row }];

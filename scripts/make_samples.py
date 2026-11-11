"""Turn a CSV export of the Review tab into samples/*.md (first 5 rows by default).

In Google Sheets: open the Review tab -> File -> Download -> CSV, then:
    python scripts/make_samples.py path/to/Review.csv [count]
"""
import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) < 2:
    sys.exit(__doc__)
count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
with open(sys.argv[1], encoding="utf-8-sig", newline="") as f:
    rows = [r for r in csv.DictReader(f) if r.get("linkedin_post")][:count]
for i, r in enumerate(rows, 1):
    slug = re.sub(r"[^a-z0-9]+", "-", r["title"].lower()).strip("-")[:50]
    path = ROOT / "samples" / f"{i:02d}-{slug}.md"
    path.write_text(
        f"# Sample {i}: {r['title']}\n\n"
        f"- Source: {r['source']} - {r['link']}\n"
        f"- Processed (UTC): {r['date']}\n"
        f"- Relevance score: {r['score']}/10 - {r['score_reason']}\n"
        f"- Generation time: {r['generation_seconds']} s\n"
        f"- QA flags: {r['qa_flags'] or 'none'}\n\n"
        f"Unedited model output. The source line is appended by the workflow.\n\n"
        f"## LinkedIn post\n\n{r['linkedin_post']}\n\n"
        f"## Newsletter blurb\n\n{r['newsletter_blurb']}\n\n"
        f"## One-pager\n\n{r['one_pager_md']}\n",
        encoding="utf-8",
    )
    print("wrote", path.relative_to(ROOT))
if not rows:
    print("no rows with content found")

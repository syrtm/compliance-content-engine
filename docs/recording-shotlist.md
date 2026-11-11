# Screen recording shot list (target: 45 seconds, no audio needed)

Prep before recording: n8n open on the workflow canvas at 100% zoom, the Google Sheet open in a second tab on `Review`, browser bookmarks bar hidden, no API keys or email addresses visible. Make sure there are unprocessed news items (or clear history: open *Skip Already Processed* -> operation *Clear Deduplication History* -> run once -> switch back).

| # | Seconds | Screen | What to show | Caption (optional) |
|---|---|---|---|---|
| 1 | 0-5 | n8n canvas | Whole workflow, 12 nodes, left to right | "Official sanctions and AML feeds -> reviewed-ready drafts" |
| 2 | 5-15 | n8n canvas | Click **Execute workflow**. Nodes turn green, the loop counts up | "One run: fetch, dedupe, generate, score" |
| 3 | 15-22 | n8n node panel | Open *Parse and Validate* output: `score`, `qa_flags`, `generation_seconds` | "Every draft is checked before a human sees it" |
| 4 | 22-32 | Google Sheet, `Review` | New rows. Click into one `linkedin_post` cell, show the appended `Source:` link | "Score 6+ goes to Review, with the source link" |
| 5 | 32-37 | Google Sheet, `Skipped` | Low-score rows with their reason | "Low relevance is filtered out, not deleted" |
| 6 | 37-42 | Google Sheet, `Review` | Change one `status` from `draft` to `approved` | "A human approves. Nothing is auto-published" |
| 7 | 42-47 | Google Sheet, `Metrics` | Weekly row updating: items, drafts, avg seconds, approval rate | "Measured weekly" |
| 8 | 47-50 | n8n canvas | Click **Execute workflow** again: *Skip Already Processed* outputs 0 new items | "Second run: nothing is processed twice" |

Tools on Windows: Xbox Game Bar (`Win+G`) or ScreenToGif for a GIF. Export under 10 MB so GitHub renders it inline; save as `docs/demo.gif` and it will show at the top of the README.

# Google Sheet template

Create one spreadsheet with three tabs. Set **File -> Settings -> Locale** to *United States* so the formulas below work as written (other locales use `;` instead of `,`).

## Tabs `Review` and `Skipped`

Row 1 (headers, exactly these names, the workflow maps columns by name):

```
date	source	title	link	score	score_reason	linkedin_post	newsletter_blurb	one_pager_md	status	generation_seconds	week_start	qa_flags
```

| Column | Meaning |
|---|---|
| date | Processing time (UTC) |
| score | Relevance 0-10 from the model. `>= 6` goes to `Review`, the rest to `Skipped` |
| status | `draft` on arrival. A human changes it to `approved` or `rejected`. `error` means the LLM call failed |
| generation_seconds | Wall-clock time of the LLM step for this item, including retries |
| week_start | Monday of the processing week, used by `Metrics` |
| qa_flags | Automatic checks: word limits, missing sections, numbers not found in the source |

## Tab `Metrics`

| Cell | Content |
|---|---|
| A2 / B2 | `Write one LinkedIn post by hand (minutes)` / *your measurement* |
| A3 / B3 | `Write one newsletter blurb by hand (minutes)` / *your measurement* |
| A4 / B4 | `Write one one-pager by hand (minutes)` / *your measurement* |
| A5 / B5 | `Manual total per news item (minutes)` / `=IF(COUNT(B2:B4)=3,SUM(B2:B4),"to be measured")` |
| A6 / B6 | `Review and edit one AI draft set (minutes)` / *your measurement* |
| A8:H8 | `week_start, items_processed, sent_to_review, drafts_generated, avg_generation_seconds, approved_items, approval_rate, est_hours_saved` |

Row 9 (copy B9:H9 down as many rows as you want weeks; A9 spills by itself):

```
A9: =IFERROR(SORT(UNIQUE(FILTER(VSTACK(Review!L2:L,Skipped!L2:L),VSTACK(Review!L2:L,Skipped!L2:L)<>"")),1,FALSE),"")
B9: =IF(A9="","",COUNTIF(Review!L:L,A9)+COUNTIF(Skipped!L:L,A9))
C9: =IF(A9="","",COUNTIF(Review!L:L,A9))
D9: =IF(A9="","",3*(COUNTIFS(Review!L:L,A9,Review!J:J,"<>error")+COUNTIFS(Skipped!L:L,A9,Skipped!J:J,"<>error")))
E9: =IF(A9="","",IFERROR(ROUND((SUMIF(Review!L:L,A9,Review!K:K)+SUMIF(Skipped!L:L,A9,Skipped!K:K))/B9,1),""))
F9: =IF(A9="","",COUNTIFS(Review!L:L,A9,Review!J:J,"approved"))
G9: =IF(A9="","",IF(C9=0,"",F9/C9))
H9: =IF(A9="","",IF(AND(ISNUMBER($B$5),ISNUMBER($B$6)),ROUND(F9*($B$5-$B$6)/60,2),"to be measured"))
```

## How "estimated hours saved" is calculated

`approved_items x (manual minutes per item - review minutes per item) / 60`

- Only **approved** items count. A draft nobody used saved nothing.
- Both inputs are stopwatch measurements typed in by a person. Until both exist the cell shows `to be measured`.
- It is an estimate from one person's baseline, not a controlled study.

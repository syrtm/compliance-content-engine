# Samples

5 unedited outputs from the measured run on 2026-11-11 (Groq `openai/gpt-oss-120b`, real items from the UK OFSI, EU Council and US Federal Reserve feeds).

Generated with `python scripts/make_samples.py Review.csv` from the `Review` tab. Chosen to cover all three sources; the other 4 `Review` rows and the 3 `Skipped` rows are in the Google Sheet.

The "Source:" line in each piece is appended by the workflow, not written by the model. Known weaknesses visible in these samples are listed under *Limits* in the main README.

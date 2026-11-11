"""Smoke test: one real Gemini call with the repo's prompt and schema. No n8n needed.

Usage (key is read from .env, never printed):
    python scripts/smoke_test.py            # run one generation
    python scripts/smoke_test.py --models   # list models your key can use
"""
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "gemini-flash-latest"  # keep in sync with workflow/code/config.js

# A real item from the UK OFSI feed (fetched 2026-11-11).
NEWS = {
    "source": "UK OFSI",
    "published": "2026-10-28T11:50:21.000Z",
    "title": "Guidance: OFSI General Licence INT/2025/7895596",
    "summary": "Details for OFSI General Licence INT/2025/7895596, Continuation of Business of Lukoil Bulgaria Entities",
}


def api_key():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("GEMINI_API_KEY=") and line.split("=", 1)[1].strip():
                return line.split("=", 1)[1].strip()
    sys.exit("GEMINI_API_KEY is missing. Copy .env.example to .env and fill it in.")


def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json", "x-goog-api-key": api_key()})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")


if "--models" in sys.argv:
    for m in call(f"{BASE}/models?pageSize=200").get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            print(m["name"].removeprefix("models/"))
    sys.exit()

user_text = "\n".join(["NEWS ITEM", f"Source: {NEWS['source']}", f"Published: {NEWS['published']}",
                       f"Title: {NEWS['title']}", f"Summary: {NEWS['summary']}"])
body = {
    "systemInstruction": {"parts": [{"text": (ROOT / "prompts/system-prompt.md").read_text(encoding="utf-8").strip()}]},
    "contents": [{"role": "user", "parts": [{"text": user_text}]}],
    "generationConfig": {
        "temperature": 0.2,
        "responseMimeType": "application/json",
        "responseSchema": json.loads((ROOT / "prompts/output-schema.json").read_text(encoding="utf-8")),
    },
}
t0 = time.time()
res = call(f"{BASE}/models/{MODEL}:generateContent", body)
out = json.loads(res["candidates"][0]["content"]["parts"][0]["text"])
print(json.dumps(out, indent=2, ensure_ascii=False))
words = lambda t: len(t.split())
print(f"\nseconds={time.time() - t0:.1f}  linkedin_words={words(out['linkedin_post'])} (max 120)  "
      f"newsletter_words={words(out['newsletter_blurb'])} (max 60)  score={out['relevance_score']}")

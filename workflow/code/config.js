// Single place to configure the workflow. No secrets here.
const config = {
  // Google Sheet that receives the output (the long ID from the sheet URL).
  spreadsheetId: 'YOUR_SPREADSHEET_ID',
  // Any OpenAI-compatible chat completions endpoint + model. Change both and the
  // Bearer credential to switch provider. List models: python scripts/smoke_test.py --models
  //   Groq (free tier, used for the samples): https://api.groq.com/openai/v1  + openai/gpt-oss-120b
  //   Google Gemini:  https://generativelanguage.googleapis.com/v1beta/openai + gemini-flash-latest
  llmBaseUrl: 'https://api.groq.com/openai/v1',
  model: 'openai/gpt-oss-120b',
  // Pause before each LLM call. Groq free tier allows 8,000 tokens/min and one item uses ~1,800.
  pauseSeconds: 15,
  // Items older than this are ignored (keeps the first run small).
  maxAgeDays: 30,
  // Newest N items per source per run (protects free-tier rate limits).
  maxItemsPerSource: 6,
  // Public feeds, verified live on 2026-11-11.
  sources: [
    {
      name: 'UK OFSI',
      url: 'https://www.gov.uk/government/organisations/office-of-financial-sanctions-implementation.atom',
    },
    {
      name: 'EU Council',
      url: 'https://www.consilium.europa.eu/en/rss/pressreleases.ashx',
    },
    {
      name: 'US Federal Reserve Enforcement',
      url: 'https://www.federalreserve.gov/feeds/press_enforcement.xml',
    },
  ],
};

// One item per feed, so a single RSS Read node fetches them all.
// Every item also carries the full config for later nodes: $('Config').first().json
return config.sources.map((s) => ({ json: { ...config, name: s.name, url: s.url } }));

// Single place to configure the workflow. No secrets here.
const config = {
  // Google Sheet that receives the output (the long ID from the sheet URL).
  spreadsheetId: 'YOUR_SPREADSHEET_ID',
  // Any OpenAI-compatible chat completions endpoint. Default: Google Gemini.
  // To switch provider, change baseUrl + model and the Bearer credential.
  llmBaseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai',
  // List the models your key can use: python scripts/smoke_test.py --models
  model: 'gemini-flash-latest',
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

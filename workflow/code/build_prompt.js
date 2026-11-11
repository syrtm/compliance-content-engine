// Runs once per loop iteration (batch size 1). Starts the timer and builds the LLM request.
const SYSTEM_PROMPT = __SYSTEM_PROMPT__;
const OUTPUT_SCHEMA = __OUTPUT_SCHEMA__;

const n = $input.first().json;
const userText = [
  'NEWS ITEM',
  `Source: ${n.source}`,
  `Published: ${n.published || 'not stated'}`,
  `Title: ${n.title}`,
  `Summary: ${n.summary || '(no summary provided)'}`,
].join('\n');

return [
  {
    json: {
      ...n,
      t0: Date.now(),
      body: {
        model: $('Config').first().json.model,
        temperature: 0.2,
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: userText },
        ],
        response_format: {
          type: 'json_schema',
          json_schema: { name: 'content_drafts', strict: true, schema: OUTPUT_SCHEMA },
        },
      },
    },
  },
];

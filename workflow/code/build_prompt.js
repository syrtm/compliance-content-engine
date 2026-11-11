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
        systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
        contents: [{ role: 'user', parts: [{ text: userText }] }],
        generationConfig: {
          temperature: 0.2,
          responseMimeType: 'application/json',
          responseSchema: OUTPUT_SCHEMA,
        },
      },
    },
  },
];

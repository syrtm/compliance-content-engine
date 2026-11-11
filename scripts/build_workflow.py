"""Rebuild workflow/compliance-content-engine.json from prompts/ and workflow/code/.

Usage: python scripts/build_workflow.py
Keeps the prompt and schema files as the single source of truth.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
read = lambda p: (ROOT / p).read_text(encoding="utf-8")
code = lambda name: read(f"workflow/code/{name}.js")

build_prompt = (
    code("build_prompt")
    .replace("__SYSTEM_PROMPT__", json.dumps(read("prompts/system-prompt.md").strip()))
    .replace("__OUTPUT_SCHEMA__", json.dumps(json.loads(read("prompts/output-schema.json"))))
)


def node(name, type_, version, pos, params, **extra):
    return {"parameters": params, "name": name, "type": type_, "typeVersion": version,
            "position": pos, "id": name.lower().replace(" ", "-").replace("≥", "gte"), **extra}


def code_node(name, pos, js):
    return node(name, "n8n-nodes-base.code", 2, pos, {"jsCode": js})


def sheet_node(name, tab, pos):
    return node(name, "n8n-nodes-base.googleSheets", 4.7, pos, {
        "operation": "append",
        "documentId": {"__rl": True, "mode": "id", "value": "={{ $('Config').first().json.spreadsheetId }}"},
        "sheetName": {"__rl": True, "mode": "name", "value": tab},
        "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": [], "schema": []},
        "options": {},
    })


nodes = [
    node("Daily Trigger", "n8n-nodes-base.scheduleTrigger", 1.3, [0, 0],
         {"rule": {"interval": [{"field": "days", "daysInterval": 1, "triggerAtHour": 7}]}}),
    code_node("Config", [220, 0], code("config")),
    node("Read Feeds", "n8n-nodes-base.rssFeedRead", 1.2, [660, 0],
         {"url": "={{ $json.url }}", "options": {"customFields": "a10:updated"}},
         retryOnFail=True, maxTries=3, waitBetweenTries=3000, onError="continueRegularOutput"),
    code_node("Normalize", [880, 0], code("normalize")),
    node("Skip Already Processed", "n8n-nodes-base.removeDuplicates", 2, [1100, 0], {
        "operation": "removeItemsSeenInPreviousExecutions",
        "logic": "removeItemsWithAlreadySeenKeyValues",
        "dedupeValue": "={{ $json.link }}",
        "options": {},
    }),
    node("Loop Over News", "n8n-nodes-base.splitInBatches", 3, [1320, 0], {"batchSize": 1, "options": {}}),
    code_node("Build Prompt", [1540, 100], build_prompt),
    node("Generate Content (LLM)", "n8n-nodes-base.httpRequest", 4.5, [1760, 100], {
        "method": "POST",
        "url": "=https://generativelanguage.googleapis.com/v1beta/models/{{ $('Config').first().json.model }}:generateContent",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "googlePalmApi",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json.body) }}",
        "options": {"timeout": 60000},
    }, retryOnFail=True, maxTries=3, waitBetweenTries=5000, onError="continueRegularOutput"),
    code_node("Parse and Validate", [1980, 100], code("parse_validate")),
    node("Score ≥ 6", "n8n-nodes-base.if", 2.3, [2200, 100], {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 3},
            "conditions": [{"id": "score-gte-6", "leftValue": "={{ $json.score }}", "rightValue": 6,
                            "operator": {"type": "number", "operation": "gte"}}],
            "combinator": "and",
        },
        "looseTypeValidation": True,
        "options": {},
    }),
    sheet_node("Append to Review", "Review", [2420, 0]),
    sheet_node("Append to Skipped", "Skipped", [2420, 200]),
]

link = lambda *targets: [{"node": t, "type": "main", "index": 0} for t in targets]
connections = {
    "Daily Trigger": {"main": [link("Config")]},
    "Config": {"main": [link("Read Feeds")]},
    "Read Feeds": {"main": [link("Normalize")]},
    "Normalize": {"main": [link("Skip Already Processed")]},
    "Skip Already Processed": {"main": [link("Loop Over News")]},
    "Loop Over News": {"main": [[], link("Build Prompt")]},
    "Build Prompt": {"main": [link("Generate Content (LLM)")]},
    "Generate Content (LLM)": {"main": [link("Parse and Validate")]},
    "Parse and Validate": {"main": [link("Score ≥ 6")]},
    "Score ≥ 6": {"main": [link("Append to Review"), link("Append to Skipped")]},
    "Append to Review": {"main": [link("Loop Over News")]},
    "Append to Skipped": {"main": [link("Loop Over News")]},
}

workflow = {"name": "Compliance Content Engine", "nodes": nodes, "connections": connections,
            "active": False, "settings": {"executionOrder": "v1"}, "pinData": {}}
out = ROOT / "workflow/compliance-content-engine.json"
out.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)} with {len(nodes)} nodes")

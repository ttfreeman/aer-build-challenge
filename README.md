# AER Triage Agent

A synthetic Alberta Energy Regulator intake-triage exercise. The agent reads public intake records, sanitizes reporter text, retrieves relevant regulatory directives from a local ChromaDB collection, uses Gemini for structured extraction, and applies deterministic policy rules for severity and routing.

All records and directives in this repository are fabricated for testing. They do not represent real people, operators, places, or regulatory requirements.

## Requirements

- Python 3.11 or newer
- A Google Gemini API key with access to a supported generative model

## Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a `.env` file in the repository root. Do not commit this file or expose the key:

```dotenv
GEMINI_API_KEY=your_api_key_here
```

The model is configurable. The default is `gemini-3.6-flash`:

```dotenv
GEMINI_MODEL=gemini-3.6-flash
```

Use a model available to the configured API key. Model availability and quotas depend on the Google AI project and plan.

## Run

Run the batch script from the repository root so its relative data paths resolve correctly:

```bash
python run_test.py
```

The script processes `data/intake_records.json` and writes the completed results to:

```text
data/output_results.json
```

The output contains the structured extraction, severity tier, route, regulatory finding, human-review flags, and execution trace for each record. The output file is written only after the entire batch finishes successfully.

## Input Data

- `data/intake_records.json`: synthetic intake records
- `data/directives_extract.md`: directive reference material
- `data/routing_rules.md`: triage and routing rules

The agent's embedded directive collection is initialized in memory by ChromaDB when the run starts.

## Troubleshooting

### `GEMINI_API_KEY environment variable not set`

Check that `.env` is in the repository root and contains a non-empty key. Alternatively, export the variable before running:

```bash
export GEMINI_API_KEY="your_api_key_here"
python run_test.py
```

### `404 NOT_FOUND: model is no longer available to new users`

The configured model is unavailable for the current API project. Set `GEMINI_MODEL` to a model currently supported by that key. The default in this project is `gemini-3.6-flash`.

### `429 RESOURCE_EXHAUSTED`

The API key has exceeded its request or token quota, or the selected model has no free-tier allowance. Check the project's Gemini quota and billing settings, then retry with an accessible model or after the quota resets.

### `503 UNAVAILABLE`

The selected model is temporarily under high demand. Retry the batch later. Since results are written at the end of the run, an interrupted batch does not produce a complete output file.

### Relative-path or file-not-found errors

Run the command from `/workspaces/aer-build-challenge` (the repository root), or change into the project directory first:

```bash
cd /workspaces/aer-build-challenge
python run_test.py
```

### ChromaDB startup warnings

A startup warning from `onnxruntime` about PCI discovery is generally non-fatal. Continue unless the process exits with a traceback.

## Notes

- Gemini calls can be slow because each record is processed individually.
- Human flags are intentional review controls and should not be treated as processing failures.
- Do not use this synthetic exercise for real regulatory decisions or real personal information.

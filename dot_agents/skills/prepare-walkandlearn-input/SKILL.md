---
name: prepare-walkandlearn-input
description: Prepare a WalkAndLearn LangGraph input file from a conversation copied to the macOS clipboard. Use when the user says they have a clipboard conversation/session/export to turn into a WalkAndLearn or W&L Summary input, asks for a LangGraph state block for a copied conversation, or wants the WalkAndLearn UI workflow prepared from clipboard text.
---

# Prepare WalkAndLearn Input

## Purpose

Turn a clipboard conversation export into a local ignored input file for the
`W&L Summary` LangGraph graph, then copy the ready state JSON back to the
clipboard.

Default target repo:

```text
/Users/flo/Work/Private/Dev/AI/Agents
```

## Workflow

1. Confirm the clipboard is plausible before writing:
   - Run `pbpaste | wc -c`.
   - Treat content under `2000` bytes as suspiciously short.
   - Do not print clipboard content in chat.

2. Resolve metadata before running the script:
   - Date must be concrete `YYYY-MM-DD`.
   - Resolve relative dates explicitly using the current date.
   - Topic should be a short slug-like phrase, e.g. `rag-precision-recall`.
   - If date or topic is missing, ask the user before running the script.
   - If topic is unclear, privately inspect only a small sample and suggest 1-3 concise topic slugs for the user to choose from.

3. Run the helper script:

```bash
python3 /Users/flo/.agents/skills/prepare-walkandlearn-input/scripts/prepare_walkandlearn_input.py \
  --date YYYY-MM-DD \
  --topic "topic words"
```

4. Report the generated filename and state block from script output.

## Behavior Rules

- Never echo the conversation text back to the user.
- Generated files belong under `agent_files/walkandlearn_summary/`.
- Generated files are intentionally ignored by git; never force-add or commit them.
- The script overwrites the clipboard with the LangGraph state JSON.
- If LangGraph is not running at `http://127.0.0.1:2024/ok`, the script starts:

```bash
uv run langgraph dev
```

- LangGraph normally opens the UI itself; do not separately open the browser.
- If browser or Chrome control is available, best-effort focus an existing LangGraph tab after the script succeeds. Do not block the workflow if focusing fails.
- Do not create a thread or start a graph run through the API.

## Script Options

- `--date YYYY-MM-DD`: Required session date.
- `--topic TEXT`: Required topic used for the filename slug.
- `--repo PATH`: Optional override for the Agents repo.
- `--min-bytes N`: Optional clipboard size threshold; default `2000`.
- `--no-launch`: Do not start LangGraph if it is not running.
- `--no-browser-focus`: Marker for callers that browser focusing should be skipped.

## Expected State Output

```json
{
  "messages": [],
  "input_filename": "input-YYYY-MM-DD-topic-slug.md"
}
```

# Module 1: LLM & Tool-Calling Foundation (Ollama / local model version)

## What this module does
Before the agent can act on real code, it needs a way to tell the LLM
"here are your allowed actions" and get back a structured decision
(e.g. "call `read_file` with `path=app.py`") instead of plain English.

This module wires up that communication layer using a **local model
via Ollama**, so there's no API cost and everything runs on your own
machine. No files are actually read/written yet, no commands are
actually run -- that's Module 2 (file/codebase tools) and Module 3
(sandboxed execution).

## Why Ollama (instead of raw Hugging Face transformers)
Ollama has native, built-in tool-calling support for specific open
models, so you don't have to hand-write prompt templates or parse
JSON out of raw text yourself. Not every open model supports this --
stick to one of the tested ones below.

## Setup

1. **Install Ollama**: https://ollama.com/download (Windows/Mac/Linux)

2. **Pull a tool-calling-capable model** (pick one):
   ```bash
   ollama pull qwen2.5       # recommended default, 7b, good tool accuracy
   ollama pull llama3.1      # alternative, 8b
   ollama pull mistral-nemo  # alternative, 12b
   ```
   If your laptop has a weaker GPU/CPU, qwen2.5 or llama3.1 at the
   default (7-8b) quantization is the safer choice over larger models.

3. **Start the Ollama server** (usually auto-starts after install;
   otherwise):
   ```bash
   ollama serve
   ```

4. **Install the Python client**:
   ```bash
   pip install ollama
   ```

## Files
- `tools_schema.py` -- defines the 6 tools the agent can eventually call,
  in the OpenAI-style function schema Ollama expects.
- `llm_client.py` -- wraps the local `ollama.chat()` call with tools
  attached. Includes:
  - `ask_agent_with_retry()` -- if the model replies without calling any
    tool (common with smaller local models), nudges it once with a
    stricter instruction before giving up.
  - `validate_tool_call()` -- checks a chosen tool's arguments against
    its schema (right tool name, all required fields present and
    non-empty) before anything downstream ever sees it.
- `test_module1.py` -- runs 5 sample instructions through the model,
  using the retry + validation above, and logs every run to
  `results_module1.json` (model name, timestamp, pass rate, per-task
  detail) so you have real numbers, not just terminal output.
- `compare_models.py` -- runs the same test suite across multiple
  pulled models back-to-back and prints a comparison table.

## Run the acceptance test
```bash
python test_module1.py            # uses the default model (qwen2.5)
python test_module1.py llama3.1   # or test a specific model
```

Expected output, for each sample task:
```
[PASS] Task: 'Read the file called config.py'
       Expected tool: read_file | Got: read_file (attempts: 1)
       Tool input: {'path': 'config.py'}
```
A FAIL will also show a `Reason:` line -- e.g. "No tool call after
retry" or "Missing/empty required argument(s): ['path']" -- so you can
tell at a glance whether it was a tool-selection mistake or a bad-
argument mistake.

## Compare multiple models
```bash
ollama pull qwen2.5
ollama pull llama3.1
python compare_models.py
```
This prints a side-by-side pass rate and appends both runs to
`results_module1.json`. Use whichever model scores higher (or is fast
enough for your machine) as your default going forward, and mention
the comparison explicitly in your README/interview -- it's a concrete,
defensible design decision.

## A known limitation to expect (and to mention in interviews)
Open, smaller local models are noticeably less reliable at tool
calling than frontier hosted models -- expect some FAILs, especially
on ambiguous phrasing, even with the retry logic above. This is worth
measuring, not hiding: your `results_module1.json` log is exactly the
evidence to cite (e.g. "qwen2.5 correctly selected the right tool in
4/5 cases even after one retry attempt") and becomes the seed of your
Module 8 evaluation work later.

## Next module
Module 2 implements the actual Python functions behind `read_file`,
`write_file`, and `search_codebase` so tool calls do something real.

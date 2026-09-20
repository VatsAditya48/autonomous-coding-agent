"""
Module 1: LLM + tool-calling foundation (Ollama version).

Wraps the local Ollama call so the rest of the agent just says
"here's the task, tell me what tool to call next" -- same interface
as the Anthropic version, so Modules 2-9 don't care which backend
is behind this file.

Requires:
    1. Ollama installed and running: https://ollama.com/download
    2. Model pulled locally:   ollama pull qwen2.5
    3. Python client:          pip install ollama

At this stage, NOTHING is actually executed. We're only confirming
the model can correctly choose a tool and produce valid structured
input for it.
"""

import ollama

DEFAULT_MODEL = "qwen2.5"  # swap for "llama3.1" or "mistral-nemo" if you prefer

from tools_schema import TOOLS

SYSTEM_PROMPT = """You are an autonomous coding agent. You have access to tools
that let you read, write, and search a codebase, run commands and tests inside
a sandbox, and inspect git diffs.

Given a task, decide which SINGLE tool to call next to make progress. Only call
one tool at a time. Always respond by calling the most appropriate tool rather
than replying in plain text."""

# A stricter follow-up used only when the model fails to call a tool the
# first time. Small local models sometimes reply in plain text instead of
# using a tool -- this gives them one more chance before we count it as a
# real failure.
RETRY_NUDGE = (
    "You did not call a tool. You MUST respond by calling exactly one of "
    "the available tools -- do not reply in plain text."
)

# Build a lookup of required arguments per tool, straight from the schema,
# so validation never drifts out of sync with tools_schema.py.
_REQUIRED_ARGS = {
    tool["function"]["name"]: tool["function"]["parameters"].get("required", [])
    for tool in TOOLS
}


def _call_model(messages: list, model: str):
    return ollama.chat(model=model, messages=messages, tools=TOOLS)


def ask_agent(task: str, history: list | None = None, model: str = DEFAULT_MODEL):
    """
    Send a task (plus optional prior conversation history) to a local
    Ollama model and return its raw response. Use `model` to swap between
    qwen2.5 / llama3.1 / etc. for comparison.
    """
    messages = history if history else []
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages + [
        {"role": "user", "content": task}
    ]
    return _call_model(messages, model)


def ask_agent_with_retry(task: str, model: str = DEFAULT_MODEL, max_retries: int = 1):
    """
    Same as ask_agent(), but if the model replies without calling any tool,
    nudge it once (or `max_retries` times) with a stricter instruction
    before giving up. Returns (response, attempts_used).
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    response = _call_model(messages, model)
    attempts = 1

    while attempts <= max_retries:
        tool_name, _ = extract_tool_call(response)
        if tool_name is not None:
            break
        messages.append(response["message"])
        messages.append({"role": "user", "content": RETRY_NUDGE})
        response = _call_model(messages, model)
        attempts += 1

    return response, attempts


def extract_tool_call(response):
    """
    Pull the first tool call out of an Ollama response, if any.
    Returns (tool_name, tool_input) or (None, None).
    """
    message = response.get("message", {})
    tool_calls = message.get("tool_calls")

    if not tool_calls:
        return None, None

    call = tool_calls[0]
    name = call["function"]["name"]
    arguments = call["function"]["arguments"]
    return name, arguments


def validate_tool_call(tool_name: str, tool_input: dict):
    """
    Check a tool call against its schema before anything downstream
    (Module 2/3) ever sees it. Returns (is_valid: bool, error: str | None).

    This catches cases like the model inventing an argument name, leaving
    a required field empty, or calling a tool that doesn't exist -- all
    more common with smaller local models than with frontier hosted ones.
    """
    if tool_name not in _REQUIRED_ARGS:
        return False, f"Unknown tool '{tool_name}' -- not in tools_schema.py"

    if tool_input is None:
        tool_input = {}

    missing = [arg for arg in _REQUIRED_ARGS[tool_name] if not tool_input.get(arg)]
    if missing:
        return False, f"Missing/empty required argument(s): {missing}"

    return True, None

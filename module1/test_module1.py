"""
Module 1 acceptance test (Ollama version).

Confirms: given plain-English instructions, the local model correctly
chooses the right tool and produces valid, schema-conformant input for it --
retrying once if the model fails to call a tool at all.

Results are logged to results_module1.json so you have a real number to
quote later ("qwen2.5: 4/5, 80% pass rate") instead of just eyeballing
the terminal output.

Usage:
    ollama pull qwen2.5      # one-time download
    ollama serve             # if not already running in the background
    python test_module1.py [model_name]
"""

import json
import sys
from datetime import datetime, timezone

from llm_client import ask_agent_with_retry, extract_tool_call, validate_tool_call, DEFAULT_MODEL

TEST_CASES = [
    ("Read the file called config.py", "read_file"),
    ("Search the codebase for the function calculate_total", "search_codebase"),
    ("Create a file named hello.txt containing 'Hello World'", "write_file"),
    ("Run the test suite and tell me if it passes", "run_tests"),
    ("Show me what has changed so far in the repo", "git_diff"),
]


def run_tests(model: str = DEFAULT_MODEL, log_path: str = "results_module1.json"):
    passed = 0
    results = []

    for task, expected_tool in TEST_CASES:
        response, attempts = ask_agent_with_retry(task, model=model)
        tool_name, tool_input = extract_tool_call(response)

        if tool_name is None:
            status, reason = "FAIL", "No tool call after retry"
        elif tool_name != expected_tool:
            status, reason = "FAIL", f"Wrong tool (expected {expected_tool})"
        else:
            is_valid, error = validate_tool_call(tool_name, tool_input)
            status, reason = ("PASS", None) if is_valid else ("FAIL", error)

        if status == "PASS":
            passed += 1

        print(f"[{status}] Task: {task!r}")
        print(f"       Expected tool: {expected_tool} | Got: {tool_name} (attempts: {attempts})")
        print(f"       Tool input: {tool_input}")
        if reason:
            print(f"       Reason: {reason}")
        print()

        results.append({
            "task": task,
            "expected_tool": expected_tool,
            "got_tool": tool_name,
            "tool_input": tool_input,
            "attempts": attempts,
            "status": status,
            "reason": reason,
        })

    pass_rate = passed / len(TEST_CASES)
    print(f"Result: {passed}/{len(TEST_CASES)} passed ({pass_rate:.0%})")

    log_entry = {
        "model": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pass_count": passed,
        "total": len(TEST_CASES),
        "pass_rate": pass_rate,
        "results": results,
    }

    try:
        with open(log_path, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append(log_entry)
    with open(log_path, "w") as f:
        json.dump(history, f, indent=2)

    print(f"Logged results to {log_path}")
    return pass_rate


if __name__ == "__main__":
    model_arg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
    run_tests(model=model_arg)

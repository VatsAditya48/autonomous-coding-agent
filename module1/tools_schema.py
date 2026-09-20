"""
Module 1: Tool schema definitions (Ollama version).

Ollama's tool-calling format follows the OpenAI-style function schema:
each tool is wrapped as {"type": "function", "function": {...}}.

Only specific models support tool calling reliably in Ollama, e.g.:
  - qwen2.5 (recommended: good accuracy, runs at 7b on a laptop)
  - llama3.1 (8b or larger)
  - mistral-nemo
  - firefunction-v2

These describe WHAT the agent can do. The actual implementation
(reading real files, running real commands) comes in Module 2 and 3.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the repository given its path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file, e.g. 'src/app.py'",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file with the given content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file to write."},
                    "content": {"type": "string", "description": "Full new content of the file."},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_codebase",
            "description": "Search the codebase for a keyword, function name, or pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text or regex pattern to search for."}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command inside the isolated Docker sandbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute."}
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Run the repository's test suite inside the sandbox and return pass/fail plus error output.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_diff",
            "description": "Return a diff of all changes made so far in the working repo.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

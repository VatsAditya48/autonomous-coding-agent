# Architecture

## Overview

```
User Input (repo + task)
        |
        v
   Host machine
   +-------------------------------------------+
   |  Orchestrator (Python)                     |
   |  Plan -> Act -> Observe -> Reflect loop    |
   |  Tools: read_file, write_file,             |
   |         search_codebase, git_diff          |
   |                                             |
   |         <-- reasoning -->  LLM API          |
   |         (local model via Ollama)           |
   |                                             |
   |  +---------------------------------------+ |
   |  |  Docker sandbox (isolated)            | |
   |  |  run_command()   run_tests()          | |
   |  +---------------------------------------+ |
   +-------------------------------------------+
        |
        v
   GitHub (PR with diff)
```

## Components

- **Orchestrator**: owns the agent loop and the tools that are safe to run
  directly on the host (reading/writing files, searching the codebase,
  diffing). Decides what to do next by asking the LLM.
- **LLM (local, via Ollama)**: does the reasoning -- which tool to call,
  how to interpret a test failure, when to stop. Not hosted/paid; runs on
  the dev machine or a shared team machine.
- **Docker sandbox**: isolates anything that actually executes code
  (`run_command`, `run_tests`) so the agent can never damage the host
  machine, even if it generates a bad or destructive command.
- **GitHub**: the agent's changes always land as a PR, never a direct
  push to main -- a human reviews and merges.

## Safety guardrails (Module 4)
1. Docker sandbox -- execution isolation
2. Max iterations -- stops infinite self-correction loops
3. Command timeout -- kills hung processes
4. Restricted commands -- blocks destructive patterns (`rm -rf`,
   `git push --force`, etc.)
5. User confirmation -- required before any flagged destructive action

See [../README.md](../README.md) for the module breakdown and
[PRD.md](PRD.md) for full requirements.

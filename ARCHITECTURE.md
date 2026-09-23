# Architecture

## Overview

The agent is deployed as a **hosted web app** with a live URL -- not a
local CLI tool. A user opens the page, submits a repo + task, and
watches the agent's reasoning trace update live while it works.

```
Browser (user)
   |  submits repo + task, watches live reasoning trace
   v
Frontend (React or simple HTML/JS)
   |  WebSocket / SSE connection for live updates
   v
Backend API (FastAPI) -- runs on the cloud VM
   |
   v
Orchestrator (Python)
Plan -> Act -> Observe -> Reflect loop
Tools: read_file, write_file, search_codebase, git_diff
   |
   |        <-- reasoning -->   Ollama (self-hosted on the same VM)
   |                             qwen2.5 / llama3.1, CPU inference
   |
   v
Docker sandbox (isolated, same VM)
   run_command()   run_tests()
   |
   v
GitHub (PR with diff)
```

## Components

- **Frontend**: takes the repo + task from the user, opens a live
  connection to the backend, and renders the agent's step-by-step
  reasoning as it happens (not just the final result).
- **Backend API (FastAPI)**: the bridge between the frontend and the
  orchestrator -- receives requests, streams progress back over
  WebSockets/SSE, and exposes the guardrail confirmation step (Module 4)
  as an actual button in the UI when a destructive action needs approval.
- **Orchestrator**: owns the agent loop and the tools that are safe to
  run directly on the host (reading/writing files, searching the
  codebase, diffing). Decides what to do next by asking the LLM.
- **LLM (self-hosted via Ollama, on the same cloud VM)**: does the
  reasoning -- which tool to call, how to interpret a test failure, when
  to stop. Runs on CPU by default (slower, ~5-15s/response) to keep
  hosting cost predictable; a GPU instance would speed this up at a
  meaningfully higher monthly cost.
- **Docker sandbox**: isolates anything that actually executes code
  (`run_command`, `run_tests`) so the agent can never damage the host VM,
  even if it generates a bad or destructive command. Runs on the same VM
  (or a securely networked second VM for stronger isolation).
- **GitHub**: the agent's changes always land as a PR, never a direct
  push to main -- a human reviews and merges.

## Deployment notes
- Needs a VM that allows running Docker (not a serverless/static host --
  e.g. a DigitalOcean/Linode/Hetzner droplet, or an AWS EC2 instance)
- Nginx (or similar) as a reverse proxy in front of the FastAPI backend
- systemd or Docker Compose to keep Ollama, the backend, and the sandbox
  running reliably across restarts
- Budget: roughly $20-40/month for a CPU-only VM with enough RAM to run
  a 7-8B model; a GPU instance for faster responses runs $100+/month

## Safety guardrails (Module 4)
1. Docker sandbox -- execution isolation
2. Max iterations -- stops infinite self-correction loops
3. Command timeout -- kills hung processes
4. Restricted commands -- blocks destructive patterns (`rm -rf`,
   `git push --force`, etc.)
5. User confirmation -- required before any flagged destructive action

See [../README.md](../README.md) for the module breakdown and
[PRD.md](PRD.md) for full requirements.

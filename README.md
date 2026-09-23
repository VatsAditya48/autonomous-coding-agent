# Autonomous AI Coding Agent

An autonomous agent, delivered as a **hosted web app**, that takes a
GitHub repo + a task (e.g. "fix this failing test") and plans, edits,
tests, and self-corrects code changes with minimal human intervention --
with sandboxing and guardrails to keep it safe, and a live view of its
reasoning in the browser.

Full requirements, architecture, and success metrics: see [docs/PRD.md](docs/PRD.md).

## Project structure

This repo is organized into independent modules, built roughly in order.
Each module has its own folder with a README, code, and (where relevant)
a test/eval script.

| Module | Folder | Status | What it does |
|---|---|---|---|
| 1 | [`module1/`](module1/) | ✅ In progress | LLM + tool-calling foundation (self-hosted model via Ollama) |
| 2 | `module2/` | ⬜ Not started | File & codebase tools (read/write/search) |
| 3 | `module3/` | ⬜ Not started | Docker sandbox & execution environment |
| 4 | `module4/` | ⬜ Not started | Safety & guardrails (blocklist, timeout, max iterations, confirmation) |
| 5 | `module5/` | ⬜ Not started | Agentic orchestration loop (Plan → Act → Observe → Reflect) |
| 6 | `module6/` | ⬜ Not started | Codebase understanding at scale (embeddings/repo map) |
| 7 | `module7/` | ⬜ Not started | Git integration & PR automation |
| 8 | `module8/` | ⬜ Not started | Evaluation & benchmarking |
| 9 | `module9/` | ⬜ Not started | Web app (frontend + API), cloud deployment, and demo |

## Tech stack
- **LLM**: self-hosted via [Ollama](https://ollama.com) (qwen2.5 / llama3.1), running on the deployment VM -- open-source, no per-token API cost
- **Language**: Python
- **Backend API**: FastAPI, streaming live agent progress over WebSockets/SSE
- **Frontend**: React (or a simple HTML/JS page) showing the live reasoning trace and the guardrail confirmation step as an actual UI action
- **Sandboxing**: Docker
- **Search**: ripgrep, embeddings via Chroma/FAISS (Module 6)
- **Version control**: Git, GitPython, GitHub API
- **Hosting/deployment**: a cloud VM that supports Docker (e.g. DigitalOcean/Linode/Hetzner droplet or AWS EC2), Nginx as reverse proxy, systemd or Docker Compose to keep services running

## Getting started

Each module is self-contained -- see its own README for setup. To start
with what's currently built:

```bash
cd module1
pip install -r requirements.txt
ollama pull qwen2.5
python test_module1.py
```

## Working as a team

- Create a branch per module or per feature: `git checkout -b module2-file-tools`
- Open a PR into `main` when a module's acceptance criteria (in its
  README) are met -- don't merge straight to main
- Keep each module's README up to date as you build; it doubles as your
  eventual project documentation and demo script
- Log real results (pass rates, benchmarks) into each module's folder as
  you go -- this becomes Module 8's evaluation data and your resume/
  interview talking points later

# Web App, Deployment & Demo

Status: not started yet.

**Scope update:** this project is being delivered as a hosted web app,
not a CLI tool -- so this module now covers meaningfully more than the
original "polish and demo" scope. It includes:

1. **Backend API (FastAPI)** wrapping the Module 5 orchestrator --
   endpoints to start a run, and a WebSocket/SSE channel to stream the
   agent's step-by-step reasoning to the frontend live
2. **Frontend** (React or a simple HTML/JS page): repo + task input,
   a live reasoning trace view, and a real UI control for the Module 4
   user-confirmation guardrail (an actual approve/deny button, not a
   terminal prompt)
3. **Deployment**: a cloud VM that supports Docker (e.g. a
   DigitalOcean/Linode/Hetzner droplet or AWS EC2 instance), Ollama
   self-hosted on that same VM, Nginx as a reverse proxy, and
   systemd/Docker Compose to keep Ollama + backend + sandbox running
   reliably
4. **Demo & docs**: the README, architecture writeup, and a short demo
   video/walkthrough of a real task being solved end-to-end on the live
   URL

**Worth discussing as a team:** this is now real full-stack + DevOps
work on top of the original "demo polish" scope -- if it's too much for
one person alongside Module 7, consider splitting backend/frontend/
deployment across two people, or pulling in help once Module 5 is
stable enough to build against.

See the root [PRD](../docs/PRD.md), [ARCHITECTURE.md](../docs/ARCHITECTURE.md),
and [README](../README.md) for this module's place in the overall build plan.

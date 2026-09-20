# Autonomous AI Coding Agent — PRD & Build Plan

## 1. Problem Statement

Developers spend significant time on repetitive coding tasks: fixing failing tests, implementing small features, and debugging errors. Most AI coding tools today are **copilots** — they suggest code, but a human still has to run it, test it, and fix mistakes.

This project builds an **autonomous agent**: given a GitHub repo and a task, it plans the change, writes code, executes tests in a sandbox, reads failures, and self-corrects — with minimal human intervention, but never at the cost of safety.

## 2. Goal

Build a working agent that can take a real GitHub issue (e.g., "fix this failing test" or "add this small feature") and produce a correct, tested code change autonomously, with guardrails preventing destructive actions.

## 3. Success Metrics (put these on your resume/demo)

- **Pass rate**: % of tasks solved without human intervention (target: benchmark against 10–15 real issues)
- **Self-correction rate**: % of initially-failing attempts that succeed within N retries
- **Average attempts to success**
- **Safety**: 0 destructive actions executed without confirmation, across all test runs
- **Latency/cost**: average time and $ per completed task

## 4. Scope

**In scope (MVP):**
- Single-repo, single-task workflow (not multi-repo orchestration)
- Python/JS repos only, to start
- Terminal-based or simple web demo UI
- One LLM backend (Claude or GPT-4o) via function calling

**Out of scope (for now):**
- Multi-agent collaboration (planner + coder + reviewer as separate agents) — good v2 feature
- Auto-merging PRs without human review
- Support for every language/build system

## 5. Users & Use Case

Primary use case: you feed it a GitHub issue link + repo. It clones the repo, understands the codebase, makes the fix, runs tests, and either:
- Opens a PR with the fix, or
- Reports back that it couldn't solve it within the attempt limit

## 6. Core Requirements

### 6.1 Functional Requirements
| # | Requirement |
|---|---|
| FR1 | Agent can clone a repo and index its file structure |
| FR2 | Agent can search the codebase for relevant files/functions |
| FR3 | Agent can read and write files |
| FR4 | Agent can run arbitrary shell commands inside a sandbox |
| FR5 | Agent can run the repo's test suite and parse pass/fail + error output |
| FR6 | Agent can loop: modify → test → analyze failure → retry, up to a max attempt count |
| FR7 | Agent can produce a git diff / open a PR summarizing changes |

### 6.2 Non-Functional / Safety Requirements
| # | Requirement |
|---|---|
| NFR1 | All code execution happens inside an isolated Docker container |
| NFR2 | Max iteration limit enforced (default: 5) |
| NFR3 | Command execution has a timeout (e.g., 60s) |
| NFR4 | A blocklist of restricted commands (`rm -rf`, `git push --force`, `curl \| bash`, etc.) |
| NFR5 | Any destructive action requires explicit user confirmation before execution |
| NFR6 | All agent actions are logged for auditability/debugging |

## 7. High-Level Architecture

```
User Input (repo + task)
        │
        ▼
   Orchestrator (Python)
   Plan → Act → Observe → Reflect loop
        │
        ├── Tool: search_codebase()   → ripgrep / embeddings
        ├── Tool: read_file()
        ├── Tool: write_file()
        ├── Tool: run_command()       → executes INSIDE Docker
        ├── Tool: run_tests()         → executes INSIDE Docker
        └── Tool: git_diff()
        │
        ▼
   LLM API (Claude/GPT-4o) — decides which tool to call next
        │
        ▼
   Docker Sandbox — isolated execution environment
        │
        ▼
   Result: Passing code + PR, OR failure report after max attempts
```

## 8. Tech Stack

| Layer | Tech |
|---|---|
| Orchestration | Python |
| LLM reasoning | Claude API (function calling / tool use) |
| Sandboxing | Docker |
| Code search | ripgrep (regex/literal) → embeddings for larger repos |
| Version control | GitPython / GitHub API |
| Test execution | pytest / npm test (matched to repo language) |
| Logging/eval | JSON logs + simple eval harness |

---

# Build Plan — Step by Step

## Phase 0: Setup (Day 1–2)
1. Set up Python project, virtualenv, repo structure
2. Get Claude API access working with a basic function-calling call
3. Get Docker installed and test running a simple container from Python (`docker` SDK for Python)

**Deliverable:** You can call the LLM API and separately spin up a Docker container from a script.

## Phase 1: Core Tools (Day 3–7)
Build each tool as an isolated, testable Python function first — before wiring up the agent loop.

4. `read_file(path)` — reads file from local repo clone
5. `write_file(path, content)` — writes/overwrites file
6. `search_codebase(query)` — start with ripgrep subprocess call
7. `run_command(cmd)` — executes inside Docker container, captures stdout/stderr, enforces timeout
8. `run_tests()` — detects test framework (pytest/npm), runs it inside Docker, parses pass/fail
9. `git_diff()` — returns diff of changes made so far

**Deliverable:** Each tool works standalone when called manually with hardcoded inputs.

## Phase 2: Sandbox & Safety Layer (Day 8–10)
10. Build a Dockerfile that clones the target repo and installs its dependencies
11. Wire `run_command` and `run_tests` to execute *inside* this container, not on host
12. Add command blocklist check before any `run_command` call executes
13. Add max-iteration counter to the orchestrator (stop after N attempts)
14. Add a `confirm_action()` step that pauses and asks the user before destructive commands

**Deliverable:** You can run ANY generated command safely — try it with intentionally bad commands (`rm -rf /`) and confirm they're blocked.

## Phase 3: The Agent Loop (Day 11–16)
15. Write the system prompt: describe available tools, the task, and instruct the LLM to reason step-by-step about which tool to call next (ReAct-style)
16. Implement the orchestrator loop:
    - Send task + current state to LLM
    - Parse tool call from response
    - Execute tool, capture result
    - Feed result back to LLM as next input
    - Repeat until tests pass, or max attempts reached
17. Implement the self-correction step explicitly: on test failure, feed the error trace back to the LLM with a prompt like "tests failed with this error, analyze the cause and fix it"

**Deliverable:** End-to-end run on ONE simple hardcoded task (e.g., a repo with one intentionally broken function + one failing test) — agent should fix it autonomously.

## Phase 4: Codebase Understanding at Scale (Day 17–20)
18. For larger repos, ripgrep alone won't be enough — add embedding-based search (chunk files, embed with a small model, store in Chroma/FAISS, retrieve top-k relevant chunks)
19. Add a lightweight "repo map" step so the agent gets an overview (file tree + key modules) before diving in

**Deliverable:** Agent can handle a multi-file repo, not just a single-file toy example.

## Phase 5: Evaluation (Day 21–24)
20. Collect 10–15 real GitHub issues (good first issues from small open-source repos, or intentionally-broken forks you create yourself)
21. Build a simple eval script: run the agent on each, log pass/fail, attempts-to-success, time, cost
22. Compute your headline metrics: pass rate, avg attempts, cost per task

**Deliverable:** A results table you can put directly in your resume/README/demo.

## Phase 6: Polish & Demo (Day 25–28)
23. Add PR creation via GitHub API (agent opens a real PR with its diff + explanation)
24. Build a minimal UI or CLI output that's demo-friendly (show the reasoning trace, not just the final diff)
25. Record a 2-3 min demo video showing a real task being solved end-to-end
26. Write a short technical README / blog post: architecture, guardrails, benchmark results, and one interesting failure case you debugged

**Deliverable:** A polished, presentable project — GitHub repo + README + demo video + benchmark numbers.

---

## Suggested Order If Time-Constrained
If you're short on time before an interview/deadline, prioritize in this order:
1. Phases 0–3 (working agent on a toy example) — **this is the non-negotiable core**
2. Phase 2's safety layer — interviewers will ask about this specifically
3. Phase 5 (evaluation numbers) — this is what makes your resume line credible
4. Phase 4 and Phase 6 can be simplified or partially done if needed

## What to Have Ready for Interviews
- The architecture diagram (from slide 6/7 style)
- A concrete failure story: "here's a case where the agent got it wrong, here's why, here's what I changed"
- Your benchmark numbers, even if the sample size is small — real numbers beat vague claims
- Why you chose Docker/guardrails specifically (tie back to a real risk scenario)

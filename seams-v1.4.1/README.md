# Ship the Seams — v1.4.1 (Prompts + CLI + Server + Graphs)

## Quickstart
1) Start a local model (LM Studio or Ollama), then auto-configure:
```bash
python seams.py configure
```
2) Start the server:
```bash
cd agent-core
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn agent_server:app --host 127.0.0.1 --port 8765 --reload
```
3) Prompts & Graphs:
```bash
python seams.py list-prompts --server http://127.0.0.1:8765
python seams.py list-graphs   --server http://127.0.0.1:8765
```

## CLI examples
```bash
python seams.py run --server http://127.0.0.1:8765 --name refactor_python_function --json '{"code":"def f(x):return x+1","goal":"clarify","constraints":["pep8"],"seed":1}'
python seams.py run-graph --server http://127.0.0.1:8765 --graph refactor_pipeline --json '{"code":"def f(x):return x+1","goal":"clarify","constraints":[],"seed":1}'
```

## VS Code
- Seams: Prompt Menu
- Seams: Run Macro (refactor)
- Seams: Graph Menu

## Health & Readiness
- /healthz, /readyz

---

## Lint Graph — v1.4.1

A minimal, deterministic **lint → (optional) fix → format → diff** pipeline.

- Prefers **local tools**: `ruff` (lint/fix) and `black` (format).  
- If tools are missing or `fix=True` with non-fixing linter, falls back to **LLM minimal fix** (`sig.lint_fix.v1`) and still returns JSON.
- Returns: `{ "code": ..., "notes": "ruff/black/LLM actions + unified diff" }`

### Run
```bash
# Server
python seams.py run-graph --server http://127.0.0.1:8765   --graph lint_pipeline   --json '{"code":"def f(x):\n return 1+1\n","linter":"ruff","formatter":"black","fix":true}'

# Local (no server) — tool-less path
python seams.py run-graph --graph lint_pipeline   --json '{"code":"def f(x):\n return 1+1\n","linter":"none","formatter":"none","fix":false}'
```

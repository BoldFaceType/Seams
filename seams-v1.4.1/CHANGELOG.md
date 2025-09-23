## v1.4.1 — Lint Graph
- Add pydantic-graph based `lint_pipeline` (Preflight → Lint → Format → LLM fallback → Finish).
- Optional local tools: ruff/black; graceful LLM fallback via `sig.lint_fix.v1`.
- Docs and tests updated.

# CHANGELOG

## v1.4.0 — Pydantic Graphs
- Graphs: refactor_pipeline (Plan → DoRefactor) via pydantic-graph.
- Server: /graphs.json, /graph/{name}, /graphs.
- CLI: list-graphs, run-graph.
- VS Code: Seams: Graph Menu.
- Signature bumped to 1.4.0.

## v1.3.0 — Real Backends & Local-first
- OpenAI, Anthropic, OpenAI-compatible (LM Studio, Ollama) in llm_json.
- Auto-detect & write seams.local.json with `python seams.py configure`.
- CLI: run, configure.

## v1.2.0 — Make it Run
- Packaging & health endpoints; HTML escaping; tests; docs.

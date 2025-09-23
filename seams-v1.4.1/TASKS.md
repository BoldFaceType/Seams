# TASKS.md — Remaining Fixes & Nice-to-Haves

## P0
- Per-tool timeout + circuit breaker (env `SEAMS_TOOL_TIMEOUT`); structured error taxonomy.
- Provider backoff on 429/503; redact secrets; cap payload logs.

## P1
- Prompt Registry v2: defaults/enums/examples in `/prompts.json`.
- CLI parity: `--file` JSON input; `--dry-run` prints resolved config.
- Signature linter & CI check; structured logs (tool,rid,dur_ms,backend,model,status).
- Docs: screenshots + troubleshooting matrix.

## P2
- Studio-lite run page; response cache (dev TTL).
- Seed capability probe `/capabilities`.
- Batch evals (NDJSON) + concurrency flag.
- Dockerfile.dev + compose for LM Studio/Ollama.

## Graphs backlog
- Mermaid export endpoints (`/graphs.mmd`, `/graphs.svg`).
- Optional state persistence (JSON/SQLite) for resume/audit.
- Human-in-the-loop pause/resume node + IDE affordance.
- Per-node timeout/retry policy aligned with provider backoff.
- CI graph snapshots (artifacts).

---

## Lint pipeline follow-ups
- Respect `pyproject.toml` for tool config (line length, excludes).
- Surface diagnostics as structured JSON (rule, line, col) alongside notes.
- Add `ruff --select/--ignore` args via input model.
- Optional `isort` step before black.
- Parallel batch mode for files.

# my_agent/graphs/lint_flow.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional, List
import subprocess, tempfile, os, json, shutil, difflib

from pydantic import BaseModel, field_validator
from pydantic_graph import BaseNode, Graph, GraphRunContext, End

# ---- Models ----
class LintInput(BaseModel):
    code: str
    linter: Literal["ruff","flake8","none"] = "ruff"
    formatter: Literal["black","none"] = "black"
    fix: bool = True
    seed: Optional[int] = None  # used only for LLM fallback

    @field_validator("code")
    @classmethod
    def _size(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 200_000:
            raise ValueError("code too large (>200KB)")
        return v

class LintOutput(BaseModel):
    code: str
    notes: str

class LintState(BaseModel):
    inp: LintInput
    orig_code: str
    cur_code: str
    notes: List[str] = []

# ---- Helpers ----
def _bin_exists(name: str) -> bool:
    return shutil.which(name) is not None

def _run(cmd: list[str], cwd: str | None = None, input_bytes: bytes | None = None, timeout: float = 30.0) -> tuple[int, bytes, bytes]:
    p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.PIPE if input_bytes is not None else None,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = p.communicate(input=input_bytes, timeout=timeout)
        return p.returncode, out, err
    except subprocess.TimeoutExpired:
        p.kill()
        return 124, b"", f"timeout: {' '.join(cmd)}".encode()

def _diff(a: str, b: str) -> str:
    return "".join(difflib.unified_diff(a.splitlines(keepends=True), b.splitlines(keepends=True), fromfile="before.py", tofile="after.py"))

# ---- Nodes ----
@dataclass
class Preflight(BaseNode[LintState]):
    async def run(self, ctx: GraphRunContext[LintState]) -> "DoLint" | "Format" | End[LintOutput]:
        if not ctx.state.orig_code.strip():
            return End(LintOutput(code=ctx.state.orig_code, notes="Empty input; nothing to lint."))
        # If user explicitly chose none/none, skip to end
        if ctx.state.inp.linter == "none" and ctx.state.inp.formatter == "none":
            return End(LintOutput(code=ctx.state.orig_code, notes="No linter/formatter selected."))
        return DoLint()

@dataclass
class DoLint(BaseNode[LintState]):
    async def run(self, ctx: GraphRunContext[LintState]) -> "Format" | "LLMFallback" | End[LintOutput]:
        linter = ctx.state.inp.linter
        if linter == "none":
            return Format()
        code = ctx.state.cur_code
        # write to temp file
        with tempfile.TemporaryDirectory() as td:
            f = os.path.join(td, "code.py")
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(code)
            if linter == "ruff":
                if not _bin_exists("ruff"):
                    ctx.state.notes.append("ruff not found")
                    return LLMFallback()
                args = ["ruff", "check", "--quiet", f]
                if ctx.state.inp.fix:
                    args = ["ruff", "check", "--fix", "--quiet", f]
                rc, out, err = _run(args, cwd=td, timeout=30.0)
                # read potentially fixed
                with open(f, "r", encoding="utf-8") as fh:
                    new_code = fh.read()
                if new_code != code:
                    ctx.state.notes.append("ruff applied fixes")
                else:
                    ctx.state.notes.append("ruff found no changes")
                ctx.state.cur_code = new_code
                return Format()
            elif linter == "flake8":
                if not _bin_exists("flake8"):
                    ctx.state.notes.append("flake8 not found")
                    return LLMFallback()
                rc, out, err = _run(["flake8", f], cwd=td, timeout=30.0)
                ctx.state.notes.append(("flake8 issues:\n" + out.decode("utf-8")) if out else "flake8 clean")
                # flake8 doesn't fix; consider LLM fix if fix=True
                if ctx.state.inp.fix:
                    return LLMFallback()
                return Format()
        return Format()

@dataclass
class Format(BaseNode[LintState]):
    async def run(self, ctx: GraphRunContext[LintState]) -> "Finish" | "LLMFallback":
        if ctx.state.inp.formatter == "black":
            if not _bin_exists("black"):
                ctx.state.notes.append("black not found")
                return LLMFallback() if ctx.state.inp.fix else Finish()
            with tempfile.TemporaryDirectory() as td:
                f = os.path.join(td, "code.py")
                with open(f, "w", encoding="utf-8") as fh:
                    fh.write(ctx.state.cur_code)
                rc, out, err = _run(["black", f, "--quiet"], cwd=td, timeout=30.0)
                with open(f, "r", encoding="utf-8") as fh:
                    new_code = fh.read()
                if new_code != ctx.state.cur_code:
                    ctx.state.notes.append("black formatted code")
                ctx.state.cur_code = new_code
        return Finish()

@dataclass
class LLMFallback(BaseNode[LintState]):
    async def run(self, ctx: GraphRunContext[LintState]) -> "Finish":
        from my_agent.llm import llm_json
        payload = {"code": ctx.state.cur_code}
        res = llm_json("sig.lint_fix.v1", payload, temperature=0.0, seed=ctx.state.inp.seed)
        code = res.get("code", ctx.state.cur_code)
        note = res.get("notes", "")
        if code != ctx.state.cur_code:
            ctx.state.notes.append("LLM applied minimal lint/format fix")
        if note:
            ctx.state.notes.append(f"LLM: {note}")
        ctx.state.cur_code = code
        return Finish()

@dataclass
class Finish(BaseNode[LintState, None, LintOutput]):
    async def run(self, ctx: GraphRunContext[LintState]) -> End[LintOutput]:
        diff = _diff(ctx.state.orig_code, ctx.state.cur_code)
        notes = "\n".join(ctx.state.notes + (["diff:\n" + diff] if diff else []))
        return End(LintOutput(code=ctx.state.cur_code, notes=notes))

# Graph
from pydantic_graph import Graph
lint_graph = Graph[LintState, None, LintOutput](nodes=[Preflight, DoLint, Format, LLMFallback, Finish])

def run_lint_graph(inp: LintInput) -> LintOutput:
    state = LintState(inp=inp, orig_code=inp.code, cur_code=inp.code, notes=[])
    res = lint_graph.run_sync(Preflight(), state=state)
    return res.output

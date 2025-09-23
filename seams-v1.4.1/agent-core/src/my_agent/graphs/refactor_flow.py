# my_agent/graphs/refactor_flow.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal, Optional

from pydantic import BaseModel
from pydantic_graph import BaseNode, Graph, GraphRunContext, End

class RefactorInput(BaseModel):
    code: str
    goal: Literal["clarify","optimize","type-annotate"]
    constraints: List[str] = []
    seed: Optional[int] = None

class RefactorOutput(BaseModel):
    code: str
    notes: str

class RefactorState(BaseModel):
    inp: RefactorInput
    out: Optional[RefactorOutput] = None

@dataclass
class Plan(BaseNode[RefactorState]):
    async def run(self, ctx: GraphRunContext[RefactorState]) -> "DoRefactor" | End[RefactorOutput]:
        if "noop" in (ctx.state.inp.constraints or []):
            return End(RefactorOutput(code=ctx.state.inp.code, notes="No-op by constraint"))
        return DoRefactor()

@dataclass
class DoRefactor(BaseNode[RefactorState, None, RefactorOutput]):
    async def run(self, ctx: GraphRunContext[RefactorState]) -> End[RefactorOutput]:
        from my_agent.llm import llm_json
        payload = ctx.state.inp.model_dump()
        result = llm_json("sig.refactor.v1", payload, temperature=0.0, seed=ctx.state.inp.seed)
        out = RefactorOutput.model_validate(result)
        ctx.state.out = out
        return End(out)

refactor_graph = Graph[RefactorState, None, RefactorOutput](nodes=[Plan, DoRefactor])

def run_refactor_graph(inp: RefactorInput) -> RefactorOutput:
    state = RefactorState(inp=inp)
    res = refactor_graph.run_sync(Plan(), state=state)
    return res.output

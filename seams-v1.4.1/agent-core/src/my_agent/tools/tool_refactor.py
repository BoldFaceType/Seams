# my_agent/tools/tool_refactor.py
from pydantic import BaseModel, field_validator
from typing import List
from my_agent.runtime import tool
from my_agent.llm import llm_json

class RefactorInput(BaseModel):
    code: str
    goal: str
    constraints: List[str] = []
    seed: int | None = None

    @field_validator("code")
    @classmethod
    def _size(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 200_000: raise ValueError("code too large (>200KB)")
        return v

    @field_validator("constraints")
    @classmethod
    def _clen(cls, v):
        if len(v) > 100: raise ValueError("too many constraints (>100)")
        return v

    @field_validator("seed")
    @classmethod
    def _seed(cls, v):
        if v is None: return v
        v = int(v)
        if not (0 <= v <= 2**31 - 1): raise ValueError("seed out of range")
        return v

    @field_validator("goal")
    @classmethod
    def _goal(cls, v: str) -> str:
        if v not in {"optimize","clarify","type-annotate"}:
            raise ValueError("goal must be optimize|clarify|type-annotate")
        return v

class RefactorOutput(BaseModel):
    code: str
    notes: str

@tool(name="tool.refactor_python_function", input_model=RefactorInput, output_model=RefactorOutput)
def refactor_python_function(inp: RefactorInput) -> RefactorOutput:
    result = llm_json("sig.refactor.v1", inp.model_dump(), temperature=0.0, seed=inp.seed)
    return RefactorOutput.model_validate(result)

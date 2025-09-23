# my_agent/graphs/__init__.py
from typing import Callable, Dict, Any, TypedDict
from .refactor_flow import run_refactor_graph, RefactorInput, RefactorOutput
from .lint_flow import run_lint_graph, LintInput, LintOutput

class GraphSpec(TypedDict):
    name: str
    input_model: Any
    output_model: Any
    runner: Callable[[Any], Any]

_GRAPH_REGISTRY: Dict[str, GraphSpec] = {
    "lint_pipeline": {"name": "lint_pipeline","input_model": LintInput,"output_model": LintOutput,"runner": run_lint_graph},
    "refactor_pipeline": {
        "name": "refactor_pipeline",
        "input_model": RefactorInput,
        "output_model": RefactorOutput,
        "runner": run_refactor_graph,
    }
}

def list_graphs():
    return [{
        "name": g["name"],
        "input": g["input_model"].model_json_schema(),
        "output": g["output_model"].model_json_schema(),
        "source": "code",
    } for g in _GRAPH_REGISTRY.values()]

def get_graph(name: str) -> GraphSpec:
    if name not in _GRAPH_REGISTRY:
        raise KeyError(name)
    return _GRAPH_REGISTRY[name]

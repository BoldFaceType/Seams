# my_agent/runtime.py
from typing import Callable, Dict, Any, Type
from pydantic import BaseModel

_REGISTRY: Dict[str, Dict[str, Any]] = {}

def tool(name: str, input_model: Type[BaseModel], output_model: Type[BaseModel]):
    def decorator(fn: Callable[[BaseModel], BaseModel]):
        _REGISTRY[name] = {"fn": fn, "input_model": input_model, "output_model": output_model}
        return fn
    return decorator

def get_tool(name: str):
    if name not in _REGISTRY:
        raise KeyError(f"Tool not found: {name}")
    return _REGISTRY[name]

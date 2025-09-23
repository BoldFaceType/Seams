# agent_server.py
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ValidationError
from typing import Dict, Any
from my_agent.runtime import get_tool
from my_agent.tools.tool_refactor import RefactorInput, RefactorOutput  # registers tool
from my_agent.graphs import list_graphs, get_graph

import os, html, json as _json, uuid, time, logging
from pathlib import Path

app = FastAPI(title="Seams Agent Tool Server", version="1.4.0")
log = logging.getLogger("seams")
if not log.handlers: logging.basicConfig(level=logging.INFO)

class InvokeRequest(BaseModel):
    payload: Dict[str, Any]

@app.post("/tool/{tool_name}")
def invoke(tool_name: str, req: InvokeRequest):
    rid = str(uuid.uuid4())[:8]; t0 = time.perf_counter(); ok = False
    try:
        try: reg = get_tool(tool_name)
        except KeyError as e: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        In, Out, fn = reg["input_model"], reg["output_model"], reg["fn"]
        try: inp = In(**req.payload)
        except ValidationError as e: raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
        out = fn(inp)
        assert isinstance(out, Out), "Tool did not return expected output model"
        ok = True
        return out.model_dump()
    except HTTPException: raise
    except Exception: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="internal_error")
    finally:
        log.info("invoke", extra={"rid": rid, "tool": tool_name, "ok": ok, "dur_ms": round((time.perf_counter()-t0)*1000,1)})

# Prompt menu
default_sig = Path(__file__).resolve().parents[2] / "signatures"
SIG_DIR = Path(os.environ.get("SEAMS_SIGNATURE_DIR", default_sig))

def _collect_prompts():
    items = []
    for p in SIG_DIR.glob("*.json"):
        try: data = _json.loads(p.read_text(encoding="utf-8"))
        except Exception: continue
        params = [{"name": k, "type": v.get("type","string"), "required": True} for k,v in (data.get("inputs") or {}).items()]
        ret = ", ".join(list((data.get("outputs") or {}).keys()) or [])
        items.append({"name": data.get("name", p.stem), "description": data.get("prompt_id",""), "params": params, "returns": ret or "object", "template": True, "source": str(p.name)})
    items.sort(key=lambda x: x["name"])
    return items

@app.get("/prompts.json")
def prompts_json():
    return _collect_prompts()

@app.get("/prompts")
def prompts_html():
    items = _collect_prompts()
    def row(it):
        name = html.escape(str(it.get('name','')), quote=True)
        args = ", ".join([f'"{html.escape(str(p["name"]))}": "<'+html.escape(str(p['type']))+'>"' for p in it.get("params", [])])
        cmd = f"python seams.py run --name {name} --json '{{{args}}}'"
        return ("<div style='margin:8px 0;padding:8px;border:1px solid #ddd;border-radius:8px'>"
                f"<b>{name}</b><br>"
                f"<button onclick=\"navigator.clipboard.writeText('{html.escape(cmd, quote=True)}')\">Copy Run Command</button>"
                "</div>")
    body = "<!doctype html><title>Prompts</title><style>body{font:14px system-ui;margin:1rem}</style><h1>Prompt Menu</h1>" + "".join([row(it) for it in items])
    return Response(content=body, media_type="text/html")

# Graph endpoints + HTML
@app.get("/graphs.json")
def graphs_json():
    return list_graphs()

@app.post("/graph/{name}")
def graph_run(name: str, payload: dict):
    try: spec = get_graph(name)
    except KeyError: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"unknown graph '{name}'")
    InModel, OutModel, runner = spec["input_model"], spec["output_model"], spec["runner"]
    inp = InModel.model_validate(payload)
    out = runner(inp)
    return OutModel.model_validate(out).model_dump()

@app.get("/graphs")
def graphs_html():
    items = list_graphs()
    def row(it):
        name = html.escape(str(it.get('name','')), quote=True)
        props = (it.get('input') or {}).get('properties', {}) or {}
        example_pairs = []
        for k,v in props.items():
            t = v.get('type','string')
            val = '0' if t=='integer' else ('[]' if t=='array' else '"<value>"')
            example_pairs.append(f'"{k}": {val}')
        json_body = '{' + ', '.join(example_pairs) + '}'
        cmd = f"python seams.py run-graph --graph {name} --json '{json_body}'"
        return ("<div style='margin:8px 0;padding:8px;border:1px solid #ddd;border-radius:8px'>"
                f"<b>{name}</b><br>"
                f"<button onclick=\"navigator.clipboard.writeText('{html.escape(cmd, quote=True)}')\">Copy Run Command</button>"
                "</div>")
    body = "<!doctype html><title>Graphs</title><style>body{font:14px system-ui;margin:1rem}</style><h1>Graphs</h1>" + "".join([row(it) for it in items])
    return Response(content=body, media_type="text/html")

@app.get("/healthz")
def healthz(): return {"ok": True}

@app.get("/readyz")
def readyz(): return {"ok": SIG_DIR.exists(), "sig_dir": str(SIG_DIR)}

# agent_core_detect.py
import json, os
from pathlib import Path
import httpx

def detect() -> dict:
    cfg = {}
    for base in ["http://127.0.0.1:1234/v1", "http://127.0.0.1:11434/v1"]:
        try:
            with httpx.Client(timeout=2.0) as c:
                r = c.get(f"{base}/models")
            if r.status_code == 200:
                cfg.update({"backend":"openai_compat","openai_base_url":base})
                try:
                    data = r.json(); model = None
                    if "data" in data and data["data"]: model = data["data"][0].get("id")
                    elif "models" in data and data["models"]:
                        m0 = data["models"][0]; model = m0.get("id") or m0.get("model")
                    if model: cfg["model"] = model
                except Exception: pass
                break
        except Exception: pass
    if not cfg and os.environ.get("OPENAI_API_KEY"): cfg = {"backend":"openai","model":"gpt-4o-mini"}
    elif not cfg and os.environ.get("ANTHROPIC_API_KEY"): cfg = {"backend":"anthropic","model":"claude-3-haiku-20240307"}
    if not cfg: cfg = {"backend":"stub","model":"noop"}
    return cfg

def detect_and_write(path: str | None = None) -> str:
    here = Path(__file__).resolve().parent
    out = Path(path or (here / "seams.local.json"))
    out.write_text(json.dumps(detect(), indent=2), encoding="utf-8")
    return str(out)

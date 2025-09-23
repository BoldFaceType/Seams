# my_agent/llm.py
# Real provider adapters; local-first auto-detect for LM Studio/Ollama.
from typing import Any, Dict
import os, json, httpx
from pathlib import Path
from jinja2 import Template

def _load_config_file() -> Dict[str, Any]:
    p = Path(__file__).resolve().parents[2] / "seams.local.json"
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except Exception: pass
    return {}

def _effective_cfg() -> Dict[str, Any]:
    cfg = _load_config_file()
    if os.environ.get("SEAMS_BACKEND"): cfg["backend"] = os.environ["SEAMS_BACKEND"]
    if os.environ.get("SEAMS_OPENAI_BASE_URL"): cfg["openai_base_url"] = os.environ["SEAMS_OPENAI_BASE_URL"]
    if os.environ.get("SEAMS_MODEL"): cfg["model"] = os.environ["SEAMS_MODEL"]
    # Probe local OpenAI-compatible servers
    if not cfg.get("backend"):
        for base in ["http://127.0.0.1:1234/v1", "http://127.0.0.1:11434/v1"]:
            try:
                with httpx.Client(timeout=2.0) as c:
                    r = c.get(f"{base}/models")
                if r.status_code == 200:
                    cfg.update({"backend":"openai_compat","openai_base_url":base})
                    try:
                        data = r.json()
                        model = None
                        if "data" in data and data["data"]:
                            model = data["data"][0].get("id")
                        elif "models" in data and data["models"]:
                            m0 = data["models"][0]; model = m0.get("id") or m0.get("model")
                        if model: cfg["model"] = model
                    except Exception: pass
                    break
            except Exception:
                pass
    if not cfg.get("backend"):
        if os.environ.get("OPENAI_API_KEY"):
            cfg["backend"] = "openai"
        elif os.environ.get("ANTHROPIC_API_KEY"):
            cfg["backend"] = "anthropic"
        else:
            cfg["backend"] = "stub"
    if not cfg.get("model"):
        cfg["model"] = "gpt-4o-mini" if cfg["backend"] in ("openai","openai_compat") else "claude-3-haiku-20240307"
    return cfg

def _render_prompt(prompt_id: str, variables: Dict[str, Any]) -> str:
    tpl = Path(__file__).resolve().parents[2] / "prompts" / "sig.refactor.v1.jinja"
    if not tpl.exists():
        return json.dumps({"instruction": f"Execute {prompt_id}", "vars": variables})
    return Template(tpl.read_text(encoding="utf-8")).render(**variables)

def _extract_json_maybe(text: str) -> Dict[str, Any]:
    text = text.strip()
    try: return json.loads(text)
    except Exception: pass
    s, e = text.find("{"), text.rfind("}")
    if s != -1 and e != -1 and e > s:
        try: return json.loads(text[s:e+1])
        except Exception: pass
    return {"code":"", "notes": f"[parse-error] expected JSON, got: {text[:400]}..."}

def llm_json(prompt_id: str, variables: Dict[str, Any], temperature: float = 0.0, seed: int | None = None) -> Dict[str, Any]:
    cfg = _effective_cfg()
    backend = cfg.get("backend","stub"); model = cfg.get("model")
    system = "You are a precise refactoring assistant. Return JSON only."
    user = _render_prompt(prompt_id, variables)

    if backend == "stub":
        return {"code": variables.get("code",""), "notes": f"[stub] no-op (seed={seed})"}

    if backend in ("openai","openai_compat"):
        base = cfg.get("openai_base_url","https://api.openai.com/v1")
        headers = {"Content-Type": "application/json"}
        if base.startswith("https://api.openai.com"):
            headers["Authorization"] = f"Bearer {os.environ.get('OPENAI_API_KEY','')}"
        payload = {"model": model, "temperature": temperature,
                   "messages":[{"role":"system","content":system},{"role":"user","content":user}]}
        if seed is not None: payload["seed"] = seed
        with httpx.Client(base_url=base, timeout=float(os.environ.get("SEAMS_HTTP_TIMEOUT","60"))) as c:
            r = c.post("/chat/completions", headers=headers, json=payload); r.raise_for_status()
            data = r.json(); content = data["choices"][0]["message"]["content"]
            return _extract_json_maybe(content)

    if backend == "anthropic":
        headers = {"x-api-key": os.environ.get("ANTHROPIC_API_KEY",""),
                   "anthropic-version":"2023-06-01","content-type":"application/json"}
        payload = {"model": model, "max_tokens": 2048, "temperature": temperature,
                   "messages":[{"role":"user","content": f"{system}\n\n{user}"}]}
        with httpx.Client(base_url="https://api.anthropic.com", timeout=float(os.environ.get("SEAMS_HTTP_TIMEOUT","60")), headers=headers) as c:
            r = c.post("/v1/messages", json=payload); r.raise_for_status()
            data = r.json(); content = "".join([p.get("text","") for p in data.get("content",[]) if p.get("type")=="text"])
            return _extract_json_maybe(content)

    return {"code": variables.get("code",""), "notes": f"[fallback] unknown backend={backend}"}

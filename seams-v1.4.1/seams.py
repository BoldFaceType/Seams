#!/usr/bin/env python
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import urllib.request, urllib.error

def _collect_local(sig_dir: Path):
    items = []
    for p in sorted(sig_dir.glob("*.json")):
        try: data = json.loads(p.read_text(encoding="utf-8"))
        except Exception: continue
        params = [{"name": k, "type": v.get("type","string"), "required": True} for k,v in (data.get("inputs") or {}).items()]
        ret = ", ".join(list((data.get("outputs") or {}).keys()) or [])
        items.append({"name": data.get("name", p.stem), "description": data.get("prompt_id",""), "params": params, "returns": ret or "object", "source": p.name})
    return items

def _collect_from_server(base_url: str):
    u = base_url.rstrip('/') + '/prompts.json'
    with urllib.request.urlopen(u, timeout=5.0) as resp:
        return json.loads(resp.read().decode('utf-8'))

def main():
    ap = argparse.ArgumentParser(prog='seams', description='Seams CLI')
    ap.add_argument('cmd', nargs='?', choices=['list-prompts','configure','run','list-graphs','run-graph'])
    ap.add_argument('--json-out', action='store_true')
    ap.add_argument('--server')
    ap.add_argument('--name')
    ap.add_argument('--graph')
    ap.add_argument('--json')
    ap.add_argument('--model')
    ap.add_argument('--backend')
    args = ap.parse_args()

    if args.cmd == 'list-prompts':
        items = None
        if args.server:
            try: items = _collect_from_server(args.server)
            except Exception as e: print(f'[warn] server fetch failed: {e}', file=sys.stderr)
        if items is None:
            here = Path(__file__).resolve().parent
            sig_dir = None
            for cand in [here / 'signatures', here.parent / 'signatures']:
                if cand.exists(): sig_dir = cand; break
            if sig_dir is None: print('[error] signatures dir not found', file=sys.stderr); sys.exit(2)
            items = _collect_local(sig_dir)
        print(json.dumps(items, indent=2) if args.json_out else "\n".join([f"- {it['name']} — " + (', '.join([p['name'] for p in it.get('params',[])]) or '(no args)') for it in items]))

    elif args.cmd == 'configure':
        from agent_core_detect import detect_and_write
        path = detect_and_write()
        print(f"[ok] wrote {path}")

    elif args.cmd == 'run':
        if not args.name: print("[error] --name required", file=sys.stderr); sys.exit(2)
        try: payload = json.loads(args.json or "{}")
        except Exception as e: print(f"[error] invalid --json: {e}", file=sys.stderr); sys.exit(2)
        if args.server:
            url = args.server.rstrip("/") + f"/tool/tool.{args.name}"
            req = urllib.request.Request(url, data=json.dumps({"payload":payload}).encode(), headers={"Content-Type":"application/json"})
            print(urllib.request.urlopen(req, timeout=30).read().decode())
        else:
            import importlib, os
            if args.backend: os.environ["SEAMS_BACKEND"] = args.backend
            if args.model: os.environ["SEAMS_MODEL"] = args.model
            if args.name != "refactor_python_function":
                print("[error] only 'refactor_python_function' available locally in this slice", file=sys.stderr); sys.exit(2)
            mod = importlib.import_module("my_agent.tools.tool_refactor")
            RefIn, fn = getattr(mod,"RefactorInput"), getattr(mod,"refactor_python_function")
            out = fn(RefIn(**payload))
            print(json.dumps(out.model_dump(), indent=2))

    elif args.cmd == 'list-graphs':
        if args.server:
            u = args.server.rstrip("/") + "/graphs.json"
            print(json.dumps(json.loads(urllib.request.urlopen(u, timeout=15).read()), indent=2))
        else:
            from agent_server import app  # ensure imports/registry
            from my_agent.graphs import list_graphs
            print(json.dumps(list_graphs(), indent=2))

    elif args.cmd == 'run-graph':
        if not args.graph: print("[error] --graph required", file=sys.stderr); sys.exit(2)
        try: payload = json.loads(args.json or "{}")
        except Exception as e: print(f"[error] invalid --json: {e}", file=sys.stderr); sys.exit(2)
        if args.server:
            url = args.server.rstrip("/") + f"/graph/{args.graph}"
            req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
            print(urllib.request.urlopen(req, timeout=60).read().decode())
        else:
            from my_agent.graphs import get_graph
            spec = get_graph(args.graph)
            InModel, runner = spec["input_model"], spec["runner"]
            inp = InModel.model_validate(payload)
            out = runner(inp)
            print(json.dumps(out.model_dump(), indent=2))

if __name__ == '__main__':
    main()

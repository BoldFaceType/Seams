# scripts/validate_signature.py
import json, sys, pathlib
REQUIRED = {"name","version","inputs","outputs","prompt_id","macro_id","agent_tool"}
p = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else "signatures/refactor_python_function.json")
data = json.loads(p.read_text(encoding="utf-8"))
missing = REQUIRED - set(data.keys())
if missing: print(f"Signature missing keys: {missing}") or sys.exit(1)
print("Signature OK")

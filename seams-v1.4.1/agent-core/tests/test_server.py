import pytest, httpx
from agent_server import app

@pytest.mark.anyio
async def test_prompts_json():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/prompts.json")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

@pytest.mark.anyio
async def test_invoke_tool():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/tool/tool.refactor_python_function", json={"payload": {"code": "def f(x):return x+1", "goal": "clarify", "constraints": ["pep8"], "seed": 1}})
        assert r.status_code == 200, r.text
        data = r.json()
        assert "code" in data and "notes" in data

import pytest, httpx
from agent_server import app

@pytest.mark.anyio
async def test_graphs_json():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/graphs.json")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert any(it["name"] == "refactor_pipeline" for it in r.json())

@pytest.mark.anyio
async def test_run_graph():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        payload = {"code": "def f(x):return x+1", "goal": "clarify", "constraints": [], "seed": 1}
        r = await c.post("/graph/refactor_pipeline", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "code" in data and "notes" in data

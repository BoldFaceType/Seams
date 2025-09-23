import pytest, httpx
from agent_server import app

@pytest.mark.anyio
async def test_lint_graph_local_path():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        payload = {"code": "def f(x):\n return 1+1\n", "linter": "none", "formatter": "none", "fix": False}
        r = await c.post("/graph/lint_pipeline", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "code" in data and "notes" in data

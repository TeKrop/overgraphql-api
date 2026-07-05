import httpx2

from app.main import create_app
from tests.fakes import FakeOverFastClient


async def test_app_serves_graphql_queries():
    app = create_app(FakeOverFastClient())
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://test") as http:
        response = await http.post("/graphql", json={"query": "{ roles { key } }"})

    assert response.status_code == 200
    assert response.json() == {"data": {"roles": [{"key": "SUPPORT"}]}}

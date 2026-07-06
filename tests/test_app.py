import httpx2
import pytest

from app.main import create_app
from tests.fakes import FakeOverFastClient


@pytest.fixture
async def http():
    app = create_app(FakeOverFastClient())
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://test") as http:
        yield http


async def test_app_serves_graphql_queries(http):
    response = await http.post("/graphql", json={"query": "{ roles { key } }"})

    assert response.status_code == 200
    assert response.json() == {"data": {"roles": [{"key": "SUPPORT"}]}}


async def test_root_serves_landing_page(http):
    response = await http.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "OverGraphQL" in response.text
    assert 'href="/graphql"' in response.text


async def test_graphql_get_serves_customized_graphiql(http):
    response = await http.get("/graphql", headers={"Accept": "text/html"})

    assert response.status_code == 200
    assert "<title>OverGraphQL API - GraphiQL</title>" in response.text
    assert "query HeroAndPlayer" in response.text

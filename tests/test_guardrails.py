"""Abuse guardrails: query depth, alias count and token count limits"""

from app.graphql.schema import schema
from app.settings import settings
from tests.fakes import FakeOverFastClient


async def execute(query: str):
    return await schema.execute(query, context_value={"client": FakeOverFastClient()})


async def test_query_depth_over_limit_is_rejected(monkeypatch):
    # The schema graph is acyclic so real queries cannot reach the default
    # limit; lower it to prove the wiring (extension lambdas read settings
    # at execution time)
    monkeypatch.setattr(settings, "max_query_depth", 1)

    result = await execute("{ maps { gamemodes { name } } }")

    assert result.errors is not None
    assert "exceeds maximum operation depth" in result.errors[0].message


async def test_too_many_aliases_is_rejected():
    aliases = " ".join(
        f"alias{i}: roles {{ name }}" for i in range(settings.max_query_aliases + 1)
    )

    result = await execute("{ " + aliases + " }")

    assert result.errors is not None
    assert "aliases" in result.errors[0].message


async def test_alias_count_at_limit_is_accepted():
    aliases = " ".join(
        f"alias{i}: roles {{ name }}" for i in range(settings.max_query_aliases)
    )

    result = await execute("{ " + aliases + " }")

    assert result.errors is None


async def test_too_many_tokens_is_rejected():
    fields = "name " * settings.max_query_tokens

    result = await execute("{ roles { " + fields + "} }")

    assert result.errors is not None
    assert "token" in result.errors[0].message

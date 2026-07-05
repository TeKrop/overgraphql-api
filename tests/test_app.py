from app.main import schema


async def test_health_query():
    result = await schema.execute("{ health }")

    assert result.errors is None
    assert result.data == {"health": "ok"}

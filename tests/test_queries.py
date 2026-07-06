from app.domain.models import Platform, PlayerGamemode
from app.domain.ports import OverFastPort
from app.graphql.schema import schema
from tests.fakes import FakeOverFastClient


async def execute(query: str, client: FakeOverFastClient | None = None, **variables):
    return await schema.execute(
        query,
        context_value={"client": client or FakeOverFastClient()},
        variable_values=variables or None,
    )


def test_fake_satisfies_port():
    fake: OverFastPort = FakeOverFastClient()

    assert fake is not None


async def test_roles_query():
    result = await execute("{ roles { key name icon description } }")

    assert result.errors is None
    assert result.data == {
        "roles": [
            {
                "key": "SUPPORT",
                "name": "Support",
                "icon": "https://example.com/support.svg",
                "description": "Support heroes heal allies.",
            },
        ],
    }


async def test_gamemodes_query():
    result = await execute("{ gamemodes { key name screenshot } }")

    assert result.errors is None
    assert result.data["gamemodes"] == [
        {
            "key": "escort",
            "name": "Escort",
            "screenshot": "https://example.com/escort.avif",
        },
    ]


async def test_maps_query_resolves_gamemode_relation():
    result = await execute("{ maps { key countryCode gamemodes { name } } }")

    assert result.errors is None
    assert result.data["maps"] == [
        {"key": "dorado", "countryCode": "MX", "gamemodes": [{"name": "Escort"}]},
    ]


async def test_heroes_query_with_nested_details():
    result = await execute(
        """
        {
          heroes {
            key
            age
            hitpoints { total }
            abilities { name video { mp4 } }
            perks { minor { name } major { name } }
            stadiumPowers { name }
            story { summary media { link } chapters { title } }
          }
        }
        """
    )

    assert result.errors is None
    hero = result.data["heroes"][0]
    assert hero["key"] == "ana"
    assert hero["age"] == 60
    assert hero["hitpoints"] == {"total": 200}
    assert hero["abilities"] == [{"name": "Sleep Dart", "video": {"mp4": "mp4"}}]
    assert hero["stadiumPowers"] is None
    assert hero["story"]["chapters"] == [{"title": "Origins"}]


async def test_heroes_query_with_key_resolves_role_relation():
    result = await execute('{ heroes(key: "ana") { name role { key name } } }')

    assert result.errors is None
    assert result.data["heroes"] == [
        {"name": "Ana", "role": {"key": "SUPPORT", "name": "Support"}},
    ]


async def test_heroes_query_with_unknown_key_returns_empty_list():
    result = await execute('{ heroes(key: "unknown") { name } }')

    assert result.errors is None
    assert result.data["heroes"] == []


async def test_key_filter_on_cached_list_entities():
    result = await execute(
        """
        {
          roles(key: "support") { name }
          gamemodes(key: "escort") { name }
          maps(key: "dorado") { name }
          missing: maps(key: "unknown") { name }
        }
        """
    )

    assert result.errors is None
    assert result.data["roles"] == [{"name": "Support"}]
    assert result.data["gamemodes"] == [{"name": "Escort"}]
    assert result.data["maps"] == [{"name": "Dorado"}]
    assert result.data["missing"] == []


async def test_player_summary_query():
    result = await execute(
        """
        {
          player(playerId: "TeKrop-2217") {
            playerId
            summary {
              username
              endorsement { level }
              competitive {
                pc { season damage { division tier } tank { division } }
                console { season }
              }
            }
          }
        }
        """
    )

    assert result.errors is None
    player = result.data["player"]
    assert player["playerId"] == "TeKrop-2217"
    assert player["summary"]["username"] == "TeKrop"
    assert player["summary"]["endorsement"] == {"level": 3}
    assert player["summary"]["competitive"]["pc"] == {
        "season": 15,
        "damage": {"division": "diamond", "tier": 3},
        "tank": None,
    }
    assert player["summary"]["competitive"]["console"] is None


async def test_player_stats_summary_query():
    result = await execute(
        """
        {
          player(playerId: "TeKrop-2217") {
            statsSummary {
              general { gamesPlayed winrate total { healing } average { deaths } }
              roles { support { kda } tank { kda } }
              heroes { hero stats { gamesWon } }
            }
          }
        }
        """
    )

    assert result.errors is None
    stats_summary = result.data["player"]["statsSummary"]
    assert stats_summary["general"]["gamesPlayed"] == 10
    assert stats_summary["general"]["total"] == {"healing": 30000}
    assert stats_summary["roles"] == {"support": {"kda": 3.5}, "tank": None}
    assert stats_summary["heroes"] == [{"hero": "ana", "stats": {"gamesWon": 6}}]


async def test_player_stats_query_passes_enum_args():
    client = FakeOverFastClient()

    result = await execute(
        """
        {
          player(playerId: "TeKrop-2217") {
            stats(platform: PC, gamemode: COMPETITIVE) {
              hero
              categories { category label stats { key label value } }
            }
          }
        }
        """,
        client=client,
    )

    assert result.errors is None
    assert client.last_stats_args == (Platform.PC, PlayerGamemode.COMPETITIVE)
    assert result.data["player"]["stats"] == [
        {
            "hero": "all-heroes",
            "categories": [
                {
                    "category": "game",
                    "label": "Game",
                    "stats": [
                        {"key": "time_played", "label": "Time Played", "value": 7200.0},
                    ],
                },
            ],
        },
    ]


async def test_player_unknown_id_returns_null_fields():
    result = await execute(
        """
        {
          player(playerId: "Unknown-1234") {
            summary { username }
            statsSummary { general { kda } }
            stats(platform: PC, gamemode: QUICKPLAY) { hero }
          }
        }
        """
    )

    assert result.errors is None
    assert result.data["player"] == {
        "summary": None,
        "statsSummary": None,
        "stats": None,
    }

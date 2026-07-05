import asyncio

import httpx2
import pytest

from app.adapters.overfast_client import OverFastClient
from app.domain.exceptions import UpstreamError
from app.domain.models import Platform, PlayerGamemode, RoleKey
from app.domain.ports import OverFastPort

ROLES = [{"key": "support", "name": "Support", "icon": "icon", "description": "desc"}]

HEROES = [
    {
        "key": "ana",
        "name": "Ana",
        "portrait": "portrait",
        "role": "support",
        "subrole": "tactician",
        "gamemodes": ["quickplay", "competitive"],
    },
]

PERK = {"name": "Perk", "description": "desc", "icon": "icon"}

HERO_ANA = {
    "description": "Sniper healer",
    "backgrounds": [{"url": "bg", "sizes": ["md", "lg"]}],
    "location": "Cairo, Egypt",
    "age": 60,
    "birthday": "1 Jan",
    "hitpoints": {"health": 200, "armor": 0, "shields": 0, "total": 200},
    "abilities": [
        {
            "name": "Sleep Dart",
            "description": "zzz",
            "icon": "icon",
            "video": {"thumbnail": "thumb", "link": {"mp4": "mp4", "webm": "webm"}},
        },
    ],
    "perks": {"minor": [PERK, PERK], "major": [PERK, PERK]},
    "stadium_powers": None,
    "story": {
        "summary": "A sniper.",
        "media": {"type": "video", "link": "youtube"},
        "chapters": [{"title": "Origins", "content": "...", "picture": "pic"}],
    },
}

STATS_SUMMARY = {
    "games_played": 10,
    "games_won": 6,
    "games_lost": 4,
    "time_played": 3600,
    "winrate": 60.0,
    "kda": 3.5,
    "total": {
        "eliminations": 100,
        "assists": 50,
        "deaths": 40,
        "damage": 50000,
        "healing": 30000,
    },
    "average": {
        "eliminations": 16.6,
        "assists": 8.3,
        "deaths": 6.6,
        "damage": 8333.3,
        "healing": 5000.0,
    },
}

PLAYER_SUMMARY = {
    "username": "TeKrop",
    "avatar": "avatar",
    "namecard": None,
    "title": "Bytefixer",
    "endorsement": {"level": 3, "frame": "frame"},
    "competitive": {
        "pc": {
            "season": 15,
            "tank": None,
            "damage": {
                "division": "diamond",
                "tier": 3,
                "role_icon": "ri",
                "rank_icon": "ki",
                "tier_icon": "ti",
            },
            "support": None,
            "open": None,
        },
        "console": None,
    },
    "last_updated_at": 1750000000,
}


def make_handler(routes: dict[str, object]):
    calls: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        if request.url.path in routes:
            return httpx2.Response(200, json=routes[request.url.path])
        return httpx2.Response(404, json={"error": "Not found"})

    return handler, calls


@pytest.fixture
async def make_client():
    clients: list[OverFastClient] = []

    def _make(routes: dict[str, object]) -> tuple[OverFastClient, list]:
        handler, calls = make_handler(routes)
        client = OverFastClient(
            base_url="http://testserver",
            static_data_ttl=3600,
            requests_per_second=10000,
            transport=httpx2.MockTransport(handler),
        )
        clients.append(client)
        return client, calls

    yield _make

    for client in clients:
        await client.aclose()


async def test_adapter_satisfies_port():
    client = OverFastClient(base_url="http://testserver", static_data_ttl=1)

    # Typed assignment makes ty statically verify the adapter satisfies the port
    port: OverFastPort = client

    assert port is client
    await client.aclose()


async def test_get_roles_parses_and_caches(make_client):
    client, calls = make_client({"/roles": ROLES})

    first = await client.get_roles()
    second = await client.get_roles()

    assert first == second
    assert first[0].key == RoleKey.SUPPORT
    assert first[0].name == "Support"
    assert len(calls) == 1


async def test_get_gamemodes_parses(make_client):
    payload = [
        {
            "key": "push",
            "name": "Push",
            "icon": "icon",
            "description": "desc",
            "screenshot": "screen",
        },
    ]
    client, _ = make_client({"/gamemodes": payload})

    gamemodes = await client.get_gamemodes()

    assert gamemodes[0].key == "push"
    assert gamemodes[0].screenshot == "screen"


async def test_get_maps_parses(make_client):
    payload = [
        {
            "key": "aatlis",
            "name": "Aatlis",
            "screenshot": "screen",
            "gamemodes": ["flashpoint"],
            "location": "Morocco",
            "country_code": None,
        },
    ]
    client, _ = make_client({"/maps": payload})

    maps = await client.get_maps()

    assert maps[0].key == "aatlis"
    assert maps[0].gamemodes == ["flashpoint"]
    assert maps[0].country_code is None


async def test_get_hero_assembles_list_entry_and_details(make_client):
    client, _ = make_client({"/heroes": HEROES, "/heroes/ana": HERO_ANA})

    hero = await client.get_hero("ana")

    assert hero is not None
    assert hero.key == "ana"
    assert hero.portrait == "portrait"
    assert hero.description == "Sniper healer"
    assert hero.abilities[0].video.mp4 == "mp4"
    assert hero.stadium_powers is None
    assert hero.story.chapters[0].title == "Origins"


async def test_get_hero_unknown_key_returns_none_without_detail_call(make_client):
    client, calls = make_client({"/heroes": HEROES})

    hero = await client.get_hero("unknown")

    assert hero is None
    assert [call.url.path for call in calls] == ["/heroes"]


async def test_get_hero_unreleased_returns_none_on_detail_404(make_client):
    client, _ = make_client({"/heroes": HEROES})

    hero = await client.get_hero("ana")

    assert hero is None


async def test_get_heroes_assembles_and_caches(make_client):
    client, calls = make_client({"/heroes": HEROES, "/heroes/ana": HERO_ANA})

    heroes = await client.get_heroes()
    await client.get_heroes()

    assert [hero.key for hero in heroes] == ["ana"]
    assert len(calls) == 2  # one list call + one detail call, then full cache hits


async def test_get_player_summary_parses_nested_ranks(make_client):
    client, _ = make_client({"/players/TeKrop-2217/summary": PLAYER_SUMMARY})

    summary = await client.get_player_summary("TeKrop-2217")

    assert summary is not None
    assert summary.username == "TeKrop"
    assert summary.endorsement.level == 3
    assert summary.competitive.pc.damage.division == "diamond"
    assert summary.competitive.pc.tank is None
    assert summary.competitive.console is None


async def test_get_player_summary_not_found_returns_none(make_client):
    client, _ = make_client({})

    summary = await client.get_player_summary("Unknown-1234")

    assert summary is None


async def test_get_player_stats_summary_flattens_heroes_dict(make_client):
    payload = {
        "general": STATS_SUMMARY,
        "roles": {"tank": None, "damage": None, "support": STATS_SUMMARY},
        "heroes": {"ana": STATS_SUMMARY},
    }
    client, _ = make_client({"/players/TeKrop-2217/stats/summary": payload})

    stats = await client.get_player_stats_summary("TeKrop-2217")

    assert stats is not None
    assert stats.general.games_played == 10
    assert stats.roles.support.winrate == 60.0
    assert [entry.hero for entry in stats.heroes] == ["ana"]
    assert stats.heroes[0].stats.total.healing == 30000


async def test_get_player_stats_sends_params_and_flattens(make_client):
    payload = {
        "all-heroes": [
            {
                "category": "game",
                "label": "Game",
                "stats": [
                    {"key": "time_played", "label": "Time Played", "value": 7200},
                ],
            },
        ],
        "ana": [
            {
                "category": "game",
                "label": "Game",
                "stats": [
                    {"key": "time_played", "label": "Time Played", "value": 3600},
                ],
            },
        ],
    }
    client, calls = make_client({"/players/TeKrop-2217/stats": payload})

    stats = await client.get_player_stats(
        "TeKrop-2217", Platform.PC, PlayerGamemode.COMPETITIVE
    )

    assert dict(calls[0].url.params) == {"platform": "pc", "gamemode": "competitive"}
    assert [entry.hero for entry in stats] == ["all-heroes", "ana"]
    assert stats[1].categories[0].category == "game"
    assert stats[1].categories[0].label == "Game"
    assert stats[1].categories[0].stats[0].key == "time_played"
    assert stats[1].categories[0].stats[0].label == "Time Played"
    assert stats[1].categories[0].stats[0].value == 3600


async def test_concurrent_static_fetches_are_coalesced(make_client):
    client, calls = make_client(
        {"/gamemodes": [], "/heroes": HEROES, "/heroes/ana": HERO_ANA}
    )

    await asyncio.gather(*(client.get_gamemodes() for _ in range(20)))
    await asyncio.gather(*(client.get_hero("ana") for _ in range(20)))

    assert [call.url.path for call in calls] == ["/gamemodes", "/heroes", "/heroes/ana"]


async def test_rate_limited_request_retries_after_delay():
    responses = [
        httpx2.Response(429, headers={"Retry-After": "0"}, json={"error": "rate"}),
        httpx2.Response(200, json=ROLES),
    ]

    def handler(_: httpx2.Request) -> httpx2.Response:
        return responses.pop(0)

    client = OverFastClient(
        base_url="http://testserver",
        static_data_ttl=3600,
        requests_per_second=10000,
        transport=httpx2.MockTransport(handler),
    )

    roles = await client.get_roles()

    assert roles[0].name == "Support"
    assert responses == []
    await client.aclose()


async def test_upstream_error_raises():
    def handler(_: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(500, json={"error": "boom"})

    client = OverFastClient(
        base_url="http://testserver",
        static_data_ttl=3600,
        transport=httpx2.MockTransport(handler),
    )

    with pytest.raises(UpstreamError, match="500"):
        await client.get_roles()

    await client.aclose()

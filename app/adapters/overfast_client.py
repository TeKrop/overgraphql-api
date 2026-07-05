"""httpx implementation of the OverFastPort, with TTL caching for semi-static data"""

import asyncio
from collections import defaultdict
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

import httpx2
from cachetools import TTLCache

from app.domain.exceptions import UpstreamError
from app.domain.models import (
    Ability,
    AbilityVideo,
    AverageStats,
    CareerStat,
    CareerStatCategory,
    CompetitiveRank,
    CompetitiveRanks,
    Endorsement,
    Gamemode,
    Hero,
    HeroBackground,
    HeroCareerStatsEntry,
    HeroStatsEntry,
    HitPoints,
    Map,
    Media,
    Perk,
    PerksContainer,
    Platform,
    PlatformCompetitiveRanks,
    PlayerGamemode,
    PlayerStatsSummary,
    PlayerSummary,
    Role,
    RoleKey,
    RolesStats,
    StatsSummary,
    Story,
    StoryChapter,
    TotalStats,
)


class OverFastClient:
    """OverFastPort adapter backed by httpx.

    Semi-static data (heroes, maps, gamemodes, roles) is cached in-process
    with a TTL; player data is always fetched from upstream, which owns
    freshness through its own SWR cache.
    """

    def __init__(
        self,
        *,
        base_url: str,
        static_data_ttl: int,
        requests_per_second: float = 20,
        transport: httpx2.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx2.AsyncClient(
            base_url=base_url, timeout=30, transport=transport
        )
        # ponytail: unbounded-enough single cache; entries = raw JSON of static
        # collections + assembled Hero objects (~50 total)
        self._cache: TTLCache[str, Any] = TTLCache(maxsize=256, ttl=static_data_ttl)
        # Coalesce concurrent fetches of the same key (GraphQL resolves list
        # items in parallel: without this, a cold cache means one upstream
        # call per item and an upstream 429)
        self._locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        # Pace request starts below OverFast's per-IP rate limit (30/s)
        self._request_interval = 1 / requests_per_second
        self._pace_lock = asyncio.Lock()
        self._next_request_at = 0.0

    async def aclose(self) -> None:
        await self._client.aclose()

    # Static entities

    async def get_roles(self) -> list[Role]:
        return [_parse_role(item) for item in await self._get_static("/roles")]

    async def get_gamemodes(self) -> list[Gamemode]:
        return [_parse_gamemode(item) for item in await self._get_static("/gamemodes")]

    async def get_maps(self) -> list[Map]:
        return [_parse_map(item) for item in await self._get_static("/maps")]

    async def get_heroes(self) -> list[Hero]:
        index = await self._heroes_index()
        heroes = await asyncio.gather(*(self.get_hero(key) for key in index))
        # An unreleased hero can be listed but have no details yet: skip it
        return [hero for hero in heroes if hero is not None]

    async def get_hero(self, key: str) -> Hero | None:
        cache_key = f"hero:{key}"
        if (cached := self._cache.get(cache_key)) is not None:
            return cached

        entry = (await self._heroes_index()).get(key)
        if entry is None:
            return None

        async with self._locks[cache_key]:
            if (cached := self._cache.get(cache_key)) is not None:
                return cached

            detail = await self._get_json(f"/heroes/{key}")
            if detail is None:
                return None

            hero = _parse_hero(entry, detail)
            self._cache[cache_key] = hero
            return hero

    # Player entity

    async def get_player_summary(self, player_id: str) -> PlayerSummary | None:
        data = await self._get_json(f"/players/{player_id}/summary")
        return None if data is None else _parse_player_summary(data)

    async def get_player_stats_summary(
        self, player_id: str
    ) -> PlayerStatsSummary | None:
        data = await self._get_json(f"/players/{player_id}/stats/summary")
        return None if data is None else _parse_player_stats_summary(data)

    async def get_player_stats(
        self,
        player_id: str,
        platform: Platform,
        gamemode: PlayerGamemode,
    ) -> list[HeroCareerStatsEntry] | None:
        data = await self._get_json(
            f"/players/{player_id}/stats",
            params={"platform": platform.value, "gamemode": gamemode.value},
        )
        return None if data is None else _parse_career_stats(data)

    # Upstream access

    async def _heroes_index(self) -> dict[str, dict[str, Any]]:
        entries = await self._get_static("/heroes")
        return {entry["key"]: entry for entry in entries}

    async def _get_static(self, path: str) -> Any:
        if (cached := self._cache.get(path)) is not None:
            return cached

        async with self._locks[path]:
            if (cached := self._cache.get(path)) is not None:
                return cached

            data = await self._get_json(path)
            if data is None:
                msg = f"OverFast API answered 404 on {path}"
                raise UpstreamError(msg)

            self._cache[path] = data
            return data

    async def _get_json(
        self, path: str, params: dict[str, str] | None = None
    ) -> Any | None:
        response = await self._paced_get(path, params)
        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            # Shared IP budget: honor Retry-After and retry once
            await asyncio.sleep(float(response.headers.get("Retry-After", "1")))
            response = await self._paced_get(path, params)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None
        if response.is_error:
            msg = f"OverFast API answered {response.status_code} on {path}"
            raise UpstreamError(msg)
        return response.json()

    async def _paced_get(
        self, path: str, params: dict[str, str] | None
    ) -> httpx2.Response:
        async with self._pace_lock:
            now = asyncio.get_running_loop().time()
            wait = self._next_request_at - now
            self._next_request_at = max(now, self._next_request_at) + (
                self._request_interval
            )
        if wait > 0:
            await asyncio.sleep(wait)
        return await self._client.get(path, params=params)


# Parsers: raw OverFast JSON -> domain models


def _opt[T](
    parse: Callable[[dict[str, Any]], T], data: dict[str, Any] | None
) -> T | None:
    return None if data is None else parse(data)


def _parse_role(data: dict[str, Any]) -> Role:
    return Role(
        key=RoleKey(data["key"]),
        name=data["name"],
        icon=data["icon"],
        description=data["description"],
    )


def _parse_gamemode(data: dict[str, Any]) -> Gamemode:
    return Gamemode(
        key=data["key"],
        name=data["name"],
        icon=data["icon"],
        description=data["description"],
        screenshot=data["screenshot"],
    )


def _parse_map(data: dict[str, Any]) -> Map:
    return Map(
        key=data["key"],
        name=data["name"],
        screenshot=data["screenshot"],
        gamemodes=list(data["gamemodes"]),
        location=data["location"],
        country_code=data.get("country_code"),
    )


def _parse_hero(entry: dict[str, Any], detail: dict[str, Any]) -> Hero:
    return Hero(
        key=entry["key"],
        name=entry["name"],
        portrait=entry["portrait"],
        role=RoleKey(entry["role"]),
        subrole=entry["subrole"],
        gamemodes=list(entry["gamemodes"]),
        description=detail["description"],
        backgrounds=[
            HeroBackground(url=item["url"], sizes=list(item["sizes"]))
            for item in detail["backgrounds"]
        ],
        location=detail["location"],
        age=detail.get("age"),
        birthday=detail.get("birthday"),
        hitpoints=_opt(_parse_hitpoints, detail.get("hitpoints")),
        abilities=[_parse_ability(item) for item in detail["abilities"]],
        perks=PerksContainer(
            minor=[_parse_perk(item) for item in detail["perks"]["minor"]],
            major=[_parse_perk(item) for item in detail["perks"]["major"]],
        ),
        stadium_powers=(
            None
            if detail.get("stadium_powers") is None
            else [_parse_perk(item) for item in detail["stadium_powers"]]
        ),
        story=_parse_story(detail["story"]),
    )


def _parse_hitpoints(data: dict[str, Any]) -> HitPoints:
    return HitPoints(
        health=data["health"],
        armor=data["armor"],
        shields=data["shields"],
        total=data["total"],
    )


def _parse_ability(data: dict[str, Any]) -> Ability:
    video = data["video"]
    return Ability(
        name=data["name"],
        description=data["description"],
        icon=data["icon"],
        video=AbilityVideo(
            thumbnail=video["thumbnail"],
            mp4=video["link"]["mp4"],
            webm=video["link"]["webm"],
        ),
    )


def _parse_perk(data: dict[str, Any]) -> Perk:
    return Perk(name=data["name"], description=data["description"], icon=data["icon"])


def _parse_story(data: dict[str, Any]) -> Story:
    media = data.get("media")
    return Story(
        summary=data["summary"],
        media=None if media is None else Media(type=media["type"], link=media["link"]),
        chapters=[
            StoryChapter(
                title=item["title"], content=item["content"], picture=item["picture"]
            )
            for item in data["chapters"]
        ],
    )


def _parse_player_summary(data: dict[str, Any]) -> PlayerSummary:
    endorsement = data.get("endorsement")
    return PlayerSummary(
        username=data["username"],
        avatar=data.get("avatar"),
        namecard=data.get("namecard"),
        title=data.get("title"),
        endorsement=(
            None
            if endorsement is None
            else Endorsement(level=endorsement["level"], frame=endorsement["frame"])
        ),
        competitive=_opt(_parse_competitive_ranks, data.get("competitive")),
        last_updated_at=data.get("last_updated_at"),
    )


def _parse_competitive_ranks(data: dict[str, Any]) -> CompetitiveRanks:
    return CompetitiveRanks(
        pc=_opt(_parse_platform_ranks, data.get("pc")),
        console=_opt(_parse_platform_ranks, data.get("console")),
    )


def _parse_platform_ranks(data: dict[str, Any]) -> PlatformCompetitiveRanks:
    return PlatformCompetitiveRanks(
        season=data.get("season"),
        tank=_opt(_parse_rank, data.get("tank")),
        damage=_opt(_parse_rank, data.get("damage")),
        support=_opt(_parse_rank, data.get("support")),
        open=_opt(_parse_rank, data.get("open")),
    )


def _parse_rank(data: dict[str, Any]) -> CompetitiveRank:
    return CompetitiveRank(
        division=data["division"],
        tier=data["tier"],
        role_icon=data["role_icon"],
        rank_icon=data["rank_icon"],
        tier_icon=data["tier_icon"],
    )


def _parse_player_stats_summary(data: dict[str, Any]) -> PlayerStatsSummary:
    roles = data.get("roles")
    return PlayerStatsSummary(
        general=_opt(_parse_stats_summary, data.get("general")),
        roles=(
            None
            if roles is None
            else RolesStats(
                tank=_opt(_parse_stats_summary, roles.get("tank")),
                damage=_opt(_parse_stats_summary, roles.get("damage")),
                support=_opt(_parse_stats_summary, roles.get("support")),
            )
        ),
        heroes=[
            HeroStatsEntry(hero=hero_key, stats=_parse_stats_summary(stats))
            for hero_key, stats in (data.get("heroes") or {}).items()
        ],
    )


def _parse_stats_summary(data: dict[str, Any]) -> StatsSummary:
    total = data["total"]
    average = data["average"]
    return StatsSummary(
        games_played=data["games_played"],
        games_won=data["games_won"],
        games_lost=data["games_lost"],
        time_played=data["time_played"],
        winrate=data["winrate"],
        kda=data["kda"],
        total=TotalStats(
            eliminations=total["eliminations"],
            assists=total["assists"],
            deaths=total["deaths"],
            damage=total["damage"],
            healing=total["healing"],
        ),
        average=AverageStats(
            eliminations=average["eliminations"],
            assists=average["assists"],
            deaths=average["deaths"],
            damage=average["damage"],
            healing=average["healing"],
        ),
    )


def _parse_career_stats(data: dict[str, Any]) -> list[HeroCareerStatsEntry]:
    return [
        HeroCareerStatsEntry(
            hero=hero_key,
            categories=[
                CareerStatCategory(
                    category=category["category"],
                    label=category["label"],
                    stats=[
                        CareerStat(
                            key=stat["key"], label=stat["label"], value=stat["value"]
                        )
                        for stat in category["stats"]
                    ],
                )
                for category in categories
            ],
        )
        for hero_key, categories in data.items()
    ]

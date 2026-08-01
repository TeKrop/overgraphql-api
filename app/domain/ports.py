"""Port interfaces (structural typing) for outbound dependencies"""

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .models import (
        CompetitiveDivision,
        Gamemode,
        Hero,
        HeroCareerStatsEntry,
        HeroStats,
        Map,
        Platform,
        PlayerGamemode,
        PlayerSearchResult,
        PlayerStatsSummary,
        PlayerSummary,
        Region,
        Role,
    )


class OverFastPort(Protocol):
    """Client interface to the upstream OverFast API.

    Single-item getters return None when the upstream answers 404
    (unknown hero key, unknown or private player).
    """

    async def get_roles(self) -> list[Role]: ...

    async def get_gamemodes(self) -> list[Gamemode]: ...

    async def get_maps(self) -> list[Map]: ...

    async def get_heroes(self) -> list[Hero]: ...

    async def get_hero(self, key: str) -> Hero | None: ...

    async def search_players(
        self, name: str, limit: int
    ) -> list[PlayerSearchResult]: ...

    async def get_player_summary(self, player_id: str) -> PlayerSummary | None: ...

    async def get_player_stats_summary(
        self, player_id: str
    ) -> PlayerStatsSummary | None: ...

    async def get_player_stats(
        self,
        player_id: str,
        platform: Platform,
        gamemode: PlayerGamemode,
    ) -> list[HeroCareerStatsEntry] | None: ...

    async def get_hero_stats(
        self,
        hero_key: str,
        platform: Platform,
        gamemode: PlayerGamemode,
        region: Region,
        map_key: str | None = None,
        competitive_division: CompetitiveDivision | None = None,
    ) -> HeroStats | None: ...

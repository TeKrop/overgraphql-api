"""Root GraphQL queries"""

from typing import Annotated

import strawberry
from strawberry.types import Info

from app.domain import models
from app.graphql.context import get_client
from app.graphql.types import Hero, Map, Player

KeyFilter = Annotated[
    str | None,
    strawberry.argument(description="Filter on a single key name"),
]


@strawberry.type(description="Root queries of the OverGraphQL API")
class Query:
    @strawberry.field(description="Roles heroes are specialized in")
    async def roles(self, info: Info, key: KeyFilter = None) -> list[models.Role]:
        roles = await get_client(info).get_roles()
        return roles if key is None else [role for role in roles if role.key == key]

    @strawberry.field(description="Gamemodes playable in Overwatch 2")
    async def gamemodes(
        self, info: Info, key: KeyFilter = None
    ) -> list[models.Gamemode]:
        gamemodes = await get_client(info).get_gamemodes()
        return (
            gamemodes
            if key is None
            else [gamemode for gamemode in gamemodes if gamemode.key == key]
        )

    @strawberry.field(description="Maps playable in Overwatch 2")
    async def maps(self, info: Info, key: KeyFilter = None) -> list[Map]:
        maps = await get_client(info).get_maps()
        if key is not None:
            maps = [map_ for map_ in maps if map_.key == key]
        return [Map.from_domain(map_) for map_ in maps]

    @strawberry.field(description="Playable Overwatch 2 heroes")
    async def heroes(self, info: Info, key: KeyFilter = None) -> list[Hero]:
        if key is not None:
            # Single lookup avoids the full per-hero details fan-out
            hero = await get_client(info).get_hero(key)
            return [] if hero is None else [Hero.from_domain(hero)]
        return [Hero.from_domain(hero) for hero in await get_client(info).get_heroes()]

    @strawberry.field(
        description="Overwatch 2 player, identified by BattleTag. "
        "Null if the player doesn't exist."
    )
    async def player(
        self,
        info: Info,
        player_id: Annotated[
            str,
            strawberry.argument(
                description="Identifier of the player: BattleTag with "
                "'#' replaced by '-' (e.g. 'TeKrop-2217')"
            ),
        ],
    ) -> Player | None:
        summary = await get_client(info).get_player_summary(player_id)
        return None if summary is None else Player.from_domain(player_id, summary)

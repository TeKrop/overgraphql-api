"""Root GraphQL queries"""

import strawberry
from strawberry.types import Info

from app.domain import models
from app.graphql.context import get_client
from app.graphql.types import Hero, Map, Player


@strawberry.type
class Query:
    @strawberry.field
    async def roles(self, info: Info, key: str | None = None) -> list[models.Role]:
        roles = await get_client(info).get_roles()
        return roles if key is None else [role for role in roles if role.key == key]

    @strawberry.field
    async def gamemodes(
        self, info: Info, key: str | None = None
    ) -> list[models.Gamemode]:
        gamemodes = await get_client(info).get_gamemodes()
        return (
            gamemodes
            if key is None
            else [gamemode for gamemode in gamemodes if gamemode.key == key]
        )

    @strawberry.field
    async def maps(self, info: Info, key: str | None = None) -> list[Map]:
        maps = await get_client(info).get_maps()
        if key is not None:
            maps = [map_ for map_ in maps if map_.key == key]
        return [Map.from_domain(map_) for map_ in maps]

    @strawberry.field
    async def heroes(self, info: Info, key: str | None = None) -> list[Hero]:
        if key is not None:
            # Single lookup avoids the full per-hero details fan-out
            hero = await get_client(info).get_hero(key)
            return [] if hero is None else [Hero.from_domain(hero)]
        return [Hero.from_domain(hero) for hero in await get_client(info).get_heroes()]

    @strawberry.field
    def player(self, player_id: str) -> Player:
        return Player(player_id=player_id)

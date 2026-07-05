"""Root GraphQL queries"""

import strawberry
from strawberry.types import Info

from app.domain import models
from app.graphql.context import get_client
from app.graphql.types import Hero, Map


@strawberry.type
class Query:
    @strawberry.field
    async def roles(self, info: Info) -> list[models.Role]:
        return await get_client(info).get_roles()

    @strawberry.field
    async def gamemodes(self, info: Info) -> list[models.Gamemode]:
        return await get_client(info).get_gamemodes()

    @strawberry.field
    async def maps(self, info: Info) -> list[Map]:
        return [Map.from_domain(map_) for map_ in await get_client(info).get_maps()]

    @strawberry.field
    async def heroes(self, info: Info) -> list[Hero]:
        return [Hero.from_domain(hero) for hero in await get_client(info).get_heroes()]

    @strawberry.field
    async def hero(self, info: Info, key: str) -> Hero | None:
        hero = await get_client(info).get_hero(key)
        return None if hero is None else Hero.from_domain(hero)

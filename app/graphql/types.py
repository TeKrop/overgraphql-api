"""GraphQL types.

Pure-data domain models are registered as strawberry types directly (no
mapping layer). Only Hero and Map are hand-written: their role/gamemodes
fields are object relations resolved through the port, not plain keys.
"""

import strawberry
from strawberry.types import Info

from app.domain import models
from app.domain.exceptions import UpstreamError
from app.graphql.context import get_client

RoleKey = strawberry.enum(models.RoleKey)
Role = strawberry.type(models.Role)
Gamemode = strawberry.type(models.Gamemode)
HeroBackground = strawberry.type(models.HeroBackground)
AbilityVideo = strawberry.type(models.AbilityVideo)
Ability = strawberry.type(models.Ability)
HitPoints = strawberry.type(models.HitPoints)
Perk = strawberry.type(models.Perk)
PerksContainer = strawberry.type(models.PerksContainer)
Media = strawberry.type(models.Media)
StoryChapter = strawberry.type(models.StoryChapter)
Story = strawberry.type(models.Story)


@strawberry.type
class Hero:
    key: str
    name: str
    portrait: str
    subrole: str
    gamemodes: list[str]
    description: str
    backgrounds: list[models.HeroBackground]
    location: str
    age: int | None
    birthday: str | None
    hitpoints: models.HitPoints | None
    abilities: list[models.Ability]
    perks: models.PerksContainer
    stadium_powers: list[models.Perk] | None
    story: models.Story
    role_key: strawberry.Private[models.RoleKey]

    @strawberry.field
    async def role(self, info: Info) -> models.Role:
        roles = await get_client(info).get_roles()
        role = next((role for role in roles if role.key == self.role_key), None)
        if role is None:
            msg = f"Role '{self.role_key}' not found upstream"
            raise UpstreamError(msg)
        return role

    @classmethod
    def from_domain(cls, hero: models.Hero) -> Hero:
        return cls(
            key=hero.key,
            name=hero.name,
            portrait=hero.portrait,
            subrole=hero.subrole,
            gamemodes=hero.gamemodes,
            description=hero.description,
            backgrounds=hero.backgrounds,
            location=hero.location,
            age=hero.age,
            birthday=hero.birthday,
            hitpoints=hero.hitpoints,
            abilities=hero.abilities,
            perks=hero.perks,
            stadium_powers=hero.stadium_powers,
            story=hero.story,
            role_key=hero.role,
        )


@strawberry.type
class Map:
    key: str
    name: str
    screenshot: str
    location: str
    country_code: str | None
    gamemode_keys: strawberry.Private[list[str]]

    @strawberry.field
    async def gamemodes(self, info: Info) -> list[models.Gamemode]:
        gamemodes = await get_client(info).get_gamemodes()
        by_key = {gamemode.key: gamemode for gamemode in gamemodes}
        return [by_key[key] for key in self.gamemode_keys if key in by_key]

    @classmethod
    def from_domain(cls, map_: models.Map) -> Map:
        return cls(
            key=map_.key,
            name=map_.name,
            screenshot=map_.screenshot,
            location=map_.location,
            country_code=map_.country_code,
            gamemode_keys=map_.gamemodes,
        )

"""GraphQL types.

Pure-data domain models are registered as strawberry types directly (no
mapping layer). Only Hero, Map and Player are hand-written: they either hold
object relations resolved through the port, or lazy per-player fetches.

All types and fields carry GraphQL descriptions (the schema is the API doc,
like Swagger on the REST side). Domain models stay strawberry-free: their
field descriptions are attached at registration time by `register()`.
"""

from typing import Annotated

import strawberry
from strawberry.types import Info

from app.domain import models
from app.domain.exceptions import UpstreamError
from app.graphql.context import get_client


def register[T](model: type[T], description: str, fields: dict[str, str]) -> type[T]:
    """Register a domain dataclass as a GraphQL type, attaching the type and
    field descriptions (raises KeyError on a description for a missing field).
    """
    # strawberry.type() returns the same class object, mutated in place
    strawberry.type(model, description=description)
    strawberry_fields = {
        field.python_name: field
        for field in model.__strawberry_definition__.fields  # ty: ignore[unresolved-attribute]
    }
    for name, field_description in fields.items():
        strawberry_fields[name].description = field_description
    return model


RoleKey = strawberry.enum(
    models.RoleKey, description="Role of a hero in the team composition"
)
Platform = strawberry.enum(models.Platform, description="Gaming platform")
PlayerGamemode = strawberry.enum(
    models.PlayerGamemode, description="Gamemode in which statistics are recorded"
)

Role = register(
    models.Role,
    "Role heroes are specialized in",
    {
        "key": "Key name of the role",
        "name": "Name of the role",
        "icon": "Icon URL of the role",
        "description": "Description of the role",
    },
)

Gamemode = register(
    models.Gamemode,
    "Gamemode playable in Overwatch 2",
    {
        "key": "Key name of the gamemode",
        "name": "Name of the gamemode",
        "icon": "Icon URL of the gamemode",
        "description": "Description of the gamemode",
        "screenshot": "URL of an example screenshot of a map for the gamemode",
    },
)

HeroBackground = register(
    models.HeroBackground,
    "Background image of a hero for a group of responsive breakpoints",
    {
        "url": "URL of the background image",
        "sizes": "Responsive breakpoint sizes for which this image is used",
    },
)

AbilityVideo = register(
    models.AbilityVideo,
    "Showcase video of an ability",
    {
        "thumbnail": "Thumbnail of the ability video",
        "mp4": "MP4 version of the ability video",
        "webm": "WebM version of the ability video",
    },
)

Ability = register(
    models.Ability,
    "Ability of a hero",
    {
        "name": "Name of the ability",
        "description": "Description of the ability",
        "icon": "Icon URL of the ability",
        "video": "Video of the ability",
    },
)

HitPoints = register(
    models.HitPoints,
    "Hit points of a hero",
    {
        "health": "Health of the hero",
        "armor": "Armor of the hero",
        "shields": "Shields of the hero",
        "total": "Total HP of the hero",
    },
)

Perk = register(
    models.Perk,
    "Perk of a hero, unlockable during a game (also used for Stadium powers)",
    {
        "name": "Name of the perk",
        "description": "Description of the perk",
        "icon": "Icon URL of the perk",
    },
)

PerksContainer = register(
    models.PerksContainer,
    "Perks of a hero, grouped by tier",
    {
        "minor": "List of minor perks",
        "major": "List of major perks",
    },
)

Media = register(
    models.Media,
    "Media concerning a hero (YouTube video, pdf story, etc.)",
    {
        "type": "Type of the media",
        "link": "Link to the media",
    },
)

StoryChapter = register(
    models.StoryChapter,
    "Chapter of the story of a hero",
    {
        "title": "Title of the chapter",
        "content": "Content of the chapter",
        "picture": "URL of the picture illustrating the chapter",
    },
)

Story = register(
    models.Story,
    "Story of a hero",
    {
        "summary": "Brief summary of the origin story of the hero",
        "media": "Media concerning the hero (YouTube video, pdf story, etc.)",
        "chapters": "List of chapters concerning the story of the hero",
    },
)

Endorsement = register(
    models.Endorsement,
    "Endorsement details of a player",
    {
        "level": "Player endorsement level, 0 if no information found",
        "frame": "URL of the endorsement frame corresponding to the level",
    },
)

CompetitiveRank = register(
    models.CompetitiveRank,
    "Competitive rank of a player for a given role",
    {
        "division": "Division of the rank",
        "tier": "Tier inside the division, lower is better",
        "role_icon": "URL of the role icon",
        "rank_icon": "URL of the division icon associated with the rank",
        "tier_icon": "URL of the tier icon associated with the rank",
    },
)

PlatformCompetitiveRanks = register(
    models.PlatformCompetitiveRanks,
    "Competitive ranks of a player on a given platform, by role",
    {
        "season": "Last competitive season played by the player on the platform",
        "tank": "Tank role rank details, null if not ranked",
        "damage": "Damage role rank details, null if not ranked",
        "support": "Support role rank details, null if not ranked",
        "open": "Open Queue rank details, null if not ranked",
    },
)

CompetitiveRanks = register(
    models.CompetitiveRanks,
    "Competitive ranks of a player, by platform",
    {
        "pc": "Ranks on PC, null if the player doesn't play on this platform",
        "console": "Ranks on console, null if the player doesn't play on this platform",
    },
)

TotalStats = register(
    models.TotalStats,
    "Total values of generic statistics",
    {
        "eliminations": "Total number of eliminations",
        "assists": "Total number of assists",
        "deaths": "Total number of deaths",
        "damage": "Total damage done",
        "healing": "Total healing done",
    },
)

AverageStats = register(
    models.AverageStats,
    "Average values of generic statistics per 10 minutes",
    {
        "eliminations": "Average eliminations per 10 minutes",
        "assists": "Average assists per 10 minutes",
        "deaths": "Average deaths per 10 minutes",
        "damage": "Average damage done per 10 minutes",
        "healing": "Average healing done per 10 minutes",
    },
)

StatsSummary = register(
    models.StatsSummary,
    "Aggregated statistics over a set of games",
    {
        "games_played": "Number of games played",
        "games_won": "Number of games won",
        "games_lost": "Number of games lost",
        "time_played": "Time played, in seconds",
        "winrate": "Winrate percentage",
        "kda": "Kills / Deaths / Assists ratio",
        "total": "Total values of generic statistics",
        "average": "Average values of generic statistics per 10 minutes",
    },
)

RolesStats = register(
    models.RolesStats,
    "Statistics summaries of a player, by role",
    {
        "tank": "Statistics on tank heroes, null if never played",
        "damage": "Statistics on damage heroes, null if never played",
        "support": "Statistics on support heroes, null if never played",
    },
)

HeroStatsEntry = register(
    models.HeroStatsEntry,
    "Statistics summary of a single hero",
    {
        "hero": "Key name of the hero",
        "stats": "Statistics summary of the hero",
    },
)

PlayerStatsSummary = register(
    models.PlayerStatsSummary,
    "Statistics summary of a player, aggregated over all platforms and gamemodes",
    {
        "general": "General statistics over all heroes, null if no game played",
        "roles": "Statistics by role, null if no game played",
        "heroes": "Statistics by hero",
    },
)

CareerStat = register(
    models.CareerStat,
    "Single career statistic",
    {
        "key": "Statistic key",
        "label": "Statistic label",
        "value": "Statistic value",
    },
)

CareerStatCategory = register(
    models.CareerStatCategory,
    "Career statistics sharing the same category",
    {
        "category": "Key name of the category",
        "label": "Label of the category",
        "stats": "List of statistics associated with the category",
    },
)

HeroCareerStatsEntry = register(
    models.HeroCareerStatsEntry,
    "Career statistics of a single hero",
    {
        "hero": "Key name of the hero, 'all-heroes' for the combined view",
        "categories": "Career statistics of the hero, grouped by category",
    },
)


@strawberry.type(description="Playable Overwatch 2 hero")
class Hero:
    key: str = strawberry.field(description="Key name of the hero")
    name: str = strawberry.field(description="Name of the hero")
    portrait: str = strawberry.field(description="Portrait picture URL of the hero")
    subrole: str = strawberry.field(description="Sub-Role of the hero")
    gamemodes: list[str] = strawberry.field(
        description="Key names of the gamemodes in which the hero is playable"
    )
    description: str = strawberry.field(description="Short description of the hero")
    backgrounds: list[models.HeroBackground] = strawberry.field(
        description="Background images of the hero, one per responsive breakpoint group"
    )
    location: str = strawberry.field(description="Location of the hero")
    age: int | None = strawberry.field(description="Age of the hero")
    birthday: str | None = strawberry.field(description="Birthday of the hero")
    hitpoints: models.HitPoints | None = strawberry.field(
        description="Hit points of the hero, null if not a playable hero"
    )
    abilities: list[models.Ability] = strawberry.field(
        description="List of abilities of the hero"
    )
    perks: models.PerksContainer = strawberry.field(
        description="Perks of the hero, grouped by tier"
    )
    stadium_powers: list[models.Perk] | None = strawberry.field(
        description="Stadium powers of the hero, null if not playable in Stadium"
    )
    story: models.Story = strawberry.field(description="Story of the hero")
    role_key: strawberry.Private[models.RoleKey]

    @strawberry.field(description="Role of the hero in the team composition")
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


@strawberry.type(
    description="Overwatch 2 player, identified by BattleTag. Profile fields "
    "are fetched with the player; statistics fields each trigger their own "
    "upstream fetch when selected."
)
class Player:
    player_id: str = strawberry.field(
        description="Identifier of the player: BattleTag with '#' replaced by '-'"
    )
    username: str = strawberry.field(
        description="Nickname of the player displayed in the game"
    )
    avatar: str | None = strawberry.field(
        description="URL of the avatar of the player, null if not found"
    )
    namecard: str | None = strawberry.field(
        description="URL of the namecard (or banner) of the player, if any"
    )
    title: str | None = strawberry.field(description="Title of the player, if any")
    endorsement: models.Endorsement | None = strawberry.field(
        description="Endorsement details of the player, null if not found"
    )
    competitive: models.CompetitiveRanks | None = strawberry.field(
        description="Competitive ranks by platform, null if never played competitive"
    )
    last_updated_at: int | None = strawberry.field(
        description="Unix timestamp of the last profile update on Blizzard side"
    )

    @strawberry.field(
        description="Statistics summary of the player, aggregated over all "
        "platforms and gamemodes. Null if the profile is private or has no game."
    )
    async def stats_summary(self, info: Info) -> models.PlayerStatsSummary | None:
        return await get_client(info).get_player_stats_summary(self.player_id)

    @strawberry.field(
        description="Career statistics of the player by hero, with labels, for "
        "a given platform and gamemode. Null if the profile is private or has "
        "no game in this context."
    )
    async def career_stats(
        self,
        info: Info,
        platform: Annotated[
            models.Platform,
            strawberry.argument(description="Platform on which stats were recorded"),
        ],
        gamemode: Annotated[
            models.PlayerGamemode,
            strawberry.argument(description="Gamemode in which stats were recorded"),
        ],
    ) -> list[models.HeroCareerStatsEntry] | None:
        return await get_client(info).get_player_stats(
            self.player_id, platform, gamemode
        )

    @classmethod
    def from_domain(cls, player_id: str, summary: models.PlayerSummary) -> Player:
        return cls(
            player_id=player_id,
            username=summary.username,
            avatar=summary.avatar,
            namecard=summary.namecard,
            title=summary.title,
            endorsement=summary.endorsement,
            competitive=summary.competitive,
            last_updated_at=summary.last_updated_at,
        )


@strawberry.type(description="Map playable in Overwatch 2")
class Map:
    key: str = strawberry.field(description="Key name of the map")
    name: str = strawberry.field(description="Name of the map")
    screenshot: str = strawberry.field(description="Screenshot URL of the map")
    location: str = strawberry.field(description="Location of the map")
    country_code: str | None = strawberry.field(
        description="Country code of the map location, null if not in a real country"
    )
    gamemode_keys: strawberry.Private[list[str]]

    @strawberry.field(description="Main gamemodes on which the map is playable")
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

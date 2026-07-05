"""Domain models: plain dataclasses for the entities exposed by the GraphQL schema.

Hero, map and gamemode keys are plain strings (not enums) on purpose: new
Blizzard content must flow through without a schema update. Only closed,
stable sets are enums.
"""

from dataclasses import dataclass
from enum import StrEnum


class RoleKey(StrEnum):
    TANK = "tank"
    DAMAGE = "damage"
    SUPPORT = "support"


class Platform(StrEnum):
    PC = "pc"
    CONSOLE = "console"


class PlayerGamemode(StrEnum):
    QUICKPLAY = "quickplay"
    COMPETITIVE = "competitive"


# Static entities


@dataclass(frozen=True, slots=True, kw_only=True)
class Role:
    key: RoleKey
    name: str
    icon: str
    description: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Gamemode:
    key: str
    name: str
    icon: str
    description: str
    screenshot: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Map:
    key: str
    name: str
    screenshot: str
    # Gamemode keys, resolved to Gamemode entities by the API layer
    gamemodes: list[str]
    location: str
    country_code: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class HeroBackground:
    url: str
    sizes: list[str]


@dataclass(frozen=True, slots=True, kw_only=True)
class AbilityVideo:
    thumbnail: str
    mp4: str
    webm: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Ability:
    name: str
    description: str
    icon: str
    video: AbilityVideo


@dataclass(frozen=True, slots=True, kw_only=True)
class HitPoints:
    health: int
    armor: int
    shields: int
    total: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Perk:
    # ponytail: also used for Stadium powers (same shape); split if they diverge
    name: str
    description: str
    icon: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PerksContainer:
    minor: list[Perk]
    major: list[Perk]


@dataclass(frozen=True, slots=True, kw_only=True)
class Media:
    type: str
    link: str


@dataclass(frozen=True, slots=True, kw_only=True)
class StoryChapter:
    title: str
    content: str
    picture: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Story:
    summary: str
    media: Media | None
    chapters: list[StoryChapter]


@dataclass(frozen=True, slots=True, kw_only=True)
class Hero:
    """Complete hero, assembled by the adapter from the heroes list
    endpoint (key, portrait, gamemodes...) and the hero details endpoint.
    """

    key: str
    name: str
    portrait: str
    role: RoleKey
    subrole: str
    gamemodes: list[str]
    description: str
    backgrounds: list[HeroBackground]
    location: str
    age: int | None
    birthday: str | None
    hitpoints: HitPoints | None
    abilities: list[Ability]
    perks: PerksContainer
    stadium_powers: list[Perk] | None
    story: Story


# Player entity


@dataclass(frozen=True, slots=True, kw_only=True)
class Endorsement:
    level: int
    frame: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetitiveRank:
    division: str
    tier: int
    role_icon: str
    rank_icon: str
    tier_icon: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PlatformCompetitiveRanks:
    season: int | None
    tank: CompetitiveRank | None
    damage: CompetitiveRank | None
    support: CompetitiveRank | None
    open: CompetitiveRank | None


@dataclass(frozen=True, slots=True, kw_only=True)
class CompetitiveRanks:
    pc: PlatformCompetitiveRanks | None
    console: PlatformCompetitiveRanks | None


@dataclass(frozen=True, slots=True, kw_only=True)
class PlayerSummary:
    username: str
    avatar: str | None
    namecard: str | None
    title: str | None
    endorsement: Endorsement | None
    competitive: CompetitiveRanks | None
    # Unix timestamp of the last profile update on Blizzard side
    last_updated_at: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class TotalStats:
    eliminations: int
    assists: int
    deaths: int
    damage: int
    healing: int


@dataclass(frozen=True, slots=True, kw_only=True)
class AverageStats:
    """Average stats per 10 minutes"""

    eliminations: float
    assists: float
    deaths: float
    damage: float
    healing: float


@dataclass(frozen=True, slots=True, kw_only=True)
class StatsSummary:
    games_played: int
    games_won: int
    games_lost: int
    time_played: int
    winrate: float
    kda: float
    total: TotalStats
    average: AverageStats


@dataclass(frozen=True, slots=True, kw_only=True)
class RolesStats:
    tank: StatsSummary | None
    damage: StatsSummary | None
    support: StatsSummary | None


@dataclass(frozen=True, slots=True, kw_only=True)
class HeroStatsEntry:
    """Stats summary of a single hero (REST dict keyed by hero, flattened to a list)"""

    hero: str
    stats: StatsSummary


@dataclass(frozen=True, slots=True, kw_only=True)
class PlayerStatsSummary:
    general: StatsSummary | None
    roles: RolesStats | None
    heroes: list[HeroStatsEntry]


@dataclass(frozen=True, slots=True, kw_only=True)
class CareerStat:
    key: str
    value: int | float


@dataclass(frozen=True, slots=True, kw_only=True)
class CareerStatCategory:
    category: str
    stats: list[CareerStat]


@dataclass(frozen=True, slots=True, kw_only=True)
class HeroCareerStatsEntry:
    """Career stats of a single hero (REST dict keyed by hero, flattened to a list)"""

    hero: str
    categories: list[CareerStatCategory]

"""Shapes of the OverFast JSON payloads, as far as the parsers read them.

These are declarations, not validation: nothing checks the JSON against them
at runtime. A key read with `data["x"]` is required, a key read with
`data.get("x")` is `NotRequired` (OverFast omits it or sends null).
"""

from typing import NotRequired, TypedDict

# Static entities


class RolePayload(TypedDict):
    key: str
    name: str
    icon: str
    description: str


class GamemodePayload(TypedDict):
    key: str
    name: str
    icon: str
    description: str
    screenshot: str


class MapPayload(TypedDict):
    key: str
    name: str
    screenshot: str
    gamemodes: list[str]
    uses: list[str]
    location: str
    country_code: NotRequired[str | None]


# Heroes


class HeroEntryPayload(TypedDict):
    """Item of the heroes list endpoint"""

    key: str
    name: str
    portrait: str | None
    role: str
    subrole: str
    gamemodes: list[str]


class HeroBackgroundPayload(TypedDict):
    url: str
    sizes: list[str]


class HitPointsPayload(TypedDict):
    health: int
    armor: int
    shields: int
    total: int


class AbilityVideoLinkPayload(TypedDict):
    mp4: str
    webm: str


class AbilityVideoPayload(TypedDict):
    thumbnail: str
    link: AbilityVideoLinkPayload


class AbilityPayload(TypedDict):
    name: str
    description: str
    icon: str
    video: AbilityVideoPayload


class PerkPayload(TypedDict):
    name: str
    description: str
    icon: str


class PerksPayload(TypedDict):
    minor: list[PerkPayload]
    major: list[PerkPayload]


class MediaPayload(TypedDict):
    type: str
    link: str


class StoryChapterPayload(TypedDict):
    title: str
    content: str
    picture: str


class StoryPayload(TypedDict):
    summary: str
    media: NotRequired[MediaPayload | None]
    chapters: list[StoryChapterPayload]


class HeroDetailPayload(TypedDict):
    """Hero details endpoint"""

    description: str
    backgrounds: list[HeroBackgroundPayload]
    location: str
    age: NotRequired[int | None]
    birthday: NotRequired[str | None]
    hitpoints: NotRequired[HitPointsPayload | None]
    abilities: list[AbilityPayload]
    perks: PerksPayload
    stadium_powers: NotRequired[list[PerkPayload] | None]
    story: StoryPayload


class HeroStatsPayload(TypedDict):
    """Item of the heroes stats endpoint"""

    hero: str
    pickrate: float
    winrate: float
    banrate: NotRequired[float | None]


# Players


class PlayerSearchResultPayload(TypedDict):
    player_id: str
    name: str
    avatar: NotRequired[str | None]
    namecard: NotRequired[str | None]
    title: NotRequired[str | None]
    is_public: NotRequired[bool | None]
    last_updated_at: NotRequired[int | None]


class PlayerSearchPayload(TypedDict):
    results: list[PlayerSearchResultPayload]


class EndorsementPayload(TypedDict):
    level: int
    frame: str


class RankPayload(TypedDict):
    division: str
    tier: int
    role_icon: str
    rank_icon: str
    tier_icon: str


class PlatformRanksPayload(TypedDict):
    season: NotRequired[int | None]
    tank: NotRequired[RankPayload | None]
    damage: NotRequired[RankPayload | None]
    support: NotRequired[RankPayload | None]
    open: NotRequired[RankPayload | None]


class CompetitiveRanksPayload(TypedDict):
    pc: NotRequired[PlatformRanksPayload | None]
    console: NotRequired[PlatformRanksPayload | None]


class PlayerSummaryPayload(TypedDict):
    username: str
    avatar: NotRequired[str | None]
    namecard: NotRequired[str | None]
    title: NotRequired[str | None]
    endorsement: NotRequired[EndorsementPayload | None]
    competitive: NotRequired[CompetitiveRanksPayload | None]
    last_updated_at: NotRequired[int | None]


class TotalStatsPayload(TypedDict):
    eliminations: int
    assists: int
    deaths: int
    damage: int
    healing: int


class AverageStatsPayload(TypedDict):
    eliminations: float
    assists: float
    deaths: float
    damage: float
    healing: float


class StatsSummaryPayload(TypedDict):
    games_played: int
    games_won: int
    games_lost: int
    time_played: int
    winrate: float
    kda: float
    total: TotalStatsPayload
    average: AverageStatsPayload


class RolesStatsPayload(TypedDict):
    tank: NotRequired[StatsSummaryPayload | None]
    damage: NotRequired[StatsSummaryPayload | None]
    support: NotRequired[StatsSummaryPayload | None]


class PlayerStatsSummaryPayload(TypedDict):
    general: NotRequired[StatsSummaryPayload | None]
    roles: NotRequired[RolesStatsPayload | None]
    heroes: NotRequired[dict[str, StatsSummaryPayload] | None]


class CareerStatPayload(TypedDict):
    key: str
    label: str
    # Upstream mixes ints and floats
    value: float


class CareerStatCategoryPayload(TypedDict):
    category: str
    label: str
    stats: list[CareerStatPayload]


# Career stats, keyed by hero
type CareerStatsPayload = dict[str, list[CareerStatCategoryPayload]]

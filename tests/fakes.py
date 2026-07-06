"""In-memory fake of the OverFastPort for query-level tests"""

from app.domain import models

SAMPLE_ROLE = models.Role(
    key=models.RoleKey.SUPPORT,
    name="Support",
    icon="https://example.com/support.svg",
    description="Support heroes heal allies.",
)

SAMPLE_GAMEMODE = models.Gamemode(
    key="escort",
    name="Escort",
    icon="https://example.com/escort.svg",
    description="Escort the payload.",
    screenshot="https://example.com/escort.avif",
)

SAMPLE_MAP = models.Map(
    key="dorado",
    name="Dorado",
    screenshot="https://example.com/dorado.jpg",
    gamemodes=["escort"],
    location="Mexico",
    country_code="MX",
)

SAMPLE_HERO = models.Hero(
    key="ana",
    name="Ana",
    portrait="https://example.com/ana.png",
    role=models.RoleKey.SUPPORT,
    subrole="tactician",
    gamemodes=["quickplay", "competitive"],
    description="Sniper healer.",
    backgrounds=[models.HeroBackground(url="https://example.com/bg.jpg", sizes=["md"])],
    location="Cairo, Egypt",
    age=60,
    birthday="1 Jan",
    hitpoints=models.HitPoints(health=200, armor=0, shields=0, total=200),
    abilities=[
        models.Ability(
            name="Sleep Dart",
            description="Puts an enemy to sleep.",
            icon="https://example.com/dart.png",
            video=models.AbilityVideo(thumbnail="thumb", mp4="mp4", webm="webm"),
        ),
    ],
    perks=models.PerksContainer(
        minor=[models.Perk(name="Minor", description="desc", icon="icon")],
        major=[models.Perk(name="Major", description="desc", icon="icon")],
    ),
    stadium_powers=None,
    story=models.Story(
        summary="A sniper.",
        media=models.Media(type="video", link="https://youtu.be/x"),
        chapters=[models.StoryChapter(title="Origins", content="...", picture="pic")],
    ),
)


SAMPLE_PLAYER_ID = "TeKrop-2217"

SAMPLE_PLAYER_SUMMARY = models.PlayerSummary(
    username="TeKrop",
    avatar="https://example.com/avatar.png",
    namecard=None,
    title="Bytefixer",
    endorsement=models.Endorsement(level=3, frame="https://example.com/frame.png"),
    competitive=models.CompetitiveRanks(
        pc=models.PlatformCompetitiveRanks(
            season=15,
            tank=None,
            damage=models.CompetitiveRank(
                division="diamond",
                tier=3,
                role_icon="ri",
                rank_icon="ki",
                tier_icon="ti",
            ),
            support=None,
            open=None,
        ),
        console=None,
    ),
    last_updated_at=1750000000,
)

SAMPLE_STATS = models.StatsSummary(
    games_played=10,
    games_won=6,
    games_lost=4,
    time_played=3600,
    winrate=60.0,
    kda=3.5,
    total=models.TotalStats(
        eliminations=100, assists=50, deaths=40, damage=50000, healing=30000
    ),
    average=models.AverageStats(
        eliminations=16.6, assists=8.3, deaths=6.6, damage=8333.3, healing=5000.0
    ),
)

SAMPLE_STATS_SUMMARY = models.PlayerStatsSummary(
    general=SAMPLE_STATS,
    roles=models.RolesStats(tank=None, damage=None, support=SAMPLE_STATS),
    heroes=[models.HeroStatsEntry(hero="ana", stats=SAMPLE_STATS)],
)

SAMPLE_CAREER_STATS = [
    models.HeroCareerStatsEntry(
        hero="all-heroes",
        categories=[
            models.CareerStatCategory(
                category="game",
                label="Game",
                stats=[
                    models.CareerStat(
                        key="time_played", label="Time Played", value=7200.0
                    ),
                ],
            ),
        ],
    ),
]


class FakeOverFastClient:
    """OverFastPort implementation serving in-memory domain objects"""

    def __init__(
        self,
        *,
        roles: list[models.Role] | None = None,
        gamemodes: list[models.Gamemode] | None = None,
        maps: list[models.Map] | None = None,
        heroes: list[models.Hero] | None = None,
    ) -> None:
        self.roles = [SAMPLE_ROLE] if roles is None else roles
        self.gamemodes = [SAMPLE_GAMEMODE] if gamemodes is None else gamemodes
        self.maps = [SAMPLE_MAP] if maps is None else maps
        self.heroes = [SAMPLE_HERO] if heroes is None else heroes
        self.last_stats_args: tuple[models.Platform, models.PlayerGamemode] | None = (
            None
        )

    async def get_roles(self) -> list[models.Role]:
        return self.roles

    async def get_gamemodes(self) -> list[models.Gamemode]:
        return self.gamemodes

    async def get_maps(self) -> list[models.Map]:
        return self.maps

    async def get_heroes(self) -> list[models.Hero]:
        return self.heroes

    async def get_hero(self, key: str) -> models.Hero | None:
        return next((hero for hero in self.heroes if hero.key == key), None)

    async def get_player_summary(self, player_id: str) -> models.PlayerSummary | None:
        return SAMPLE_PLAYER_SUMMARY if player_id == SAMPLE_PLAYER_ID else None

    async def get_player_stats_summary(
        self, player_id: str
    ) -> models.PlayerStatsSummary | None:
        return SAMPLE_STATS_SUMMARY if player_id == SAMPLE_PLAYER_ID else None

    async def get_player_stats(
        self,
        player_id: str,
        platform: models.Platform,
        gamemode: models.PlayerGamemode,
    ) -> list[models.HeroCareerStatsEntry] | None:
        self.last_stats_args = (platform, gamemode)
        return SAMPLE_CAREER_STATS if player_id == SAMPLE_PLAYER_ID else None

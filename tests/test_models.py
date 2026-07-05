from dataclasses import FrozenInstanceError

import pytest

from app.domain.models import Hero, RoleKey


def test_hero_construction_and_immutability():
    hero = Hero(
        key="ana",
        name="Ana",
        portrait="https://example.com/ana.png",
        role=RoleKey.SUPPORT,
        subrole="tactician",
        gamemodes=["quickplay", "competitive"],
    )

    assert hero.role == "support"
    with pytest.raises(FrozenInstanceError):
        hero.name = "Nope"  # ty: ignore[invalid-assignment]

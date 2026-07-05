from dataclasses import FrozenInstanceError

import pytest

from app.domain.models import Role, RoleKey


def test_model_construction_and_immutability():
    role = Role(
        key=RoleKey.SUPPORT,
        name="Support",
        icon="https://example.com/support.svg",
        description="Support heroes heal and empower their allies.",
    )

    assert role.key == "support"
    with pytest.raises(FrozenInstanceError):
        role.name = "Nope"  # ty: ignore[invalid-assignment]

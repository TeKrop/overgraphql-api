"""GraphQL context accessors (the DI seam between resolvers and the port)"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from strawberry.types import Info

    from app.domain.ports import OverFastPort


def get_client(info: Info) -> OverFastPort:
    return info.context["client"]

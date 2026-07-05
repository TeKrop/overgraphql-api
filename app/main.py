"""Application entrypoint: ASGI app wiring the schema to the OverFast client"""

from typing import TYPE_CHECKING, Any

from strawberry.asgi import GraphQL

from app.adapters.overfast_client import OverFastClient
from app.graphql.schema import schema
from app.settings import settings

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response
    from starlette.websockets import WebSocket

    from app.domain.ports import OverFastPort


class OverGraphQLApp(GraphQL[dict[str, Any], None]):
    def __init__(self, client: OverFastPort) -> None:
        super().__init__(schema)
        self.client = client

    async def get_context(
        self,
        request: Request | WebSocket,
        response: Response | WebSocket,
    ) -> dict[str, Any]:
        return {"client": self.client}


def create_app(client: OverFastPort | None = None) -> OverGraphQLApp:
    return OverGraphQLApp(
        client
        or OverFastClient(
            base_url=settings.overfast_api_url,
            static_data_ttl=settings.static_data_ttl,
            requests_per_second=settings.upstream_requests_per_second,
        )
    )


app = create_app()

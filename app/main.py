"""Application entrypoint: ASGI app wiring the schema to the OverFast client"""

from pathlib import Path
from typing import TYPE_CHECKING, Any

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Mount, Route
from strawberry.asgi import GraphQL

from app.adapters.overfast_client import OverFastClient
from app.graphql.schema import schema
from app.logging_config import configure_logging
from app.settings import settings

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response
    from starlette.websockets import WebSocket

    from app.domain.ports import OverFastPort

configure_logging()

_TEMPLATES = Path(__file__).parent / "templates"
_LANDING_HTML = (_TEMPLATES / "landing.html").read_text()
_GRAPHIQL_HTML = (_TEMPLATES / "graphiql.html").read_text()


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

    async def render_graphql_ide(self, request: Request) -> Response:
        return HTMLResponse(_GRAPHIQL_HTML)


async def landing(request: Request) -> HTMLResponse:
    return HTMLResponse(_LANDING_HTML)


def create_app(client: OverFastPort | None = None) -> Starlette:
    graphql_app = OverGraphQLApp(
        client
        or OverFastClient(
            base_url=settings.overfast_api_url,
            static_data_ttl=settings.static_data_ttl,
            requests_per_second=settings.upstream_requests_per_second,
        )
    )
    # The GraphQL app stays mounted at root (it serves any path, /graphql
    # included, without trailing-slash redirects); the landing page only
    # takes over "/"
    return Starlette(routes=[Route("/", landing), Mount("/", graphql_app)])


app = create_app()

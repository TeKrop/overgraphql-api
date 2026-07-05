"""Application entrypoint: GraphQL schema and ASGI app"""

import strawberry
from strawberry.asgi import GraphQL
from strawberry.extensions import QueryDepthLimiter

from app.settings import settings


@strawberry.type
class Query:
    # ponytail: placeholder root field, replaced by real entities in phase 4
    @strawberry.field
    def health(self) -> str:
        return "ok"


schema = strawberry.Schema(
    query=Query,
    extensions=[lambda: QueryDepthLimiter(max_depth=settings.max_query_depth)],
)

app = GraphQL(schema)

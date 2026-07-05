"""GraphQL schema assembly"""

import strawberry
from strawberry.extensions import QueryDepthLimiter

from app.graphql.query import Query
from app.settings import settings

schema = strawberry.Schema(
    query=Query,
    extensions=[lambda: QueryDepthLimiter(max_depth=settings.max_query_depth)],
)

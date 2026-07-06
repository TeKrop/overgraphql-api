"""GraphQL schema assembly"""

import strawberry
from strawberry.extensions import (
    MaxAliasesLimiter,
    MaxTokensLimiter,
    QueryDepthLimiter,
)

from app.graphql.query import Query
from app.settings import settings

# GraphiQL and introspection stay enabled: this is a public API, they are features
schema = strawberry.Schema(
    query=Query,
    extensions=[
        lambda: QueryDepthLimiter(max_depth=settings.max_query_depth),
        lambda: MaxAliasesLimiter(max_alias_count=settings.max_query_aliases),
        lambda: MaxTokensLimiter(max_token_count=settings.max_query_tokens),
    ],
)

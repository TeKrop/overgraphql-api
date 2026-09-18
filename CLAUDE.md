# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

OverGraphQL API is a pure GraphQL facade over [OverFast API](https://github.com/TeKrop/overfast-api): it never talks to Blizzard directly, doesn't parse anything itself, and reshapes OverFast's REST responses into one relational graph (Overwatch 2 heroes, roles, gamemodes, maps, player stats). Built with Strawberry GraphQL + httpx2, served by Starlette/uvicorn.

## Commands

All dev commands run inside Docker via `just` (see `justfile` / `just --list`; requires `docker`, `docker compose`, `just`). There's no host-side venv workflow — use the `just` recipes, which mount `app/`, `tests/`, `htmlcov/` into the container.

## Architecture

Hexagonal-lite, dependencies flow inward only, in `app/`:

```
main → graphql | adapters → logging_config → settings → domain
```

Enforced by import-linter (`[tool.importlinter]` in `pyproject.toml`, `uv run lint-imports`, run by `just lint` and CI): `graphql` and `adapters` never import each other (so only `main` imports the concrete adapter), `domain` imports no framework or I/O library, and there are no import cycles between sibling modules. A new top-level module under `app/` must be added to the `layers` contract (`exhaustive = true`).

- **`app/domain/`** — plain frozen dataclasses (`models.py`) and a single `typing.Protocol` port (`ports.py`, `OverFastPort`). No framework imports. Hero/map/gamemode keys are plain `str` on purpose (new Blizzard content flows through without a schema change); only closed sets (`RoleKey`, `Platform`, `PlayerGamemode`) are `StrEnum`. `exceptions.py::UpstreamError` is raised both by the adapter (unexpected upstream status) and by `graphql/types.py` (an upstream response that violates an invariant, e.g. a hero referencing a role that doesn't exist) — it always means "upstream data didn't match our assumptions," never a client-input problem.
- **`app/adapters/overfast_client.py`** — the only implementation of `OverFastPort`. Owns HTTP (httpx2), caching, request coalescing, pacing, and REST→domain parsing (`_parse_*` functions at the bottom of the file).
- **`app/graphql/`** — `query.py` (root `Query` type / resolvers), `types.py` (registers domain dataclasses as strawberry types), `context.py` (`get_client(info)` — the DI seam), `schema.py` (assembles `strawberry.Schema` with guardrail extensions).
- **`app/main.py`** — Starlette app wiring: constructs `OverFastClient` from settings, injects it as `client` in the GraphQL context, serves GraphiQL at `/graphql` and a landing page at `/`.

Resolvers only ever see `OverFastPort` through `get_client(info)`; tests swap in `tests/fakes.py::FakeOverFastClient` (in-memory, no HTTP).

### Two caching strategies (in `OverFastClient`)

- **Semi-static data** (heroes, roles, gamemodes, maps): cached in-process in a single `TTLCache` (`STATIC_DATA_TTL`, default 24h). Concurrent fetches of the same key are coalesced through a per-key `asyncio.Lock` (critical: GraphQL resolves list items in parallel, so an uncoalesced cold cache means one upstream call per item and a 429). All upstream GETs are paced below OverFast's per-IP rate limit via a shared `_pace_lock`/`_next_request_at`, with one retry on 429 honoring `Retry-After`.
- **Player data**: always fetched fresh from OverFast, which owns freshness via its own SWR cache. No caching, no batching, one player at a time.

### GraphQL type registration (`app/graphql/types.py`)

Most domain dataclasses need zero mapping code: `register(model, description, field_descriptions)` calls `strawberry.type()` on the dataclass in place and attaches descriptions after the fact — every type/field/argument in the schema is documented (the schema doc *is* the API doc, GraphiQL is the intended way to browse it, no separate docs site). Only `Hero`, `Map`, and `Player` in `types.py` are hand-written strawberry types: they hold relations resolved through the port (e.g. `Hero.role`, `Map.gamemodes`) or lazy per-field upstream fetches (e.g. `Player.stats_summary`, `Player.career_stats`), which a plain `register()` can't express.

### Guardrails

Query depth, alias count, and document token size are enforced via strawberry extensions in `schema.py`, configured from `Settings` (`MAX_QUERY_DEPTH`, `MAX_QUERY_ALIASES`, `MAX_QUERY_TOKENS`). GraphiQL and introspection are intentionally left enabled — this is a public API and they serve as its documentation. See `tests/test_guardrails.py`.

## Testing conventions

- `tests/fakes.py` provides `FakeOverFastClient` plus `SAMPLE_*` domain fixtures — construct it with overrides (`FakeOverFastClient(heroes=[...])`) rather than hitting real HTTP.
- Query-level tests build a GraphQL app with the fake client injected and assert on the raw GraphQL response.
- `ruff` per-file-ignores already account for test-only patterns (private member access, magic values, unused fixture args) and for strawberry's runtime annotation resolution in `app/graphql/` — don't work around these with noqa comments.

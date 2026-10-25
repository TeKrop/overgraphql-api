# Build arguments
ARG PYTHON_VERSION=3.15
ARG UV_VERSION=0.13.5

# Create a temporary stage to pull the uv binary
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv-stage

# Main stage
FROM python:${PYTHON_VERSION}-alpine AS main

# Copy the uv binary from the temporary stage to the main stage
COPY --from=uv-stage /uv /bin/uv

# Copy only requirements (caching in Docker layer)
COPY pyproject.toml uv.lock /code/

# Sync the project into a new environment (no dev dependencies)
WORKDIR /code
RUN uv sync --frozen --no-cache --no-dev

# Copy application code
COPY ./app /code/app

# For dev image, copy the tests and install necessary dependencies
FROM main AS dev
# grimp (import-linter) has no cp315 musl wheel yet; drop gcc once it does
RUN apk add --no-cache gcc musl-dev
RUN uv sync --frozen --no-cache
COPY ./tests /code/tests

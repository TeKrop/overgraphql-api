# Aliases

docker_compose := "docker compose"
docker_run := docker_compose + " run \
    --volume ${PWD}/app:/code/app \
    --volume ${PWD}/tests:/code/tests \
    --volume ${PWD}/htmlcov:/code/htmlcov \
    --publish 8000:8000 \
    --rm \
    app"

# print recipe names and comments as help
help:
    @just --list

# build project images
build:
    @echo "Building OverGraphQL API (dev mode)..."
    BUILD_TARGET="dev" {{ docker_compose }} build

# run OverGraphQL API application (dev mode)
start:
    @echo "Launching OverGraphQL API in dev mode with autoreload..."
    {{ docker_run }} uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# run type checker
check checker_args="":
    @echo {{ if checker_args != "" { "Running type checker on " + checker_args + "..." } else { "Running type checker..." } }}
    {{ if checker_args != "" { "uv run ty check " + checker_args } else { "uv run ty check" } }}

# run linter
lint:
    @echo "Running linter..."
    uv run ruff check --fix --exit-non-zero-on-fix

# run formatter
format:
    @echo "Running formatter..."
    uv run ruff format

# access an interactive shell inside the app container
shell:
    @echo "Running shell on app container..."
    {{ docker_run }} /bin/sh

# execute a given command inside the app container
exec command="":
    @echo "Running command on app container..."
    {{ docker_run }} {{ command }}

# run tests, pytest_args can be specified
test pytest_args="":
    @echo {{ if pytest_args != "" { "Running tests on " + pytest_args + "..." } else { "Running all tests with coverage..." } }}
    {{ docker_run }} {{ if pytest_args != "" { "uv run python -m pytest " + pytest_args } else { "uv run python -m pytest --cov app/ --cov-report html tests/" } }}

# build & run OverGraphQL API application (production mode)
up:
    @echo "Building OverGraphQL API (production mode)..."
    {{ docker_compose }} build
    @echo "Stopping OverGraphQL API and cleaning containers..."
    {{ docker_compose }} down --remove-orphans
    @echo "Launching OverGraphQL API (production mode)..."
    {{ docker_compose }} up -d

# stop the app and remove containers
down:
    @echo "Stopping OverGraphQL API and cleaning containers..."
    {{ docker_compose }} down --remove-orphans

# update lock file
lock:
    uv lock --upgrade

"""Application settings, loaded from environment variables and .env file"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base URL of the OverFast API instance used as upstream
    overfast_api_url: str = "https://overfast-api.tekrop.fr"

    # TTL (in seconds) for semi-static data (heroes, maps, gamemodes, roles)
    static_data_ttl: int = 86400

    # Pacing of upstream requests, must stay below OverFast's per-IP rate limit
    upstream_requests_per_second: float = 20

    # Maximum allowed GraphQL query depth
    max_query_depth: int = 10


settings = Settings()

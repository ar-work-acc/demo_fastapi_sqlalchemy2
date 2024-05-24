import logging
import secrets
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    ENVIRONMENT: Literal["dev", "stage", "prod", "test"] = "dev"

    API_V1_PATH: str = "/api/v1"

    # generate the key by running: openssl rand -hex 32
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    LOG_FILENAME: str = "logs/server.log"
    LOG_LEVEL: int = logging.DEBUG

    # Database URL: "postgresql+asyncpg://postgres:pw2023@localhost:5432/shop"
    DB_SCHEME: str = "postgresql+asyncpg"
    DB_SCHEME_SYNC: str = "postgresql+psycopg2"  # Celery, bad
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_SERVER: str = "localhost"
    DB_PORT: int = 5432
    DB_DATABASE: str = "shop"

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme=self.DB_SCHEME,
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_SERVER,
            port=self.DB_PORT,
            path=self.DB_DATABASE,
        )

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URL_SYNC(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme=self.DB_SCHEME_SYNC,
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_SERVER,
            port=self.DB_PORT,
            path=self.DB_DATABASE,
        )

    ADMIN_USERNAME: str = "admin@meowfish.org"
    ADMIN_PASSWORD: str = "pw2023"

    USER_USERNAME: str = ""
    USER_PASSWORD: str = ""

    CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    BROKER: str = "redis"
    REDIS_USERNAME: str = ""
    REDIS_PASSWORD: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB_BROKER: int = 0
    REDIS_DB_RESULT_BACKEND: int = 1

    @computed_field  # type: ignore[misc]
    @property
    def CELERY_BROKER_URL(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme=self.BROKER,
            username=self.REDIS_USERNAME,
            password=self.REDIS_PASSWORD,
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=str(self.REDIS_DB_BROKER),
        )

    @computed_field  # type: ignore[misc]
    @property
    def CELERY_BACKEND(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme=self.BROKER,
            username=self.REDIS_USERNAME,
            password=self.REDIS_PASSWORD,
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=str(self.REDIS_DB_RESULT_BACKEND),
        )


# use camel-case so VSCode can index for auto import
PROJECT_SETTINGS = Settings()
print(f"*** Project settings loaded for {PROJECT_SETTINGS.ENVIRONMENT}! ***")


def initialize_settings() -> None:
    """Initialize all common settings for the system."""
    logging.basicConfig(
        filename=PROJECT_SETTINGS.LOG_FILENAME,
        encoding="utf-8",
        level=PROJECT_SETTINGS.LOG_LEVEL,
        format="%(asctime)s [%(levelname)s][%(name)s]: %(message)s",
    )

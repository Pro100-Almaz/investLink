import logging
import pathlib

import decouple
from pydantic_settings import BaseSettings
from pydantic import BaseConfig

ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.parent.parent.resolve()


class BackendBaseSettings(BaseSettings):
    TITLE: str = "InvestLink Backend"
    VERSION: str = "0.1.0"
    TIMEZONE: str = "UTC"
    DESCRIPTION: str | None = None
    DEBUG: bool = False

    BACKEND_SERVER_HOST: str = decouple.config("BACKEND_SERVER_HOST", cast=str)
    BACKEND_SERVER_PORT: int = decouple.config("BACKEND_SERVER_PORT", cast=int)
    BACKEND_SERVER_WORKERS: int = decouple.config("BACKEND_SERVER_WORKERS", cast=int)
    API_PREFIX: str = "/api"
    DOCS_URL: str = "/docs"
    OPENAPI_URL: str = "/openapi.json"
    REDOC_URL: str = "/redoc"
    OPENAPI_PREFIX: str = ""

    POSTGRES_HOST: str = decouple.config("POSTGRES_HOST", cast=str)
    DB_MAX_POOL_CON: int = decouple.config("DB_MAX_POOL_CON", cast=int)
    POSTGRES_DB: str = decouple.config("POSTGRES_DB", cast=str)
    POSTGRES_PASSWORD: str = decouple.config("POSTGRES_PASSWORD", cast=str)
    DB_POOL_SIZE: int = decouple.config("DB_POOL_SIZE", cast=int)
    DB_POOL_OVERFLOW: int = decouple.config("DB_POOL_OVERFLOW", cast=int)
    POSTGRES_PORT: int = decouple.config("POSTGRES_PORT", cast=int)
    POSTGRES_SCHEMA: str = decouple.config("POSTGRES_SCHEMA", cast=str)
    DB_TIMEOUT: int = decouple.config("DB_TIMEOUT", cast=int)
    POSTGRES_USERNAME: str = decouple.config("POSTGRES_USERNAME", cast=str)
    POSTGRES_URI: str = decouple.config("POSTGRES_URI", cast=str)

    REDIS_HOST: str = decouple.config("REDIS_HOST", cast=str)
    REDIS_PORT: int = decouple.config("REDIS_PORT", cast=int)
    REDIS_DB: int = decouple.config("REDIS_DB", default=0, cast=int)
    REDIS_PASSWORD: str | None = decouple.config("REDIS_PASSWORD", default=None, cast=str)
    REDIS_POOL_SIZE: int = decouple.config("REDIS_POOL_SIZE", default=10, cast=int)
    REDIS_POOL_TIMEOUT: int = decouple.config("REDIS_POOL_TIMEOUT", default=5, cast=int)

    IS_DB_ECHO_LOG: bool = decouple.config("IS_DB_ECHO_LOG", cast=bool)
    IS_DB_FORCE_ROLLBACK: bool = decouple.config("IS_DB_FORCE_ROLLBACK", cast=bool)
    IS_DB_EXPIRE_ON_COMMIT: bool = decouple.config("IS_DB_EXPIRE_ON_COMMIT", cast=bool)

    API_TOKEN: str = decouple.config("API_TOKEN", cast=str)
    AUTH_TOKEN: str = decouple.config("AUTH_TOKEN", cast=str)
    JWT_TOKEN_PREFIX: str = decouple.config("JWT_TOKEN_PREFIX", cast=str)
    JWT_SECRET_KEY: str = decouple.config("JWT_SECRET_KEY", cast=str)
    JWT_SUBJECT: str = decouple.config("JWT_SUBJECT", cast=str)
    JWT_MIN: int = decouple.config("JWT_MIN", cast=int)
    JWT_HOUR: int = decouple.config("JWT_HOUR", cast=int)
    JWT_DAY: int = decouple.config("JWT_DAY", cast=int)
    JWT_ACCESS_TOKEN_EXPIRATION_TIME: int = JWT_MIN * JWT_HOUR * JWT_DAY

    IS_ALLOWED_CREDENTIALS: bool = decouple.config("IS_ALLOWED_CREDENTIALS", cast=bool)
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://0.0.0.0:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]

    LOGGING_LEVEL: int = logging.INFO
    LOGGERS: tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    HASHING_ALGORITHM_LAYER_1: str = decouple.config("HASHING_ALGORITHM_LAYER_1", cast=str)
    HASHING_ALGORITHM_LAYER_2: str = decouple.config("HASHING_ALGORITHM_LAYER_2", cast=str)
    HASHING_SALT: str = decouple.config("HASHING_SALT", cast=str)
    JWT_ALGORITHM: str = decouple.config("JWT_ALGORITHM", cast=str)

    POLYGON_API_KEY: str = decouple.config("POLYGON_API_KEY", cast=str)
    UPDATE_INTERVAL_MINUTES: str = decouple.config("UPDATE_INTERVAL_MINUTES", default=60, cast=int)

    class Config(BaseConfig):
        case_sensitive: bool = True
        env_file: str = f"{str(ROOT_DIR)}/.env"
        validate_assignment: bool = True

    @property
    def set_backend_app_attributes(self) -> dict[str, str | bool | None]:
        return {
            "title": self.TITLE,
            "version": self.VERSION,
            "debug": self.DEBUG,
            "description": self.DESCRIPTION,
            "docs_url": self.DOCS_URL,
            "openapi_url": self.OPENAPI_URL,
            "redoc_url": self.REDOC_URL,
            "openapi_prefix": self.OPENAPI_PREFIX,
            "api_prefix": self.API_PREFIX,
        }

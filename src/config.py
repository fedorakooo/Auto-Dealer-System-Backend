from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    """PostgreSQL connection settings."""

    POSTGRES_USER: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_NAME: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_NAME}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class LoggerSettings(BaseSettings):
    """Logging configuration settings."""

    LOGGING_CONFIG: dict[str, Any] = {}

    @classmethod
    def load_from_yaml(cls, file_path: str = "config.yaml") -> dict[str, Any]:
        """Load logging configuration from YAML file."""
        path = Path(__file__).parent.parent.parent.parent / file_path
        if not path.exists():
            return {}

        with path.open() as f:
            config = yaml.safe_load(f)
            return config.get("logger", {})


class JWTSettings(BaseSettings):
    """JWT settings."""

    PRIVATE_KEY: str = ""
    PUBLIC_KEY: str = ""
    algorithm: str = "RS256"
    access_token_expire_minutes: float = 15
    refresh_token_expire_minutes: float = 20160
    reset_password_token_expire_minutes: int = 1440

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @classmethod
    def load_from_yaml(cls, file_path: str = "config.yaml") -> dict[str, Any]:
        """Load JWT configuration from YAML file."""
        path = Path(__file__).parent.parent.parent.parent / file_path
        if not path.exists():
            return {}

        with path.open() as f:
            config = yaml.safe_load(f)
            return config.get("jwt_handler", {})


class RedisSettings(BaseSettings):
    """Redis connection settings."""

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_USER: str = ""
    REDIS_USER_PASSWORD: str = ""
    decode_responses: bool = True

    @property
    def port(self) -> int:
        return int(self.REDIS_PORT)

    @property
    def username(self) -> str:
        return self.REDIS_USER

    @property
    def password(self) -> str:
        return self.REDIS_USER_PASSWORD

    @property
    def host(self) -> str:
        return self.REDIS_HOST

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class S3Settings(BaseSettings):
    """S3 connection settings."""

    S3_ACCESS_KEY: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_BUCKET_NAME: str = "auto-dealer-media"
    S3_REGION_NAME: str = "us-east-1"

    @property
    def access_key(self) -> str:
        return self.S3_ACCESS_KEY

    @property
    def secret_key(self) -> str:
        return self.S3_SECRET_ACCESS_KEY

    @property
    def endpoint(self) -> str:
        return self.S3_ENDPOINT_URL

    @property
    def bucket_name(self) -> str:
        return self.S3_BUCKET_NAME

    @property
    def region_name(self) -> str:
        return self.S3_REGION_NAME

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class PubSubSettings(BaseSettings):
    """Redis Pub/Sub settings."""

    DATA_CHANGES_CHANNEL: str = "system:data_changes"

    @property
    def data_changes_channel(self) -> str:
        return self.DATA_CHANGES_CHANNEL

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class MongoSettings(BaseSettings):
    """MongoDB connection settings."""

    MONGO_HOST: str = "localhost"
    MONGO_PORT: str = "27017"
    MONGO_USER: str = "admin"
    MONGO_PASSWORD: str = "admin_pwd"
    MONGO_DB: str = "audit_logs"

    @property
    def url(self) -> str:
        return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(BaseSettings):
    """Application settings container."""

    postgres_settings: PostgresSettings = PostgresSettings()
    logger_settings: LoggerSettings = LoggerSettings()
    jwt_settings: JWTSettings = JWTSettings()
    redis_settings: RedisSettings = RedisSettings()
    pubsub_settings: PubSubSettings = PubSubSettings()
    s3_settings: S3Settings = S3Settings()
    mongo_settings: MongoSettings = MongoSettings()

    def __init__(self) -> None:
        super().__init__()
        self.logger_settings.LOGGING_CONFIG = LoggerSettings.load_from_yaml()
        self.jwt_settings = JWTSettings()
        jwt_config = JWTSettings.load_from_yaml()
        if jwt_config:
            for key, value in jwt_config.items():
                if hasattr(self.jwt_settings, key):
                    setattr(self.jwt_settings, key, value)


settings = Settings()

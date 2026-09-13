from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.parent.parent


class AppSettings(BaseSettings):
    IS_DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )


class BotSettings(AppSettings):
    BOT_TOKEN: str


class RedisSettings(AppSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CONNECTION_POOL_MAXSIZE: int = 10
    EXPIRE: int = 3600 * 24

    def model_post_init(self, __context) -> None:
        object.__setattr__(
            self, "REDIS_HOST", "localhost" if self.IS_DEBUG else "redis"
        )
        object.__setattr__(
            self,
            "REDIS_URL",
            f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}",
        )


class LoggingSettings(AppSettings):
    LOG_LEVEL: str = "INFO"


class DBSettings(AppSettings):
    SQLITE_URL: str = "sqlite+aiosqlite:///db.sqlite3"

    POSTGRES_DB: str = "POSTGRES_DB"
    POSTGRES_USER: str = "POSTGRES_USER"
    POSTGRES_PASSWORD: str = "POSTGRES_PASSWORD"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    def get_pg_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def model_post_init(self, __context) -> None:
        object.__setattr__(
            self,
            "DB_URL",
            self.SQLITE_URL if self.IS_DEBUG else self.get_pg_url(),
        )


class AdminSettings(AppSettings):
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str
    ADMIN_SECRET_KEY: str
    ADMIN_HOST: str = "0.0.0.0"
    ADMIN_PORT: int = 8080


class Settings(AppSettings):
    bot: BotSettings = BotSettings()
    redis: RedisSettings = RedisSettings()
    logging: LoggingSettings = LoggingSettings()
    db: DBSettings = DBSettings()
    admin: AdminSettings = AdminSettings()


settings = Settings()

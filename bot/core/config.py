from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.parent


class AppSettings(BaseSettings):
    IS_DEBUG: bool = True
    BASE_URL: str

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


class Settings:
    bot: BotSettings = BotSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()

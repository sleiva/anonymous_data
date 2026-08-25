from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    hf_token: str | None = None
    default_device: str = "auto"
    log_level: str = "INFO"
    data_dir: str = "data"
    output_dir: str = "output"
    cache_dir: str = ".cache"


@lru_cache
def get_settings() -> Settings:
    return Settings()
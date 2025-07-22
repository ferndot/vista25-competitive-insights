from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ALLOWED_ORIGINS: list[str]
    SUPABASE_URL: str
    SUPABASE_KEY: str
    OPENAI_API_KEY: str


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

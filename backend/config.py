from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/business_evaluator"
    sec_user_agent: str = "BusinessEvaluator admin@businessevaluator.com"
    cors_origins: str = "http://localhost:3000"
    redis_url: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

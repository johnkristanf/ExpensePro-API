from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    OPENAI_API_KEY: str
    DATABASE_ASYNC_DSN: str
    DATABASE_SYNC_DSN: str

settings = Settings()

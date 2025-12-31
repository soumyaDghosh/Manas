from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Manas"
    DEBUG: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    API_V1_STR: str = "/api/v1"
    REDIS_PASSWORD: str = ""
    REDIS_USERNAME: str = ""
    GEMINI_API_KEY: str
    FIREBASE_CREDENTIALS: str
    BETTER_STACK_SOURCE_TOKEN: str = ""
    BETTER_STACK_INGESTING_HOST: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # pyright: ignore[reportCallIssue]

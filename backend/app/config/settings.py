from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Manas"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_USERNAME: str = None
    GEMINI_API_KEY: str
    FIREBASE_CREDENTIALS: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

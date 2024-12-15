import os
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODE: Literal['DEV', 'TEST', 'PROD']

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    TEST_DB_HOST: str | None = None
    TEST_DB_PORT: int | None = None
    TEST_DB_USER: str | None = None
    TEST_DB_PASS: str | None = None
    TEST_DB_NAME: str | None = None

    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: str

    class Config:
        env_file = ".env" if os.getenv("MODE") == "DEV" or "TEST" else ".env-non-dev"
        extra = "allow"


settings = Settings()




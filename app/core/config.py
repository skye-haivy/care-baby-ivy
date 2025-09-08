import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    environment: str = os.getenv("ENVIRONMENT", "local")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    database_url: str | None = os.getenv("DATABASE_URL")


settings = Settings()


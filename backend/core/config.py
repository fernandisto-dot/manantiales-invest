from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Manantiales Invest API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://manantiales:manantiales123@localhost/manantiales_db"

    # JWT
    SECRET_KEY: str = "cambia-esta-clave-secreta-en-produccion-ahora"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    # Admin default (solo para primer setup)
    FIRST_ADMIN_EMAIL: str = "admin@manantiales.com"
    FIRST_ADMIN_PASSWORD: str = "admin1234"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

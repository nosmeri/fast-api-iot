from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str  # 데이터베이스 URL

    JWT_SECRET_KEY: str  # JWT 비밀 키
    JWT_EXPIRES_IN_HOURS: float  # JWT 만료 시간 (시간 단위)
    JWT_ALGORITHM: str = "HS256"  # JWT 알고리즘

    model_config = ConfigDict(env_file=".env")


settings = Settings()

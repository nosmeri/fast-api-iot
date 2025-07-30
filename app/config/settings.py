from pydantic_settings import BaseSettings, SettingsConfigDict

from utils.path import BASE_DIR


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str  # 데이터베이스 URL

    JWT_SECRET_KEY: str  # JWT 비밀 키
    JWT_ACCESS_EXPIRES_IN_HOURS: float  # JWT 액세스 토큰 만료 시간 (시간 단위)
    JWT_REFRESH_EXPIRES_IN_DAYS: float  # JWT 리프레시 토큰 만료 시간 (일 단위)
    JWT_ALGORITHM: str = "HS256"  # JWT 알고리즘

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8", case_sensitive=False
    )


# 설정 인스턴스 생성
settings = Settings()  # type: ignore

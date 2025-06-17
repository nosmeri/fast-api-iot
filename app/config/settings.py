from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str  # 데이터베이스 URL

    JWT_SECRET_KEY: str  # JWT 비밀 키
    JWT_EXPIRES_IN_HOURS: float = 24.0  # JWT 만료 시간 (시간 단위)
    JWT_ALGORITHM: str = "HS256"  # JWT 알고리즘

    # 환경 변수에서 기본값을 가져오기 위한 방법
    class Config:
        env_file = ".env"  # 환경 변수 파일을 로드

settings = Settings()
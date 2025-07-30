from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config.settings import settings

# 데이터베이스 연결 설정
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    echo=True,  # 쿼리 로그 활성화
    isolation_level="REPEATABLE_READ",  # 트랜잭션 격리 수준 설정
)

# 세션 생성
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


# 데이터베이스 모델 정의
class Base(DeclarativeBase):
    pass


# 데이터베이스 세션 생성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

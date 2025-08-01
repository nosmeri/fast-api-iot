from config.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# 비동기 데이터베이스 URL 생성 (postgresql:// → postgresql+asyncpg://)
async_database_url = settings.SQLALCHEMY_DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# 비동기 엔진 생성
async_engine = create_async_engine(
    async_database_url,
    pool_pre_ping=True,
    echo=True,  # 쿼리 로그 활성화
)

# 비동기 세션 생성
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


# 데이터베이스 모델 정의
class Base(DeclarativeBase):
    pass


# 비동기 데이터베이스 세션 생성
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

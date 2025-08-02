from typing import Any

from fastapi import HTTPException, status
from models.user import User
from schemas.user import UserResponse, user_to_response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# 모든 사용자 조회
async def get_all_users(db: AsyncSession) -> list[UserResponse]:
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [user_to_response(user) for user in users]


# 사용자 업데이트
async def db_update(
    db: AsyncSession, userid: str, update_data: dict[str, Any]
) -> UserResponse:
    result = await db.execute(select(User).filter(User.id == userid))
    user = result.scalar_one_or_none()
    if user:
        for key, value in update_data.items():
            setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        return user_to_response(user)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )


# 사용자 삭제
async def db_delete(db: AsyncSession, userid: str) -> UserResponse:
    result = await db.execute(select(User).filter(User.id == userid))
    user = result.scalar_one_or_none()
    if user:
        await db.delete(user)
        await db.commit()
        return user_to_response(user)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

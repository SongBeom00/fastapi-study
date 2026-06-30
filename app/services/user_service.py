from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.user_schema import UserResponse, UserProfileUpdate


async def get_user(conn: AsyncConnection, user_id: int) -> UserResponse:
    """
    user_id로 단일 사용자를 조회한다.
    (users 테이블: id, name, email, tier, created_at 가정)
    """
    try:
        query = text("""
            SELECT id, name, email, tier, created_at
            FROM users
            WHERE id = :user_id
        """)
        result = await conn.execute(query, {"user_id": user_id})
        row = result.fetchone()

        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        return UserResponse(
            id=row.id,
            name=row.name,
            email=row.email,
            tier=row.tier,
            created_at=row.created_at,
        )

    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="사용자 조회 중 DB 오류가 발생했습니다."
        )


async def update_user(
    conn: AsyncConnection,
    user_id: int,
    data: UserProfileUpdate,
) -> UserResponse:
    """
    user_id에 해당하는 사용자의 프로필(name, email, tier)을 수정한다.
    """
    try:
        async with conn.begin():  # commit 보장
            query = text("""
                UPDATE users
                SET name = :name,
                    email = :email,
                    tier = :tier
                WHERE id = :id
                RETURNING id, name, email, tier, created_at
            """)

            result = await conn.execute(
                query,
                {
                    "id": user_id,
                    "name": data.name,
                    "email": data.email,
                    "tier": data.tier,
                }
            )

            row = result.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="수정할 사용자가 존재하지 않습니다."
                )

        return UserResponse(
            id=row.id,
            name=row.name,
            email=row.email,
            tier=row.tier,
            created_at=row.created_at,
        )

    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="사용자 수정 중 DB 오류가 발생했습니다."
        )

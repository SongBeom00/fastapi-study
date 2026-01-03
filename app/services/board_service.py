from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import text, Connection
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.exc import SQLAlchemyError
from typing import List

from app.schemas.board_schema import BoardData, BoardCreate, BoardUpdate, BoardDelete


async def get_all_boards(conn: AsyncConnection) -> List:
    try:
        query = text("""
        SELECT id, title, content, created_at, updated_at, created_by, updated_by, is_deleted FROM board where is_deleted = FALSE;
        """)
        result = await conn.execute(query)
        rows = result.fetchall()
        all_posts =[BoardData(id=row.id,
                              title=row.title,
                              content=row.content,
                              created_by=row.created_by,
                              updated_by=row.updated_by,
                              created_at=row.created_at,
                              updated_at=row.updated_at,
                              is_deleted=row.is_deleted
                              ) for row in rows]
        return all_posts
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="요청하신 서비스가 잠시 내부적으로 문제가 발생하였습니다.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="알 수 없는 이유로 서비스 오류가 발생하였습니다.")


async def create_board(
    conn: AsyncConnection,
    data: BoardCreate,
    user_id: int,
) -> BoardData:
    try:
        async with conn.begin():
            query = text("""
                INSERT INTO board (
                    title,
                    content,
                    created_by,
                    updated_by
                )
                VALUES (
                    :title,
                    :content,
                    :created_by,
                    :updated_by
                )
                RETURNING
                    id,
                    title,
                    content,
                    created_by,
                    updated_by,
                    created_at,
                    updated_at,
                    is_deleted
            """)

            result = await conn.execute(
                query,
                {
                    "title": data.title,
                    "content": data.content,
                    "created_by": user_id,
                    "updated_by": user_id,
                }
            )

            row = result.fetchone()

        return BoardData(
            id=row.id,
            title=row.title,
            content=row.content,
            created_by=row.created_by,
            updated_by=row.updated_by,
            created_at=row.created_at,
            updated_at=row.updated_at,
            is_deleted=row.is_deleted,
        )

    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="게시글 등록 중 DB 오류가 발생했습니다."
        )


async def update_board(
    conn: AsyncConnection,
    data: BoardUpdate,
    user_id: int,
) -> BoardData:
    try:
        async with conn.begin(): # commit 보장
            query = text("""
                UPDATE board
                SET title = :title,
                    content = :content
                WHERE id = :id
                AND is_deleted = FALSE
                RETURNING
                    id,
                    title,
                    content,
                    created_by,
                    updated_by,
                    created_at,
                    updated_at,
                    is_deleted
            """)

            result = await conn.execute(
                query,
                {
                    "id" : data.id,
                    "title": data.title,
                    "content": data.content,
                    "updated_by": user_id,
                }
            )

            row = result.fetchone()

            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="수정할 게시글이 존재하지 않습니다."
                )

        return BoardData(
            id=row.id,
            title=row.title,
            content=row.content,
            created_by=row.created_by,
            updated_by=row.updated_by,
            created_at=row.created_at,
            updated_at=row.updated_at,
            is_deleted=row.is_deleted,
        )

    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="게시글 수정 중 DB 오류가 발생했습니다."
        )


async def soft_delete_board(
    conn: AsyncConnection,
    data: BoardDelete,
    user_id: int,
) -> None:
    try:
        async with conn.begin():
            query = text("""
                UPDATE board
                SET
                    is_deleted = TRUE,
                    updated_by = :updated_by,
                    updated_at = NOW()
                WHERE id = :id
                  AND is_deleted = FALSE
            """)

            result = await conn.execute(
                query,
                {
                    "id": data.id,
                    "updated_by": user_id,
                }
            )

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="삭제할 게시글이 존재하지 않습니다."
                )

    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="게시글 삭제 중 DB 오류가 발생했습니다."
        )
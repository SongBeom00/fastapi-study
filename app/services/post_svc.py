from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import text, Connection
from sqlalchemy.exc import SQLAlchemyError
from typing import List

from app.schemas.post_schema import BoardData


async def get_all_boards(conn: Connection) -> List:
    try:
        query = """
        SELECT id, title, content, created_by, updated_by FROM board;
        """
        result = await conn.execute(text(query))
        all_posts =[BoardData(id=row.id,
                              title=row.title,
                              content=row.content,
                              created_by=row.created_by,
                              updated_by=row.updated_by,
                              created_at=row.created_at,
                              updated_at=row.updated_at
                              ) for row in result]
        result.close()
        return all_posts
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="요청하신 서비스가 잠시 내부적으로 문제가 발생하였습니다.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="알 수 없는 이유로 서비스 오류가 발생하였습니다.")
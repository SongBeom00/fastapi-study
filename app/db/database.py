from sqlalchemy import create_engine, Connection
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool, NullPool
from contextlib import contextmanager
from fastapi import status
from fastapi.exceptions import HTTPException
from dotenv import load_dotenv
import os


load_dotenv()

DATABASE_CONN = os.getenv('DATABASE_CONN')
if not DATABASE_CONN:
    raise RuntimeError('DATABASE_CONN is not set')

engine: AsyncEngine = create_async_engine(DATABASE_CONN, #echo=True,
                                          #poolclass=NullPool, # Connection Pool 사용하지 않음
                                          pool_size=10, max_overflow=0,
                                          pool_recycle=300
                                          )

async def direct_get_conn():
    """
    즉시 커넥션 반환
    DB 커넥션 하나를 그대로 반환
    호출한 쪽에사 반드시 await conn.close()를 호출해야 합니다.

    :return: conn
    """
    conn = None
    try:
        conn = await engine.connect()
        return conn

    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='요청하신 서비스가 잠시 내부적으로 문제가 발생했습니다.')
async def context_get_conn():
    conn = None
    try:
        conn = await engine.connect()
        yield conn
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='요청하신 서비스가 잠시 내부적으로 문제가 발생했습니다.')
    finally:
        if conn:
            await conn.close()
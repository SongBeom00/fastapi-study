from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy import text, Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.util import await_only

from app.db import database
from app.schemas.board_schema import BoardData, BoardResponse, BoardCreate, BoardUpdate, BoardDelete
from app.services import board_service


# router 생성
router = APIRouter(prefix='/boards', tags=['boards'])

@router.get("/", response_model=list[BoardResponse])
async def get_post_list(
    request: Request,
    conn: AsyncConnection = Depends(database.context_get_conn)
):
    return await board_service.get_all_boards(conn)

@router.post("/", response_model=BoardResponse)
async def create_board(
        data: BoardCreate,
        conn: AsyncConnection = Depends(database.context_get_conn)
):

    return await board_service.create_board(conn=conn, data=data, user_id=1)

@router.put("/", response_model=BoardResponse)
async def update_board(
        data: BoardUpdate,
        conn: AsyncConnection = Depends(database.context_get_conn)
):
    return await board_service.update_board(conn=conn, data=data, user_id=1)

@router.post("/soft-delete", response_model=BoardResponse)
async def soft_delete_board(
        data: BoardDelete,
        conn: AsyncConnection = Depends(database.context_get_conn)
):
    await board_service.soft_delete_board(conn=conn, data=data, user_id=1)
    return {"message": "게시글이 삭제되었습니다."}
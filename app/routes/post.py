from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy import text, Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection

from ..db import database
from ..schemas.post_schema import BoardData
from ..services import post_svc

# router 생성
router = APIRouter(prefix='/boards', tags=['boards'])

@router.get("/", response_model=list[BoardData])
async def get_post_list(
    request: Request,
    conn: AsyncConnection = Depends(database.context_get_conn)
):
    return await post_svc.get_all_posts(conn)

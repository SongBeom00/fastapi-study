import json

from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db import database
from app.schemas.user_schema import UserResponse, UserProfileUpdate
from app.services import user_service

# router 생성
router = APIRouter(prefix='/users', tags=['users'])

# 캐시 만료 시간(초)
CACHE_TTL = 60 * 5


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    request: Request,
    conn: AsyncConnection = Depends(database.context_get_conn),
):
    rd = request.app.state.redis
    cache_key = f"user:profile:{user_id}"

    # 1. 레디스에서 캐시 확인
    cached_user = await rd.get(cache_key)
    if cached_user:
        # 캐시 Hit
        print(f"🚀 Cache Hit! (user_id: {user_id})")
        # Redis에 저장된 JSON 문자열을 파이썬 딕셔너리로 변환하여 반환
        return json.loads(cached_user)

    # 2. 캐시 Miss → DB 조회
    print(f"🐌 Cache Miss! Fetching from DB... (user_id: {user_id})")
    user_data = await user_service.get_user(conn, user_id)

    # 3. 조회 결과를 캐시에 저장 (TTL 적용)
    await rd.set(cache_key, json.dumps(user_data, default=str), ex=CACHE_TTL)

    return user_data

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_profile(
    user_id: int,
    profile: UserProfileUpdate,
    request: Request,
    conn: AsyncConnection = Depends(database.context_get_conn),
):
    rd = request.app.state.redis
    cache_key = f"user:profile:{user_id}"

    # 1. DB 수정 (없는 사용자면 서비스에서 404)
    updated_user = await user_service.update_user(conn, user_id, profile)

    # 2. 캐시 무효화 → 다음 GET 요청 때 최신 데이터를 다시 캐싱
    await rd.delete(cache_key)

    return updated_user




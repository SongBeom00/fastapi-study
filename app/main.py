import uvicorn
from fastapi import FastAPI, Query, Request
from enum import Enum
from pydantic import BaseModel
from app.routes import board, user
from typing import Annotated
import logging
from contextlib import asynccontextmanager
import redis.asyncio as redis # 비동기 모듈을 임포트합니다

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 서버 시작 시 : Redis 연결 풀(Pool) 생성 후 app.state 저장
    app.state.redis = redis.from_url("redis://localhost:6379/0", decode_responses=True)
    print("✅ Redis 연결 성공!")

    yield # 서버 시작 시 yield 위의 코드가 실행되고, 서버 종료 시 yield 아래의 코드가 실행됩니다.

    # 2. 서버 종료 시 : Redis 연결 안전하게 해제
    await app.state.redis.aclose()
    print("❌ Redis 연결 해제!")

app = FastAPI(lifespan=lifespan)

# 라우터 등록
app.include_router(board.router)
app.include_router(user.router)

@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(title="Query string", min_length=3)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@app.post("/items/{item_id}")
async def set_item(item_id: str, value: str, request: Request):
    """
    Redis에 데이터를 저장합니다 (SET)
    :param item_id:
    :param value:
    :param request:
    :return:
    """
    rd = request.app.state.redis
    key = f"item:{item_id}"

    await rd.set(key, value)

    return {"message" : "Data saved to Redis successfully", "key" : key, "value" : value}

@app.get("/items/{item_id}")
async def get_item(item_id: str, request: Request):
    """
    Redis에서 데이터를 조회합니다. (GET)
    :param item_id:
    :param request:
    :return:
    """
    rd = request.app.state.redis
    key = f"item:{item_id}"

    # await rd.get(키)
    result = await rd.get(key)

    # Redis에 데이터가 없으면 None을 반환
    if result is None:
        return {"error" : "Item not found in Redis"}

    return {"key" : key, "value" : result}

# @app.get("/items/{item_id}")
# async def read_item(item_id: str, q: str | None = None):
#     if q:
#         return {"item_id" : item_id, "q" : q}
#     return {"item_id": item_id}

# @app.get("/items/{item_id}")
# async def read_item(item_id: str, q: str | None = None, short: bool = False):
#     item = {"item_id" : item_id}
#     if q:
#         item.update({"q" : q})
#     if not short:
#         item.update({"description" : "This is an amazing item that has a long description"})
#     return item

# @app.post("/items/")
# async def create_item(item: Item):
#     return item

# @app.put("/items/{item_id}")
# async def update_item(item_id: str, item: Item):
#     return {"item_id": item_id, **item.dict()}
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path" : file_path}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host='0.0.0.0', reload=True)



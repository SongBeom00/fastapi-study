import uvicorn
from fastapi import FastAPI, Query
from enum import Enum
from pydantic import BaseModel
from app.routes import board
from typing import Annotated
import logging
app = FastAPI()

# 라우터 등록
app.include_router(board.router)

@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(title="Query string", min_length=3)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results



# @app.get("/items/{item_id}")
# async def read_item(item_id: str, q: str | None = None):
#     if q:
#         return {"item_id" : item_id, "q" : q}
#     return {"item_id": item_id}
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id" : item_id}
    if q:
        item.update({"q" : q})
    if not short:
        item.update({"description" : "This is an amazing item that has a long description"})
    return item

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



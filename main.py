# app.py
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, BackgroundTasks
import asyncio
import time

app = FastAPI(title="RESTful API Example")

# In-memory store
items_db = {}

# Pydantic model
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

#  POST - Create item
@app.post("/v1/items", status_code=201)
def create_item(item: Item):
    item_id = len(items_db) + 1
    items_db[item_id] = item
    return {
        "message": "Item created",
        "id": item_id,
        "_links": {
            "self": f"/v1/items/{item_id}",
            "update": f"/v1/items/{item_id}",
            "delete": f"/v1/items/{item_id}"
        }
    }

#  GET - Read item
@app.get("/v1/items/{item_id}")
def get_item(item_id: int):
    item = items_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "item": item,
        "_links": {
            "self": f"/v1/items/{item_id}",
            "update": f"/v1/items/{item_id}",
            "delete": f"/v1/items/{item_id}"
        }
    }

#  PUT - Full update
@app.put("/v1/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = item
    return {"message": "Item updated", "item": item}

#  PATCH - Partial update
@app.patch("/v1/items/{item_id}")
def patch_item(item_id: int, item: Item):
    existing = items_db.get(item_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    update_data = item.dict(exclude_unset=True)
    updated = existing.copy(update=update_data)
    items_db[item_id] = updated
    return {"message": "Item partially updated", "item": updated}

#  DELETE - Delete item
@app.delete("/v1/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return {"message": "Item deleted"}

# Query String Versioning
@app.get("/items")
def get_items_by_query(version: Optional[str] = "1"):
    return {"version": version, "items": items_db}

# Header Versioning
@app.get("/header-items")
def get_items_by_header(x_api_version: Optional[str] = Header(default="1")):
    return {"version": x_api_version, "items": items_db}

# Media Type Versioning
@app.get("/media-items")
def get_items_by_media_type(request: Request):
    media_type = request.headers.get("accept")
    return {"version_from_accept_header": media_type, "items": items_db}

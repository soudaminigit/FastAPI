from fastapi import FastAPI, HTTPException, Request, Header, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel
import logging
import time

app = FastAPI()

# ========== Slide 1: Data + Idempotency ==========

# In-memory DB simulation
orders = {
    2: {"orderID": 2, "productID": 4, "quantity": 2, "orderValue": 10.00}
}

class Order(BaseModel):
    productID: int
    quantity: int
    orderValue: float

# POST: Create new order (non-idempotent)
@app.post("/orders", status_code=201)
def create_order(order: Order):
    new_id = max(orders.keys()) + 1
    orders[new_id] = {"orderID": new_id, **order.dict()}
    return {"message": "Order created", "id": new_id}

# PUT: Update order (idempotent)
@app.put("/orders/{order_id}")
def update_order(order_id: int, order: Order):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    orders[order_id] = {"orderID": order_id, **order.dict()}
    return {"message": "Order updated", "order": orders[order_id]}

# GET: Retrieve order with client-side caching
@app.get("/orders/{order_id}")
def get_order(order_id: int):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return JSONResponse(
        content=orders[order_id],
        headers={
            #"Cache-Control": "max-age=600, private",
            "Cache-Control": "max-age=600, public",
            "Content-Type": "application/json"
        }
    )

# ========== Slide 3: Large requests, Pagination, Async ==========

@app.get("/orders/")
async def list_orders(skip: int = 0, limit: int = 10):
    return list(orders.values())[skip:skip + limit]

# Simulate async long-running task
@app.get("/orders/slow/{order_id}")
async def get_order_slow(order_id: int):
    import asyncio
    await asyncio.sleep(2)  # simulate delay
    return orders.get(order_id, {"error": "not found"})

# ========== Slide 4: Logging & Rate Throttling (Simulated) ==========
# Middleware
#Run before the request reaches your route

#Run after the response is returned by the route

#Allow you to inspect, modify, or log requests and responses


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger = logging.getLogger("uvicorn")
    logger.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    return response

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
# ========== Slide 5: Basic Auth ==========

def fake_auth(x_token: Optional[str] = Header(None)):
    if x_token != "secret-token":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/secure/orders", dependencies=[Depends(fake_auth)])
def get_secure_orders():
    return orders

# ========== Slide 6 & 7: Monitoring & Testing Ready ==========

@app.get("/status")
def health_check(user_agent: Optional[str] = Header(None)):
    return {
        "status": "ok",
        "user_agent": user_agent
    }

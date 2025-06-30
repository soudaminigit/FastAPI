# app.py
from fastapi import FastAPI, BackgroundTasks
import asyncio
import time

app = FastAPI()

# Synchronous endpoint (for comparison)
@app.get("/ping")
def ping():
    return {"message": "pong", "mode": "sync"}

# Asynchronous endpoint using asyncio
@app.get("/async-task")
async def async_task():
    await asyncio.sleep(5)  # Simulates a long task
    return {"message": "Async task completed after 5 seconds"}

# Background task
def write_log(task_name: str):
    time.sleep(3)
    with open("log.txt", "a") as f:
        f.write(f"{task_name} completed at {time.strftime('%X')}\n")

@app.get("/background-task")
async def run_background_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(write_log, "background-task")
    return {"message": "Background task scheduled"}

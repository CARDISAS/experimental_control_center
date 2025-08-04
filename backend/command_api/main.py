import os, json, asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from pymodbus.client import AsyncModbusTcpClient

MCU_HOST = os.getenv("MCU_HOST", "esp32.local")
MCU_PORT = int(os.getenv("MCU_PORT", "502"))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

app = FastAPI(title="Command API")
r = redis.from_url(REDIS_URL)

@app.get("/api/latest")
async def latest():
    data = await r.get("latest")
    return JSONResponse(content=json.loads(data) if data else {})

@app.post("/api/valves/{vid}")
async def set_valve(vid: int, state: bool):
    async with AsyncModbusTcpClient(MCU_HOST, MCU_PORT) as client:
        await client.write_coil(vid, state, unit=1)
    return {"valve": vid, "state": state}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await r.get("latest")
            if data:
                await ws.send_text(data.decode())
            await asyncio.sleep(1)
    except Exception:
        await ws.close()

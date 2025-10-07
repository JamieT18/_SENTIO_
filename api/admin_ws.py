"""
Admin WebSocket endpoint for real-time system updates
"""
from fastapi import WebSocket, APIRouter
from fastapi.responses import JSONResponse
import asyncio
import os

router = APIRouter()

ADMIN_TOKEN = os.environ.get('SENTIO_ADMIN_TOKEN', 'admin-token')

@router.websocket("/ws/admin")
async def admin_ws(websocket: WebSocket):
    await websocket.accept()
    token = None
    try:
        token = await websocket.receive_text()
    except Exception:
        await websocket.close(code=4001)
        return
    if token != ADMIN_TOKEN:
        await websocket.close(code=4003)
        return
    try:
        while True:
            # Simulate sending system status/logs every 2s
            status = {
                "status": "healthy",
                "cpu": 12.5,
                "memory": 1024,
                "active_users": 42,
                "timestamp": str(asyncio.get_event_loop().time())
            }
            logs = [
                "2025-10-06 05:12:42 - INFO - System healthy",
                "2025-10-06 05:10:21 - WARN - High latency detected",
                "2025-10-06 05:09:10 - ERROR - Test failure in trading engine",
            ]
            await websocket.send_json({"status": status, "logs": logs})
            await asyncio.sleep(2)
    except Exception:
        await websocket.close()

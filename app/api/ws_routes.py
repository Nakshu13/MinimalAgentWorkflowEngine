from fastapi import APIRouter, WebSocket
from app.core.ws_manager import ws_manager

router = APIRouter()


@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except Exception:
        ws_manager.disconnect(websocket)

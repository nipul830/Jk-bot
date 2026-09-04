import os
from typing import Any
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="RoyalInstitute Secure Bridge", version="0.1.0")
TOKEN = os.getenv("ROYAL_BRIDGE_TOKEN", "")

class OrderRequest(BaseModel):
    symbol: str
    side: str
    volume: float
    sl: float | None = None
    tp: float | None = None

state: dict[str, Any] = {
    "mt5_connected": False,
    "engine_running": False,
    "account": {"balance": 0.0, "equity": 0.0},
    "positions": [],
    "signals": [],
}

def auth(authorization: str | None = Header(default=None)):
    if not TOKEN:
        raise HTTPException(503, "Bridge token is not configured")
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(401, "Unauthorized")

@app.get("/health")
def health():
    return {"ok": True, "service": "royalinstitute-bridge"}

@app.get("/api/state", dependencies=[Depends(auth)])
def get_state():
    return state

@app.post("/api/start", dependencies=[Depends(auth)])
def start():
    state["engine_running"] = True
    return {"ok": True, "engine_running": True}

@app.post("/api/stop", dependencies=[Depends(auth)])
def stop():
    state["engine_running"] = False
    return {"ok": True, "engine_running": False}

@app.post("/api/orders", dependencies=[Depends(auth)])
def order(req: OrderRequest):
    # Execution adapter is intentionally not implemented here.
    # Connect this endpoint to the original MT5 engine on the VPS.
    raise HTTPException(501, "MT5 execution adapter not configured")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("ROYAL_BRIDGE_HOST", "127.0.0.1"), port=int(os.getenv("ROYAL_BRIDGE_PORT", "8765")))

import os
from typing import Any
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

app = FastAPI(title="RoyalInstitute MT5 Bridge", version="0.2.0")
TOKEN = os.getenv("ROYAL_BRIDGE_TOKEN", "")
MT5_PATH = os.getenv("MT5_PATH") or None

class OrderRequest(BaseModel):
    symbol: str
    side: str
    volume: float
    sl: float | None = None
    tp: float | None = None
    deviation: int = 20
    magic: int = 830007


def auth(authorization: str | None = Header(default=None)):
    if not TOKEN:
        raise HTTPException(503, "Bridge token is not configured")
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(401, "Unauthorized")


def require_mt5():
    if mt5 is None:
        raise HTTPException(503, "MetaTrader5 Python package is not installed")
    if not mt5.initialize(path=MT5_PATH):
        code, message = mt5.last_error()
        raise HTTPException(503, f"MT5 initialize failed: {code} {message}")


def position_dict(p: Any) -> dict[str, Any]:
    return {
        "ticket": int(p.ticket), "symbol": p.symbol, "type": int(p.type),
        "volume": float(p.volume), "price_open": float(p.price_open),
        "price_current": float(p.price_current), "sl": float(p.sl),
        "tp": float(p.tp), "profit": float(p.profit),
        "magic": int(p.magic), "time": int(p.time)
    }


@app.get("/health")
def health():
    return {"ok": True, "service": "royalinstitute-mt5-bridge", "mt5_package": mt5 is not None}


@app.get("/api/state", dependencies=[Depends(auth)])
def get_state():
    require_mt5()
    info = mt5.account_info()
    positions = mt5.positions_get() or ()
    symbols = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
    prices = {}
    for symbol in symbols:
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            prices[symbol] = {"bid": float(tick.bid), "ask": float(tick.ask), "time": int(tick.time)}
    return {
        "mt5_connected": info is not None,
        "engine_running": True,
        "account": {
            "login": int(info.login), "server": info.server,
            "balance": float(info.balance), "equity": float(info.equity),
            "margin": float(info.margin), "free_margin": float(info.margin_free),
            "profit": float(info.profit), "currency": info.currency,
        } if info else None,
        "prices": prices,
        "positions": [position_dict(p) for p in positions],
    }


@app.post("/api/start", dependencies=[Depends(auth)])
def start():
    require_mt5()
    return {"ok": True, "engine_running": True, "note": "MT5 terminal connection is active"}


@app.post("/api/stop", dependencies=[Depends(auth)])
def stop():
    return {"ok": True, "engine_running": False, "note": "This disables bridge-side execution; it does not close existing positions"}


@app.post("/api/orders", dependencies=[Depends(auth)])
def order(req: OrderRequest):
    require_mt5()
    if req.volume <= 0:
        raise HTTPException(400, "Volume must be greater than zero")
    side = req.side.upper()
    if side not in {"BUY", "SELL"}:
        raise HTTPException(400, "side must be BUY or SELL")

    if not mt5.symbol_select(req.symbol, True):
        raise HTTPException(400, f"Symbol is not available: {req.symbol}")
    tick = mt5.symbol_info_tick(req.symbol)
    if not tick:
        raise HTTPException(503, f"No tick data for {req.symbol}")

    order_type = mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL
    price = tick.ask if side == "BUY" else tick.bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": req.symbol,
        "volume": req.volume,
        "type": order_type,
        "price": price,
        "sl": req.sl or 0.0,
        "tp": req.tp or 0.0,
        "deviation": req.deviation,
        "magic": req.magic,
        "comment": "RoyalInstitute",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result is None:
        code, message = mt5.last_error()
        raise HTTPException(502, f"MT5 order_send failed: {code} {message}")
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise HTTPException(400, {
            "message": "MT5 rejected the order",
            "retcode": int(result.retcode),
            "comment": result.comment,
        })
    return {"ok": True, "retcode": int(result.retcode), "order": int(result.order), "deal": int(result.deal), "price": float(result.price)}


@app.get("/api/candles/{symbol}", dependencies=[Depends(auth)])
def candles(symbol: str, timeframe: str = "M5", count: int = 200):
    require_mt5()
    tf = {
        "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
    }.get(timeframe.upper())
    if tf is None:
        raise HTTPException(400, "Unsupported timeframe")
    count = max(1, min(count, 2000))
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
    if rates is None:
        code, message = mt5.last_error()
        raise HTTPException(404, f"No candle data: {code} {message}")
    return [
        {"time": int(r["time"]), "open": float(r["open"]), "high": float(r["high"]),
         "low": float(r["low"]), "close": float(r["close"]), "volume": int(r["tick_volume"])}
        for r in rates
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("ROYAL_BRIDGE_HOST", "127.0.0.1"), port=int(os.getenv("ROYAL_BRIDGE_PORT", "8765")))

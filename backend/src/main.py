import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Cloudflare Workers environment variables are available via os.environ for Python
from .auth import KISAuth
from .market_data import MarketData
from .international_trade import InternationalTrade
from .executor import OrderExecutor
from .rsi_strategy import RSIStrategy

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy initialization for Workers
_auth = None
def get_auth():
    global _auth
    if _auth is None:
        _auth = KISAuth()
    return _auth

class OrderRequest(BaseModel):
    ticker: str
    market: str = "kr"
    action: str
    qty: int
    price: Optional[float] = 0.0

@app.get("/")
async def root():
    return {"status": "AI Stock Backend is Running on Cloudflare"}

@app.get("/api/balance")
async def get_balance():
    auth = get_auth()
    executor = OrderExecutor(auth)
    holdings, summary = executor.get_balance()
    if summary:
        return {"summary": summary, "holdings": holdings}
    raise HTTPException(status_code=500, detail="Failed to fetch balance")

@app.get("/api/quote/{market}/{ticker}")
async def get_quote(market: str, ticker: str):
    auth = get_auth()
    if market == "kr":
        md = MarketData(auth)
        st = RSIStrategy()
        data = md.get_current_price(ticker)
        ohlcv = md.get_ohlcv(ticker)
        signal, strength = st.check_signal(ohlcv)
        return {"price_info": data, "analysis": {"signal": signal, "strength": strength}}
    elif market == "us":
        intl = InternationalTrade(auth)
        data = intl.get_us_price(ticker)
        return {"price_info": data, "analysis": {"signal": "N/A", "strength": 0}}
    raise HTTPException(status_code=400, detail="Invalid market")

@app.post("/api/order")
async def place_order(req: OrderRequest):
    auth = get_auth()
    if req.market == "kr":
        executor = OrderExecutor(auth)
        result = executor.create_order(req.ticker, req.qty, side=req.action)
    elif req.market == "us":
        intl = InternationalTrade(auth)
        result = intl.create_us_order(req.ticker, req.qty, req.price, side=req.action)
    
    if result:
        return {"status": "success", "data": result}
    raise HTTPException(status_code=500, detail="Order failed")

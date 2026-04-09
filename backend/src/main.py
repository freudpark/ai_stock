import json
import os
from auth import KISAuth
from market_data import MarketData
from international_trade import InternationalTrade
from executor import OrderExecutor
from rsi_strategy import RSIStrategy
from ai_agent import AIAgent

async def on_fetch(request, env, ctx):
    # Setup environment variables safely
    os.environ["KIS_APP_MODE"] = getattr(env, "KIS_APP_MODE", "vps")
    os.environ["KIS_API_KEY"] = getattr(env, "KIS_API_KEY", "")
    os.environ["KIS_API_SECRET"] = getattr(env, "KIS_API_SECRET", "")
    os.environ["KIS_CANO"] = getattr(env, "KIS_CANO", "")
    os.environ["KIS_ACNT_PRDT_CD"] = getattr(env, "KIS_ACNT_PRDT_CD", "01")
    # For future real AI integration
    os.environ["GEMINI_API_KEY"] = getattr(env, "GEMINI_API_KEY", "")
    os.environ["NVIDIA_API_KEY"] = getattr(env, "NVIDIA_API_KEY", "")
    
    auth = KISAuth()
    
    if request.method == "OPTIONS":
        return create_response({}, status=200)

    url_obj = request.url
    
    try:
        if "/api/balance" in url_obj:
            executor = OrderExecutor(auth)
            holdings, summary = await executor.get_balance()
            return create_response({"summary": summary, "holdings": holdings})
        
        elif "/api/debug" in url_obj:
            return create_response({
                "KIS_APP_MODE": os.environ.get("KIS_APP_MODE"),
                "HAS_KEY": bool(os.environ.get("KIS_API_KEY")),
                "HAS_SECRET": bool(os.environ.get("KIS_API_SECRET")),
                "BASE_URL": auth.base_url,
                "MODE": auth.app_mode
            })
        
        elif "/api/quote" in url_obj:
            parts = url_obj.split("/")
            ticker = parts[-1]
            market = parts[-2]
            
            if market == "kr":
                md = MarketData(auth)
                st = RSIStrategy()
                data = await md.get_current_price(ticker)
                ohlcv = await md.get_ohlcv(ticker)
                signal, strength = st.check_signal(ohlcv)
                return create_response({"price_info": data, "analysis": {"signal": signal, "strength": strength}})
            
            elif market == "us":
                intl = InternationalTrade(auth)
                data = await intl.get_us_price(ticker)
                return create_response({"price_info": data, "analysis": {"signal": "N/A", "strength": 0}})

        elif "/api/auto-trade" in url_obj and request.method == "POST":
            req_data = await request.json()
            ticker = req_data.get("ticker", "005930")
            market = req_data.get("market", "kr")
            
            if market != "kr":
                return create_response({"error": "Auto-trade currently only supports KR market"}, status=400)
                
            # 1. Data Fetch
            md = MarketData(auth)
            st = RSIStrategy()
            price_data = await md.get_current_price(ticker)
            ohlcv_data = await md.get_ohlcv(ticker)
            signal, strength = st.check_signal(ohlcv_data)
            
            # 2. AI Agent Decision
            agent = AIAgent()
            decision_data = await agent.analyze_and_decide(ticker, price_data, ohlcv_data, signal, strength)
            
            # 3. Execution based on Decision
            trade_result = None
            if decision_data["decision"] in ["BUY", "SELL"] and decision_data["qty"] > 0:
                executor = OrderExecutor(auth)
                trade_result = await executor.create_order(
                    ticker=ticker, 
                    qty=decision_data["qty"], 
                    side=decision_data["decision"], 
                    order_type="01" # Market order
                )
            
            return create_response({
                "status": "success",
                "ai_decision": decision_data,
                "execution_result": trade_result
            })

        elif "/api/order" in url_obj and request.method == "POST":
            req_data = await request.json()
            ticker = req_data.get("ticker")
            market = req_data.get("market", "kr")
            action = req_data.get("action")
            qty = int(req_data.get("qty", 0))
            price = float(req_data.get("price", 0.0))
            
            if market == "kr":
                executor = OrderExecutor(auth)
                result = await executor.create_order(ticker, qty, side=action)
            else:
                intl = InternationalTrade(auth)
                result = await intl.create_us_order(ticker, qty, price, side=action)
            
            if result:
                return create_response({"status": "success", "data": result})
            return create_response({"status": "failed"}, status=500)

    except Exception as e:
        return create_response({"error": str(e)}, status=500)
        
    return create_response({"status": "AI Stock Backend on Cloudflare (Native Async)"})

def create_response(data, status=200):
    from js import Response, Headers
    headers = Headers.new()
    headers.set("Content-Type", "application/json")
    headers.set("Access-Control-Allow-Origin", "*")
    headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    headers.set("Access-Control-Allow-Headers", "*")
    
    return Response.new(json.dumps(data), headers=headers, status=status)

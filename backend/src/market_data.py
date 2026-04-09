import json
from js import fetch, Request, Headers
from auth import KISAuth

class MarketData:
    def __init__(self, auth: KISAuth):
        self.auth = auth

    async def get_current_price(self, ticker: str):
        """Fetch current price using native fetch (Async)."""
        tr_id = "FHKST01010100"
        url = f"{self.auth.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
        
        url_with_params = f"{url}?FID_COND_MRKT_DIV_CODE=J&FID_INPUT_ISCD={ticker}"
        
        kis_headers = await self.auth.get_headers(tr_id=tr_id)
        headers = Headers.new()
        for k, v in kis_headers.items():
            headers.set(k, v)
        
        try:
            request = Request.new(url_with_params, method="GET", headers=headers)
            response = await fetch(request)
            data = await response.json()
            if data["rt_cd"] == "0":
                return data["output"]
            return None
        except Exception as e:
            print(f"[ERROR] Fetch current price failed: {e}")
            return None

    async def get_ohlcv(self, ticker: str, period: str = "D", count: int = 30):
        """Fetch OHLCV historical data (Async)."""
        tr_id = "FHKST03010100"
        url = f"{self.auth.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
        
        params = f"FID_COND_MRKT_DIV_CODE=J&FID_INPUT_ISCD={ticker}&FID_PERIOD_DIV_CODE={period}&FID_ORG_ADJ_PRC=0"
        url_with_params = f"{url}?{params}"
        
        kis_headers = await self.auth.get_headers(tr_id=tr_id)
        headers = Headers.new()
        for k, v in kis_headers.items():
            headers.set(k, v)
            
        try:
            request = Request.new(url_with_params, method="GET", headers=headers)
            response = await fetch(request)
            data = await response.json()
            if data["rt_cd"] == "0":
                # Return raw list (output2) since pandas is not available
                return data["output2"][:count]
            return None
        except Exception as e:
            print(f"[ERROR] OHLCV fetch failed: {e}")
            return None

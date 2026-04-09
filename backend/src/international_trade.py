import os
import json
from js import fetch, Request, Headers
from auth import KISAuth

class InternationalTrade:
    def __init__(self, auth: KISAuth):
        self.auth = auth
        self.cano = os.getenv("KIS_CANO")
        self.acnt_prdt_cd = os.getenv("KIS_ACNT_PRDT_CD", "01")

    async def get_us_price(self, symbol: str, exchange: str = "NASD"):
        """Fetch US stock price using native fetch (Async)."""
        tr_id = "HHDFS00000300"
        url = f"{self.auth.base_url}/uapi/overseas-stock/v1/quotations/price"
        
        url_with_params = f"{url}?AUTH=&EXCD={exchange}&SYMB={symbol}"
        
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
            print(f"[ERROR] US price fetch failed: {e}")
            return None

    async def create_us_order(self, symbol: str, qty: int, price: float, side: str = "BUY", exchange: str = "NASD"):
        """Execute US stock order using native fetch (Async)."""
        if side == "BUY":
            tr_id = "TTTT1002U" if self.auth.app_mode == "prod" else "VTTT1002U"
        else:
            tr_id = "TTTT1006U" if self.auth.app_mode == "prod" else "VTTT1006U"
            
        url = f"{self.auth.base_url}/uapi/overseas-stock/v1/trading/order"
        
        kis_headers = await self.auth.get_headers(tr_id=tr_id)
        headers = Headers.new()
        for k, v in kis_headers.items():
            headers.set(k, v)
        
        body = json.dumps({
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "OVRS_EXCG_CD": exchange,
            "PDNO": symbol,
            "ORD_QTY": str(qty),
            "OVRS_ORD_UNPR": f"{price:.2f}",
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": "00"
        })
        
        try:
            request = Request.new(url, method="POST", headers=headers, body=body)
            response = await fetch(request)
            data = await response.json()
            if data["rt_cd"] == "0":
                return data["output"]
            return None
        except Exception as e:
            print(f"[ERROR] US order execution failed: {e}")
            return None

import os
import json
from js import fetch, Request, Headers
from auth import KISAuth

class OrderExecutor:
    def __init__(self, auth: KISAuth):
        self.auth = auth
        self.cano = os.getenv("KIS_CANO", "").strip().strip('"')
        self.acnt_prdt_cd = os.getenv("KIS_ACNT_PRDT_CD", "01").strip().strip('"')

    async def create_order(self, ticker: str, qty: int, price: int = 0, side: str = "BUY", order_type: str = "01"):
        """Execute an order with robust dict handling."""
        tr_id = "TTTC0802U" if side == "BUY" else "TTTC0801U"
        if self.auth.app_mode == "vps":
            tr_id = "VTTC0802U" if side == "BUY" else "VTTC0801U"
            
        url = f"{self.auth.base_url}/uapi/domestic-stock/v1/trading/order-cash"
        
        try:
            kis_headers = await self.auth.get_headers(tr_id=tr_id)
            headers = Headers.new()
            for k, v in kis_headers.items():
                headers.set(k, v)
            
            body = json.dumps({
                "CANO": self.cano,
                "ACNT_PRDT_CD": self.acnt_prdt_cd,
                "PDNO": ticker,
                "ORD_DVSN": order_type,
                "ORD_QTY": str(qty),
                "ORD_UNPR": str(price) if order_type == "00" else "0",
            })
            
            request = Request.new(url, method="POST", headers=headers, body=body)
            response = await fetch(request)
            raw_text = await response.text()
            data = json.loads(raw_text)
            
            if data.get("rt_cd") == "0":
                return data.get("output")
            return {"error": data.get("msg1"), "code": data.get("msg_cd"), "raw": raw_text}
        except Exception as e:
            return {"error": str(e)}

    async def get_balance(self):
        """Check current account balance with robust dict handling."""
        tr_id = "TTTC8434R"
        if self.auth.app_mode == "vps":
            tr_id = "VTTC8434R"
            
        url = f"{self.auth.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
        
        params = f"CANO={self.cano}&ACNT_PRDT_CD={self.acnt_prdt_cd}&AFHR_FLPR_YN=N&OFL_YN=&INQR_DVSN=01&UNPR_DVSN=01&FUND_STTL_ICLD_YN=N&FNCG_AMT_AUTO_RDPT_YN=N&PRCS_DVSN=00&CTX_AREA_FK100=&CTX_AREA_NK100="
        url_with_params = f"{url}?{params}"
        
        try:
            kis_headers = await self.auth.get_headers(tr_id=tr_id)
            headers = Headers.new()
            for k, v in kis_headers.items():
                headers.set(k, v)
                
            request = Request.new(url_with_params, method="GET", headers=headers)
            response = await fetch(request)
            raw_text = await response.text()
            data = json.loads(raw_text)
            
            if data.get("rt_cd") == "0":
                return data.get("output1"), data.get("output2")
            else:
                return None, {"error": data.get("msg1"), "code": data.get("msg_cd"), "raw": raw_text}
        except Exception as e:
            err_msg = str(e)
            if "KIS Auth Error:" in err_msg:
                detail = err_msg.split("KIS Auth Error: ")[-1]
                return None, {"error": "Authentication Failed", "detail": detail}
            return None, {"error": f"Internal Error: {err_msg}"}

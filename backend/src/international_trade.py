import os
import requests
import json
from core.auth import KISAuth

class InternationalTrade:
    def __init__(self, auth: KISAuth):
        self.auth = auth
        self.cano = os.getenv("KIS_CANO")
        self.acnt_prdt_cd = os.getenv("KIS_ACNT_PRDT_CD", "01")

    def get_us_price(self, symbol: str, exchange: str = "NASD"):
        """
        Fetch current price of a US stock.
        exchange: NASD (Nasdaq), NYSE (New York), AMEX (American)
        """
        tr_id = "HHDFS00000300"
        url = f"{self.auth.base_url}/uapi/overseas-stock/v1/quotations/price"
        
        params = {
            "AUTH": "",
            "EXCD": exchange,
            "SYMB": symbol
        }
        
        headers = self.auth.get_headers(tr_id=tr_id)
        
        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            if data["rt_cd"] == "0":
                return data["output"]
            else:
                print(f"[ERROR] US Price Fetch Failed: {data['msg1']}")
                return None
        except Exception as e:
            print(f"[ERROR] US Price Network Error: {e}")
            return None

    def create_us_order(self, symbol: str, qty: int, price: float, side: str = "BUY", exchange: str = "NASD"):
        """
        Execute an order for US stock.
        side: "BUY" or "SELL"
        """
        if side == "BUY":
            tr_id = "TTTT1002U" if self.auth.app_mode == "prod" else "VTTT1002U"
        else:
            tr_id = "TTTT1006U" if self.auth.app_mode == "prod" else "VTTT1006U"
            
        url = f"{self.auth.base_url}/uapi/overseas-stock/v1/trading/order"
        
        headers = self.auth.get_headers(tr_id=tr_id)
        
        body = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "OVRS_EXCG_CD": exchange,
            "PDNO": symbol,
            "ORD_QTY": str(qty),
            "OVRS_ORD_UNPR": f"{price:.2f}",
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": "00" # 지정가 기본
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(body))
            data = response.json()
            if data["rt_cd"] == "0":
                print(f"[SUCCESS] US {side} order for {symbol}. Qty: {qty}. Order No: {data['output']['ODNO']}")
                return data["output"]
            else:
                print(f"[ERROR] US Order Failed: {data['msg1']} ({data['msg_cd']})")
                return None
        except Exception as e:
            print(f"[ERROR] US Order Exception: {e}")
            return None

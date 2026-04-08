import os
import requests
import json
from core.auth import KISAuth

class OrderExecutor:
    def __init__(self, auth: KISAuth):
        self.auth = auth
        self.cano = os.getenv("KIS_CANO")
        self.acnt_prdt_cd = os.getenv("KIS_ACNT_PRDT_CD", "01")

    def create_order(self, ticker: str, qty: int, price: int = 0, side: str = "BUY", order_type: str = "01"):
        """
        Execute an order (Domestic Kr).
        side: "BUY" or "SELL"
        order_type: "01" (Market), "00" (Limit)
        """
        tr_id = "TTTC0802U" if side == "BUY" else "TTTC0801U"
        if self.auth.app_mode == "vps":
            tr_id = "VTTC0802U" if side == "BUY" else "VTTC0801U" # Mock TR IDs
            
        url = f"{self.auth.base_url}/uapi/domestic-stock/v1/trading/order-cash"
        
        # 01: Market Price, 00: Limit Price
        headers = self.auth.get_headers(tr_id=tr_id)
        
        body = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "PDNO": ticker,
            "ORD_DVSN": order_type,
            "ORD_QTY": str(qty),
            "ORD_UNPR": str(price) if order_type == "00" else "0",
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(body))
            response.raise_for_status()
            data = response.json()
            
            if data["rt_cd"] == "0":
                print(f"[SUCCESS] {side} order placed for {ticker}. Qty: {qty}. Order No: {data['output']['ODNO']}")
                return data["output"]
            else:
                print(f"[ERROR] Order Failed: {data['msg1']} ({data['msg_cd']})")
                return None
        except Exception as e:
            print(f"[ERROR] Order execution exception: {e}")
            return None

    def get_balance(self):
        """Check current account balance and holdings."""
        tr_id = "TTTC8434R"
        if self.auth.app_mode == "vps":
            tr_id = "VTTC8434R"
            
        url = f"{self.auth.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
        
        params = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "01",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        headers = self.auth.get_headers(tr_id=tr_id)
        
        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            if data["rt_cd"] == "0":
                return data["output1"], data["output2"] # Holdings, Asset Summary
            else:
                print(f"[ERROR] Balance Inquiry Failed: {data['msg1']}")
                return None, None
        except Exception as e:
            print(f"[ERROR] Balance fetch exception: {e}")
            return None, None

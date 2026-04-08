import requests
import pandas as pd
from core.auth import KISAuth

class MarketData:
    def __init__(self, auth: KISAuth):
        self.auth = auth

    def get_current_price(self, ticker: str):
        """Fetch current price of a stock (Domestic Kr)."""
        tr_id = "FHKST01010100"  # 주식현재가 시세
        url = f"{self.auth.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": ticker
        }
        
        headers = self.auth.get_headers(tr_id=tr_id)
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data["rt_cd"] == "0":
                return data["output"]
            else:
                print(f"[ERROR] API Response Error: {data['msg1']}")
                return None
        except Exception as e:
            print(f"[ERROR] Network error: {e}")
            return None

    def get_ohlcv(self, ticker: str, period: str = "D", count: int = 30):
        """Fetch OHLCV historical data for strategy analysis."""
        tr_id = "FHKST03010100"  # 주식일별주가
        url = f"{self.auth.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": ticker,
            "FID_PERIOD_DIV_CODE": period,
            "FID_ORG_ADJ_PRC": "0"
        }
        
        headers = self.auth.get_headers(tr_id=tr_id)
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data["rt_cd"] == "0":
                df = pd.DataFrame(data["output2"])
                # Clean up data types
                cols = ['stck_clpr', 'stck_hgpr', 'stck_lwpr', 'stck_oprc', 'acml_vol']
                for col in cols:
                    df[col] = pd.to_numeric(df[col])
                return df.head(count)
            else:
                return None
        except Exception as e:
            print(f"[ERROR] Failed to fetch OHLCV: {e}")
            return None

if __name__ == "__main__":
    auth = KISAuth()
    market = MarketData(auth)
    # Test for Samsung Electronics (005930)
    price_info = market.get_current_price("005930")
    if price_info:
        print(f"Samsung Electronics Price: {price_info['stck_prpr']}")

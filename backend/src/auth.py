import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class KISAuth:
    def __init__(self):
        self.api_key = os.getenv("KIS_API_KEY")
        self.api_secret = os.getenv("KIS_API_SECRET")
        self.app_mode = os.getenv("KIS_APP_MODE", "vps")  # Default to vps for safety
        
        if self.app_mode == "prod":
            self.base_url = "https://openapi.koreainvestment.com:9443"
        else:
            self.base_url = "https://openapivts.koreainvestment.com:29443"
            
        self.access_token = None

    def get_access_token(self):
        """Fetch a new access token from KIS API."""
        url = f"{self.base_url}/oauth2/tokenP"
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.api_key,
            "appsecret": self.api_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(body))
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")
            return self.access_token
        except Exception as e:
            print(f"[ERROR] Failed to get access token: {e}")
            return None

    def get_headers(self, tr_id=None):
        """Prepare common headers for KIS API requests."""
        if not self.access_token:
            self.get_access_token()
            
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.api_key,
            "appsecret": self.api_secret,
        }
        if tr_id:
            headers["tr_id"] = tr_id
        return headers

if __name__ == "__main__":
    # Simple test
    auth = KISAuth()
    token = auth.get_access_token()
    if token:
        print(f"[SUCCESS] Access token obtained: {token[:10]}...")
    else:
        print("[FAIL] Authentication check failed. Check your .env file.")

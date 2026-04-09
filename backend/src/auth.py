import os
import json
from js import fetch, Request, Headers

class KISAuth:
    def __init__(self):
        self.api_key = os.getenv("KIS_API_KEY", "").strip().strip('"').strip("'")
        self.api_secret = os.getenv("KIS_API_SECRET", "").strip().strip('"').strip("'")
        self.app_mode = os.getenv("KIS_APP_MODE", "vps").strip().strip('"')
        
        if self.app_mode == "prod":
            self.base_url = "https://openapi.koreainvestment.com:9443"
        else:
            self.base_url = "https://openapivts.koreainvestment.com:29443"
            
        self.access_token = None
        self.last_auth_error = None

    async def get_access_token(self):
        """Fetch a new access token using robust text-to-json parsing."""
        url = f"{self.base_url}/oauth2/tokenP"
        headers = Headers.new()
        headers.set("content-type", "application/json")
        
        body = json.dumps({
            "grant_type": "client_credentials",
            "appkey": self.api_key,
            "appsecret": self.api_secret
        })
        
        request = Request.new(url, method="POST", headers=headers, body=body)
        
        try:
            response = await fetch(request)
            raw_text = await response.text()
            
            try:
                data = json.loads(raw_text)
                # Now 'data' is a true Python dict
                if isinstance(data, dict):
                    self.access_token = data.get("access_token")
                    if not self.access_token:
                        self.last_auth_error = data.get("error_description", raw_text)
                else:
                    self.last_auth_error = f"Unexpected response format: {raw_text}"
            except Exception as e:
                self.last_auth_error = f"JSON Parse Error: {str(e)} | Raw: {raw_text}"
                
            return self.access_token
        except Exception as e:
            self.last_auth_error = f"Network Error: {str(e)}"
            return None

    async def get_headers(self, tr_id=None):
        """Prepare headers, ensuring token is available."""
        if not self.access_token:
            token = await self.get_access_token()
            if not token:
                raise Exception(f"KIS Auth Error: {self.last_auth_error}")
            
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.api_key,
            "appsecret": self.api_secret,
            "custtype": "P",
        }
        if tr_id:
            headers["tr_id"] = tr_id
        return headers

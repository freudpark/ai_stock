import os
import json
import asyncio
import websockets
import requests
from dotenv import load_dotenv

load_dotenv()

class KISWebSocket:
    def __init__(self, auth):
        self.auth = auth
        self.approval_key = None
        
        if self.auth.app_mode == "prod":
            self.ws_url = "ws://ops.koreainvestment.com:21000" # Real
        else:
            self.ws_url = "ws://ops.koreainvestment.com:31000" # Mock (Check if VTS uses same or separate)
            
    def get_approval_key(self):
        """Approval key is required specifically for WebSockets."""
        url = f"{self.auth.base_url}/oauth2/Approval"
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.auth.api_key,
            "secretkey": self.auth.api_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(body))
            data = response.json()
            self.approval_key = data.get("approval_key")
            return self.approval_key
        except Exception as e:
            print(f"[ERROR] Failed to get approval key: {e}")
            return None

    async def subscribe_price(self, ticker: str):
        """Subscribe to real-time execution data for a ticker."""
        if not self.approval_key:
            self.get_approval_key()
            
        async with websockets.connect(self.ws_url) as ws:
            # Subscribe format (Standard Domestic Stock Execution)
            send_data = {
                "header": {
                    "approval_key": self.approval_key,
                    "custtype": "P", # Personal
                    "tr_type": "1", # Register
                    "content-type": "utf-8"
                },
                "body": {
                    "input": {
                        "tr_id": "H0STCNT0", # Real-time execution
                        "tr_key": ticker
                    }
                }
            }
            await ws.send(json.dumps(send_data))
            print(f"[WS] Subscribed to {ticker} real-time data.")
            
            while True:
                response = await ws.recv()
                if response[0] == '0' or response[0] == '1': # Data packet
                    # Simple parsing for demo
                    data_parts = response.split('|')
                    if len(data_parts) > 3:
                        msg_header = data_parts[0]
                        msg_body = data_parts[3]
                        print(f"[WS DATA] {ticker} -> {msg_body[:50]}...")
                else:
                    print(f"[WS MESSAGE] {response}")

if __name__ == "__main__":
    from core.auth import KISAuth
    auth = KISAuth()
    client = KISWebSocket(auth)
    
    # Run the async loop
    # asyncio.run(client.subscribe_price("005930"))

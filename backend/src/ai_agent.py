import json
import os
from js import fetch, Request, Headers

class AIAgent:
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY", "").strip().strip('"')
        self.invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"

    async def analyze_and_decide(self, ticker, price_data, ohlcv_data, rsi_signal, rsi_strength):
        """
        NVIDIA Qwen 3.5-122B-A10B 모델을 호출하여 시장 데이터를 종합 분석합니다.
        """
        if not self.api_key:
            return {
                "ticker": ticker,
                "decision": "HOLD",
                "qty": 0,
                "reason": "오류: NVIDIA API Key가 설정되지 않았습니다."
            }

        # 프롬프트 구성 (시장 데이터 주입)
        system_prompt = (
            "당신은 고도의 금융 분석 AI '프로이트'입니다. 다음 주식 데이터를 바탕으로 '매수(BUY)', '매도(SELL)', '관망(HOLD)' 중 하나를 결정하고 수량을 추천하십시오.\n\n"
            f"종목: {ticker}\n"
            f"현재가: {price_data.get('stck_prpr', 'N/A')}원\n"
            f"보조지표(RSI): 시그널={rsi_signal}, 강도={rsi_strength:.2f}\n"
            "최근 가격 동향(OHLCV): " + str([f"종가:{x['stck_clpr']}" for x in ohlcv_data[:5]]) + "\n\n"
            "응답은 반드시 아래 JSON 형식으로만 하십시오. (다른 텍스트 금지)\n"
            '{"decision": "BUY/SELL/HOLD", "qty": 수량(정수), "reason": "한글로 된 분석 근거"}'
        )

        headers = Headers.new()
        headers.set("Authorization", f"Bearer {self.api_key}")
        headers.set("Content-Type", "application/json")
        headers.set("Accept", "application/json")

        payload = json.dumps({
            "model": "qwen/qwen3.5-122b-a10b",
            "messages": [{"role": "user", "content": system_prompt}],
            "max_tokens": 1024,
            "temperature": 0.60,
            "top_p": 0.95,
            "stream": False # Simple non-stream for parsing JSON
        })

        try:
            request = Request.new(self.invoke_url, method="POST", headers=headers, body=payload)
            response = await fetch(request)
            raw_text = await response.text()
            
            ai_data = json.loads(raw_text)
            content = ai_data['choices'][0]['message']['content'].strip()
            
            # JSON 파싱 (AI가 가끔 텍스트를 섞을 수 있으므로 JSON만 추출)
            if "{" in content:
                content = content[content.find("{"):content.rfind("}")+1]
                
            decision_json = json.loads(content)
            
            return {
                "ticker": ticker,
                "decision": decision_json.get("decision", "HOLD"),
                "qty": int(decision_json.get("qty", 0)),
                "price": float(price_data.get('stck_prpr', 0)),
                "reason": f"[AI Qwen 분석] {decision_json.get('reason', '분석 결과 관망을 추천합니다.')}"
            }
        except Exception as e:
            print(f"[ERROR] NVIDIA AI Error: {str(e)}")
            return {
                "ticker": ticker,
                "decision": "HOLD",
                "qty": 0,
                "reason": f"AI 분석 중 오류가 발생했습니다: {str(e)}"
            }

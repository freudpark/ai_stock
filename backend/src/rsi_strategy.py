class RSIStrategy:
    def __init__(self, period=14, buy_threshold=30, sell_threshold=70):
        self.period = period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def calculate_rsi(self, prices):
        """Calculate RSI using raw list data (Async-friendly)."""
        if len(prices) < self.period + 1:
            return None
            
        deltas = [prices[i] - prices[i+1] for i in range(len(prices)-1)]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[:self.period]) / self.period
        avg_loss = sum(losses[:self.period]) / self.period
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def check_signal(self, ohlcv_data):
        """Analyze raw list and return trading signal."""
        if not ohlcv_data or len(ohlcv_data) < self.period + 1:
            return "HOLD", 0.0
            
        # Extract closing prices (stck_clpr) from raw list of dicts
        try:
            prices = [float(x['stck_clpr']) for x in ohlcv_data]
            current_rsi = self.calculate_rsi(prices)
            
            if current_rsi is None:
                return "HOLD", 0.0
                
            if current_rsi <= self.buy_threshold:
                strength = min(1.0, (self.buy_threshold - current_rsi) / 10 + 0.5)
                return "BUY", strength
            elif current_rsi >= self.sell_threshold:
                strength = min(1.0, (current_rsi - self.sell_threshold) / 10 + 0.5)
                return "SELL", strength
        except Exception as e:
            print(f"[ERROR] Strategy analysis error: {e}")
            
        return "HOLD", 0.0

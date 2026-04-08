import pandas as pd

class RSIStrategy:
    def __init__(self, period=14, buy_threshold=30, sell_threshold=70):
        self.period = period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def calculate_rsi(self, df):
        """Calculate Relative Strength Index (RSI)."""
        delta = df['stck_clpr'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def check_signal(self, df):
        """Analyze data and return trading signal."""
        if len(df) < self.period + 1:
            return "HOLD", 0.0
            
        rsi_series = self.calculate_rsi(df)
        current_rsi = rsi_series.iloc[0] # Most recent is first in KIS response order
        
        print(f"[STRATEGY] Current RSI: {current_rsi:.2f}")
        
        if current_rsi <= self.buy_threshold:
            # Strength is high when RSI is very low
            strength = min(1.0, (self.buy_threshold - current_rsi) / 10 + 0.5)
            return "BUY", strength
        elif current_rsi >= self.sell_threshold:
            strength = min(1.0, (current_rsi - self.sell_threshold) / 10 + 0.5)
            return "SELL", strength
            
        return "HOLD", 0.0

class MovingAverageCrossoverStrategy:
    def __init__(self, short_window=5, long_window=20):
        self.short_window = short_window
        self.long_window = long_window

    def compute_sma(self, prices, window):
        if len(prices) < window:
            return None
        return sum(prices[-window:]) / window

    def generate_signal(self, prices):
        short_sma = self.compute_sma(prices, self.short_window)
        long_sma = self.compute_sma(prices, self.long_window)

        if short_sma is None or long_sma is None:
            return "hold"

        if short_sma > long_sma:
            return "buy"
        elif short_sma < long_sma:
            return "sell"
        else:
            return "hold"

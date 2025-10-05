class PerformanceTracker:
    def __init__(self):
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        self.profit = 0.0

    def record_trade(self, profit_pct):
        self.total_trades += 1
        if profit_pct > 0:
            self.wins += 1
        else:
            self.losses += 1
        self.profit += profit_pct

    def win_rate(self):
        return self.wins / self.total_trades if self.total_trades else 0

    def avg_profit(self):
        return self.profit / self.total_trades if self.total_trades else 0

class AnomalyDetector:
    def __init__(self, max_drawdown=0.1):
        self.max_drawdown = max_drawdown
        self.peak = 0
        self.trough = float('inf')
        self.drawdown = 0

    def update(self, current_value):
        if current_value > self.peak:
            self.peak = current_value
            self.trough = current_value
        if current_value < self.trough:
            self.trough = current_value
            self.drawdown = (self.peak - self.trough) / self.peak

        return self.drawdown > self.max_drawdown

from core.interfaces import IStrategyManager

class MockStrategyManager(IStrategyManager):
    def __init__(self):
        self.status = "stopped"

    def get_strategy_status(self):
        return self.status

    def run_strategy(self):
        self.status = "running"

    def stop_strategy(self):
        self.status = "stopped"

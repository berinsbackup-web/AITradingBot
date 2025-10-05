from core.interfaces import IPortfolioManager

class MockPortfolioManager(IPortfolioManager):
    def __init__(self):
        self.portfolio = {}

    def get_portfolio(self):
        return self.portfolio

    def update_portfolio(self, trades):
        print(f"MockPortfolioManager: updated with trades {trades}")
        # Mock updating portfolio here

    def get_positions(self):
        # Return a copy to protect internal state
        return dict(self.positions)

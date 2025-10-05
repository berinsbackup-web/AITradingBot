import os
import numpy as np
import pandas as pd
from scipy.stats import norm

class RiskManager:
    def __init__(
        self,
        initial_capital=100000,
        max_drawdown_limit=0.2,
        confidence_level=0.95,
        max_position_value: float | None = None,
        max_daily_loss: float | None = None,
        max_single_order_value: float | None = None,
    ):
        self.initial_capital = initial_capital
        self.max_drawdown_limit = max_drawdown_limit
        self.confidence_level = confidence_level
        self.equity_curve = pd.Series(dtype=float)
        self.position_sizes = {}
        self.returns = []

        # Safety rails (env overrides allowed)
        self.max_position_value = float(os.getenv("MAX_POSITION_VALUE", max_position_value or 0) or 0)
        self.max_daily_loss = float(os.getenv("MAX_DAILY_LOSS", max_daily_loss or 0) or 0)
        self.max_single_order_value = float(os.getenv("MAX_SINGLE_ORDER_VALUE", max_single_order_value or 0) or 0)

        self._panic = False

    # -------- Analytics --------
    def update_equity_curve(self, timestamp, portfolio_value):
        self.equity_curve.at[timestamp] = portfolio_value

    def max_drawdown(self):
        if self.equity_curve.empty:
            return 0.0
        running_max = self.equity_curve.cummax()
        drawdowns = (running_max - self.equity_curve) / running_max
        return drawdowns.max()

    def check_max_drawdown_limit(self):
        return self.max_drawdown() > self.max_drawdown_limit

    def value_at_risk(self, returns):
        if len(returns) == 0:
            return 0.0
        mu = np.mean(returns)
        sigma = np.std(returns)
        var = - (mu + sigma * norm.ppf(1 - self.confidence_level))
        return var

    def expected_shortfall(self, returns):
        if len(returns) == 0:
            return 0.0
        sorted_returns = np.sort(returns)
        cutoff_index = int((1 - self.confidence_level) * len(returns))
        return -np.mean(sorted_returns[:cutoff_index]) if cutoff_index > 0 else 0.0

    def dynamic_position_sizing(self, symbol, risk_per_trade=0.005, stop_loss_pct=0.02, current_price=None):
        if current_price is None or current_price <= 0:
            raise ValueError("Invalid current_price for position sizing.")
        risk_amount = self.initial_capital * risk_per_trade
        max_units = risk_amount / (stop_loss_pct * current_price)
        self.position_sizes[symbol] = max_units
        return max_units

    async def position_size(self, symbol):
        # Async-compatible for callers awaiting this
        return self.position_sizes.get(symbol, 0)

    def risk_report(self, current_portfolio_value):
        returns_array = np.array(self.returns)
        report = {
            "current_value": current_portfolio_value,
            "max_drawdown": self.max_drawdown(),
            "drawdown_exceeded": self.check_max_drawdown_limit(),
            "VaR_95": self.value_at_risk(returns_array),
            "Expected_Shortfall_95": self.expected_shortfall(returns_array),
            "Total_Returns": np.sum(returns_array),
            "panic": self._panic,
            "max_position_value": self.max_position_value,
            "max_daily_loss": self.max_daily_loss,
            "max_single_order_value": self.max_single_order_value,
        }
        return report

    def add_return(self, return_value):
        self.returns.append(return_value)

    # -------- Safety rails --------
    def trigger_panic(self, reason: str):
        self._panic = True
        # in practice: notify + persist event
        print(f"PANIC STOP TRIGGERED: {reason}")

    def clear_panic(self):
        self._panic = False
        print("Panic stop cleared.")

    @property
    def is_panic(self) -> bool:
        return self._panic

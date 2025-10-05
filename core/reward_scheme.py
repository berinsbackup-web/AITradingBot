import numpy as np

class RewardScheme:
    def __init__(self, portfolio, mode='risk_adjusted', trade_fee=0.001):
        self.portfolio = portfolio
        self.mode = mode
        self.trade_fee = trade_fee
        self._reset()

    def _reset(self):
        self.equity_curve = []
        self.peak_equity = None

    def reset(self):
        self._reset()

    def compute(self, last_obs, action, trade_executed):
        curr_equity = self.portfolio.total_equity()
        self.equity_curve.append(curr_equity)
        if self.peak_equity is None or curr_equity > self.peak_equity:
            self.peak_equity = curr_equity

        profit = curr_equity - self.equity_curve[-2] if len(self.equity_curve) > 1 else 0.0
        cost = -self.trade_fee * abs(trade_executed) if trade_executed else 0.0
        drawdown = (self.peak_equity - curr_equity) / self.peak_equity if self.peak_equity else 0.0
        dd_penalty = -drawdown if drawdown > 0.02 else 0.0

        rolling_win = 10
        equity_arr = np.array(self.equity_curve[-rolling_win:])
        if len(equity_arr) > 1:
            volatility = np.std(np.diff(equity_arr))
            risk = -volatility * 0.5
        else:
            risk = 0.0

        if self.mode == 'profit':
            reward = profit + cost
        elif self.mode == 'risk_adjusted':
            reward = profit + cost + risk + dd_penalty
        else:
            reward = profit + cost

        return reward

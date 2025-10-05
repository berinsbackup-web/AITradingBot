import numpy as np


class AdaptiveIndicators:
    def __init__(self, closes, highs=None, lows=None):
        self.closes = np.array(closes)
        self.highs = np.array(highs) if highs is not None else self.closes
        self.lows = np.array(lows) if lows is not None else self.closes

    def adaptive_ema(self, span_base=20, volatility_window=14):
        volatility = self.atr(period=volatility_window)
        if volatility is None or volatility == 0:
            span = span_base
        else:
            span = max(5, span_base / volatility)

        alpha = 2 / (span + 1)
        ema = [self.closes[0]]
        for price in self.closes[1:]:
            ema.append(alpha * price + (1 - alpha) * ema[-1])
        return np.array(ema)

    def macd(self, short_span=12, long_span=26, signal_span=9):
        ema_short = self.adaptive_ema(span_base=short_span)
        ema_long = self.adaptive_ema(span_base=long_span)
        macd_line = ema_short - ema_long
        signal = self._ema_series(macd_line, signal_span)
        histogram = macd_line - signal
        return macd_line, signal, histogram

    def stochastic_rsi(self, rsi_period=14, stoch_period=14, smooth_k=3, smooth_d=3):
        rsi = self.compute_rsi(period=rsi_period)
        if rsi is None:
            return None, None
        rsi = np.array(rsi)
        recent_rsi = rsi[-stoch_period:]
        lowest_low = np.min(recent_rsi)
        highest_high = np.max(recent_rsi)
        if highest_high == lowest_low:
            stoch_rsi = 0
        else:
            stoch_rsi = 100 * (rsi[-1] - lowest_low) / (highest_high - lowest_low)

        percent_k = self._simple_moving_average(np.append(rsi[-smooth_k:], stoch_rsi), smooth_k)
        percent_d = self._simple_moving_average(np.append(rsi[-smooth_d:], percent_k), smooth_d)

        return percent_k, percent_d

    def atr(self, period=14):
        if len(self.closes) < period + 1:
            return None
        trs = []
        for i in range(1, len(self.closes)):
            tr = max(
                self.highs[i] - self.lows[i],
                abs(self.highs[i] - self.closes[i - 1]),
                abs(self.lows[i] - self.closes[i - 1])
            )
            trs.append(tr)
        atr = np.mean(trs[-period:])
        return atr

    def compute_rsi(self, period=14):
        if len(self.closes) < period + 1:
            return None

        deltas = np.diff(self.closes)
        seed = deltas[:period]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi = [0] * period + [100 - 100 / (1 + rs)]

        for delta in deltas[period:]:
            upval = max(delta, 0)
            downval = max(-delta, 0)
            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up / down if down != 0 else 0
            rsi.append(100 - 100 / (1 + rs))

        return np.array(rsi)

    def _ema_series(self, data, span):
        alpha = 2 / (span + 1)
        ema = [data[0]]
        for val in data[1:]:
            ema.append(alpha * val + (1 - alpha) * ema[-1])
        return np.array(ema)

    def _simple_moving_average(self, data, window):
        if len(data) < window:
            return np.mean(data)
        return np.mean(data[-window:])

    def compute_adx(self, period=14):
        if len(self.closes) < period + 1:
            return None
        trs = []
        for i in range(1, len(self.closes)):
            tr = max(
                self.highs[i] - self.lows[i],
                abs(self.highs[i] - self.closes[i-1]),
                abs(self.lows[i] - self.closes[i-1])
            )
            trs.append(tr)
        adx_proxy = np.mean(trs[-period:])
        return adx_proxy

    def bb_width(self, window=20, num_std=2):
        if len(self.closes) < window:
            return None
        sma = np.mean(self.closes[-window:])
        std = np.std(self.closes[-window:])
        upper = sma + num_std * std
        lower = sma - num_std * std
        return upper - lower

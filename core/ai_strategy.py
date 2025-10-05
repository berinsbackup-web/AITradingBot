import numpy as np
import asyncio
import os
from core.order_manager import Order, OrderSide, OrderType
from core.indicators import AdaptiveIndicators
from .deep_rl_agent import DeepRLAgent

class AIStrategy:
    def __init__(self, risk_manager, order_manager, config=None):
        self.risk_manager = risk_manager
        self.order_manager = order_manager
        self.config = config or {}

        # Strategy parameters
        self.short_window = self.config.get('short_window', 5)
        self.long_window = self.config.get('long_window', 20)
        self.rsi_period = self.config.get('rsi_period', 14)
        self.bollinger_window = self.config.get('bollinger_window', 20)
        self.trade_quantity = self.config.get('trade_quantity', 1)
        self.stop_loss_pct = self.config.get('stop_loss_pct', 0.05)
        self.take_profit_pct = self.config.get('take_profit_pct', 0.1)

        # Safety: default to inference-only in live
        self.inference_only = bool(self.config.get("inference_only", True) or os.getenv("INFERENCE_ONLY", "1") == "1")

        # RL Agent Initialization
        self.rl_agent = DeepRLAgent(state_size=4, action_size=3)
        try:
            self.rl_agent.load_model('dqn_model.pth')
            print("Loaded pre-trained RL model.")
        except FileNotFoundError:
            print("No pre-trained model found; training from scratch.")

    def evaluate_market(self, market_data):
        closes = market_data.get('close', [])
        highs = market_data.get('high', [])
        lows = market_data.get('low', [])

        min_data = max(self.long_window, self.rsi_period, self.bollinger_window)
        if len(closes) < min_data:
            print(f"Insufficient data (length={len(closes)}), holding position")
            return 'hold'

        indicators = AdaptiveIndicators(closes, highs, lows)
        ema_short = indicators.adaptive_ema(span_base=self.short_window)
        ema_long = indicators.adaptive_ema(span_base=self.long_window)
        rsi_array = indicators.compute_rsi(period=self.rsi_period)
        lower_band, _, upper_band = self.compute_bollinger_bands(closes, self.bollinger_window)

        short_ma = ema_short[-1]
        long_ma = ema_long[-1]
        rsi = rsi_array[-1] if rsi_array is not None else None
        price = closes[-1]

        adx = indicators.compute_adx() or 0
        bb_width = indicators.bb_width(self.bollinger_window) or 0

        SIDEWAYS_ADX_THRESHOLD = 0.5
        SIDEWAYS_BB_WIDTH_THRESHOLD = 1.0
        is_sideways = (adx < SIDEWAYS_ADX_THRESHOLD) and (bb_width < SIDEWAYS_BB_WIDTH_THRESHOLD)

        print(f"EMA short: {short_ma:.4f}, EMA long: {long_ma:.4f}")
        print(f"RSI: {rsi}")
        print(f"Price: {price}")
        print(f"Bollinger Bands - Lower: {lower_band}, Upper: {upper_band}")
        print(f"ADX: {adx}, BB Width: {bb_width}, Sideways: {is_sideways}")

        if is_sideways:
            return 'hold'

        cond_buy = (short_ma > long_ma) and (rsi is None or rsi < 70) and (price < upper_band if upper_band else True)
        cond_sell = (short_ma < long_ma) and (rsi is None or rsi >= 70) and (price > lower_band if lower_band else True)

        print(f"Buy condition: {cond_buy}, Sell condition: {cond_sell}")

        if cond_buy:
            return 'buy'
        elif cond_sell:
            return 'sell'
        else:
            return 'hold'

    def generate_signal(self, market_data):
        return self.evaluate_market(market_data)

    async def execute_strategy(self, market_data, asset='DEFAULT'):
        signal = self.evaluate_market(market_data)

        if signal in ('buy', 'sell'):
            order = Order(
                symbol=asset,
                qty=self.trade_quantity,
                side=OrderSide[signal.upper()],
                order_type=OrderType.MARKET,
                price=market_data['close'][-1]
            )
            await self.order_manager.place_order(order)

        # RL tuning only if explicitly enabled
        if not self.inference_only:
            features = self.extract_features(market_data)
            dummy_trade_result = {'profit_pct': 0.01}
            reward = self.calculate_reward(dummy_trade_result)
            next_features = self.extract_features(market_data)
            self.rl_tune_strategy(features, reward, next_features)

        await asyncio.sleep(0)

    @staticmethod
    def compute_bollinger_bands(prices, window=20, num_std=2):
        if len(prices) < window:
            return None, None, None
        sma = np.mean(prices[-window:])
        std = np.std(prices[-window:])
        upper = sma + num_std * std
        lower = sma - num_std * std
        return lower, sma, upper

    def rl_tune_strategy(self, state, reward, next_state):
        if self.inference_only:
            return
        action = self.rl_agent.choose_action(state)
        # Adjust stop loss as example adaptive parameter tuning logic
        if action == 0:
            self.stop_loss_pct = max(0.01, (self.stop_loss_pct or 0.05) - 0.005)
        elif action == 1:
            self.stop_loss_pct = min(0.1, (self.stop_loss_pct or 0.05) + 0.005)

        self.rl_agent.memorize(state, action, reward, next_state, False)
        self.rl_agent.replay()

    def extract_features(self, market_data):
        closes = market_data.get('close', [])
        highs = market_data.get('high', [])
        lows = market_data.get('low', [])

        indicators = AdaptiveIndicators(closes, highs, lows)
        ema10 = indicators.adaptive_ema(span_base=10)[-1] if len(closes) >= 10 else 0
        rsi = indicators.compute_rsi(period=14)[-1] if len(closes) >= 14 else 0
        adx = indicators.compute_adx() or 0

        asset = market_data.get('asset', 'DEFAULT')
        position = self.order_manager.positions.get(asset, {}) if hasattr(self.order_manager, 'positions') else {}
        position_size = position.get('long', 0) - position.get('short', 0)

        return np.array([ema10, rsi, adx, position_size])

    def calculate_reward(self, trade_result):
        if trade_result and 'profit_pct' in trade_result:
            return trade_result['profit_pct']
        return 0

    async def on_market_data(self, market_data):
        signal = self.evaluate_market(market_data)
        if signal in ('buy', 'sell'):
            order = Order(
                symbol=market_data.get('asset', 'DEFAULT'),
                qty=self.trade_quantity,
                side=OrderSide[signal.upper()],
                order_type=OrderType.MARKET,
                price=market_data['close'][-1]
            )
            await self.order_manager.place_order(order)

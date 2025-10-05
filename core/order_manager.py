import asyncio
import time
import logging
from enum import Enum, auto
import numpy as np
import hashlib
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    PENDING = auto()
    FILLED = auto()
    PARTIAL = auto()
    CANCELLED = auto()
    REJECTED = auto()
    UNKNOWN = auto()

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"

@dataclass(frozen=True)
class IdempotencyKey:
    value: str

def _mk_idempotency_key(order_payload: dict) -> IdempotencyKey:
    canon = "|".join(str(order_payload.get(k)) for k in ("symbol","side","qty","order_type","price"))
    h = hashlib.sha256(canon.encode("utf-8")).hexdigest()
    return IdempotencyKey(h)

class Order:
    def __init__(self, symbol, qty, side: OrderSide, order_type: OrderType, price=None):
        self.symbol = symbol
        self.qty = qty
        self.side = side
        self.order_type = order_type
        self.price = price
        self.status = OrderStatus.PENDING
        self.filled_qty = 0
        self.placed_timestamp = None
        self.execution_report = []
        self.fills = []
        self.avg_fill_price = 0.0
        self.last_update = None

    def update_fill(self, fill_qty, fill_price, timestamp=None):
        self.filled_qty += fill_qty
        total_filled = self.filled_qty
        prev_value = self.avg_fill_price * (total_filled - fill_qty) if total_filled > fill_qty else 0.0
        self.avg_fill_price = (prev_value + fill_price * fill_qty) / total_filled if total_filled else 0.0
        self.fills.append((fill_qty, fill_price, timestamp or time.time()))
        self.last_update = timestamp or time.time()
        if self.filled_qty >= self.qty:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIAL

    def is_stale(self, timeout=60):
        now = time.time()
        return self.last_update and (now - self.last_update > timeout)

def model_slippage(order_size, avg_spread, volatility):
    baseline = avg_spread * np.random.uniform(1, 2)
    liquid_penalty = order_size * 0.00015
    vol_penalty = volatility * 0.35
    return baseline + liquid_penalty + vol_penalty

class LatencyCompensator:
    def __init__(self, lookback=50):
        self.latencies = []
        self.lookback = lookback

    def record(self, latency):
        self.latencies.append(latency)
        if len(self.latencies) > self.lookback:
            self.latencies = self.latencies[-self.lookback:]

    def avg_latency(self):
        return float(np.mean(self.latencies[-self.lookback:])) if self.latencies else 0.0

class OrderManager:
    def __init__(self, risk_manager=None, api_client=None, slippage=0.0, latency=0.0, config=None):
        self.risk_manager = risk_manager
        self.api_client = api_client
        self.slippage = slippage
        self.latency = latency
        self.active_orders = {}
        self.positions = {}  # Track positions by symbol with 'long' and 'short'
        self.latency_comp = LatencyCompensator()
        self.config = config or {}

        self._market_depth_lock = asyncio.Lock()
        self.order_book_cache = {}

        # idempotency/dedupe window (seconds)
        self._recent_keys = {}
        self._dedupe_window_sec = int(self.config.get("order_dedupe_window_sec", 10))

    async def place_order(self, order: Order, avg_spread=0.05, volatility=0.01):
        # Risk-managed maximum allowed size for symbol (async API)
        if self.risk_manager:
            try:
                max_pos = await self.risk_manager.position_size(order.symbol)  # risk_manager should expose async
            except TypeError:
                # fallback if risk_manager.position_size is sync
                max_pos = self.risk_manager.position_size(order.symbol)
            if max_pos and order.qty > max_pos:
                logger.warning(f"Order qty {order.qty} exceeds risk-managed position size {max_pos}. Order rejected.")
                order.status = OrderStatus.REJECTED
                return order

            # Panic-stop check
            if getattr(self.risk_manager, "is_panic", False):
                logger.error("PANIC STOP active — rejecting all orders")
                order.status = OrderStatus.REJECTED
                return order

            # Optional single-order value cap
            price_for_value = order.price or 0.0
            if hasattr(self.risk_manager, "max_single_order_value") and self.risk_manager.max_single_order_value:
                if abs(price_for_value * order.qty) > self.risk_manager.max_single_order_value:
                    logger.error("Order exceeds single-order value limit")
                    order.status = OrderStatus.REJECTED
                    return order

        # Build & check idempotency
        key = _mk_idempotency_key({
            "symbol": order.symbol,
            "side": order.side.value,
            "qty": order.qty,
            "order_type": order.order_type.value,
            "price": order.price,
        })
        now = time.time()
        if key.value in self._recent_keys and now - self._recent_keys[key.value] < self._dedupe_window_sec:
            logger.warning(f"Deduped duplicate order for {order.symbol} (idempotency={key.value})")
            order.status = OrderStatus.REJECTED
            return order

        order.placed_timestamp = now
        try:
            t0 = time.perf_counter()
            await asyncio.sleep(self.latency)

            slippage_amt = model_slippage(order.qty, avg_spread, volatility) if self.slippage else 0.0
            eff_price = order.price
            if order.order_type == OrderType.LIMIT and order.price:
                if order.side == OrderSide.BUY:
                    eff_price = order.price * (1 + slippage_amt)
                else:
                    eff_price = order.price * (1 - slippage_amt)

            api_kwargs = dict(
                symbol=order.symbol,
                quantity=order.qty,
                side=order.side.value,
                order_type=order.order_type.value,
                price=eff_price
            )
            # If broker supports it, pass idempotency key
            if self.api_client and hasattr(self.api_client, "send_order"):
                if "idempotency_key" in self.api_client.send_order.__code__.co_varnames:
                    api_kwargs["idempotency_key"] = key.value

            api_response = await self.api_client.send_order(**api_kwargs)

            fills = api_response.get('fills', [])
            if fills:
                for fill in fills:
                    qty = fill.get('qty', 0)
                    price = fill.get('price', eff_price)
                    ts = fill.get('timestamp', time.time())
                    order.update_fill(qty, price, ts)
            elif 'filled_qty' in api_response:
                qty = api_response['filled_qty']
                price = api_response.get('fill_price', eff_price)
                order.update_fill(qty, price)
            else:
                order.status = OrderStatus.UNKNOWN

            order.execution_report.append(api_response)
            self.active_orders[order.symbol] = order

            pos = self.positions.get(order.symbol, {'long': 0, 'short': 0})
            if order.side == OrderSide.BUY:
                pos['long'] += order.filled_qty
            else:
                pos['short'] += order.filled_qty
            self.positions[order.symbol] = pos

            elapsed = time.perf_counter() - t0
            self.latency_comp.record(elapsed)
            self._recent_keys[key.value] = now

        except Exception as e:
            logger.error(f"Order placement failure: {e}")
            order.status = OrderStatus.REJECTED

        logger.info(f"Order for {order.symbol} placed with status {order.status}")
        return order

    async def cancel_order(self, symbol):
        if symbol not in self.active_orders:
            logger.warning(f"No active order found to cancel for {symbol}")
            return False
        order = self.active_orders[symbol]
        try:
            await self.api_client.cancel_order(order_id=order.execution_report[-1].get('order_id'))
            order.status = OrderStatus.CANCELLED
            logger.info(f"Order cancelled for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order for {symbol}: {e}")
            return False

    async def hold_positions(self):
        try:
            positions = await self.api_client.get_positions()
            return positions
        except Exception as e:
            logger.error(f"Failed to fetch open positions: {e}")
            return []

    async def sweep_stale_orders(self, timeout=60):
        to_cancel = [sym for sym, order in self.active_orders.items() if order.is_stale(timeout)]
        for symbol in to_cancel:
            await self.cancel_order(symbol)
            logger.info(f"{symbol}: Cancelled as stale/partial order")

    async def update_market_depth(self, symbol, bid_price, bid_qty, ask_price, ask_qty, timestamp=None):
        async with self._market_depth_lock:
            self.order_book_cache[symbol] = {
                "bid_price": bid_price,
                "bid_quantity": bid_qty,
                "ask_price": ask_price,
                "ask_quantity": ask_qty,
                "timestamp": timestamp,
            }
            logger.debug(f"Updated market depth cache for {symbol}")

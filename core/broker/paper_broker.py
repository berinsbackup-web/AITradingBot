# core/broker/paper_broker.py
import time
from typing import Optional
from collections import defaultdict
from .base import IBroker


class PaperBroker(IBroker):
    """
    A simple in-memory paper broker for testing and validation.
    Fills all orders immediately at the provided price.
    """

    def __init__(self):
        self._orders: dict[str, dict] = {}
        self._positions = defaultdict(lambda: {"symbol": "", "qty": 0.0, "avg_price": 0.0})
        self._counter = 0

    # ----------------------------------------------------------------------
    # ✅ Modern IBroker interface
    async def place_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        order_type: str,
        price: Optional[float] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict:
        """Implements order placement with instant fills."""
        if idempotency_key and idempotency_key in self._orders:
            return self._orders[idempotency_key]

        self._counter += 1
        order_id = f"paper-{self._counter}"
        ts = time.time()
        fill_qty = float(quantity)
        fill_price = float(price or 0.0)

        # Update positions
        pos = self._positions[symbol]
        pos["symbol"] = symbol
        if side.upper() == "BUY":
            total_cost = pos["avg_price"] * pos["qty"] + fill_price * fill_qty
            pos["qty"] += fill_qty
            pos["avg_price"] = (total_cost / pos["qty"]) if pos["qty"] else 0.0
        else:  # SELL
            pos["qty"] -= fill_qty
            if pos["qty"] <= 0:
                pos["qty"] = 0.0
                pos["avg_price"] = 0.0

        resp = {
            "order_id": order_id,
            "status": "filled",
            "fills": [{"qty": fill_qty, "price": fill_price, "timestamp": ts}],
        }

        if idempotency_key:
            self._orders[idempotency_key] = resp

        return resp

    # ----------------------------------------------------------------------
    # ✅ Backward compatibility for older code (like OrderManager)
    async def send_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        order_type: str,
        price: Optional[float] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict:
        """Legacy wrapper to support older code."""
        return await self.place_order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            order_type=order_type,
            price=price,
            idempotency_key=idempotency_key,
        )

    async def cancel_order(self, order_id: str) -> dict:
        return {"order_id": order_id, "status": "cancelled"}

    async def get_positions(self) -> list[dict]:
        return list(self._positions.values())

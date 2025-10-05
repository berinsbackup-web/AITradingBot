# core/broker/base.py
from abc import ABC, abstractmethod
from typing import Optional

class IBroker(ABC):
    """Common broker interface for real and paper brokers."""

    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        order_type: str,
        price: Optional[float] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict:
        """Place an order with the broker."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> dict:
        """Cancel an active order."""
        pass

    @abstractmethod
    async def get_positions(self) -> list[dict]:
        """Retrieve all open positions."""
        pass

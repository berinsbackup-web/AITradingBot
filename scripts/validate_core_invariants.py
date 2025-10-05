import asyncio
from core.order_manager import OrderManager, Order, OrderSide, OrderType
from core.mock_risk_manager import MockRiskManager
from core.broker.paper_broker import PaperBroker


async def main():
    rm = MockRiskManager()
    om = OrderManager(
        risk_manager=rm,
        api_client=PaperBroker(),
        config={"order_dedupe_window_sec": 120}
    )

    # Duplicate orders should dedupe
    o1 = await om.place_order(Order("TEST", 1, OrderSide.BUY, OrderType.MARKET, price=100.0))
    o2 = await om.place_order(Order("TEST", 1, OrderSide.BUY, OrderType.MARKET, price=100.0))
    assert o1.status.name in ("FILLED", "PARTIAL", "PENDING")
    assert o2.status.name == "REJECTED"

    # Panic stop blocks all
    rm.trigger_panic("manual")
    o3 = await om.place_order(Order("TEST", 1, OrderSide.SELL, OrderType.MARKET, price=99.0))
    assert o3.status.name == "REJECTED"

    print("All core invariants hold.")


if __name__ == "__main__":
    asyncio.run(main())

import pytest
from core.broker.interfaces import BrokerInterface
from core.broker.paper_trading import PaperTradingBroker



def test_place_order_adds_order():
    broker = PaperTradingBroker()
    order_id = broker.place_order("AAPL", side="BUY", qty=10, price=150)
    assert order_id is not None
    assert len(broker.orders) == 1


def test_cancel_order_updates_status():
    broker = PaperTradingBroker()
    order_id = broker.place_order("AAPL", side="BUY", qty=10, price=150)
    assert broker.cancel_order(order_id)
    assert broker.orders[0]["status"] == "CANCELED"

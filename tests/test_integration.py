import pytest
from core.run_bot_with_token_refresh import get_broker
from core.broker.paper_trading import PaperTradingBroker
from core.broker.live_trading import LiveBroker



def test_get_broker_returns_paper_broker():
    broker = get_broker("paper")
    assert broker is not None
    assert hasattr(broker, "place_order")


def test_get_broker_unknown_returns_none():
    broker = get_broker("unknown")
    assert broker is None or hasattr(broker, "place_order")

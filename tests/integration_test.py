import pytest
from core.risk_manager import RiskManager
from core.order_manager import OrderManager
from core.ai_strategy import AIStrategy
from core.live_data_manager import LiveDataManager
from core.run_bot_with_token_refresh import get_broker
from core.broker.live_trading import LiveBroker
from core.broker.paper_trading import PaperTradingBroker



def test_get_broker_returns_instance():
    broker = get_broker("paper")
    assert broker is not None
    assert hasattr(broker, "place_order")


def test_risk_manager_allows_entry():
    rm = RiskManager(max_drawdown_limit=0.05)
    rm.current_drawdown = 0.01
    assert rm.can_enter_position("long")


def test_risk_manager_blocks_entry_on_drawdown():
    rm = RiskManager(max_drawdown_limit=0.05)
    rm.current_drawdown = 0.10
    assert not rm.can_enter_position("long")


def test_order_manager_has_required_methods():
    om = OrderManager()
    assert hasattr(om, "submit_order")
    assert hasattr(om, "cancel_order")


def test_ai_strategy_can_predict():
    strat = AIStrategy()
    assert hasattr(strat, "predict")


def test_live_data_manager_can_start_stream():
    ldm = LiveDataManager()
    assert hasattr(ldm, "start_stream")

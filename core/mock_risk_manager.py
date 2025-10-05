# core/mock_risk_manager.py
from core.interfaces import IRiskManager

class MockRiskManager(IRiskManager):
    """
    A mock risk manager for testing.
    Provides simple, fixed rules for position sizing and risk checks.
    """

    def __init__(self, default_position_size: float = 10.0):
        self._default_position_size = default_position_size
        self.is_panic = False                   # Panic-stop flag
        self.max_single_order_value = None      # Optional single order cap

    def update_risk_limits(self, limits):
        print(f"MockRiskManager: update_risk_limits {limits}")
        if "max_single_order_value" in limits:
            self.max_single_order_value = limits["max_single_order_value"]
        if "default_position_size" in limits:
            self._default_position_size = limits["default_position_size"]

    def check_risk(self, trade):
        print(f"MockRiskManager: check_risk for trade {trade}")
        return True

    async def position_size(self, symbol: str) -> float:
        """
        Return the maximum position size allowed for a given symbol.
        In this mock, we just return a fixed safe number.
        """
        return self._default_position_size

    # ------------------------------------------------------------------
    # ✅ Panic-stop control for testing
    def trigger_panic(self, reason: str = "manual"):
        """
        Engage panic-stop mode.
        All further orders will be rejected.
        """
        print(f"MockRiskManager: PANIC TRIGGERED due to {reason}")
        self.is_panic = True

    def reset_panic(self):
        """
        Reset panic-stop mode.
        """
        print("MockRiskManager: Panic reset")
        self.is_panic = False

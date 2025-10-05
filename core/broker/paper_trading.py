from core.brokers.interfaces import BrokerInterface

class PaperTradingBroker(BrokerInterface):
    def __init__(self):
        self.positions = {}

    def connect(self):
        print("PaperTradingBroker connected")

    def place_order(self, symbol, quantity, order_type):
        self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        print(f"[PaperTrading] Placed {order_type} order for {quantity} of {symbol}")
        return {"symbol": symbol, "quantity": quantity, "order_type": order_type}

    def cancel_order(self, order_id):
        print(f"[PaperTrading] Cancelled order {order_id}")
        return {"order_id": order_id, "cancelled": True}

    def get_order_status(self, order_id):
        print(f"[PaperTrading] Status for order {order_id}: Filled")
        return {"order_id": order_id, "status": "Filled"}

    def get_account_balance(self):
        return {"balance": 100000}

    def get_positions(self):
        return self.positions

    def close_position(self, symbol, quantity):
        if symbol in self.positions:
            self.positions[symbol] = max(0, self.positions[symbol] - quantity)
            print(f"[PaperTrading] Closed {quantity} of {symbol} position")
        return {"symbol": symbol, "quantity": quantity}

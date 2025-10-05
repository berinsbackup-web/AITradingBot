from core.brokers.interfaces import BrokerInterface

class LiveBroker(BrokerInterface):
    def __init__(self, token_manager, live_api):
        self.token_manager = token_manager
        self.live_api = live_api
        self.positions = {}

    def submit_order(self, side: str, qty: int, price: float):
        # Use live API to submit order with current token
        token = self.token_manager.get_token()
        response = self.live_api.place_order(token, side, qty, price)
        if response.get('success'):
            self.positions[side] = self.positions.get(side, 0) + qty
            print(f"[LiveTrading] Submitted {side} order qty={qty} at price={price}")
            return response
        else:
            print(f"[LiveTrading] Failed to submit order: {response.get('error')}")
            return response

    def get_positions(self):
        # Fetch current positions live from API
        token = self.token_manager.get_token()
        positions = self.live_api.fetch_positions(token)
        self.positions = positions
        return self.positions

    def close_position(self, side: str, qty: int):
        # Close position via live API
        token = self.token_manager.get_token()
        response = self.live_api.close_position(token, side, qty)
        if response.get('success'):
            self.positions[side] = max(0, self.positions.get(side, 0) - qty)
            print(f"[LiveTrading] Closed {qty} of {side} position")
            return response
        else:
            print(f"[LiveTrading] Failed to close position: {response.get('error')}")
            return response

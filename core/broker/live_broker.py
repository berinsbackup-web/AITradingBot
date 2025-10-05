from core.brokers.interfaces import BrokerInterface

class LiveBroker(BrokerInterface):
    def __init__(self, token_manager, live_api, base_url):
        self.token_manager = token_manager
        self.live_api = live_api
        self.base_url = base_url
        self.positions = {}

    def connect(self):
        print("LiveBroker connected")

    async def place_order(self, qty, order_type, side):
        print(f"Placing order: qty={qty}, order_type={order_type}, side={side}")
        response = await self.live_api.place_order(qty, order_type, side)
        return response

    async def cancel_order(self, order_id):
        print(f"Cancelling order id: {order_id}")
        response = await self.live_api.cancel_order(order_id)
        return response

    async def get_order_status(self, order_id):
        print(f"Getting status for order id: {order_id}")
        response = await self.live_api.get_order_status(order_id)
        return response

    def submit_order(self, side: str, qty: int, price: float):
        token = self.token_manager.get_token()
        response = self.live_api.place_order_sync(token, side, qty, price)
        if response.get('success'):
            self.positions[side] = self.positions.get(side, 0) + qty
            print(f"[LiveTrading] Submitted {side} order qty={qty} at price={price}")
        else:
            print(f"[LiveTrading] Failed to submit order: {response.get('error')}")
        return response

    def get_positions(self):
        token = self.token_manager.get_token()
        positions = self.live_api.fetch_positions(token)
        self.positions = positions
        return positions

    def close_position(self, side: str, qty: int):
        token = self.token_manager.get_token()
        response = self.live_api.close_position(token, side, qty)
        if response.get('success'):
            self.positions[side] = max(0, self.positions.get(side, 0) - qty)
            print(f"[LiveTrading] Closed {qty} of {side} position")
        else:
            print(f"[LiveTrading] Failed to close position: {response.get('error')}")
        return response

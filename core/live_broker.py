import requests

class LiveBroker:
    def __init__(self, api_key, access_token, base_url):
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = base_url

    def headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def place_order(self, symbol, qty, order_type, side, price=None):
        order_data = {
            "symbol": symbol,
            "qty": qty,
            "side": side,  # "BUY" or "SELL"
            "order_type": order_type,  # "MARKET" or "LIMIT"
            "price": price
        }
        r = requests.post(f"{self.base_url}/orders", headers=self.headers(), json=order_data)
        r.raise_for_status()
        return r.json()

    def fetch_order_status(self, order_id):
        r = requests.get(f"{self.base_url}/orders/{order_id}", headers=self.headers())
        r.raise_for_status()
        return r.json()

    def get_account_info(self):
        r = requests.get(f"{self.base_url}/account", headers=self.headers())
        r.raise_for_status()
        return r.json()

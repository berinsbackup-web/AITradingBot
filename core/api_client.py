import httpx
from core.config import TradingConfig
import logging
import asyncio
import functools

logger = logging.getLogger(__name__)

def retry_on_exception(max_retries=5, backoff_in_seconds=1):
    def decorator_retry(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    wait = backoff_in_seconds * (2 ** retries)
                    logger.warning(f"Exception {e}, retrying in {wait} seconds...")
                    await asyncio.sleep(wait)
                    retries += 1
            raise Exception(f"Failed after {max_retries} retries.")
        return wrapper
    return decorator_retry

class UpstoxApiClient:
    def __init__(self, config: TradingConfig):
        self.config = config
        self.base_url = "https://api.upstox.com/v2"
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def _send_request(self, method, endpoint, **kwargs):
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        auth_header = {"Authorization": f"Bearer {self.config.UPSTOX_ACCESS_TOKEN}"}
        headers.update(auth_header)

        try:
            response = await self._client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during API call: {e}")
            raise

    @retry_on_exception()
    async def get(self, endpoint, params=None):
        return await self._send_request("GET", endpoint, params=params)

    @retry_on_exception()
    async def post(self, endpoint, data=None, json=None):
        return await self._send_request("POST", endpoint, data=data, json=json)

    @retry_on_exception()
    async def put(self, endpoint, data=None, json=None):
        return await self._send_request("PUT", endpoint, data=data, json=json)

    @retry_on_exception()
    async def delete(self, endpoint):
        return await self._send_request("DELETE", endpoint)

    # Domain Specific Helper Methods

    async def send_order(self, symbol, quantity, side, order_type, price=None):
        """
        Places an order on Upstox. Adjust payload per Upstox API spec:
        symbol example: "NSE:RELIANCE"
        """
        exchange, sym = symbol.split(":")
        payload = {
            "exchange": exchange,
            "symbol": sym,
            "transaction_type": side,
            "quantity": quantity,
            "order_type": order_type,
            "product": "I",  # sample product code
            "duration": "DAY",
        }
        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Limit order requires price")
            payload["price"] = price

        endpoint = "/orders"
        response = await self.post(endpoint, json=payload)
        logger.debug(f"Placed order {payload} response: {response}")
        return response

    async def cancel_order(self, order_id):
        endpoint = f"/orders/{order_id}/cancel"
        response = await self.post(endpoint)
        logger.debug(f"Cancelled order {order_id} response: {response}")
        return response

    async def get_positions(self):
        endpoint = "/positions"
        response = await self.get(endpoint)
        logger.debug(f"Positions response: {response}")
        return response.get("data", {}).get("net_positions", [])

    async def get_order_book(self):
        endpoint = "/orderbook"
        response = await self.get(endpoint)
        logger.debug(f"Order book response: {response}")
        return response.get("data", [])

    async def get_live_quotes(self, symbols):
        endpoint = "/quotes"
        params = {"symbols": ",".join(symbols)}
        response = await self.get(endpoint, params=params)
        logger.debug(f"Live quotes for {symbols} response: {response}")
        return response.get("data", [])

    async def close(self):
        await self._client.aclose()

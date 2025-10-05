import os
import json
import asyncio
import aiohttp
import websockets
from dotenv import load_dotenv

class MarketDataManager:
    def __init__(self, config):
        load_dotenv()  # Load vars from .env into environment
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("UPSTOX_ACCESS_TOKEN not set in environment variables")
        self.ws_url = None
        self.subscribed_symbols = set()
        self.config = config

    async def fetch_authorized_ws_url(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }
        authorize_url = "https://api.upstox.com/api/market-data-feed/authorize/v3"
        async with aiohttp.ClientSession() as session:
            async with session.get(authorize_url, headers=headers) as response:
                text = await response.text()
                print(f"DEBUG: Status: {response.status}, Response Body: {text}")
                if response.status == 200:
                    data = await response.json()
                    self.ws_url = data["data"]["authorized_redirect_uri"]
                    print(f"Authorized WebSocket URI obtained: {self.ws_url}")
                elif response.status == 401:
                    print("Authorization failed: Invalid or expired token.")
                elif response.status == 404:
                    print("API endpoint not found; verify the URL.")
                else:
                    print(f"Failed to authorize WebSocket URI: {response.status}")
                    self.ws_url = None

    async def start(self):
        await self.fetch_authorized_ws_url()
        if not self.ws_url:
            print("WebSocket URL not available, aborting connection.")
            return

        async with websockets.connect(self.ws_url) as websocket:
            await self._subscribe_to_symbols(websocket)
            await self._receive_market_data(websocket)

    async def _subscribe_to_symbols(self, websocket):
        for symbol in self.subscribed_symbols:
            subscribe_packet = json.dumps({
                "action": "subscribe",
                "symbol": symbol
            })
            await websocket.send(subscribe_packet)
            print(f"Sent subscribe request for {symbol}")

    async def _receive_market_data(self, websocket):
        async for message in websocket:
            data = json.loads(message)
            print(f"Received market data: {data}")

    def subscribe(self, symbol: str):
        self.subscribed_symbols.add(symbol)
        print(f"Subscribed to symbol: {symbol}")

    def unsubscribe(self, symbol: str):
        self.subscribed_symbols.discard(symbol)
        print(f"Unsubscribed from symbol: {symbol}")

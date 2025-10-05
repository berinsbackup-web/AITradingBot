import asyncio
import websockets
import json
import logging
from typing import List, AsyncGenerator


logger = logging.getLogger(__name__)


class UpstoxStreamClient:
    def __init__(self, access_token: str, ws_url: str = "wss://uat-esocket9.tickertape.in/"):
        self.ws_url = ws_url
        self.access_token = access_token
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        auth_msg = json.dumps({
            "type": "authorization",
            "access_token": self.access_token
        })
        await self.ws.send(auth_msg)
        logger.info("Connected to Upstox WebSocket and sent authorization.")

    async def subscribe(self, symbols: List[str]):
        # symbols format: ["NSE:RELIANCE", "NSE:TCS"]
        sub_msg = json.dumps({
            "type": "subscribe",
            "symbol": symbols
        })
        await self.ws.send(sub_msg)
        logger.info(f"Subscribed to symbols: {symbols}")

    async def receive(self) -> AsyncGenerator[dict, None]:
        try:
            while True:
                message = await self.ws.recv()
                data = json.loads(message)
                logger.debug(f"Received message: {data}")
                yield data
        except websockets.ConnectionClosed:
            logger.warning("WebSocket connection closed.")
        except Exception as e:
            logger.error(f"Error receiving WebSocket messages: {e}")

    async def disconnect(self):
        if self.ws:
            await self.ws.close()
            logger.info("Disconnected WebSocket connection.")

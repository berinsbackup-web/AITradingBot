import asyncio
import threading
import websockets
from core import upstox_protobuf_decoder

class UpstoxWebSocketClient:
    def __init__(self, ws_url, message_handler):
        self.ws_url = ws_url
        self.stop_event = threading.Event()
        self.message_handler = message_handler  # Callback to process decoded messages

    async def websocket_consumer(self):
        async with websockets.connect(self.ws_url) as websocket:
            while not self.stop_event.is_set():
                try:
                    msg_bytes = await websocket.recv()
                    # For demo assume bars message type, extend logic to determine type as needed
                    decoded_msg = upstox_protobuf_decoder.decode_upstox_message(msg_bytes, "bars")
                    self.message_handler(decoded_msg)
                except Exception as e:
                    print(f"WebSocket error: {e}")
                    break

    def start(self):
        self.stop_event.clear()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.websocket_consumer())
        finally:
            loop.close()

    def stop(self):
        self.stop_event.set()

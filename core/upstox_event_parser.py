import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def parse_upstox_message(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parses raw JSON streaming message from Upstox WebSocket into 
    a normalized event dict your trading bot can consume.

    Returns None if message is not useful.
    """

    msg_type = message.get("type")

    if msg_type == "trade":
        # Trade message
        event = {
            "event": "trade",
            "symbol": message.get("symbol"),
            "price": float(message.get("price", 0)),
            "quantity": int(message.get("quantity", 0)),
            "timestamp": message.get("timestamp"),
        }
        return event

    elif msg_type == "quote":
        # Quote / market depth update
        event = {
            "event": "quote",
            "symbol": message.get("symbol"),
            "bid_price": float(message.get("bidPrice", 0)),
            "bid_quantity": int(message.get("bidQuantity", 0)),
            "ask_price": float(message.get("askPrice", 0)),
            "ask_quantity": int(message.get("askQuantity", 0)),
            "timestamp": message.get("timestamp"),
        }
        return event

    elif msg_type == "ohlc":
        # OHLC price update
        event = {
            "event": "ohlc",
            "symbol": message.get("symbol"),
            "open": float(message.get("open", 0)),
            "high": float(message.get("high", 0)),
            "low": float(message.get("low", 0)),
            "close": float(message.get("close", 0)),
            "volume": int(message.get("volume", 0)),
            "timestamp": message.get("timestamp"),
        }
        return event

    elif msg_type == "heartbeat":
        # Ignore heartbeat
        return None

    else:
        logger.debug(f"Ignored unrecognized message type: {msg_type}")
        return None

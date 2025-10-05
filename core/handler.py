import logging

logger = logging.getLogger(__name__)

# Example of a handler that sends trade events to AI strategy manager
async def trade_event_handler(event, strategy_manager):
    symbol = event.get("symbol")
    price = event.get("price")
    quantity = event.get("quantity")
    timestamp = event.get("timestamp")

    logger.info(f"Trade event received for {symbol} at {price} qty {quantity}")

    # Example: pass data to your AI strategy manager for decision making
    await strategy_manager.on_trade(symbol, price, quantity, timestamp)

# Example of a handler for quote updates, which might update order book
async def quote_event_handler(event, order_manager):
    symbol = event.get("symbol")
    bid_price = event.get("bid_price")
    bid_qty = event.get("bid_quantity")
    ask_price = event.get("ask_price")
    ask_qty = event.get("ask_quantity")
    timestamp = event.get("timestamp")

    logger.info(f"Quote update for {symbol}: bid {bid_price}x{bid_qty}, ask {ask_price}x{ask_qty}")

    # Update order manager market data cache/state
    await order_manager.update_market_depth(symbol, bid_price, bid_qty, ask_price, ask_qty, timestamp)

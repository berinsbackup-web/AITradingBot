import asyncio
import logging
from core.event_queue import EventQueue
from core.live_broker import LiveBroker

logger = logging.getLogger(__name__)

class StrategyManager:
    def __init__(self, strategy, risk_manager, order_manager, portfolio, live_broker: LiveBroker = None):
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.order_manager = order_manager
        self.portfolio = portfolio
        self.live_broker = live_broker

        self._trade_lock = asyncio.Lock()
        self._trade_queue = asyncio.Queue()
        self._trade_worker_task = asyncio.create_task(self._trade_worker())

        self._market_data_lock = asyncio.Lock()

        self.event_queue = EventQueue()
        self._event_task = asyncio.create_task(self._process_events())

        self._shutdown_event = asyncio.Event()

    async def _trade_worker(self):
        while not self._shutdown_event.is_set():
            try:
                event = await self._trade_queue.get()
                try:
                    # Forward trade event to strategy's on_trade method
                    await self.strategy.on_trade(
                        event["symbol"],
                        event["price"],
                        event["quantity"],
                        event.get("timestamp")
                    )
                    # Optionally place order via live broker
                    if self.live_broker:
                        response = await self.live_broker.place_order(
                            symbol=event["symbol"],
                            qty=event["quantity"],
                            order_type="MARKET",
                            side="BUY" if event["quantity"] > 0 else "SELL"
                        )
                        logger.info(f"Placed live order: {response}")
                except Exception as e:
                    logger.error(f"Error processing trade in strategy: {e}")
                finally:
                    self._trade_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in trade worker: {e}")

    async def on_trade(self, symbol, price, quantity, timestamp=None):
        await self._trade_queue.put({
            "symbol": symbol,
            "price": price,
            "quantity": quantity,
            "timestamp": timestamp
        })

    async def on_market_data(self, market_data_snapshot):
        async with self._market_data_lock:
            try:
                await self.strategy.on_market_data(market_data_snapshot)
            except Exception as e:
                logger.error(f"Error processing market data: {e}")

    async def _process_events(self):
        async def handler(event):
            if event.type == "trade":
                payload = event.payload
                await self.on_trade(
                    payload.get("symbol"),
                    payload.get("price"),
                    payload.get("quantity"),
                    payload.get("timestamp")
                )
            elif event.type == "market_data":
                await self.on_market_data(event.payload)
            else:
                logger.warning(f"Unhandled event in StrategyManager: {event.type}")

        try:
            await self.event_queue.process_events(handler)
        except asyncio.CancelledError:
            logger.info("Event processing cancelled.")
        except Exception as e:
            logger.error(f"Error in event processing: {e}")

    async def shutdown(self):
        logger.info("Shutting down StrategyManager...")
        self._shutdown_event.set()
        self._trade_worker_task.cancel()
        self._event_task.cancel()
        try:
            await self._trade_worker_task
            await self._event_task
        except asyncio.CancelledError:
            pass
        logger.info("StrategyManager shutdown complete.")

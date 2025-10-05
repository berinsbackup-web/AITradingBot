import asyncio

class LiveDataManager:
    def __init__(self, config):
        self.config = config
        self._callbacks = []
        self._running = False

    def subscribe(self, callback):
        """Register a callback to receive MarketDataSnapshot dicts."""
        self._callbacks.append(callback)

    async def start(self):
        self._running = True
        # Setup connection to live market data feed here
        while self._running:
            raw_data = await self._get_next_tick()
            snapshot = self._convert_to_snapshot(raw_data)
            for cb in self._callbacks:
                await cb(snapshot)

    async def stop(self):
        self._running = False

    async def _get_next_tick(self):
        # Implementation: receive next raw tick/bar data from feed
        pass

    def _convert_to_snapshot(self, raw_data):
        # Convert raw tick/bar to unified MarketDataSnapshot dict
        snapshot = {
            'symbol': raw_data.get('symbol'),
            'timestamp': raw_data.get('timestamp'),
            'open': raw_data.get('open_series'),
            'high': raw_data.get('high_series'),
            'low': raw_data.get('low_series'),
            'close': raw_data.get('close_series'),
            'volume': raw_data.get('volume_series'),
        }
        return snapshot

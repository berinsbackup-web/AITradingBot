import asyncio
import logging
from typing import Callable, Dict, Any, List

logger = logging.getLogger(__name__)

class EventDispatcher:
    def __init__(self):
        self._handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Handler registered for event type: {event_type}")

    async def dispatch(self, event: Dict[str, Any]):
        event_type = event.get("event")
        if not event_type:
            logger.warning("Received event without 'event' key to dispatch")
            return

        handlers = self._handlers.get(event_type, [])
        if not handlers:
            logger.debug(f"No handlers registered for event type: {event_type}")
            return

        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error in handler for event {event_type}: {e}")

import asyncio

class Event:
    def __init__(self, event_type, payload=None):
        self.type = event_type
        self.payload = payload

class EventQueue:
    def __init__(self, maxsize=1000):
        self.queue = asyncio.Queue(maxsize=maxsize)

    async def put(self, event):
        await self.queue.put(event)

    async def get(self):
        event = await self.queue.get()
        self.queue.task_done()
        return event

    async def process_events(self, handler):
        while True:
            event = await self.get()
            await handler(event)

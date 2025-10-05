import asyncio
from core.interfaces import IOrderManager

class MockOrderManager(IOrderManager):
    async def place_order(self, order_data):
        await asyncio.sleep(0.1)
        return {"order_id": "mock123", "status": "placed", "details": order_data}

    async def modify_order(self, order_id, update_data):
        await asyncio.sleep(0.1)
        return {"order_id": order_id, "status": "modified", "updates": update_data}

    async def cancel_order(self, order_id):
        await asyncio.sleep(0.1)
        return {"order_id": order_id, "status": "cancelled"}

    async def get_order_status(self, order_id):
        await asyncio.sleep(0.1)
        return {"order_id": order_id, "status": "filled"}

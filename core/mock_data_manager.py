import asyncio
from core.interfaces import IDataManager

class MockDataManager(IDataManager):
    def fetch_data(self, symbol: str, start: str, end: str):
        print(f"MockDataManager: fetching data for {symbol} from {start} to {end}")
        return {}

    def store_data(self, symbol: str, data):
        print(f"MockDataManager: storing data for {symbol}")

from core.interfaces import IDataManager

class LiveDataManager(IDataManager):
    def __init__(self):
        self.callbacks = []

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def fetch_data(self):
        # Dummy implementation, extend as needed
        pass

    def store_data(self):
        # Dummy implementation, extend as needed
        pass

    def get_latest_data(self):
        # Return sample data for testing
        return {"close": [100, 101, 102, 103, 104]}

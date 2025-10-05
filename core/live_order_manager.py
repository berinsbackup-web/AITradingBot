from core.interfaces import IDataManager

class LiveDataManager(IDataManager):
    def __init__(self):
        self.callbacks = []

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def fetch_data(self):
        # implement real fetching or mock logic
        pass

    def store_data(self):
        # implement real storage or mock logic
        pass

    def get_latest_data(self):
        return {"close": [100, 101, 102, 103, 104]}

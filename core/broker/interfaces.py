from abc import ABC, abstractmethod

class BrokerInterface(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def place_order(self, symbol: str, quantity: int, order_type: str):
        pass

    @abstractmethod
    def cancel_order(self, order_id: str):
        pass

    @abstractmethod
    def get_order_status(self, order_id: str):
        pass

    @abstractmethod
    def get_account_balance(self):
        pass

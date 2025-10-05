from abc import ABC, abstractmethod

class IStrategyManager(ABC):
    @abstractmethod
    def run_strategy(self, strategy_name: str):
        pass

    @abstractmethod
    def stop_strategy(self, strategy_name: str):
        pass

    @abstractmethod
    def get_strategy_status(self, strategy_name: str):
        pass


class IDataManager(ABC):
    @abstractmethod
    def fetch_data(self, symbol: str, start: str, end: str):
        pass

    @abstractmethod
    def store_data(self, symbol: str, data):
        pass

class IOrderManager(ABC):
    @abstractmethod
    def place_order(self, symbol: str, quantity: int, price: float):
        pass

    @abstractmethod
    def cancel_order(self, order_id: int):
        pass

class IPortfolioManager(ABC):
    @abstractmethod
    def get_portfolio(self):
        pass

    @abstractmethod
    def update_portfolio(self, trades):
        pass
class IRiskManager(ABC):
    @abstractmethod
    def update_risk_limits(self, limits):
        pass

    @abstractmethod
    def check_risk(self, trade):
        pass
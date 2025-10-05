import time
from core.oauth_token_manager import OAuthTokenManager
from core.ai_strategy import AIStrategy
from core.risk_manager import RiskManager
from core.order_manager import OrderManager
from live_data_manager import LiveDataManager
from core.broker_api import BrokerAPI  # Your broker's API wrapper
from logger import setup_logger

logger = setup_logger(__name__)

def main():
    auth_api = BrokerAPI.AuthAPI()
    token_manager = OAuthTokenManager(auth_api)
    broker_api = BrokerAPI(token_manager)
    risk_manager = RiskManager()
    order_manager = OrderManager(broker_api)
    ai_strategy = AIStrategy(risk_manager, order_manager)
    live_data_manager = LiveDataManager()

    logger.info('Starting trading bot...')
    while True:
        try:
            token_manager.get_token()
            market_data = live_data_manager.get_latest_data()
            ai_strategy.execute_strategy(market_data)
            order_manager.update_order_status()
        except Exception as e:
            logger.error(f"Error in bot loop: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()

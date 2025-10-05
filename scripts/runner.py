import time
from core.run_bot_with_token_refresh import main as run_bot_main
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Trading Bot Runner")
    try:
        run_bot_main()
    except Exception as e:
        logger.error(f"Unexpected error in main runner: {e}")
        raise e

if __name__ == '__main__':
    main()

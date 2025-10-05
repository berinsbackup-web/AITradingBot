# core/upstox_protobuf_decoder.py

import json
import logging

logger = logging.getLogger(__name__)

def decode_message(raw_data):
    """
    Decode raw market message data assumed to be JSON string or dict.
    Returns a dict representing the parsed market data.

    Fallback to empty dict if JSON parsing fails.
    """
    if isinstance(raw_data, bytes):
        try:
            raw_data = raw_data.decode('utf-8')
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error: {e}")
            return {}

    if isinstance(raw_data, str):
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {}
    elif isinstance(raw_data, dict):
        data = raw_data
    else:
        logger.error(f"Unsupported raw_data type: {type(raw_data)}")
        data = {}

    return data

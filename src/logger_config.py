"""
Configures logging for the breach screening application,
including log format and log levels.
"""

import logging

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler("screening_service.log"),
            logging.StreamHandler()
        ]
    )
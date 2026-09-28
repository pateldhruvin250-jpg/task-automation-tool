"""Centralized logging configuration so every module logs consistently."""

import logging
import os

from src.config import Config


def setup_logging():
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    log_file = os.path.join(Config.LOGS_DIR, "automation.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )

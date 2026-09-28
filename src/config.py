"""
Configuration loader for the Currency Exchange Rate Automation Tool.

Values can be overridden with environment variables, which makes the
tool safe to run in different environments (dev laptop, CI, cron server)
without editing code.
"""

import os


class Config:
    # Third-party API (Frankfurter — free, no API key required)
    API_BASE_URL = os.getenv("EXCHANGE_API_BASE_URL", "https://api.frankfurter.app")

    # Base currency and the currencies we track against it
    BASE_CURRENCY = os.getenv("BASE_CURRENCY", "USD")
    TARGET_CURRENCIES = os.getenv("TARGET_CURRENCIES", "INR,EUR,GBP").split(",")

    # If a tracked rate moves beyond this percentage since the last run,
    # the tool flags it as a notable change in the report/log.
    ALERT_THRESHOLD_PERCENT = float(os.getenv("ALERT_THRESHOLD_PERCENT", "1.0"))

    # Local storage
    DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data.db"))
    REPORTS_DIR = os.getenv("REPORTS_DIR", os.path.join(os.path.dirname(__file__), "..", "reports"))
    LOGS_DIR = os.getenv("LOGS_DIR", os.path.join(os.path.dirname(__file__), "..", "logs"))

    # Network resilience
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_BACKOFF_SECONDS = float(os.getenv("RETRY_BACKOFF_SECONDS", "2"))

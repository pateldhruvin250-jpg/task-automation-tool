"""
Handles all communication with the third-party exchange-rate API.

Isolating network calls in one module keeps the rest of the tool easy
to unit test (we mock this module instead of the network itself).
"""

import logging
import time

import requests

from src.config import Config

logger = logging.getLogger("task_automation.fetcher")


class ExchangeRateFetchError(Exception):
    """Raised when the exchange rate API cannot be reached or returns bad data."""


def fetch_latest_rates(base_currency: str = None, target_currencies: list = None) -> dict:
    """
    Fetch the latest exchange rates for the configured currencies.

    Retries with exponential backoff on network failure, since flaky
    connections are the most common real-world failure mode for an
    automation tool like this.

    Returns:
        dict like {"base": "USD", "date": "2026-09-27", "rates": {"INR": 83.2, ...}}
    """
    base_currency = base_currency or Config.BASE_CURRENCY
    target_currencies = target_currencies or Config.TARGET_CURRENCIES

    params = {
        "from": base_currency,
        "to": ",".join(target_currencies),
    }

    last_error = None
    for attempt in range(1, Config.MAX_RETRIES + 1):
        try:
            logger.info(
                "Fetching rates (attempt %d/%d) base=%s targets=%s",
                attempt, Config.MAX_RETRIES, base_currency, target_currencies,
            )
            response = requests.get(
                f"{Config.API_BASE_URL}/latest",
                params=params,
                timeout=Config.REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()

            if "rates" not in data:
                raise ExchangeRateFetchError(f"Unexpected API response shape: {data}")

            return {
                "base": data.get("base", base_currency),
                "date": data.get("date"),
                "rates": data["rates"],
            }

        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            logger.warning("Fetch attempt %d failed: %s", attempt, exc)
            if attempt < Config.MAX_RETRIES:
                time.sleep(Config.RETRY_BACKOFF_SECONDS * attempt)

    raise ExchangeRateFetchError(
        f"Failed to fetch exchange rates after {Config.MAX_RETRIES} attempts: {last_error}"
    )

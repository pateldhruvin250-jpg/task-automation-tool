import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.fetcher import fetch_latest_rates, ExchangeRateFetchError


class TestFetcher(unittest.TestCase):

    @patch("src.fetcher.requests.get")
    def test_fetch_latest_rates_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "base": "USD",
            "date": "2026-09-27",
            "rates": {"INR": 83.12, "EUR": 0.91},
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_latest_rates("USD", ["INR", "EUR"])

        self.assertEqual(result["base"], "USD")
        self.assertEqual(result["rates"]["INR"], 83.12)
        mock_get.assert_called_once()

    @patch("src.fetcher.requests.get")
    def test_fetch_retries_then_raises(self, mock_get):
        mock_get.side_effect = Exception("network down")

        with self.assertRaises(Exception):
            fetch_latest_rates("USD", ["INR"])

    @patch("src.fetcher.requests.get")
    def test_fetch_raises_on_bad_shape(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"unexpected": "shape"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertRaises(ExchangeRateFetchError):
            fetch_latest_rates("USD", ["INR"])


if __name__ == "__main__":
    unittest.main()

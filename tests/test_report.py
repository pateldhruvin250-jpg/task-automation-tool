import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.report import build_report_rows


class TestReport(unittest.TestCase):

    def test_flags_large_change(self):
        rows = build_report_rows(
            "USD",
            rates={"INR": 85.0},
            previous_rates={"INR": 83.0},
        )
        self.assertTrue(rows[0]["flagged"])
        self.assertAlmostEqual(rows[0]["change_percent"], 2.4096, places=3)

    def test_no_flag_for_small_change(self):
        rows = build_report_rows(
            "USD",
            rates={"INR": 83.1},
            previous_rates={"INR": 83.0},
        )
        self.assertFalse(rows[0]["flagged"])

    def test_handles_no_previous_rate(self):
        rows = build_report_rows(
            "USD",
            rates={"INR": 83.0},
            previous_rates={"INR": None},
        )
        self.assertIsNone(rows[0]["change_percent"])
        self.assertFalse(rows[0]["flagged"])


if __name__ == "__main__":
    unittest.main()

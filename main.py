#!/usr/bin/env python3
"""
Currency Exchange Rate Tracker & Report Automation Tool
--------------------------------------------------------
Fetches live exchange rates from a third-party API (Frankfurter),
compares them to the previously stored rates, flags significant
moves, and generates CSV + JSON reports automatically.

This automates a task that would otherwise be manual: checking
rates, comparing to last time, and writing up a summary.

Usage:
    python main.py
    python main.py --base USD --targets INR,EUR,GBP,JPY
    python main.py --schedule daily     (prints the cron line to use)
"""

import argparse
import logging
import sys

from src.config import Config
from src.logger_setup import setup_logging
from src.fetcher import fetch_latest_rates, ExchangeRateFetchError
from src.storage import init_db, save_rates, get_previous_rate
from src.report import build_report_rows, write_csv_report, write_json_report

logger = logging.getLogger("task_automation.main")


def parse_args():
    parser = argparse.ArgumentParser(description="Exchange rate automation tool")
    parser.add_argument("--base", default=Config.BASE_CURRENCY, help="Base currency, e.g. USD")
    parser.add_argument(
        "--targets",
        default=",".join(Config.TARGET_CURRENCIES),
        help="Comma-separated target currencies, e.g. INR,EUR,GBP",
    )
    parser.add_argument(
        "--schedule",
        choices=["daily", "hourly"],
        help="Print a ready-to-use cron expression for the chosen frequency and exit",
    )
    return parser.parse_args()


def print_schedule_hint(frequency: str):
    cron_line = {
        "hourly": "0 * * * *",
        "daily": "0 9 * * *",
    }[frequency]
    script_path = __file__
    print(f"# Add this line with `crontab -e` to run {frequency}:")
    print(f"{cron_line} /usr/bin/python3 {script_path}")


def run(base_currency: str, target_currencies: list) -> int:
    init_db()

    try:
        result = fetch_latest_rates(base_currency, target_currencies)
    except ExchangeRateFetchError as exc:
        logger.error("Could not complete run: %s", exc)
        return 1

    previous_rates = {
        currency: get_previous_rate(base_currency, currency)
        for currency in result["rates"]
    }

    rows = build_report_rows(base_currency, result["rates"], previous_rates)
    save_rates(base_currency, result["rates"])

    csv_path = write_csv_report(rows)
    json_path = write_json_report(rows)

    flagged = [r for r in rows if r["flagged"]]
    logger.info(
        "Run complete. %d currencies tracked, %d flagged for notable change.",
        len(rows), len(flagged),
    )
    if flagged:
        for r in flagged:
            logger.warning(
                "ALERT: %s/%s moved %.2f%% (now %.4f, was %.4f)",
                base_currency, r["target_currency"], r["change_percent"],
                r["rate"], r["previous_rate"],
            )

    print(f"Reports written:\n  {csv_path}\n  {json_path}")
    return 0


if __name__ == "__main__":
    setup_logging()
    args = parse_args()

    if args.schedule:
        print_schedule_hint(args.schedule)
        sys.exit(0)

    targets = [c.strip().upper() for c in args.targets.split(",") if c.strip()]
    sys.exit(run(args.base.upper(), targets))

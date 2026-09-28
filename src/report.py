"""
Turns fetched + analyzed rate data into human-readable report files.
This is the "reduce repetitive manual work" part of the tool: instead
of someone checking rates and typing up a note by hand, the tool
produces a ready-to-share CSV and JSON report automatically.
"""

import csv
import json
import logging
import os
from datetime import datetime

from src.config import Config

logger = logging.getLogger("task_automation.report")


def _ensure_reports_dir():
    os.makedirs(Config.REPORTS_DIR, exist_ok=True)


def build_report_rows(base_currency: str, rates: dict, previous_rates: dict) -> list:
    """
    Combine current + previous rates into report rows and flag any
    currency that moved beyond the configured alert threshold.
    """
    rows = []
    for currency, rate in rates.items():
        previous = previous_rates.get(currency)
        change_percent = None
        flagged = False

        if previous:
            change_percent = round(((rate - previous) / previous) * 100, 4)
            flagged = abs(change_percent) >= Config.ALERT_THRESHOLD_PERCENT

        rows.append({
            "base_currency": base_currency,
            "target_currency": currency,
            "rate": rate,
            "previous_rate": previous,
            "change_percent": change_percent,
            "flagged": flagged,
        })
    return rows


def write_csv_report(rows: list, timestamp: str = None) -> str:
    _ensure_reports_dir()
    timestamp = timestamp or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(Config.REPORTS_DIR, f"exchange_report_{timestamp}.csv")

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "base_currency", "target_currency", "rate",
            "previous_rate", "change_percent", "flagged",
        ])
        writer.writeheader()
        writer.writerows(rows)

    logger.info("CSV report written to %s", path)
    return path


def write_json_report(rows: list, timestamp: str = None) -> str:
    _ensure_reports_dir()
    timestamp = timestamp or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(Config.REPORTS_DIR, f"exchange_report_{timestamp}.json")

    with open(path, "w") as f:
        json.dump({"generated_at": timestamp, "rows": rows}, f, indent=2)

    logger.info("JSON report written to %s", path)
    return path

# Currency Exchange Rate Tracker & Report Automation Tool

A Python automation tool that fetches live exchange rates from a
third-party API, stores history locally, flags notable rate changes,
and automatically generates CSV/JSON reports — removing the need to
manually check and log rates.

## Features

- Fetches live exchange rates from the [Frankfurter API](https://www.frankfurter.app/) (free, no API key required)
- Retry logic with exponential backoff for network resilience
- Stores historical rates locally in SQLite
- Compares each run against the previous one and flags moves above a configurable threshold
- Auto-generates timestamped CSV and JSON reports
- Structured logging to both console and a log file
- Ready to schedule via cron (Linux/Mac) or Task Scheduler (Windows)
- Fully unit tested with mocked network calls (no internet needed to run tests)

## Tech Stack

Python 3, `requests`, `sqlite3` (standard library), `unittest`

## Project Structure

```
task-automation-tool/
├── main.py                # CLI entry point
├── src/
│   ├── config.py           # Environment-driven configuration
│   ├── fetcher.py           # Third-party API integration + retry logic
│   ├── storage.py           # SQLite persistence
│   ├── report.py            # CSV/JSON report generation
│   └── logger_setup.py      # Logging configuration
├── tests/
│   ├── test_fetcher.py
│   └── test_report.py
├── reports/                # Generated reports land here
├── logs/                   # Generated logs land here
└── requirements.txt
```

## Setup

```bash
git clone <your-repo-url>
cd task-automation-tool
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
# Run once with default currencies (INR, EUR, GBP against USD)
python main.py

# Run with custom base/target currencies
python main.py --base USD --targets INR,EUR,GBP,JPY

# Print a cron line to schedule it
python main.py --schedule daily
```

Reports are written to `reports/` as `exchange_report_<timestamp>.csv`
and `.json`. Logs are written to `logs/automation.log`.

## Scheduling (example)

```bash
crontab -e
# Run every day at 9 AM
0 9 * * * /usr/bin/python3 /path/to/task-automation-tool/main.py
```

## Running Tests

```bash
python -m unittest discover -s tests -v
```

All network calls are mocked in the test suite, so tests run without
internet access.

## Possible Extensions

- Send email/Slack alerts when a flagged change is detected
- Swap SQLite for MySQL/PostgreSQL for multi-user deployments
- Add more data sources (stocks, crypto) using the same fetch/report pattern

#!/usr/bin/env python3
"""Export Luthor logs via the API and publish them to Google Sheets."""

from __future__ import annotations

import argparse
import csv
import io
import os
import sys
from datetime import date, timedelta

import gspread
import httpx
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def fetch_export(
    *,
    api_url: str,
    export_token: str,
    table: str,
    export_format: str,
    start_date: date | None,
    end_date: date | None,
) -> bytes:
    params: dict[str, str] = {"table": table, "format": export_format}
    if start_date is not None:
        params["start_date"] = start_date.isoformat()
    if end_date is not None:
        params["end_date"] = end_date.isoformat()

    with httpx.Client(base_url=api_url, timeout=60.0) as client:
        response = client.get(
            "/export/logs",
            params=params,
            headers={"X-Export-Token": export_token},
        )
        response.raise_for_status()
        return response.content


def csv_bytes_to_rows(content: bytes) -> list[list[str]]:
    text = content.decode("utf-8")
    reader = csv.reader(io.StringIO(text))
    return [row for row in reader]


def publish_to_sheet(
    *,
    credentials_path: str,
    spreadsheet_name: str,
    worksheet_name: str,
    rows: list[list[str]],
) -> str:
    credentials = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    client = gspread.authorize(credentials)

    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=26)

    worksheet.clear()
    if rows:
        worksheet.update(rows, value_input_option="RAW")

    return spreadsheet.url


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Luthor logs to Google Sheets")
    parser.add_argument("--api-url", default=os.getenv("LUTHOR_API_URL", "http://localhost:8080"))
    parser.add_argument("--export-token", default=os.getenv("LUTHOR_EXPORT_TOKEN"))
    parser.add_argument("--table", default="inference_logs")
    parser.add_argument("--format", default="csv", choices=["csv", "xlsx"])
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--end-date", default=None, help="YYYY-MM-DD")
    parser.add_argument(
        "--credentials",
        default=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"),
        help="Path to Google service account JSON",
    )
    parser.add_argument(
        "--spreadsheet",
        default=os.getenv("LUTHOR_SHEETS_NAME", "Luthor Logs"),
    )
    parser.add_argument(
        "--worksheet",
        default=os.getenv("LUTHOR_SHEETS_WORKSHEET", "inference_logs"),
    )
    parser.add_argument(
        "--yesterday",
        action="store_true",
        help="Export logs for the previous calendar day",
    )
    args = parser.parse_args()

    if not args.export_token:
        print("LUTHOR_EXPORT_TOKEN or --export-token is required", file=sys.stderr)
        sys.exit(1)
    if not args.credentials:
        print("GOOGLE_SERVICE_ACCOUNT_JSON or --credentials is required", file=sys.stderr)
        sys.exit(1)

    start_date = date.fromisoformat(args.start_date) if args.start_date else None
    end_date = date.fromisoformat(args.end_date) if args.end_date else None
    if args.yesterday:
        yesterday = date.today() - timedelta(days=1)
        start_date = yesterday
        end_date = yesterday

    if args.format != "csv":
        print("Google Sheets upload currently supports CSV exports only", file=sys.stderr)
        sys.exit(1)

    content = fetch_export(
        api_url=args.api_url,
        export_token=args.export_token,
        table=args.table,
        export_format=args.format,
        start_date=start_date,
        end_date=end_date,
    )
    rows = csv_bytes_to_rows(content)
    if not rows:
        print("No rows returned by export endpoint")
        return

    sheet_url = publish_to_sheet(
        credentials_path=args.credentials,
        spreadsheet_name=args.spreadsheet,
        worksheet_name=args.worksheet,
        rows=rows,
    )
    print(f"Published {len(rows) - 1} rows to {sheet_url}")


if __name__ == "__main__":
    main()

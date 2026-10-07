import csv
import threading
from pathlib import Path
from typing import Protocol

import config


class RowLog(Protocol):
    def append(self, row: list) -> None: ...


class GoogleSheetLog:
    def __init__(self, spreadsheet_id: str, worksheet: str, credentials_file: str):
        import gspread

        client = gspread.service_account(filename=credentials_file)
        self._sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet)

    def append(self, row: list) -> None:
        self._sheet.append_row(row, value_input_option="USER_ENTERED")


class CsvLog:
    def __init__(self, path: Path):
        self._path = path
        self._lock = threading.Lock()

    def append(self, row: list) -> None:
        with self._lock, self._path.open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row)


def make_log() -> RowLog:
    if config.GOOGLE_CREDENTIALS_FILE and config.SPREADSHEET_ID:
        return GoogleSheetLog(config.SPREADSHEET_ID, config.WORKSHEET_NAME, config.GOOGLE_CREDENTIALS_FILE)
    return CsvLog(config.CSV_LOG_FILE)

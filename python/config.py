import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Не задана переменная окружения {name} (см. .env.example)")
    return value


@dataclass(frozen=True)
class Portal:
    name: str
    webhook_url: str
    iblock_id: str
    status_property: str
    status_value: str
    title_property: str


IBLOCK_TYPE_ID = "bitrix_processes"
CHECKLIST_TRIGGER_TITLE = "Запчасти"

PORTALS = {
    2: Portal(
        name="coffeeteen",
        webhook_url=_require("BITRIX_COFFEETEEN_WEBHOOK"),
        iblock_id="32",
        status_property="PROPERTY_258",
        status_value="556",
        title_property="PROPERTY_260",
    ),
    0: Portal(
        name="franshizasvezhar",
        webhook_url=_require("BITRIX_SVEZHAR_WEBHOOK"),
        iblock_id="83",
        status_property="PROPERTY_849",
        status_value="2437",
        title_property="PROPERTY_851",
    ),
}

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME", "log")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "")
CSV_LOG_FILE = Path(os.getenv("CSV_LOG_FILE", BASE_DIR / "log.csv"))

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

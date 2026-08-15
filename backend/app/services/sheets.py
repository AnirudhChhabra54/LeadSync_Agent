"""
Google Sheets service — read/write contact rows via gspread.
Auth uses service account JSON from environment variable (no file on disk).
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import gspread

from app.config import get_settings
from app.utils.normalize import normalize_phone, normalize_email

logger = logging.getLogger(__name__)

_gc: Optional[gspread.Client] = None
_worksheet = None

EXPECTED_HEADERS = [
    "Timestamp",
    "Name",
    "Phone",
    "Email",
    "Company",
    "Designation",
    "Website / LinkedIn",
    "Audio URL",
    "Voice Note Summary",
    "Session ID",
    "Status",
]


def _get_worksheet():
    """Get or create the gspread worksheet handle and ensure headers exist."""
    global _gc, _worksheet
    if _worksheet is None:
        settings = get_settings()
        creds = settings.google_creds_dict
        if not creds or not creds.get("type"):
            logger.warning("Google service account credentials not configured — Sheets operations will fail")
            return None
        try:
            _gc = gspread.service_account_from_dict(creds)
            spreadsheet = _gc.open_by_key(settings.GOOGLE_SHEET_ID)
            try:
                _worksheet = spreadsheet.worksheet(settings.GOOGLE_SHEETS_TAB_NAME)
            except gspread.exceptions.WorksheetNotFound:
                _worksheet = spreadsheet.add_worksheet(title=settings.GOOGLE_SHEETS_TAB_NAME, rows="1000", cols="20")

            # Check if headers exist
            all_vals = _worksheet.get_all_values()
            if not all_vals or len(all_vals) == 0 or (len(all_vals) == 1 and not all_vals[0][0]):
                _worksheet.update("A1:K1", [EXPECTED_HEADERS])
                logger.info(f"Initialized headers in sheet '{settings.GOOGLE_SHEETS_TAB_NAME}'")

            logger.info(f"Connected to Google Sheet: {settings.GOOGLE_SHEET_ID}")
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            return None
    return _worksheet


def get_all_rows() -> list[dict]:
    """
    Read all contact rows from the sheet.
    Returns list of dicts keyed by column headers.
    """
    ws = _get_worksheet()
    if ws is None:
        return []
    try:
        records = ws.get_all_records()
        return records
    except Exception as e:
        logger.error(f"Error reading rows from Google Sheets: {e}")
        return []


def find_duplicate(phone: str, email: str) -> Optional[dict]:
    """
    Check if a contact with matching phone or email already exists.
    Returns the matching row dict or None.
    """
    norm_phone = normalize_phone(phone)
    norm_email = normalize_email(email)

    if not norm_phone and not norm_email:
        return None

    rows = get_all_rows()
    for row in rows:
        row_phone = normalize_phone(str(row.get("Phone", "")))
        row_email = normalize_email(str(row.get("Email", "")))

        if norm_phone and row_phone and norm_phone == row_phone:
            return row
        if norm_email and row_email and norm_email == row_email:
            return row

    return None


def _format_cell_value(val: any) -> str:
    """
    Format value for Google Sheets to prevent formula parse errors.
    If a string starts with '+' or '=', prepend a single quote (') so Sheets
    treats it strictly as a plain text string instead of a mathematical formula.
    """
    if val is None:
        return ""
    s = str(val).strip()
    if s.startswith("+") or s.startswith("="):
        return f"'{s}"
    return s


def append_contact_row(
    name: str,
    phone: str,
    email: str,
    company: str,
    designation: str,
    website_linkedin: str,
    session_id: str,
    status: str = "New — awaiting voice note",
) -> int:
    """
    Append a new contact row to the sheet.
    Returns the 1-based row index of the new row.

    Column order: Timestamp, Name, Phone, Email, Company, Designation,
                  Website / LinkedIn, Audio URL, Voice Note Summary,
                  Session ID, Status
    """
    ws = _get_worksheet()
    if ws is None:
        logger.error("Cannot write to sheet — no worksheet connection")
        return -1

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    row = [
        timestamp,
        _format_cell_value(name),
        _format_cell_value(phone),
        _format_cell_value(email),
        _format_cell_value(company),
        _format_cell_value(designation),
        _format_cell_value(website_linkedin),
        "",  # Audio URL (filled later)
        "",  # Voice Note Summary (filled later)
        session_id,
        status,
    ]
    try:
        ws.append_row(row, value_input_option="USER_ENTERED")
        all_values = ws.get_all_values()
        return len(all_values)
    except Exception as e:
        logger.error(f"Error appending row to Google Sheets: {e}")
        return -1


def update_row_voice_note(
    row_index: int,
    audio_url: str,
    voice_summary: str,
    status: str = "Complete — voice note attached",
):
    """
    Update an existing row with voice note data.
    Columns: H = Audio URL (col 8), I = Voice Note Summary (col 9), K = Status (col 11)
    """
    ws = _get_worksheet()
    if ws is None:
        logger.error("Cannot update sheet — no worksheet connection")
        return

    try:
        ws.update_cell(row_index, 8, audio_url)
        ws.update_cell(row_index, 9, _format_cell_value(voice_summary))
        ws.update_cell(row_index, 11, status)
        logger.info(f"Updated row {row_index} with voice note data")
    except Exception as e:
        logger.error(f"Failed to update row {row_index} in Google Sheets: {e}")


def find_row_by_session_and_name(session_id: str, name: str = "") -> Optional[int]:
    """
    Find the row index for a contact by session ID and name.
    If name is not matched or empty, returns the latest row matching session_id.
    Returns 1-based row index or None.
    """
    ws = _get_worksheet()
    if ws is None:
        return None

    try:
        all_values = ws.get_all_values()
        latest_match = None

        for i, row in enumerate(all_values[1:], start=2):  # Skip header row
            if len(row) >= 10 and row[9] == session_id:
                latest_match = i
                if name and len(row) >= 2 and row[1].strip().lower() == name.strip().lower():
                    return i

        return latest_match
    except Exception as e:
        logger.error(f"Error searching row by session in Google Sheets: {e}")
        return None

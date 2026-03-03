#!/usr/bin/env python3
"""
PANELIN Morning Audit - Phase 1
Monitors customer touchpoints and generates a daily summary.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class PanelinAudit:
    """Main morning audit coordinator."""

    def __init__(self) -> None:
        self.results: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "channels": {},
            "summary": {},
        }
        self.sheet = self._connect_sheets()

    def _connect_sheets(self) -> Any | None:
        """Connect to Google Sheets if configuration is present."""
        creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "").strip()
        sheet_id = os.getenv("GOOGLE_SHEETS_ID", "").strip()

        if not creds_path or not sheet_id:
            logger.warning(
                "⚠️ Google Sheets env vars missing. "
                "Set GOOGLE_SHEETS_CREDENTIALS_PATH and GOOGLE_SHEETS_ID."
            )
            return None

        creds_file = Path(creds_path)
        if not creds_file.exists():
            logger.warning("⚠️ Google credentials file not found: %s", creds_file)
            return None

        try:
            import gspread
            from google.oauth2.service_account import Credentials
        except ImportError:
            logger.error(
                "❌ Missing dependencies. Install with: pip install -r requirements.txt"
            )
            return None

        try:
            creds = Credentials.from_service_account_file(
                str(creds_file),
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
            gc = gspread.authorize(creds)
            sheet = gc.open_by_key(sheet_id)
            logger.info("✅ Connected to Google Sheets: %s", sheet.title)
            return sheet
        except Exception as exc:  # pragma: no cover (network/remote dependency)
            logger.error("❌ Google Sheets connection failed: %s", exc)
            return None

    def _audit_whatsapp(self) -> dict[str, Any]:
        """Phase 1 manual WhatsApp check placeholder."""
        logger.info("📱 Checking WhatsApp Web...")
        logger.warning(
            "⚠️  Phase 1 manual step: open WhatsApp Web and count unread messages."
        )
        return {
            "platform": "WhatsApp",
            "status": "manual_check_required",
            "message": "Count unread messages in WhatsApp Web.",
            "count": 0,
        }

    def _audit_facebook(self) -> dict[str, Any]:
        """Phase 1 manual Facebook check placeholder."""
        logger.info("📘 Checking Facebook Page...")
        logger.warning(
            "⚠️  Phase 1 manual step: check Facebook Page inbox and unread messages."
        )
        return {
            "platform": "Facebook",
            "status": "manual_check_required",
            "message": "Check Facebook Page inbox and unread messages.",
            "count": 0,
        }

    def _audit_mercadolibre(self) -> dict[str, Any]:
        """Phase 1 manual MercadoLibre check placeholder."""
        logger.info("🛍️ Checking MercadoLibre...")
        logger.warning(
            "⚠️  Phase 1 manual step: review MercadoLibre questions, messages, and orders."
        )
        return {
            "platform": "MercadoLibre",
            "status": "manual_check_required",
            "message": "Check MercadoLibre questions, messages, and new orders.",
            "count": 0,
        }

    def _audit_email(self) -> dict[str, Any]:
        """Phase 1 manual email check placeholder."""
        logger.info("📧 Checking Email...")
        logger.warning(
            "⚠️  Phase 1 manual step: review Gmail inbox and spam for customer inquiries."
        )
        return {
            "platform": "Email",
            "status": "manual_check_required",
            "message": "Check Gmail inbox and spam for customer inquiries.",
            "count": 0,
        }

    def run_audit(self) -> dict[str, Any] | None:
        """Run all channel audits."""
        try:
            logger.info("🔄 Running all channel audits...")
            self.results["channels"]["whatsapp"] = self._audit_whatsapp()
            self.results["channels"]["facebook"] = self._audit_facebook()
            self.results["channels"]["mercadolibre"] = self._audit_mercadolibre()
            self.results["channels"]["email"] = self._audit_email()
            logger.info("✅ All channel audits completed")
            return self.results
        except Exception as exc:  # pragma: no cover
            logger.error("❌ Audit failed: %s", exc)
            return None

    def write_to_sheets(self) -> None:
        """Write results to 'Daily Audit' worksheet if Sheets is configured."""
        if not self.sheet:
            logger.warning("⚠️ Skipping Google Sheets write (no sheet connection).")
            return

        try:
            ws = self.sheet.worksheet("Daily Audit")
        except Exception:
            ws = self.sheet.add_worksheet("Daily Audit", rows=100, cols=10)

        try:
            header = ws.row_values(1)
            if not header:
                ws.append_row(["Timestamp", "Channel", "Status", "Count", "Notes"])

            rows = []
            for data in self.results["channels"].values():
                rows.append(
                    [
                        self.results["timestamp"],
                        data["platform"],
                        data["status"],
                        data.get("count", 0),
                        data.get("message", ""),
                    ]
                )

            ws.append_rows(rows)
            logger.info("✅ Results written to Google Sheets")
        except Exception as exc:  # pragma: no cover
            logger.error("❌ Failed to write to Google Sheets: %s", exc)

    def send_summary_email(self) -> None:
        """Phase 2 placeholder for daily summary email delivery."""
        logger.info("📬 Email summary placeholder (Phase 2)")


def main() -> int:
    """Program entry point."""
    logger.info("=" * 60)
    logger.info("🌅 PANELIN MORNING AUDIT STARTED")
    logger.info("=" * 60)

    load_dotenv()
    audit = PanelinAudit()
    results = audit.run_audit()

    if not results:
        logger.error("❌ Morning audit did not complete.")
        return 1

    audit.write_to_sheets()
    audit.send_summary_email()

    logger.info("=" * 60)
    logger.info("🎉 MORNING AUDIT COMPLETE")
    logger.info("📝 Logs saved to: %s", LOG_FILE)
    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Immutable audit log system.
Blockchain-style chain verification for integrity assurance.
"""

import json
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from config.settings import settings
from config.logging_config import get_logger
from src.utils import AuditLogException, safe_json_dumps

logger = get_logger(__name__)


class ImmutableAuditLog:
    """
    Append-only audit log with SHA256 hash chaining.
    Ensures log integrity and tamper-detection.
    """

    def __init__(self, log_file: Optional[Path] = None):
        """
        Initialize audit log.

        Args:
            log_file: Path to audit log file
        """
        self.log_file = log_file or (settings.logs_dir / "audit_log.jsonl")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.last_hash = self._get_last_hash()

    def log_event(self, event_type: str, details: dict, user_id: Optional[str] = None) -> str:
        """
        Log an event to the audit trail.

        Args:
            event_type: Type of event (scan_initiated, ml_classification, etc.)
            details: Event details dictionary
            user_id: Optional user identifier

        Returns:
            Event ID (UUID)
        """
        event_id = str(uuid.uuid4())

        entry = {
            "id": event_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "user_id": user_id or "system",
            "previous_hash": self.last_hash,
        }

        # Calculate hash of entry
        entry_string = json.dumps(entry, sort_keys=True, default=str)
        current_hash = hashlib.sha256(entry_string.encode()).hexdigest()
        entry["current_hash"] = current_hash

        # Write to audit log file
        try:
            with open(self.log_file, "a") as f:
                f.write(safe_json_dumps(entry) + "\n")

            self.last_hash = current_hash
            logger.debug(f"Audit event logged: {event_type} ({event_id})")
            return event_id

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            raise AuditLogException(f"Audit log write failed: {e}")

    def verify_integrity(self) -> Tuple[bool, str]:
        """
        Verify integrity of audit log chain.
        Checks that all hash links are valid.

        Returns:
            Tuple of (is_valid, message)
        """
        if not self.log_file.exists():
            return True, "Audit log file does not exist yet"

        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()

            if not lines:
                return True, "Audit log is empty"

            previous_hash = "0" * 64  # Genesis hash

            for line_num, line in enumerate(lines, 1):
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    return False, f"Invalid JSON at line {line_num}: {e}"

                # Verify previous hash link
                if entry.get("previous_hash") != previous_hash:
                    return False, f"Chain broken at line {line_num}"

                # Verify current hash
                entry_copy = entry.copy()
                stored_hash = entry_copy.pop("current_hash")
                entry_string = json.dumps(entry_copy, sort_keys=True, default=str)
                calculated_hash = hashlib.sha256(entry_string.encode()).hexdigest()

                if calculated_hash != stored_hash:
                    return False, f"Hash mismatch at line {line_num}"

                previous_hash = stored_hash

            logger.info("Audit log integrity verified successfully")
            return True, "Audit log integrity verified"

        except Exception as e:
            return False, f"Verification error: {e}"

    def get_last_hash(self) -> str:
        """Get the hash of the last log entry."""
        return self.last_hash

    def _get_last_hash(self) -> str:
        """Retrieve last hash from log file."""
        if not self.log_file.exists():
            return "0" * 64

        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()

            if not lines:
                return "0" * 64

            last_line = lines[-1]
            entry = json.loads(last_line)
            return entry.get("current_hash", "0" * 64)

        except Exception:
            return "0" * 64

    def export_period(self, start_time: str, end_time: str) -> list:
        """
        Export audit events from a time period.

        Args:
            start_time: ISO format start time
            end_time: ISO format end time

        Returns:
            List of events in period
        """
        events = []

        if not self.log_file.exists():
            return events

        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    timestamp = entry.get("timestamp", "")

                    if start_time <= timestamp <= end_time:
                        events.append(entry)

            return events

        except Exception as e:
            logger.error(f"Error exporting audit events: {e}")
            return []


# Global instance
audit_log = ImmutableAuditLog()

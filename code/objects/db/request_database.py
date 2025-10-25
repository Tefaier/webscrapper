import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json

from dto.request import Request


class RequestDatabase:
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    chapters INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'CREATED',
                    process_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    result_file TEXT,
                    log_file TEXT,
                    details TEXT,
                    expired BOOLEAN DEFAULT false
            )
            """
            )

    def get_request(self, id: int) -> Optional[Request]:
        """Create a new request and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM requests WHERE id = ?", (id,))
            result = cursor.fetchone()

            if result is None:
                return None

            columns = [description[0] for description in cursor.description]
            request_dict = dict(zip(columns, result))

            return Request(
                id=request_dict["id"],
                url=request_dict["url"],
                chapters=request_dict["chapters"],
                status=request_dict["status"],
                process_id=request_dict["process_id"],
                created_at=request_dict["created_at"],
                started_at=request_dict["started_at"],
                completed_at=request_dict["completed_at"],
                result_file=request_dict["result_file"],
                log_file=request_dict["log_file"],
                details=request_dict["details"],
                expired=request_dict["expired"],
            )

    def create_request(self, url: str, chapters: int) -> int:
        """Create a new request and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO requests (url, chapters) VALUES (?, ?)", (url, chapters))
            return cursor.lastrowid

    def start_processing(self, request_id: int, process_id: str):
        """Mark a request as in progress"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE requests SET status = 'ACTIVE', process_id = ?, started_at = CURRENT_TIMESTAMP WHERE id = ?",
                (process_id, request_id),
            )

    def complete_processing(self, request_id: int, details: Dict[str, Any], result_file: str, log_file: str):
        """Mark a request as completed with results"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE requests SET status = 'SUCCESS', completed_at = CURRENT_TIMESTAMP, result_file = ?, log_file = ? WHERE id = ?",
                (result_file, log_file, json.dumps(details), request_id),
            )

    def fail_processing(self, request_id: int, details: Dict[str, Any], result_file: str, log_file: str):
        """Mark a request as failed"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE requests SET status = 'FAILED', completed_at = CURRENT_TIMESTAMP, result_file = ?, log_file = ? WHERE id = ?",
                (result_file, log_file, json.dumps(details), request_id),
            )

    def claim_pending_requests(self, max_count: int) -> List[int]:
        """Atomically get and update oldest CREATED requests to ACTIVE status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # First select IDs of oldest pending requests
            cursor.execute(
                "SELECT id FROM requests WHERE status = 'CREATED' ORDER BY created_at ASC LIMIT ?",
                (max_count,),
            )
            ids = [row[0] for row in cursor.fetchall()]

            if ids:
                # Atomically update status for selected IDs using explicit IDs
                placeholders = ", ".join(["?"] * len(ids))
                cursor.execute(f"UPDATE requests SET status = 'ACTIVE' " f"WHERE id IN ({placeholders})", ids)
            return ids

    def claim_expired_requests(self, expiration_period: timedelta) -> List[int]:
        """Atomically get and update SUCCESS and FAILED requests to CLEARED status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # First select IDs of requests to kill
            cursor.execute(
                "SELECT id FROM requests WHERE status in ('CREATED', 'FAILED') and completed_at != null and completed_at < ?",
                (datetime.now() - expiration_period,),
            )
            ids = [row[0] for row in cursor.fetchall()]

            if ids:
                # Atomically update status for selected IDs using explicit IDs
                placeholders = ", ".join(["?"] * len(ids))
                cursor.execute(f"UPDATE requests SET expired = true WHERE id IN ({placeholders})", ids)
            return ids

import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any
import json

class RequestDatabase:
    def __init__(self, db_path: str = "requests.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
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
                    details TEXT
            )
            """)

    def create_request(self, url: str, chapters: int) -> int:
        """Create a new request and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO requests (url, chapters) VALUES (?, ?)",
                (url, chapters)
            )
            return cursor.lastrowid

    def start_processing(self, request_id: int, process_id: str):
        """Mark a request as in progress"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE requests SET status = 'ACTIVE', process_id = ?, started_at = CURRENT_TIMESTAMP WHERE id = ?",
                (process_id, request_id)
            )

    def complete_processing(self, request_id: int, details: Dict[str, Any], result_file: str, log_file: str):
        """Mark a request as completed with results"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE requests SET status = 'SUCCESS', completed_at = CURRENT_TIMESTAMP, result_file = ?, log_file = ? WHERE id = ?",
                (result_file, log_file, json.dumps(details), request_id)
            )

    def fail_processing(self, request_id: int, details: Dict[str, Any], result_file: str, log_file: str):
        """Mark a request as failed"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE requests SET status = 'FAILED', completed_at = CURRENT_TIMESTAMP, result_file = ?, log_file = ? WHERE id = ?",
                (result_file, log_file, json.dumps(details), request_id)
            )


import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

from dto.add_website import AddWebsite


class AddWebsiteDatabase:
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS add_website (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE
            )
            """
            )

    def get_all(self) -> List[AddWebsite]:
        """Get all website entries from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, url FROM add_website")
            return [AddWebsite(id=row[0], url=row[1]) for row in cursor.fetchall()]

    def get_by_id(self, website_id: int) -> Optional[AddWebsite]:
        """Get a website entry by its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, url FROM add_website WHERE id = ?", (website_id,))
            row = cursor.fetchone()
            return AddWebsite(id=row[0], url=row[1]) if row else None

    def get_by_url(self, url: str) -> Optional[AddWebsite]:
        """Get a website entry by its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, url FROM add_website WHERE url = ?", (url,))
            row = cursor.fetchone()
            return AddWebsite(id=row[0], url=row[1]) if row else None

    def insert(self, url: str) -> Optional[int]:
        """Insert a new website URL and return the generated ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("INSERT INTO add_website (url) VALUES (?)", (url,))
            conn.commit()
            return cursor.lastrowid

    def get_count(self) -> int:
        """Get the total count of website entries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM add_website")
            return cursor.fetchone()[0]

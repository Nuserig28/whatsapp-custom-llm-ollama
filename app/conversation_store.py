import sqlite3
from typing import List, Tuple


class ConversationStore:
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.sqlite_path)

    def _init_db(self) -> None:
        with self._conn() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_key TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_key ON messages(user_key)")
            con.commit()

    def add(self, user_key: str, role: str, content: str) -> None:
        with self._conn() as con:
            con.execute(
                "INSERT INTO messages (user_key, role, content) VALUES (?, ?, ?)",
                (user_key, role, content),
            )
            con.commit()

    def last_n(self, user_key: str, n: int = 10) -> List[Tuple[str, str]]:
        with self._conn() as con:
            rows = con.execute(
                """
                SELECT role, content
                FROM messages
                WHERE user_key = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_key, n),
            ).fetchall()

        rows.reverse()
        return [(r[0], r[1]) for r in rows]

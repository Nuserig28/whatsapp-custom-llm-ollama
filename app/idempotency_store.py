import sqlite3


class IdempotencyStore:
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.sqlite_path)

    def _init_db(self) -> None:
        with self._conn() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_events (
                    event_id TEXT PRIMARY KEY,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            con.commit()

    def seen(self, event_id: str) -> bool:
        with self._conn() as con:
            row = con.execute(
                "SELECT event_id FROM processed_events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
        return row is not None

    def mark(self, event_id: str) -> None:
        with self._conn() as con:
            con.execute(
                "INSERT OR IGNORE INTO processed_events (event_id) VALUES (?)",
                (event_id,),
            )
            con.commit()

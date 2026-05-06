import sqlite3
from contextlib import contextmanager
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.khoi_tao_database()

    @contextmanager
    def ket_noi(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def khoi_tao_database(self):
        with self.ket_noi() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner TEXT NOT NULL,
                    repo TEXT NOT NULL,
                    analyzed_at TEXT NOT NULL,
                    commit_count INTEGER NOT NULL,
                    contributor_count INTEGER NOT NULL,
                    top_contributor TEXT,
                    total_score REAL NOT NULL,
                    total_additions INTEGER NOT NULL,
                    total_deletions INTEGER NOT NULL
                )
                """
            )

    def luu_lich_su(self, ket_qua_phan_tich):
        overview = ket_qua_phan_tich.get("overview", {})
        with self.ket_noi() as connection:
            cursor = connection.execute(
                """
                INSERT INTO analysis_history (
                    owner,
                    repo,
                    analyzed_at,
                    commit_count,
                    contributor_count,
                    top_contributor,
                    total_score,
                    total_additions,
                    total_deletions
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    overview.get("owner", ""),
                    overview.get("repo", ""),
                    overview.get("analyzed_at", ""),
                    overview.get("analyzed_commit_count", 0),
                    overview.get("contributor_count", 0),
                    overview.get("top_contributor", ""),
                    overview.get("total_score", 0.0),
                    overview.get("total_additions", 0),
                    overview.get("total_deletions", 0),
                ),
            )
            return cursor.lastrowid

    def lay_lich_su(self):
        with self.ket_noi() as connection:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    analyzed_at,
                    owner,
                    repo,
                    commit_count,
                    contributor_count,
                    top_contributor,
                    total_score,
                    total_additions,
                    total_deletions
                FROM analysis_history
                ORDER BY id DESC
                """
            )
            return [dict(row) for row in cursor.fetchall()]


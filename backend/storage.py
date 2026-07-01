"""SQLite database operations for NeMusic."""
import os
import sys
import sqlite3
import json
from datetime import datetime

# Handle PyInstaller bundle paths
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "nemusic.db")


def get_db_path():
    """Return the database file path, ensuring the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)
    return DB_PATH


class Database:
    """SQLite database manager for NeMusic."""

    def __init__(self, db_path=None):
        self._db_path = db_path or get_db_path()
        self._conn = None
        self._init_db()

    def _init_db(self):
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._create_tables()

    def _create_tables(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS user (
                uid      INTEGER PRIMARY KEY,
                nickname TEXT,
                avatar   TEXT,
                cookie   TEXT,
                login_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS playlist_cache (
                id          INTEGER PRIMARY KEY,
                name        TEXT,
                cover_url   TEXT,
                song_count  INTEGER,
                data_json   TEXT,
                updated_at  TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS play_cache (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id    INTEGER,
                title      TEXT,
                artist     TEXT,
                album      TEXT,
                cover_url  TEXT,
                local_path TEXT,
                url_hash   TEXT,
                expire_at  TIMESTAMP,
                size_bytes INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS download (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id     INTEGER,
                title       TEXT,
                artist      TEXT,
                album       TEXT,
                cover_url   TEXT,
                file_path   TEXT,
                quality     TEXT,
                file_size   INTEGER,
                downloaded  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS favorite (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id  INTEGER UNIQUE,
                title    TEXT,
                artist   TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self._conn.commit()

    # --- User ---
    def save_user(self, uid, nickname, avatar, cookie):
        self._conn.execute(
            "INSERT OR REPLACE INTO user (uid, nickname, avatar, cookie, login_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (uid, nickname, avatar, cookie, datetime.now()),
        )
        self._conn.commit()

    def get_user(self):
        row = self._conn.execute(
            "SELECT * FROM user ORDER BY login_at DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None

    def clear_user(self):
        self._conn.execute("DELETE FROM user")
        self._conn.commit()

    # --- Playlist Cache ---
    def save_playlist(self, pl_id, name, cover_url, song_count, data):
        self._conn.execute(
            "INSERT OR REPLACE INTO playlist_cache "
            "(id, name, cover_url, song_count, data_json, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (pl_id, name, cover_url, song_count, json.dumps(data), datetime.now()),
        )
        self._conn.commit()

    def get_playlists(self):
        rows = self._conn.execute(
            "SELECT id, name, cover_url, song_count, updated_at "
            "FROM playlist_cache ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_playlist_data(self, pl_id):
        row = self._conn.execute(
            "SELECT data_json FROM playlist_cache WHERE id = ?", (pl_id,)
        ).fetchone()
        return json.loads(row["data_json"]) if row else None

    # --- Play Cache ---
    def add_cache(self, song_id, title, artist, album, cover_url,
                  local_path, url_hash, expire_at, size_bytes):
        self._conn.execute(
            "INSERT INTO play_cache (song_id, title, artist, album, cover_url, "
            "local_path, url_hash, expire_at, size_bytes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (song_id, title, artist, album, cover_url,
             local_path, url_hash, expire_at, size_bytes),
        )
        self._conn.commit()

    def get_cache_by_song_id(self, song_id):
        row = self._conn.execute(
            "SELECT * FROM play_cache WHERE song_id = ? "
            "ORDER BY created_at DESC LIMIT 1",
            (song_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_all_cache(self):
        rows = self._conn.execute(
            "SELECT * FROM play_cache ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_cache(self, cache_id):
        row = self._conn.execute(
            "SELECT local_path FROM play_cache WHERE id = ?", (cache_id,)
        ).fetchone()
        if row and row["local_path"] and os.path.exists(row["local_path"]):
            os.remove(row["local_path"])
        self._conn.execute("DELETE FROM play_cache WHERE id = ?", (cache_id,))
        self._conn.commit()

    # --- Downloads ---
    def add_download(self, song_id, title, artist, album, cover_url,
                     file_path, quality, file_size):
        self._conn.execute(
            "INSERT INTO download (song_id, title, artist, album, cover_url, "
            "file_path, quality, file_size) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (song_id, title, artist, album, cover_url,
             file_path, quality, file_size),
        )
        self._conn.commit()

    def get_downloads(self):
        rows = self._conn.execute(
            "SELECT * FROM download ORDER BY downloaded DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_download(self, song_id):
        row = self._conn.execute(
            "SELECT * FROM download WHERE song_id = ?", (song_id,)
        ).fetchone()
        return dict(row) if row else None

    def delete_download(self, download_id):
        row = self._conn.execute(
            "SELECT file_path FROM download WHERE id = ?", (download_id,)
        ).fetchone()
        if row and row["file_path"] and os.path.exists(row["file_path"]):
            os.remove(row["file_path"])
        self._conn.execute("DELETE FROM download WHERE id = ?", (download_id,))
        self._conn.commit()

    # --- Favorites ---
    def add_favorite(self, song_id, title, artist):
        try:
            self._conn.execute(
                "INSERT INTO favorite (song_id, title, artist) VALUES (?, ?, ?)",
                (song_id, title, artist),
            )
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_favorite(self, song_id):
        self._conn.execute("DELETE FROM favorite WHERE song_id = ?", (song_id,))
        self._conn.commit()

    def get_favorites(self):
        rows = self._conn.execute(
            "SELECT * FROM favorite ORDER BY added_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def is_favorite(self, song_id):
        row = self._conn.execute(
            "SELECT 1 FROM favorite WHERE song_id = ?", (song_id,)
        ).fetchone()
        return row is not None

    def close(self):
        if self._conn:
            self._conn.close()

# NeMusic Player Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows desktop music player (NeMusic.exe) that accesses NetEase Cloud Music library with login, search, playlists, lyrics, and download management.

**Architecture:** Python backend provides NetEase API access (with built-in AES/RSA encryption) and VLC audio playback. Frontend is a single-page HTML/JS app rendered inside a pywebview native window. JS-Python bridge exposes API methods and event callbacks.

**Tech Stack:** Python 3.10+, pywebview ≥5.0, python-vlc ≥3.0, pycryptodome ≥3.19, requests ≥2.31, SQLite (built-in), PyInstaller ≥6.0

## Global Constraints

- Python ≥3.10
- pywebview ≥5.0 (uses system Edge WebView2)
- python-vlc ≥3.0 (requires VLC installed or libVLC DLL bundled)
- pycryptodome ≥3.19
- requests ≥2.31
- PyInstaller ≥6.0
- Project root: `E:\NeMusic\`
- All Python backend modules in `backend/` package
- All frontend files in `frontend/` directory
- Runtime data in `data/` (auto-created)
- Frontend uses vanilla HTML/CSS/JS — no frameworks
- API rate limit: ≥200ms between requests, max 3 retries with 1s/3s/10s delays
- Song URL refresh on expiry is transparent to user

---

## File Structure

```
E:\NeMusic\
├── main.py                 # Entry point
├── build.py                # PyInstaller build script
├── requirements.txt        # Python dependencies
├── icon.ico                # Application icon (placeholder)
├── backend/
│   ├── __init__.py
│   ├── crypto.py           # AES/RSA encryption for NetEase API
│   ├── storage.py          # SQLite DB operations
│   ├── netease.py          # Low-level NetEase HTTP client
│   ├── api.py              # High-level API for JS bridge
│   ├── player.py           # VLC audio player wrapper
│   ├── lyric.py            # LRC lyric parser
│   └── download.py         # Download/cache manager
├── frontend/
│   ├── index.html          # SPA main page
│   ├── css/
│   │   ├── main.css        # Global styles + CSS variables
│   │   ├── sidebar.css     # Sidebar navigation
│   │   ├── player-bar.css  # Bottom player bar
│   │   ├── lyrics.css      # Lyrics view
│   │   ├── search.css      # Search page
│   │   ├── playlist.css    # Playlist detail page
│   │   └── download.css    # Download management page
│   └── js/
│       ├── app.js          # App init + router
│       ├── api-bridge.js   # Python-JS communication
│       ├── player.js       # Frontend player logic
│       ├── lyrics.js       # Lyrics rendering + scroll
│       ├── search.js       # Search page logic
│       ├── playlist.js     # Playlist page logic
│       ├── download.js     # Download management logic
│       └── utils.js        # Shared utilities
└── data/                    # Created at runtime
    ├── nemusic.db
    ├── cache/
    └── downloads/
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `E:\NeMusic\requirements.txt`
- Create: `E:\NeMusic\backend\__init__.py`
- Create: `E:\NeMusic\main.py` (skeleton)
- Create: `E:\NeMusic\build.py` (skeleton)
- Create: directory structure

**Produces:** Runnable skeleton that opens an empty pywebview window.

- [ ] **Step 1: Create requirements.txt**

```
pywebview>=5.0
python-vlc>=3.0.0
pycryptodome>=3.19.0
requests>=2.31.0
```

- [ ] **Step 2: Create backend __init__.py**

```python
# NeMusic backend package
```

- [ ] **Step 3: Create main.py skeleton**

```python
"""NeMusic - NetEase Cloud Music Desktop Player."""
import os
import sys
import webview

# Ensure backend is importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


class NeMusicAPI:
    """API object exposed to JavaScript via pywebview."""

    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def echo(self, message):
        """Test method to verify JS-Python bridge."""
        return f"Python received: {message}"


def main():
    api = NeMusicAPI()
    html_path = os.path.join(BASE_DIR, "frontend", "index.html")

    window = webview.create_window(
        title="NeMusic - 网易云音乐",
        url=html_path,
        js_api=api,
        width=1100,
        height=720,
        min_size=(800, 500),
    )
    api.set_window(window)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Create build.py skeleton**

```python
"""PyInstaller build script for NeMusic."""
import PyInstaller.__main__
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build():
    frontend_dir = os.path.join(BASE_DIR, "frontend")
    icon_path = os.path.join(BASE_DIR, "icon.ico")

    args = [
        os.path.join(BASE_DIR, "main.py"),
        "--name=NeMusic",
        "--onefile",
        "--windowed",
        f"--add-data={frontend_dir}{os.pathsep}frontend",
    ]
    if os.path.exists(icon_path):
        args.append(f"--icon={icon_path}")

    PyInstaller.__main__.run(args)


if __name__ == "__main__":
    build()
```

- [ ] **Step 5: Create directory structure**

Run:
```powershell
New-Item -ItemType Directory -Path "E:\NeMusic\frontend\css" -Force
New-Item -ItemType Directory -Path "E:\NeMusic\frontend\js" -Force
New-Item -ItemType Directory -Path "E:\NeMusic\frontend\assets" -Force
New-Item -ItemType Directory -Path "E:\NeMusic\data\cache" -Force
New-Item -ItemType Directory -Path "E:\NeMusic\data\downloads" -Force
```

- [ ] **Step 6: Install dependencies and verify**

Run:
```powershell
cd E:\NeMusic
pip install -r requirements.txt
python main.py
```

Expected: A window titled "NeMusic - 网易云音乐" opens. It will be blank (no index.html yet).

- [ ] **Step 7: Commit (if using git)**

---

### Task 2: Crypto Module (AES/RSA for NetEase API)

**Files:**
- Create: `E:\NeMusic\backend\crypto.py`

**Produces:** `encrypt_request(data: dict) -> (params: str, enc_sec_key: str)` for NetEase API request encryption.

- [ ] **Step 1: Write crypto.py with NetEase API encryption**

```python
"""AES/RSA encryption for NetEase Cloud Music API requests."""
import base64
import json
import os
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad

# NetEase's RSA public key (fixed, from web player source)
NETEASE_RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCgtRd8U7jDnAaJVBh+z1s0nHj8
XL2Fiz+WbSkLFSodDNG5o6gQ9MaqTUBMR7g/e/yiA4hJjwDH+kWFj6w3TAh2Cz7o
FxL+XlMqUdiT/ZqG1XhjsSK7uQNHDxVZrLRdRVxIW0Lo8mTLzoSZ0Hi/+nSe3J6I
DCoMt3gV1JZZUh+jKQIDAQAB
-----END PUBLIC KEY-----"""

# Fixed IV for AES
AES_IV = b"0102030405060708"

# Nonce for the X-Real-IP header
NONCE = b"0CoJUm6Qyw8W8jud"


def _generate_aes_key() -> bytes:
    """Generate a random 16-byte AES key."""
    return os.urandom(16)


def _aes_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    """AES-128-CBC encrypt."""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data, AES.block_size))


def _rsa_encrypt(data: bytes) -> bytes:
    """RSA encrypt with NetEase's public key (reversed result)."""
    key = RSA.import_key(NETEASE_RSA_PUBLIC_KEY)
    cipher = PKCS1_v1_5.new(key)
    encrypted = cipher.encrypt(data)
    # NetEase expects the encrypted bytes in reverse order
    return encrypted[::-1]


def encrypt_request(plain_data: dict) -> dict:
    """
    Encrypt request data for NetEase API.

    Args:
        plain_data: Dictionary of request parameters.

    Returns:
        dict with keys 'params' and 'encSecKey' ready for POST body.
    """
    text = json.dumps(plain_data)

    # First AES pass with fixed nonce key
    first_key = NONCE
    first_encrypted = _aes_encrypt(text.encode(), first_key, AES_IV)
    first_b64 = base64.b64encode(first_encrypted).decode()

    # Second AES pass with random key
    second_key = _generate_aes_key()
    second_encrypted = _aes_encrypt(first_b64.encode(), second_key, AES_IV)
    params = base64.b64encode(second_encrypted).decode()

    # RSA encrypt the random key
    reversed_key = second_key[::-1]
    enc_sec_key = base64.b64encode(
        _rsa_encrypt(reversed_key)
    ).decode()

    return {"params": params, "encSecKey": enc_sec_key}
```

- [ ] **Step 2: Verify crypto module works**

Run:
```powershell
cd E:\NeMusic
python -c "from backend.crypto import encrypt_request; r = encrypt_request({'s': 'test'}); print('params:', r['params'][:50] + '...'); print('encSecKey:', r['encSecKey'][:50] + '...')"
```

Expected: Two long base64 strings printed, no errors.

- [ ] **Step 3: Commit**

---

### Task 3: Storage Module (SQLite Database)

**Files:**
- Create: `E:\NeMusic\backend\storage.py`

**Produces:** `Database` class with methods for user, playlists, cache, downloads, and favorites.

- [ ] **Step 1: Write storage.py**

```python
"""SQLite database operations for NeMusic."""
import os
import sqlite3
import json
from datetime import datetime

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
        row = self._conn.execute("SELECT * FROM user ORDER BY login_at DESC LIMIT 1").fetchone()
        return dict(row) if row else None

    def clear_user(self):
        self._conn.execute("DELETE FROM user")
        self._conn.commit()

    # --- Playlist Cache ---
    def save_playlist(self, pl_id, name, cover_url, song_count, data):
        self._conn.execute(
            "INSERT OR REPLACE INTO playlist_cache (id, name, cover_url, song_count, data_json, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (pl_id, name, cover_url, song_count, json.dumps(data), datetime.now()),
        )
        self._conn.commit()

    def get_playlists(self):
        rows = self._conn.execute(
            "SELECT id, name, cover_url, song_count, updated_at FROM playlist_cache ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_playlist_data(self, pl_id):
        row = self._conn.execute(
            "SELECT data_json FROM playlist_cache WHERE id = ?", (pl_id,)
        ).fetchone()
        return json.loads(row["data_json"]) if row else None

    # --- Play Cache ---
    def add_cache(self, song_id, title, artist, album, cover_url, local_path, url_hash, expire_at, size_bytes):
        self._conn.execute(
            "INSERT INTO play_cache (song_id, title, artist, album, cover_url, local_path, url_hash, expire_at, size_bytes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (song_id, title, artist, album, cover_url, local_path, url_hash, expire_at, size_bytes),
        )
        self._conn.commit()

    def get_cache_by_song_id(self, song_id):
        row = self._conn.execute(
            "SELECT * FROM play_cache WHERE song_id = ? ORDER BY created_at DESC LIMIT 1",
            (song_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_all_cache(self):
        rows = self._conn.execute(
            "SELECT * FROM play_cache ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_cache(self, cache_id):
        row = self._conn.execute("SELECT local_path FROM play_cache WHERE id = ?", (cache_id,)).fetchone()
        if row and row["local_path"] and os.path.exists(row["local_path"]):
            os.remove(row["local_path"])
        self._conn.execute("DELETE FROM play_cache WHERE id = ?", (cache_id,))
        self._conn.commit()

    # --- Downloads ---
    def add_download(self, song_id, title, artist, album, cover_url, file_path, quality, file_size):
        self._conn.execute(
            "INSERT INTO download (song_id, title, artist, album, cover_url, file_path, quality, file_size) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (song_id, title, artist, album, cover_url, file_path, quality, file_size),
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
        row = self._conn.execute("SELECT file_path FROM download WHERE id = ?", (download_id,)).fetchone()
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
        rows = self._conn.execute("SELECT * FROM favorite ORDER BY added_at DESC").fetchall()
        return [dict(r) for r in rows]

    def is_favorite(self, song_id):
        row = self._conn.execute(
            "SELECT 1 FROM favorite WHERE song_id = ?", (song_id,)
        ).fetchone()
        return row is not None

    def close(self):
        if self._conn:
            self._conn.close()
```

- [ ] **Step 2: Verify database creation**

Run:
```powershell
cd E:\NeMusic
python -c "from backend.storage import Database; db = Database(); db.close(); import os; print('DB exists:', os.path.exists('data/nemusic.db'))"
```

- [ ] **Step 3: Commit**

---

### Task 4: NetEase HTTP Client

**Files:**
- Create: `E:\NeMusic\backend\netease.py`

**Consumes:** `backend.crypto.encrypt_request`
**Produces:** `NetEaseClient` class with low-level API methods.

- [ ] **Step 1: Write netease.py**

```python
"""Low-level NetEase Cloud Music HTTP client."""
import time
import requests
from backend.crypto import encrypt_request

BASE_URL = "https://music.163.com"
API_BASE = f"{BASE_URL}/weapi"

# Standard headers
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": f"{BASE_URL}/",
    "Origin": BASE_URL,
}


class NetEaseClient:
    """Low-level client for NetEase Cloud Music API."""

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(HEADERS)
        self._last_request_time = 0
        self._cookie = {}

    @property
    def cookie(self):
        return self._cookie

    @cookie.setter
    def cookie(self, cookie_dict):
        self._cookie = cookie_dict or {}
        self._session.cookies.update(self._cookie)

    def _rate_limit(self):
        """Ensure at least 200ms between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < 0.2:
            time.sleep(0.2 - elapsed)
        self._last_request_time = time.time()

    def _request(self, endpoint, data, retries=3):
        """
        Send an encrypted POST request to the NetEase API.

        Args:
            endpoint: API path (e.g. '/cloudsearch/get/web')
            data: Plain dict of parameters.
            retries: Max retry count on failure.

        Returns:
            Parsed JSON response dict.
        """
        url = f"{API_BASE}{endpoint}"
        encrypted = encrypt_request(data)

        for attempt in range(retries):
            self._rate_limit()
            try:
                resp = self._session.post(url, data=encrypted, timeout=15)
                result = resp.json()

                if result.get("code") == 200:
                    return result
                elif result.get("code") in (301, 401):
                    # Cookie expired
                    raise CookieExpiredError(f"Cookie expired: {result}")

                # API error, maybe retry
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return result

            except requests.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise e

        return {"code": -1, "message": "Request failed after retries"}

    # --- Search ---
    def search(self, keyword, limit=30, offset=0, search_type=1):
        """
        Search songs.

        Args:
            keyword: Search query.
            limit: Results per page (max 30).
            offset: Pagination offset.
            search_type: 1=song, 100=artist, 10=album, 1000=playlist.

        Returns:
            API response with search results.
        """
        return self._request("/cloudsearch/get/web", {
            "s": keyword,
            "type": search_type,
            "limit": str(limit),
            "offset": str(offset),
            "total": "true",
        })

    # --- Song ---
    def get_song_detail(self, song_ids):
        """
        Get song details.

        Args:
            song_ids: Single song ID or list of song IDs.

        Returns:
            API response with song details.
        """
        if isinstance(song_ids, int):
            song_ids = [song_ids]
        ids_str = ",".join(str(i) for i in song_ids)
        return self._request("/v3/song/detail", {
            "c": f'[{{"id":{ids_str}}}]',
            "ids": f"[{ids_str}]",
        })

    def get_song_url(self, song_ids, br=320000):
        """
        Get playable song URLs.

        Args:
            song_ids: Single song ID or list of song IDs.
            br: Bitrate — 128000, 192000, 320000, 999000 (FLAC).

        Returns:
            API response with song URLs.
        """
        if isinstance(song_ids, int):
            song_ids = [song_ids]
        ids_str = ",".join(str(i) for i in song_ids)
        return self._request("/song/enhance/player/url", {
            "ids": f"[{ids_str}]",
            "br": str(br),
        })

    def get_lyric(self, song_id):
        """
        Get lyrics for a song.

        Args:
            song_id: Song ID.

        Returns:
            API response with lrc lyric data.
        """
        return self._request("/song/lyric", {
            "id": str(song_id),
            "lv": "-1",
            "tv": "-1",
        })

    # --- Login ---
    def login_cellphone(self, phone, password):
        """
        Login with phone number and password.

        Args:
            phone: Phone number.
            password: MD5-hashed password.

        Returns:
            API response with login result.
        """
        return self._request("/login/cellphone", {
            "phone": phone,
            "password": password,
            "rememberLogin": "true",
        })

    def login_qr_key(self):
        """Get a QR code unikey for login."""
        return self._request("/login/qr/key", {
            "type": "1",
        })

    def login_qr_create(self, key):
        """Generate QR code URL from unikey."""
        return self._request("/login/qr/create", {
            "key": key,
            "qrimg": "true",
        })

    def login_qr_check(self, key):
        """Check QR code scan status."""
        return self._request("/login/qr/client/login", {
            "key": key,
            "type": "1",
        })

    # --- User ---
    def get_user_playlists(self, uid, limit=100, offset=0):
        """
        Get user's playlists.

        Args:
            uid: User ID.
            limit: Max playlists.
            offset: Offset.

        Returns:
            API response with playlist list.
        """
        return self._request("/user/playlist", {
            "uid": str(uid),
            "limit": str(limit),
            "offset": str(offset),
        })

    def get_user_detail(self, uid):
        return self._request("/user/detail", {"uid": str(uid)})

    def refresh_login(self):
        """Refresh login cookie."""
        return self._request("/login/refresh", {})

    # --- Playlist ---
    def get_playlist_detail(self, playlist_id):
        """
        Get playlist with all songs.

        Args:
            playlist_id: Playlist ID.

        Returns:
            API response with playlist tracks.
        """
        return self._request("/v6/playlist/detail", {
            "id": str(playlist_id),
            "n": "1000",
            "total": "true",
        })

    # --- Toplist ---
    def get_toplist(self):
        """Get all toplists."""
        return self._request("/toplist", {})

    def get_toplist_detail(self):
        """Get detailed toplist data."""
        return self._request("/toplist/detail", {})

    def close(self):
        self._session.close()


class CookieExpiredError(Exception):
    """Raised when NetEase API returns a cookie-expired status."""
    pass
```

- [ ] **Step 2: Verify module imports cleanly**

Run:
```powershell
cd E:\NeMusic
python -c "from backend.netease import NetEaseClient; print('NetEaseClient imported successfully')"
```

- [ ] **Step 3: Commit**

---

### Task 5: VLC Audio Player

**Files:**
- Create: `E:\NeMusic\backend\player.py`

**Produces:** `Player` class wrapping python-vlc for audio playback with position tracking and event callbacks.

- [ ] **Step 1: Write player.py**

```python
"""VLC-based audio player for NeMusic."""
import time
import threading
import vlc


class Player:
    """Audio player wrapping VLC MediaPlayer."""

    def __init__(self):
        self._instance = vlc.Instance("--no-video")
        self._player = self._instance.media_player_new()
        self._callbacks = {
            "on_position_change": None,
            "on_state_change": None,
            "on_song_end": None,
            "on_error": None,
        }
        self._current_url = None
        self._current_song = None  # song info dict
        self._position_timer = None
        self._running = False

    def set_callback(self, name, func):
        """Register a callback. name: 'on_position_change', 'on_state_change', 'on_song_end', 'on_error'."""
        if name in self._callbacks:
            self._callbacks[name] = func

    def play(self, url, song_info=None):
        """
        Play audio from URL.

        Args:
            url: Audio stream URL.
            song_info: Dict with song metadata (id, name, artist, cover, etc.)
        """
        self._current_url = url
        self._current_song = song_info or {}
        self._running = True

        media = self._instance.media_new(url)
        self._player.set_media(media)
        self._player.play()

        self._start_position_timer()
        self._notify_state("playing")

    def pause(self):
        self._player.pause()
        self._notify_state("paused")

    def resume(self):
        self._player.play()
        self._notify_state("playing")

    def toggle_play_pause(self):
        if self._player.is_playing():
            self.pause()
        else:
            self.resume()

    def stop(self):
        self._running = False
        self._stop_position_timer()
        self._player.stop()

    def seek(self, position_sec):
        """Seek to position in seconds."""
        self._player.set_time(int(position_sec * 1000))

    def set_volume(self, volume):
        """Set volume 0-100."""
        self._player.audio_set_volume(int(volume))

    def get_volume(self):
        return self._player.audio_get_volume()

    def get_position(self):
        """Return (current_sec, total_sec)."""
        current_ms = self._player.get_time()
        total_ms = self._player.get_length()
        current = current_ms / 1000.0 if current_ms > 0 else 0
        total = total_ms / 1000.0 if total_ms > 0 else 0
        return current, total

    def get_current_song(self):
        """Return current song info dict."""
        return self._current_song

    def is_playing(self):
        return self._player.is_playing() == 1

    def _start_position_timer(self):
        self._stop_position_timer()
        self._position_timer = threading.Thread(target=self._position_loop, daemon=True)
        self._position_timer.start()

    def _stop_position_timer(self):
        if self._position_timer and self._position_timer.is_alive():
            self._position_timer = None

    def _position_loop(self):
        """Emit position updates every second and detect song end."""
        last_pos = -1
        while self._running:
            time.sleep(0.5)
            if not self._running:
                break

            current, total = self.get_position()

            # Position tracking
            curr_int = int(current)
            if curr_int != last_pos and self._callbacks["on_position_change"]:
                last_pos = curr_int
                pct = (current / total * 100) if total > 0 else 0
                try:
                    self._callbacks["on_position_change"](
                        current_sec=current, total_sec=total, percentage=pct
                    )
                except Exception:
                    pass

            # Song end detection (stopped playing and had progressed past 1 sec)
            if not self.is_playing() and current > 1 and total > 0:
                self._running = False
                if self._callbacks["on_song_end"]:
                    try:
                        self._callbacks["on_song_end"]()
                    except Exception:
                        pass
                break

    def _notify_state(self, state):
        if self._callbacks["on_state_change"]:
            try:
                self._callbacks["on_state_change"](state=state)
            except Exception:
                pass

    def _notify_error(self, code, message):
        if self._callbacks["on_error"]:
            try:
                self._callbacks["on_error"](code=code, message=message)
            except Exception:
                pass

    def destroy(self):
        self._running = False
        self._stop_position_timer()
        self._player.stop()
        self._player.release()
        self._instance.release()
```

- [ ] **Step 2: Verify player imports**

Run:
```powershell
cd E:\NeMusic
python -c "from backend.player import Player; p = Player(); print('Player created, volume:', p.get_volume()); p.destroy()"
```

- [ ] **Step 3: Commit**

---

### Task 6: LRC Lyric Parser

**Files:**
- Create: `E:\NeMusic\backend\lyric.py`

**Produces:** `parse_lrc(lrc_text: str) -> list[dict]` — parses LRC format into timed lyric lines.

- [ ] **Step 1: Write lyric.py**

```python
"""LRC lyric file parser."""
import re


def parse_lrc(lrc_text):
    """
    Parse LRC-format lyrics into timed lines.

    Args:
        lrc_text: Raw LRC lyric string.

    Returns:
        List of dicts: [{"time": seconds_float, "text": "lyric line"}, ...]
        Sorted by time ascending. Returns empty list if no lyrics.
    """
    if not lrc_text:
        return []

    lines = []
    # Pattern: [mm:ss.xx] or [mm:ss.xxx] followed by text
    pattern = re.compile(r"\[(\d{1,3}):(\d{2})(?:\.(\d{2,3}))?\](.*)")

    for line in lrc_text.strip().split("\n"):
        match = pattern.match(line.strip())
        if not match:
            continue

        minutes = int(match.group(1))
        seconds = int(match.group(2))
        centiseconds = match.group(3) or "0"
        # Normalize to seconds as float
        if len(centiseconds) == 2:
            cs = int(centiseconds) / 100.0
        else:
            cs = int(centiseconds) / 1000.0

        time_sec = minutes * 60 + seconds + cs
        text = match.group(4).strip()

        if text:
            lines.append({"time": time_sec, "text": text})

    # Sort by time
    lines.sort(key=lambda x: x["time"])
    return lines


def find_current_line(lyric_lines, current_time_sec):
    """
    Find the index of the current lyric line based on playback position.

    Args:
        lyric_lines: Parsed lyric lines from parse_lrc().
        current_time_sec: Current playback position in seconds.

    Returns:
        Index of the current line, or -1 if before the first line.
    """
    if not lyric_lines:
        return -1

    current_idx = -1
    for i, line in enumerate(lyric_lines):
        if line["time"] <= current_time_sec:
            current_idx = i
        else:
            break

    return current_idx
```

- [ ] **Step 2: Verify lyric parser**

Run:
```powershell
cd E:\NeMusic
python -c "
from backend.lyric import parse_lrc, find_current_line
sample = '[00:00.00]First line\n[00:10.50]Second line\n[00:20.00]Third line'
lines = parse_lrc(sample)
print('Parsed lines:', len(lines))
print('First line:', lines[0])
print('Current at 5s:', find_current_line(lines, 5))
print('Current at 15s:', find_current_line(lines, 15))
"
```

Expected: 3 lines parsed, current at 5s = 0 (first line), current at 15s = 1 (second line).

- [ ] **Step 3: Commit**

---

### Task 7: Download & Cache Manager

**Files:**
- Create: `E:\NeMusic\backend\download.py`

**Consumes:** `backend.storage.Database`, `backend.netease.NetEaseClient`
**Produces:** `DownloadManager` class with `add_download(song_id)`, `get_list()`, `delete(id)`, `export(song_id, path)`.

- [ ] **Step 1: Write download.py**

```python
"""Download and cache management for NeMusic."""
import os
import hashlib
import requests
from datetime import datetime, timedelta
from backend.storage import Database

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
DOWNLOADS_DIR = os.path.join(DATA_DIR, "downloads")


class DownloadManager:
    """Manage song downloads and play caching."""

    def __init__(self, netease_client, db=None):
        self._netease = netease_client
        self._db = db or Database()
        os.makedirs(CACHE_DIR, exist_ok=True)
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    def download_song(self, song_id, title, artist, album, cover_url, quality="320k"):
        """
        Download a song file for offline use.

        Args:
            song_id: NetEase song ID.
            title: Song title.
            artist: Artist name.
            album: Album name.
            cover_url: Cover image URL.
            quality: Target quality ('128k', '192k', '320k', 'flac').

        Returns:
            dict: {success: bool, file_path: str or None, message: str}
        """
        # Check if already downloaded
        existing = self._db.get_download(song_id)
        if existing and os.path.exists(existing["file_path"]):
            return {"success": True, "file_path": existing["file_path"], "message": "Already downloaded"}

        # Check disk space (require > 100MB)
        self._check_disk_space(100 * 1024 * 1024)

        # Map quality to bitrate
        br_map = {"128k": 128000, "192k": 192000, "320k": 320000, "flac": 999000}
        br = br_map.get(quality, 320000)

        # Get song URL
        result = self._netease.get_song_url(song_id, br=br)
        songs = result.get("data", [])
        if not songs or not songs[0].get("url"):
            # Try lower quality
            for fallback_br in [192000, 128000]:
                result = self._netease.get_song_url(song_id, br=fallback_br)
                songs = result.get("data", [])
                if songs and songs[0].get("url"):
                    break
            else:
                return {"success": False, "file_path": None, "message": "No playable URL (song may be unavailable)"}

        url = songs[0]["url"]
        actual_br = songs[0].get("br", br)
        ext = ".flac" if actual_br >= 999000 else ".mp3"

        # Download the file
        safe_name = f"{song_id}_{self._safe_filename(title)}"
        file_path = os.path.join(DOWNLOADS_DIR, f"{safe_name}{ext}")

        try:
            self._download_file(url, file_path)
        except Exception as e:
            return {"success": False, "file_path": None, "message": str(e)}

        file_size = os.path.getsize(file_path)

        # Record in database
        self._db.add_download(
            song_id=song_id,
            title=title,
            artist=artist,
            album=album,
            cover_url=cover_url,
            file_path=file_path,
            quality=self._br_to_label(actual_br),
            file_size=file_size,
        )

        return {"success": True, "file_path": file_path, "message": "Download complete"}

    def cache_song(self, song_id, title, artist, album, cover_url, url):
        """
        Cache a played song to local storage.

        Args:
            song_id: NetEase song ID.
            title: Song title.
            artist: Artist name.
            album: Album name.
            cover_url: Cover image URL.
            url: Audio stream URL.

        Returns:
            Local file path or None.
        """
        # Check if already cached and fresh
        existing = self._db.get_cache_by_song_id(song_id)
        if existing and os.path.exists(existing["local_path"]):
            return existing["local_path"]

        self._check_disk_space(100 * 1024 * 1024)

        url_hash = hashlib.md5(url.encode()).hexdigest()
        safe_name = f"{song_id}_{self._safe_filename(title)}.mp3"
        file_path = os.path.join(CACHE_DIR, safe_name)

        try:
            self._download_file(url, file_path)
        except Exception:
            return None

        file_size = os.path.getsize(file_path)
        expire_at = datetime.now() + timedelta(days=7)

        self._db.add_cache(
            song_id=song_id,
            title=title,
            artist=artist,
            album=album,
            cover_url=cover_url,
            local_path=file_path,
            url_hash=url_hash,
            expire_at=expire_at,
            size_bytes=file_size,
        )

        return file_path

    def get_cached_url(self, song_id):
        """Get local cache path for a song if available and fresh."""
        cached = self._db.get_cache_by_song_id(song_id)
        if cached and os.path.exists(cached["local_path"]):
            return cached["local_path"]
        return None

    def get_downloaded_path(self, song_id):
        """Get local download path for a song if available."""
        downloaded = self._db.get_download(song_id)
        if downloaded and os.path.exists(downloaded["file_path"]):
            return downloaded["file_path"]
        return None

    def get_download_list(self):
        """Get all downloaded songs."""
        return self._db.get_downloads()

    def get_cache_list(self):
        """Get all cached songs."""
        return self._db.get_all_cache()

    def delete_download(self, download_id):
        """Delete a downloaded song."""
        self._db.delete_download(download_id)

    def delete_cache(self, cache_id):
        """Delete a cached song."""
        self._db.delete_cache(cache_id)

    def export_song(self, song_id, target_path):
        """
        Copy a downloaded song to an external location.

        Args:
            song_id: NetEase song ID.
            target_path: Destination file path.

        Returns:
            dict: {success: bool, message: str}
        """
        downloaded = self._db.get_download(song_id)
        if not downloaded or not os.path.exists(downloaded["file_path"]):
            # Try cache as fallback
            cached = self._db.get_cache_by_song_id(song_id)
            if cached and os.path.exists(cached["local_path"]):
                downloaded = cached
            else:
                return {"success": False, "message": "File not found in downloads or cache"}

        import shutil
        shutil.copy2(downloaded["file_path"], target_path)
        return {"success": True, "message": f"Exported to {target_path}"}

    def _download_file(self, url, file_path):
        """Stream download a file to disk."""
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

    def _check_disk_space(self, required_bytes):
        """Raise OSError if available disk space is insufficient."""
        import shutil
        usage = shutil.disk_usage(DATA_DIR)
        if usage.free < required_bytes:
            raise OSError(
                f"Insufficient disk space. "
                f"Available: {usage.free // (1024*1024)}MB, "
                f"Required: {required_bytes // (1024*1024)}MB"
            )

    @staticmethod
    def _safe_filename(name):
        """Sanitize a string for use as a filename."""
        return "".join(c for c in name if c.isalnum() or c in " _-")[:50]

    @staticmethod
    def _br_to_label(br):
        if br >= 999000:
            return "flac"
        elif br >= 320000:
            return "320k"
        elif br >= 192000:
            return "192k"
        return "128k"
```

- [ ] **Step 2: Verify module imports**

Run:
```powershell
cd E:\NeMusic
python -c "from backend.download import DownloadManager; print('DownloadManager imported')"
```

- [ ] **Step 3: Commit**

---

### Task 8: API Layer (JS Bridge Interface)

**Files:**
- Create: `E:\NeMusic\backend\api.py`

**Consumes:** `backend.netease.NetEaseClient`, `backend.storage.Database`, `backend.player.Player`, `backend.download.DownloadManager`, `backend.lyric.parse_lrc`
**Produces:** `NeMusicAPI` class — the complete JS-Python bridge.

- [ ] **Step 1: Write api.py**

```python
"""High-level API exposed to the JavaScript frontend via pywebview."""
import hashlib
import json
from backend.netease import NetEaseClient, CookieExpiredError
from backend.storage import Database
from backend.player import Player
from backend.download import DownloadManager
from backend.lyric import parse_lrc, find_current_line


class NeMusicAPI:
    """Complete API layer for the NeMusic frontend."""

    def __init__(self):
        self._window = None
        self._db = Database()
        self._netease = NetEaseClient()
        self._player = Player()
        self._download_mgr = DownloadManager(self._netease, self._db)

        # Restore saved login
        self._restore_login()

        # Set up player callbacks
        self._player.set_callback("on_position_change", self._on_position_change)
        self._player.set_callback("on_state_change", self._on_state_change)
        self._player.set_callback("on_song_end", self._on_song_end)
        self._player.set_callback("on_error", self._on_error)

        # Play queue
        self._queue = []
        self._queue_index = -1

    def set_window(self, window):
        self._window = window

    def _emit(self, event, data=None):
        """Send an event to the JavaScript frontend."""
        if self._window:
            try:
                payload = json.dumps({"event": event, "data": data or {}})
                self._window.evaluate_js(f"NeMusic.emit({payload})")
            except Exception:
                pass

    def _on_position_change(self, current_sec, total_sec, percentage):
        self._emit("position_change", {
            "current": current_sec, "total": total_sec, "percentage": percentage,
        })

    def _on_state_change(self, state):
        self._emit("state_change", {"state": state})

    def _on_song_end(self):
        self._emit("song_end", {})
        # Auto-play next in queue
        self.next_song()

    def _on_error(self, code, message):
        self._emit("error", {"code": code, "message": message})

    # --- Login ---
    def login_phone(self, phone, password):
        """Login with phone number and md5 password."""
        md5_pw = hashlib.md5(password.encode()).hexdigest()
        try:
            result = self._netease.login_cellphone(phone, md5_pw)
            return self._handle_login_result(result)
        except Exception as e:
            return {"success": False, "message": str(e)}

    def login_qrcode(self):
        """Get QR code for login. Returns qr_url and unikey."""
        try:
            key_result = self._netease.login_qr_key()
            unikey = key_result.get("data", {}).get("unikey", "")
            if not unikey:
                return {"success": False, "message": "Failed to get QR key"}

            qr_result = self._netease.login_qr_create(unikey)
            qr_url = qr_result.get("data", {}).get("qrimg", "")
            return {"success": True, "qr_url": qr_url, "unikey": unikey}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def check_qrcode(self, unikey):
        """Check QR code login status. Returns status and user info if logged in."""
        try:
            result = self._netease.login_qr_check(unikey)
            code = result.get("code")
            if code == 800:
                return {"status": "expired"}
            elif code == 801:
                return {"status": "waiting"}
            elif code == 802:
                return {"status": "scanned"}
            elif code == 803:
                # Login success
                cookie = result.get("cookie", "")
                self._set_cookie(cookie)
                profile = result.get("profile", {})
                uid = profile.get("userId", 0)
                nickname = profile.get("nickname", "")
                avatar = profile.get("avatarUrl", "")
                self._db.save_user(uid, nickname, avatar, cookie)
                return {"status": "success", "uid": uid, "nickname": nickname, "avatar": avatar}
            else:
                return {"status": "unknown", "code": code}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_login_result(self, result):
        code = result.get("code")
        if code == 200:
            cookie = result.get("cookie", "")
            profile = result.get("profile", {})
            uid = profile.get("userId", 0)
            nickname = profile.get("nickname", "")
            avatar = profile.get("avatarUrl", "")
            self._set_cookie(cookie)
            self._db.save_user(uid, nickname, avatar, cookie)
            return {"success": True, "uid": uid, "nickname": nickname, "avatar": avatar}
        elif code == 501:
            return {"success": False, "message": "账号不存在"}
        elif code == 502:
            return {"success": False, "message": "密码错误"}
        elif code == 503:
            return {"success": False, "message": "需要验证码，请使用二维码登录"}
        else:
            return {"success": False, "message": result.get("message", f"登录失败 (code={code})")}

    def _set_cookie(self, cookie_str):
        """Parse cookie string and set on the HTTP client."""
        cookies = {}
        if cookie_str:
            for item in cookie_str.split(";"):
                item = item.strip()
                if "=" in item:
                    k, v = item.split("=", 1)
                    cookies[k.strip()] = v.strip()
        self._netease.cookie = cookies

    def _restore_login(self):
        """Restore saved login state from database."""
        user = self._db.get_user()
        if user and user.get("cookie"):
            self._set_cookie(user["cookie"])

    def get_login_status(self):
        """Check if user is logged in."""
        user = self._db.get_user()
        if user:
            return {"logged_in": True, "uid": user["uid"], "nickname": user["nickname"], "avatar": user["avatar"]}
        return {"logged_in": False}

    def logout(self):
        self._db.clear_user()
        self._netease.cookie = {}
        return {"success": True}

    # --- Search ---
    def search(self, keyword, limit=30, offset=0):
        """Search songs by keyword."""
        try:
            result = self._netease.search(keyword, limit, offset)
            songs = []
            raw_songs = (
                result.get("result", {}).get("songs", [])
            )
            for s in raw_songs:
                songs.append({
                    "id": s.get("id"),
                    "name": s.get("name", ""),
                    "artists": ", ".join(a.get("name", "") for a in s.get("ar", [])),
                    "album": s.get("al", {}).get("name", ""),
                    "cover": s.get("al", {}).get("picUrl", ""),
                    "duration": s.get("dt", 0) // 1000,
                })
            total = result.get("result", {}).get("songCount", len(songs))
            return {"success": True, "songs": songs, "total": total}
        except Exception as e:
            return {"success": False, "message": str(e), "songs": []}

    # --- Play ---
    def play_song(self, song_info):
        """
        Play a song. song_info is a dict with at minimum {id, name, artists, cover}.

        Also adds to play queue and requests the play URL.
        """
        song_id = song_info.get("id")
        if not song_id:
            return {"success": False, "message": "No song ID"}

        # Check local cache or download first
        local_path = (
            self._download_mgr.get_downloaded_path(song_id)
            or self._download_mgr.get_cached_url(song_id)
        )

        if local_path:
            url = local_path
        else:
            # Get streaming URL
            url_result = self._netease.get_song_url(song_id, br=320000)
            songs = url_result.get("data", [])
            if not songs or not songs[0].get("url"):
                # Try lower quality
                for br in [192000, 128000]:
                    url_result = self._netease.get_song_url(song_id, br=br)
                    songs = url_result.get("data", [])
                    if songs and songs[0].get("url"):
                        break
                else:
                    return {"success": False, "message": "该歌曲暂无版权"}

            url = songs[0]["url"]

        # Add to queue if not already playing this song
        current = self._player.get_current_song()
        if not current or current.get("id") != song_id:
            self._queue.append(song_info)

        self._player.play(url, song_info)
        return {"success": True}

    def play_songs(self, songs, start_index=0):
        """Set play queue and start playing from index."""
        self._queue = list(songs)
        self._queue_index = start_index
        if self._queue and start_index < len(self._queue):
            return self.play_song(self._queue[start_index])
        return {"success": False, "message": "Empty queue"}

    def toggle_play_pause(self):
        self._player.toggle_play_pause()
        return {"state": "playing" if self._player.is_playing() else "paused"}

    def next_song(self):
        if not self._queue:
            return {"success": False, "message": "Empty queue"}
        self._queue_index = (self._queue_index + 1) % len(self._queue)
        return self.play_song(self._queue[self._queue_index])

    def prev_song(self):
        if not self._queue:
            return {"success": False, "message": "Empty queue"}
        self._queue_index = (self._queue_index - 1) % len(self._queue)
        return self.play_song(self._queue[self._queue_index])

    def seek(self, position_sec):
        self._player.seek(position_sec)

    def set_volume(self, volume):
        self._player.set_volume(volume)

    def get_volume(self):
        return self._player.get_volume()

    def get_current_song(self):
        song = self._player.get_current_song()
        if song:
            current, total = self._player.get_position()
            song["current"] = current
            song["total"] = total
            song["is_playing"] = self._player.is_playing()
        return song or {}

    def get_queue(self):
        return self._queue

    def remove_from_queue(self, index):
        if 0 <= index < len(self._queue):
            removed = self._queue.pop(index)
            if index < self._queue_index:
                self._queue_index -= 1
            return {"success": True, "removed": removed}
        return {"success": False, "message": "Invalid index"}

    def clear_queue(self):
        self._queue = []
        self._queue_index = -1
        self._player.stop()
        return {"success": True}

    # --- Lyrics ---
    def get_lyric(self, song_id):
        """Get parsed lyrics for a song."""
        try:
            result = self._netease.get_lyric(song_id)
            lrc_data = result.get("lrc", {})
            lrc_text = lrc_data.get("lyric", "")
            if not lrc_text:
                return {"success": True, "lines": [], "message": "纯音乐，请欣赏"}

            lines = parse_lrc(lrc_text)
            return {"success": True, "lines": lines}
        except Exception as e:
            return {"success": False, "lines": [], "message": str(e)}

    # --- Playlists ---
    def get_user_playlists(self):
        """Get current user's playlists."""
        try:
            user = self._db.get_user()
            if not user:
                return {"success": False, "playlists": [], "message": "Not logged in"}

            result = self._netease.get_user_playlists(user["uid"])
            playlists = []
            for pl in result.get("playlist", []):
                pl_info = {
                    "id": pl.get("id"),
                    "name": pl.get("name", ""),
                    "cover": pl.get("coverImgUrl", ""),
                    "track_count": pl.get("trackCount", 0),
                    "creator": pl.get("creator", {}).get("nickname", ""),
                }
                playlists.append(pl_info)
            return {"success": True, "playlists": playlists}
        except Exception as e:
            return {"success": False, "playlists": [], "message": str(e)}

    def get_playlist_detail(self, playlist_id):
        """Get all songs in a playlist."""
        try:
            result = self._netease.get_playlist_detail(playlist_id)
            playlist = result.get("playlist", {})
            songs = []
            for track in playlist.get("tracks", []):
                songs.append({
                    "id": track.get("id"),
                    "name": track.get("name", ""),
                    "artists": ", ".join(a.get("name", "") for a in track.get("ar", [])),
                    "album": track.get("al", {}).get("name", ""),
                    "cover": track.get("al", {}).get("picUrl", ""),
                    "duration": track.get("dt", 0) // 1000,
                })
            return {
                "success": True,
                "playlist": {
                    "id": playlist.get("id"),
                    "name": playlist.get("name", ""),
                    "cover": playlist.get("coverImgUrl", ""),
                    "track_count": playlist.get("trackCount", 0),
                },
                "songs": songs,
            }
        except Exception as e:
            return {"success": False, "songs": [], "message": str(e)}

    # --- Toplists ---
    def get_toplist(self):
        """Get all official toplists."""
        try:
            result = self._netease.get_toplist_detail()
            lists = []
            for tl in result.get("list", []):
                lists.append({
                    "id": tl.get("id"),
                    "name": tl.get("name", ""),
                    "cover": tl.get("coverImgUrl", ""),
                    "update_frequency": tl.get("updateFrequency", ""),
                })
            return {"success": True, "lists": lists}
        except Exception as e:
            return {"success": False, "lists": [], "message": str(e)}

    def get_toplist_detail(self, toplist_id):
        """Get songs in a toplist (same as playlist detail)."""
        return self.get_playlist_detail(toplist_id)

    # --- Downloads ---
    def download_song(self, song_id, title, artist, album, cover, quality="320k"):
        """Download a song to local storage."""
        try:
            return self._download_mgr.download_song(
                song_id=song_id, title=title, artist=artist,
                album=album, cover_url=cover, quality=quality,
            )
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_downloads(self):
        """Get list of downloaded songs."""
        try:
            downloads = self._download_mgr.get_download_list()
            caches = self._download_mgr.get_cache_list()
            return {"success": True, "downloads": downloads, "caches": caches}
        except Exception as e:
            return {"success": False, "downloads": [], "caches": [], "message": str(e)}

    def delete_download(self, download_id):
        try:
            self._download_mgr.delete_download(download_id)
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_cache(self, cache_id):
        try:
            self._download_mgr.delete_cache(cache_id)
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def export_song(self, song_id, target_path):
        try:
            return self._download_mgr.export_song(song_id, target_path)
        except Exception as e:
            return {"success": False, "message": str(e)}

    def cleanup(self):
        """Clean up resources on exit."""
        self._player.destroy()
        self._netease.close()
        self._db.close()
```

- [ ] **Step 2: Verify API imports**

Run:
```powershell
cd E:\NeMusic
python -c "from backend.api import NeMusicAPI; api = NeMusicAPI(); print('NeMusicAPI created'); api.cleanup()"
```

- [ ] **Step 3: Commit**

---

### Task 9: Frontend — HTML Shell & Global Styles

**Files:**
- Create: `E:\NeMusic\frontend\index.html`
- Create: `E:\NeMusic\frontend\css\main.css`

**Produces:** Complete HTML layout with all page sections, CSS variables, typography, and layout grid.

- [ ] **Step 1: Write index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeMusic - 网易云音乐</title>
    <link rel="stylesheet" href="css/main.css">
    <link rel="stylesheet" href="css/sidebar.css">
    <link rel="stylesheet" href="css/player-bar.css">
    <link rel="stylesheet" href="css/lyrics.css">
    <link rel="stylesheet" href="css/search.css">
    <link rel="stylesheet" href="css/playlist.css">
    <link rel="stylesheet" href="css/download.css">
</head>
<body>
    <!-- App Container -->
    <div id="app">
        <!-- Sidebar -->
        <nav id="sidebar">
            <div class="sidebar-header">
                <h1 class="app-logo">🎵 NeMusic</h1>
            </div>
            <ul class="nav-menu">
                <li class="nav-item active" data-page="search">
                    <span class="nav-icon">🔍</span> 搜索
                </li>
                <li class="nav-item" data-page="playlists">
                    <span class="nav-icon">📋</span> 我的歌单
                </li>
                <li class="nav-item" data-page="toplist">
                    <span class="nav-icon">🏆</span> 排行榜
                </li>
                <li class="nav-item" data-page="downloads">
                    <span class="nav-icon">💾</span> 下载管理
                </li>
            </ul>
            <!-- Login area -->
            <div class="sidebar-footer" id="login-area">
                <button class="btn-login" id="btn-login">🔑 登录</button>
            </div>
        </nav>

        <!-- Main Content -->
        <main id="main-content">
            <!-- Search Page -->
            <section id="page-search" class="page active">
                <div class="search-box">
                    <input type="text" id="search-input" placeholder="搜索歌曲、歌手、专辑..." autocomplete="off">
                    <button id="search-btn">搜索</button>
                </div>
                <div class="search-results" id="search-results">
                    <p class="empty-hint">输入关键词搜索歌曲</p>
                </div>
            </section>

            <!-- Playlists Page -->
            <section id="page-playlists" class="page">
                <div id="playlist-list" class="card-grid">
                    <p class="empty-hint">请先登录查看歌单</p>
                </div>
            </section>

            <!-- Playlist Detail Page (nested in playlists) -->
            <section id="page-playlist-detail" class="page">
                <div class="detail-header">
                    <button class="btn-back" id="btn-back-playlist">← 返回</button>
                    <img id="playlist-detail-cover" class="detail-cover" src="" alt="">
                    <div class="detail-info">
                        <h2 id="playlist-detail-name"></h2>
                        <p id="playlist-detail-meta"></p>
                        <button class="btn-play-all" id="btn-play-all-playlist">▶ 播放全部</button>
                    </div>
                </div>
                <div class="song-list" id="playlist-detail-songs"></div>
            </section>

            <!-- Toplist Page -->
            <section id="page-toplist" class="page">
                <div id="toplist-list" class="card-grid"></div>
            </section>

            <!-- Toplist Detail Page -->
            <section id="page-toplist-detail" class="page">
                <div class="detail-header">
                    <button class="btn-back" id="btn-back-toplist">← 返回</button>
                    <img id="toplist-detail-cover" class="detail-cover" src="" alt="">
                    <div class="detail-info">
                        <h2 id="toplist-detail-name"></h2>
                        <button class="btn-play-all" id="btn-play-all-toplist">▶ 播放全部</button>
                    </div>
                </div>
                <div class="song-list" id="toplist-detail-songs"></div>
            </section>

            <!-- Downloads Page -->
            <section id="page-downloads" class="page">
                <div class="download-tabs">
                    <button class="tab-btn active" data-tab="downloads-tab">已下载</button>
                    <button class="tab-btn" data-tab="cache-tab">缓存管理</button>
                </div>
                <div id="downloads-tab" class="tab-content active">
                    <div class="song-list" id="download-list"></div>
                    <p class="empty-hint" id="download-empty">暂无下载歌曲</p>
                </div>
                <div id="cache-tab" class="tab-content">
                    <div class="song-list" id="cache-list"></div>
                    <p class="empty-hint" id="cache-empty">暂无缓存</p>
                </div>
            </section>

            <!-- Lyrics View (overlay) -->
            <section id="page-lyrics" class="page lyrics-overlay">
                <div class="lyrics-bg" id="lyrics-bg"></div>
                <div class="lyrics-content">
                    <button class="btn-close-lyrics" id="btn-close-lyrics">✕</button>
                    <div class="lyrics-song-info">
                        <img id="lyrics-cover" src="" alt="">
                        <h3 id="lyrics-title"></h3>
                        <p id="lyrics-artist"></p>
                    </div>
                    <div class="lyrics-scroll" id="lyrics-scroll">
                        <p class="lyrics-empty">暂无歌词</p>
                    </div>
                </div>
            </section>
        </main>

        <!-- Bottom Player Bar -->
        <footer id="player-bar">
            <div class="player-left">
                <img id="player-cover" class="player-cover" src="" alt="">
                <div class="player-song-info" id="player-song-info-area">
                    <span id="player-title" class="player-title">未播放</span>
                    <span id="player-artist" class="player-artist"></span>
                </div>
            </div>
            <div class="player-center">
                <div class="player-controls">
                    <button class="btn-ctrl" id="btn-prev">⏮</button>
                    <button class="btn-ctrl btn-play" id="btn-play">▶️</button>
                    <button class="btn-ctrl" id="btn-next">⏭</button>
                </div>
                <div class="player-progress">
                    <span id="progress-current">0:00</span>
                    <input type="range" id="progress-bar" min="0" max="100" value="0">
                    <span id="progress-total">0:00</span>
                </div>
            </div>
            <div class="player-right">
                <button class="btn-ctrl" id="btn-lyrics">🎤</button>
                <div class="volume-control">
                    <span>🔊</span>
                    <input type="range" id="volume-bar" min="0" max="100" value="70">
                </div>
            </div>
        </footer>
    </div>

    <!-- Login Modal -->
    <div id="login-modal" class="modal hidden">
        <div class="modal-content">
            <button class="modal-close" id="modal-close">✕</button>
            <h2>登录网易云音乐</h2>
            <div class="login-tabs">
                <button class="tab-btn active" data-login-tab="qr">二维码登录</button>
                <button class="tab-btn" data-login-tab="phone">手机号登录</button>
            </div>
            <div id="login-qr-tab" class="login-tab-content active">
                <div id="qr-container">
                    <p>加载中...</p>
                </div>
            </div>
            <div id="login-phone-tab" class="login-tab-content">
                <input type="text" id="login-phone-input" placeholder="手机号">
                <input type="password" id="login-password-input" placeholder="密码">
                <button class="btn-primary" id="btn-phone-login">登录</button>
                <p id="login-phone-error" class="login-error"></p>
            </div>
        </div>
    </div>

    <!-- Toast Container -->
    <div id="toast-container"></div>

    <script src="js/utils.js"></script>
    <script src="js/api-bridge.js"></script>
    <script src="js/player.js"></script>
    <script src="js/lyrics.js"></script>
    <script src="js/search.js"></script>
    <script src="js/playlist.js"></script>
    <script src="js/download.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Write main.css**

```css
/* === CSS Variables & Reset === */
:root {
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-card: #1f2b47;
    --bg-hover: #2a3a5c;
    --text-primary: #e8e8e8;
    --text-secondary: #a0a0b8;
    --accent: #ec4141;
    --accent-hover: #ff5a5a;
    --player-height: 72px;
    --sidebar-width: 220px;
    --border-radius: 8px;
    --shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    overflow: hidden;
    height: 100vh;
    user-select: none;
}

#app {
    display: grid;
    grid-template-columns: var(--sidebar-width) 1fr;
    grid-template-rows: 1fr var(--player-height);
    height: 100vh;
}

#main-content {
    overflow-y: auto;
    padding: 24px;
    position: relative;
}

/* === Shared === */
.page {
    display: none;
}
.page.active {
    display: block;
}

.empty-hint {
    color: var(--text-secondary);
    text-align: center;
    padding: 60px 20px;
    font-size: 15px;
}

.btn-primary {
    padding: 10px 24px;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-size: 14px;
}
.btn-primary:hover {
    background: var(--accent-hover);
}

.btn-play-all {
    padding: 8px 28px;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-size: 14px;
    margin-top: 8px;
}
.btn-play-all:hover {
    background: var(--accent-hover);
}

/* Cards */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 16px;
}

.card {
    background: var(--bg-card);
    border-radius: var(--border-radius);
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.15s;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow);
}
.card img {
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
}
.card-body {
    padding: 10px 12px;
}
.card-body h4 {
    font-size: 13px;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.card-body p {
    font-size: 12px;
    color: var(--text-secondary);
}

/* Song List */
.song-list {
    margin-top: 12px;
}
.song-item {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    border-radius: var(--border-radius);
    cursor: pointer;
    gap: 12px;
}
.song-item:hover {
    background: var(--bg-hover);
}
.song-item.playing {
    background: var(--bg-hover);
    color: var(--accent);
}
.song-index {
    width: 30px;
    text-align: center;
    color: var(--text-secondary);
    font-size: 13px;
}
.song-item .song-cover {
    width: 40px;
    height: 40px;
    border-radius: 4px;
    object-fit: cover;
}
.song-item .song-info {
    flex: 1;
    min-width: 0;
}
.song-item .song-name {
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.song-item .song-artist {
    font-size: 12px;
    color: var(--text-secondary);
}
.song-item .song-duration {
    font-size: 12px;
    color: var(--text-secondary);
    margin-right: 8px;
}
.song-item .btn-song-action {
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 14px;
    padding: 4px 8px;
    border-radius: 4px;
}
.song-item .btn-song-action:hover {
    color: var(--accent);
}

/* Detail Header */
.detail-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 16px;
}
.detail-cover {
    width: 160px;
    height: 160px;
    border-radius: var(--border-radius);
    object-fit: cover;
}
.detail-info h2 {
    font-size: 22px;
    margin-bottom: 8px;
}
.detail-info p {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 4px;
}
.btn-back {
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 14px;
    padding: 4px 0;
    display: block;
    margin-bottom: 12px;
}
.btn-back:hover {
    color: var(--accent);
}

/* Modal */
.modal {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}
.modal.hidden {
    display: none;
}
.modal-content {
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 28px;
    min-width: 360px;
    max-width: 420px;
    position: relative;
}
.modal-content h2 {
    margin-bottom: 20px;
    font-size: 20px;
}
.modal-close {
    position: absolute;
    top: 12px;
    right: 16px;
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 18px;
    cursor: pointer;
}
.modal-close:hover {
    color: var(--text-primary);
}

/* Login */
.login-tabs {
    display: flex;
    gap: 0;
    margin-bottom: 16px;
}
.tab-btn {
    flex: 1;
    padding: 8px;
    background: var(--bg-card);
    color: var(--text-secondary);
    border: none;
    cursor: pointer;
    font-size: 13px;
}
.tab-btn.active {
    background: var(--accent);
    color: white;
}
.tab-btn:first-child {
    border-radius: 6px 0 0 6px;
}
.tab-btn:last-child {
    border-radius: 0 6px 6px 0;
}
.login-tab-content {
    display: none;
    text-align: center;
}
.login-tab-content.active {
    display: block;
}
.login-tab-content input {
    display: block;
    width: 100%;
    padding: 10px 12px;
    margin-bottom: 10px;
    background: var(--bg-card);
    border: 1px solid var(--bg-hover);
    border-radius: var(--border-radius);
    color: var(--text-primary);
    font-size: 14px;
}
.login-tab-content input:focus {
    outline: none;
    border-color: var(--accent);
}
.login-error {
    color: var(--accent);
    font-size: 13px;
    margin-top: 8px;
}

/* Tabs */
.download-tabs {
    display: flex;
    gap: 0;
    margin-bottom: 16px;
}
.tab-content {
    display: none;
}
.tab-content.active {
    display: block;
}

/* Toast */
#toast-container {
    position: fixed;
    top: 16px;
    right: 16px;
    z-index: 2000;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.toast {
    padding: 10px 20px;
    background: var(--bg-card);
    color: var(--text-primary);
    border-radius: var(--border-radius);
    font-size: 13px;
    box-shadow: var(--shadow);
    animation: toastIn 0.3s ease;
}
@keyframes toastIn {
    from { opacity: 0; transform: translateX(50px); }
    to { opacity: 1; transform: translateX(0); }
}
.toast.error {
    border-left: 3px solid var(--accent);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: var(--bg-hover);
    border-radius: 3px;
}
```

- [ ] **Step 3: Verify**

Run:
```powershell
cd E:\NeMusic
python main.py
```

Expected: Window opens showing the full layout (sidebar, main content area, player bar). Pages will be empty/stub.

- [ ] **Step 4: Commit**

---

### Task 10: Frontend — Sidebar & Player Bar CSS

**Files:**
- Create: `E:\NeMusic\frontend\css\sidebar.css`
- Create: `E:\NeMusic\frontend\css\player-bar.css`

**Produces:** Styled sidebar navigation and fixed bottom player bar.

- [ ] **Step 1: Write sidebar.css**

```css
/* === Sidebar === */
#sidebar {
    background: var(--bg-secondary);
    display: flex;
    flex-direction: column;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    grid-row: 1 / 3;
}

.sidebar-header {
    padding: 20px 16px 12px;
}
.app-logo {
    font-size: 18px;
    font-weight: 700;
    color: var(--accent);
}

.nav-menu {
    list-style: none;
    padding: 8px;
    flex: 1;
}
.nav-item {
    padding: 10px 12px;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-size: 14px;
    color: var(--text-secondary);
    transition: background 0.15s, color 0.15s;
    display: flex;
    align-items: center;
    gap: 10px;
}
.nav-item:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}
.nav-item.active {
    background: var(--bg-hover);
    color: var(--accent);
    font-weight: 600;
}
.nav-icon {
    font-size: 16px;
    width: 22px;
    text-align: center;
}

.sidebar-footer {
    padding: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.btn-login {
    width: 100%;
    padding: 10px;
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--bg-hover);
    border-radius: var(--border-radius);
    cursor: pointer;
    font-size: 14px;
}
.btn-login:hover {
    background: var(--bg-hover);
}
.user-info {
    display: flex;
    align-items: center;
    gap: 10px;
}
.user-info img {
    width: 36px;
    height: 36px;
    border-radius: 50%;
}
.user-info .user-name {
    font-size: 13px;
    color: var(--text-primary);
}
.btn-logout {
    font-size: 11px;
    color: var(--text-secondary);
    cursor: pointer;
    background: none;
    border: none;
}
.btn-logout:hover {
    color: var(--accent);
}
```

- [ ] **Step 2: Write player-bar.css**

```css
/* === Bottom Player Bar === */
#player-bar {
    background: var(--bg-secondary);
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    padding: 0 20px;
    gap: 20px;
    z-index: 100;
}

.player-left {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 240px;
    min-width: 180px;
}
.player-cover {
    width: 46px;
    height: 46px;
    border-radius: 6px;
    object-fit: cover;
    background: var(--bg-card);
}
.player-song-info {
    min-width: 0;
    cursor: pointer;
    display: flex;
    flex-direction: column;
}
.player-title {
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.player-artist {
    font-size: 11px;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.player-center {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}
.player-controls {
    display: flex;
    align-items: center;
    gap: 16px;
}
.btn-ctrl {
    background: none;
    border: none;
    color: var(--text-primary);
    font-size: 18px;
    cursor: pointer;
    padding: 4px;
    border-radius: 50%;
    transition: color 0.15s;
}
.btn-ctrl:hover {
    color: var(--accent);
}
.btn-play {
    font-size: 24px;
    background: var(--accent);
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}
.btn-play:hover {
    background: var(--accent-hover);
    color: white;
}
.player-progress {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    max-width: 600px;
    font-size: 11px;
    color: var(--text-secondary);
}
#progress-bar {
    flex: 1;
    height: 4px;
    -webkit-appearance: none;
    appearance: none;
    background: var(--bg-hover);
    border-radius: 2px;
    outline: none;
    cursor: pointer;
}
#progress-bar::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 12px;
    height: 12px;
    background: var(--accent);
    border-radius: 50%;
    cursor: pointer;
}

.player-right {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 180px;
    justify-content: flex-end;
}
.volume-control {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
}
#volume-bar {
    width: 80px;
    height: 4px;
    -webkit-appearance: none;
    appearance: none;
    background: var(--bg-hover);
    border-radius: 2px;
    outline: none;
    cursor: pointer;
}
#volume-bar::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 12px;
    height: 12px;
    background: var(--accent);
    border-radius: 50%;
    cursor: pointer;
}
```

- [ ] **Step 3: Verify and commit**

---

### Task 11: Frontend — Lyrics CSS

**Files:**
- Create: `E:\NeMusic\frontend\css\lyrics.css`

- [ ] **Step 1: Write lyrics.css**

```css
/* === Lyrics Overlay === */
.lyrics-overlay {
    position: absolute;
    inset: 0;
    z-index: 50;
}
.lyrics-bg {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    filter: blur(40px) brightness(0.3);
    transform: scale(1.1);
}
.lyrics-content {
    position: relative;
    z-index: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px 20px;
}
.btn-close-lyrics {
    position: absolute;
    top: 16px;
    left: 16px;
    background: rgba(255,255,255,0.1);
    border: none;
    color: var(--text-primary);
    font-size: 18px;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
}
.btn-close-lyrics:hover {
    background: rgba(255,255,255,0.2);
}

.lyrics-song-info {
    text-align: center;
    margin-bottom: 24px;
}
.lyrics-song-info img {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    margin-bottom: 12px;
}
.lyrics-song-info h3 {
    font-size: 18px;
    margin-bottom: 4px;
}
.lyrics-song-info p {
    font-size: 13px;
    color: var(--text-secondary);
}

.lyrics-scroll {
    flex: 1;
    overflow-y: auto;
    width: 100%;
    max-width: 600px;
    text-align: center;
    padding: 20px 0;
    scroll-behavior: smooth;
}
.lyrics-line {
    padding: 8px 20px;
    font-size: 16px;
    color: rgba(255,255,255,0.4);
    transition: color 0.3s, font-size 0.3s;
    cursor: pointer;
}
.lyrics-line.active {
    color: var(--accent);
    font-size: 20px;
    font-weight: 600;
}
.lyrics-line:hover {
    color: rgba(255,255,255,0.7);
}
.lyrics-empty {
    color: var(--text-secondary);
    margin-top: 60px;
}
```

- [ ] **Step 2: Commit**

---

### Task 12: Frontend — Remaining CSS (search, playlist, download)

**Files:**
- Create: `E:\NeMusic\frontend\css\search.css`
- Create: `E:\NeMusic\frontend\css\playlist.css`
- Create: `E:\NeMusic\frontend\css\download.css`

- [ ] **Step 1: Write search.css**

```css
/* === Search === */
.search-box {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}
.search-box input {
    flex: 1;
    padding: 10px 16px;
    background: var(--bg-card);
    border: 1px solid var(--bg-hover);
    border-radius: var(--border-radius);
    color: var(--text-primary);
    font-size: 14px;
}
.search-box input:focus {
    outline: none;
    border-color: var(--accent);
}
.search-box button {
    padding: 10px 24px;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-size: 14px;
}
.search-box button:hover {
    background: var(--accent-hover);
}
.search-results .song-item {
    display: grid;
    grid-template-columns: 40px 40px 1fr auto auto;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
}
```

- [ ] **Step 2: Write playlist.css**

```css
/* === Playlist === */
#page-playlist-detail .song-item,
#page-toplist-detail .song-item {
    display: grid;
    grid-template-columns: 30px 40px 1fr auto auto;
    align-items: center;
    gap: 12px;
}
```

- [ ] **Step 3: Write download.css**

```css
/* === Downloads === */
#page-downloads .song-item {
    display: grid;
    grid-template-columns: 40px 1fr auto auto auto;
    align-items: center;
    gap: 12px;
}
```

- [ ] **Step 4: Commit**

---

### Task 13: Frontend — Utility & API Bridge JS

**Files:**
- Create: `E:\NeMusic\frontend\js\utils.js`
- Create: `E:\NeMusic\frontend\js\api-bridge.js`

**Produces:** Shared helpers and the JS-Python communication layer.

- [ ] **Step 1: Write utils.js**

```javascript
/* === Utility Functions === */
const $ = (sel, parent) => (parent || document).querySelector(sel);
const $$ = (sel, parent) => [...(parent || document).querySelectorAll(sel)];

function formatTime(seconds) {
    if (!seconds || seconds <= 0) return "0:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
}

function formatCount(n) {
    if (n >= 100000000) return (n / 100000000).toFixed(1) + "亿";
    if (n >= 10000) return (n / 10000).toFixed(1) + "万";
    return String(n);
}

function showToast(message, type = "") {
    const container = $("#toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function showPage(pageName) {
    $$(".page").forEach(p => p.classList.remove("active"));
    const page = $(`#page-${pageName}`);
    if (page) page.classList.add("active");

    $$(".nav-item").forEach(i => i.classList.remove("active"));
    const navItem = $(`.nav-item[data-page="${pageName}"]`);
    if (navItem) navItem.classList.add("active");
}
```

- [ ] **Step 2: Write api-bridge.js**

```javascript
/* === Python-JS Bridge === */

/**
 * NeMusic global namespace.
 * Calls Python backend methods via window.pywebview.api.
 * Handles async communication pattern.
 */
window.NeMusic = window.NeMusic || {};

const NeMusic = window.NeMusic;

// Event listeners registry
NeMusic._listeners = {};

/**
 * Register an event listener.
 * @param {string} event - Event name
 * @param {function} callback - Called with event data
 */
NeMusic.on = function (event, callback) {
    if (!NeMusic._listeners[event]) {
        NeMusic._listeners[event] = [];
    }
    NeMusic._listeners[event].push(callback);
};

/**
 * Receive and dispatch events from Python.
 * Called by Python via window.evaluate_js('NeMusic.emit(...)').
 * @param {object} payload - {event: string, data: object}
 */
NeMusic.emit = function (payload) {
    const listeners = NeMusic._listeners[payload.event] || [];
    listeners.forEach(fn => {
        try { fn(payload.data); } catch (e) { console.error(e); }
    });
};

/**
 * Call a Python API method.
 * pywebview makes sync JS->Python calls, so we fire-and-forget
 * or get the return value directly.
 */
NeMusic.api = window.pywebview ? window.pywebview.api : null;

if (!NeMusic.api) {
    console.warn("pywebview API not available — running in browser mode");
    // Provide mock for browser development
    NeMusic.api = new Proxy({}, {
        get(target, prop) {
            return (...args) => {
                console.log(`[Mock API] ${prop}`, args);
                return Promise.resolve({ success: false, message: "Running in browser (no Python backend)" });
            };
        }
    });
}
```

- [ ] **Step 3: Commit**

---

### Task 14: Frontend — Player JS & Lyrics JS

**Files:**
- Create: `E:\NeMusic\frontend\js\player.js`
- Create: `E:\NeMusic\frontend\js\lyrics.js`

**Consumes:** `NeMusic.api`, `utils.js`
**Produces:** Player control logic (play/pause/next/prev/progress/volume) and lyrics display.

- [ ] **Step 1: Write player.js**

```javascript
/* === Player Frontend Logic === */

const PlayerUI = {
    elements: {},

    init() {
        this.elements = {
            cover: $("#player-cover"),
            title: $("#player-title"),
            artist: $("#player-artist"),
            btnPlay: $("#btn-play"),
            btnPrev: $("#btn-prev"),
            btnNext: $("#btn-next"),
            btnLyrics: $("#btn-lyrics"),
            progressBar: $("#progress-bar"),
            progressCurrent: $("#progress-current"),
            progressTotal: $("#progress-total"),
            volumeBar: $("#volume-bar"),
            songInfoArea: $("#player-song-info-area"),
        };

        this._bindEvents();
        this._bindNeMusicEvents();
        this._loadVolume();
    },

    _bindEvents() {
        this.elements.btnPlay.addEventListener("click", () => {
            NeMusic.api.toggle_play_pause();
        });

        this.elements.btnPrev.addEventListener("click", () => {
            NeMusic.api.prev_song();
        });

        this.elements.btnNext.addEventListener("click", () => {
            NeMusic.api.next_song();
        });

        this.elements.btnLyrics.addEventListener("click", () => {
            LyricsUI.toggle();
        });

        this.elements.songInfoArea.addEventListener("click", () => {
            LyricsUI.show();
        });

        // Progress bar
        let progressDragging = false;
        this.elements.progressBar.addEventListener("mousedown", () => {
            progressDragging = true;
        });
        document.addEventListener("mouseup", () => {
            if (progressDragging) {
                progressDragging = false;
                const pct = parseInt(this.elements.progressBar.value);
                const total = parseFloat(this.elements.progressTotal.dataset.total || 0);
                if (total > 0) {
                    const seekSec = (pct / 100) * total;
                    NeMusic.api.seek(seekSec);
                }
            }
        });
        this.elements.progressBar.addEventListener("input", () => {
            if (!progressDragging) progressDragging = true;
        });

        // Volume
        this.elements.volumeBar.value = 70;
        this.elements.volumeBar.addEventListener("input", () => {
            const vol = parseInt(this.elements.volumeBar.value);
            NeMusic.api.set_volume(vol);
            localStorage.setItem("nemusic_volume", vol);
        });
    },

    _loadVolume() {
        const saved = localStorage.getItem("nemusic_volume");
        if (saved !== null) {
            const vol = parseInt(saved);
            this.elements.volumeBar.value = vol;
            NeMusic.api.set_volume(vol);
        }
    },

    _bindNeMusicEvents() {
        NeMusic.on("position_change", (data) => {
            this.elements.progressCurrent.textContent = formatTime(data.current);
            this.elements.progressTotal.textContent = formatTime(data.total);
            this.elements.progressTotal.dataset.total = data.total;
            if (document.activeElement !== this.elements.progressBar) {
                this.elements.progressBar.value = data.percentage;
            }
            LyricsUI.updatePosition(data.current);
        });

        NeMusic.on("state_change", (data) => {
            if (data.state === "playing") {
                this.elements.btnPlay.textContent = "⏸";
            } else {
                this.elements.btnPlay.textContent = "▶️";
            }
        });

        NeMusic.on("song_end", () => {
            // Auto-next is handled by Python. UI will update on next state_change.
        });

        NeMusic.on("error", (data) => {
            showToast(data.message || "播放出错", "error");
        });

        NeMusic.on("song_change", (data) => {
            this.updateNowPlaying(data);
        });
    },

    /** Update now-playing display */
    updateNowPlaying(song) {
        this.elements.cover.src = song.cover || "";
        this.elements.title.textContent = song.name || "未播放";
        this.elements.artist.textContent = song.artists || "";
    },
};
```

- [ ] **Step 2: Write lyrics.js**

```javascript
/* === Lyrics Frontend Logic === */

const LyricsUI = {
    elements: {},
    lines: [],
    currentIndex: -1,
    isVisible: false,

    init() {
        this.elements = {
            overlay: $("#page-lyrics"),
            bg: $("#lyrics-bg"),
            cover: $("#lyrics-cover"),
            title: $("#lyrics-title"),
            artist: $("#lyrics-artist"),
            scroll: $("#lyrics-scroll"),
            btnClose: $("#btn-close-lyrics"),
        };

        this.elements.btnClose.addEventListener("click", () => this.hide());
    },

    async load(songId) {
        this.reset();
        const result = await NeMusic.api.get_lyric(songId);
        this.lines = result.lines || [];

        if (!this.lines.length) {
            this.elements.scroll.innerHTML = `<p class="lyrics-empty">${result.message || "暂无歌词"}</p>`;
        } else {
            this.elements.scroll.innerHTML = this.lines.map((line, i) =>
                `<p class="lyrics-line" data-index="${i}" data-time="${line.time}">${line.text}</p>`
            ).join("");

            // Click to seek
            this.elements.scroll.querySelectorAll(".lyrics-line").forEach(el => {
                el.addEventListener("click", () => {
                    const time = parseFloat(el.dataset.time);
                    NeMusic.api.seek(time);
                });
            });
        }
    },

    updatePosition(currentSec) {
        if (!this.lines.length) return;

        let activeIdx = -1;
        for (let i = 0; i < this.lines.length; i++) {
            if (this.lines[i].time <= currentSec) {
                activeIdx = i;
            } else {
                break;
            }
        }

        if (activeIdx !== this.currentIndex) {
            this.currentIndex = activeIdx;
            this._highlightLine(activeIdx);
        }
    },

    _highlightLine(index) {
        const lines = this.elements.scroll.querySelectorAll(".lyrics-line");
        lines.forEach(l => l.classList.remove("active"));

        if (index >= 0 && index < lines.length) {
            const el = lines[index];
            el.classList.add("active");
            // Scroll to center
            const containerH = this.elements.scroll.clientHeight;
            const elTop = el.offsetTop;
            const elH = el.clientHeight;
            this.elements.scroll.scrollTop = elTop - containerH / 2 + elH / 2;
        }
    },

    show() {
        const song = NeMusic.api.get_current_song ? NeMusic.api.get_current_song() : {};
        if (song && song.id) {
            // Update covers
            song = NeMusic.api.get_current_song();
        }
        // Async: get current song info
        this._showWithSong();
    },

    async _showWithSong() {
        // Try to get current song via API
        let song;
        try {
            song = NeMusic.api.get_current_song();
        } catch (e) {
            song = {};
        }

        if (song && song.id) {
            this.elements.cover.src = song.cover || "";
            this.elements.title.textContent = song.name || "";
            this.elements.artist.textContent = song.artists || "";
            this.elements.bg.style.backgroundImage = `url(${song.cover || ""})`;
            await this.load(song.id);
        }

        this.elements.overlay.classList.add("active");
        this.isVisible = true;
    },

    hide() {
        this.elements.overlay.classList.remove("active");
        this.isVisible = false;
        showPage(this._previousPage || "search");
    },

    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            // Save current page
            const activePage = document.querySelector(".page.active");
            if (activePage) {
                this._previousPage = activePage.id.replace("page-", "");
            }
            this.show();
        }
    },

    reset() {
        this.lines = [];
        this.currentIndex = -1;
        this.elements.scroll.innerHTML = '<p class="lyrics-empty">暂无歌词</p>';
    },
};
```

- [ ] **Step 3: Commit**

---

### Task 15: Frontend — Search JS

**Files:**
- Create: `E:\NeMusic\frontend\js\search.js`

**Consumes:** `NeMusic.api`, `utils.js`, `PlayerUI`

- [ ] **Step 1: Write search.js**

```javascript
/* === Search Page Logic === */

const SearchUI = {
    init() {
        $("#search-btn").addEventListener("click", () => this.doSearch());
        $("#search-input").addEventListener("keydown", (e) => {
            if (e.key === "Enter") this.doSearch();
        });
    },

    async doSearch() {
        const keyword = $("#search-input").value.trim();
        if (!keyword) return;

        showToast(`搜索: ${keyword}`);
        const result = await NeMusic.api.search(keyword, 50, 0);

        const container = $("#search-results");
        if (!result.success || !result.songs.length) {
            container.innerHTML = '<p class="empty-hint">未找到相关歌曲</p>';
            return;
        }

        container.innerHTML = result.songs.map((song, i) => `
            <div class="song-item" data-song='${JSON.stringify(song).replace(/'/g, "&#39;")}'>
                <span class="song-index">${i + 1}</span>
                <img class="song-cover" src="${song.cover || ''}" alt="" onerror="this.style.display='none'">
                <div class="song-info">
                    <div class="song-name">${song.name}</div>
                    <div class="song-artist">${song.artists}</div>
                </div>
                <span class="song-duration">${formatTime(song.duration)}</span>
                <button class="btn-song-action download-btn" data-songid="${song.id}" title="下载">⬇</button>
            </div>
        `).join("");

        // Click to play
        container.querySelectorAll(".song-item").forEach(item => {
            item.addEventListener("click", (e) => {
                if (e.target.closest(".download-btn")) return;
                const song = JSON.parse(item.dataset.song);
                this.playSong(song);
            });
        });

        // Download button
        container.querySelectorAll(".download-btn").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                e.stopPropagation();
                const songId = parseInt(btn.dataset.songid);
                const item = btn.closest(".song-item");
                const song = JSON.parse(item.dataset.song);
                const result = await NeMusic.api.download_song(
                    song.id, song.name, song.artists, song.album, song.cover, "320k"
                );
                showToast(result.message || (result.success ? "下载成功" : "下载失败"), result.success ? "" : "error");
            });
        });
    },

    async playSong(song) {
        const result = await NeMusic.api.play_song(song);
        if (result.success) {
            PlayerUI.updateNowPlaying(song);
        } else {
            showToast(result.message || "播放失败", "error");
        }
    },
};
```

- [ ] **Step 2: Commit**

---

### Task 16: Frontend — Playlist JS & Download JS

**Files:**
- Create: `E:\NeMusic\frontend\js\playlist.js`
- Create: `E:\NeMusic\frontend\js\download.js`

**Consumes:** `NeMusic.api`, `utils.js`, `PlayerUI`

- [ ] **Step 1: Write playlist.js**

```javascript
/* === Playlist & Toplist Page Logic === */

const PlaylistUI = {
    init() {
        // Back buttons
        $("#btn-back-playlist").addEventListener("click", () => showPage("playlists"));
        $("#btn-back-toplist").addEventListener("click", () => showPage("toplist"));

        // Play all buttons
        $("#btn-play-all-playlist").addEventListener("click", () => this._playAllFrom("playlist-detail-songs"));
        $("#btn-play-all-toplist").addEventListener("click", () => this._playAllFrom("toplist-detail-songs"));
    },

    async loadUserPlaylists() {
        const result = await NeMusic.api.get_user_playlists();
        const container = $("#playlist-list");

        if (!result.success || !result.playlists.length) {
            container.innerHTML = `<p class="empty-hint">${result.message || "请先登录查看歌单"}</p>`;
            return;
        }

        container.innerHTML = result.playlists.map(pl => `
            <div class="card" data-plid="${pl.id}">
                <img src="${pl.cover || ''}" alt="${pl.name}" onerror="this.src=''">
                <div class="card-body">
                    <h4>${pl.name}</h4>
                    <p>${pl.track_count} 首 · ${pl.creator}</p>
                </div>
            </div>
        `).join("");

        container.querySelectorAll(".card").forEach(card => {
            card.addEventListener("click", () => {
                const plId = parseInt(card.dataset.plid);
                this.showPlaylistDetail(plId);
            });
        });
    },

    async loadToplist() {
        const result = await NeMusic.api.get_toplist();
        const container = $("#toplist-list");

        if (!result.success || !result.lists.length) {
            container.innerHTML = '<p class="empty-hint">加载排行榜失败</p>';
            return;
        }

        container.innerHTML = result.lists.map(tl => `
            <div class="card" data-tlid="${tl.id}">
                <img src="${tl.cover || ''}" alt="${tl.name}" onerror="this.src=''">
                <div class="card-body">
                    <h4>${tl.name}</h4>
                    <p>${tl.update_frequency || ''}</p>
                </div>
            </div>
        `).join("");

        container.querySelectorAll(".card").forEach(card => {
            card.addEventListener("click", () => {
                const tlId = parseInt(card.dataset.tlid);
                this.showToplistDetail(tlId);
            });
        });
    },

    async showPlaylistDetail(plId) {
        const result = await NeMusic.api.get_playlist_detail(plId);
        if (!result.success) {
            showToast(result.message, "error");
            return;
        }

        const pl = result.playlist;
        $("#playlist-detail-cover").src = pl.cover || "";
        $("#playlist-detail-name").textContent = pl.name;
        $("#playlist-detail-meta").textContent = `${pl.track_count} 首`;

        this._renderSongList("playlist-detail-songs", result.songs);
        showPage("playlist-detail");
    },

    async showToplistDetail(tlId) {
        const result = await NeMusic.api.get_toplist_detail(tlId);
        if (!result.success) {
            showToast(result.message, "error");
            return;
        }

        const pl = result.playlist;
        $("#toplist-detail-cover").src = pl.cover || "";
        $("#toplist-detail-name").textContent = pl.name;

        this._renderSongList("toplist-detail-songs", result.songs);
        showPage("toplist-detail");
    },

    _renderSongList(containerId, songs) {
        const container = $(`#${containerId}`);
        container.innerHTML = songs.map((song, i) => `
            <div class="song-item" data-song='${JSON.stringify(song).replace(/'/g, "&#39;")}'>
                <span class="song-index">${i + 1}</span>
                <img class="song-cover" src="${song.cover || ''}" alt="" onerror="this.style.display='none'">
                <div class="song-info">
                    <div class="song-name">${song.name}</div>
                    <div class="song-artist">${song.artists}</div>
                </div>
                <span class="song-duration">${formatTime(song.duration)}</span>
                <button class="btn-song-action download-btn" data-songid="${song.id}" title="下载">⬇</button>
            </div>
        `).join("");

        container.querySelectorAll(".song-item").forEach(item => {
            item.addEventListener("click", async (e) => {
                if (e.target.closest(".download-btn")) return;
                const song = JSON.parse(item.dataset.song);

                // Play all songs from this index
                const allSongs = songs;
                await NeMusic.api.play_songs(allSongs, i);
                PlayerUI.updateNowPlaying(song);
            });
        });

        container.querySelectorAll(".download-btn").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                e.stopPropagation();
                const songId = parseInt(btn.dataset.songid);
                const item = btn.closest(".song-item");
                const song = JSON.parse(item.dataset.song);
                const result = await NeMusic.api.download_song(
                    song.id, song.name, song.artists, song.album, song.cover, "320k"
                );
                showToast(result.message || (result.success ? "下载成功" : "下载失败"), result.success ? "" : "error");
            });
        });
    },

    async _playAllFrom(containerId) {
        const items = $$(`#${containerId} .song-item`);
        if (!items.length) return;
        const songs = items.map(item => JSON.parse(item.dataset.song));
        await NeMusic.api.play_songs(songs, 0);
        PlayerUI.updateNowPlaying(songs[0]);
    },
};
```

- [ ] **Step 2: Write download.js**

```javascript
/* === Download Management Page Logic === */

const DownloadUI = {
    init() {
        // Tab switching
        $$(".download-tabs .tab-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                $$(".download-tabs .tab-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");

                $$("#page-downloads .tab-content").forEach(t => t.classList.remove("active"));
                $(`#${btn.dataset.tab}`).classList.add("active");
            });
        });
    },

    async load() {
        const result = await NeMusic.api.get_downloads();
        if (!result.success) return;

        this._renderDownloadList(result.downloads || []);
        this._renderCacheList(result.caches || []);
    },

    _renderDownloadList(downloads) {
        const container = $("#download-list");
        const emptyHint = $("#download-empty");

        if (!downloads.length) {
            container.innerHTML = "";
            emptyHint.style.display = "block";
            return;
        }

        emptyHint.style.display = "none";
        container.innerHTML = downloads.map(d => `
            <div class="song-item" data-songid="${d.song_id}" data-path="${d.file_path || ''}">
                <img class="song-cover" src="${d.cover_url || ''}" alt="" onerror="this.style.display='none'">
                <div class="song-info">
                    <div class="song-name">${d.title}</div>
                    <div class="song-artist">${d.artist} · ${d.quality || ''} · ${formatFileSize(d.file_size)}</div>
                </div>
                <span class="song-duration">${d.downloaded ? new Date(d.downloaded).toLocaleDateString() : ""}</span>
                <button class="btn-song-action play-local" title="播放本地文件">▶</button>
                <button class="btn-song-action export-local" title="导出">📂</button>
                <button class="btn-song-action delete-dl" title="删除">🗑</button>
            </div>
        `).join("");

        this._bindDownloadActions(container);
    },

    _renderCacheList(caches) {
        const container = $("#cache-list");
        const emptyHint = $("#cache-empty");

        if (!caches.length) {
            container.innerHTML = "";
            emptyHint.style.display = "block";
            return;
        }

        emptyHint.style.display = "none";
        container.innerHTML = caches.map(c => `
            <div class="song-item" data-cacheid="${c.id}" data-path="${c.local_path || ''}">
                <img class="song-cover" src="${c.cover_url || ''}" alt="" onerror="this.style.display='none'">
                <div class="song-info">
                    <div class="song-name">${c.title}</div>
                    <div class="song-artist">${c.artist} · 缓存 · ${formatFileSize(c.size_bytes)}</div>
                </div>
                <span class="song-duration">${c.created_at ? new Date(c.created_at).toLocaleDateString() : ""}</span>
                <button class="btn-song-action play-local" title="播放本地文件">▶</button>
                <button class="btn-song-action delete-cache" title="删除">🗑</button>
            </div>
        `).join("");

        this._bindCacheActions(container);
    },

    _bindDownloadActions(container) {
        container.querySelectorAll(".play-local").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                e.stopPropagation();
                const item = btn.closest(".song-item");
                const songId = parseInt(item.dataset.songid);
                const path = item.dataset.path;
                // Play local file: create a song object and pass it, backend will use local path
                const song = { id: songId, name: item.querySelector(".song-name").textContent, artists: item.querySelector(".song-artist").textContent.split("·")[0].trim(), cover: item.querySelector(".song-cover").src };
                await NeMusic.api.play_song(song);
                PlayerUI.updateNowPlaying(song);
            });
        });

        container.querySelectorAll(".export-local").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                e.stopPropagation();
                const item = btn.closest(".song-item");
                const songId = parseInt(item.dataset.songid);
                const name = item.querySelector(".song-name").textContent;
                // Use the export API
                const targetPath = `E:\\NeMusic\\data\\downloads\\${name}.mp3`;
                const result = await NeMusic.api.export_song(songId, targetPath);
                showToast(result.message, result.success ? "" : "error");
            });
        });

        container.querySelectorAll(".delete-dl").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                e.stopPropagation();
                const item = btn.closest(".song-item");
                const dlId = parseInt(item.dataset.dlid);
                if (dlId) {
                    await NeMusic.api.delete_download(dlId);
                    showToast("已删除");
                    DownloadUI.load();
                }
            });
        });
    },

    _bindCacheActions(container) {
        container.querySelectorAll(".play-local").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                e.stopPropagation();
                const item = btn.closest(".song-item");
                const songId = parseInt(item.dataset.songid || 0);
                const song = { id: songId, name: item.querySelector(".song-name").textContent, artists: item.querySelector(".song-artist").textContent.split("·")[0].trim(), cover: item.querySelector(".song-cover").src };
                await NeMusic.api.play_song(song);
                PlayerUI.updateNowPlaying(song);
            });
        });

        container.querySelectorAll(".delete-cache").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                e.stopPropagation();
                const item = btn.closest(".song-item");
                const cacheId = parseInt(item.dataset.cacheid);
                await NeMusic.api.delete_cache(cacheId);
                showToast("缓存已删除");
                DownloadUI.load(); // Reload
            });
        });
    },
};

function formatFileSize(bytes) {
    if (!bytes) return "";
    const kb = bytes / 1024;
    if (kb < 1024) return kb.toFixed(1) + " KB";
    return (kb / 1024).toFixed(1) + " MB";
}
```

- [ ] **Step 3: Commit**

---

### Task 17: Frontend — App Entry (Router & Init)

**Files:**
- Create: `E:\NeMusic\frontend\js\app.js`

**Consumes:** All other JS modules, `NeMusic.api`

- [ ] **Step 1: Write app.js**

```javascript
/* === App Initialization & Router === */

const App = {
    async init() {
        // Initialize all UI modules
        PlayerUI.init();
        LyricsUI.init();
        SearchUI.init();
        PlaylistUI.init();
        DownloadUI.init();

        // Bind navigation
        this._bindNav();

        // Bind login
        this._bindLogin();

        // Check login state
        await this._checkLogin();

        // Show search page by default
        showPage("search");
    },

    _bindNav() {
        $$(".nav-item").forEach(item => {
            item.addEventListener("click", async () => {
                const page = item.dataset.page;

                if (page === "playlists") {
                    await PlaylistUI.loadUserPlaylists();
                } else if (page === "toplist") {
                    await PlaylistUI.loadToplist();
                } else if (page === "downloads") {
                    await DownloadUI.load();
                }

                showPage(page);
            });
        });
    },

    _bindLogin() {
        const modal = $("#login-modal");
        const btnLogin = $("#btn-login");
        const btnClose = $("#modal-close");

        btnLogin.addEventListener("click", () => {
            modal.classList.remove("hidden");
            this._startQRLogin();
        });

        btnClose.addEventListener("click", () => {
            modal.classList.add("hidden");
        });

        modal.addEventListener("click", (e) => {
            if (e.target === modal) modal.classList.add("hidden");
        });

        // Tab switching
        $$(".login-tabs .tab-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                $$(".login-tabs .tab-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                $$(".login-tab-content").forEach(t => t.classList.remove("active"));
                $(`#login-${btn.dataset.loginTab}-tab`).classList.add("active");

                if (btn.dataset.loginTab === "qr") {
                    this._startQRLogin();
                }
            });
        });

        // Phone login
        $("#btn-phone-login").addEventListener("click", async () => {
            const phone = $("#login-phone-input").value.trim();
            const password = $("#login-password-input").value;
            if (!phone || !password) {
                $("#login-phone-error").textContent = "请输入手机号和密码";
                return;
            }

            const result = await NeMusic.api.login_phone(phone, password);
            if (result.success) {
                this._onLoginSuccess(result);
            } else {
                $("#login-phone-error").textContent = result.message || "登录失败";
            }
        });
    },

    async _startQRLogin() {
        const container = $("#qr-container");
        container.innerHTML = "<p>加载二维码...</p>";

        const result = await NeMusic.api.login_qrcode();
        if (!result.success) {
            container.innerHTML = `<p>${result.message}</p>`;
            return;
        }

        container.innerHTML = `<img src="${result.qr_url}" alt="QR Code" style="width:200px;height:200px;">`;
        this._pollQRCode(result.unikey);
    },

    async _pollQRCode(unikey) {
        const check = async () => {
            const result = await NeMusic.api.check_qrcode(unikey);
            if (result.status === "success") {
                this._onLoginSuccess(result);
                return;
            } else if (result.status === "expired") {
                $("#qr-container").innerHTML = '<p>二维码已过期，<button onclick="App._startQRLogin()">重新获取</button></p>';
                return;
            } else if (result.status === "scanned") {
                $("#qr-container").innerHTML = '<p>已扫描，请在手机上确认登录...</p>';
            } else if (result.status === "error") {
                return;
            }

            // Continue polling
            if (result.status !== "success" && result.status !== "expired") {
                setTimeout(check, 2000);
            }
        };

        setTimeout(check, 2000);
    },

    _onLoginSuccess(user) {
        $("#login-modal").classList.add("hidden");
        showToast(`登录成功: ${user.nickname || ""}`);

        // Update sidebar
        const loginArea = $("#login-area");
        loginArea.innerHTML = `
            <div class="user-info">
                <img src="${user.avatar || ''}" alt="">
                <span class="user-name">${user.nickname || "用户"}</span>
                <button class="btn-logout" id="btn-logout">退出</button>
            </div>
        `;

        $("#btn-logout").addEventListener("click", async () => {
            await NeMusic.api.logout();
            this._onLogout();
        });

        // Reload playlists
        PlaylistUI.loadUserPlaylists();
    },

    _onLogout() {
        const loginArea = $("#login-area");
        loginArea.innerHTML = '<button class="btn-login" id="btn-login">🔑 登录</button>';
        $("#btn-login").addEventListener("click", () => this._bindLogin());
        showToast("已退出登录");
    },

    async _checkLogin() {
        const status = await NeMusic.api.get_login_status();
        if (status.logged_in) {
            this._onLoginSuccess(status);
        }
    },
};

// Boot
document.addEventListener("DOMContentLoaded", () => App.init());
```

- [ ] **Step 2: Commit**

---

### Task 18: Wire main.py with Full API

**Files:**
- Modify: `E:\NeMusic\main.py`

**Consumes:** `backend.api.NeMusicAPI`
**Produces:** Fully functional application entry point.

- [ ] **Step 1: Update main.py**

Replace the skeleton `NeMusicAPI` class with the real one:

```python
"""NeMusic - NetEase Cloud Music Desktop Player."""
import os
import sys
import webview

# Ensure backend is importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.api import NeMusicAPI


def on_closing():
    """Clean up resources when window is closed."""
    if hasattr(on_closing, "api") and on_closing.api:
        try:
            on_closing.api.cleanup()
        except Exception:
            pass


def main():
    api = NeMusicAPI()
    on_closing.api = api

    html_path = os.path.join(BASE_DIR, "frontend", "index.html")

    window = webview.create_window(
        title="NeMusic - 网易云音乐",
        url=html_path,
        js_api=api,
        width=1100,
        height=720,
        min_size=(800, 500),
    )
    api.set_window(window)

    # Register cleanup on close
    window.events.closing += on_closing

    webview.start(debug=False, http_server=True)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Launch and smoke test**

Run:
```powershell
cd E:\NeMusic
python main.py
```

Expected: Window opens with complete layout. Sidebar navigation works. Login modal opens. Search works (returns real results from NetEase API). Playlist and toplist pages load data.

- [ ] **Step 3: Test core flows**

Manual test checklist:
1. Open login modal → QR code loads
2. Enter phone/password login form works
3. Search for a song → results appear
4. Click a song → plays audio
5. Player bar updates with song info, progress moves
6. Lyrics button → lyrics view opens with cover background
7. Toggle play/pause, next/prev
8. Volume slider works
9. Click "我的歌单" → load playlists (if logged in)
10. Click "排行榜" → load toplist
11. Click "下载管理" → show downloads/cache
12. Download a song from search results

- [ ] **Step 4: Commit**

---

### Task 19: PyInstaller Build Script

**Files:**
- Modify: `E:\NeMusic\build.py`

**Produces:** `dist/NeMusic.exe`

- [ ] **Step 1: Update build.py with proper configuration**

```python
"""PyInstaller build script for NeMusic.

Run: python build.py
Output: dist/NeMusic.exe
"""
import PyInstaller.__main__
import os
import sys
import site
import shutil


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def find_vlc_lib():
    """Find the VLC library directory for bundling."""
    import vlc

    # Try to locate VLC installation
    vlc_paths = [
        r"C:\Program Files\VideoLAN\VLC",
        r"C:\Program Files (x86)\VideoLAN\VLC",
        os.path.join(BASE_DIR, "vlc"),
    ]

    # Check if python-vlc can tell us
    try:
        instance = vlc.Instance()
        # The instance might have info about the VLC path
    except Exception:
        pass

    for path in vlc_paths:
        if os.path.exists(path):
            return path
    return None


def clean():
    """Clean build artifacts."""
    for d in ["build", "dist", "__pycache__"]:
        p = os.path.join(BASE_DIR, d)
        if os.path.exists(p):
            shutil.rmtree(p)
    # Clean spec files
    for f in os.listdir(BASE_DIR):
        if f.endswith(".spec"):
            os.remove(os.path.join(BASE_DIR, f))


def build():
    frontend_dir = os.path.join(BASE_DIR, "frontend")
    icon_path = os.path.join(BASE_DIR, "icon.ico")

    args = [
        os.path.join(BASE_DIR, "main.py"),
        "--name=NeMusic",
        "--onefile",
        "--windowed",
        "--clean",
        f"--add-data={frontend_dir}{os.pathsep}frontend",
        "--hidden-import=vlc",
        "--hidden-import=pywebview",
        "--hidden-import=Crypto",
        "--hidden-import=requests",
    ]

    # Icon
    if os.path.exists(icon_path):
        args.append(f"--icon={icon_path}")

    # VLC DLL bundling
    vlc_path = find_vlc_lib()
    if vlc_path:
        vlc_plugins = os.path.join(vlc_path, "plugins")
        args.append(f"--add-binary={os.path.join(vlc_path, 'libvlc.dll')}{os.pathsep}.")
        args.append(f"--add-binary={os.path.join(vlc_path, 'libvlccore.dll')}{os.pathsep}.")
        if os.path.exists(vlc_plugins):
            args.append(f"--add-binary={vlc_plugins}{os.pathsep}plugins")

    print("Building NeMusic.exe...")
    PyInstaller.__main__.run(args)
    print("Build complete! Output: dist/NeMusic.exe")


if __name__ == "__main__":
    if "--clean" in sys.argv:
        clean()
    build()
```

- [ ] **Step 2: Run build**

Run:
```powershell
cd E:\NeMusic
python build.py
```

Expected: Build completes without fatal errors. `dist/NeMusic.exe` is created.

- [ ] **Step 3: Test the exe**

Run `dist/NeMusic.exe` and verify:
- Window opens
- Search works
- Audio plays (VLC libs bundled correctly)
- Login works

- [ ] **Step 4: Commit**

---

### Task 20: Final Testing & Polish

**Files:** (verify existing)
- Verify: `E:\NeMusic\dist\NeMusic.exe` exists and runs

**Goal:** Verify all features work end-to-end and fix any issues.

- [ ] **Step 1: Run full feature test**

Manual test against the spec checklist:

| Feature | Check |
|---------|-------|
| Window opens with correct title & size | [ ] |
| Sidebar navigation switches pages | [ ] |
| Player bar visible on all pages | [ ] |
| Search returns results | [ ] |
| Click song → plays audio | [ ] |
| Play/Pause toggle | [ ] |
| Next/Prev song | [ ] |
| Progress bar updates & draggable | [ ] |
| Volume slider works | [ ] |
| Lyrics view opens | [ ] |
| Lyrics scroll with playback | [ ] |
| Lyrics click to seek | [ ] |
| Cover blur background in lyrics | [ ] |
| QR code login renders | [ ] |
| Phone login works | [ ] |
| Logout works | [ ] |
| My playlists load | [ ] |
| Playlist detail shows songs | [ ] |
| Play all from playlist | [ ] |
| Toplist loads | [ ] |
| Toplist detail shows songs | [ ] |
| Download song | [ ] |
| Download/cache management page | [ ] |
| Delete cache/download | [ ] |
| Network error toast | [ ] |
| Exe runs standalone | [ ] |

- [ ] **Step 2: Fix any issues found**

Fix issues as they're discovered during testing.

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: NeMusic player — complete implementation"
```

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
                    raise CookieExpiredError(f"Cookie expired: {result}")

                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return result

            except requests.RequestException:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

        return {"code": -1, "message": "Request failed after retries"}

    # --- Search ---
    def search(self, keyword, limit=30, offset=0, search_type=1):
        return self._request("/cloudsearch/get/web", {
            "s": keyword,
            "type": search_type,
            "limit": str(limit),
            "offset": str(offset),
            "total": "true",
        })

    # --- Song ---
    def get_song_detail(self, song_ids):
        if isinstance(song_ids, int):
            song_ids = [song_ids]
        ids_str = ",".join(str(i) for i in song_ids)
        return self._request("/v3/song/detail", {
            "c": f'[{{"id":{ids_str}}}]',
            "ids": f"[{ids_str}]",
        })

    def get_song_url(self, song_ids, br=320000):
        if isinstance(song_ids, int):
            song_ids = [song_ids]
        ids_str = ",".join(str(i) for i in song_ids)
        return self._request("/song/enhance/player/url", {
            "ids": f"[{ids_str}]",
            "br": str(br),
        })

    def get_lyric(self, song_id):
        return self._request("/song/lyric", {
            "id": str(song_id),
            "lv": "-1",
            "tv": "-1",
        })

    # --- Login ---
    def login_cellphone(self, phone, password):
        return self._request("/login/cellphone", {
            "phone": phone,
            "password": password,
            "rememberLogin": "true",
        })

    def login_qr_key(self):
        import time
        return self._request(
            f"/login/qr/key?timestamp={int(time.time() * 1000)}",
            {"type": 1},
        )

    def login_qr_create(self, key):
        import time
        return self._request(
            f"/login/qr/create?timestamp={int(time.time() * 1000)}",
            {"key": key, "qrimg": True},
        )

    def login_qr_check(self, key):
        import time
        return self._request(
            f"/login/qr/client/login?timestamp={int(time.time() * 1000)}",
            {"key": key, "type": 1},
        )

    # --- User ---
    def get_user_playlists(self, uid, limit=100, offset=0):
        return self._request("/user/playlist", {
            "uid": str(uid),
            "limit": str(limit),
            "offset": str(offset),
        })

    def get_user_detail(self, uid):
        return self._request("/user/detail", {"uid": str(uid)})

    def refresh_login(self):
        return self._request("/login/refresh", {})

    # --- Playlist ---
    def get_playlist_detail(self, playlist_id):
        return self._request("/v6/playlist/detail", {
            "id": str(playlist_id),
            "n": "1000",
            "total": "true",
        })

    # --- Toplist ---
    def get_toplist(self):
        return self._request("/toplist", {})

    def get_toplist_detail(self):
        return self._request("/toplist/detail", {})

    def close(self):
        self._session.close()


class CookieExpiredError(Exception):
    """Raised when NetEase API returns a cookie-expired status."""
    pass

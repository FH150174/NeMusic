"""High-level API exposed to the JavaScript frontend via pywebview."""
import hashlib
import json
from backend.apiserver import APIServerManager
from backend.storage import Database
from backend.player import Player
from backend.download import DownloadManager
from backend.lyric import parse_lrc


class NeMusicAPI:
    """Complete API layer for the NeMusic frontend."""

    def __init__(self):
        self._window = None
        self._db = Database()
        self._server = APIServerManager()
        self._player = Player()
        self._download_mgr = None  # Created after server starts

        # Start the API server
        self._server.start()
        self._download_mgr = DownloadManager(self._server, self._db)

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
        self.next_song()

    def _on_error(self, code, message):
        self._emit("error", {"code": code, "message": message})

    # --- Login ---
    def login_phone(self, phone, password):
        """Login with phone number and md5 password."""
        md5_pw = hashlib.md5(password.encode()).hexdigest()
        try:
            result = self._server.request("/login/cellphone", {
                "phone": phone,
                "md5_password": md5_pw,
            })
            return self._handle_login_result(result)
        except Exception as e:
            return {"success": False, "message": str(e)}

    def login_qrcode(self):
        """Get QR code for login. Returns qr_image (data URI) and unikey."""
        try:
            # Step 1: Get unikey
            key_result = self._server.request("/login/qr/key")
            unikey = key_result.get("data", {}).get("unikey", "")
            if not unikey:
                return {"success": False, "message": "Failed to get QR key"}

            # Step 2: Create QR image
            qr_result = self._server.request("/login/qr/create", {
                "key": unikey,
                "qrimg": "true",
            })
            qr_data = qr_result.get("data", {})

            # Get QR as base64 data URI
            qr_img = qr_data.get("qrimg", "")
            qr_url = qr_data.get("qrurl", "")

            if qr_img:
                # Node.js server already returns data URI format
                if qr_img.startswith("data:image"):
                    qr_url = qr_img
                else:
                    qr_url = "data:image/png;base64," + qr_img

            if not qr_url:
                return {"success": False, "message": "Failed to generate QR code"}

            # Save QR code to a temp file as fallback for CSP-restricted WebView2
            qr_file_path = ""
            try:
                import base64, os
                # Extract base64 data from the data URI
                if qr_url.startswith("data:image/png;base64,"):
                    b64_data = qr_url[len("data:image/png;base64,"):]
                elif qr_url.startswith("data:image/"):
                    # Find the base64 part after the comma
                    comma_idx = qr_url.find(",")
                    if comma_idx > 0:
                        b64_data = qr_url[comma_idx + 1:]
                    else:
                        b64_data = ""
                else:
                    b64_data = qr_img if qr_img else ""

                if b64_data:
                    png_data = base64.b64decode(b64_data)
                    qr_dir = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "..", "data",
                    )
                    qr_dir = os.path.abspath(qr_dir)
                    os.makedirs(qr_dir, exist_ok=True)
                    qr_file_path = os.path.join(qr_dir, "qr_temp.png")
                    with open(qr_file_path, "wb") as f:
                        f.write(png_data)
                else:
                    qr_file_path = ""
            except Exception:
                qr_file_path = ""

            return {
                "success": True,
                "qr_image": qr_url,
                "qr_file": qr_file_path,
                "unikey": unikey,
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def check_qrcode(self, unikey):
        """Check QR code login status."""
        try:
            result = self._server.request("/login/qr/check", {"key": unikey})
            code = result.get("code")
            if code == 800:
                return {"status": "expired"}
            elif code == 801:
                return {"status": "waiting"}
            elif code == 802:
                return {"status": "scanned"}
            elif code == 803:
                cookie = result.get("cookie", "")
                self._server.cookie = _parse_cookie_string(cookie)
                profile = result.get("profile", {})
                uid = profile.get("userId", 0)
                nickname = profile.get("nickname", "")
                avatar = profile.get("avatarUrl", "")
                self._db.save_user(uid, nickname, avatar, cookie)
                return {
                    "status": "success",
                    "uid": uid,
                    "nickname": nickname,
                    "avatar": avatar,
                }
            else:
                return {"status": "unknown", "code": code}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_login_result(self, result):
        code = result.get("code")
        if code == 200:
            cookie = result.get("cookie", "")
            self._server.cookie = _parse_cookie_string(cookie)
            profile = result.get("profile", {})
            uid = profile.get("userId", 0)
            nickname = profile.get("nickname", "")
            avatar = profile.get("avatarUrl", "")
            self._db.save_user(uid, nickname, avatar, cookie)
            return {
                "success": True,
                "uid": uid,
                "nickname": nickname,
                "avatar": avatar,
            }
        elif code == 501:
            return {"success": False, "message": "账号不存在"}
        elif code == 502:
            return {"success": False, "message": "密码错误"}
        elif code == 503:
            return {"success": False, "message": "需要验证码，请使用二维码登录"}
        else:
            return {
                "success": False,
                "message": result.get("message", f"登录失败 (code={code})"),
            }

    def _restore_login(self):
        """Restore saved login state from database."""
        user = self._db.get_user()
        if user and user.get("cookie"):
            self._server.cookie = _parse_cookie_string(user["cookie"])

    def get_login_status(self):
        """Check if user is logged in."""
        user = self._db.get_user()
        if user:
            return {
                "logged_in": True,
                "uid": user["uid"],
                "nickname": user["nickname"],
                "avatar": user["avatar"],
            }
        return {"logged_in": False}

    def logout(self):
        self._db.clear_user()
        self._server.cookie = {}
        return {"success": True}

    # --- Search ---
    def search(self, keyword, limit=30, offset=0):
        """Search songs by keyword."""
        try:
            result = self._server.request("/cloudsearch", {
                "keywords": keyword,
                "limit": str(limit),
                "offset": str(offset),
                "type": "1",
            })
            songs = _extract_songs(result)
            total = result.get("result", {}).get("songCount", len(songs))
            return {"success": True, "songs": songs, "total": total}
        except Exception as e:
            return {"success": False, "message": str(e), "songs": [], "total": 0}

    # --- Play ---
    def play_song(self, song_info):
        """Play a song."""
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
            # Get streaming URL via API server
            url_result = self._server.request("/song/url/v1", {
                "id": str(song_id),
                "level": "standard",
            })
            songs = url_result.get("data", [])
            if not songs or not songs[0].get("url"):
                # Try lower quality
                url_result = self._server.request("/song/url/v1", {
                    "id": str(song_id),
                    "level": "standard",
                })
                songs = url_result.get("data", [])
                if not songs or not songs[0].get("url"):
                    return {"success": False, "message": "该歌曲暂无版权"}
            url = songs[0]["url"]

        # Add to queue
        current = self._player.get_current_song()
        if not current or current.get("id") != song_id:
            self._queue.append(song_info)
            self._queue_index = len(self._queue) - 1

        self._player.play(url, song_info)
        return {"success": True}

    def play_songs(self, songs, start_index=0):
        """Set play queue and start playing."""
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
            result = self._server.request("/lyric", {"id": str(song_id)})
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
                return {
                    "success": False,
                    "playlists": [],
                    "message": "Not logged in",
                }
            result = self._server.request("/user/playlist", {
                "uid": str(user["uid"]),
            })
            playlists = []
            for pl in result.get("playlist", []):
                playlists.append({
                    "id": pl.get("id"),
                    "name": pl.get("name", ""),
                    "cover": pl.get("coverImgUrl", ""),
                    "track_count": pl.get("trackCount", 0),
                    "creator": pl.get("creator", {}).get("nickname", ""),
                })
            return {"success": True, "playlists": playlists}
        except Exception as e:
            return {"success": False, "playlists": [], "message": str(e)}

    def get_playlist_detail(self, playlist_id):
        """Get all songs in a playlist."""
        try:
            result = self._server.request("/playlist/detail", {
                "id": str(playlist_id),
            })
            playlist = result.get("playlist", {})
            songs = []
            for track in playlist.get("tracks", []):
                songs.append(_track_to_song(track))
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
            result = self._server.request("/toplist/detail")
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
        """Get songs in a toplist."""
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
        """Get list of downloaded and cached songs."""
        try:
            downloads = self._download_mgr.get_download_list()
            caches = self._download_mgr.get_cache_list()
            return {"success": True, "downloads": downloads, "caches": caches}
        except Exception as e:
            return {
                "success": False,
                "downloads": [],
                "caches": [],
                "message": str(e),
            }

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
        self._server.stop()
        self._db.close()


# --- Helper Functions ---

def _parse_cookie_string(cookie_str):
    """Parse cookie string into dict."""
    cookies = {}
    if cookie_str:
        for item in cookie_str.split(";"):
            item = item.strip()
            if "=" in item:
                k, v = item.split("=", 1)
                cookies[k.strip()] = v.strip()
    return cookies


def _track_to_song(track):
    """Convert a track dict to a standard song dict."""
    return {
        "id": track.get("id"),
        "name": track.get("name", ""),
        "artists": ", ".join(
            a.get("name", "") for a in (track.get("ar") or [])
        ),
        "album": (track.get("al") or {}).get("name", ""),
        "cover": (track.get("al") or {}).get("picUrl", ""),
        "duration": track.get("dt", 0) // 1000,
    }


def _extract_songs(result):
    """Extract song list from search or playlist result."""
    songs = []
    raw_songs = (
        result.get("result", {}).get("songs", [])
        or result.get("playlist", {}).get("tracks", [])
        or result.get("songs", [])
    )
    for s in raw_songs:
        if "ar" in s or "artists" in s:
            songs.append(_track_to_song(s))
        elif "al" in s:
            songs.append({
                "id": s.get("id"),
                "name": s.get("name", ""),
                "artists": ", ".join(
                    a.get("name", "") for a in s.get("ar", [])
                ),
                "album": s.get("al", {}).get("name", ""),
                "cover": s.get("al", {}).get("picUrl", ""),
                "duration": s.get("dt", 0) // 1000,
            })
    return songs

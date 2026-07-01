"""Download and cache management for NeMusic."""
import os
import sys
import hashlib
import requests
from datetime import datetime, timedelta
from backend.storage import Database

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
DOWNLOADS_DIR = os.path.join(DATA_DIR, "downloads")


class DownloadManager:
    """Manage song downloads and play caching."""

    def __init__(self, api_server, db=None):
        self._server = api_server
        self._db = db or Database()
        os.makedirs(CACHE_DIR, exist_ok=True)
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    def _get_song_url(self, song_id, level="standard"):
        """Get playable song URL from API server."""
        result = self._server.request("/song/url/v1", {
            "id": str(song_id),
            "level": level,
        })
        songs = result.get("data", [])
        if songs and songs[0].get("url"):
            return songs[0]
        return None

    def download_song(self, song_id, title, artist, album, cover_url,
                      quality="320k"):
        """Download a song file for offline use."""
        existing = self._db.get_download(song_id)
        if existing and os.path.exists(existing["file_path"]):
            return {
                "success": True,
                "file_path": existing["file_path"],
                "message": "Already downloaded",
            }

        self._check_disk_space(100 * 1024 * 1024)

        # Try standard quality first, then lower
        levels = ["standard", "higher", "exhigh", "lossless"]
        song_data = None
        for level in levels:
            song_data = self._get_song_url(song_id, level)
            if song_data and song_data.get("url"):
                break

        if not song_data or not song_data.get("url"):
            return {
                "success": False,
                "file_path": None,
                "message": "No playable URL (song may be unavailable)",
            }

        url = song_data["url"]
        actual_br = song_data.get("br", 320000)
        ext = ".flac" if actual_br >= 999000 else ".mp3"

        safe_name = f"{song_id}_{self._safe_filename(title)}"
        file_path = os.path.join(DOWNLOADS_DIR, f"{safe_name}{ext}")

        try:
            self._download_file(url, file_path)
        except Exception as e:
            return {"success": False, "file_path": None, "message": str(e)}

        file_size = os.path.getsize(file_path)

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

        return {
            "success": True,
            "file_path": file_path,
            "message": "Download complete",
        }

    def cache_song(self, song_id, title, artist, album, cover_url, url):
        """Cache a played song to local storage."""
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
        return self._db.get_downloads()

    def get_cache_list(self):
        return self._db.get_all_cache()

    def delete_download(self, download_id):
        self._db.delete_download(download_id)

    def delete_cache(self, cache_id):
        self._db.delete_cache(cache_id)

    def export_song(self, song_id, target_path):
        """Copy a downloaded song to an external location."""
        downloaded = self._db.get_download(song_id)
        if not downloaded or not os.path.exists(downloaded["file_path"]):
            cached = self._db.get_cache_by_song_id(song_id)
            if cached and os.path.exists(cached["local_path"]):
                downloaded = cached
            else:
                return {
                    "success": False,
                    "message": "File not found in downloads or cache",
                }

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

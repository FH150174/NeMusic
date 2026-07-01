"""Manage NeteaseCloudMusicApi Node.js subprocess."""
import os
import sys
import time
import subprocess
import requests

# Handle PyInstaller bundle paths
import sys as _sys
if getattr(_sys, "frozen", False):
    BASE_DIR = _sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVER_PORT = 29999
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"


def _find_node():
    """Find the node executable."""
    import subprocess
    try:
        result = subprocess.run(
            ["where", "node"], capture_output=True, text=True
        )
        if result.returncode == 0:
            node_path = result.stdout.strip().split("\n")[0]
            if os.path.exists(node_path):
                return node_path
    except Exception:
        pass
    # Common paths
    paths = [
        r"C:\Program Files\nodejs\node.exe",
        r"D:\Node.js\node.exe",
        os.path.expandvars(r"%APPDATA%\nvm\current\node.exe"),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return "node"


class APIServerManager:
    """Start/stop the Node.js NeteaseCloudMusicApi server and proxy requests."""

    def __init__(self):
        self._process = None
        self._session = requests.Session()
        self._cookie_jar = {}

    def start(self):
        """Start the Node.js API server."""
        if self._process is not None:
            return True

        js_path = os.path.join(BASE_DIR, "api_server.js")
        node_exe = _find_node()

        try:
            self._process = subprocess.Popen(
                [node_exe, js_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=BASE_DIR,
                env={**os.environ, "NEMUSIC_API_PORT": str(SERVER_PORT)},
            )
        except FileNotFoundError:
            print("ERROR: Node.js not found. Please install Node.js.")
            return False

        # Wait for server to be ready (max 15 seconds)
        for _ in range(30):
            try:
                resp = self._session.get(
                    f"{SERVER_URL}/login/qr/key",
                    params={"timestamp": int(time.time() * 1000)},
                    timeout=3,
                )
                if resp.status_code == 200:
                    return True
            except requests.ConnectionError:
                pass
            time.sleep(0.5)

        return False

    def stop(self):
        """Stop the Node.js API server."""
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
            self._process = None

    @property
    def cookie(self):
        return self._cookie_jar

    @cookie.setter
    def cookie(self, cookie_dict):
        self._cookie_jar = cookie_dict or {}

    def request(self, endpoint, data=None):
        """
        Make a GET request to the local Node.js API server.
        The server handles all Netease crypto internally.
        """
        url = f"{SERVER_URL}{endpoint}"
        params = data or {}
        params["timestamp"] = int(time.time() * 1000)

        cookie_str = None
        if self._cookie_jar:
            cookie_str = "; ".join(
                f"{k}={v}" for k, v in self._cookie_jar.items()
            )

        headers = {}
        if cookie_str:
            headers["Cookie"] = cookie_str

        try:
            resp = self._session.get(
                url, params=params, headers=headers, timeout=30
            )
            return resp.json()
        except Exception as e:
            return {"code": -1, "message": str(e)}

    @property
    def is_running(self):
        return self._process is not None and self._process.poll() is None

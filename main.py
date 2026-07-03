"""NeMusic - NetEase Cloud Music Desktop Player."""
import os
import sys
import threading
import webview

# Handle PyInstaller bundle paths
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.api import NeMusicAPI

_app_api = None


def on_closing():
    """Save state and clean up resources when window is closed."""
    global _app_api
    if _app_api:
        try:
            _app_api.save_playback_state()
        except Exception:
            pass
        try:
            _app_api.cleanup()
        except Exception:
            pass


def _start_api_server(api):
    """Start the API server in background thread."""
    ok = api.start_backend()
    if not ok:
        api._emit("error", {"code": -1, "message": "API服务器启动失败，请检查Node.js是否安装"})


def main():
    global _app_api

    # Create API without starting backend (fast)
    api = NeMusicAPI()
    _app_api = api

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
    window.events.closing += on_closing

    # Start API server in background after window is shown
    threading.Thread(target=_start_api_server, args=(api,), daemon=True).start()

    webview.start(debug=False, http_server=True)


if __name__ == "__main__":
    main()

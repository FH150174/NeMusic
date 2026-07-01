"""NeMusic - NetEase Cloud Music Desktop Player."""
import os
import sys
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
    """Clean up resources when window is closed."""
    global _app_api
    if _app_api:
        try:
            _app_api.cleanup()
        except Exception:
            pass


def main():
    global _app_api
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
    webview.start(debug=False, http_server=True)


if __name__ == "__main__":
    main()

"""Minimal test to verify pywebview JS-Python bridge."""
import webview
import json
import os



class TestAPI:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def echo(self, msg):
        return f"Python收到: {msg}"

    def get_songs(self):
        return [
            {"id": 1, "name": "晴天", "artist": "周杰伦"},
            {"id": 2, "name": "夜曲", "artist": "周杰伦"},
        ]

    def get_qr(self):
        return {
            "success": True,
            "qr_image": "data:image/png;base64,FAKE_QR_DATA_FOR_TESTING",
            "unikey": "test-unikey-12345",
        }


def main():
    api = TestAPI()
    html = """
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><style>
        body { font-family: sans-serif; padding: 20px; background: #1a1a2e; color: #eee; }
        button { padding: 8px 16px; margin: 5px; cursor: pointer; }
        .result { margin: 10px 0; padding: 10px; background: #333; border-radius: 5px; }
        .error { color: #ff5a5a; }
        .ok { color: #5aff5a; }
    </style></head><body>
        <h2>PyWebview Bridge Test</h2>
        <button onclick="testEcho()">1. Test Echo (text)</button>
        <button onclick="testSongs()">2. Test Get Songs (dict/list)</button>
        <button onclick="testQR()">3. Test Get QR (nested dict)</button>
        <div id="output"></div>

        <script>
        function log(msg, cls) {
            var div = document.createElement('div');
            div.className = 'result ' + (cls || '');
            div.textContent = msg;
            document.getElementById('output').appendChild(div);
        }

        async function testEcho() {
            try {
                var api = window.pywebview ? window.pywebview.api : null;
                if (!api) { log('ERROR: window.pywebview.api is null/undefined', 'error'); return; }
                log('API object: ' + JSON.stringify(Object.keys(api)));
                var result = await api.echo('Hello Bridge Test!');
                log('ECHO RESULT: ' + JSON.stringify(result), 'ok');
            } catch(e) {
                log('ECHO ERROR: ' + e.message, 'error');
            }
        }

        async function testSongs() {
            try {
                var result = await window.pywebview.api.get_songs();
                log('SONGS RESULT: ' + JSON.stringify(result), 'ok');
            } catch(e) {
                log('SONGS ERROR: ' + e.message, 'error');
            }
        }

        async function testQR() {
            try {
                var result = await window.pywebview.api.get_qr();
                log('QR RESULT keys: ' + JSON.stringify(Object.keys(result)), 'ok');
                log('QR success: ' + result.success + ', unikey: ' + result.unikey, 'ok');
            } catch(e) {
                log('QR ERROR: ' + e.message, 'error');
            }
        }
        </script>
    </body></html>
    """

    window = webview.create_window(
        title="Bridge Test",
        html=html,
        js_api=api,
        width=600,
        height=500,
    )
    api.set_window(window)
    webview.start(debug=True)


if __name__ == "__main__":
    main()

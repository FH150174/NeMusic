/* === Python-JS Bridge === */

window.NeMusic = window.NeMusic || {};
var NeMusic = window.NeMusic;

// Event registry
NeMusic._listeners = {};

/**
 * Register an event listener.
 * @param {string} event
 * @param {function} callback
 */
NeMusic.on = function (event, callback) {
    if (!NeMusic._listeners[event]) {
        NeMusic._listeners[event] = [];
    }
    NeMusic._listeners[event].push(callback);
};

/**
 * Receive and dispatch events from Python.
 * Called by Python via: window.evaluate_js('NeMusic.emit(...)')
 * @param {object} payload — {event: string, data: object}
 */
NeMusic.emit = function (payload) {
    var listeners = NeMusic._listeners[payload.event] || [];
    listeners.forEach(function (fn) {
        try { fn(payload.data); } catch (e) { console.error(e); }
    });
};

/**
 * Reference to the Python API object.
 * pywebview exposes methods of the Python js_api object sync-style.
 */
NeMusic.api = window.pywebview ? window.pywebview.api : null;

if (!NeMusic.api) {
    console.warn("pywebview API not available — running in browser mode");
    // Mock API for browser development
    NeMusic.api = new Proxy({}, {
        get: function (target, prop) {
            return function () {
                var args = Array.prototype.slice.call(arguments);
                console.log("[Mock API] " + prop, args);
                return { success: false, message: "Running in browser (no Python backend)" };
            };
        }
    });
}

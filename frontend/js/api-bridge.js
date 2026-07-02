/* === Python-JS Bridge === */
/* pywebview injects window.pywebview AFTER page scripts load.
   So we use a lazy proxy that checks for the real API on every call. */

window.NeMusic = window.NeMusic || {};
var NeMusic = window.NeMusic;

// Event registry — Python calls NeMusic.emit(payload)
NeMusic._listeners = {};

NeMusic.on = function (event, callback) {
    if (!NeMusic._listeners[event]) {
        NeMusic._listeners[event] = [];
    }
    NeMusic._listeners[event].push(callback);
};

NeMusic.emit = function (payload) {
    var listeners = NeMusic._listeners[payload.event] || [];
    listeners.forEach(function (fn) {
        try { fn(payload.data); } catch (e) { console.error(e); }
    });
};

/**
 * Lazy API proxy.
 * On every call, checks if the real pywebview API is available.
 * If yes, calls it; if no, returns an error.
 * This handles the timing issue where pywebview injects its API after page load.
 */
NeMusic.api = createLazyAPI();

function createLazyAPI() {
    return new Proxy({}, {
        get: function (target, prop) {
            // Ignore special properties
            if (typeof prop === "symbol" || prop === "then" || prop === "toJSON" || prop === "inspect") {
                return undefined;
            }
            // Return a function that delegates to the real API
            return function () {
                var args = arguments;
                var api = getRealAPI();
                if (!api) {
                    console.warn("[NeMusic] Real API not available yet for: " + prop);
                    return { success: false, message: "API initializing, please retry" };
                }
                if (typeof api[prop] !== "function") {
                    console.warn("[NeMusic] API method not found: " + prop);
                    return { success: false, message: "Method not found: " + prop };
                }
                try {
                    return api[prop].apply(api, args);
                } catch (e) {
                    console.error("[NeMusic] API call " + prop + " error:", e.message);
                    return { success: false, message: e.message };
                }
            };
        }
    });
}

function getRealAPI() {
    if (typeof window.pywebview !== "undefined" && window.pywebview && window.pywebview.api) {
        return window.pywebview.api;
    }
    return null;
}

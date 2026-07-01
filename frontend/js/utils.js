/* === Utility Functions === */

/** Shortcut for querySelector */
const $ = (sel, parent) => (parent || document).querySelector(sel);

/** Shortcut for querySelectorAll (returns array) */
const $$ = (sel, parent) => [...(parent || document).querySelectorAll(sel)];

/** Format seconds to m:ss */
function formatTime(seconds) {
    if (!seconds || seconds <= 0) return "0:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
}

/** Format large numbers with Chinese units */
function formatCount(n) {
    if (n >= 100000000) return (n / 100000000).toFixed(1) + "亿";
    if (n >= 10000) return (n / 10000).toFixed(1) + "万";
    return String(n);
}

/** Show a toast message */
function showToast(message, type) {
    type = type || "";
    const container = $("#toast-container");
    const toast = document.createElement("div");
    toast.className = "toast " + type;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(function () { toast.remove(); }, 3000);
}

/** Format file size for display */
function formatFileSize(bytes) {
    if (!bytes) return "";
    var kb = bytes / 1024;
    if (kb < 1024) return kb.toFixed(1) + " KB";
    return (kb / 1024).toFixed(1) + " MB";
}

/** Switch visible page */
function showPage(pageName) {
    $$(".page").forEach(function (p) { p.classList.remove("active"); });
    var page = $("#page-" + pageName);
    if (page) page.classList.add("active");

    $$(".nav-item").forEach(function (i) { i.classList.remove("active"); });
    var navItem = document.querySelector('.nav-item[data-page="' + pageName + '"]');
    if (navItem) navItem.classList.add("active");
}

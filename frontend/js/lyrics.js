/* === Lyrics Frontend Logic === */

var LyricsUI = {
    elements: {},
    lines: [],
    currentIndex: -1,
    isVisible: false,
    _previousPage: "search",

    init: function () {
        this.elements.overlay = $("#page-lyrics");
        this.elements.bg = $("#lyrics-bg");
        this.elements.cover = $("#lyrics-cover");
        this.elements.title = $("#lyrics-title");
        this.elements.artist = $("#lyrics-artist");
        this.elements.scroll = $("#lyrics-scroll");
        this.elements.btnClose = $("#btn-close-lyrics");

        var self = this;
        this.elements.btnClose.addEventListener("click", function () {
            self.hide();
        });
    },

    load: async function (songId) {
        this.reset();
        var result = await NeMusic.api.get_lyric(songId);
        this.lines = result.lines || [];

        if (!this.lines.length) {
            this.elements.scroll.innerHTML =
                '<p class="lyrics-empty">' + (result.message || "暂无歌词") + "</p>";
        } else {
            var html = "";
            for (var i = 0; i < this.lines.length; i++) {
                html +=
                    '<p class="lyrics-line" data-index="' +
                    i +
                    '" data-time="' +
                    this.lines[i].time +
                    '">' +
                    this.lines[i].text +
                    "</p>";
            }
            this.elements.scroll.innerHTML = html;

            var self = this;
            this.elements.scroll.querySelectorAll(".lyrics-line").forEach(function (el) {
                el.addEventListener("click", function () {
                    var time = parseFloat(this.dataset.time);
                    NeMusic.api.seek(time);
                });
            });
        }
    },

    updatePosition: function (currentSec) {
        if (!this.lines.length) return;

        var activeIdx = -1;
        for (var i = 0; i < this.lines.length; i++) {
            if (this.lines[i].time <= currentSec) {
                activeIdx = i;
            } else {
                break;
            }
        }

        if (activeIdx !== this.currentIndex) {
            this.currentIndex = activeIdx;
            this._highlightLine(activeIdx);
        }
    },

    _highlightLine: function (index) {
        var lines = this.elements.scroll.querySelectorAll(".lyrics-line");
        lines.forEach(function (l) { l.classList.remove("active"); });

        if (index >= 0 && index < lines.length) {
            var el = lines[index];
            el.classList.add("active");
            var containerH = this.elements.scroll.clientHeight;
            this.elements.scroll.scrollTop =
                el.offsetTop - containerH / 2 + el.clientHeight / 2;
        }
    },

    show: async function () {
        // Save current page for restore
        var activePage = document.querySelector(".page.active:not(.lyrics-overlay)");
        if (activePage) {
            this._previousPage = activePage.id.replace("page-", "");
        }

        // Get current song info
        var song = {};
        try {
            song = NeMusic.api.get_current_song();
        } catch (e) {}

        if (song && song.id) {
            this.elements.cover.src = song.cover || "";
            this.elements.title.textContent = song.name || "";
            this.elements.artist.textContent = song.artists || "";
            this.elements.bg.style.backgroundImage =
                "url(" + (song.cover || "") + ")";
            await this.load(song.id);
        }

        this.elements.overlay.classList.add("active");
        this.isVisible = true;
    },

    hide: function () {
        this.elements.overlay.classList.remove("active");
        this.isVisible = false;
        showPage(this._previousPage);
    },

    toggle: function () {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    },

    reset: function () {
        this.lines = [];
        this.currentIndex = -1;
        this.elements.scroll.innerHTML =
            '<p class="lyrics-empty">暂无歌词</p>';
    },
};

/* === Lyrics Page Logic === */

var LyricsUI = {
    elements: {},
    lines: [],
    currentIndex: -1,
    currentSongId: 0,

    init: function () {
        this.elements.cover = $("#lyrics-cover");
        this.elements.title = $("#lyrics-title");
        this.elements.artist = $("#lyrics-artist");
        this.elements.scroll = $("#lyrics-scroll");
        this.elements.empty = $("#lyrics-empty");
    },

    /** Load lyrics for a song and cache them */
    load: async function (songId) {
        if (!songId || songId === this.currentSongId) return;
        this.currentSongId = songId;

        this.reset();

        // Get song info from Python
        var song = {};
        try { song = NeMusic.api.get_current_song(); } catch (e) {}

        this.elements.cover.src = song.cover || "";
        this.elements.title.textContent = song.name || "";
        this.elements.artist.textContent = song.artists || "";

        var result = await NeMusic.api.get_lyric(songId);
        this.lines = result.lines || [];

        if (!this.lines.length) {
            this.elements.empty.style.display = "block";
            this.elements.empty.textContent = result.message || "暂无歌词";
            this.elements.scroll.innerHTML = "";
        } else {
            this.elements.empty.style.display = "none";
            var html = "";
            for (var i = 0; i < this.lines.length; i++) {
                html +=
                    '<p class="lyrics-line" data-index="' + i +
                    '" data-time="' + this.lines[i].time + '">' +
                    this.lines[i].text + "</p>";
            }
            this.elements.scroll.innerHTML = html;

            // Click to seek
            var self = this;
            this.elements.scroll.querySelectorAll(".lyrics-line").forEach(function (el) {
                el.addEventListener("click", function () {
                    var time = parseFloat(this.dataset.time);
                    NeMusic.api.seek(time);
                });
            });
        }
    },

    /** Update highlighted line based on playback position */
    updatePosition: function (currentSec) {
        if (!this.lines.length) return;

        var activeIdx = -1;
        for (var i = 0; i < this.lines.length; i++) {
            if (this.lines[i].time <= currentSec) {
                activeIdx = i;
            } else break;
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

    /** Called when navigating to lyrics page */
    show: function () {
        // Get current song and load lyrics
        try {
            var song = NeMusic.api.get_current_song();
            if (song && song.id) {
                this.elements.cover.src = song.cover || "";
                this.elements.title.textContent = song.name || "未在播放";
                this.elements.artist.textContent = song.artists || "";
                this.load(song.id);
            }
        } catch (e) {}
        showPage("lyrics");
    },

    reset: function () {
        this.lines = [];
        this.currentIndex = -1;
        this.elements.scroll.innerHTML = "";
        this.elements.empty.style.display = "block";
        this.elements.empty.textContent = "暂无歌词";
    },
};

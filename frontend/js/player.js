/* === Player Frontend Logic === */

var PlayerUI = {
    elements: {},
    _progressDragging: false,

    init: function () {
        this.elements.cover = $("#player-cover");
        this.elements.title = $("#player-title");
        this.elements.artist = $("#player-artist");
        this.elements.btnPlay = $("#btn-play");
        this.elements.btnPrev = $("#btn-prev");
        this.elements.btnNext = $("#btn-next");
        this.elements.btnLyrics = $("#btn-lyrics");
        this.elements.progressBar = $("#progress-bar");
        this.elements.progressCurrent = $("#progress-current");
        this.elements.progressTotal = $("#progress-total");
        this.elements.volumeBar = $("#volume-bar");
        this.elements.songInfoArea = $("#player-song-info-area");

        this._bindEvents();
        this._bindNeMusicEvents();
        this._loadVolume();
    },

    _bindEvents: function () {
        var self = this;

        this.elements.btnPlay.addEventListener("click", function () {
            NeMusic.api.toggle_play_pause();
        });

        this.elements.btnPrev.addEventListener("click", function () {
            NeMusic.api.prev_song();
        });

        this.elements.btnNext.addEventListener("click", function () {
            NeMusic.api.next_song();
        });

        // Lyrics button or clicking song info area → go to lyrics page
        this.elements.btnLyrics.addEventListener("click", function () {
            LyricsUI.show();
        });
        var goLyrics = function () { LyricsUI.show(); };
        this.elements.songInfoArea.addEventListener("click", goLyrics);
        this.elements.cover.addEventListener("click", goLyrics);

        // Progress bar drag
        this.elements.progressBar.addEventListener("mousedown", function () {
            self._progressDragging = true;
        });
        document.addEventListener("mouseup", function () {
            if (self._progressDragging) {
                self._progressDragging = false;
                var pct = parseInt(self.elements.progressBar.value);
                var total = parseFloat(self.elements.progressTotal.dataset.total || 0);
                if (total > 0) {
                    NeMusic.api.seek((pct / 100) * total);
                }
            }
        });

        // Volume
        this.elements.volumeBar.value = 70;
        this.elements.volumeBar.addEventListener("input", function () {
            var vol = parseInt(self.elements.volumeBar.value);
            NeMusic.api.set_volume(vol);
            localStorage.setItem("nemusic_volume", vol);
        });
    },

    _loadVolume: function () {
        var saved = localStorage.getItem("nemusic_volume");
        if (saved !== null) {
            var vol = parseInt(saved);
            this.elements.volumeBar.value = vol;
            NeMusic.api.set_volume(vol);
        }
    },

    _bindNeMusicEvents: function () {
        var self = this;

        NeMusic.on("position_change", function (data) {
            self.elements.progressCurrent.textContent = formatTime(data.current);
            self.elements.progressTotal.textContent = formatTime(data.total);
            self.elements.progressTotal.dataset.total = data.total;
            if (!self._progressDragging) {
                self.elements.progressBar.value = data.percentage;
            }
            LyricsUI.updatePosition(data.current);
        });

        NeMusic.on("state_change", function (data) {
            if (data.state === "playing") {
                self.elements.btnPlay.textContent = "⏸";
            } else {
                self.elements.btnPlay.textContent = "▶️";
            }
        });

        NeMusic.on("song_end", function () {
            // Auto-next handled by Python
        });

        NeMusic.on("error", function (data) {
            showToast(data.message || "播放出错", "error");
        });
    },

    /** Update bottom bar now-playing display */
    updateNowPlaying: function (song) {
        this.elements.cover.src = song.cover || "";
        this.elements.title.textContent = song.name || "未播放";
        this.elements.artist.textContent = song.artists || "";
    },
};

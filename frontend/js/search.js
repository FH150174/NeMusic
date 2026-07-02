/* === Search Page Logic === */

var SearchUI = {
    init: function () {
        var self = this;

        $("#search-btn").addEventListener("click", function () {
            self.doSearch();
        });

        $("#search-input").addEventListener("keydown", function (e) {
            if (e.key === "Enter") self.doSearch();
        });
    },

    doSearch: async function () {
        var keyword = $("#search-input").value.trim();
        if (!keyword) return;

        showToast("搜索: " + keyword);
        var result = await NeMusic.api.search(keyword, 50, 0);

        var container = $("#search-results");
        if (!result.success || !result.songs.length) {
            container.innerHTML = '<p class="empty-hint">未找到相关歌曲</p>';
            return;
        }

        var self = this;
        var html = "";
        for (var i = 0; i < result.songs.length; i++) {
            var song = result.songs[i];
            var songJson = JSON.stringify(song).replace(/'/g, "&#39;");
            html +=
                '<div class="song-item" data-song=\'' + songJson + "'>" +
                '<span class="song-index">' + (i + 1) + "</span>" +
                '<img class="song-cover" src="' + (song.cover || "") +
                '" alt="" onerror="this.style.display=\'none\'">' +
                '<div class="song-info">' +
                '<div class="song-name">' + song.name + "</div>" +
                '<div class="song-artist">' + song.artists + "</div>" +
                "</div>" +
                '<span class="song-duration">' + formatTime(song.duration) + "</span>" +
                '<button class="btn-song-action download-btn" data-songid="' + song.id +
                '" title="下载">⬇</button>' +
                "</div>";
        }
        container.innerHTML = html;

        // Pre-fetch first 5 song URLs for instant play
        var first5 = result.songs.slice(0, 5).map(function (s) { return s.id; });
        NeMusic.api.prefetch_urls(first5);

        // Click to play
        container.querySelectorAll(".song-item").forEach(function (item) {
            item.addEventListener("click", function (e) {
                if (e.target.closest(".download-btn")) return;
                var song = JSON.parse(item.dataset.song);
                self.playSong(song);
            });
        });

        // Download buttons
        container.querySelectorAll(".download-btn").forEach(function (btn) {
            btn.addEventListener("click", async function (e) {
                e.stopPropagation();
                var item = btn.closest(".song-item");
                var song = JSON.parse(item.dataset.song);
                var result = await NeMusic.api.download_song(
                    song.id, song.name, song.artists, song.album, song.cover, "320k"
                );
                showToast(
                    result.message || (result.success ? "下载成功" : "下载失败"),
                    result.success ? "" : "error"
                );
            });
        });
    },

    playSong: async function (song) {
        // Update UI immediately for instant feedback
        PlayerUI.updateNowPlaying(song);
        var result = await NeMusic.api.play_song(song);
        if (result.success) {
            // Auto-load lyrics in background
            LyricsUI.load(song.id);
        } else {
            showToast(result.message || "播放失败", "error");
        }
    },
};

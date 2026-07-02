/* === Playlist & Toplist Page Logic === */

var PlaylistUI = {
    init: function () {
        var self = this;

        $("#btn-back-playlist").addEventListener("click", function () {
            showPage("playlists");
        });
        $("#btn-back-toplist").addEventListener("click", function () {
            showPage("toplist");
        });

        $("#btn-play-all-playlist").addEventListener("click", function () {
            self._playAllFrom("playlist-detail-songs");
        });
        $("#btn-play-all-toplist").addEventListener("click", function () {
            self._playAllFrom("toplist-detail-songs");
        });
    },

    loadUserPlaylists: async function () {
        var result = await NeMusic.api.get_user_playlists();
        var container = $("#playlist-list");

        if (!result.success || !result.playlists.length) {
            container.innerHTML =
                '<p class="empty-hint">' +
                (result.message || "请先登录查看歌单") +
                "</p>";
            return;
        }

        var html = "";
        for (var i = 0; i < result.playlists.length; i++) {
            var pl = result.playlists[i];
            html +=
                '<div class="card" data-plid="' + pl.id + '">' +
                '<img src="' + (pl.cover || "") + '" alt="' + pl.name +
                '" onerror="this.src=\'\'">' +
                '<div class="card-body">' +
                "<h4>" + pl.name + "</h4>" +
                "<p>" + pl.track_count + " 首 · " + pl.creator + "</p>" +
                "</div>" +
                "</div>";
        }
        container.innerHTML = html;

        var self = this;
        container.querySelectorAll(".card").forEach(function (card) {
            card.addEventListener("click", function () {
                self.showPlaylistDetail(parseInt(card.dataset.plid));
            });
        });
    },

    loadToplist: async function () {
        var result = await NeMusic.api.get_toplist();
        var container = $("#toplist-list");

        if (!result.success || !result.lists.length) {
            container.innerHTML =
                '<p class="empty-hint">加载排行榜失败</p>';
            return;
        }

        var html = "";
        for (var i = 0; i < result.lists.length; i++) {
            var tl = result.lists[i];
            html +=
                '<div class="card" data-tlid="' + tl.id + '">' +
                '<img src="' + (tl.cover || "") + '" alt="' + tl.name +
                '" onerror="this.src=\'\'">' +
                '<div class="card-body">' +
                "<h4>" + tl.name + "</h4>" +
                "<p>" + (tl.update_frequency || "") + "</p>" +
                "</div>" +
                "</div>";
        }
        container.innerHTML = html;

        var self = this;
        container.querySelectorAll(".card").forEach(function (card) {
            card.addEventListener("click", function () {
                self.showToplistDetail(parseInt(card.dataset.tlid));
            });
        });
    },

    showPlaylistDetail: async function (plId) {
        var result = await NeMusic.api.get_playlist_detail(plId);
        if (!result.success) {
            showToast(result.message, "error");
            return;
        }

        var pl = result.playlist;
        $("#playlist-detail-cover").src = pl.cover || "";
        $("#playlist-detail-name").textContent = pl.name;
        $("#playlist-detail-meta").textContent = pl.track_count + " 首";

        this._renderSongList("playlist-detail-songs", result.songs);
        NeMusic.api.prefetch_urls(result.songs.map(function (s) { return s.id; }));
        showPage("playlist-detail");
    },

    showToplistDetail: async function (tlId) {
        var result = await NeMusic.api.get_toplist_detail(tlId);
        if (!result.success) {
            showToast(result.message, "error");
            return;
        }

        var pl = result.playlist;
        $("#toplist-detail-cover").src = pl.cover || "";
        $("#toplist-detail-name").textContent = pl.name;

        this._renderSongList("toplist-detail-songs", result.songs);
        NeMusic.api.prefetch_urls(result.songs.map(function (s) { return s.id; }));
        showPage("toplist-detail");
    },

    _renderSongList: function (containerId, songs) {
        var container = $("#" + containerId);
        var html = "";
        for (var i = 0; i < songs.length; i++) {
            var song = songs[i];
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

        var self = this;
        // Single click = select, double-click = play
        container.querySelectorAll(".song-item").forEach(function (item, songIndex) {
            item.addEventListener("click", function (e) {
                if (e.target.closest(".download-btn")) return;
                container.querySelectorAll(".song-item").forEach(function (i) { i.classList.remove("selected"); });
                item.classList.add("selected");
            });
            item.addEventListener("dblclick", async function (e) {
                if (e.target.closest(".download-btn")) return;
                var song = JSON.parse(item.dataset.song);
                PlayerUI.updateNowPlaying(song);
                NeMusic.api.play_songs(songs, songIndex);
                LyricsUI.load(song.id);
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

    _playAllFrom: async function (containerId) {
        var items = $$("#" + containerId + " .song-item");
        if (!items.length) return;
        var songs = items.map(function (item) {
            return JSON.parse(item.dataset.song);
        });
        PlayerUI.updateNowPlaying(songs[0]);
        NeMusic.api.play_songs(songs, 0);
        LyricsUI.load(songs[0].id);
    },
};

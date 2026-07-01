/* === Download Management Page Logic === */

var DownloadUI = {
    init: function () {
        var self = this;

        $$(".download-tabs .tab-btn").forEach(function (btn) {
            btn.addEventListener("click", function () {
                $$(".download-tabs .tab-btn").forEach(function (b) {
                    b.classList.remove("active");
                });
                btn.classList.add("active");

                $$("#page-downloads .tab-content").forEach(function (t) {
                    t.classList.remove("active");
                });
                $("#" + btn.dataset.tab).classList.add("active");
            });
        });
    },

    load: async function () {
        var result = await NeMusic.api.get_downloads();
        if (!result.success) return;

        this._renderDownloadList(result.downloads || []);
        this._renderCacheList(result.caches || []);
    },

    _renderDownloadList: function (downloads) {
        var container = $("#download-list");
        var emptyHint = $("#download-empty");

        if (!downloads.length) {
            container.innerHTML = "";
            emptyHint.style.display = "block";
            return;
        }

        emptyHint.style.display = "none";
        var html = "";
        for (var i = 0; i < downloads.length; i++) {
            var d = downloads[i];
            html +=
                '<div class="song-item" data-songid="' + d.song_id +
                '" data-dlid="' + d.id + '" data-path="' + (d.file_path || "") + '">' +
                '<img class="song-cover" src="' + (d.cover_url || "") +
                '" alt="" onerror="this.style.display=\'none\'">' +
                '<div class="song-info">' +
                '<div class="song-name">' + d.title + "</div>" +
                '<div class="song-artist">' + d.artist + " · " +
                (d.quality || "") + " · " + formatFileSize(d.file_size) + "</div>" +
                "</div>" +
                '<span class="song-duration">' +
                (d.downloaded ? new Date(d.downloaded).toLocaleDateString() : "") +
                "</span>" +
                '<button class="btn-song-action play-local" title="播放">▶</button>' +
                '<button class="btn-song-action delete-dl" title="删除">🗑</button>' +
                "</div>";
        }
        container.innerHTML = html;

        this._bindDownloadActions(container);
    },

    _renderCacheList: function (caches) {
        var container = $("#cache-list");
        var emptyHint = $("#cache-empty");

        if (!caches.length) {
            container.innerHTML = "";
            emptyHint.style.display = "block";
            return;
        }

        emptyHint.style.display = "none";
        var html = "";
        for (var i = 0; i < caches.length; i++) {
            var c = caches[i];
            html +=
                '<div class="song-item" data-cacheid="' + c.id +
                '" data-path="' + (c.local_path || "") + '" data-songid="' +
                (c.song_id || 0) + '">' +
                '<img class="song-cover" src="' + (c.cover_url || "") +
                '" alt="" onerror="this.style.display=\'none\'">' +
                '<div class="song-info">' +
                '<div class="song-name">' + c.title + "</div>" +
                '<div class="song-artist">' + c.artist + " · 缓存 · " +
                formatFileSize(c.size_bytes) + "</div>" +
                "</div>" +
                '<span class="song-duration">' +
                (c.created_at ? new Date(c.created_at).toLocaleDateString() : "") +
                "</span>" +
                '<button class="btn-song-action play-local" title="播放">▶</button>' +
                '<button class="btn-song-action delete-cache" title="删除">🗑</button>' +
                "</div>";
        }
        container.innerHTML = html;

        this._bindCacheActions(container);
    },

    _bindDownloadActions: function (container) {
        var self = this;

        container.querySelectorAll(".play-local").forEach(function (btn) {
            btn.addEventListener("click", function (e) {
                e.stopPropagation();
                var item = btn.closest(".song-item");
                var song = {
                    id: parseInt(item.dataset.songid),
                    name: item.querySelector(".song-name").textContent,
                    artists: item.querySelector(".song-artist")
                        .textContent.split("·")[0].trim(),
                    cover: item.querySelector(".song-cover").src,
                };
                NeMusic.api.play_song(song);
                PlayerUI.updateNowPlaying(song);
            });
        });

        container.querySelectorAll(".delete-dl").forEach(function (btn) {
            btn.addEventListener("click", async function (e) {
                e.stopPropagation();
                var item = btn.closest(".song-item");
                var dlId = parseInt(item.dataset.dlid);
                if (dlId) {
                    await NeMusic.api.delete_download(dlId);
                    showToast("已删除");
                    self.load();
                }
            });
        });
    },

    _bindCacheActions: function (container) {
        var self = this;

        container.querySelectorAll(".play-local").forEach(function (btn) {
            btn.addEventListener("click", function (e) {
                e.stopPropagation();
                var item = btn.closest(".song-item");
                var song = {
                    id: parseInt(item.dataset.songid),
                    name: item.querySelector(".song-name").textContent,
                    artists: item.querySelector(".song-artist")
                        .textContent.split("·")[0].trim(),
                    cover: item.querySelector(".song-cover").src,
                };
                NeMusic.api.play_song(song);
                PlayerUI.updateNowPlaying(song);
            });
        });

        container.querySelectorAll(".delete-cache").forEach(function (btn) {
            btn.addEventListener("click", async function (e) {
                e.stopPropagation();
                var item = btn.closest(".song-item");
                var cacheId = parseInt(item.dataset.cacheid);
                await NeMusic.api.delete_cache(cacheId);
                showToast("缓存已删除");
                self.load();
            });
        });
    },
};

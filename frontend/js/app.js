/* === App Initialization & Router === */

var App = {
    _qrInterval: null,

    init: async function () {
        PlayerUI.init();
        LyricsUI.init();
        SearchUI.init();
        PlaylistUI.init();
        DownloadUI.init();

        this._bindNav();
        this._bindLogin();
        await this._checkLogin();
        showPage("search");
    },

    _bindNav: function () {
        $$(".nav-item").forEach(function (item) {
            item.addEventListener("click", async function () {
                var page = item.dataset.page;

                if (page === "playlists") {
                    await PlaylistUI.loadUserPlaylists();
                } else if (page === "toplist") {
                    await PlaylistUI.loadToplist();
                } else if (page === "downloads") {
                    await DownloadUI.load();
                }

                showPage(page);
            });
        });
    },

    _bindLogin: function () {
        var self = this;
        var modal = $("#login-modal");
        var btnLogin = $("#btn-login");
        var btnClose = $("#modal-close");

        btnLogin.addEventListener("click", function () {
            modal.classList.remove("hidden");
            self._startQRLogin();
        });

        btnClose.addEventListener("click", function () {
            modal.classList.add("hidden");
            if (self._qrInterval) {
                clearTimeout(self._qrInterval);
                self._qrInterval = null;
            }
        });

        modal.addEventListener("click", function (e) {
            if (e.target === modal) {
                modal.classList.add("hidden");
                if (self._qrInterval) {
                    clearTimeout(self._qrInterval);
                    self._qrInterval = null;
                }
            }
        });

        // Login tab switching
        $$(".login-tabs .tab-btn").forEach(function (btn) {
            btn.addEventListener("click", function () {
                $$(".login-tabs .tab-btn").forEach(function (b) {
                    b.classList.remove("active");
                });
                btn.classList.add("active");

                $$(".login-tab-content").forEach(function (t) {
                    t.classList.remove("active");
                });
                $("#login-" + btn.dataset.loginTab + "-tab").classList.add("active");

                if (btn.dataset.loginTab === "qr") {
                    self._startQRLogin();
                }
            });
        });

        // Phone login
        $("#btn-phone-login").addEventListener("click", async function () {
            var phone = $("#login-phone-input").value.trim();
            var password = $("#login-password-input").value;
            if (!phone || !password) {
                $("#login-phone-error").textContent = "请输入手机号和密码";
                return;
            }

            var result = await NeMusic.api.login_phone(phone, password);
            if (result.success) {
                self._onLoginSuccess(result);
            } else {
                $("#login-phone-error").textContent = result.message || "登录失败";
            }
        });
    },

    _startQRLogin: async function () {
        var container = $("#qr-container");
        container.innerHTML = "<p>加载二维码...</p>";

        try {
            var result = await NeMusic.api.login_qrcode();
        } catch (e) {
            container.innerHTML =
                '<p style="color:#ec4141;">加载二维码失败<br>' +
                '<button class="btn-primary" style="margin-top:8px;" ' +
                'onclick="App._startQRLogin()">重试</button></p>';
            return;
        }

        if (!result.success) {
            container.innerHTML =
                '<p style="color:#ec4141;">' +
                (result.message || "加载失败") + '<br>' +
                '<button class="btn-primary" style="margin-top:8px;" ' +
                'onclick="App._startQRLogin()">重试</button></p>';
            return;
        }

        // Convert data URI to blob URL to avoid CSP restrictions
        var qrSrc = result.qr_image || "";
        if (qrSrc && qrSrc.indexOf("base64,") > 0) {
            try {
                var b64 = qrSrc.split("base64,")[1];
                var raw = atob(b64);
                var ua = new Uint8Array(raw.length);
                for (var i = 0; i < raw.length; i++) {
                    ua[i] = raw.charCodeAt(i);
                }
                var blob = new Blob([ua], { type: "image/png" });
                qrSrc = URL.createObjectURL(blob);
            } catch (e) {
                // Fall back to data URI (might still work)
            }
        }

        container.innerHTML =
            '<img src="' + qrSrc +
            '" alt="QR Code" style="width:200px;height:200px;"' +
            ' onerror="this.style.display=\'none\';' +
            'this.nextSibling.style.display=\'block\';">' +
            '<div style="display:none;color:#ec4141;margin-top:10px;">' +
            '二维码加载失败<br>' +
            '<button class="btn-primary" style="margin-top:8px;" ' +
            'onclick="App._startQRLogin()">重新获取</button></div>' +
            '<p style="margin-top:12px;color:#a0a0b8;font-size:13px;">' +
            '请使用 <b>网易云音乐 APP</b> 扫描二维码登录</p>';
        this._pollQRCode(result.unikey);
    },

    _pollQRCode: function (unikey) {
        var self = this;

        var check = async function () {
            var result = await NeMusic.api.check_qrcode(unikey);

            if (result.status === "success") {
                self._onLoginSuccess(result);
                return;
            } else if (result.status === "expired") {
                $("#qr-container").innerHTML =
                    '<p>二维码已过期<br><a href="#" id="qr-retry">重新获取</a></p>';
                $("#qr-retry").addEventListener("click", function (e) {
                    e.preventDefault();
                    self._startQRLogin();
                });
                return;
            } else if (result.status === "scanned") {
                $("#qr-container").innerHTML =
                    '<p>✓ 已扫描成功</p>' +
                    '<p style="color:#a0a0b8;font-size:13px;">请在 <b>网易云音乐 APP</b> 中确认登录</p>';
            }

            if (result.status !== "success" && result.status !== "expired") {
                self._qrInterval = setTimeout(check, 2000);
            }
        };

        self._qrInterval = setTimeout(check, 2000);
    },

    _onLoginSuccess: function (user) {
        $("#login-modal").classList.add("hidden");
        if (this._qrInterval) {
            clearTimeout(this._qrInterval);
            this._qrInterval = null;
        }

        showToast("登录成功: " + (user.nickname || ""));

        var loginArea = $("#login-area");
        var avatarHtml = user.avatar
            ? '<img src="' + user.avatar + '" alt="" onerror="this.style.display=\'none\'">'
            : '<div class="avatar-placeholder">' + (user.nickname || "U").charAt(0).toUpperCase() + '</div>';
        loginArea.innerHTML =
            '<div class="user-info">' +
            avatarHtml +
            '<span class="user-name">' + (user.nickname || "用户") + "</span>" +
            '<button class="btn-logout" id="btn-logout">退出</button>' +
            "</div>";

        var self = this;
        $("#btn-logout").addEventListener("click", async function () {
            await NeMusic.api.logout();
            self._onLogout();
        });

        // Reload playlists if on playlists page
        PlaylistUI.loadUserPlaylists();
    },

    _onLogout: function () {
        var loginArea = $("#login-area");
        loginArea.innerHTML =
            '<button class="btn-login" id="btn-login">🔑 登录</button>';
        var self = this;
        $("#btn-login").addEventListener("click", function () {
            var modal = $("#login-modal");
            modal.classList.remove("hidden");
            self._startQRLogin();
        });
        showToast("已退出登录");

        // Reset playlists page
        $("#playlist-list").innerHTML =
            '<p class="empty-hint">请先登录查看歌单</p>';
    },

    _checkLogin: async function () {
        var status = await NeMusic.api.get_login_status();
        if (status.logged_in) {
            this._onLoginSuccess(status);
        }
    },
};

// Boot when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
    App.init();
});

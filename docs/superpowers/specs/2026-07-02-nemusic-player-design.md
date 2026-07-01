# NeMusic Player — 设计文档

**日期**: 2026-07-02  
**项目**: 网易云音乐桌面播放器  
**技术路线**: Python + pywebview + VLC  
**打包形式**: 单个 exe (PyInstaller)

---

## 1. 产品概述

NeMusic 是一个 Windows 桌面原生音乐播放器，调用网易云音乐曲库，支持账号登录、歌单同步、搜索播放、歌词展示、下载管理。界面使用 pywebview 渲染现代化 Web UI，后端用 Python 实现网易云 API 加密调用和音频播放。

### 功能边界

**包含**:
- 网易云手机号/二维码登录，Cookie 持久化
- 搜索歌曲（支持关键词、歌手、专辑）
- 播放控制（播放/暂停、上一首/下一首、进度拖拽、音量调节）
- 歌词同步展示（LRC 解析，当前行高亮居中，带封面模糊背景）
- 我的歌单同步浏览
- 官方排行榜浏览
- 自动缓存（播放过的歌曲缓存到本地，同首不重复加载）
- 手动下载（选择歌曲下载为 MP3 到指定文件夹）
- 下载管理页面（查看/播放/删除已下载和缓存文件）

**不包含**:
- 每日推荐、私人 FM 等智能推荐功能
- 评论、动态、社交功能
- MV 播放
- 播客

---

## 2. 架构设计

```
┌──────────────────────────────────────────────────┐
│                  PyWebview 窗口                    │
│                                                    │
│   ┌────────┐  ┌──────────────────┐               │
│   │ 侧边栏  │  │    主内容区       │               │
│   │        │  │  - 搜索页         │               │
│   │ 搜索    │  │  - 歌单详情       │               │
│   │ 我的歌单│  │  - 排行榜         │               │
│   │ 排行榜  │  │  - 歌词视图       │               │
│   │ 下载管理│  │  - 下载管理       │               │
│   └────────┘  └──────────────────┘               │
│   ┌──────────────────────────────────────────────┐│
│   │           底部播放控制栏 (固定)                ││
│   │  封面 │ 歌名-歌手 │ 进度条 │ 播放控制 │ 歌词 ││
│   │  50px │           │       │          │ 音量 ││
│   └──────────────────────────────────────────────┘│
│                                                    │
│         ▲ JS Bridge (window.pywebview.api)         │
│         │                                          │
│   ┌─────▼──────────────────────────────────────┐  │
│   │           Python Backend                     │  │
│   │                                              │  │
│   │  ┌──────────┐ ┌────────────┐ ┌───────────┐  │  │
│   │  │ 网易云API │ │ 音频播放器  │ │ 下载管理   │  │  │
│   │  │ (加密请求)│ │ (VLC)      │ │           │  │  │
│   │  └──────────┘ └────────────┘ └───────────┘  │  │
│   │  ┌──────────┐ ┌────────────────────────┐    │  │
│   │  │ 账号管理  │ │ SQLite 本地存储         │    │  │
│   │  │(登录/Cookie)│(收藏/历史/缓存/下载记录)│    │  │
│   │  └──────────┘ └────────────────────────┘    │  │
│   └─────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

### 关键设计决策

| 决策 | 选择 | 原因 |
|------|------|------|
| 窗口方案 | pywebview + Edge WebView2 | Windows 原生窗口 + 现代 Web UI，依赖少，打包体积可控 |
| 音频引擎 | python-vlc (libVLC) | 支持流媒体直接播放，格式全面，稳定成熟 |
| 网易云 API | Python 直连 (内置加密) | 无需 Node.js 依赖，打包简单 |
| 本地存储 | SQLite | Python 内置支持，轻量零配置 |
| 前端 | 原生 HTML/CSS/JS | 无框架依赖，体积小，加载快 |

---

## 3. 页面路由 & 交互流程

```
                    ┌──────────┐
           ┌───────│  侧边导航  │───────┐
           │       └──────────┘       │
           ▼                          ▼
   ┌──────────────┐           ┌──────────────┐
   │   搜索页      │           │  我的歌单     │
   │ · 搜索框      │           │ · 歌单列表    │
   │ · 搜索结果    │           │ · 点击进入    │
   └──────────────┘           │   歌单详情    │
                              └──────────────┘
           ▼                          ▼
   ┌──────────────┐           ┌──────────────┐
   │  排行榜       │           │  下载管理     │
   │ · 官方榜      │           │ · 已下载列表  │
   │ · 全球榜      │           │ · 缓存管理   │
   └──────────────┘           └──────────────┘

                底部播放控制栏（固定可见）
        ┌──────────────────────────────────────────┐
        │ 专辑封面 │ 歌名 - 歌手 │ ▶▶ │ 🎤 歌词    │
        │  50x50  │            │ ⏸  │ 🔊 音量    │
        └──────────────────────────────────────────┘
                              │
                    点击歌词按钮 / 歌名区域
                              │
                              ▼
        ┌──────────────────────────────────────────┐
        │           歌词展示视图                     │
        │                                          │
        │    · 当前播放歌曲信息（封面 + 歌名歌手）    │
        │    · 滚动歌词（当前行高亮居中）            │
        │    · 歌词可拖拽调整进度                    │
        │    · 背景使用封面图模糊效果                │
        │    · 点击返回按钮或歌词按钮关闭            │
        └──────────────────────────────────────────┘
```

### 交互规则
- 底部播放控制栏在所有页面固定显示
- 点击底部栏「歌词」按钮或歌名区域 → 主内容区切换为歌词视图
- 歌词视图使用封面模糊背景，当前行居中高亮
- 再次点击歌词按钮或返回按钮 → 恢复到先前浏览的页面
- 播放列表以队列形式管理（可清空、移除单首）

---

## 4. 数据流设计

### 4.1 API 调用流程

```
前端 UI                    Python Backend              网易云服务器
───────                    ──────────────              ────────────
   │                           │                           │
   │  api.search("晴天")        │                          │
   │ ────────────────────────►  │                           │
   │                           │  构建加密请求               │
   │                           │  (AES + RSA + Base64)      │
   │                           │ ──────────────────────────►│
   │                           │         返回 JSON           │
   │                           │ ◄───────────────────────── │
   │  返回标准化结果              │                           │
   │ ◄──────────────────────── │                           │
```

### 4.2 播放 URL 获取策略

- 点击播放时**实时请求**播放 URL（URL 有时效性，通常 5-30 分钟）
- 播放过程中 URL 过期 → 后端静默刷新 URL 并继续播放，前端无感知
- 缓存/下载时请求**最高可用音质**（优先 320kbps → 192kbps → 128kbps）

### 4.3 Python → JS API 接口

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `api.search(keyword, limit, offset)` | 关键词, 条数, 偏移 | `{songs: [...]}` | 搜索歌曲 |
| `api.get_song_detail(song_id)` | 歌曲 ID | `{id, name, artists, album, cover, duration}` | 歌曲详情 |
| `api.get_song_url(song_id, quality)` | 歌曲 ID, 音质 | `{url, quality, expire_at}` | 播放 URL |
| `api.get_lyric(song_id)` | 歌曲 ID | `{lrc: "..."}` | LRC 歌词文本 |
| `api.login_phone(phone, password)` | 手机号, 密码 | `{success, uid, nickname, cookie}` | 手机号登录 |
| `api.login_qrcode()` | 无 | `{qr_url, unikey}` | 获取二维码 |
| `api.check_qrcode(unikey)` | unikey | `{status, cookie}` | 轮询二维码状态 |
| `api.get_user_playlists(uid)` | 用户 ID | `{playlists: [...]}` | 用户歌单列表 |
| `api.get_playlist_detail(playlist_id)` | 歌单 ID | `{songs: [...]}` | 歌单内歌曲 |
| `api.get_toplist()` | 无 | `{lists: [...]}` | 排行榜列表 |
| `api.get_toplist_detail(id)` | 榜 ID | `{songs: [...]}` | 排行榜歌曲 |
| `player.play(url)` | 音频 URL | `void` | 开始播放 |
| `player.pause()` | 无 | `void` | 暂停 |
| `player.resume()` | 无 | `void` | 继续播放 |
| `player.seek(position)` | 秒数 | `void` | 跳转进度 |
| `player.set_volume(0-100)` | 音量值 | `void` | 设置音量 |
| `player.get_position()` | 无 | `{current, total}` | 当前播放进度 |
| `download.add(song_id)` | 歌曲 ID | `{success, file_path}` | 下载歌曲到本地 |
| `download.get_list()` | 无 | `{downloads: [...]}` | 已下载列表 |

### 4.4 事件回调 (Python → JS)

| 事件 | 触发时机 | 数据 |
|------|---------|------|
| `on_position_change` | 每秒 | `{current_sec, total_sec, percentage}` |
| `on_play_state_change` | 播放/暂停/停止 | `{state: "playing"\|"paused"\|"stopped"}` |
| `on_song_end` | 当前歌曲播放完毕 | `void` (自动切下一首) |
| `on_error` | 播放出错 | `{code, message}` |

---

## 5. 本地存储 (SQLite)

### 表结构

```sql
-- 用户/登录状态
CREATE TABLE user (
    uid      INTEGER PRIMARY KEY,
    nickname TEXT,
    avatar   TEXT,
    cookie   TEXT,        -- 序列化的 Cookie 字符串
    login_at TIMESTAMP
);

-- 歌单缓存（加速打开速度）
CREATE TABLE playlist_cache (
    id          INTEGER PRIMARY KEY,
    name        TEXT,
    cover_url   TEXT,
    song_count  INTEGER,
    data_json   TEXT,      -- 完整 JSON 缓存
    updated_at  TIMESTAMP
);

-- 播放缓存（自动缓存）
CREATE TABLE play_cache (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id    INTEGER,
    title      TEXT,
    artist     TEXT,
    album      TEXT,
    cover_url  TEXT,
    local_path TEXT,       -- 本地缓存文件路径
    url_hash   TEXT,
    expire_at  TIMESTAMP,
    size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 手动下载记录
CREATE TABLE download (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id     INTEGER,
    title       TEXT,
    artist      TEXT,
    album       TEXT,
    cover_url   TEXT,
    file_path   TEXT,      -- 实际存储路径
    quality     TEXT,      -- '320k' / '192k' / '128k'
    file_size   INTEGER,
    downloaded  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 收藏的歌曲（可选，如果用户需要本地收藏）
CREATE TABLE favorite (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id  INTEGER UNIQUE,
    title    TEXT,
    artist   TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 存储位置
所有本地文件（数据库、缓存音频、下载歌曲）统一存储在项目的 `data/` 目录下：
```
E:\NeMusic\data\
├── nemusic.db       # SQLite 数据库
├── cache\            # 自动缓存音频文件
│   └── *.mp3
└── downloads\        # 手动下载文件
    └── *.mp3
```

---

## 6. 错误处理

| 场景 | 处理方式 |
|------|---------|
| 无网络连接 | 前端显示网络错误 toast，按钮禁用搜索等在线功能，本地下载页面可正常使用 |
| 登录密码错误 | 前端提示「密码错误，请重试」，保留输入内容 |
| 登录需验证码 | 前端提示「需要验证码，请使用二维码登录」 |
| 歌曲 URL 过期 | 后端自动重新请求新 URL，播放无感接续（当前进度位置继续播放） |
| 歌曲无版权/下架 | 前端 toast 提示「该歌曲暂无版权，已自动跳过」，播放列表移除该项 |
| API 请求限流 | 每次请求间隔 ≥ 200ms；失败后递增延迟重试最多 3 次（1s / 3s / 10s） |
| VLC 播放器初始化失败 | 检查 libVLC DLL 是否存在，缺失时弹窗提示缺少运行库 |
| 下载存储空间不足 | 下载前检查磁盘剩余空间（需 > 100MB），不足时弹窗提示 |
| Cookie 过期 | API 返回 301/401 时尝试刷新 Cookie，失败则清空登录状态并提示重新登录 |
| 歌词不存在/纯音乐 | 歌词视图显示「暂无歌词」或「♫ 纯音乐，请欣赏」 |

---

## 7. 技术栈明细

| 层 | 技术 | 版本 | 用途 |
|----|------|------|------|
| Python | CPython | 3.10+ | 后端主语言 |
| 窗口 | pywebview | ≥5.0 | 原生窗口 + WebView2 渲染 |
| 音频 | python-vlc | ≥3.0 | 基于 libVLC 的音频播放 |
| 加密 | pycryptodome | ≥3.19 | AES-128-CBC / RSA 加密 |
| HTTP | requests | ≥2.31 | HTTP 请求 |
| 数据库 | sqlite3 | 内置 | 本地数据存储 |
| 前端 | HTML5 + CSS3 + Vanilla JS | - | 无框架依赖 |
| CSS | 自定义样式 + CSS Variables | - | 主题色管理 |
| 打包 | PyInstaller | ≥6.0 | 打包为单 exe |
| 图标 | 自定义 icon.ico | - | 应用图标 |

---

## 8. 项目目录结构

```
E:\NeMusic\
├── main.py                 # 程序入口，启动 pywebview 窗口
├── build.py                # PyInstaller 打包脚本
├── requirements.txt        # Python 依赖
├── icon.ico                # 应用图标
├── backend/
│   ├── __init__.py
│   ├── api.py              # 网易云 API 封装（面向前端的接口层）
│   ├── crypto.py           # AES / RSA 加密实现
│   ├── netease.py          # 网易云底层 HTTP 请求 + 参数构建
│   ├── player.py           # VLC 音频播放器封装
│   ├── download.py         # 下载/缓存管理
│   ├── storage.py          # SQLite 数据库操作
│   └── lyric.py            # LRC 歌词解析器
├── frontend/
│   ├── index.html           # 主页面（SPA 结构）
│   ├── css/
│   │   ├── main.css         # 全局样式 + CSS Variables
│   │   ├── sidebar.css      # 侧边导航栏
│   │   ├── player-bar.css   # 底部播放控制栏
│   │   ├── lyrics.css       # 歌词视图
│   │   ├── search.css       # 搜索页
│   │   ├── playlist.css     # 歌单详情页
│   │   └── download.css     # 下载管理页
│   ├── js/
│   │   ├── app.js           # 应用入口 + 路由管理
│   │   ├── api-bridge.js    # Python ↔ JS 通信封装
│   │   ├── player.js        # 播放逻辑（前端侧）
│   │   ├── lyrics.js        # 歌词渲染 + 滚动
│   │   ├── search.js        # 搜索逻辑
│   │   ├── playlist.js      # 歌单逻辑
│   │   ├── download.js      # 下载管理逻辑
│   │   └── utils.js         # 工具函数
│   └── assets/
│       └── default-cover.jpg # 默认封面图
├── data/                     # 运行时数据（自动创建）
│   ├── nemusic.db            # SQLite 数据库
│   ├── cache/                # 自动缓存音频
│   └── downloads/            # 手动下载文件
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-07-02-nemusic-player-design.md  # 本设计文档
```

---

## 9. 打包输出

使用 PyInstaller 打包，生成目标：

```
NeMusic.exe  (~60-80MB)
```

打包包含：
- Python 解释器 + 所有 .py 模块
- libVLC 核心 DLL
- pywebview 依赖（WebView2 使用系统自带，不打包）
- 前端静态资源（HTML/CSS/JS 内嵌）
- 应用图标

---

## 10. 设计决策记录

| # | 讨论点 | 结论 |
|---|--------|------|
| 1 | 界面形式 | 桌面原生窗口应用 |
| 2 | 功能范围 | 完整版（登录 + 歌单 + 搜索 + 歌词 + 下载），不含智能推荐 |
| 3 | 技术方案 | Python + pywebview（现代 Web UI + 轻量打包） |
| 4 | 下载管理 | 自动缓存 + 手动导出下载，两者兼具 |
| 5 | 歌词交互 | 点击底部栏按钮切换至歌词视图，封面模糊背景 |
| 6 | 项目位置 | E:\NeMusic\ |

# getkit

[中文](README.md) | [English](README.en.md)

An interactive downloader built around [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [gallery-dl](https://github.com/mikf/gallery-dl): paste links to download, with automatic per-site engine selection.

> For personal study and research only. Please comply with each platform's terms of service and copyright rules. Do not use it for infringement or commercial purposes.

## Features

- **Automatic per-site engine routing**: YouTube / Bilibili etc. via yt-dlp, Instagram via gallery-dl, Douyin via yt-dlp + a local signing plugin.
- **List then pick**: enumerate the items inside one link (playlists, Instagram carousels, Douyin image albums) and select by index.
- **Multiple modes**: best quality, target resolution, audio only (mp3/m4a/flac/wav/opus), manual format selection, subtitles only.
- **Browser cookies**: read login state from Chrome (etc.); on Chrome it can **auto-select the profile that is still logged in** for each site.
- **Persistent preferences**: settings are saved to `get_config.json`.

## Site support

| Site | Engine | Capability / limits |
|---|---|---|
| YouTube / Bilibili etc. | yt-dlp | Full support (quality/audio/subtitles/playlists) |
| Instagram | gallery-dl | Posts, carousels, Reels, Stories, user profiles; **login required** |
| Xiaohongshu (RedNote) | yt-dlp | Single video notes with `xsec_token` only; image posts unsupported |
| Douyin | yt-dlp + plugin | Single videos and **image albums (images + live photos)**; requires a `UIFID` cookie in Chrome |

## Requirements

- **Python** ≥ 3.8 (3.9+ recommended)
- **yt-dlp**, **gallery-dl**
- **ffmpeg** (for muxing / audio conversion)

Install:

```bash
# macOS (Homebrew)
brew install yt-dlp gallery-dl ffmpeg

# Or install the Python tools with pip
pip install -r requirements.txt
```

On Windows / Linux, install yt-dlp, gallery-dl and ffmpeg via pip or your package manager, and make sure they are on `PATH`.

## Quick start

```bash
git clone https://github.com/Corbaccio/getkit.git
cd getkit
./setup.sh          # macOS/Linux: detect & install deps (Windows: setup.ps1)
python3 get.py
```

> On first run, `get_config.json` is generated from `config.example.json` (Chrome cookies enabled by default).
> If dependencies are missing, the program prints the install command for your OS at startup.

Main menu:

```
  1. Start download
  2. Settings
  0. Quit
```

Choose "Start download", paste links (one per line; multiple allowed), end with an empty line, then follow the prompts.

## Layout

```
getkit/
├── get.py                    # entry point
├── getkit/                   # downloader package
│   ├── config.py             # config & paths
│   ├── sites.py              # site detection / URL normalization
│   ├── cookies.py            # browser cookies / Chrome profile auto-detection
│   ├── tools.py              # external tool discovery
│   ├── runner.py             # command execution & output
│   ├── prompts.py            # interactive helpers
│   ├── listing.py            # item enumeration
│   ├── engines.py            # download command construction
│   ├── settings.py           # settings flow
│   ├── main.py               # main menu
│   └── flows/                # per-site flows (ytdlp / gallery / douyin)
├── plugins/douyinfix/        # yt-dlp Douyin signing plugin
├── config.example.json       # sample config
├── requirements.txt
└── Arsenal/                  # default output dir (ignored)
```

## Usage

### General

- After pasting links, pick a download type and confirm.
- For sites that need login or hit anti-bot, log in via the browser and set the cookie source in Settings.

### yt-dlp flow (YouTube / Bilibili etc.)

Best quality, target resolution, audio only, list-and-pick formats, subtitles only, and **list items then pick** (good for playlists/collections).

### Instagram (gallery-dl)

Menu: images + videos / videos only / images only / **list media and pick** / skip.
Requires an Instagram login; re-login when the session expires.

### Douyin

Menu: **list and pick (images / live / videos)** / download all.

- Single video: downloaded directly.
- Image album (`aweme_type=68`): expanded into "images" and "live photos" items you can select.
- Requires a valid `UIFID` cookie in Chrome (set automatically after visiting douyin.com).
- "Work unavailable" usually means the post is filtered / under review / private / deleted.

## Cookies & login

`cookies_browser` in `get_config.json` controls whether browser cookies are used.

- **Chrome auto profile (default)**: the program reads each Chrome profile's cookie DB and picks the one whose login is **still valid** per site, so you don't switch manually.
- **Manual**: choose "manual" in Settings and enter the profile name (usually `Default` for Chrome).

Notes:

- Reading Chrome cookies accesses the OS keychain (macOS shows a prompt) — click "Always Allow".
- Auto profile detection reads the Chrome cookie files directly and supports the common macOS / Windows / Linux Chrome locations; if it cannot find them it falls back to the manual profile.
- Other browsers (Safari/Edge/Firefox...) are handled by yt-dlp / gallery-dl themselves.

## Douyin plugin

Douyin's web API uses the Argus anti-bot, requiring `uifid` + `x-secsdk-web-signature`; upstream yt-dlp does not support it yet. This repo ships a **local yt-dlp plugin** in `plugins/douyinfix/` that:

- adds the full web query params and computes `x-secsdk-web-signature` (MD5, no JS);
- expands the `images[]` of an album into a selectable playlist.

The program loads it automatically via `--plugin-dirs <repo>/plugins`. The signing formula comes from community findings (see Credits); if Douyin changes it, the plugin may need updating.

## Configuration (get_config.json)

| Field | Meaning | Default |
|---|---|---|
| `output_dir` | Output directory | `Arsenal/` inside the repo |
| `cookies_browser` | Cookie browser (empty = none) | `"chrome"` |
| `cookies_profile` | Profile name in manual mode | `"Default"` |
| `auto_profile` | Auto-select Chrome profile per site | `true` |
| `concurrency` | Concurrent fragments | `4` |
| `filename_template` | Filename template | `"%(title)s.%(ext)s"` |

## FAQ

- **Douyin 403**: the program forces a direct connection for Douyin (ignoring the system proxy) because the proxy makes Douyin's CDN return 403. If it still fails, check for a global proxy.
- **`aweme_detail: null`**: the work is unavailable (filtered / under review / private / deleted).
- **Instagram asks for login**: session expired — log in again in the browser.
- **Keychain prompt**: needed to read Chrome cookies; click "Always Allow".
- **yt-dlp not found**: make sure it is installed and on `PATH`.

## Disclaimer

This project is for personal study and technical research only. It provides no content and does not encourage any copyright infringement or violation of platform terms. Users are solely responsible for their use.

## License

[MIT](LICENSE) © 2026 Corbaccio

## Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) / [gallery-dl](https://github.com/mikf/gallery-dl)
- Douyin signing approach from yt-dlp issue #9667 and Evil0ctal's public findings

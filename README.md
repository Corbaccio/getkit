# getkit

[中文](README.md) | [English](README.en.md)

一个围绕 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 与 [gallery-dl](https://github.com/mikf/gallery-dl) 的交互式下载器：粘贴链接即可下载，并可按站点自动选择下载引擎。

> 仅供个人学习与研究使用。请遵守各平台的服务条款与版权规定，不要用于侵权或商业用途。

## 功能特性

- **按站点自动分流引擎**：YouTube / B站等走 yt-dlp，Instagram 走 gallery-dl，抖音走 yt-dlp + 本地签名插件。
- **先解析、再挑选**：把「一条链接里的多个条目」列出清单（播放列表、Instagram 轮播、抖音图文/图集），按序号挑选下载。
- **多种下载模式**：最佳画质、指定分辨率、纯音频（mp3/m4a/flac/wav/opus）、手动选格式、仅字幕。
- **浏览器 cookies**：支持从 Chrome 等浏览器读取登录态；Chrome 下可按站点**自动挑选登录有效的 profile**。
- **偏好持久化**：设置自动保存到 `get_config.json`。

## 站点支持

| 站点 | 引擎 | 能力与限制 |
|---|---|---|
| YouTube / B站 等 | yt-dlp | 完整支持（画质/音频/字幕/播放列表） |
| Instagram | gallery-dl | 帖子、多图轮播、Reels、Stories、用户主页；**需要登录** |
| 小红书 | yt-dlp | 仅带 `xsec_token` 的**单条视频笔记**；图文笔记暂不支持 |
| 抖音 | yt-dlp + 插件 | 单视频、**图文图集（图片 + live 动图）**；需要 Chrome 中有 `UIFID` cookie |

## 环境要求

- **Python** ≥ 3.8（推荐 3.9+）
- **yt-dlp**、**gallery-dl**
- **ffmpeg**（音视频合并 / 音频转换）

安装示例：

```bash
# macOS (Homebrew)
brew install yt-dlp gallery-dl ffmpeg

# 或使用 pip 安装 Python 工具
pip install -r requirements.txt
```

Windows / Linux 请分别安装 yt-dlp、gallery-dl、ffmpeg（pip 或系统包管理器均可），并确保它们在 `PATH` 中。

## 快速开始

```bash
git clone https://github.com/Corbaccio/getkit.git
cd getkit
./setup.sh          # macOS/Linux：检测并安装依赖（Windows 用 setup.ps1）
python3 get.py
```

> 首次运行会自动根据 `config.example.json` 生成 `get_config.json`（默认已启用 Chrome cookies）。
> 未装依赖时程序会在启动时给出对应系统的安装命令。

首次运行会显示主菜单：

```
  1. 开始下载
  2. 设置
  0. 退出
```

选择「开始下载」，粘贴链接（每行一个，可一次多个），回车空行结束，再按提示选择下载类型即可。

## 目录结构

```
getkit/
├── get.py                    # 入口
├── getkit/                   # 下载器包
│   ├── config.py             # 配置与路径
│   ├── sites.py              # 站点识别 / 链接归一化
│   ├── cookies.py            # 浏览器 cookies / Chrome profile 自动检测
│   ├── tools.py              # 外部工具定位与检查
│   ├── runner.py             # 命令执行与结果输出
│   ├── prompts.py            # 交互辅助
│   ├── listing.py            # 条目解析（列出清单）
│   ├── engines.py            # 下载命令参数构造
│   ├── settings.py           # 设置流程
│   ├── main.py               # 主菜单
│   └── flows/                # 各站点下载流程（ytdlp / gallery / douyin）
├── plugins/douyinfix/        # yt-dlp 抖音签名插件
├── config.example.json       # 配置样例
├── requirements.txt
└── Arsenal/                  # 默认输出目录（已忽略）
```

## 下载目录结构

下载会按平台自动归档到输出目录（默认 `Arsenal/`）：

```
Arsenal/
├── YouTube/<标题>.mp4
├── Bilibili/<标题>.mp4
├── 小红书/<标题>.mp4
├── 抖音/
│   ├── <单视频标题>.mp4
│   └── <作品文案>/              # 图文图集：一个作品一个文件夹
├── Instagram/<用户名>/          # gallery-dl 结构
└── 其它/<标题>                  # 识别不出平台
```

整理存量文件（把散落文件按上面的规则归档）：

```bash
python3 organize.py            # 预览将要做的移动
python3 organize.py --apply    # 执行（只移动，不删除、不改名）
```

## 使用指南

### 通用

- 粘贴链接后，先选「下载类型」，再确认即可开始。
- 需要登录或触发风控的站点，请先在浏览器登录，并在设置里配置 cookies 来源。

### yt-dlp 流程（YouTube / B站等）

支持：最佳画质、指定分辨率、纯音频、列出所有格式手动选择、仅字幕，以及「**先解析条目清单，再挑选下载**」（适合播放列表/合集）。

### Instagram（gallery-dl）

菜单：图片 + 视频 / 仅视频 / 仅图片 / **先列出媒体清单手动挑选** / 跳过。
需要 Instagram 登录态，且 session 过期后需重新登录。

### 抖音

菜单：**解析并挑选（图片 / 动图 / 视频）** / 全部下载。

- 单条视频：直接下载。
- 图文图集（`aweme_type=68`）：展开为「图片」与「live 动图」两类条目，可按序号挑选。
- 需要 Chrome 中存在有效 `UIFID` cookie（正常访问过 douyin.com 即会有）。
- 若提示「作品不可用」，通常是该作品被过滤/审核/私密或已删除。

## cookies 与登录

`get_config.json` 中的 `cookies_browser` 决定是否使用浏览器 cookies。

- **Chrome 自动选择 profile（默认）**：程序会读取各 Chrome profile 的 cookie 数据库，按站点挑选**登录仍然有效**的那个 profile（如 Instagram 命中某个 profile、抖音命中另一个），无需手动切换。
- **手动指定**：在「设置 → cookies」里选「手动指定」，填入 profile 名称（Chrome 通常为 `Default`）。

注意事项：

- 读取 Chrome cookies 会访问系统钥匙串（macOS 会弹出授权框），选「始终允许」即可。
- 自动选择 profile 依赖直接读取 Chrome 的 cookie 文件，目前对 macOS / Windows / Linux 的常见 Chrome 安装路径做了适配；若无法识别，会回退为「手动 profile」。
- 其它浏览器（Safari/Edge/Firefox 等）由 yt-dlp / gallery-dl 自行处理路径。

## 抖音插件说明

抖音网页接口启用了 Argus 反爬，需要 `uifid` + `x-secsdk-web-signature` 签名，内置 yt-dlp 尚未支持。本仓库在 `plugins/douyinfix/` 提供一个**本地 yt-dlp 插件**补齐：

- 请求时加上完整 web 参数并按公式计算 `x-secsdk-web-signature`（MD5，无需 JS）；
- 图集接口返回的 `images[]` 展开为可挑选的 playlist。

程序会自动以 `--plugin-dirs <仓库>/plugins` 加载该插件。签名算法来源于社区发现（见文末致谢），若抖音日后调整算法，插件可能失效，需要相应更新。

## 配置项（get_config.json）

| 字段 | 含义 | 默认值 |
|---|---|---|
| `output_dir` | 输出目录 | 仓库内 `Arsenal/` |
| `cookies_browser` | cookies 浏览器（空 = 不使用） | `"chrome"` |
| `cookies_profile` | 手动模式下的 profile 名 | `"Default"` |
| `auto_profile` | 是否按站点自动选择 Chrome profile | `true` |
| `concurrency` | 并发分片数 | `4` |
| `filename_template` | 文件名模板 | `"%(title)s.%(ext)s"` |

## 常见问题

- **抖音下载 403**：程序已对抖音强制直连（忽略系统代理），因为系统代理会让抖音 CDN 返回 403。若仍 403，检查是否用了全局代理。
- **`aweme_detail: null`**：该作品不可用（被过滤/审核/私密/删除）。
- **Instagram 报需要登录**：session 过期，请在浏览器重新登录。
- **钥匙串弹窗**：读取 Chrome cookies 需要授权，点「始终允许」。
- **找不到 yt-dlp**：确保已安装且在 `PATH` 中（macOS 亦可 `brew install yt-dlp`）。

## 免责声明

本项目仅为个人学习与技术研究用途，不提供任何内容，也不鼓励任何侵犯版权或违反平台服务条款的行为。使用者需自行承担一切责任。

## License

[MIT](LICENSE) © 2026 Corbaccio

## 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) / [gallery-dl](https://github.com/mikf/gallery-dl)
- 抖音签名思路来自 yt-dlp issue #9667 及 Evil0ctal 的公开发现

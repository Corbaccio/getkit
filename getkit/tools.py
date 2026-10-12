#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外部工具定位与可用性检查。"""

from __future__ import annotations

import os
import shutil
import sys

# 可执行文件路径（优先用 PATH 里的，找不到再退回 homebrew 默认位置）
YTDLP = shutil.which("yt-dlp") or "/opt/homebrew/bin/yt-dlp"
GALLERY_DL = shutil.which("gallery-dl")
FFMPEG = shutil.which("ffmpeg")


def check_tools() -> None:
    if not os.path.isfile(YTDLP) and shutil.which(YTDLP) is None:
        print(f"[错误] 找不到 yt-dlp（{YTDLP}）。请先安装：brew install yt-dlp")
        sys.exit(1)
    if FFMPEG is None:
        print("[提示] 未检测到 ffmpeg，音视频合并和音频转换可能失败。")
    if GALLERY_DL is None:
        print("[提示] 未检测到 gallery-dl，Instagram 下载将不可用（brew install gallery-dl）。")

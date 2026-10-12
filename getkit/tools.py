#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外部工具定位、可用性检查与安装指引。"""

from __future__ import annotations

import os
import shutil
import sys

# 可执行文件路径（优先用 PATH 里的，找不到再退回 homebrew 默认位置）
YTDLP = shutil.which("yt-dlp") or "/opt/homebrew/bin/yt-dlp"
GALLERY_DL = shutil.which("gallery-dl")
FFMPEG = shutil.which("ffmpeg")


def install_hint() -> str:
    """当前系统的依赖安装命令提示。"""
    if sys.platform == "darwin":
        return "brew install yt-dlp gallery-dl ffmpeg"
    if os.name == "nt":
        return ("winget install yt-dlp\n"
                "     winget install Gyan.FFmpeg\n"
                "     pip install -r requirements.txt")
    return "pip install -r requirements.txt   # 另需 ffmpeg（apt/dnf/pacman 等安装）"


def missing_tools() -> list[str]:
    """返回缺失的必需/可选工具名。"""
    missing = []
    if not os.path.isfile(YTDLP) and shutil.which(YTDLP) is None:
        missing.append("yt-dlp")
    if GALLERY_DL is None:
        missing.append("gallery-dl")
    if FFMPEG is None:
        missing.append("ffmpeg")
    return missing


def check_tools() -> None:
    """检查依赖，缺失时给出安装指引。yt-dlp 缺失直接退出。"""
    if not os.path.isfile(YTDLP) and shutil.which(YTDLP) is None:
        print("[错误] 找不到 yt-dlp —— 它是必需的下载引擎。")
        print(f"        安装：{install_hint()}")
        sys.exit(1)
    if FFMPEG is None:
        print("[提示] 未检测到 ffmpeg，音视频合并和音频转换可能失败。")
        print(f"        安装：{install_hint()}")
    if GALLERY_DL is None:
        print("[提示] 未检测到 gallery-dl，Instagram 下载将不可用。")
        print(f"        安装：{install_hint()}")

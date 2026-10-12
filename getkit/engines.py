#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下载命令参数构造（yt-dlp / gallery-dl）。"""

from __future__ import annotations

from .cookies import cookie_args_for
from .config import Config
from .sites import plugin_args
from .tools import GALLERY_DL, YTDLP


def build_common_args(cfg: Config, playlist_ok: bool) -> list[str]:
    """yt-dlp 公共参数（不含 cookies；cookies 按链接单独追加）。"""
    args = [
        YTDLP,
        "--newline",                    # 进度按行刷新，便于查看
        "-P", cfg.output_dir,           # 输出目录
        "-o", cfg.filename_template,    # 文件名模板
        "--no-mtime",
    ] + plugin_args()
    if cfg.concurrency and int(cfg.concurrency) > 1:
        args += ["-N", str(cfg.concurrency)]
    if not playlist_ok:
        args += ["--no-playlist"]
    return args


def build_gallery_args(cfg: Config, url: str) -> list[str]:
    args = [GALLERY_DL, "-d", cfg.output_dir]
    args += cookie_args_for(cfg, url)
    return args

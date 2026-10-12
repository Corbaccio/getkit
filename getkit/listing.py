#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""条目解析：把链接解析成可挑选的清单（yt-dlp / gallery-dl）。"""

from __future__ import annotations

import json
import os
import subprocess

from .cookies import cookie_args_for
from .config import Config
from .runner import auth_hint, tail
from .sites import plugin_args
from .tools import GALLERY_DL, YTDLP

# gallery-dl 视频/图片过滤表达式（--filter）
VIDEO_EXTS = ("mp4", "mov", "m4v", "webm", "mkv", "ts", "m4s", "flv")
IMAGE_EXTS = ("jpg", "jpeg", "png", "gif", "webp", "heic", "heif", "avif", "bmp")
VIDEO_FILTER = "extension in (%s)" % ", ".join(repr(e) for e in VIDEO_EXTS)
IMAGE_FILTER = "extension in (%s)" % ", ".join(repr(e) for e in IMAGE_EXTS)


def ytdlp_list(cfg: Config, url: str) -> list[dict] | None:
    """用 yt-dlp --flat-playlist -J 列出条目。返回 list 或 None（失败）。"""
    args = [YTDLP, "--flat-playlist", "-J", "--no-warnings"]
    args += plugin_args() + cookie_args_for(cfg, url) + [url]
    try:
        proc = subprocess.run(args, capture_output=True, text=True)
    except OSError as e:
        print(f"[错误] 无法启动 yt-dlp: {e}")
        return None
    if not proc.stdout.strip():
        print("[错误] 解析失败：")
        print(tail(proc.stderr))
        auth_hint(proc.stderr)
        return None
    try:
        data = json.loads(proc.stdout)
    except ValueError as e:
        print(f"[错误] 解析返回的 JSON 失败：{e}")
        return None

    entries = data.get("entries")
    if entries:
        items = []
        for i, entry in enumerate(entries, start=1):
            if not entry:
                continue
            items.append({
                "title": entry.get("title") or entry.get("id") or f"条目 {i}",
                "duration": entry.get("duration"),
                "ext": entry.get("ext"),
                "dtype": entry.get("douyin_type"),
            })
        return items or None

    return [{
        "title": data.get("title") or data.get("id") or "视频",
        "duration": data.get("duration"),
        "ext": data.get("ext"),
        "dtype": data.get("douyin_type"),
    }]


def gallerydl_list(cfg: Config, url: str) -> list[dict] | None:
    """用 gallery-dl -j -s 列出媒体条目。返回 list 或 None（失败）。"""
    if GALLERY_DL is None:
        print("[错误] 未安装 gallery-dl。")
        return None
    args = [GALLERY_DL, "-j", "-s", "--no-colors"] + cookie_args_for(cfg, url) + [url]
    try:
        proc = subprocess.run(args, capture_output=True, text=True)
    except OSError as e:
        print(f"[错误] 无法启动 gallery-dl: {e}")
        return None
    if not proc.stdout.strip():
        print("[错误] 解析失败：")
        print(tail(proc.stderr))
        auth_hint(proc.stderr)
        return None
    try:
        messages = json.loads(proc.stdout)
    except ValueError as e:
        print(f"[错误] 解析返回的 JSON 失败：{e}")
        return None

    items = []
    for msg in messages:
        if not isinstance(msg, list) or not msg:
            continue
        code = msg[0]
        if code == 3:
            meta = msg[2] if len(msg) > 2 and isinstance(msg[2], dict) else {}
            filename = meta.get("filename") or os.path.basename(str(msg[1]).split("?")[0])
            items.append({
                "title": filename,
                "extension": meta.get("extension") or "",
                "category": meta.get("category") or "",
            })
        elif code == -1 and isinstance(msg[1], dict):
            print(f"  [警告] {msg[1].get('message', '解析出错')}")
    if not items and proc.stderr.strip():
        print("[提示] 未解析到媒体，底层日志：")
        print(tail(proc.stderr))
        auth_hint(proc.stderr)
    return items or None


def entry_tag(item: dict) -> str:
    """条目类型标签：图片 / 动图 / 视频。"""
    dtype = item.get("dtype")
    if dtype == "image":
        return "[图]"
    if dtype == "live":
        return "[动图]"
    if item.get("ext") in IMAGE_EXTS:
        return "[图]"
    return "[视频]"


def print_gallery_items(items: list[dict]) -> None:
    for i, item in enumerate(items, start=1):
        ext = f" .{item['extension']}" if item.get("extension") else ""
        kind = item.get("category") or ""
        print(f"  {i}. {item['title']}{ext}  {('(' + kind + ')') if kind else ''}")
